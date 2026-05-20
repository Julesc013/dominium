# Latest Warning Disposition

Current task: `PUBLIC-SURFACE-REGISTRY-01`.

## Accepted Local/Generated Warnings

- `.aide.local/**`, `.dominium.local/**`, `.xstack_cache/**`, `build/`, `out/`, `dist/`, `artifacts/`, `tmp/`, and `__pycache__/` remain local/generated roots and must not be tracked.
- Generated/archive material is not source truth unless a stronger contract explicitly promotes it.

## Conservative Classifications

- Engine, runtime, and game header surfaces are `provisional`, not stable API/ABI.
- Workbench module surfaces are `internal`.
- Package, pack, schema, registry, release, and update surfaces are mostly `provisional`.
- `archive/generated/aide` is `historical`.
- Public surface fixtures are `fixture`.
- Retired root-level `schema` and `schemas` are recorded as `retired`.

## Blocking Warnings

- Compatibility corpus is not populated by this task.
- Stable API/ABI proof remains assigned to `API-ABI-CANON-01`.
- Fast strict is green for this registry task: 30/30 commands, 299.828 seconds.
- Full CTest remains T4 full/release debt.
- Feature work and DOE-00 remain blocked until Foundation Lock closes.

Next task: `API-ABI-CANON-01`.
