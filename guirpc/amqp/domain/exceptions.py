class ConsumerConfigurationError(Exception):
    def __str__(self):
        return 'An error occurred while trying to read consumer configuration.'


class AMQPConnectionURINotSetError(Exception):
    def __str__(self):
        return 'The AMQP_URI environment variable is not set.'


class SerializationError(Exception):
    def __init__(self, object_, sz, error):
        self.object = object_
        self.sz = sz
        self.error = error

    def __str__(self):
        return ('An error occurred while serializing object ' +
                '({0}) "{1}" with serializer: {2}\n'.format(type(self.object),
                                                            self.object,
                                                            self.sz) +
                f'*** {self.error.__class__.__name__} ***\n{self.error}')


class OpeningChannelError(Exception):
    def __init__(self, con):
        self.con = con

    def __str__(self):
        return ('Broker connection is not open when trying to open a new channel; '
                f'connection details are: {self.con.__dict__ if self.con else None}')


class InvalidAMQPConnectionURI(Exception):
    def __init__(self, uri):
        self.uri = uri

    def __str__(self):
        return f'An error occurred while parsing AMQP URI: {self.uri}'