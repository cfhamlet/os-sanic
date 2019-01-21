EXTENSIONS = [
    {
        'name': 'case02',
        'extension_class': '.extension.Case02Extension'
    }
]

ROUTES = [
    {
        'uri': '/',
        'view_class': '.view.Case02View'
    },
]

STATICS = [
    {
        'uri': '/static',
        'file_or_directory': './static'
    }
]
