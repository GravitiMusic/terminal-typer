from terminal_typer.app import TerminalTyperApp
from terminal_typer.constants import PROMPT_TEXT


def main() -> None:
    app = TerminalTyperApp(PROMPT_TEXT)
    app.run()


if __name__ == "__main__":
    main()
