import configparser
import os
from shutil import copytree, rmtree, ignore_patterns
import time


FIXTURES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'fixtures')


CONSUMER_INI = """
[server]
verbose_name: {app_name} - RPC Consumer
root: {app_name}/server.py

[server.connection]
host = localhost
port = 5672
user = guest
password = guest

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
verbose_name: {app_name} - RPC Producer
root: {app_name}/client.py

[client.connection]
host = localhost
port = 5672
user = guest
password = guest

[client.amqp_entities]
exchange = {exchange}
routing_key = {routing_key}

[client.options]
response_consumer = {consumer}
"""


def initconsumer(work_dir, app_name, **options):
    _cmd_handler(
        'consumer', work_dir, app_name, CONSUMER_INI, options)


def initproducer(work_dir, app_name, **options):
    _cmd_handler(
        'producer', work_dir, app_name, PRODUCER_INI, options)


def _cmd_handler(fixture, work_dir, app_name, config_ini, options):
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

    config = configparser.ConfigParser(allow_no_value=True)
    config.read_string(
        config_ini.format(app_name=app_name, **options))
    with open(f'{app_name}.ini', 'w') as configfile:
        config.write(configfile)
