from guilogacore_rpc.amqp.domain.objects import ProxyRequest
from guilogacore_rpc.amqp.decorators import faas_producer
from guilogacore_rpc.amqp.serializers import JsonSerializer, TextSerializer
from guilogacore_rpc.amqp.utils import ClientConnector

CONNECTOR = ClientConnector()


@faas_producer(con=CONNECTOR, faas_name='foobar_sum', req_sz=JsonSerializer)
def foobar_sum(num1: int, num2: int):
    """
    This is a ProxyRequest constructor that will pass through an RPC call to a server.
    It will call the foobar_sum FaaS with :class:`JsonSerializer` as request serializer type,
    as it requires it to parse properly the request object on server side.

    :param num1: number.
    :param num2: number.
    :return: ProxyResponse
    """
    object_ = {'foo': num1, 'bar': num2}
    return ProxyRequest(object_=object_)


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
