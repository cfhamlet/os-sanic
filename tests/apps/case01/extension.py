from os_sanic.extension import Extension


class Case01Extension(Extension):
    def test(self):
        return 'Case01'
