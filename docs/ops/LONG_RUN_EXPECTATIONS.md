# Long-Run Expectations (OPS-LongRun)

Status: EVOLVING.
Scope: long-run stability expectations and fixtures.

## Goals
- Long-running server sessions remain stable and deterministic.
- Logs and replays are continuously generated without data loss.
- Shutdown is clean and explicit, with replay and logs closed.

## Fixture controls (headless)
- `--ticks <n>`: length of the run in ticks.
- `--checkpoint-interval <n>`: emits checkpoint log entries every N ticks.
- `--health-interval <n>`: emits health log entries every N ticks.

These options are used by the long-run fixture to exercise stability over
extended durations (including overnight runs).

## Memory plateau checks
The current server implementation logs health checks but does not enforce
memory plateau validation yet. When `--health-interval` is set, the server
emits a warning and a refusal code (`REFUSE_INVALID_INTENT`) to indicate the
check is not available.

## Expected behavior
- No silent restarts; any failure is explicit and logged.
- Replays are deterministic across identical runs.
- Logs remain structured and ordered across rotations.
