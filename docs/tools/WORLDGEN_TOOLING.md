Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

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
- `tools/worldgen_offline/refinement_runner.py`
- `tools/worldgen_offline/validation_checker.py`
- `tools/worldgen_offline/epistemic_simulator.py`
- `tools/worldgen_offline/pack_diff_visualizer.py`

## Determinism
- Tool outputs MUST be deterministic for the same inputs.
- Any nondeterministic metadata MUST be omitted.