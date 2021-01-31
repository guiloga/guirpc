from .domain.mixins import AppConfigMixin
from .domain.objects import BrokerConnectionParams, AMQPEntities, ServerOptions, ClientOptions


class ConsumerConfiguration(AppConfigMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def get_instance(cls, filepath: str):
        """
        Factory function to create an instance from read configuration data.

        :rtype: ConsumerConfiguration
        """
        config_data = cls.read_config_ini(filepath)
        return cls(
            verbose_name=config_data['server']['verbose_name'],
            root=config_data['server']['root'],
            broker_connection=BrokerConnectionParams.create(
                config_data['server.connection']),
            amqp_entities=AMQPEntities.create(
                config_data['server.amqp_entities']),
            options=ServerOptions.create(
                config_data['server.options']),
        )


class ProducerConfiguration(AppConfigMixin):
    def __init__(self, producer_application_id: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.producer_application_id = producer_application_id

    @classmethod
    def get_instance(cls, filepath: str):
        """
        Factory function to create an instance from read configuration data.

        :rtype: ProducerConfiguration
        """
        config_data = cls.read_config_ini(filepath)
        return cls(
            verbose_name=config_data['client']['verbose_name'],
            root=config_data['client']['root'],
            producer_application_id=config_data['client']['producer_application_id'],
            broker_connection=BrokerConnectionParams.create(
                config_data['client.connection']),
            amqp_entities=AMQPEntities.create(
                config_data['client.amqp_entities']),
            options=ClientOptions.create(
                config_data['client.options']),
        )
