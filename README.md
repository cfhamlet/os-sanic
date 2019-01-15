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
    os-sanic startproject project --with-app example
    ```
    
    This command will create a new project with an example app in current directory with the following structure:
    
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

    App is designed as reusable unit. Each app may has some extensions as pluggins for loading data, managing db connection. It also has [views](https://sanic.readthedocs.io/en/latest/sanic/class_based_views.html) for http requests. The definition of the app is in ``app.py``, You can check the ``example`` app for more details.
    
    
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


## Config

* Server config

    The default config file is ``config.py``, parameters define here are used in server scope, can be accessed from the ``config`` member of ``Sanic`` instance, [more details](https://sanic.readthedocs.io/en/latest/sanic/config.html).
    
* Install apps

    You can add app package string into ``INSTALLED_APPS`` in the ``config.py`` to make it work.
    
    ```
    INSTALLED_APPS = ['apps.examples', ]
    ```
    
    More verbose config can be written as following:
    
    ```
    INSTALLED_APPS = [
        {
            'name': 'example',
            'package': 'apps.example',
            'root': True,
        },
    ]
    ```
    - ``name``: the app name, if not set will use ``package``'s last fragment
    - ``package``: the app's package
    - ``root``: if the ``root`` is set ``True``, the app's views will not use app name as url prefix.
    - ``prefix``: use this as the app's views prefix otherwise use app name
    
* App definition

    App is defined in the ``app.py``. ``EXTENSIONS``, ``VIEWS`` and ``STATICS`` are the core components.
    
    - ``EXTENSIONS`` are used as plugin mechanism. Can be used for loadding data, manage db connection and so forth. ``name`` and ``extension_class`` are necessary, other params will pass to extension instance's config.
    
        ```
        EXTENSIONS = [
            {
                'name': 'Example',
                'extension_class': '.extension.Example',
                'key1', 'value1',
            },
        ]
        ```
    
    - ``VIEWS`` are used for http requests. The simple style:

    
        ````
        VIEWS = [('/', '.view.ExampleView'), ]
        ````
    
        More verbose style which can pass params:
    

        ```
        VIEWS = [
            {
                'uri': '/',
                'view_class': '.view.ExampleView',
                'key1': 'value1',
            }
        ]
        ```

    - ``STATICS`` are used for serving static files, [see](https://sanic.readthedocs.io/en/latest/sanic/static_files.html). ``file_or_directory`` can be absolute or relative path base on the appliction runtime config path.

        ```
        STATICS = [
            {
                'uri': '/static',
                'file_or_directory': '.'
            }
        ]
        ```


## APIs

* View Class

    The view class is normal sanic [HTTPMethodView](https://sanic.readthedocs.io/en/latest/sanic/class_based_views.html#class-based-views). If you define extra params in the ``VIEWS``, they will be attached to a config object and pass to the view's ``__init__()``
    
    ```
    from sanic.views import HTTPMethodView
    
    class ExampleView(HTTPMethodView):
    
        def __init__(self, config):
            config.key1
    ```

* Extension Class

    The extenion class must inherit from ``os_sanic.extension.Extension``.
    
    The base class's members are ``name``, ``config``, ``application``, ``logger``
    
    - ``name``: the extension name
    - ``config``: if you define extra params in the ``EXTENSIONS``, they will be attached to this config object
    - ``application``: a project scope object for accessing all of the apps
    - ``logger``, the built-in logger object
    
    
    The extension class has three usefull methods invoked by the framework, ``setup``, ``run``, ``cleanup``, they all can be normal method or async method
    
    - ``setup``: called before server start
    - ``run``: called afeter server run
    - ``cleanup``: called after server stop, if there are multi extensions configured in ``EXTENSIONS``, the cleanup methods execute order will from last extension to the first one
    
    
* application object

    The application object represent the each individual app
    
    - it is a member of extension instance:
    
        ```
        from os_sanic.extension import Extension

        class Example(Extension):

            def setup(self):
                self.application
                ...
        ```
    
    - it can be access in the view class
    
        ```
        from sanic.views import HTTPMethodView

        class ExampleView(HTTPMethodView):

        def get(self, request):
            self.application
            ...
        ```
        
    - you can get extension instance by:
    
        ```
        application.get_extension('extension_name')
        ```

        or get other app's extension

        ```
        application.get_extension('app_name.extension_name')
        ```

    - get app relative logger
  
        ```
        application.get_logger('logger_name')
        ```

    - get sanic instance(it is the same object ``request.app`` in the view)
        
        ```
        application.sanic
        ```


## Unit Tests

  ```
  tox
  ```

## License

MIT licensed.
