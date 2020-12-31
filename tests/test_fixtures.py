import pytest

from guilogacore_rpc.amqp.domain.exceptions import SerializationError
from guilogacore_rpc.amqp.domain.objects import ProxyResponse
from guilogacore_rpc.amqp.producer import Producer
from guilogacore_rpc.fixtures.producer import client


class TestFixtures:
    @pytest.mark.usefixtures('connector')
    def test_producer_creation(self, connector):
        producer = Producer(connector.bck_con,
                            connector.config.amqp_entities)

        assert producer.connection.is_open
        assert producer.channel.is_open
        assert producer.channel.channel_number == 1

    def test_publish(self):
        x_resp = client.foobar_count()
        assert isinstance(x_resp, ProxyResponse)
        assert x_resp.object is not None

    def test_foobar_sum_ok(self):
        x_resp = client.foobar_sum(2, 3)

        assert isinstance(x_resp, ProxyResponse)
        assert x_resp.status_code == 200
        assert x_resp.object.get('result') == 5

    def test_foobar_sum_server_error(self):
        pass

    def test_foobar_sum_validation_error(self):
        pass

    def test_foobar_count_ok(self):
        x_resp = client.foobar_count(
            'Hello foobar, foo bar foo bar foo bar, total foobar is 10')

        assert isinstance(x_resp, ProxyResponse)
        assert x_resp.status_code == 200
        assert int(x_resp.object) == 10

    def test_foobar_count_serialization_error(self):
        with pytest.raises(SerializationError):
            x_resp = client.foobar_count(
                'Bad sentence, it contains ñ and cannot be encoded into ascii')

    def test_foobar_count_validation_error(self):
        pass
