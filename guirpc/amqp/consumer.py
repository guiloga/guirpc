import functools
import logging
import time
from typing import Dict, Callable

import pika

from guirpc.amqp.domain import ProxyResponse
from guirpc.amqp.domain.contracts import ConsumerInterface
from guirpc.amqp.domain.encoding import StringEncoder, BytesEncoder
from guirpc.amqp.serializers import TextSerializer

LOGGER = logging.getLogger('rpcServer')


class Consumer(ConsumerInterface):
    """
    This is an async consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, this class will stop and indicate
    that reconnection is necessary. You should look at the output, as
    there are limited reasons why the connection may be closed, which
    usually are tied to permission related issues or socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.
    """

    def __init__(self, faas_callables: Dict[str, Callable], *args, **kwargs):
        super(Consumer, self).__init__(*args, **kwargs)
        self._faas_callables = faas_callables
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._consuming = False
        self._should_reconnect = False

    @property
    def faas_callables(self):
        return self._faas_callables

    @property
    def should_reconnect(self):
        return self._should_reconnect

    def connect(self):
        passw = self.amqp_url.split('@')[0].split(':')[-1]
        LOGGER.info('Connecting to %s', self.amqp_url.replace(':%s' % passw, ':' + '*' * 8))

        return pika.SelectConnection(
            parameters=pika.URLParameters(self.amqp_url),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

    def close_connection(self):
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            LOGGER.info('Connection is closing or already closed')
        else:
            LOGGER.info('Closing connection')
            self._connection.close()

    def on_connection_open(self, _unused_connection):
        LOGGER.info('Connection opened')
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        LOGGER.error('Connection open failed: %s', err)
        self.reconnect()

    def on_connection_closed(self, _unused_connection, reason):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            LOGGER.warning('Connection closed, reconnect necessary: %s', reason)
            self.reconnect()

    def reconnect(self):
        self._should_reconnect = True
        self.stop()

    def open_channel(self):
        LOGGER.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        LOGGER.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.amqp_entities.exchange)

    def add_on_channel_close_callback(self):
        LOGGER.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        LOGGER.warning('Channel %i was closed: %s', channel, reason)
        self.close_connection()

    def setup_exchange(self, exchange_name):
        LOGGER.info('Declaring exchange: %s', exchange_name)
        # Note: using functools.partial is not required, it is demonstrating
        # how arbitrary data can be passed to the callback when it is called
        cb = functools.partial(
            self.on_exchange_declareok, userdata=exchange_name)
        self._channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=self.amqp_entities.exchange_type,
            callback=cb)

    def on_exchange_declareok(self, _unused_frame, userdata):
        LOGGER.info('Exchange declared: %s', userdata)
        self.setup_queue(self.amqp_entities.queue)

    def setup_queue(self, queue_name):
        LOGGER.info('Declaring queue %s', queue_name)
        cb = functools.partial(self.on_queue_declareok, userdata=queue_name)
        self._channel.queue_declare(queue=queue_name, callback=cb)

    def on_queue_declareok(self, _unused_frame, userdata):
        queue_name = userdata
        LOGGER.info('Binding %s to %s with %s', self.amqp_entities.exchange, queue_name,
                    self.amqp_entities.routing_key)
        cb = functools.partial(self.on_bindok, userdata=queue_name)
        self._channel.queue_bind(
            queue_name,
            self.amqp_entities.exchange,
            routing_key=self.amqp_entities.routing_key,
            callback=cb)

    def on_bindok(self, _unused_frame, userdata):
        LOGGER.info('Queue bound: %s', userdata)
        self.set_qos()

    def set_qos(self):
        self._channel.basic_qos(
            prefetch_count=self.prefetch_count, callback=self.on_basic_qos_ok)

    def on_basic_qos_ok(self, _unused_frame):
        LOGGER.info('QOS set to: %d', self.prefetch_count)
        self.start_consuming()

    def start_consuming(self):
        LOGGER.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(
            self.amqp_entities.queue, self.on_message)
        self._consuming = True

    def add_on_cancel_callback(self):
        LOGGER.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        LOGGER.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, _ch, basic_deliver, properties, body):
        # TODO: Threading/Multiprocessing
        faas_name = properties.headers.get('FaaS-Name')
        LOGGER.info(f"Received message -> requests FaaS: {faas_name} [delivery_tag=#%s | corr_id='%s' | app_id='%s']",
                    basic_deliver.delivery_tag, properties.correlation_id, properties.app_id)
        self.acknowledge_message(basic_deliver.delivery_tag)

        if not faas_name in self.faas_callables.keys():
            is_err, status, err_msg = (
                True, 400, f"[RequestError] FaaS with name '{faas_name}' is not registered")
        else:
            faas = self.faas_callables[faas_name]
            try:
                x_resp = faas.__call__(body, properties)
                is_err = False
            except Exception as err:
                is_err, status, err_msg = (
                    True, 500, "[ServerError] An unexpected error occurred "
                               "while processing the request message: "
                               f"'{err.__class__.__name__} -> {err}'")

        if is_err:
            x_resp = ProxyResponse(status, error_message=err_msg)
            resp_bytes = StringEncoder.encode(x_resp.error_message)
            body = BytesEncoder.encode(resp_bytes)
            x_resp.set_properties(bytes_=body,
                                  encoding=TextSerializer.ENCODING,
                                  content_type=TextSerializer.CONTENT_TYPE,
                                  message_headers={'Response-Status': x_resp.status_code,
                                                   'Response-Serializer': TextSerializer.__name__})
        _ch.basic_publish(exchange='',
                          routing_key=properties.reply_to,
                          properties=pika.BasicProperties(
                              content_type=x_resp.content_type,
                              content_encoding=x_resp.encoding,
                              headers=x_resp.message_headers,
                              correlation_id=properties.correlation_id),
                          body=x_resp.bytes)
        LOGGER.info("Reply published with routing_key='%s'" % properties.reply_to)

    def acknowledge_message(self, delivery_tag):
        self._channel.basic_ack(delivery_tag)
        LOGGER.info('Acknowledged message #%s', delivery_tag)

    def stop_consuming(self):
        if self._channel:
            LOGGER.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            cb = functools.partial(
                self.on_cancelok, userdata=self._consumer_tag)
            self._channel.basic_cancel(self._consumer_tag, cb)

    def on_cancelok(self, _unused_frame, userdata):
        self._consuming = False
        LOGGER.info(
            'RabbitMQ acknowledged the cancellation of the consumer: %s',
            userdata)
        self.close_channel()

    def close_channel(self):
        LOGGER.info('Closing the channel')
        self._channel.close()

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        if not self._closing:
            self._closing = True
            LOGGER.info('Stopping')
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
            LOGGER.info('Stopped')


class ProxyReconnectConsumer(ConsumerInterface):
    """
    This is an proxy consumer that will reconnect if the nested
    Consumer indicates that a reconnect is necessary.
    """
    MAX_RECONNECT_DELAY = 300

    def __init__(self, faas_callables: Dict[str, Callable], *args, **kwargs):
        super(ProxyReconnectConsumer, self).__init__(*args, **kwargs)
        self._reconnect_delay = 0
        self._consumer = Consumer(faas_callables, *args, **kwargs)

    def run(self):
        while True:
            try:
                self._consumer.run()
            except KeyboardInterrupt:
                self._consumer.stop()
                break
            LOGGER.info('Reconnection evaluation')
            self._maybe_reconnect()

    def _maybe_reconnect(self):
        if self._consumer.should_reconnect:
            self._consumer.stop()
            self._update_reconnect_delay()
            LOGGER.info('Reconnecting attempt after %d seconds', self._reconnect_delay)
            time.sleep(self._reconnect_delay)
            self._consumer = self._create_new_consumer()

    def _update_reconnect_delay(self):
        self._reconnect_delay += max(1, self._reconnect_delay // 0.67)
        self._reconnect_delay = min(self._reconnect_delay, self.MAX_RECONNECT_DELAY)

    def _create_new_consumer(self):
        return Consumer(self._consumer.faas_callables,
                        amqp_url=self.amqp_url,
                        amqp_entities=self.amqp_entities,
                        prefetch_count=self.prefetch_count)
