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
        stdout, stderr = call(runf, 'startproject xxx', env)
        for f in files:
            assert os.path.exists(os.path.join(tmpdir.strpath, f))
