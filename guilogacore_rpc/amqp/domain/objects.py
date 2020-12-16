from typing import Any


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
            prefetch_count=int(object_data.get('prefetch_count')),
        )

    @property
    def as_dict(self):
        return dict(
            prefetch_count=self.prefetch_count,
        )


class ProxyObject:
    def __init__(self, object_):
        self.__object = object_

    @property
    def object(self) -> Any:
        return self.__object


class PropertiesMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._encoding = None
        self._bytes = None
        self._content_type = None
        self._message_headers = None

    def set_properties(self, bytes_: bytes, encoding: str, content_type: str,
                       message_headers: dict):
        self._bytes = bytes_
        self._encoding = encoding
        self._content_type = content_type
        self._message_headers = message_headers

    @property
    def bytes(self):
        return self._bytes

    @property
    def content(self):
        ct = self._bytes.decode(encoding=self._encoding) if self._bytes else None
        return ct

    @property
    def content_type(self):
        return self._content_type

    @property
    def message_headers(self):
        return self._message_headers


class ProxyRequest(PropertiesMixin, ProxyObject):
    def __init__(self, app_id: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app_id = app_id

    @property
    def app_id(self):
        return self._app_id


class ProxyResponse(PropertiesMixin, ProxyObject):
    def __init__(self, status_code: int = 200, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._status_code = status_code
        self._error_message = None

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
