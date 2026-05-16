# POST-CONVERGE-10F Blockers

## Blocking Issues

1. `inv_repox_rules` still fails.
   - Current local proof manifest: 1,844 failures and 5 warnings.
   - Dominant categories: `INV-DOC-STATUS-HEADER`, `INV-CANON-INDEX`, `INV-CANON-NO-HIST-REF`, `INV-OFFLINE-BOOT-OK`, `INV-REPOX-STRUCTURE`.
   - Classification: broad RepoX/canonical-evidence drift, not a safe narrow stale-path fix.

2. Canonical `ctest --preset verify` currently discovers zero tests.
   - The tuple verify build still discovers 493 tests.
   - Classification: canonical build-dir/test-discovery gap.

3. Full CTest remains unproven.
   - Focused unit gate passes.
   - Focused RepoX gate fails, so wall-time is not the only blocker.

## Non-Blocking Warnings

- RepoX generated proof/profile outputs are now written to ignored `.dominium.local/ctest/repox/`.
- Strict layout/root validators pass with known transitional-root exceptions.
- Validator commands emit non-blocking `tomllib` fallback warnings on the local Python version.

## Cleared

- `invariant_units_present` no longer fails.
- `unit.mass_energy.stub` is declared in `data/registries/unit_registry.json`.
- `unit.schema` false-positive path token is no longer treated as a unit ID.

## Authorization

No move, cleanup, product boot proof, package proof, release proof, or broad RepoX rewrite is authorized by this task.

Recommended next task: `POST-CONVERGE-10G - RepoX Rule and Canonical Evidence Drift Remediation`.
