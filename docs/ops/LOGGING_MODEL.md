Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Logging Model (OPS-Log)

Status: EVOLVING.
Scope: server logging format, rotation, and guarantees.

## Format
Server logs are JSON-lines with a header:
```
{"schema":"server_log_v1"}
```

Each event is a single JSON object with the following fields:
- `seq` (integer): monotonically increasing sequence number.
- `tick` (integer): tick index for run-loop events.
- `level` (string): `info`, `warn`, or `error`.
- `domain` (string): subsystem or context (e.g., `server`, `compat`, `replay`).
- `event` (string): event name (e.g., `start`, `shutdown`, `advance`).
- `message` (string, optional): human-readable summary.
- `refusal_code_id` (integer, optional): canonical refusal code id.
- `refusal_code` (string, optional): canonical refusal code token.

Ordering is deterministic and is defined by `seq`.

## Rotation
Rotation is size-based and preserves all data:
- `--log-max-bytes <n>` sets the maximum size per log file (0 disables rotation).
- `--log-rotate-max <n>` sets the max number of rotated files to keep.
- Rotated files use numeric suffixes (`server.log.1`, `server.log.2`, ...).

## Location
Logs are per-instance:
`data_root/logs/server/<instance_id>/server.log`

## Presentation guarantees
- Warnings and errors are explicit via `level`.
- Refusals always include canonical refusal codes.
- No stack traces are emitted by default.