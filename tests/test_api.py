import pytest

from bitcaster_sdk.exceptions import ConfigurationError


def test_trigger(client_setup, response_trigger):
    import bitcaster_sdk

    bitcaster_sdk.trigger("a1")


#
@pytest.mark.parametrize("bae", ["", "aa", "ftp://example.com", "https://example.com"])
def test_init_error(bae):
    import bitcaster_sdk

    with pytest.raises(ConfigurationError):
        bitcaster_sdk.init(bae)


@pytest.mark.parametrize("bae", ["https://token@example.com/api/o/ORG/p/PRJ/a/APP"])
def test_init_success(bae):
    import bitcaster_sdk

    bitcaster_sdk.init(bae)
