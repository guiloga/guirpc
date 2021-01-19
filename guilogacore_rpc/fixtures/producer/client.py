from typing import Any

from guilogacore_rpc.amqp.domain.objects import ProxyRequest
from guilogacore_rpc.amqp.decorators import faas_producer
from guilogacore_rpc.amqp.serializers import JsonSerializer, TextSerializer
from guilogacore_rpc.amqp.utils import ClientConnector

CONNECTOR = ClientConnector()


@faas_producer(con=CONNECTOR, faas_name='foobar_sum', req_sz=JsonSerializer)
def foobar_sum(sum_body):
    """
    This is a ProxyRequest constructor that will pass through an RPC call to a server.
    It will call the foobar_sum FaaS with :class:`JsonSerializer` as request serializer type,
    as it requires it to parse properly the request object on server side.

    :param sum_body: (dict) the body of the sum.
        .e.g {'foo': 1, 'bar': 2}
    :return: ProxyResponse
    """
    return ProxyRequest(object_=sum_body)


@faas_producer(con=CONNECTOR, faas_name='foobar_count', req_sz=TextSerializer)
def foobar_count(sentence: str = 'My name is foo and I love bars'):
    """
    This is a ProxyRequest constructor that will pass through an RPC call to a server.
    It will call the foobar_sum function with :class:`JsonSerializer` as request serializer type,
    as it requires it to parse the request object.

    :param sentence: the sentence to be parsed.
    :return: ProxyResponse
    """
    return ProxyRequest(object_=sentence)
