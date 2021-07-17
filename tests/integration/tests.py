import pytest

from guirpc.amqp.domain import ProxyResponse
from guirpc.amqp.domain.exceptions import SerializationError
from guirpc.amqp.producer import Producer
from guirpc.amqp.utils import get_producer_config, ClientConnector
from guirpc.fixtures.producer import client


class TestProducer:
    @pytest.mark.usefixtures("connector")
    def test_producer_creation(self, connector):
        producer = Producer(connector.bck_con, connector.config.amqp_entities)

        assert producer.connection.is_open
        assert producer.channel.is_open
        assert producer.channel.channel_number == 1

    def test_publish(self):
        x_resp = client.foobar_count()
        assert isinstance(x_resp, ProxyResponse)
        assert x_resp.object is not None


class TestFixtures:
    def test_foobar_sum_ok(self):
        sum_body = {"foo": 2, "bar": 3}
        x_resp = client.foobar_sum(sum_body)

        assert isinstance(x_resp, ProxyResponse)
        assert x_resp.status_code == 200
        assert x_resp.object.get("result") == 5

    def test_foobar_sum_error(self):
        sum_body = {"foo": 3}
        x_resp = client.foobar_sum(sum_body)

        assert isinstance(x_resp, ProxyResponse)
        assert x_resp.is_error
        assert x_resp.status_code == 400

    def test_foobar_count_ok(self):
        x_resp = client.foobar_count(
            "Hello foobar, foo bar foo bar foo bar, total foobar"
        )

        assert isinstance(x_resp, ProxyResponse)
        assert x_resp.status_code == 200
        assert int(x_resp.object) == 10

    def test_foobar_count_error(self):
        x_resp = client.foobar_count("foo hello")

        assert isinstance(x_resp, ProxyResponse)
        assert x_resp.is_error
        assert x_resp.status_code == 400

    def test_foobar_count_serialization_error(self):
        with pytest.raises(SerializationError):
            try:
                client.foobar_count(
                    "Bad sentence, "
                    "it contains ñ and cannot be encoded into ascii"
                )
            except SerializationError as err:
                assert err.__str__()
                raise

    @pytest.mark.usefixtures("raw_obj")
    @pytest.mark.skip
    def test_foobar_raw(self, raw_obj):
        x_resp = client.foobar_raw(raw_obj)

        assert isinstance(x_resp, ProxyResponse)
        assert x_resp.status_code == 200
        assert isinstance(x_resp.object, raw_obj.__class__)
        assert raw_obj != x_resp.object

    def test_error_faas_not_registered(self):
        pass

    def test_connection_is_open_decorator(self):
        client.CONNECTOR.close_all_connections()
        assert client.CONNECTOR.bck_con.is_closed
        _ = client.foobar_count()
        assert client.CONNECTOR.bck_con.is_open


class TestClientConnector:
    @pytest.mark.usefixtures("connector")
    def test_creation(self, connector):
        connector.reload()
        connector2 = ClientConnector()

        assert connector.is_initialized
        assert connector2.is_initialized
        assert connector.config == connector2.config
        assert connector.bck_con == connector2.bck_con

    @pytest.mark.usefixtures("connector")
    def test_reload(self, connector):
        config_hash = connector.config.__hash__()
        bck_con_hash = connector.bck_con.__hash__()
        connector.reload()

        assert connector.is_reload_required is False
        assert connector.config.__hash__() != config_hash
        assert connector.bck_con.__hash__() != bck_con_hash

    def test_open_bck_con(self):
        config = get_producer_config()
        bck_con = ClientConnector.open_bck_con(config.con_params.amqp_url)

        assert bck_con.is_open
