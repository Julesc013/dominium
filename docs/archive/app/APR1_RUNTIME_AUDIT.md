# ARCHIVED: APR1 Runtime Audit

Archived: point-in-time audit.
Reason: APR audit snapshot; current product contracts supersede it.
Superseded by:
- `docs/app/README.md`
- `docs/app/PRODUCT_BOUNDARIES.md`
- `docs/app/RUNTIME_LOOP.md`
Still useful: background on early runtime inventory.

# APR1 Runtime Audit

This audit captures current runtime loops, timing sources, shutdown behavior, and determinism risks
for client/server/launcher/setup/tools. It is descriptive only (no refactor).

## Client
Loop shape:
- CLI-only paths: no loop; exits after printing or running MP0 demo.
- Windowed mode: `client_run_windowed` uses a loop that:
  - polls platform events (`dsys_poll_event`)
  - handles quit/resize/DPI events
  - submits a minimal frame and presents
  - sleeps for ~16ms

Timing sources:
- `dsys_sleep_ms(16)` in the windowed loop for frame pacing.
- No explicit time deltas in CLI paths.

Termination paths:
- `DSYS_EVENT_QUIT` or `dsys_window_should_close` ends windowed loop.
- No signal/CTRL+C handling; CLI paths exit by returning from `main`.

Determinism risks:
- Windowed loop uses real-time sleep and OS event timing (not used by tests).
- CLI smoke path uses deterministic MP0 demo.

## Server
Loop shape:
- CLI-only; no persistent loop.
- MP0 loopback/server-auth demos run a fixed number of ticks and exit.

Timing sources:
- None in app layer (no sleep calls).

Termination paths:
- No signal handling; exits after completing demo or printing status.

Determinism risks:
- MP0 demos are deterministic; no known nondeterministic outputs in smoke/status paths.

## Launcher
Loop shape:
- CLI-only; no loop.
- Commands perform immediate work (version, list-profiles, capabilities).

Timing sources:
- None in app layer.

Termination paths:
- No signal handling.

Determinism risks:
- Capability probe reads platform/renderer availability; output is deterministic for a given build/host.

## Setup
Loop shape:
- CLI-only; no loop.
- `status` and `prepare` commands execute once and exit.

Timing sources:
- None in app layer.

Termination paths:
- No signal handling.

Determinism risks:
- `prepare` touches filesystem; deterministic for a given path, not used by tests unless requested.

## Tools
Loop shape:
- CLI-only; no loop.
- Commands are stubs or one-shot operations.

Timing sources:
- None in app layer.

Termination paths:
- No signal handling.

Determinism risks:
- CLI smoke/status paths print fixed strings; deterministic.

## Platform/runtime notes
- DSYS Win32 backend queues events in the window proc and exposes them via `dsys_poll_event`.
- No unified signal/CTRL+C handling exists in DSYS or app layers.
