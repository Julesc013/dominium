Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Native UI Policy

Server, launcher, setup, and tools may use OS-native widgets in GUI mode, but
GUI remains optional and must not block CLI/TUI paths.

Policy rules:
- GUI mode is always opt-in via `--ui=gui`.
- Missing GUI support must fail loudly with a non-zero exit code.
- GUI code sits behind a small product-local boundary so core logic stays
  testable without UI.

APR3 status:
- `server`, `launcher`, `setup`, and `tools` return `D_APP_EXIT_UNAVAILABLE`
  with a clear "gui not implemented" message.