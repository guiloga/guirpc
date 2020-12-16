from abc import ABC, abstractmethod

from .objects import AMQPEntities, ProxyObject


class ConsumerInterface(ABC):
    def __init__(self,
                 amqp_url: str,
                 amqp_entities: AMQPEntities,
                 prefetch_count: int = 1):
        """
        Contract/Interface for a consumer class.

        :param str amqp_url: The AMQP url to connect with
            (default is: amqp://guest:guest@localhost:5672/%2F).
        :param AMQPEntities amqp_entities: Params for configured way of amqp_entities
            (exchange, exchange_type, queue and routing_key).
        :param int prefetch_count: the consumer throughput
            (In production, experiment with higher prefetch values).
        """
        self._amqp_url = amqp_url
        self._amqp_entities = amqp_entities
        self._prefetch_count = prefetch_count

    @property
    def amqp_url(self):
        return self._amqp_url

    @property
    def amqp_entities(self):
        return self._amqp_entities

    @property
    def prefetch_count(self):
        return self._prefetch_count

    @abstractmethod
    def run(self):
        """
        The execution of that method will start the RPC server consuming.
        """
        pass


class BaseSerializer(ABC):
    CONTENT_TYPE: str = None
    ENCODING: str = None

    @classmethod
    @abstractmethod
    def serialize(cls, obj: ProxyObject) -> str:
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, obj_str: str) -> ProxyObject:
        pass
