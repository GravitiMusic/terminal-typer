import json
from dataclasses import dataclass
from pathlib import Path

from .constants import (
    DEFAULT_TIMED_SECONDS,
    DEFAULT_WORDS_PER_TEST,
    TIMED_SECONDS_OPTIONS,
    WORD_COUNT_OPTIONS,
)


@dataclass
class UserSettings:
    word_count: int = DEFAULT_WORDS_PER_TEST
    timed_seconds: int = DEFAULT_TIMED_SECONDS


def _settings_file_path() -> Path:
    return Path(__file__).resolve().parent.parent / "config" / "user_settings.json"


def _validate_word_count(value: object) -> int:
    if isinstance(value, int) and value in WORD_COUNT_OPTIONS:
        return value
    return DEFAULT_WORDS_PER_TEST


def _validate_timed_seconds(value: object) -> int:
    if isinstance(value, int) and value in TIMED_SECONDS_OPTIONS:
        return value
    return DEFAULT_TIMED_SECONDS


def load_settings() -> UserSettings:
    settings_path = _settings_file_path()
    if not settings_path.exists():
        return UserSettings()

    try:
        with settings_path.open("r", encoding="utf-8") as settings_file:
            data = json.load(settings_file)
    except (OSError, json.JSONDecodeError):
        return UserSettings()

    if not isinstance(data, dict):
        return UserSettings()

    return UserSettings(
        word_count=_validate_word_count(data.get("word_count")),
        timed_seconds=_validate_timed_seconds(data.get("timed_seconds")),
    )


def save_settings(settings: UserSettings) -> None:
    settings_path = _settings_file_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "word_count": _validate_word_count(settings.word_count),
        "timed_seconds": _validate_timed_seconds(settings.timed_seconds),
    }
    with settings_path.open("w", encoding="utf-8") as settings_file:
        json.dump(payload, settings_file, indent=2)
        settings_file.write("\n")