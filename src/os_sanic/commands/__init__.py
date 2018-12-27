import re
import os
from shutil import copy2, copystat, ignore_patterns
import ast
from importlib import import_module
from enum import Enum
from jinja2 import Template

CommandScope = Enum('CommandScoe', 'GLOBAL, PROJECT')


class Command(object):

    scope = CommandScope.GLOBAL
    name = None
    description = ''
    usage = ''
    help = ''

    def add_arguments(self, parser):
        pass

    def process_arguments(self, args):
        pass

    def run(self, args):
        pass


def valid_name(name):
    def _module_exists(module_name):
        try:
            import_module(module_name)
            return True
        except ImportError:
            return False
    try:
        ast.parse('{} = None'.format(name))
    except:
        raise ValueError('Not a valid name: {}'.format(name))

    if name.startswith('_'):
        raise ValueError('Not a valid name: {}'.format(name))
    elif _module_exists(name):
        raise ValueError('Module {} already existed'.format(name))


def copy_tpl(src, dst, ignores=[]):
    if os.path.exists(dst):
        raise IOError('Already existed {}'.format(dst))
    ignore = ignore_patterns(*ignores)
    names = os.listdir(src)
    ignored_names = ignore(src, names)

    if not os.path.exists(dst):
        os.makedirs(dst)

    for name in names:
        if name in ignored_names:
            continue

        src_name = os.path.join(src, name)
        dst_name = os.path.join(dst, name)
        if os.path.isdir(src_name):
            copy_tpl(src_name, dst_name, ignores)
        else:
            copy2(src_name, dst_name)
    copystat(src, dst)


def render_tpl(dst_dir, **kwargs):
    template_files = []
    for directory, _, filenames in os.walk(dst_dir):
        for name in filenames:
            template_file = os.path.join(directory,  name)
            if not template_file.endswith('-tpl'):
                continue
            template_files.append(template_file)
    for template_file in template_files:
        with open(template_file, 'rb') as fp:
            raw = fp.read().decode('utf8')
        dst_file = template_file[0:-len('-tpl')]
        Template(raw).stream(**kwargs).dump(dst_file)
        os.remove(template_file)


def create_from_tpl(tpl_dir, dst_dir, ignores=[], **kwargs):
    copy_tpl(tpl_dir, dst_dir, ignores)
    render_tpl(dst_dir, **kwargs)
