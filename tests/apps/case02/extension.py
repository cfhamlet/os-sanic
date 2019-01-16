from os_sanic.extension import Extension


class Case02Extension(Extension):
    def test(self):
        return 'Case02'
