from dataclasses import dataclass


@dataclass(frozen=True)
class TypingResults:
    elapsed_time: float
    wpm: float
    correct_wpm: float
    accuracy: float
    user_input: str
    is_match: bool
    typed_length: int
    prompt_length: int
    correct_characters: int
    incorrect_characters: int
    extra_characters: int
    missed_characters: int


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
    typed_length = len(user_input)
    prompt_length = len(prompt_text)
    comparison_length = min(typed_length, prompt_length)
    correct_characters = sum(
        1
        for idx in range(comparison_length)
        if user_input[idx] == prompt_text[idx]
    )
    incorrect_characters = comparison_length - correct_characters
    extra_characters = max(0, typed_length - prompt_length)
    missed_characters = max(0, prompt_length - typed_length)
    minutes = elapsed_time / 60
    wpm = ((typed_length / 5) / minutes) if minutes > 0 else 0.0
    correct_wpm = ((correct_characters / 5) / minutes) if minutes > 0 else 0.0
    accuracy = ((correct_characters / typed_length) * 100) if typed_length > 0 else 0.0

    return TypingResults(
        elapsed_time=elapsed_time,
        wpm=wpm,
        correct_wpm=correct_wpm,
        accuracy=accuracy,
        user_input=user_input,
        is_match=user_input == prompt_text,
        typed_length=typed_length,
        prompt_length=prompt_length,
        correct_characters=correct_characters,
        incorrect_characters=incorrect_characters,
        extra_characters=extra_characters,
        missed_characters=missed_characters,
    )