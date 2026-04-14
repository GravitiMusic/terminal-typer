from dataclasses import dataclass


@dataclass(frozen=True)
class TypingResults:
    elapsed_time: float
    wpm: float
    user_input: str
    is_match: bool


def calculate_results(
    prompt_text: str,
    typed_chars: list[str],
    start_time: float | None,
    end_time: float | None,
) -> TypingResults:
    user_input = "".join(typed_chars)
    elapsed_time = (
        (end_time - start_time)
        if start_time is not None and end_time is not None
        else 0.0
    )
    minutes = elapsed_time / 60
    wpm = ((len(user_input) / 5) / minutes) if minutes > 0 else 0.0

    return TypingResults(
        elapsed_time=elapsed_time,
        wpm=wpm,
        user_input=user_input,
        is_match=user_input == prompt_text,
    )