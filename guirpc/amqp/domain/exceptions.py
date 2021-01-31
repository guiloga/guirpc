class ConsumerConfigurationError(Exception):
    def __str__(self):
        return 'An error occurred while trying to read consumer configuration.'


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
