import os

from tests.cmd_runner import call
from tests.utils import cd, copy_file


def test_no_args(tmpdir):
    stdout, _ = call()
    assert b'startproject' in stdout
    assert b'startapp' not in stdout


def test_startproject_001(tmpdir):
    f = 'cmd_runner.py'
    runf = os.path.join(tmpdir.strpath, f)
    copy_file(f, runf)
    env = os.environ.copy()
    env['COVERAGE_PROCESS_START'] = os.path.abspath('.coveragerc')
    env['COVERAGE_FILE'] = os.path.abspath('.coverage')

    files = [
        'xxx/manage.py',
        'xxx/config.py',
        'xxx/apps',
        'xxx/apps/__init__.py',
        'xxx/apps/xxx/__init__.py',
        'xxx/apps/xxx/app.py',
        'xxx/apps/xxx/view.py',
        'xxx/apps/xxx/extension.py',
    ]
    with cd(tmpdir):
        print(tmpdir)
        call(runf, 'startproject xxx', env)
        for f in files:
            assert os.path.exists(os.path.join(tmpdir.strpath, f))


def create_project(tmpdir, proj_name):
    f = 'cmd_runner.py'
    runf = os.path.join(tmpdir.strpath, f)
    copy_file(f, runf)
    env = os.environ.copy()
    env['COVERAGE_PROCESS_START'] = os.path.abspath('.coveragerc')
    env['COVERAGE_FILE'] = os.path.abspath('.coverage')

    with cd(tmpdir):
        call(runf, 'startproject {}'.format(proj_name), env)


def test_start_app(tmpdir):
    proj_name = 'xxx'
    create_project(tmpdir, proj_name)
    proj_path = os.path.join(tmpdir.strpath, proj_name)
    env = os.environ.copy()
    env['COVERAGE_PROCESS_START'] = os.path.abspath('.coveragerc')
    env['COVERAGE_FILE'] = os.path.abspath('.coverage')
    with cd(proj_path):
        print(proj_path)
        copy_file('manage_for_test.py', 'manage.py')
        app_name = 'yyy'
        call('manage.py', f'startapp {app_name}', env)
    for ff in ('apps/yyy', 'apps/yyy/app.py'):
        print(ff)
        p = os.path.join(proj_path, ff)
        assert os.path.exists(p)


def test_info(tmpdir):
    proj_name = 'xxx'
    create_project(tmpdir, proj_name)
    proj_path = os.path.join(tmpdir.strpath, proj_name)
    env = os.environ.copy()
    env['COVERAGE_PROCESS_START'] = os.path.abspath('.coveragerc')
    env['COVERAGE_FILE'] = os.path.abspath('.coverage')
    expect = [
        f'"package": "apps.{proj_name}",',
        f'{proj_name.capitalize()}: <class \'apps.{proj_name}.extension.{proj_name.capitalize()}\'>',
        f'/ <class \'apps.{proj_name}.view.{proj_name.capitalize()}View\'>',
    ]
    with cd(proj_path):
        print(proj_path)
        copy_file('manage_for_test.py', 'manage.py')
        stdout, _ = call('manage.py', 'info', env)
        for exp in expect:
            assert exp.encode() in stdout
