# os-sanic

[![Build Status](https://www.travis-ci.org/cfhamlet/os-sanic.svg?branch=master)](https://www.travis-ci.org/cfhamlet/os-sanic)
[![codecov](https://codecov.io/gh/cfhamlet/os-sanic/branch/master/graph/badge.svg)](https://codecov.io/gh/cfhamlet/os-sanic)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/os-sanic.svg)](https://pypi.python.org/pypi/os-sanic)
[![PyPI](https://img.shields.io/pypi/v/os-sanic.svg)](https://pypi.python.org/pypi/os-sanic)

A framework to organize [Sanic](https://github.com/huge-success/sanic) project, make you focus on development.



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
    │   │   ├── handler.py
    │   │   ├── static
    │   │   │   ├── README.txt
    ├── config.py
    └── manager.py
    ```

* Create app

    App is designed as reusable unit. Each app may has some extensions as pluggins for loading/dumping data, managing db connection when server starting up/down. It should has handlers for processing http/https/websocket requests. Routes(URIs to handlers) are necessary. Besides, [serving static files](https://sanic.readthedocs.io/en/latest/sanic/static_files.html) is also useful. You can check the ``example`` app for more details.
    
    
    ```
    python manage.py startproject first
    ```
    
    This command will create a app named 'first' in the apps directory. You should add the app package string into ``INSTALLED_APPS`` in the ``config.py`` manually to enable it.

* Create app with full feature

    The sanic framework offering [Middleware](https://sanic.readthedocs.io/en/latest/sanic/middleware.html) and [Exception](https://sanic.readthedocs.io/en/latest/sanic/exceptions.html), they all can be used. The following command will create a app with middleware and error handlers.
    
    ```
    python manage.py startapp second --full-feature
    ```
    
    But, attention please, the middlewares and exception handler is not just working on 
blueprint scope right now(v18.12). They will affect on the whole project. [issue](https://github.com/huge-success/sanic/issues/37)
    
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
    
    More verbose config can be written as follows:
    
    ```
    INSTALLED_APPS = [
        {
            'name': 'example',
            'package': 'apps.example',
            'url_prefix': '/example',
        }
    ]
    ```
    - ``name``: the app name, if not set will use ``package``'s last fragment
    - ``package``: the app's package
    - ``url_prefix``(alias ``prefix``): use this as the app's views prefix otherwise use app name
    - ``config``: app's config file, same as the ``app.py`` file, but will cover the parameters defined in ``app.py``.
    
* App definition

    App is defined in the ``app.py``. ``EXTENSIONS``, ``ROUTES`` and ``STATICS`` are the main components.
    
    - ``EXTENSIONS`` are used as plugin mechanism. Can be used for loadding/dumping data, managing db connection when server staring up/down. ``name`` and ``extension_class`` are necessary, other parameters will pass to extension instance's config.
    
        ```
        EXTENSIONS = [
            {
                'name': 'Example',
                'extension_class': '.extension.Example',
                'key1', 'value1',
            }
        ]
        ```
    
    - ``ROUTES`` are used for specifying handlers for different URIs.  All [built-in parameters](https://sanic.readthedocs.io/en/latest/sanic/routing.html) of route definition can be used. 

    
        ````
        ROUTES = [
            ('/e1', '.handler.ExampleView'),
            ('/e2', '.handler.handle_post', ['post']),
            ('/e3', '.handler.handle_websocket', 'websocket', None, True)
        ]
        ````
        
        
        More verbose style which can pass custom parameters: 
    

        ```
        ROUTES = [
            {
                'uri': '/',
                'handler': '.view.ExampleView',
                'costom_key': 'custom_value',
            }
        ]
        ```

    - ``STATICS`` are used for [serving static files](https://sanic.readthedocs.io/en/latest/sanic/static_files.html). ``file_or_directory`` can be absolute or relative path base on the appliction runtime config path.

        ```
        STATICS = [
            {
                'uri': '/static',
                'file_or_directory': '.',
            }
        ]
        ```


## APIs

* Handler

    The handler can be normal function, sanic [``HTTPMethodView``](https://sanic.readthedocs.io/en/latest/sanic/class_based_views.html) class or sanic [``CompositionView``](https://sanic.readthedocs.io/en/latest/sanic/class_based_views.html#using-compositionview) instance. The parameters defined in the ``ROUTES`` will be attached to a config object. If you use ```HTTPMethodView``, the config can be accessed from the View class.
    
    ```
    from sanic.views import HTTPMethodView
    
    class ExampleView(HTTPMethodView):
    
        def get(self, request):
            self.config.key1
            ...
    ```

* Extension Class

    The extenion class must inherit from ``os_sanic.extension.Extension``.

    The base class's members are ``config``, ``application`` and ``logger``

    - ``config``: if you define extra parameters in the ``EXTENSIONS``, they will be attached to this config object
    - ``application``: current application object, can be used for accessing all the project apps
    - ``logger``, the built-in logger object


    The extension class has two usefull methods invoked by the framework: ``setup``, ``cleanup``. They all can be sync or async.

    - ``setup``: called before server start
    - ``cleanup``: called after server stop, if there are multi extensions configured in ``EXTENSIONS``, the cleanup methods execute order will from last extension to the first

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
    
    - it can be accessed in the view class
    
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
        application.get_extension('app_name/extension_name')
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
