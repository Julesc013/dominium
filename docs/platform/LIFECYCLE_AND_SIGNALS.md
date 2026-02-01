Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Lifecycle and Signals

The platform runtime exposes explicit lifecycle helpers. Signal handlers only
set flags; application loops exit cleanly on the next iteration.

## APIs
- `dsys_lifecycle_init()`: install signal/console handlers.
- `dsys_lifecycle_shutdown()`: restore previous handlers.
- `dsys_lifecycle_request_shutdown(reason)`: request shutdown from app logic.
- `dsys_lifecycle_shutdown_requested()`: poll shutdown flag.
- `dsys_lifecycle_shutdown_reason()`/`_text()`: retrieve reason.

## Signals handled
- POSIX: `SIGINT`, `SIGTERM`
- Windows: `CTRL_C_EVENT`, `CTRL_BREAK_EVENT`, console close/logoff/shutdown

Handlers never call into engine/game logic and do not perform heavy work. They
only set shutdown flags and a reason code.

## Exit codes
Shared exit codes are defined in `domino/app/runtime.h`:
- `0` clean exit (window close or app-requested shutdown)
- `130` signal/console shutdown
- `1` runtime failure
- `2` usage/CLI error
- `3` explicit unavailability (e.g., renderer requested but missing)

## Current usage
Client windowed/TUI and tools TUI loops install handlers and poll the shutdown
flag each loop iteration. CLI-only commands rely on default OS behavior and do
not install lifecycle handlers.