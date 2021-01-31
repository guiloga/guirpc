from typing import Any

from .mixins import MessagePropertiesMixin


class BrokerConnectionParams:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    @classmethod
    def create(cls, object_data: dict):
        """
        Factory function to create an instance from dict data.

        :param dict object_data: connection data.
        :rtype: BrokerConnectionParams
        """
        return cls(
            host=object_data.get('host'),
            port=object_data.get('port'),
            user=object_data.get('user'),
            password=object_data.get('password'),
        )

    @property
    def amqp_url(self):
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/%2F"


class AMQPEntities:
    def __init__(self, exchange, exchange_type: str = 'direct', queue: str = '',
                 routing_key: str = ''):
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.queue = queue
        self.routing_key = routing_key

    @classmethod
    def create(cls, object_data: dict):
        """
        Factory function to create an instance from dict data.

        :param dict object_data: routing params data.
        :rtype: AMQPEntities
        """
        return cls(
            exchange=object_data.get('exchange'),
            exchange_type=object_data.get('exchange_type', 'direct'),
            queue=object_data.get('queue', ''),
            routing_key=object_data.get('routing_key', ''),
        )


class ServerOptions:
    def __init__(self, prefetch_count: int = 1):
        self.prefetch_count = prefetch_count

    @classmethod
    def create(cls, object_data: dict):
        """
        Factory function to create an instance from dict data.

        :param dict object_data: options data.
        :rtype: ServerOptions
        """
        return cls(
            prefetch_count=int(object_data.get('prefetch_count', 1)),
        )

    @property
    def as_dict(self):
        return dict(
            prefetch_count=self.prefetch_count,
        )


class ClientOptions:
    def __init__(self, response_consumer: str = ''):
        self.response_consumer = response_consumer

    @classmethod
    def create(cls, object_data: dict):
        """
        Factory function to create an instance from dict data.

        :param dict object_data: options data.
        :rtype: ClientOptions
        """
        return cls(
            response_consumer=object_data.get('response_consumer', ''),
        )

    @property
    def as_dict(self):
        return dict(
            response_consumer=self.response_consumer,
        )


class ProxyObject:
    def __init__(self, object_: Any = None):
        self.__object = object_

    @property
    def object(self) -> Any:
        return self.__object


class ProxyRequest(MessagePropertiesMixin, ProxyObject):
    def __init__(self, app_id: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app_id = app_id

    @property
    def app_id(self):
        return self._app_id

    @app_id.setter
    def app_id(self, id_):
        self._app_id = id_

    @classmethod
    def create(cls, object_, encoding, content_type, message_headers=None, app_id=None):
        return cls(
            object_=object_,
            encoding=encoding,
            content_type=content_type,
            message_headers=message_headers,
            app_id=app_id
        )


class ProxyResponse(MessagePropertiesMixin, ProxyObject):
    def __init__(self, status_code, *args, error_message: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._status_code = status_code
        self._error_message = error_message

    @property
    def status_code(self):
        return self._status_code

    @status_code.setter
    def status_code(self, st_c: int):
        # TODO: Set it with a factory of STATUS_CODES objects
        self._status_code = st_c

    @property
    def error_message(self):
        return self._error_message

    @error_message.setter
    def error_message(self, err_m: str):
        self._error_message = err_m

    @property
    def is_error(self):
        st_str = str(self._status_code)
        return st_str[:1] in ['5', '4']

    @property
    def is_success(self):
        st_str = str(self._status_code)
        return st_str[:1] == '2'
