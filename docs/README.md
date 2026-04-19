# TerminalTyper

TerminalTyper is a Textual-based typing test for the terminal. It supports fixed word-count tests, rolling timed tests, selectable word lists, persistent settings, personal bests, and a filterable run history screen.

## Features

- Word-count tests with 30, 60, 90, and 120-word options
- Timed tests with rolling lines and resize-aware wrapping
- Multiple bundled word lists
- Persistent user settings
- Personal best tracking by mode, setting, and word list
- Run history with filters and accuracy/error stats
- Keyboard-first navigation throughout the app

## Requirements

- Python 3.13+

## Installation

From the repository root:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
```

This installs the `terminal-typer` console command.

## Running

You can start the app in either of these ways:

```bash
terminal-typer
```

```bash
python main.py
```

## Data Storage

Release builds no longer write user data into the repository. Settings, history, and personal bests are stored in:

```text
~/.local/share/terminal-typer
```

If `XDG_DATA_HOME` is set, TerminalTyper uses that location instead. You can also override the storage directory explicitly with the `TERMINAL_TYPER_HOME` environment variable.

On first run, TerminalTyper will copy existing JSON data forward from the legacy `config/` directory if those files are present.

## Development

Install editable dependencies and run the app:

```bash
pip install -e .
python main.py
```

Build a release artifact locally:

```bash
uv build
```

## Release Notes

This project is now set up to package its bundled language files with the Python distribution, so installed builds no longer depend on the original repository layout.

For a release summary, see [CHANGELOG.md](../CHANGELOG.md).

## License

TerminalTyper is released under the MIT License. See [LICENSE](../LICENSE).
