# TOOLCHAIN-MATRIX-0 Retro Audit

## Scope

- ARCH-MATRIX-0 target matrix source: `data/registries/target_matrix_registry.json` (`exists=True`)
- PLATFORM-FORMALIZE capability source: `data/registries/platform_capability_registry.json` + `src/platform/platform_probe.py` (`exists=True`)
- RELEASE build identity source: `src/release/build_id_engine.py` (`source_revision_id`, `build_product_build_metadata`, `build_id_identity_from_input_payload`)
- Release manifest generation/verification source: `src/release/release_manifest_engine.py`

## Existing Gate Tooling

- `CONVERGENCE-GATE`: `tools/convergence/convergence_gate_common.py`
- `WORLDGEN-LOCK verify`: `tools/worldgen/worldgen_lock_common.py`
- `BASELINE-UNIVERSE verify`: `tools/mvp/baseline_universe_common.py`
- `GAMEPLAY verify`: `tools/mvp/gameplay_loop_common.py`
- `DISASTER suite`: `tools/mvp/disaster_suite_common.py`
- `release manifest verify`: `src/release/release_manifest_engine.py`

## Audit Notes

- Current committed mock dist root exists only for the Windows NT x86_64 lane: `True`
- Existing target policy is product support policy, not an environment run registry.
- Existing platform probes are host-observed and therefore not suitable as the sole Ω-9 env descriptor source for offline cross-boot comparison.
- Existing build-id rules already provide deterministic identity inputs; Ω-9 needs a canonical env/profile wrapper around them.
- Existing Ω verifiers already cover worldgen/universe/gameplay/disaster semantics; Ω-9 only needs to orchestrate and archive comparable outputs.
