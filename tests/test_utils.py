from os_sanic.utils import deep_update


def test_deep_update():
    a = {'a': {'b': 1}}
    b = {'a': {'b': 2}}

    deep_update(a, b)
    assert a['a']['b'] == 2
