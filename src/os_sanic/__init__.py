import pkgutil
import sys
from os_sanic.manage import run


__all__ = ['__version__', 'version_info', 'run']

__version__ = pkgutil.get_data(__package__, 'VERSION').decode('ascii').strip()
version_info = tuple(int(v) if v.isdigit() else v
                     for v in __version__.split('.'))


del pkgutil
del sys
