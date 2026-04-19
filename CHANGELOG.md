# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-04-18

Initial packaged release of TerminalTyper.

### Added

- Word-count typing tests with selectable test lengths
- Timed typing mode with rolling, resize-aware lines
- Multiple bundled word lists packaged with the application
- Persistent settings for test length, timed duration, and word list selection
- Personal best tracking by mode, setting, and word list
- Run history with per-run accuracy and error statistics
- Filterable History screen in the terminal UI
- Release packaging with a console entrypoint and bundled resources
- Per-user data storage outside the repository

### Changed

- Project packaging now uses a standard root pyproject configuration
- User runtime data now lives under the user data directory instead of the repo
- Language assets are now loaded from packaged resources instead of the old repo-only path

### Fixed

- Prevented scroll-container key handling from interfering with page navigation
- Fixed duplicate history recording on results redraw
- Stabilized timed-mode line wrapping and resize behavior
