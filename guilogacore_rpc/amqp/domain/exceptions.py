class ConsumerConfigurationError(Exception):
    def __str__(self):
        return 'An error occurred while trying to read consumer configuration.'
