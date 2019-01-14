#!/usr/bin/env python
from sanic import Sanic
from os_sanic import run

app = Sanic(__name__)

if __name__ == "__main__":
    # =========== for test coverage ===============
    import os
    import sys
    sys.path.insert(0, os.getcwd())
    if os.getenv('COVERAGE_PROCESS_START'):
        import coverage
        coverage.process_startup()
    # =============================================

    run(app)
