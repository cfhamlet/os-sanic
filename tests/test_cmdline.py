import json
import os
import uuid
from shutil import copytree

import pytest
import requests
from pytest_xprocess import getrootdir
from xprocess import ProcessStarter, XProcess

from tests.cmd_runner import call
from tests.utils import cd, copy_file, unused_port


@pytest.fixture()
def xproc(request):
    rootdir = getrootdir(request.config)
    rootdir = rootdir.join(str(uuid.uuid1())[0:8])
    yield XProcess(request.config, rootdir)
    if rootdir.exists():
        rootdir.remove()


@pytest.fixture
def cov_env():
    env = os.environ.copy()
    env['COVERAGE_PROCESS_START'] = os.path.abspath('.coveragerc')
    env['COVERAGE_FILE'] = os.path.abspath('.coverage')
    return env


@pytest.fixture
def new_project(tmpdir):
    def _create_project(proj_name, app_name=None):
        create_project(tmpdir, proj_name, app_name)
        proj_path = os.path.join(tmpdir.strpath, proj_name)
        with cd(proj_path):
            copy_file('manage_for_test.py', 'manage.py')
        return proj_path

    yield _create_project


def create_project(tmpdir, proj_name, app_name=None):
    f = 'cmd_runner.py'
    runf = os.path.join(tmpdir.strpath, f)
    copy_file(f, runf)
    env = os.environ.copy()
    env['COVERAGE_PROCESS_START'] = os.path.abspath('.coveragerc')
    env['COVERAGE_FILE'] = os.path.abspath('.coverage')

    cmd = f'startproject {proj_name}'
    if app_name:
        cmd += f' --with-app {app_name}'

    with cd(tmpdir):
        call(runf, cmd, env)


def test_no_args(tmpdir):
    stdout, _ = call()
    assert b'startproject' in stdout
    assert b'startapp' not in stdout


def test_startproject_001(new_project):
    proj_name = 'xxx'
    app_name = 'example'
    proj_path = new_project(proj_name, app_name)

    files = [
        'manage.py',
        'config.py',
        'apps',
        'apps/__init__.py',
        f'apps/{app_name}/__init__.py',
        f'apps/{app_name}/app.py',
        f'apps/{app_name}/view.py',
        f'apps/{app_name}/extension.py',
    ]
    print(proj_path)
    for f in files:
        assert os.path.exists(os.path.join(proj_path, f))


def test_start_app(new_project, cov_env):
    proj_path = new_project('xxx')
    print(proj_path)
    with cd(proj_path):
        app_name = 'yyy'
        call('manage.py', f'startapp {app_name}', cov_env)
        prefix = f'apps/{app_name}/'
        for ff in ('', 'app.py', 'extension.py', '__init__.py', 'view.py'):
            ff = os.path.join(prefix, ff)
            assert os.path.exists(ff)


def test_info(new_project, cov_env):
    proj_name = 'xxx'
    app_name = 'example'
    proj_path = new_project(proj_name, app_name)
    print(proj_path)
    expect = [
        f'"name": "{app_name}",',
        f'"package": "apps.{app_name}",',
        f'<class \'apps.{app_name}.extension.{app_name.capitalize()}\'>',
        f'<class \'apps.{app_name}.view.{app_name.capitalize()}View\'>',
    ]
    with cd(proj_path):
        stdout, _ = call('manage.py', 'info', cov_env)
        for exp in expect:
            assert exp.encode() in stdout


@pytest.fixture
def run_server(xproc, cov_env):
    name = 'sanic_server'

    def _run_server(proj_path, *run_args):

        class Starter(ProcessStarter):
            pattern = '.*Starting\\s+worker'
            env = cov_env
            args = [
                'python',
                'manage.py',
                *run_args,
            ]

            def __init__(self, control_dir, process):
                self.control_dir = control_dir
                self.process = process

        copytree(proj_path, xproc.rootdir.join(name))
        xproc.ensure(name, Starter)
        return xproc

    yield _run_server

    xproc.getinfo(name).terminate()


def test_run_001(new_project, run_server):
    proj_name = 'xxx'
    app_name = 'example'
    proj_path = new_project(proj_name, app_name)
    port = unused_port()
    run_server(proj_path, 'run', '--port', f'{port}')
    url = f'http://127.0.0.1:{port}/'
    r = requests.get(url)
    assert r.status_code == 200
    d = json.loads(r.content)
    assert d == {'view': 'ExampleView'}


def test_run_002(new_project, run_server):
    proj_name = 'xxx'
    app_name = 'example'
    proj_path = new_project(proj_name, app_name)
    port = unused_port()
    xproc = run_server(proj_path, 'run', '--port', f'{port}', '-l', 'DEBUG')
    info = xproc.getinfo('sanic_server')
    log = info.logpath.open().read()
    expects = ['[App.example.Example] [INFO] run',
               '[App.example.Example] [INFO] setup']
    for exp in expects:
        assert exp in log
