# Latest Warning Disposition

Current task: `CANON-SPINE-NEW`.

## Accepted Local/Generated Warnings

- `.aide.local/**`, `.dominium.local/**`, `.xstack_cache/**`, `build/`, `out/`, `dist/`, `artifacts/`, `tmp/`, and `__pycache__/` are local/generated roots and must not be tracked.
- Historical/archive and fixture paths may still contain legacy terms; new active source must follow the naming canon.

## Repaired Warnings

- Former bad-root tracked file count remains 0.
- `tools/build/` is now treated as a source-owned tooling root while root `build/` remains generated/local.
- Root `dist/` and `artifacts/` are ignored as generated/local outputs.
- AIDE context snapshot/index/validation were refreshed after the generated-root policy fix.

## Blocking Warnings

- Build boundary validation still has active warnings and needs a dedicated repair pass.
- Full CTest is not green yet.
- Feature work and DOE-00 remain blocked.

Next task: `CANON-SPINE-BOUNDARY-01 - Repair Remaining Boundary Imports and Full Proof`.
