from .app import TerminalTyperApp
from .prompts import generate_prompt, generate_timed_line


def main() -> None:
    app = TerminalTyperApp(generate_prompt, generate_timed_line)
    app.run()


if __name__ == "__main__":
    main()
