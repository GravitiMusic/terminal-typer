import json
import random
from functools import lru_cache
from importlib.resources import files

from .constants import DEFAULT_WORD_LIST_NAME, DEFAULT_WORDS_PER_TEST, TIMED_FALLBACK_LINE_WIDTH


def _languages_dir():
    return files("terminal_typer.assets.languages")


@lru_cache(maxsize=1)
def list_word_list_options() -> tuple[str, ...]:
    options = sorted(
        path.name
        for path in _languages_dir().iterdir()
        if path.name.endswith(".json")
    )
    if not options:
        raise ValueError("No language list JSON files were bundled with the package")
    return tuple(options)


def _resolve_word_list_name(word_list_name: str) -> str:
    options = list_word_list_options()
    if word_list_name in options:
        return word_list_name
    if DEFAULT_WORD_LIST_NAME in options:
        return DEFAULT_WORD_LIST_NAME
    return options[0]


@lru_cache(maxsize=16)
def load_words(word_list_name: str) -> tuple[str, ...]:
    resolved_name = _resolve_word_list_name(word_list_name)
    word_bank_file = _languages_dir() / resolved_name
    with word_bank_file.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    words = payload.get("words", [])
    if not isinstance(words, list) or not words:
        raise ValueError(f"{resolved_name} does not contain a valid non-empty 'words' list")

    sanitized_words = tuple(word for word in words if isinstance(word, str) and word.strip())
    if not sanitized_words:
        raise ValueError(f"{resolved_name} does not contain usable words")

    return sanitized_words


def generate_prompt(word_count: int = DEFAULT_WORDS_PER_TEST, word_list_name: str = DEFAULT_WORD_LIST_NAME) -> str:
    words = load_words(word_list_name)

    if word_count <= len(words):
        selected_words = random.sample(words, word_count)
    else:
        selected_words = [random.choice(words) for _ in range(word_count)]

    return " ".join(selected_words)


def generate_timed_line(
    line_width: int = TIMED_FALLBACK_LINE_WIDTH,
    word_list_name: str = DEFAULT_WORD_LIST_NAME,
) -> str:
    words = load_words(word_list_name)
    target_width = max(8, line_width)
    selected_words: list[str] = []
    current_width = 0

    while True:
        word = random.choice(words)
        additional_width = len(word) if not selected_words else len(word) + 1

        if selected_words and current_width + additional_width > target_width:
            break

        selected_words.append(word)
        current_width += additional_width

        if current_width >= target_width:
            break

    return " ".join(selected_words)