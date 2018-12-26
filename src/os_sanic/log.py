from sanic.log import logger
import logging


def getLogger(name):
    lg = logging.getLogger(name)
    if logger.hasHandlers():
        lg.addHandler(logger.handlers[0])
    lg.setLevel(logger.level)
    return lg


LOGGING_CONFIG_PATCH = dict(

    formatters={
        "generic": {
            "format": "%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S]",
        },
    }
)

BASE_LOGGING = {
    **LOGGING_CONFIG_PATCH['formatters']['generic']
}
