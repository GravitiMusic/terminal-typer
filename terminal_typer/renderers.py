from rich.console import Group
from rich.table import Table
from rich.text import Text

from .constants import APP_NAME, LOGO_PALETTE
from .history import format_setting_label
from .metrics import TypingResults


def _format_personal_best(best_wpm: float | None) -> str:
    if best_wpm is None:
        return "No best yet"
    return f"{best_wpm:.2f} WPM"


def render_intro_logo(frame: int) -> Text:
    text = Text()
    for idx, ch in enumerate(APP_NAME):
        color = LOGO_PALETTE[(idx + frame) % len(LOGO_PALETTE)]
        text.append(ch, style=f"bold {color}")
    return text


def render_page_title(title: str, accent_color: str) -> Text:
    text = Text()
    text.append(title, style=f"bold {accent_color}")
    return text


def render_page_help(help_text: str, accent_color: str) -> Text:
    text = Text()
    text.append(help_text, style=accent_color)
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

    preview_styles = ("grey42", "grey50")
    for idx, preview in enumerate(lines[1:]):
        output.append("\n")
        output.append(preview, style=preview_styles[idx % len(preview_styles)])

    return output


def render_results(
    results: TypingResults,
    menu_options: list[str],
    menu_index: int,
    show_match_status: bool,
    results_label: str,
    personal_best_wpm: float | None,
    is_new_personal_best: bool,
    best_update_eligible: bool,
) -> Text:
    result_text = Text()
    result_text.append("\n")
    result_text.append(f"{results_label}\n", style="#9cb0c2")
    result_text.append(f"Time taken : {results.elapsed_time:.2f} seconds\n")
    result_text.append(f"You typed: {results.user_input}\n")
    result_text.append(f"Word per minute: {results.wpm:.2f}\n")
    result_text.append(f"Corrected WPM: {results.correct_wpm:.2f}\n")
    result_text.append(f"Accuracy: {results.accuracy:.2f}%\n")
    result_text.append(
        "Errors: "
        f"{results.incorrect_characters + results.extra_characters} mistyped, "
        f"{results.missed_characters} missed\n"
    )
    result_text.append(f"Personal best: {_format_personal_best(personal_best_wpm)}\n")
    if show_match_status:
        if results.is_match:
            result_text.append("Perfect match!\n", style="green")
        else:
            result_text.append("Text doesn't match the prompt.\n", style="red")
    else:
        result_text.append("Timed test complete.\n", style="green")

    if is_new_personal_best:
        result_text.append("New personal best!\n", style="bold green")
    elif not best_update_eligible:
        result_text.append("Personal best unchanged because the prompt was not completed correctly.\n", style="yellow")

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
    word_count_best_wpm: float | None,
    timed_best_wpm: float | None,
) -> Text:
    title_text = Text()
    title_text.append("\nChoose an option:\n", style="grey62")
    for idx, option in enumerate(menu_options):
        display_option = option
        if option == "Start word-count test":
            display_option = (
                f"{option} (Current: {current_word_count} words, Best: {_format_personal_best(word_count_best_wpm)})"
            )
        elif option == "Start timed test":
            display_option = (
                f"{option} (Current: {current_timed_seconds} seconds, Best: {_format_personal_best(timed_best_wpm)})"
            )

        is_selected = idx == menu_index
        prefix = "  > " if is_selected else "    "
        style = "bold black on #93e1d8" if is_selected else "#8ea3b8"
        title_text.append(f"{prefix}{display_option}\n", style=style)

    title_text.append("Use arrow keys to choose and Enter to confirm.", style="grey50")
    return title_text


def render_settings_menu(
    current_word_count: int,
    current_timed_seconds: int,
    current_word_list_name: str,
    selected_row: int,
) -> Group:
    settings_table = Table.grid(expand=True)
    settings_table.add_column(width=3)
    settings_table.add_column(ratio=2)
    settings_table.add_column(ratio=2)

    rows = [
        ("Word-count test length", f"{current_word_count} words"),
        ("Timed test length", f"{current_timed_seconds} seconds"),
        ("Word list", current_word_list_name),
    ]

    for idx, (label, value) in enumerate(rows):
        is_selected = idx == selected_row
        cursor = ">" if is_selected else " "
        label_style = "bold black on #93e1d8" if is_selected else "#8ea3b8"
        value_style = "bold black on #93e1d8" if is_selected else "#cfd7df"
        settings_table.add_row(
            f" {cursor}",
            Text(label, style=label_style),
            Text(value, style=value_style),
        )

    is_save_selected = selected_row == len(rows)
    save_cursor = ">" if is_save_selected else " "
    save_style = "bold black on #93e1d8" if is_save_selected else "#cfd7df"
    settings_table.add_row(
        f" {save_cursor}",
        Text("Save and return", style=save_style),
        Text("", style=save_style),
    )

    footer = Text(
        "Use Up/Down to move, Left/Right to change values, and Enter on Save and return.",
        style="grey50",
    )
    return Group(Text("\nSettings Form\n", style="grey62"), settings_table, Text(""), footer)
def render_history_screen(
    summary: dict[str, float | int | None],
    records: list[dict],
    mode_filter_label: str,
    setting_filter_label: str,
    word_list_filter_label: str,
    selected_filter_row: int,
) -> Group:
    filter_table = Table.grid(expand=True)
    filter_table.add_column(width=3)
    filter_table.add_column(ratio=2)
    filter_table.add_column(ratio=2)

    filter_rows = [
        ("Mode", mode_filter_label),
        ("Setting", setting_filter_label),
        ("Word list", word_list_filter_label),
        ("Return", "Enter to go back"),
    ]

    for idx, (label, value) in enumerate(filter_rows):
        is_selected = idx == selected_filter_row
        cursor = ">" if is_selected else " "
        label_style = "bold black on #93e1d8" if is_selected else "#8ea3b8"
        value_style = "bold black on #93e1d8" if is_selected else "#cfd7df"
        filter_table.add_row(
            f" {cursor}",
            Text(label, style=label_style),
            Text(value, style=value_style),
        )

    summary_table = Table.grid(expand=True)
    summary_table.add_column(ratio=1)
    summary_table.add_column(ratio=1)
    summary_table.add_column(ratio=1)
    summary_table.add_column(ratio=1)

    total_runs = summary.get("total_runs", 0)
    displayed_runs = summary.get("displayed_runs", 0)
    recent_average_wpm = summary.get("recent_average_wpm")
    recent_best_wpm = summary.get("recent_best_wpm")
    recent_average_accuracy = summary.get("recent_average_accuracy")
    clean_runs = summary.get("clean_runs", 0)
    average_label = f"{recent_average_wpm:.2f} WPM" if isinstance(recent_average_wpm, (int, float)) else "N/A"
    best_label = f"{recent_best_wpm:.2f} WPM" if isinstance(recent_best_wpm, (int, float)) else "N/A"
    accuracy_label = (
        f"{recent_average_accuracy:.2f}%" if isinstance(recent_average_accuracy, (int, float)) else "N/A"
    )

    summary_table.add_row(
        Text(f"Showing\n{displayed_runs}/{total_runs}", style="#cfd7df"),
        Text(f"Recent average\n{average_label}", style="#cfd7df"),
        Text(f"Recent best\n{best_label}", style="#cfd7df"),
        Text(f"Avg accuracy\n{accuracy_label}", style="#cfd7df"),
    )

    history_title = Text("\nRun History\n", style="#9cb0c2")
    clean_runs_text = Text(f"\nClean runs in view: {clean_runs}\n", style="grey62")

    if not records:
        empty = Text(
            "\nNo runs recorded yet. Complete a test to build your history.\n",
            style="grey50",
        )
        footer = Text(
            "\nUse Up/Down to choose a filter row, Left/Right to change filters, and Enter on Return.",
            style="grey50",
        )
        return Group(history_title, filter_table, Text(""), summary_table, clean_runs_text, empty, footer)

    runs_table = Table(
        show_header=True,
        header_style="bold #8ea3b8",
        expand=True,
        box=None,
        pad_edge=False,
    )
    runs_table.add_column("When", ratio=2)
    runs_table.add_column("Mode", ratio=1)
    runs_table.add_column("Setting", ratio=1)
    runs_table.add_column("WPM", ratio=1, justify="right")
    runs_table.add_column("Acc", ratio=1, justify="right")
    runs_table.add_column("Err", ratio=1, justify="right")
    runs_table.add_column("List", ratio=2)

    for record in records:
        timestamp = str(record.get("timestamp", ""))[5:16].replace("T", " ")
        test_mode = str(record.get("test_mode", "unknown"))
        setting_value = int(record.get("setting_value", 0))
        setting_label = format_setting_label(test_mode, setting_value) if setting_value else "?"
        word_list_name = str(record.get("word_list_name", "unknown"))
        wpm = record.get("wpm", 0.0)
        accuracy = record.get("accuracy")
        accuracy_label = f"{accuracy:.1f}%" if isinstance(accuracy, (int, float)) else "N/A"
        error_fields = ("incorrect_characters", "extra_characters", "missed_characters")
        if any(field in record for field in error_fields):
            error_label = str(sum(int(record.get(field, 0)) for field in error_fields))
        elif test_mode == "words" and record.get("is_match"):
            error_label = "0"
        else:
            error_label = "--"
        runs_table.add_row(
            timestamp,
            test_mode,
            setting_label,
            f"{wpm:.2f}",
            accuracy_label,
            error_label,
            word_list_name,
        )

    footer = Text(
        "\nUse Up/Down to choose a filter row, Left/Right to change filters, and Enter on Return.",
        style="grey50",
    )
    return Group(
        history_title,
        filter_table,
        Text(""),
        summary_table,
        clean_runs_text,
        Text("\nRecent Runs\n", style="grey62"),
        runs_table,
        footer,
    )