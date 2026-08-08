from enum import StrEnum, auto
from functools import lru_cache
from os import getenv
from pathlib import Path
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
    owner_id: int = 0

    @field_validator('fsm_mode', mode="before")
    @classmethod
    def fsm_mode_to_lower(cls, v: str):
        return v.lower()


class LogConfig(BaseModel):
    project_name: str = "my project"
    show_datetime: bool
    datetime_format: str
    show_debug_logs: bool
    time_in_utc: bool
    use_colors_in_console: bool
    renderer: LogRenderer
    allow_third_party_logs: bool

    @field_validator('renderer', mode="before")
    @classmethod
    def log_renderer_to_lower(cls, v: str):
        return v.lower()


class RedisConfig(BaseModel):
    dsn: RedisDsn


class GameConfig(BaseModel):
    starting_points: int
    send_gameover_sticker: bool
    throttle_time_spin: int
    throttle_time_other: int


@lru_cache
def parse_config_file() -> dict:
    file_path = getenv("CONFIG_FILE_PATH", "settings.toml")
    
    config_data = {}
    path = Path(file_path)
    if path.is_file():
        with open(path, "rb") as file:
            config_data = load(file)
    else:
        # Fallback default dictionary if file doesn't exist
        config_data = {
            "bot": {
                "token": "1234567890:placeholder",
                "fsm_mode": "redis",
                "owner_id": 0
            },
            "redis": {
                "dsn": "redis://localhost:6379/0"
            },
            "logs": {
                "project_name": "casino_bot",
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

    # Override with environment variables if present
    env_token = getenv("BOT_TOKEN")
    if env_token:
        config_data.setdefault("bot", {})["token"] = env_token

    env_owner_id = getenv("OWNER_ID")
    if env_owner_id:
        try:
            config_data.setdefault("bot", {})["owner_id"] = int(env_owner_id)
        except ValueError:
            pass

    env_fsm_mode = getenv("FSM_MODE")
    if env_fsm_mode:
        config_data.setdefault("bot", {})["fsm_mode"] = env_fsm_mode

    env_redis_url = getenv("REDIS_URL")
    if env_redis_url:
        config_data.setdefault("redis", {})["dsn"] = env_redis_url

    return config_data


@lru_cache
def get_config(model: Type[ConfigType], root_key: str) -> ConfigType:
    config_dict = parse_config_file()
    if root_key not in config_dict:
        error = f"Key {root_key} not found"
        raise ValueError(error)
    return model.model_validate(config_dict[root_key])
