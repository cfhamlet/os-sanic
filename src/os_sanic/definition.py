from enum import Enum
from logging import _nameToLevel
from typing import List

from pydantic import BaseModel

LogLevel = Enum('LogLevel', [(k, k) for k in _nameToLevel], type=str)
LogLevel.__repr__ = lambda x: x.name


class NamedModel(BaseModel):
    name: str

    class Config:
        allow_extra = True


class AppCfg(NamedModel):
    package: str
    prefix: str = None
    config: str = None

    class Config:
        allow_mutation = False


class ApplicationCfg(BaseModel):
    EXTENSIONS: List = []
    MIDDLEWARE: List = []
    ROUTES: List = []
    STATICS: List = []

    class Config:
        allow_mutation = False
        ignore_extra = True


class ApplicationContext(BaseModel):
    app_cfg: AppCfg
    core_cfg: ApplicationCfg
    user_cfg: ApplicationCfg
    runtime_path: str


class ExtensionCfg(NamedModel):
    extension_class: str

    class Config:
        allow_mutation = False


class URIModel(BaseModel):
    uri: str

    class Config:
        allow_extra = True
        allow_mutation = False


class RouteCfg(URIModel):
    view_class: str


class StaticCfg(URIModel):
    file_or_directory: str


class Workflowable(object):
    def setup(self):
        pass

    def cleanup(self):
        pass
