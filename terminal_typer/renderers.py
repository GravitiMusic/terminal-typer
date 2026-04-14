from rich.text import Text

from .constants import APP_NAME, LOGO_PALETTE
from .metrics import TypingResults


def render_intro_logo(frame: int) -> Text:
    text = Text()
    for idx, ch in enumerate(APP_NAME):
        color = LOGO_PALETTE[(idx + frame) % len(LOGO_PALETTE)]
        text.append(ch, style=f"bold {color}")
    return text


def render_progress(prompt_text: str, typed_text: str) -> Text:
    output = Text()

    for idx, expected in enumerate(prompt_text):
        if idx < len(typed_text):
            is_correct = typed_text[idx] == expected
            if is_correct:
                style = "white"
            elif expected == " ":
                style = "black on red"
            else:
                style = "red"
        else:
            style = "grey50"

        output.append(expected, style=style)

    if len(typed_text) > len(prompt_text):
        extra = typed_text[len(prompt_text) :]
        for ch in extra:
            style = "black on red" if ch == " " else "red"
            output.append(ch, style=style)

    return output


def render_results(
    results: TypingResults,
    menu_options: list[str],
    menu_index: int,
) -> Text:
    result_text = Text()
    result_text.append("\n")
    result_text.append(f"Time taken : {results.elapsed_time:.2f} seconds\n")
    result_text.append(f"You typed: {results.user_input}\n")
    result_text.append(f"Word per minute: {results.wpm:.2f}\n")
    if results.is_match:
        result_text.append("Perfect match!\n", style="green")
    else:
        result_text.append("Text doesn't match the prompt.\n", style="red")

    result_text.append(
        "\nUse arrow keys to choose an option, then press Enter.\n",
        style="grey62",
    )
    for idx, option in enumerate(menu_options):
        is_selected = idx == menu_index
        prefix = "  > " if is_selected else "    "
        style = "bold black on #93e1d8" if is_selected else "#8ea3b8"
        result_text.append(f"{prefix}{option}\n", style=style)

    result_text.append("\nPress Esc to quit.", style="grey50")
    return result_text