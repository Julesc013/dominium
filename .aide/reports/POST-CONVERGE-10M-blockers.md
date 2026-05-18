# POST-CONVERGE-10M Blockers

Status: DERIVED
Last Reviewed: 2026-05-16

## Remaining Focused RepoX Blockers

- `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR`: 7 missing distribution wrapper/projection surfaces.
- `INV-NO-ADHOC-MAIN`: 5 missing AppShell-owned wrapper delegation surfaces.
- `INV-REFINEMENT-BUDGETED`: MW-4 stress fixture cannot evaluate because `game.domain.embodiment` reaches stale `embodiment.*` lazy imports.
- `INV-NO-BLOCKING-WORLDGEN-IN-UI`: MW-4 viewer stress fixture has the same stale lazy import blocker.
- `INV-TOOL-VERSION-MISMATCH`: CompatX and SecureX tool hashes remain stale.
- `INV-IDENTITY-FINGERPRINT`: identity fingerprint remains stale.
- `INV-REPOX-RULESET-MISSING`: two rule IDs remain unmapped.
- `INV-CANON-NO-SUPERSEDED`: `docs/architecture/DIRECTORY_CONTEXT.md` is still marked canonical and superseded.
- `INV-NO-EXTENSION-INTERPRETATION-WITHOUT-REGISTRY`: `capability_overrides` still lacks registry coverage.
- `INV-NO-RANDOM-RETRY-LOOPS-IN-WORLDGEN`: `while True` remains in `game/domain/worldgen/mw/mw_system_refiner_l2.py`.
- `INV-SHADOW-BOUNDED`: bounded shadow policy still flags `while ` in `game/domain/worldgen/earth/lighting/horizon_shadow_engine.py`.

## Known Warnings

- `INV-AUDITX-OUTPUT-STALE`: audit outputs may be stale.
- Four `WARN-GLOSSARY-TERM-CANON` warnings for `survival_mode` in audit evidence.

## Readiness

POST-CONVERGE-11 remains blocked because the remaining failures are not limited to product/projection proof blockers.
