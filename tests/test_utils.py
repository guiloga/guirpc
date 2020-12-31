import pytest

from guilogacore_rpc.amqp.utils import get_producer_config, ClientConnector
from guilogacore_rpc.amqp.providers import ProducerConfiguration


def test_get_producer_config():
    config = get_producer_config()
    assert isinstance(config, ProducerConfiguration)


class TestClientConnector:
    @pytest.mark.usefixtures('connector')
    def test_creation(self, connector):
        connector2 = ClientConnector()

        assert connector.is_initialized
        assert connector2.is_initialized
        assert connector.config == connector2.config
        assert connector.bck_con == connector2.bck_con

    @pytest.mark.usefixtures('connector')
    def test_reload_client(self, connector):
        ClientConnector.close_all_connections()
        assert connector.is_reload_required

        config_hash = connector.config.__hash__()
        bck_con_hash = connector.bck_con.__hash__()
        connector.reload()

        assert connector.is_reload_required is False
        assert connector.config.__hash__() != config_hash
        assert connector.bck_con.__hash__() != bck_con_hash

    def test_open_bck_con(self):
        config = get_producer_config()
        bck_con = ClientConnector.open_bck_con(
            config.con_params.amqp_url)

        assert bck_con.is_open
