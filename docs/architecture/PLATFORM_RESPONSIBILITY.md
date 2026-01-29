# Platform Responsibility (PLATFORM-PERFECT-0)

Status: FROZEN.

Purpose: Freeze the platform runtime layer so all supported operating systems, environments, and execution modes behave consistently without affecting simulation semantics.

## Platform Responsibility (Final)

The platform layer provides only:

- process lifecycle
- file system access (sandbox-aware)
- monotonic time source
- threading primitives (capability-gated)
- input events (optional)
- IPC primitives
- windowing (optional)
- environment discovery

The platform layer MUST NOT:

- know about simulation state
- know about gameplay or content
- influence authority or determinism
- embed policy decisions

## Supported Platform Classes

All platforms expose the same abstract interfaces:

### Full OS platforms

- Windows (Win9x, WinNT+)
- Linux
- macOS (Classic + X)

### POSIX-like / UNIX

- BSD variants
- embedded POSIX

### Bare / restricted environments

- headless servers
- containers
- CI environments
- minimal libc environments

### Null platform

- no filesystem
- no input
- no windowing
- used for testing and verification

## Filesystem & Path Rules

- No absolute paths are stored in simulation artifacts.
- All file access routes through the platform FS abstraction.
- Sandbox policy is enforced at the FS boundary.
- Directory iteration order is deterministic and platform-independent.

## Time & Clock Model

- Monotonic time only.
- No wall-clock dependence in authoritative logic.
- Tests may inject time sources explicitly.
- Time policy selection is explicit (deterministic vs interactive).

## Threading & Concurrency

- Threading is a capability and may be disabled.
- Single-thread fallback must work everywhere.
- Thread count MUST NOT affect determinism.
- Authoritative scheduling follows deterministic ordering rules.

## IPC & Multi-Process

Required IPC channels:

- launcher ↔ client
- launcher ↔ server
- sidecar AI IPC
- tool IPC

IPC MUST be message-based, deterministic, and include compat_report metadata.

## Environment & Config

Environment variables are documented here and must not affect simulation semantics.

Platform path overrides (system only):

- `DSYS_PATH_APP_ROOT`
- `DSYS_PATH_USER_DATA`
- `DSYS_PATH_USER_CONFIG`
- `DSYS_PATH_USER_CACHE`
- `DSYS_PATH_TEMP`

Tooling-only controls (no simulation impact):

- `OPS_DETERMINISTIC` (forces deterministic timestamps in ops/share/bugreport tools)
- `USERNAME`, `USER` (used only for optional redaction labels)

Any new environment variable must be added to this list and reviewed as a contract change.

Config loading is explicit and validated. No implicit config discovery may affect simulation.

## Error Handling & Exit Codes

Exit codes are standardized across all binaries:

- `D_APP_EXIT_OK` = 0
- `D_APP_EXIT_FAILURE` = 1
- `D_APP_EXIT_USAGE` = 2
- `D_APP_EXIT_UNAVAILABLE` = 3
- `D_APP_EXIT_SIGNAL` = 130

Platform errors are explicit and must never masquerade as simulation failures.

## Freeze & Lock

The platform runtime layer is FROZEN. Allowed changes are limited to:

- bug fixes
- new platform backends that obey the same contracts
