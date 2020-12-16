from typing import Type
from pika import BasicProperties

from .domain.contracts import BaseSerializer
from .domain.encoding import StringEncoder, BytesEncoder
from .domain.objects import ProxyRequest
from .serializers import TextSerializer


def register_faas(req_sz:  Type[BaseSerializer],
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
        def _exec(b64_msg_bytes: bytes, pika_props: BasicProperties):
            required_en = req_codec or req_sz.ENCODING
            msg_bytes = BytesEncoder.decode(b64_msg_bytes)
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

            x_request = ProxyRequest(
                object_=object_,
                app_id=pika_props.app_id)

            x_request.set_properties(
                bytes_=msg_bytes,
                encoding=required_en,
                content_type=req_sz.CONTENT_TYPE,
                message_headers=pika_props.headers)

            x_response = func(x_request)

            resp_str = None
            try:
                resp_str = resp_sz.serialize(x_response.object)
            except Exception as err:
                x_response.status = 500
                x_response.error_message = (
                    'SerializationError: an error occurred while serializing message ' +
                    '{0} with {1}\n'.format(x_response.object, resp_sz) +
                    f'\n*** error_trace ***\n{err}')

            response_encoding = resp_codec or resp_sz.ENCODING
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
                    f'\n*** error_trace ***\n{err}')

            if x_response.is_error:
                resp_ct = TextSerializer.CONTENT_TYPE
                response_encoding = TextSerializer.ENCODING
                resp_bytes = StringEncoder.encode(x_response.error_message,
                                                  codec=response_encoding)
            else:
                resp_ct = resp_sz.CONTENT_TYPE

            b64_resp_bytes = BytesEncoder.encode(resp_bytes)

            x_response.set_properties(
                bytes_=b64_resp_bytes,
                encoding=response_encoding,
                content_type=resp_ct,
                message_headers=pika_props.headers)

            return x_response

        return _exec
    return exec_wrapper
