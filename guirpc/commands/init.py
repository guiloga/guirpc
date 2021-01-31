import configparser
import os
import time
from shutil import copytree, rmtree, ignore_patterns

from . import read_config_defaults

FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'fixtures')

CONFIG_DEFAULTS = read_config_defaults()

CONSUMER_INI = """
[server]
verbose_name: {app_name} - RPC Consumer
root: {app_name}/server.py

[server.connection]
host = {host}
port = {port}
user = {user}
password = {password}

[server.amqp_entities]
exchange = {exchange}
exchange_type = {exchange_type}
queue = {queue}
routing_key = {routing_key}

[server.options]
prefetch_count = {prefetch_count}
"""

PRODUCER_INI = """
[client]
verbose_name = {app_name} - RPC Producer
root = {app_name}/client.py
producer_application_id = {producer_id}

[client.connection]
host = {host}
port = {port}
user = {user}
password = {password}

[client.amqp_entities]
exchange = {exchange}
routing_key = {routing_key}

[client.options]
response_consumer = {consumer}
"""


def initconsumer(work_dir, app_name, **options):
    _init_cmd_handler(
        'consumer', work_dir, app_name, CONSUMER_INI, options)


def initproducer(work_dir, app_name, **options):
    _init_cmd_handler(
        'producer', work_dir, app_name, PRODUCER_INI, options)


def createconfig(name, **options):
    client_flag = options.get('client', False)
    out_dir = options.get('out_dir', '')
    print("Creating {0} config INI named '{1}.ini'..".format(
        'client' if client_flag else 'server',
        name))

    try:
        if client_flag:
            values = {**CONFIG_DEFAULTS['producer_config']['globals'],
                      **CONFIG_DEFAULTS['producer_config']['amqp_entities'],
                      **CONFIG_DEFAULTS['producer_config']['options']}
            _create_config_file(name, PRODUCER_INI, values, out_dir)
        else:
            values = {**CONFIG_DEFAULTS['consumer_config']['amqp_entities'],
                      **CONFIG_DEFAULTS['consumer_config']['options']}
            _create_config_file(name, CONSUMER_INI, values, out_dir)
    except Exception as error:
        print(f"An error occurred: '{error.__class__.__name__} -> {error}'")


def _init_cmd_handler(fixture, work_dir, app_name, config_ini, options):
    print(f"Initializing {fixture} '{app_name}'..")
    time.sleep(.5)

    src = os.path.join(FIXTURES_DIR, fixture)
    dest = os.path.join(work_dir, app_name)
    try:
        copytree(src, dest,
                 ignore=ignore_patterns('*.pyc', 'tmp*'),
                 ignore_dangling_symlinks=True)
    except Exception as error:
        print(f'An error occurred: {error}')
        rmtree(dest)
        return

    _create_config_file(app_name, config_ini, options)


def _create_config_file(name: str, config_ini: str, format_values: dict, out_dir: str = ''):
    url = format_values.pop('connect',
                            'guest:guest@localhost:5672')
    splitted_url = url.split('@')
    user, password = splitted_url[0].split(':')
    host, port = splitted_url[1].split(':')
    format_values.update({'user': user,
                          'password': password,
                          'host': host,
                          'port': port})

    config = configparser.ConfigParser(allow_no_value=True)
    config.read_string(
        config_ini.format(app_name=name, **format_values))

    filename = os.path.join(out_dir, f'{name}.ini')
    if not os.path.isfile(filename):
        with open(filename, 'w') as configfile:
            config.write(configfile)
    else:
        print(f"Error: file '{filename}' already exists.")
