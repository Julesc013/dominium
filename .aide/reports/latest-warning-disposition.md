# Latest Warning Disposition

Current task: `CANON-SPINE-BOUNDARY-01`.

## Accepted Local/Generated Warnings

- `.aide.local/**`, `.dominium.local/**`, `.xstack_cache/**`, `build/`, `out/`, `dist/`, `artifacts/`, `tmp/`, and `__pycache__/` are local/generated roots and must not be tracked.
- Historical/archive and fixture paths may still contain legacy terms; new active source must follow the naming canon.

## Repaired Warnings

- Former bad-root tracked file count remains 0.
- Build boundary validation now passes with 0 active failures.
- `ALL_BUILD`, smoke CTest, and focused spine CTest pass.
- Active release Python and tracked generated/local roots were checked and found clean.

## Blocking Warnings

- Full CTest is not green yet.
- Feature work and DOE-00 remain blocked.

Next task: `POST-RESTRUCTURE-02 - Full Green Proof and Origin Sync`.
