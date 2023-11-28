# mypy: ignore-errors
import os
from os import environ

from felo.config.default import DefaultSettings


def get_config() -> DefaultSettings:
    env = environ.get("ENV", "dev")
    env_settings = {
        "dev": DefaultSettings,
    }
    try:
        print("current dir", os.getcwd())
        setting = env_settings[env]()
        return setting
    except KeyError:
        return DefaultSettings()  # fallback to default


CONFIG = get_config()
