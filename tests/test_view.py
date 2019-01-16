import json


def test_001(os_sanic_server):
    server = os_sanic_server(
        'test', None, 'tests.apps.case01')
    _, response = server.sanic.test_client.get('/case01')
    assert response.status == 200
    assert json.loads(response.body) == {'view': 'Case01'}


def test_002(os_sanic_server):
    server = os_sanic_server(
        'test', None, 'tests.apps.case01', 'tests.apps.case02')

    _, response = server.sanic.test_client.get('/case02')
    assert response.status == 200
    assert json.loads(response.body) == {'view': 'Case01'}


def test_003(os_sanic_server):
    server = os_sanic_server(
        'test', None,  'tests.apps.case02')

    _, response = server.sanic.test_client.get('/case02/static/hello.txt')
    assert response.status == 200
    assert response.body == b'hello'
