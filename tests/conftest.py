from pytest import fixture

from guilogacore_rpc.amqp.utils import ClientConnector


@fixture(scope='session')
def connector():
    return ClientConnector()


@fixture(scope="session")
def raw_obj():
    return Foo()


class Foo:
    def __init__(self):
        self.name = 'Foo'
        self.likes = 'Bars'

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
