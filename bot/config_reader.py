from enum import StrEnum, auto
from functools import lru_cache
from os import getenv
import os
from tomllib import load
from typing import Type, TypeVar

from pydantic import BaseModel, SecretStr, field_validator, RedisDsn

ConfigType = TypeVar("ConfigType", bound=BaseModel)


class LogRenderer(StrEnum):
    JSON = auto()
    CONSOLE = auto()


class FSMMode(StrEnum):
    MEMORY = auto()
    REDIS = auto()


class BotConfig(BaseModel):
    token: SecretStr
    fsm_mode: FSMMode

    @field_validator('fsm_mode', mode="before")
    @classmethod
    def fsm_mode_to_lower(cls, v: str):
        return v.lower()


class LogConfig(BaseModel):
    project_name: str = "my project"
    show_datetime: bool = True
    datetime_format: str = "%Y-%m-%d %H:%M:%S"
    show_debug_logs: bool = False
    time_in_utc: bool = False
    use_colors_in_console: bool = False
    renderer: LogRenderer = LogRenderer.JSON
    allow_third_party_logs: bool = True

    @field_validator('renderer', mode="before")
    @classmethod
    def log_renderer_to_lower(cls, v: str):
        return v.lower()


class RedisConfig(BaseModel):
    dsn: RedisDsn


class GameConfig(BaseModel):
    starting_points: int = 50
    send_gameover_sticker: bool = True
    throttle_time_spin: int = 2
    throttle_time_other: int = 1


@lru_cache
def parse_config_file() -> dict:
    file_path = getenv("CONFIG_FILE_PATH")
    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as file:
            return load(file)
    
    # Fallback structure populated from environment variables
    return {
        "bot": {
            "token": getenv("BOT_TOKEN", "1234567890:TOKEN"),
            "fsm_mode": getenv("FSM_MODE", "memory")
        },
        "redis": {
            "dsn": getenv("REDIS_DSN", "redis://localhost:6379")
        },
        "logs": {
            "project_name": getenv("PROJECT_NAME", "casino_bot"),
            "show_datetime": True,
            "datetime_format": "%Y-%m-%d %H:%M:%S",
            "show_debug_logs": False,
            "time_in_utc": False,
            "renderer": "json",
            "use_colors_in_console": False,
            "allow_third_party_logs": True
        },
        "game_config": {
            "starting_points": 50,
            "send_gameover_sticker": True,
            "throttle_time_spin": 2,
            "throttle_time_other": 1
        }
    }


@lru_cache
def get_config(model: Type[ConfigType], root_key: str) -> ConfigType:
    config_dict = parse_config_file()
    if root_key not in config_dict:
        error = f"Key {root_key} not found"
        raise ValueError(error)
    return model.model_validate(config_dict[root_key])
