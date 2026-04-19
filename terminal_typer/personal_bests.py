import json

from .paths import data_file_path


def _personal_bests_file_path():
    return data_file_path("personal_bests.json")


def _load_personal_bests() -> dict:
    personal_bests_path = _personal_bests_file_path()
    if not personal_bests_path.exists():
        return {}

    try:
        with personal_bests_path.open("r", encoding="utf-8") as personal_bests_file:
            data = json.load(personal_bests_file)
    except (OSError, json.JSONDecodeError):
        return {}

    if not isinstance(data, dict):
        return {}
    return data


def _save_personal_bests(data: dict) -> None:
    personal_bests_path = _personal_bests_file_path()
    personal_bests_path.parent.mkdir(parents=True, exist_ok=True)
    with personal_bests_path.open("w", encoding="utf-8") as personal_bests_file:
        json.dump(data, personal_bests_file, indent=2)
        personal_bests_file.write("\n")


def get_personal_best(test_mode: str, setting_value: int, word_list_name: str) -> float | None:
    data = _load_personal_bests()
    mode_bucket = data.get(test_mode, {})
    word_list_bucket = mode_bucket.get(word_list_name, {})
    record = word_list_bucket.get(str(setting_value))
    if not isinstance(record, dict):
        return None

    wpm = record.get("wpm")
    if not isinstance(wpm, (int, float)):
        return None
    return float(wpm)


def record_personal_best(
    test_mode: str,
    setting_value: int,
    word_list_name: str,
    wpm: float,
) -> tuple[float | None, bool]:
    current_best = get_personal_best(test_mode, setting_value, word_list_name)
    if wpm <= 0 or (current_best is not None and wpm <= current_best):
        return current_best, False

    data = _load_personal_bests()
    mode_bucket = data.setdefault(test_mode, {})
    word_list_bucket = mode_bucket.setdefault(word_list_name, {})
    word_list_bucket[str(setting_value)] = {"wpm": round(wpm, 2)}
    _save_personal_bests(data)
    return round(wpm, 2), True