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
virtual_host = {vhost}

[server.amqp_entities]
exchange = {exchange}
exchange_type = {exchange_type}
queue = {queue}
routing_key = {routing_key}

[server.options]
max_workers = {max_workers}
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
virtual_host = {vhost}

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
    url = options.get('connect')
    print("Creating {0} config INI named '{1}.ini'..".format(
        'client' if client_flag else 'server',
        name))

    try:
        if client_flag:
            values = {**CONFIG_DEFAULTS['producer_config']['globals'],
                      **CONFIG_DEFAULTS['producer_config']['amqp_entities'],
                      **CONFIG_DEFAULTS['producer_config']['options']}
            config_ini = PRODUCER_INI
        else:
            values = {**CONFIG_DEFAULTS['consumer_config']['amqp_entities'],
                      **CONFIG_DEFAULTS['consumer_config']['options']}
            config_ini = CONSUMER_INI
    except Exception as error:
        print(f"An error occurred: '{error.__class__.__name__} -> {error}'")

    if url:
        values['connect'] = url

    _create_config_file(name, config_ini, values, out_dir)


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
    url = format_values.get('connect')
    if url:
        host, port, user, password, vhost = _parse_amqp_uri(url)
        format_values.update({'user': user,
                              'password': password,
                              'host': host,
                              'port': port,
                              'vhost': vhost})
    else:
        config_ini = _cut_connection_from_config_ini(config_ini)
    config = configparser.ConfigParser(allow_no_value=True)
    config.read_string(
        config_ini.format(app_name=name, **format_values))

    filename = os.path.join(out_dir, f'{name}.ini')
    if not os.path.isfile(filename):
        with open(filename, 'w') as configfile:
            config.write(configfile)
    else:
        print(f"Error: file '{filename}' already exists.")


def _cut_connection_from_config_ini(config_ini: str):
    config_ini = config_ini.replace(
        "\n[server.connection]", "")
    config_ini = config_ini.replace(
        "\n[client.connection]", "")

    config_ini = config_ini.replace(
        "\nhost = {host}\nport = {port}\n"
        "user = {user}\npassword = {password}\n"
        "virtual_host = {vhost}\n", "")

    return config_ini.rstrip()


def _parse_amqp_uri(uri):
    try:
        sp_url = uri.split('@')
        p1 = sp_url[0].replace('amqp://', '').split(':')
        p2 = sp_url[-1].split('/')
        if len(p2) == 1:
            p2 += ['']
        p3 = p2[0].split(':')
    except Exception:
        raise Exception("Invalid connection uri: '%s'", uri)

    return [*p3, *p1, p2[-1] if p2[-1] and p2[-1] != '%2F' else '/']
