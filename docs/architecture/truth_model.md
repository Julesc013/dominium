Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to canon v1.0.0 and implemented by `engine/include/domino/truth_model_v1.h`.

# Truth Model v1 Contract

## Purpose
Define the minimal authoritative state envelope consumed by Observation Kernel derivation.

## Contract Surfaces
- `TruthModel` (authoritative): `engine/include/domino/truth_model_v1.h`
- `PerceivedModel` (derived): `client/observability/perceived_model_v1.h`
- `RenderModel` (presentation): `client/presentation/render_model_v1.h`

## Invariants
- Truth mutation is Process-only.
- PerceivedModel derivation must not mutate TruthModel.
- RenderModel must remain presentational and non-authoritative.
- Unknown/latent information must remain explicit (no fabricated certainty).
- Authority and lens constraints must be enforced before perception output is emitted.
- Renderer compile units must not include `domino/truth_model_v1.h`.

## TruthModel v1 Shape
- `schema_version`
- `universe_identity_ref`
- `universe_state_ref`
- `registry_refs`
  - `domain_registry_hash`
  - `law_registry_hash`
  - `experience_registry_hash`
  - `lens_registry_hash`
  - `astronomy_catalog_index_hash`
  - `ui_registry_hash`
- `simulation_tick`
- `universe_state.camera_assemblies[]` (lab camera assembly set)
- `universe_state.time_control` (rate/pause deterministic time control)
- `universe_state.process_log[]` (deterministic process hash anchors)

## Example
```json
{
  "schema_version": "1.0.0",
  "universe_identity_ref": "saves/save.lab.bootstrap/universe_identity.json",
  "universe_state_ref": "saves/save.lab.bootstrap/universe_state.json",
  "registry_refs": {
    "domain_registry_hash": "4f94...e9",
    "law_registry_hash": "9c80...3a",
    "experience_registry_hash": "9df1...9a",
    "lens_registry_hash": "eac1...7c",
    "astronomy_catalog_index_hash": "c59b...67",
    "ui_registry_hash": "305f...66"
  },
  "simulation_tick": 0
}
```

## TODO
- Add explicit schema files for TruthModel/PerceivedModel/RenderModel contracts if promoted to persisted artifacts.
- Add deterministic snapshot partitioning rules for multi-viewpoint observation caching.
- Add compatibility notes for future coordinate-frame metadata expansion.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/architecture/truth_perceived_render.md`
- `docs/contracts/lens_contract.md`
- `docs/architecture/observation_kernel.md`
