from guilogacore_rpc.amqp.domain.objects import ProxyRequest
from guilogacore_rpc.amqp.decorators import faas_producer
from guilogacore_rpc.amqp import open_connection



CONFIG = None
BK_CON = open_connection()


@faas_producer(con=BK_CON, faas_name='foobar_sum')
def foobar_sum(num1, num2, *args, **kwargs) -> ProxyRequest:
    object_ = {'foo': num1, 'bar': num2}
    return ProxyRequest(object_=object_)


@faas_producer(con=BK_CON, faas_name='foobar_count')
def foobar_count(sentence, *args, **kwargs) -> ProxyRequest:
    return ProxyRequest(object_=sentence)
