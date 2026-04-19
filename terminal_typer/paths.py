import os
import shutil
from pathlib import Path


APP_DATA_ENV_VAR = "TERMINAL_TYPER_HOME"
APP_DIR_NAME = "terminal-typer"


def _legacy_config_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "config"


def _default_data_home() -> Path:
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home).expanduser() / APP_DIR_NAME
    return Path.home() / ".local" / "share" / APP_DIR_NAME


def user_data_dir() -> Path:
    override = os.environ.get(APP_DATA_ENV_VAR)
    data_dir = Path(override).expanduser() if override else _default_data_home()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def data_file_path(filename: str) -> Path:
    target_path = user_data_dir() / filename
    if target_path.exists():
        return target_path

    legacy_path = _legacy_config_dir() / filename
    if legacy_path.exists():
        try:
            shutil.copy2(legacy_path, target_path)
        except OSError:
            pass

    return target_path
