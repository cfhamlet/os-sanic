from enum import Enum
from typing import List, Set, Union

from pydantic import BaseModel, Schema, validator
from sanic.constants import HTTP_METHODS


class NamedModel(BaseModel):
    name: str

    class Config:
        allow_extra = True


class AppCfg(NamedModel):
    package: str
    url_prefix: str = Schema(None, alias='prefix')
    config: str = None
    host: str = None
    version: int = None
    strict_slashes: bool = False

    class Config:
        allow_mutation = False


class ApplicationCfg(BaseModel):
    EXTENSIONS: List = []
    ROUTES: List = []
    STATICS: List = []
    MIDDLEWARES: List = []
    ERROR_HANDLERS: List = []

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
    handler: str
    methods: Union[List[str], Set[str], str] = frozenset({'GET'})
    host: str = None
    stream: bool = False
    strict_slashes: bool = None
    name: str = None

    @validator('methods', whole=True)
    def valid_methods(cls, v):
        vv = None
        if isinstance(v, str):
            vv = set([v.upper()])
        else:
            vv = set([i.upper() for i in v])
        invalid = vv - set(list(HTTP_METHODS) + ['WEBSOCKET'])

        if invalid:
            raise ValueError(f'Invalid methods {invalid}')
        return vv


class StaticCfg(URIModel):
    file_or_directory: str
    name = "static"
    pattern: str = r"/?.+"
    use_modified_since: bool = True
    use_content_range: bool = False
    stream_large_files: bool = False
    host: str = None
    strict_slashes: bool = None
    content_type: str = None


class Workflowable(object):
    def setup(self):
        pass

    def cleanup(self):
        pass
