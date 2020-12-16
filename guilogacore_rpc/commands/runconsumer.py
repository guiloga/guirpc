import importlib
import logging
import os
import sys
import time

from guilogacore_rpc.amqp.domain.exceptions import ConsumerConfigurationError
from guilogacore_rpc.amqp.consumers import ProxyReconnectConsumer
from guilogacore_rpc.amqp.providers import ConsumerConfiguration

LOG_FORMAT = ('%(asctime)s [%(levelname)s] %(message)s')

APP_MODULE_NAME = None
FaaS_MODULE = None


def _set_app_module_to_path(app_file):
    dir_abspath = os.path.dirname(
        os.path.abspath(app_file))

    global APP_MODULE_NAME
    APP_MODULE_NAME = os.path.basename(dir_abspath)

    if APP_MODULE_NAME not in sys.path:
        sys.path.append(APP_MODULE_NAME)


def _import_faas_module():
    global FaaS_MODULE
    FaaS_MODULE = importlib.import_module(
        f'{APP_MODULE_NAME}.faas')


def find_registered_faas(app_file):
    _set_app_module_to_path(app_file)
    _import_faas_module()

    registered_faas = {}
    attr_names = [item for item in FaaS_MODULE.__dict__ if item[:2] != '__']
    for name in attr_names:
        attr_ = getattr(FaaS_MODULE, name)
        if attr_.__qualname__ == 'register_faas.<locals>.exec_wrapper.<locals>._exec':
            registered_faas[name] = attr_

    return registered_faas


class ConfigININotProvidedError(Exception):
    def __str__(self):
        return 'The .ini configuration file has not been provided. ' \
            'Set CONSUMER_CONFIG_FILEPATH environment variable ' \
            'or provide it using the "--with-config" option.'


def main(*args):
    with_config = args[0]
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    config_filepath = with_config or os.getenv('CONSUMER_CONFIG_FILEPATH')
    if not config_filepath:
        raise ConfigININotProvidedError

    try:
        cs_conf = ConsumerConfiguration.get_instance(config_filepath)
    except Exception:
        raise ConsumerConfigurationError

    callables = find_registered_faas(cs_conf.faas_app)
    consumer = ProxyReconnectConsumer(
        faas_callables=callables,
        amqp_url=cs_conf.con_params.amqp_url,
        amqp_entities=cs_conf.amqp_entities,
        **cs_conf.server_options.as_dict)

    logger = logging.getLogger('consumer')
    logger.info('*' * 12 + ' Running foobar - RPC Consumer ' + '*' * 12)
    time.sleep(.5)
    for name in callables.keys():
        logger.info('#' * 3 + ' registered FaaS: %s' % name)
    time.sleep(.3)
    consumer.run()
