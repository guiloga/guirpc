import configparser

from guilogacore_rpc.amqp.domain.objects import BrokerConnectionParams, AMQPEntities, ServerOptions


class ConsumerConfiguration:
    def __init__(self, verbose_name: str, faas_app: str, broker_connection: BrokerConnectionParams,
                 amqp_entities: AMQPEntities, server_options: ServerOptions):
        self.verbose_name = verbose_name
        self.faas_app = faas_app
        self.con_params = broker_connection
        self.amqp_entities = amqp_entities
        self.server_options = server_options

    @classmethod
    def get_instance(cls, filepath: str):
        """
        Factory function to create an instance from read configuration data.

        :rtype: ConsumerConfiguration
        """
        config_data = read_config_ini(filepath)
        # params_data = config_data['params']
        return cls(
            verbose_name=config_data['FaaS']['verbose_name'],
            faas_app=config_data['FaaS']['faas_app'],
            broker_connection=BrokerConnectionParams.create(
                config_data['broker_connection']),
            amqp_entities=AMQPEntities.create(
                config_data['amqp_entities']),
            server_options=ServerOptions.create(
                config_data['server_options']),
        )


def read_config_ini(filepath: str) -> dict:
    config = configparser.ConfigParser()
    config.read(filepath)
    return convert_config_to_dict(config)


def convert_config_to_dict(config: configparser.ConfigParser) -> dict:
    dict_config = {}
    for section in config.sections():
        dict_section = {}
        for key, value in config[section].items():
            dict_section[key] = value
        dict_config[section] = dict_section

    return dict_config
