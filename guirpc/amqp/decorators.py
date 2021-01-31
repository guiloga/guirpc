import pickle
from typing import Type

from pika import BasicProperties

from .domain.contracts import BaseSerializer
from .domain.encoding import StringEncoder, BytesEncoder
from .domain.exceptions import SerializationError
from .domain.objects import ProxyRequest, ProxyResponse
from .producer import Producer
from .serializers import TextSerializer, BinarySerializer
from .utils import ClientConnector


def _connection_is_open(func):
    def wrapper(*args, **kwargs):
        client_con = args[0] if len(args) > 0 else kwargs['con']
        if client_con.is_reload_required:
            client_con.reload()
        return func(*args, **kwargs)

    return wrapper


def register_faas(req_sz: Type[BaseSerializer],
                  resp_sz: Type[BaseSerializer],
                  req_codec: str = None,
                  resp_codec: str = None):
    """
    Decorator for registering FaaS application functions.
    Each decorated function of this type will be a callable passed to the consumer.

    :param req_sz: Request serializer type.
    :param resp_sz: Response serializer type.
    :param req_codec: Request encoding. If not provided the default value comes from req_sz.
    :param resp_codec: Response encoding. If not provided the default value comes from resp_sz.
    :return: The function wrapper that calls decorated function
        with the proper decoding and encoding response process.
    """

    def exec_wrapper(func):
        def _exec(msg_bytes_en: bytes, pika_props: BasicProperties) -> ProxyResponse:
            msg_bytes = BytesEncoder.decode(msg_bytes_en)
            required_en = req_codec or req_sz.ENCODING
            if req_sz is not BinarySerializer:
                try:
                    msg_str = StringEncoder.decode(msg_bytes,
                                                   codec=required_en)
                except Exception:
                    # TODO: return proper status 40X and message (don't raise an Exception)
                    raise Exception(
                        f'ContentDecodingError: an error occurred while trying to decode {msg_bytes} ' +
                        f'into \'{required_en}\'')

                try:
                    object_ = req_sz.deserialize(msg_str)
                except Exception:
                    # TODO: return proper status 40X and message (don't raise an Exception)
                    raise Exception(
                        'DeserializationError: an error occurred while deserializing message ' +
                        '{0} with {1}'.format(msg_str, req_sz))
            else:
                object_ = pickle.loads(msg_bytes)
                msg_bytes = object_

            x_request = ProxyRequest(
                object_=object_,
                app_id=pika_props.app_id)

            x_request.set_properties(
                bytes_=msg_bytes,
                encoding=required_en,
                content_type=req_sz.CONTENT_TYPE,
                message_headers=pika_props.headers)

            x_response = func(x_request)

            response_encoding = resp_codec or resp_sz.ENCODING
            if resp_sz is not BinarySerializer:
                resp_str = None
                try:
                    resp_str = resp_sz.serialize(x_response.object)
                except Exception as err:
                    x_response.status = 500
                    x_response.error_message = (
                            'SerializationError: an error occurred while serializing object ' +
                            '{0} with {1}\n'.format(x_response.object, resp_sz) +
                            f'\n*** error_desc ***\n{err}')

                resp_bytes = None
                try:
                    if resp_str:
                        resp_bytes = StringEncoder.encode(resp_str,
                                                          codec=response_encoding)
                except Exception as err:
                    x_response.status = 500
                    x_response.error_message = (
                            f'ContentEncodingError: an error occurred while trying to encode {resp_str} ' +
                            f'into \'{response_encoding}\'' +
                            f'\n*** error_desc ***\n{err}')
            else:
                resp_bytes = pickle.dumps(x_response.object)

            if x_response.is_error:
                resp_ct = TextSerializer.CONTENT_TYPE
                response_encoding = TextSerializer.ENCODING
                resp_bytes = StringEncoder.encode(x_response.error_message,
                                                  codec=response_encoding)
            else:
                resp_ct = resp_sz.CONTENT_TYPE

            body = BytesEncoder.encode(resp_bytes)

            x_response.set_properties(
                bytes_=body,
                encoding=response_encoding,
                content_type=resp_ct,
                message_headers={'Response-Status': x_response.status_code,
                                 'Response-Serializer': resp_sz.__name__})

            return x_response

        return _exec

    return exec_wrapper


@_connection_is_open
def faas_producer(con: ClientConnector,
                  faas_name: str,
                  req_sz: Type[BaseSerializer]):
    """
    Decorator that implements an interface, it establishes that the decorated function
    needs to return a ProxyRequest object, it then passes the proxy_request object
    through a Producer RPC call getting back a ProxyResponse.

    :param con: the client connector (ClientConnector).
    :param faas_name: the name of the RPC FaaS function that will be invoked.
    :param req_sz: the request serializer type.
    :return: The function wrapper that calls the decorated function
        passing trough a Producer publish call returning a ProxyResponse.
    """

    def publish_wrapper(func):
        def _publish(*args, **kwargs) -> ProxyResponse:
            x_request = func(*args, **kwargs)
            x_request.app_id = con.config.producer_application_id or 'Unknown'
            x_request.add_headers({'FaaS-Name': faas_name})

            if req_sz is not BinarySerializer:
                try:
                    req_str = req_sz.serialize(x_request.object)
                    req_bytes = StringEncoder.encode(req_str,
                                                     codec=req_sz.ENCODING)
                except Exception as err:
                    raise SerializationError(x_request.object, req_sz, err)
            else:
                req_bytes = pickle.dumps(x_request.object)

            body = BytesEncoder.encode(req_bytes)

            x_request.bytes = body
            x_request.content_type = req_sz.CONTENT_TYPE
            x_request.encoding = req_sz.ENCODING

            producer = Producer(con.bck_con, con.config.amqp_entities)
            x_response = producer.publish(x_request)

            return x_response

        return _publish

    return publish_wrapper
