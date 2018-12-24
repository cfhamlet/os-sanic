from sanic.config import Config as SanicConfig


class Config(SanicConfig):

    def __init__(self, defaults=None, load_env=True, keep_alive=True):
        super(Config, self).__init__(defaults=defaults,
                                     load_env=load_env,
                                     keep_alive=keep_alive)
        self.LOGO = None
