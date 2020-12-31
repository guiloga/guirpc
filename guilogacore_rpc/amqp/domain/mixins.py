import configparser


class AMQPMixin:
    def __init__(self,
                 amqp_entities):
        self._amqp_entities = amqp_entities

    @property
    def amqp_entities(self):
        return self._amqp_entities


class AppConfigMixin:
    def __init__(self, verbose_name, root, broker_connection, amqp_entities, options):
        self.verbose_name = verbose_name
        self.root = root
        self.con_params = broker_connection
        self.amqp_entities = amqp_entities
        self.options = options

    @classmethod
    def read_config_ini(cls, filepath: str) -> dict:
        config = configparser.ConfigParser()
        config.read(filepath)
        return cls.convert_config_to_dict(config)

    @staticmethod
    def convert_config_to_dict(config: configparser.ConfigParser) -> dict:
        dict_config = {}
        for section in config.sections():
            dict_section = {}
            for key, value in config[section].items():
                dict_section[key] = value
            dict_config[section] = dict_section

        return dict_config


class MessagePropertiesMixin:
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

    @bytes.setter
    def bytes(self, bt):
        self._bytes = bt

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, enc):
        self._encoding = enc

    @property
    def content_type(self):
        return self._content_type

    @content_type.setter
    def content_type(self, ctp):
        self._content_type = ctp

    @property
    def message_headers(self):
        return self._message_headers

    def add_headers(self, headers: dict):
        if not self._message_headers:
            self._message_headers = {**headers}
        else:
            self._message_headers.update(headers)
