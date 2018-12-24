import collections
import inspect
from importlib import import_module
from pkgutil import iter_modules


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


def iter_classes(module_path, base_class, include_base_class=False, skip_fail=True):
    for module in walk_modules(module_path, skip_fail=skip_fail):
        for obj in vars(module).values():
            if inspect.isclass(obj) and \
                    issubclass(obj, base_class) and \
                    obj.__module__ == module.__name__ and \
                    (include_base_class or
                     all([obj != base for base in base_class])
                     if isinstance(base_class, tuple)
                     else obj != base_class):
                yield obj


def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d
