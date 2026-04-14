import time

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.events import Key
from textual.widgets import Footer, Static

from .constants import APP_CSS, MENU_OPTIONS
from .metrics import TypingResults, calculate_results
from .renderers import render_intro_logo, render_progress, render_results


class TerminalTyperApp(App):
    CSS = APP_CSS
    BINDINGS = [("escape", "quit", "Quit")]

    def __init__(self, prompt_text: str) -> None:
        super().__init__()
        self.prompt_text = prompt_text
        self.chars: list[str] = []
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.mode = "intro"
        self.intro_frame = 0
        self.intro_timer = None
        self.menu_options = list(MENU_OPTIONS)
        self.menu_index = 0
        self.result: TypingResults | None = None

    def compose(self) -> ComposeResult:
        with Vertical(id="root"):
            with Vertical(id="card"):
                yield Static("Welcome to", id="intro_welcome")
                yield Static(id="intro_logo")
                yield Static("Press Enter to start the typing test.", id="intro_prompt")
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
            if event.key == "enter":
                self._start_typing_test()
            return

        if self.mode == "results":
            self._handle_results_keys(event.key)
            return

        if self.mode != "typing":
            return

        key_name = event.key
        character = event.character

        if key_name == "enter":
            self.end_time = time.perf_counter()
            self._refresh_target()
            self._show_results()
            return

        if key_name == "backspace":
            if self.chars:
                self.chars.pop()
            self._refresh_target()
            return

        if character is None or len(character) != 1 or ord(character) < 32:
            return

        if self.start_time is None:
            self.start_time = time.perf_counter()

        self.chars.append(character)
        self._refresh_target()

    def _show_intro(self) -> None:
        self.mode = "intro"
        self.query_one("#intro_welcome", Static).display = True
        self.query_one("#intro_logo", Static).display = True
        self.query_one("#intro_prompt", Static).display = True

        self.query_one("#title", Static).display = False
        self.query_one("#help", Static).display = False
        self.query_one("#target", Static).display = False
        self.query_one("#summary", Static).display = False

        if self.intro_timer is None:
            self.intro_timer = self.set_interval(0.12, self._animate_intro)

        self._animate_intro()

    def _start_typing_test(self) -> None:
        self.mode = "typing"
        self.chars = []
        self.start_time = None
        self.end_time = None
        self.result = None

        if self.intro_timer is not None:
            self.intro_timer.stop()
            self.intro_timer = None

        self.query_one("#intro_welcome", Static).display = False
        self.query_one("#intro_logo", Static).display = False
        self.query_one("#intro_prompt", Static).display = False

        self.query_one("#title", Static).display = True
        self.query_one("#help", Static).display = True
        self.query_one("#target", Static).display = True
        self.query_one("#summary", Static).display = True
        self.query_one("#summary", Static).update("")
        self._refresh_target()

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
                self._start_typing_test()
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
        target.update(render_progress(self.prompt_text, "".join(self.chars)))

    def _show_results(self) -> None:
        summary = self.query_one("#summary", Static)
        self.mode = "results"
        self.result = calculate_results(
            prompt_text=self.prompt_text,
            typed_chars=self.chars,
            start_time=self.start_time,
            end_time=self.end_time,
        )
        summary.update(render_results(self.result, self.menu_options, self.menu_index))