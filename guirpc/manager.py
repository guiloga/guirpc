import os

import click

from guirpc.commands.init import initconsumer, initproducer, createconfig
from guirpc.commands.run import runconsumer

WORKING_DIR = os.getcwd()


@click.group()
def amqp_manager():
    pass


cli_manager = click.CommandCollection(
    help="##### guirpc (alias 'guirpc') #####\n\n"
         "This is a command line manager to start, run and test RPC consumers and producers.",
    sources=[amqp_manager, ])


@amqp_manager.command('runconsumer')
@click.option('-c', '--with-config',
              envvar='CONSUMER_CONFIG_FILEPATH',
              help='the .ini configuration file path to run the consumer. '
                   'Default value gets CONSUMER_CONFIG_FILEPATH environment variable.')
def run_consumer(with_config, **options):
    """Run an RPC server/consumer."""
    runconsumer(with_config, **options)


@amqp_manager.command('initconsumer')
@click.argument('app_name')
@click.option('-E', '--exchange', help='the exchange name.', default='rpc_gateway')
@click.option('-t', '--exchange-type', help='the exchange type.', default='direct')
@click.option('-q', '--queue', help='the queue name.', default='my_queue')
@click.option('-r', '--routing-key', help='the routing key.', default='my_queue')
@click.option('-p', '--prefetch-count', type=int, help='the QOS prefetch count.', default=1)
@click.option('-U', '--connect',
              help='the RabbitMQ server url to connect to "user:password@host:port".',
              default='guest:guest@localhost:5672')
def init_consumer(app_name, **options):
    """Starts an RPC server/consumer application."""
    initconsumer(WORKING_DIR, app_name, **options)


@amqp_manager.command('initproducer')
@click.argument('app_name')
@click.option('-p', '--producer-id', help='the application producer id.', default='')
@click.option('-E', '--exchange', help='the exchange name.', default='rpc_gateway')
@click.option('-r', '--routing-key', help='the routing key.', default='my_queue')
@click.option('-C', '--consumer', help='the response consumer.', default='')
@click.option('-U', '--connect',
              help='the RabbitMQ server url to connect to "user:password@host:port".',
              default='guest:guest@localhost:5672')
def init_producer(app_name, **options):
    """Starts an RPC client/consumer application."""
    initproducer(WORKING_DIR, app_name, **options)


@amqp_manager.command('createconfig')
@click.argument('name')
@click.option('--client', is_flag=True,
              help='With this flag it generates a client configuration file. Defaults server.')
@click.option('-o', '--out-dir', help='the target directory.', default='')
def create_config(name, **options):
    """Creates a server or client INI configuration file with default values."""
    createconfig(name, **options)


@amqp_manager.command('publishone')
@click.argument('exchange')
@click.argument('routing_key')
@click.argument('message')
def publish_one(exchange, routing_key, message):
    """Sends a single RPC call with specified routing. (Not implemented yet)"""
    pass


def main():
    cli_manager()


if __name__ == '__main__':
    main()
