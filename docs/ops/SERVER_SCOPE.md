Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Server Scope (OPS-Server)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: EVOLVING.
Scope: server responsibilities, run modes, and operational guarantees.

## Responsibilities
- Headless-first: server must run without any client or graphical shell.
- Generate a compat_report for every mode (run/inspect/validate/replay).
- Emit structured logs for every significant action.
- Produce deterministic replays for every run unless explicitly disabled.
- Refuse explicitly on incompatibility or invalid intent; never fail silently.
- Never mutate state outside the current process execution.

## Non-goals
- No client UI assumptions.
- No implicit content installation or pack mutation.
- No hidden compatibility decisions.

## Run modes (CLI)
- `--headless` (default): Run the headless server loop and emit replay + logs.
- `--inspect`: Read-only inspection via the app read-only adapter.
- `--validate`: Compatibility validation only (no run, no mutation).
- `--replay <file>`: Read-only replay scan with step/rewind/pause.

## Artifact roots
Server artifacts are scoped by `data_root` and `instance_id`:
- `data_root`: resolved from `--data-root`, `DOM_DATA_ROOT`, `DOM_INSTANCE_ROOT`, or `./data`.
- Log root (per instance): `data_root/logs/server/<instance_id>/server.log`.
- Replay (per instance): `data_root/replays/<instance_id>/server.replay`.
- compat_report (per instance): `data_root/compat/<instance_id>/compat_report.json`.

Overrides:
- `--log-root` overrides the base log root (instance subdirectory still applied).
- `--replay-out` overrides the replay output path (headless mode only).
- `--compat-report` overrides the compat_report output path.

## Explicit refusal behavior
- Compatibility failures return `D_APP_EXIT_UNAVAILABLE` and include refusal codes.
- Replay/inspect/validate failures emit explicit refusal logs and messages.
