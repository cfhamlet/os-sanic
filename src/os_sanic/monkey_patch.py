import os
import signal
from contextlib import contextmanager
from time import sleep
from unittest import mock

from sanic import reloader_helpers
from sanic.reloader_helpers import (_iter_module_files, kill_process_children,
                                    restart_with_reloader)


@contextmanager
def patch():
    with mock.patch.object(reloader_helpers, 'watchdog', patch_reloader_helpers_watchdog):
        yield


def patch_reloader_helpers_watchdog(sleep_interval):
    mtimes = {}
    worker_process = []
    signal.signal(
        signal.SIGTERM, lambda *args: kill_program_completly(
            worker_process)
    )
    signal.signal(
        signal.SIGINT, lambda *args: kill_program_completly(
            worker_process)
    )

    worker_process.append(restart_with_reloader())
    while True:
        for filename in _iter_module_files():
            try:
                mtime = os.stat(filename).st_mtime
            except OSError:
                continue

            old_time = mtimes.get(filename)
            if old_time is None:
                mtimes[filename] = mtime
                continue
            elif mtime > old_time:
                wp = worker_process.pop()
                kill_process_children(wp.pid)
                wp.terminate()
                worker_process.append(restart_with_reloader())
                mtimes[filename] = mtime
                break

        sleep(sleep_interval)


def kill_program_completly(proc):
    if not proc:
        kill_process_children(os.getpid())
        os._exit(0)
    proc = proc.pop()
    kill_process_children(proc.pid)
    proc.terminate()
    os._exit(0)
