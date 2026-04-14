PROMPT_TEXT = "The quick brown fox jumps over the lazy dog."
APP_NAME = "TerminalTyper"

LOGO_PALETTE = (
    "#f9c74f",
    "#90be6d",
    "#43aa8b",
    "#4d908e",
    "#577590",
    "#f3722c",
    "#f9844a",
)

MENU_OPTIONS = ("Retry test", "Return to title screen")

APP_CSS = """
Screen {
    background: #101418;
    color: #d6dde4;
}

#root {
    width: 100%;
    height: 100%;
    align: center middle;
}

#card {
    width: 88;
    max-width: 95%;
    border: tall #2e3b47;
    padding: 1 2;
    background: #141b22;
}

#title {
    text-style: bold;
    color: #a7c7e7;
    margin-bottom: 1;
}

#intro_welcome {
    color: #8ea3b8;
    text-style: bold;
    margin-bottom: 1;
}

#intro_logo {
    text-style: bold;
    margin-bottom: 1;
}

#intro_prompt {
    color: #9cb0c2;
    margin-bottom: 1;
}

#help {
    color: #8f9dad;
    margin-bottom: 1;
}

#target {
    margin-bottom: 1;
}

#summary {
    margin-top: 1;
    color: #cfd7df;
}
"""