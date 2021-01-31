import hashlib
import importlib
import os
from typing import Dict

import pika
from pika.exceptions import ConnectionWrongStateError

from .providers import ProducerConfiguration

DEFAULT_CONFIG_ENVAR = 'PRODUCER_CONFIG_FILEPATH'


def get_producer_config(envar: str = DEFAULT_CONFIG_ENVAR) -> ProducerConfiguration:
    try:
        config_path = os.environ[envar]
        config = ProducerConfiguration.get_instance(config_path)
    except Exception as err:
        raise Exception(
            f'An error occurred in "get_producer_config":\n'
            f'*** {err.__class__.__name__} ***\n{err}')

    return config


class ClientConnector:
    CONFIG: Dict[str, ProducerConfiguration] = dict()
    BCK_CON: Dict[str, pika.BlockingConnection] = dict()

    initialized_clients = []

    def __init__(self, config_envar: str = DEFAULT_CONFIG_ENVAR):
        self._config_envar = config_envar

        if not self.is_initialized:
            self.reload()
            ClientConnector.initialized_clients.append(self.client_id)

        self._set_attributes()

        if self.is_reload_required:
            self.reload()

    @property
    def bck_con(self):
        return self._bck_con

    @property
    def config(self):
        return self._config

    @property
    def client_id(self):
        md5 = hashlib.md5(self._config_envar.lower().encode())
        return md5.hexdigest()

    @property
    def is_initialized(self):
        return self.client_id in ClientConnector.initialized_clients

    @property
    def is_reload_required(self):
        if not self._bck_con.is_open:
            return True
        return False

    def _set_attributes(self):
        self._bck_con = ClientConnector.BCK_CON[self.client_id]
        self._config = ClientConnector.CONFIG[self.client_id]

    def reload(self):
        config = get_producer_config(self._config_envar)
        ClientConnector.CONFIG.update(
            {self.client_id: config})
        ClientConnector.BCK_CON.update(
            {self.client_id: self.open_bck_con(config.con_params.amqp_url)})

        self._set_attributes()

    @classmethod
    def close_all_connections(cls):
        for id_, con in cls.BCK_CON.items():
            try:
                con.close()
            except ConnectionWrongStateError:
                pass

    @classmethod
    def restore(cls):
        cls.close_all_connections()

        cls.BCK_CON = dict()
        cls.CONFIG = dict()

    @staticmethod
    def open_bck_con(amqp_url: str):
        return pika.BlockingConnection(
            pika.URLParameters(amqp_url))


def import_serializer(class_name):
    module = importlib.import_module(
        'guirpc.amqp.serializers')
    try:
        class_ = getattr(module, class_name)
    except AttributeError as err:
        raise Exception(
            f'An error occurred in "import_serializer":\n'
            f'*** {err.__class__.__name__} ***\n{err}')

    return class_
