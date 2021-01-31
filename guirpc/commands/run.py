import logging
import logging.config
import os
from importlib import util

import yaml

from guirpc.amqp.consumer import ProxyReconnectConsumer
from guirpc.amqp.domain.exceptions import ConsumerConfigurationError
from guirpc.amqp.providers import ConsumerConfiguration

RESOURCES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'resources')

FaaS_MODULE = None


def _read_log_config():
    filename = os.path.join(RESOURCES_DIR, 'logging.yaml')
    with open(filename, 'r') as file:
        log_config = yaml.safe_load(file)
    return log_config


def _configure_logging():
    logging.config.dictConfig(_read_log_config())

    logging.addLevelName(logging.CRITICAL, 'critical')
    logging.addLevelName(logging.ERROR, 'error')
    logging.addLevelName(logging.WARNING, 'warning')
    logging.addLevelName(logging.INFO, 'info')
    logging.addLevelName(logging.DEBUG, 'debug')


def _import_faas_module(app_file):
    global FaaS_MODULE

    spec = util.spec_from_file_location('faas_module', app_file)
    FaaS_MODULE = util.module_from_spec(spec)
    spec.loader.exec_module(FaaS_MODULE)


def find_registered_faas(app_file):
    err = _import_faas_module(app_file)

    registered_faas = dict()

    if not err:
        attr_names = [item for item in FaaS_MODULE.__dict__ if item[:2] != '__']
        for name in attr_names:
            attr_ = getattr(FaaS_MODULE, name)
            try:
                if attr_.__qualname__ == 'register_faas.<locals>.exec_wrapper.<locals>._exec':
                    registered_faas[name] = attr_
            except AttributeError:
                pass

    return registered_faas, err


class ConfigININotProvidedError(Exception):
    def __str__(self):
        return 'The .ini configuration file has not been provided. ' \
               'Set CONSUMER_CONFIG_FILEPATH environment variable ' \
               'or provide it using the "--with-config" option.'


def runconsumer(with_config, **options):
    _configure_logging()
    logger = logging.getLogger('rpcServer')

    config_filepath = with_config
    if not config_filepath:
        raise ConfigININotProvidedError

    try:
        cs_conf = ConsumerConfiguration.get_instance(config_filepath)
    except Exception:
        raise ConsumerConfigurationError

    callables, err = find_registered_faas(cs_conf.root)
    if not err:
        consumer = ProxyReconnectConsumer(
            faas_callables=callables,
            amqp_url=cs_conf.con_params.amqp_url,
            amqp_entities=cs_conf.amqp_entities,
            **cs_conf.options.as_dict)

        logger.info('*' * 16 + f' {cs_conf.verbose_name} ' + '*' * 16)
        for name in callables.keys():
            logger.info('#' * 3 + ' registered FaaS: %s' % name)
        consumer.run()
    else:
        logger.info(f'An error occurred while loading consumer application: {err}')
