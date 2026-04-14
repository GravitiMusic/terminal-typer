import time
from collections.abc import Callable

from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.events import Key
from textual.widgets import Footer, Static

from .constants import (
    APP_CSS,
    MENU_OPTIONS,
    TIMED_LINE_WORDS,
    TIMED_SECONDS_OPTIONS,
    TIMED_VISIBLE_LINES,
    TITLE_MENU_OPTIONS,
    WORD_COUNT_OPTIONS,
)
from .metrics import TypingResults, calculate_results
from .renderers import (
    render_intro_logo,
    render_progress,
    render_results,
    render_settings_menu,
    render_timed_progress,
    render_title_menu,
)
from .settings import UserSettings, load_settings, save_settings


class TerminalTyperApp(App):
    CSS = APP_CSS
    BINDINGS = [("escape", "quit", "Quit")]

    def __init__(
        self,
        word_prompt_provider: Callable[[int], str],
        timed_line_provider: Callable[[int], str],
    ) -> None:
        super().__init__()
        self.word_prompt_provider = word_prompt_provider
        self.timed_line_provider = timed_line_provider
        self.prompt_text = ""
        self.settings: UserSettings = load_settings()
        self.chars: list[str] = []
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.test_mode = "words"
        self.timed_deadline: float | None = None
        self.timed_refresh_timer = None
        self.timed_lines: list[str] = []
        self.timed_line_chars: list[str] = []
        self.mode = "intro"
        self.intro_frame = 0
        self.intro_timer = None
        self.title_menu_options = list(TITLE_MENU_OPTIONS)
        self.title_menu_index = 0
        self.word_count_options = list(WORD_COUNT_OPTIONS)
        self.timed_seconds_options = list(TIMED_SECONDS_OPTIONS)
        self.word_count_index = self.word_count_options.index(self.settings.word_count)
        self.timed_seconds_index = self.timed_seconds_options.index(self.settings.timed_seconds)
        self.settings_row_index = 0
        self.menu_options = list(MENU_OPTIONS)
        self.menu_index = 0
        self.result: TypingResults | None = None

    def compose(self) -> ComposeResult:
        with Vertical(id="root"):
            with Vertical(id="card"):
                yield Static("Welcome to", id="intro_welcome")
                yield Static(id="intro_logo")
                yield Static("Choose an option from the menu below.", id="intro_prompt")
                with VerticalScroll(id="content_scroller"):
                    yield Static("Type this text", id="title")
                    yield Static("Type to begin. Enter to finish. Backspace to correct.", id="help")
                    yield Static(id="target")
                    yield Static(id="summary")
        yield Footer()

    def on_mount(self) -> None:
        self._show_intro()
        self.intro_timer = self.set_interval(0.12, self._animate_intro)

    def on_key(self, event: Key) -> None:
        if self.mode == "intro":
            self._handle_intro_keys(event.key)
            return

        if self.mode == "settings":
            self._handle_settings_keys(event.key)
            return

        if self.mode == "results":
            self._handle_results_keys(event.key)
            return

        if self.mode != "typing":
            return

        if self.test_mode == "timed" and self._timed_test_expired():
            self._finish_timed_test()
            return

        key_name = event.key
        character = event.character

        if key_name == "enter":
            if self.test_mode == "timed":
                return
            self.end_time = time.perf_counter()
            self._refresh_target()
            self._show_results()
            return

        if key_name == "backspace":
            if self.test_mode == "timed":
                if self.timed_line_chars:
                    self.timed_line_chars.pop()
                    if self.chars:
                        self.chars.pop()
            elif self.chars:
                self.chars.pop()
            self._refresh_target()
            return

        if character is None or len(character) != 1 or ord(character) < 32:
            return

        if self.start_time is None:
            self.start_time = time.perf_counter()
            if self.test_mode == "timed":
                self.timed_deadline = self.start_time + self.settings.timed_seconds

        if self.test_mode == "timed":
            self._handle_timed_character(character)
            return

        self.chars.append(character)
        self._refresh_target()
        self._update_timed_status_if_needed()

    def _show_intro(self) -> None:
        self.mode = "intro"
        self.query_one("#content_scroller", VerticalScroll).scroll_home(animate=False)
        self.query_one("#intro_welcome", Static).display = True
        self.query_one("#intro_logo", Static).display = True
        self.query_one("#intro_prompt", Static).display = True

        self.query_one("#title", Static).display = True
        self.query_one("#title", Static).update("Main Menu")
        self.query_one("#help", Static).display = True
        self.query_one("#help", Static).update("Use arrow keys to navigate. Enter to select.")
        self.query_one("#target", Static).display = False
        self.query_one("#summary", Static).display = True
        self.query_one("#summary", Static).update(
            render_title_menu(
                self.title_menu_options,
                self.title_menu_index,
                self.settings.word_count,
                self.settings.timed_seconds,
            )
        )

        if self.intro_timer is None:
            self.intro_timer = self.set_interval(0.12, self._animate_intro)

        self._animate_intro()

    def _start_word_count_test(self) -> None:
        self.test_mode = "words"
        prompt_text = self.word_prompt_provider(self.settings.word_count)
        self._start_typing_test(prompt_text)

    def _start_timed_test(self) -> None:
        self.test_mode = "timed"
        prompt_text = self._build_initial_timed_prompt()
        self._start_typing_test(prompt_text)
        self._update_timed_status_if_needed()

        if self.timed_refresh_timer is None:
            self.timed_refresh_timer = self.set_interval(0.1, self._on_timed_tick)

    def _start_typing_test(self, prompt_text: str) -> None:
        self.mode = "typing"
        self.query_one("#content_scroller", VerticalScroll).scroll_home(animate=False)
        self.prompt_text = prompt_text
        self.chars = []
        self.timed_line_chars = []
        self.start_time = None
        self.end_time = None
        self.result = None
        self.timed_deadline = None
        self._stop_timed_refresh_timer()

        if self.intro_timer is not None:
            self.intro_timer.stop()
            self.intro_timer = None

        self.query_one("#intro_welcome", Static).display = False
        self.query_one("#intro_logo", Static).display = False
        self.query_one("#intro_prompt", Static).display = False

        self.query_one("#title", Static).display = True
        self.query_one("#title", Static).update("Type this text")
        self.query_one("#help", Static).display = True
        if self.test_mode == "timed":
            self.query_one("#help", Static).update("Type until the timer ends. Backspace to correct.")
        else:
            self.query_one("#help", Static).update("Type to begin. Enter to finish. Backspace to correct.")
        self.query_one("#target", Static).display = True
        self.query_one("#summary", Static).display = True
        if self.test_mode == "timed":
            self._update_timed_status_if_needed()
        else:
            self.query_one("#summary", Static).update("")
        self._refresh_target()

    def _show_settings(self) -> None:
        self.mode = "settings"
        self.query_one("#content_scroller", VerticalScroll).scroll_home(animate=False)
        self.word_count_index = self.word_count_options.index(self.settings.word_count)
        self.timed_seconds_index = self.timed_seconds_options.index(self.settings.timed_seconds)
        self.settings_row_index = 0
        self.query_one("#intro_welcome", Static).display = True
        self.query_one("#intro_logo", Static).display = True
        self.query_one("#intro_prompt", Static).display = True

        self.query_one("#title", Static).display = True
        self.query_one("#title", Static).update("Settings")
        self.query_one("#help", Static).display = True
        self.query_one("#help", Static).update("Configure your test defaults.")
        self.query_one("#target", Static).display = False
        self.query_one("#summary", Static).display = True
        self.query_one("#summary", Static).update(
            render_settings_menu(
                self.word_count_options[self.word_count_index],
                self.timed_seconds_options[self.timed_seconds_index],
                self.settings_row_index,
            )
        )

    def _handle_intro_keys(self, key_name: str) -> None:
        if key_name in ("up", "left"):
            self.title_menu_index = (self.title_menu_index - 1) % len(self.title_menu_options)
            self.query_one("#summary", Static).update(
                render_title_menu(
                    self.title_menu_options,
                    self.title_menu_index,
                    self.settings.word_count,
                    self.settings.timed_seconds,
                )
            )
            return

        if key_name in ("down", "right"):
            self.title_menu_index = (self.title_menu_index + 1) % len(self.title_menu_options)
            self.query_one("#summary", Static).update(
                render_title_menu(
                    self.title_menu_options,
                    self.title_menu_index,
                    self.settings.word_count,
                    self.settings.timed_seconds,
                )
            )
            return

        if key_name == "enter":
            selected = self.title_menu_options[self.title_menu_index]
            if selected == "Start word-count test":
                self._start_word_count_test()
            elif selected == "Start timed test":
                self._start_timed_test()
            else:
                self._show_settings()

    def _handle_settings_keys(self, key_name: str) -> None:
        if key_name == "up":
            self.settings_row_index = (self.settings_row_index - 1) % 3
            self._refresh_settings_menu()
            return

        if key_name == "down":
            self.settings_row_index = (self.settings_row_index + 1) % 3
            self._refresh_settings_menu()
            return

        if key_name == "left":
            if self.settings_row_index == 0:
                self.word_count_index = (self.word_count_index - 1) % len(self.word_count_options)
            elif self.settings_row_index == 1:
                self.timed_seconds_index = (self.timed_seconds_index - 1) % len(self.timed_seconds_options)
            self._refresh_settings_menu()
            return

        if key_name == "right":
            if self.settings_row_index == 0:
                self.word_count_index = (self.word_count_index + 1) % len(self.word_count_options)
            elif self.settings_row_index == 1:
                self.timed_seconds_index = (self.timed_seconds_index + 1) % len(self.timed_seconds_options)
            self._refresh_settings_menu()
            return

        if key_name == "enter":
            if self.settings_row_index == 2:
                self.settings.word_count = self.word_count_options[self.word_count_index]
                self.settings.timed_seconds = self.timed_seconds_options[self.timed_seconds_index]
                save_settings(self.settings)
                self._show_intro()

    def _handle_results_keys(self, key_name: str) -> None:
        if key_name in ("up", "left"):
            self.menu_index = (self.menu_index - 1) % len(self.menu_options)
            self._show_results()
            return

        if key_name in ("down", "right"):
            self.menu_index = (self.menu_index + 1) % len(self.menu_options)
            self._show_results()
            return

        if key_name == "enter":
            selected = self.menu_options[self.menu_index]
            if selected == "Retry test":
                if self.test_mode == "timed":
                    self._start_timed_test()
                else:
                    self._start_word_count_test()
            else:
                self.menu_index = 0
                self._show_intro()

    def _animate_intro(self) -> None:
        if self.mode != "intro":
            return

        logo = self.query_one("#intro_logo", Static)
        logo.update(render_intro_logo(self.intro_frame))
        self.intro_frame += 1

    def _refresh_target(self) -> None:
        target = self.query_one("#target", Static)
        if self.test_mode == "timed":
            lines_for_render = list(self.timed_lines)
            if lines_for_render:
                lines_for_render[0] = self._active_timed_line_target()
            target.update(render_timed_progress(lines_for_render, "".join(self.timed_line_chars)))
            self.query_one("#content_scroller", VerticalScroll).scroll_home(animate=False)
            return

        target.update(render_progress(self.prompt_text, "".join(self.chars)))
        self.query_one("#content_scroller", VerticalScroll).scroll_end(animate=False)

    def _build_initial_timed_prompt(self) -> str:
        self.timed_lines = [
            self.timed_line_provider(TIMED_LINE_WORDS)
            for _ in range(TIMED_VISIBLE_LINES)
        ]
        return " ".join(self.timed_lines)

    def _advance_timed_line(self) -> None:
        if self.timed_lines:
            self.timed_lines.pop(0)
        self.timed_lines.append(self.timed_line_provider(TIMED_LINE_WORDS))
        self.prompt_text = " ".join(self.timed_lines)
        self.timed_line_chars = []

    def _active_timed_line_target(self) -> str:
        if not self.timed_lines:
            return ""
        # Preserve a contiguous word stream across visual line boundaries.
        return f"{self.timed_lines[0]} "

    def _handle_timed_character(self, character: str) -> None:
        self.chars.append(character)
        self.timed_line_chars.append(character)

        active_line_target = self._active_timed_line_target()
        if active_line_target and len(self.timed_line_chars) >= len(active_line_target):
            self._advance_timed_line()

        self._refresh_target()
        self._update_timed_status_if_needed()

    def _refresh_settings_menu(self) -> None:
        self.query_one("#summary", Static).update(
            render_settings_menu(
                self.word_count_options[self.word_count_index],
                self.timed_seconds_options[self.timed_seconds_index],
                self.settings_row_index,
            )
        )

    def _timed_test_expired(self) -> bool:
        return self.timed_deadline is not None and time.perf_counter() >= self.timed_deadline

    def _update_timed_status_if_needed(self) -> None:
        if self.test_mode != "timed" or self.mode != "typing":
            return

        if self.timed_deadline is None:
            self.query_one("#summary", Static).update(
                f"Time left: {self.settings.timed_seconds:.1f}s | Timer starts on first keystroke"
            )
            return

        time_left = max(0.0, self.timed_deadline - time.perf_counter())
        self.query_one("#summary", Static).update(
            f"Time left: {time_left:.1f}s | Target duration: {self.settings.timed_seconds}s"
        )

    def _on_timed_tick(self) -> None:
        if self.mode != "typing" or self.test_mode != "timed":
            return

        if self._timed_test_expired():
            self._finish_timed_test()
            return

        self._update_timed_status_if_needed()

    def _finish_timed_test(self) -> None:
        self.end_time = time.perf_counter()
        self._show_results()

    def _stop_timed_refresh_timer(self) -> None:
        if self.timed_refresh_timer is not None:
            self.timed_refresh_timer.stop()
            self.timed_refresh_timer = None

    def _show_results(self) -> None:
        summary = self.query_one("#summary", Static)
        self._stop_timed_refresh_timer()
        self.mode = "results"
        self.result = calculate_results(
            prompt_text=self.prompt_text,
            typed_chars=self.chars,
            start_time=self.start_time,
            end_time=self.end_time,
        )
        results_label = (
            f"Timed test ({self.settings.timed_seconds} seconds)"
            if self.test_mode == "timed"
            else f"Word-count test ({self.settings.word_count} words)"
        )
        summary.update(
            render_results(
                self.result,
                self.menu_options,
                self.menu_index,
                show_match_status=self.test_mode != "timed",
                results_label=results_label,
            )
        )