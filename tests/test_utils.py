from os_sanic.utils import deep_update, normalize_slash


def test_normalize_prefix():
    data = [
        ('/', '/'),
        ('a/', '/a/'),
        ('//a', '/a'),
        ('/a//', '/a/'),
        ('', '/'),
        ('/a', '/a'),
        ('/a///c', '/a/c'),
    ]

    for raw, expect in data:
        assert normalize_slash(raw) == expect


def test_deep_update():
    a = {'a': {'b': 1}}
    b = {'a': {'b': 2}}

    deep_update(a, b)
    assert a['a']['b'] == 2
