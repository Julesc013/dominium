# Latest Warning Disposition

Current task: `FAST-STRICT-TEST-TIER-01`.

## Accepted Local/Generated Warnings

- `.aide.local/**`, `.dominium.local/**`, `.xstack_cache/**`, `build/`, `out/`, `dist/`, `artifacts/`, `tmp/`, and `__pycache__/` remain local/generated roots and must not be tracked.
- Task evidence under `.aide/reports/FAST-STRICT-TEST-TIER-01-*` is tracked audit evidence, not local cache output.

## Repaired Warnings

- Dominium now has an explicit normal development proof gate: `fast_strict` = T0 + T1 + T2.
- The normal gate passed 30/30 commands in 332.828 seconds.
- Full CTest is no longer treated as the routine edit-loop gate.

## Blocking Warnings

- Full CTest is still not green and remains T4 full/release debt.
- The previous recorded full CTest result is 440/503 passed, 63 failed, about 3227.41 seconds; this task did not rerun it.
- `FULL-GATE-DEBT-01` remains required for broad full-proof debt.
- Feature work and DOE-00 remain blocked until Foundation Lock closes.

Next task: `PUBLIC-SURFACE-REGISTRY-01`.
