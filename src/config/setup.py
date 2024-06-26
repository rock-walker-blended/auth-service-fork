import os
from functools import lru_cache
from typing import Dict, Type

from src.config.settings.app import AppSettings
from src.config.settings.base import AppEnvTypes, BaseAppSettings
from src.config.settings.development import DevAppSettings
from src.config.settings.docker import DockerAppSettings
from src.config.settings.production import ProdAppSettings
from src.config.settings.test import TestAppSettings

environments: Dict[AppEnvTypes, Type[AppSettings]] = {
    AppEnvTypes.dev: DevAppSettings,
    AppEnvTypes.prod: ProdAppSettings,
    AppEnvTypes.test: TestAppSettings,
    AppEnvTypes.docker: DockerAppSettings,
}


@lru_cache
def get_app_settings() -> AppSettings:
    app_env = BaseAppSettings().app_env

    config = environments[app_env]
    return config()
