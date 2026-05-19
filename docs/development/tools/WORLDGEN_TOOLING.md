Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Worldgen Tooling

Status: canonical.
Scope: offline worldgen tooling only.
Authority: canonical. Engine and game code MUST NOT depend on these tools.

## Binding rules
- Tools MUST be optional and offline-only.
- Tools MUST read packs and schemas without modifying them.
- Tools MUST emit derived data only under `build/cache/assets/`.
- Tool outputs MUST be disposable and reproducible.
- Engine output MUST remain authoritative over tool output.

## Tool inventory
- `tools/domain/worldgen/offline/refinement_runner.py`
- `tools/domain/worldgen/offline/validation_checker.py`
- `tools/domain/worldgen/offline/epistemic_simulator.py`
- `tools/domain/worldgen/offline/pack_diff_visualizer.py`

## Determinism
- Tool outputs MUST be deterministic for the same inputs.
- Any nondeterministic metadata MUST be omitted.
