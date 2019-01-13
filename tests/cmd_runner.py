import os
import shlex
import subprocess
import sys

import pytest
from sanic import Sanic

from os_sanic.manage import main


def process(runable_file=None, cmdline='', env=None, **kwargs):
    if env is None:
        env = os.environ.copy()
    if env.get('COVERAGE', None) is not None:
        if 'COVERAGE_PROCESS_START' not in env:
            env['COVERAGE_PROCESS_START'] = os.path.abspath('.coveragerc')

    f = runable_file
    if not f:
        f = os.path.abspath(__file__)
    cmd = 'python -u {} {}'.format(f, cmdline)
    proc = subprocess.Popen(shlex.split(cmd),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            cwd=os.getcwd(),
                            env=env,
                            **kwargs)
    return proc


def call(runable_file=None, cmdline='', env=None, **kwargs):
    proc = process(runable_file, cmdline, env, **kwargs)
    stdout, stderr = proc.communicate()
    return stdout, stderr


if __name__ == "__main__":
    sys.path.insert(0, os.getcwd())
    if os.getenv('COVERAGE_PROCESS_START'):
        import coverage
        coverage.process_startup()
    main()
