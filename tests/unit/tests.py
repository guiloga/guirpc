"""
This module covers all unit tests about domain and
infrastructure layers of guirpc.amqp package.
"""

from guirpc.amqp.providers import ProducerConfiguration
from guirpc.amqp.utils import get_producer_config


######################
# DOMAIN Layer Tests #
######################

# objects
class TestBrokerConnectionParams:
    def test_creation(self):
        pass


class TestAMQPEntities:
    def test_creation(self):
        pass


class TestServerOptions:
    def test_creation(self):
        pass


class TestClientOptions:
    def test_creation(self):
        pass


class TestProxyObject:
    def test_creation(self):
        pass


class TestProxyRequest:
    def test_creation(self):
        pass


class TestProxyResponse:
    def test_creation(self):
        pass


# mixins
class TestAppConfigMixin:
    pass


class TestMessagePropertiesMixin:
    pass


# contracts
class TestContracts:
    pass


# encoding
class TestEncoding:
    pass


##############################
# INFRASTRUCTURE Layer Tests #
##############################

# providers
class TestProviders:
    pass


# serializers
class TestSerializers:
    pass


# decorators
class TestDecorators:
    pass


# utils
class TestUtils:
    def test_get_producer_config(self):
        config = get_producer_config()
        assert isinstance(config, ProducerConfiguration)
