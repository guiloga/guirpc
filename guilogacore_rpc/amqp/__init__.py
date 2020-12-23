import pika


def open_connection(blocking=True):
    # TODO: SelectConnection
    return pika.BlockingConnection(
        pika.URLParameters('amqp://guest:guest@localhost:5672/%2F'))
