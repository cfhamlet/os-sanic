import os
from contextlib import contextmanager
from shutil import copy2, copystat


@contextmanager
def cd(new_path):
    old_path = os.getcwd()
    yield os.chdir(new_path)
    os.chdir(old_path)


def copy_file(f, dest):
    path = os.path.dirname(__file__)
    f = os.path.join(path, f)
    copy2(f, dest)
