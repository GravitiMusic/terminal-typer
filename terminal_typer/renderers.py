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


def render_timed_progress(lines: list[str], typed_current_line: str) -> Text:
    output = Text()
    if not lines:
        return output

    active_line = lines[0]
    for idx, expected in enumerate(active_line):
        if idx < len(typed_current_line):
            is_correct = typed_current_line[idx] == expected
            if is_correct:
                style = "white"
            elif expected == " ":
                style = "black on red"
            else:
                style = "red"
        else:
            style = "grey50"
        output.append(expected, style=style)

    if len(typed_current_line) > len(active_line):
        extra = typed_current_line[len(active_line) :]
        for ch in extra:
            style = "black on red" if ch == " " else "red"
            output.append(ch, style=style)

    for preview in lines[1:]:
        output.append("\n")
        output.append(preview, style="grey42")

    return output


def render_results(
    results: TypingResults,
    menu_options: list[str],
    menu_index: int,
    show_match_status: bool,
    results_label: str,
) -> Text:
    result_text = Text()
    result_text.append("\n")
    result_text.append(f"{results_label}\n", style="#9cb0c2")
    result_text.append(f"Time taken : {results.elapsed_time:.2f} seconds\n")
    result_text.append(f"You typed: {results.user_input}\n")
    result_text.append(f"Word per minute: {results.wpm:.2f}\n")
    if show_match_status:
        if results.is_match:
            result_text.append("Perfect match!\n", style="green")
        else:
            result_text.append("Text doesn't match the prompt.\n", style="red")
    else:
        result_text.append("Timed test complete.\n", style="green")

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


def render_title_menu(
    menu_options: list[str],
    menu_index: int,
    current_word_count: int,
    current_timed_seconds: int,
) -> Text:
    title_text = Text()
    title_text.append("\nChoose an option:\n", style="grey62")
    for idx, option in enumerate(menu_options):
        display_option = option
        if option == "Start word-count test":
            display_option = f"{option} (Current: {current_word_count} words)"
        elif option == "Start timed test":
            display_option = f"{option} (Current: {current_timed_seconds} seconds)"

        is_selected = idx == menu_index
        prefix = "  > " if is_selected else "    "
        style = "bold black on #93e1d8" if is_selected else "#8ea3b8"
        title_text.append(f"{prefix}{display_option}\n", style=style)

    title_text.append("Use arrow keys to choose and Enter to confirm.", style="grey50")
    return title_text


def render_settings_menu(
    current_word_count: int,
    current_timed_seconds: int,
    selected_row: int,
) -> Text:
    settings_text = Text()
    rows = [
        f"Word-count test length: {current_word_count} words",
        f"Timed test length: {current_timed_seconds} seconds",
        "Save and return",
    ]

    settings_text.append("\nSettings:\n", style="grey62")
    for idx, row in enumerate(rows):
        is_selected = idx == selected_row
        prefix = "  > " if is_selected else "    "
        style = "bold black on #93e1d8" if is_selected else "#8ea3b8"
        settings_text.append(f"{prefix}{row}\n", style=style)

    settings_text.append("\nUse left/right to change values. Press Enter on Save and return.", style="grey50")
    return settings_text