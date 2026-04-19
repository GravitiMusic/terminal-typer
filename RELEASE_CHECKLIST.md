# Release Checklist

## Before Tagging

- Confirm the working tree is clean except for intentional release changes
- Run the app locally and check the main menu, settings, history, word-count mode, and timed mode
- Review CHANGELOG.md and confirm the release notes match the shipped features
- Verify the version in pyproject.toml and terminal_typer/__init__.py matches the intended release number

## Build And Verify

- Build artifacts: `uv build`
- Confirm both `dist/terminal_typer-<version>.tar.gz` and `dist/terminal_typer-<version>-py3-none-any.whl` are created
- Smoke-test package import: `python -c "import terminal_typer; print(terminal_typer.__version__)"`
- Smoke-test launcher: `python main.py`

## Repository Review

- Confirm LICENSE is present and referenced in metadata
- Confirm README.md and docs/README.md reflect the current install and runtime behavior
- Confirm user data is not being written into the repository tree
- Confirm .gitignore matches the current project layout

## Release Steps

- Commit the release changes
- Tag the release, for example `v0.1.0`
- Push the commit and tag
- Publish the built artifacts wherever you distribute releases

## After Release

- Start a new changelog section for the next unreleased version
- Bump the version only when the next release cycle actually begins
