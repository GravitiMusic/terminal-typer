APP_NAME = "TerminalTyper"
DEFAULT_WORDS_PER_TEST = 30
DEFAULT_TIMED_SECONDS = 30
TIMED_LINE_WORDS = 15
TIMED_VISIBLE_LINES = 3
WORD_COUNT_OPTIONS = (30, 60, 90, 120)
TIMED_SECONDS_OPTIONS = (30, 60, 90, 120)
TITLE_MENU_OPTIONS = ("Start word-count test", "Start timed test", "Settings")

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
    height: 90%;
    border: tall #2e3b47;
    padding: 1 2;
    background: #141b22;
}

#content_scroller {
    height: 1fr;
    overflow-y: auto;
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