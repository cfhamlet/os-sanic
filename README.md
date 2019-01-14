# os-sanic

[![Build Status](https://www.travis-ci.org/cfhamlet/os-sanic.svg?branch=master)](https://www.travis-ci.org/cfhamlet/os-sanic)
[![codecov](https://codecov.io/gh/cfhamlet/os-sanic/branch/master/graph/badge.svg)](https://codecov.io/gh/cfhamlet/os-sanic)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/os-sanic.svg)](https://pypi.python.org/pypi/os-sanic)
[![PyPI](https://img.shields.io/pypi/v/os-sanic.svg)](https://pypi.python.org/pypi/os-sanic)

A framework to organize [Sanic](https://github.com/huge-success/sanic) project and simplify development.



## Install

  ```
  pip install os-sanic
  ```

## Usage

* Create project

    Typically, a project contains management script, config file and a set of reusable apps. 

    ```
    os-sanic startproject project
    ```
    
    This command will create a new project(with an example app) in current directory with the following structure:
    
    ```
    project/
    ├── apps
    ├── __init__.py
    │   ├── example
    │   │   ├── __init__.py
    │   │   ├── app.py
    │   │   ├── extension.py
    │   │   ├── view.py    
    ├── config.py
    └── manager.py
    ```

    
* Create app

    App is designed as reusable component. Each app may has some extensions for loading data, managing db connection and so forth. It also has [views](https://sanic.readthedocs.io/en/latest/sanic/class_based_views.html) for http requests. The definition of the app is configured in ``app.py``, You can check the ``example`` app for more details.
    
    
    ```
    python manage.py startproject first
    ```
    
    This command will create a app in the apps directory. You should at least add the app package string into ``INSTALLED_APPS`` in the ``config.py`` manually to enable it.
    
* Show the project information

    ```
    python manage.py info
    ```

* Start the server

    ```
    python manage.py run
    ```
    
    This command will load ``config.py`` and start the server. Use ``--help`` to seed more command line options.


## Unit Tests

  ```
  tox
  ```

## License

MIT licensed.
