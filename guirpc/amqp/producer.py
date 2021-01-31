import pickle
from uuid import uuid4

import pika

from .domain.contracts import ProducerInterface
from .domain.encoding import BytesEncoder, StringEncoder
from .domain.objects import ProxyRequest, ProxyResponse
from .serializers import BinarySerializer, TextSerializer
from .utils import import_serializer


class Producer(ProducerInterface):
    """
    This is a an RPC client/producer that will send requests and block until
    receiving back a response through a unique channel.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._response_queue = None
        self._corr_id = None
        self._response = None
        self._set_channel_consume()

    @property
    def response(self):
        return self._response

    def _set_channel_consume(self):
        _dq = self.channel.queue_declare(queue=self.amqp_entities.queue,
                                         exclusive=True,
                                         auto_delete=True)
        self._response_queue = _dq.method.queue

        self.channel.basic_consume(
            queue=self._response_queue,
            on_message_callback=self._handle_response,
            auto_ack=True)

    def _handle_response(self, ch, method, props, body):
        if self._corr_id == props.correlation_id:
            self.set_x_response(body, props)
            self.channel.queue_delete(self._response_queue)

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

        while not self.response:
            self.connection.process_data_events()

        return self.response

    def set_x_response(self, body, props):
        status = props.headers.get('Response-Status')
        sz_name = props.headers.get('Response-Serializer')

        sz = import_serializer(sz_name)
        decoded_body = BytesEncoder.decode(body)

        object_, error_message = (None, None)
        if sz is not BinarySerializer:
            msg_str = StringEncoder.decode(decoded_body,
                                           codec=sz.ENCODING)

            st_str = str(status)
            if st_str[:1] in ['5', '4']:
                error_message = TextSerializer.deserialize(msg_str)
            else:
                object_ = sz.deserialize(msg_str)
        else:
            object_ = pickle.loads(decoded_body)

        x_resp = ProxyResponse(status, object_, error_message=error_message)
        x_resp.set_properties(bytes_=body,
                              encoding=props.content_encoding,
                              content_type=props.content_type,
                              message_headers=props.headers)

        self._response = x_resp
