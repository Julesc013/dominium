Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-26
Scope: ED-4/4 epistemic invariance under LOD switching.

# LOD Epistemic Invariance Baseline

## Contracts Added

1. `dom.contract.epistemic_invariance_lod`
2. `dom.contract.no_precision_leak`
3. `dom.contract.no_hidden_state_leak`

Violation refusal code:

1. `refusal.ep.lod_information_gain`

## Enforcement Points

1. Observation Kernel redaction layer:
   - deterministic LOD redaction via `filter.lod_epistemic_redaction.v1`
   - precision envelope metadata stamping
2. Solver tier transitions:
   - `process.region_expand`
   - `process.region_collapse`
   - pre/post perceived snapshot invariance checks
3. Collapse memory continuity:
   - collapse path verifies lawful memory item IDs are preserved
4. RepoX hard checks:
   - `INV-SOLVER-TIER-REDACTION-REQUIRED`
   - `INV-NO-DIRECT-MICRO-TO-PERCEIVED`
5. AuditX semantic checks:
   - `E28_PRECISION_LEAK_ON_REFINEMENT_SMELL`
   - `E29_HIDDEN_STATE_LEAK_SMELL`

## Test Coverage

1. `test_macro_to_micro_no_precision_gain`
2. `test_precision_quantization_stable`
3. `test_hidden_inventory_not_exposed`
4. `test_memory_preserved_on_collapse`
5. `test_strict_mode_violation_refusal`

## Determinism Notes

1. All invariance checks are tick-driven and deterministic.
2. Strict-mode refusal path is deterministic and emits `refusal.ep.lod_information_gain`.
3. Redaction and channel ordering are stable under canonical sorted traversal.

## Known Limitations

1. Approximation deltas inside the same quantization envelope are allowed.
2. Current invariant checks focus on perceived channels/entities/camera precision and sensitive key-path tokens.
3. Future expansion can add stronger symbolic derivability checks for macro-to-micro transitions.

## Gate Execution (2026-02-26)

1. RepoX:
   - command: `tools/xstack/repox/check.py --repo-root . --profile STRICT`
   - result: PASS (`findings=0`)
2. AuditX:
   - command: `tools/auditx/auditx.py scan --repo-root . --format json`
   - result: COMPLETE (`findings_count=1516`, non-gating semantic scan)
3. TestX (LOD invariance suite):
   - command: `tools/xstack/testx_all.py --repo-root . --profile STRICT --cache off --subset testx.epistemics.lod_macro_to_micro_no_precision_gain,testx.epistemics.lod_precision_quantization_stable,testx.epistemics.lod_hidden_inventory_not_exposed,testx.epistemics.lod_memory_preserved_on_collapse,testx.epistemics.lod_strict_mode_violation_refusal`
   - result: PASS (`selected_tests=5`)
4. strict build:
   - configure: `cmake -S . -B out/build/vs2026/verify -G "Visual Studio 17 2022" -A x64` + verify-equivalent cache variables
   - build: `cmake --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game dominium_client`
   - result: PASS
5. `ui_bind --check`:
   - pre-step: `tools/xstack/registry_compile/registry_compile.py --repo-root . --out-dir build/registries --lockfile-out build/lockfile.json`
   - command: `tools/xstack/ui_bind.py --repo-root . --check`
   - result: PASS (`checked_windows=21`)

