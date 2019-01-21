import collections
import inspect
import re
import types
from enum import Enum
from importlib import import_module
from logging import _nameToLevel
from pkgutil import iter_modules
from pydantic import BaseModel

LogLevel = Enum('LogLevel', [(k, k) for k in _nameToLevel], type=str)
LogLevel.__repr__ = lambda x: x.name


class NamedModel(BaseModel):
    name: str

    class Config:
        allow_extra = True


def normalize_slash(tag, with_prefix_slash=True):
    tag = re.sub('[/]+', '/', tag)

    if with_prefix_slash and not tag.startswith('/'):
        tag = '/' + tag

    return tag


def walk_modules(module_path, skip_fail=True):

    mod = None
    try:
        mod = import_module(module_path)
        yield mod
    except Exception as e:
        if not skip_fail:
            raise e

    if mod and hasattr(mod, '__path__'):
        for _, subpath, _ in iter_modules(mod.__path__):
            fullpath = '.'.join((module_path, subpath))
            for m in walk_modules(fullpath, skip_fail):
                yield m


def expected_cls(module, cls, base_class, include_base_class=False):
    if inspect.isclass(cls) and \
            issubclass(cls, base_class) and \
            cls.__module__ == module.__name__ and \
            (include_base_class or
             all([cls != base for base in base_class])
             if isinstance(base_class, tuple)
             else cls != base_class):
        return True
    return False


def load_class(class_path, base_class, include_base_class=False, package=None):
    module_path, class_name = class_path.rsplit('.', 1)
    module = import_module(module_path, package=package)
    cls = getattr(module, class_name)
    if expected_cls(module, cls, base_class, include_base_class):
        return cls
    return None


def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def load_module_from_pyfile(filename):
    module = types.ModuleType('config')
    module.__file__ = filename
    try:
        with open(filename) as config_file:
            exec(compile(config_file.read(), filename, 'exec'),
                 module.__dict__)
    except IOError as e:
        e.strerror = 'Unable to load configuration file (%s)' % e.strerror
        raise
    return module
