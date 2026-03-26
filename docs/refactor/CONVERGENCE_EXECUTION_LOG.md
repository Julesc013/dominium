Status: DERIVED
Last Reviewed: 2026-03-26
Stability: provisional
Future Series: XI-5
Replacement Target: XI-4b bounded follow-up and XI-5 src removal execution

# XI-4 Convergence Execution Log

- Execution Mode: `conservative_preflight`
- Execution Boundary: `record canonical selections, quarantine ambiguous clusters, defer code-changing merge/rewire work outside the bounded XI-4 slice`
- Entry Count: `27061`
- Applied Records: `6065`
- Quarantined: `2415`
- Skipped: `18581`
- Quarantined Clusters: `1372`
- Deprecated Files Applied: `0`

## Gate Summary

- `build_strict` `cmake --build --preset verify --config Debug --target domino_engine dominium_game dominium_client` -> `pass`
- `testx_targeted` `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable,test_deprecated_files_not_in_default_build,test_canonical_paths_used_for_core_concepts_smoke,test_convergence_execution_log_deterministic` -> `pass`
- `validate_fast` `python tools/validation/tool_run_validation.py --repo-root . --profile FAST` -> `fail` note=`repo-global validation refusal: registry entries must declare stability in data/registries/toolchain_test_profile_registry.json`
- `validate_strict` `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT` -> `fail` note=`repo-global validation failure: ARCH-AUDIT disaster worktree cleanup under build/tmp/omega4_disaster_arch_audit failed`
- `omega_1_worldgen_lock` `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .` -> `pass`
- `omega_2_baseline_universe` `python tools/mvp/tool_verify_baseline_universe.py --repo-root .` -> `pass`
- `omega_3_gameplay_loop` `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .` -> `pass`
- `omega_4_disaster_suite` `python tools/mvp/tool_run_disaster_suite.py --repo-root .` -> `pass`

## Applied Canonical Selections

- `duplicate.cluster.001766fd09987b8e`
- `duplicate.cluster.00568dbb181a010c`
- `duplicate.cluster.0075f9b78b2784df`
- `duplicate.cluster.00957dc8238267e7`
- `duplicate.cluster.009faa1f4aabebd0`
- `duplicate.cluster.00a62f3a2d04bce2`
- `duplicate.cluster.00a8e4e5f99b95ea`
- `duplicate.cluster.00cde83970d1a878`
- `duplicate.cluster.00d330cd08e12e89`
- `duplicate.cluster.010a6c73373ffb28`
- `duplicate.cluster.011240a4d3a9c337`
- `duplicate.cluster.01125043ff4b4f2e`
- `duplicate.cluster.012f61d42c532f81`
- `duplicate.cluster.0173e9284a9e362e`
- `duplicate.cluster.0186ea13e4877d2a`
- `duplicate.cluster.018857820b64235e`
- `duplicate.cluster.01941b70f1147be9`
- `duplicate.cluster.01a56aa0bb6ca819`
- `duplicate.cluster.01ac553c372a0543`
- `duplicate.cluster.0215fe1a7e62a79d`

## Quarantined Clusters

- `duplicate.cluster.0075f9b78b2784df`
- `duplicate.cluster.0253285ae8918910`
- `duplicate.cluster.0260b746b91f764a`
- `duplicate.cluster.0284e66e92fa82a8`
- `duplicate.cluster.02a76b808e9594ff`
- `duplicate.cluster.03a31072d7ac07a9`
- `duplicate.cluster.03ab149d795288bb`
- `duplicate.cluster.03d1718b6abbb996`
- `duplicate.cluster.0631a59ef2fe2be3`
- `duplicate.cluster.065d7d23b936c46c`
- `duplicate.cluster.06f2c33736385885`
- `duplicate.cluster.07162c47dda2a254`
- `duplicate.cluster.07c7e7b9365cb9dc`
- `duplicate.cluster.0873f4be504cdfe1`
- `duplicate.cluster.0954e6658a2eb4fa`
- `duplicate.cluster.0a8e71d06f3c5f95`
- `duplicate.cluster.0b7c5e4a1d1e1287`
- `duplicate.cluster.0bb6cc4d90e796fb`
- `duplicate.cluster.0bbdf1ddf2183c6a`
- `duplicate.cluster.0c2a75870f52b0dd`
- ... see `docs/refactor/QUARANTINE_*.md` for the full packet set

## Deferred Clusters

- `duplicate.cluster.00957dc8238267e7`
- `duplicate.cluster.009faa1f4aabebd0`
- `duplicate.cluster.00a8e4e5f99b95ea`
- `duplicate.cluster.00cde83970d1a878`
- `duplicate.cluster.012f61d42c532f81`
- `duplicate.cluster.0173e9284a9e362e`
- `duplicate.cluster.0186ea13e4877d2a`
- `duplicate.cluster.018857820b64235e`
- `duplicate.cluster.01ac553c372a0543`
- `duplicate.cluster.023b28d207758467`
- `duplicate.cluster.0284e66e92fa82a8`
- `duplicate.cluster.035d65e2a0dca8fc`
- `duplicate.cluster.03620c5caaa74a60`
- `duplicate.cluster.036e7a65ad2b9e5f`
- `duplicate.cluster.03ab149d795288bb`
- `duplicate.cluster.043680824e715686`
- `duplicate.cluster.05838775fc7c2d87`
- `duplicate.cluster.05964fb02c313471`
- `duplicate.cluster.066845c9155f85c7`
- `duplicate.cluster.06a9effbf03b0573`
- ... see `data/refactor/convergence_execution_log.json` for the full deferred set

