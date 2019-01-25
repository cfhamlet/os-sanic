EXTENSIONS = [
    {
        'name': 'case01',
        'extension_class': '.extension.Case01Extension'
    }
]

ROUTES = [
    ('/', '.view.Case01View'),
    {
        'uri': '/config',
        'handler': '.view.Case02View',
        'key01': 'value01',
    }
]
