import pytest
from os_sanic.server import Server


@pytest.fixture()
def os_sanic_server():

    def _create(sanic, config, *apps):
        if not config:
            config = {}
        if 'INSTALLED_APPS' not in config:
            config['INSTALLED_APPS'] = []

        config['INSTALLED_APPS'].extend(apps)
        return Server.create(sanic, config)

    yield _create
