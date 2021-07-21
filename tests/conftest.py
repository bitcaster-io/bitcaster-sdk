import pytest
import responses


class FakeRequestsMock:
    fake = True

    def add_callback(self, *args, **kwargs):
        pass

    def add(self, *args, **kwargs):
        pass


class BitcasterRequestsMock:
    fake = True

    def add_callback(self, *args, **kwargs):
        pass

    def add(self, *args, **kwargs):
        pass


@pytest.fixture
def mocked_responses():
    yield FakeRequestsMock()
    # with responses.RequestsMock() as rsps:
    #     yield rsps
