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
