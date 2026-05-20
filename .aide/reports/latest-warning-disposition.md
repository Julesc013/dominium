# Latest Warning Disposition

Current task: `DEPENDENCY-DIRECTION-01`.

## Accepted Local/Generated Warnings

- `.aide.local/**`, `.dominium.local/**`, `.xstack_cache/**`, `build/`, `out/`,
  `dist/`, `artifacts/`, `tmp/`, and `__pycache__/` remain local/generated roots
  and must not be tracked.
- Generated/archive material is not source truth unless a stronger contract
  explicitly promotes it.

## Dependency Direction Warnings And Debt

- Dependency-direction validator strict result: FAIL on existing debt.
- High-confidence violations: 358.
- Warnings: 38.
- Active exceptions: 0.
- Broad exceptions: 0.

These findings are not accepted as clean. They are recorded as current debt. A
later bounded task must remove dependencies, move code to the correct owner, add
proper contracts/service boundaries, or add precise temporary exceptions with
owner and retirement task.

## ABI Warnings

- `tools/validators/abi/check_public_headers.py --repo-root . --strict` reports
  PASS with 2,851 warnings and 0 high-confidence violations.
- These warnings block stable or frozen ABI promotion until explicitly resolved
  or excepted.

## Blocking Warnings

- Full CTest remains T4 full/release debt.
- Feature work and DOE-00 remain blocked until Foundation Lock closes.

Next task: `COMMAND-SURFACE-01`.
