# Server Operations (OPS-CLI)

Status: EVOLVING.
Scope: server CLI operations, modes, and artifacts.

## Headless run (default)
```
server --headless --data-root <path> --instance-id <uuid> --ticks 120
```
Artifacts:
- Logs: `data_root/logs/server/<instance_id>/server.log`
- Replay: `data_root/replays/<instance_id>/server.replay`
- compat_report: `data_root/compat/<instance_id>/compat_report.json`

## Inspect mode (read-only)
```
server --inspect --format json --data-root <path> --instance-id <uuid>
```

## Validate mode (compatibility only)
```
server --validate --data-root <path> --instance-id <uuid>
```

## Replay scan (read-only)
```
server --replay <file> --replay-step 0
server --replay <file> --replay-rewind --replay-steps 5
server --replay <file> --replay-pause
```

## Key options
- `--data-root <path>`: override data root (default uses env or `./data`).
- `--instance-id <id>`: instance identifier (UUID preferred).
- `--compat-report <path>`: explicit compat_report path.
- `--log-root <path>`: base log root (instance subdirectory applied).
- `--log-max-bytes <n>`: max bytes per log file (0 disables rotation).
- `--log-rotate-max <n>`: max number of rotated logs to keep.
- `--replay-out <path>`: replay output path (headless only).
- `--replay-rotate-max <n>`: max number of rotated replays to keep.
- `--no-replay`: disable replay generation (headless only).
- `--checkpoint-interval <n>`: checkpoint log cadence.
- `--health-interval <n>`: health log cadence (placeholder).

## Exit codes
- `0`: success
- `2`: CLI usage error
- `3`: unavailable/refused (compatibility, replay read failures)
