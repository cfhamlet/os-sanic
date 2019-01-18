EXTENSIONS = [
    {
        'name': 'case01',
        'extension_class': '.extension.Case01Extension'
    }
]

VIEWS = [
    ('/', '.view.Case01View'),
    {
        'uri': '/config',
        'view_class': '.view.Case02View',
        'key01': 'value01',
    }
]
