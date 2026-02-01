Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Replay Workflow (DEV-Replay)

Status: EVOLVING.
Scope: replay-first run and inspection workflow.

## Guarantees
- Every headless server run emits a replay unless `--no-replay` is set.
- Replays are deterministic for identical inputs and build versions.
- Replays are read-only artifacts; they do not mutate state.

## Server replay controls
Use the server CLI to scan replay events:
```
server --replay <file>
server --replay <file> --replay-step 0
server --replay <file> --replay-rewind --replay-steps 10
server --replay <file> --replay-pause
```

## Tooling
- `dominium-tools replay <file>` reads and summarizes replay files.
- `tools/playtest/replay_diff.py` compares replay outputs across runs.
- `tools/playtest/replay_metrics.py` summarizes replay-derived metrics.

## Recommended workflow
1. Run headless server to generate replay and compat_report.
2. Inspect replay with server `--replay` or `dominium-tools replay`.
3. Diff replays across builds or configurations if determinism is questioned.