import logging
import sys

from sanic.log import logger


def getLogger(name):
    lg = logging.getLogger(name)
    if not lg.hasHandlers():
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
    },
    handlers={
        "console": {
            "stream": sys.stderr
        },
        "access_console": {
            "stream": sys.stderr
        },
    },

)

BASE_LOGGING = {
    **LOGGING_CONFIG_PATCH['formatters']['generic']
}
