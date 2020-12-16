import configparser
import os
from shutil import copytree, rmtree, ignore_patterns
from shutil import Error as ShutilError
import time

import click

from guilogacore_rpc.commands.runconsumer import main as main_runconsumer

WORKING_DIR = os.getcwd()
MODULE_DIR = os.path.dirname(__file__)

INITIAL_CONFIG = """
[FaaS]
verbose_name: {app_name} - RPC Consumer
faas_app: {app_name}/faas.py

[broker_connection]
host = localhost
port = 5672
user = guest
password = guest

[amqp_entities]
exchange = {exchange}
exchange_type = {exchange_type}
queue = {queue}
routing_key = {routing_key}

[server_options]
prefetch_count = {prefetch_count}
"""


@click.group()
def amqp_manager():
    pass


@amqp_manager.command('runconsumer')
@click.option('-c', '--with-config',
              envvar='CONSUMER_CONFIG_FILEPATH',
              help='the .ini configuration file path to run the consumer. '
                   'Default value gets CONSUMER_CONFIG_FILEPATH environment variable.')
def run_consumer(with_config):
    """Run an RPC server/consumer.
    """
    args = (with_config,)
    main_runconsumer(*args)


cli_manager = click.CommandCollection(
    help="##### guilogacore-rpc (alias 'gui-rpc') #####\n\n"
         "This is a command line manager to start, run and operate wih consumer/producers.",
    sources=[amqp_manager,])


@amqp_manager.command('initconsumer')
@click.argument('app_name')
@click.option('-e', '--exchange', help='the exchange.', default='rpc_gateway')
@click.option('-t', '--exchange-type', help='the exchange type.', default='direct')
@click.option('-q', '--queue', help='the queue name.', default='my_queue')
@click.option('-r', '--routing-key', help='the routing key.', default='my_queue')
@click.option('-c', '--prefetch-count', type=int, help='the routing key.', default=1)
def init_consumer(app_name, **options):
    print(f"Initializing consumer '{app_name}'..")
    time.sleep(.5)

    src = os.path.join(MODULE_DIR, 'fixtures', 'consumer')
    dest = os.path.join(WORKING_DIR, app_name)
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
        INITIAL_CONFIG.format(app_name=app_name, **options))
    with open(f'{app_name}.ini', 'w') as configfile:
        config.write(configfile)


@amqp_manager.command('initproducer')
# @click.option('')
def init_producer():
    pass


@amqp_manager.command('generateconfig')
# @click.option('')
def generate_config():
    pass


if __name__ == '__main__':
    cli_manager()
