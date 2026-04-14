import json
import random
from functools import lru_cache
from pathlib import Path

from .constants import DEFAULT_WORDS_PER_TEST, TIMED_LINE_WORDS


def _word_bank_path() -> Path:
    return (
        Path(__file__).resolve().parent.parent
        / "assets"
        / "static"
        / "languages"
        / "english_5k.json"
    )


@lru_cache(maxsize=1)
def load_english_5k_words() -> tuple[str, ...]:
    word_bank_file = _word_bank_path()
    with word_bank_file.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    words = payload.get("words", [])
    if not isinstance(words, list) or not words:
        raise ValueError("english_5k.json does not contain a valid non-empty 'words' list")

    sanitized_words = tuple(word for word in words if isinstance(word, str) and word.strip())
    if not sanitized_words:
        raise ValueError("english_5k.json does not contain usable words")

    return sanitized_words


def generate_prompt(word_count: int = DEFAULT_WORDS_PER_TEST) -> str:
    words = load_english_5k_words()

    if word_count <= len(words):
        selected_words = random.sample(words, word_count)
    else:
        selected_words = [random.choice(words) for _ in range(word_count)]

    return " ".join(selected_words)


def generate_timed_line(word_count: int = TIMED_LINE_WORDS) -> str:
    words = load_english_5k_words()
    selected_words = [random.choice(words) for _ in range(word_count)]
    return " ".join(selected_words)