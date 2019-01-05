#!/usr/bin/env python
import sys

if __name__ == "__main__":
    try:
        from os_sanic.cmdline import execute
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that os-sanic is missing to avoid masking other
        # exceptions on Python 3.
        try:
            import os_sanic
        except ImportError:
            raise ImportError(
                "Couldn't import os-sanic."
                "Are you sure it's installed and "
                "available on your PYTHONPATH environment variable?"
                "Did you forget to activate a virtual environment?"
            )
        raise
    # =========== for test coverage ===============
    import os
    sys.path.insert(0, os.getcwd())
    if os.getenv('COVERAGE_PROCESS_START'):
        import coverage
        coverage.process_startup()
    # =============================================

    execute('project')