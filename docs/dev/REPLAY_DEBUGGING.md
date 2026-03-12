Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Replay Debugging (DEV-ReplayDebug)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


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
