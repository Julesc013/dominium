# Replay Debugging (DEV-ReplayDebug)

Status: EVOLVING.
Scope: replay-driven debugging and regression analysis.

## Baseline flow
1. Run the server headless to generate a replay:
```
server --headless --data-root <path> --instance-id <uuid> --ticks 120
```
2. Inspect the replay:
```
server --replay <path> --replay-step 0
dominium-tools replay <path>
```
3. Review logs and compat_report alongside the replay for context.

## Determinism checks
- Keep inputs and build versions constant.
- Use replay diff tooling:
```
python tools/playtest/replay_diff.py --left <replay_a> --right <replay_b>
```

## Refusal diagnostics
- Refusals are explicit and encoded with canonical codes.
- Use the refusal explain tool:
```
python tools/inspect/refusal_explain.py --input <refusal_payload.json>
```

## Notes
- Replays are read-only artifacts.
- Replay stepping, rewind, and pause are available via server CLI flags.
