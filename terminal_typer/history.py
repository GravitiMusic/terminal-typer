import json
from datetime import datetime, timezone

from .paths import data_file_path


HISTORY_LIMIT = 200


def format_setting_label(test_mode: str, setting_value: int) -> str:
    return f"{setting_value}s" if test_mode == "timed" else f"{setting_value}w"


def _history_file_path():
    return data_file_path("run_history.json")


def load_run_history(limit: int | None = None) -> list[dict]:
    history_path = _history_file_path()
    if not history_path.exists():
        return []

    try:
        with history_path.open("r", encoding="utf-8") as history_file:
            data = json.load(history_file)
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []

    records = [record for record in data if isinstance(record, dict)]
    if limit is None:
        return records
    return records[:limit]


def filter_run_history(
    records: list[dict],
    test_mode_filter: str = "all",
    setting_filter: tuple[str, int] | None = None,
    word_list_filter: str = "all",
) -> list[dict]:
    filtered = records

    if test_mode_filter != "all":
        filtered = [
            record for record in filtered if record.get("test_mode") == test_mode_filter
        ]

    if setting_filter is not None:
        setting_mode, setting_value = setting_filter
        filtered = [
            record
            for record in filtered
            if record.get("test_mode") == setting_mode
            and record.get("setting_value") == setting_value
        ]

    if word_list_filter != "all":
        filtered = [
            record
            for record in filtered
            if record.get("word_list_name") == word_list_filter
        ]

    return filtered


def record_run(
    test_mode: str,
    setting_value: int,
    word_list_name: str,
    elapsed_time: float,
    wpm: float,
    correct_wpm: float,
    accuracy: float,
    is_match: bool,
    user_input: str,
    prompt_text: str,
    correct_characters: int,
    incorrect_characters: int,
    extra_characters: int,
    missed_characters: int,
) -> None:
    history = load_run_history()
    history.insert(
        0,
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "test_mode": test_mode,
            "setting_value": setting_value,
            "word_list_name": word_list_name,
            "elapsed_time": round(elapsed_time, 2),
            "wpm": round(wpm, 2),
            "correct_wpm": round(correct_wpm, 2),
            "accuracy": round(accuracy, 2),
            "is_match": is_match,
            "typed_length": len(user_input),
            "prompt_length": len(prompt_text),
            "correct_characters": correct_characters,
            "incorrect_characters": incorrect_characters,
            "extra_characters": extra_characters,
            "missed_characters": missed_characters,
        },
    )
    history = history[:HISTORY_LIMIT]

    history_path = _history_file_path()
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("w", encoding="utf-8") as history_file:
        json.dump(history, history_file, indent=2)
        history_file.write("\n")


def _record_error_count(record: dict) -> int | None:
    detailed_fields = (
        "incorrect_characters",
        "extra_characters",
        "missed_characters",
    )
    if any(field in record for field in detailed_fields):
        return sum(int(record.get(field, 0)) for field in detailed_fields)

    if record.get("test_mode") == "words":
        return 0 if record.get("is_match") else None

    return None


def summarize_run_history(
    records: list[dict],
    total_runs: int | None = None,
) -> dict[str, float | int | None]:
    displayed_runs = len(records)
    if total_runs is None:
        total_runs = displayed_runs

    if not records:
        return {
            "total_runs": total_runs,
            "displayed_runs": 0,
            "recent_average_wpm": None,
            "recent_best_wpm": None,
            "recent_average_accuracy": None,
            "clean_runs": 0,
        }

    recent_wpms = [record.get("wpm") for record in records if isinstance(record.get("wpm"), (int, float))]
    recent_accuracies = [
        record.get("accuracy")
        for record in records
        if isinstance(record.get("accuracy"), (int, float))
    ]
    clean_runs = sum(1 for record in records if _record_error_count(record) == 0)
    if not recent_wpms:
        return {
            "total_runs": total_runs,
            "displayed_runs": displayed_runs,
            "recent_average_wpm": None,
            "recent_best_wpm": None,
            "recent_average_accuracy": None,
            "clean_runs": clean_runs,
        }

    return {
        "total_runs": total_runs,
        "displayed_runs": displayed_runs,
        "recent_average_wpm": round(sum(recent_wpms) / len(recent_wpms), 2),
        "recent_best_wpm": round(max(recent_wpms), 2),
        "recent_average_accuracy": (
            round(sum(recent_accuracies) / len(recent_accuracies), 2)
            if recent_accuracies
            else None
        ),
        "clean_runs": clean_runs,
    }