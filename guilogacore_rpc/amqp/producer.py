from uuid import uuid4

import pika

from .domain.contracts import ProducerInterface
from .domain.objects import ProxyRequest, ProxyResponse


class Producer(ProducerInterface):
    """
    This is a an RPC client/producer that will send requests and block until
    receiving back a response through a unique channel.
    """
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self._response_queue = None
        self._corr_id = None
        self._response = None
        self._set_channel_consume()

    def _set_channel_consume(self):
        _dq = self.channel.queue_declare(queue=self.amqp_entities.queue,
                                         exclusive=True)
        self._response_queue = _dq.method.queue

        self.channel.basic_consume(
            queue=self._response_queue,
            on_message_callback=self._handle_response,
            auto_ack=True)

    def _handle_response(self, ch, method, props, body):
        if self._corr_id == props.correlation_id:
            print('Response body received %s' % body)
            self._response = body
            # response_bytes = base64.b64decode(body)
            # response_message = response_bytes.decode('ascii')
            # self.response = response_message

    def publish(self, request: ProxyRequest) -> ProxyResponse:
        self._response = None
        self._corr_id = str(uuid4())
        self.channel.basic_publish(
            exchange=self.amqp_entities.exchange,
            routing_key=self.amqp_entities.routing_key,
            properties=pika.BasicProperties(
                content_type=request.content_type,
                content_encoding=request.encoding,
                headers=request.message_headers,
                reply_to=self._response_queue,
                correlation_id=self._corr_id,
                app_id=request.app_id,
                delivery_mode=2,
            ),
            body=request.bytes)

        while self._response is None:
            self.connection.process_data_events()

        return self._response
