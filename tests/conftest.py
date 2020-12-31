from pytest import fixture

from guilogacore_rpc.amqp.utils import ClientConnector


@fixture(scope='session')
def connector():
    return ClientConnector()
