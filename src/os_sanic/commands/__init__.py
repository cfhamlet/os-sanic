import ast
import os
from importlib import import_module
from logging import _nameToLevel
from shutil import copy2, copystat, ignore_patterns

import click
from jinja2 import Template


def valid_name(ctx, param, value):
    if value is None:
        return None
    def _module_exists(module_name):
        try:
            import_module(module_name)
            return True
        except ImportError:
            return False
    try:
        ast.parse(f'{value} = None')
    except:
        raise click.BadParameter(f'Not a valid name, {value}')

    if value.startswith('_'):
        raise click.BadParameter(f'Not a valid name, {value}')
    elif _module_exists(value):
        raise click.BadParameter(f'Module already existed, {value}')

    return value


def valid_log_level(ctx, param, value):
    v = value.upper()
    if v not in _nameToLevel:
        choices = ' '.join(_nameToLevel.keys())
        raise click.BadParameter(
            f'Invalid choice: {value}. (choose from {choices})')
    return v

def copy_tpl(src, dst, ignores=[]):
    if os.path.exists(dst):
        raise IOError(f'Path already existed {dst}')
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
