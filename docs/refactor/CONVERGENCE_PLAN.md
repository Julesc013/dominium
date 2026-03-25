# Deterministic Convergence Plan

- Generated: 2026-03-26
- Duplicate clusters: 6066
- Actions: 45511
- Fingerprint: `461f3e5e0b07a4c02fc044a6e4e4bbbbc22c904bca19e7e07772a9676128056a`

## Resolution Summary

- Keep-only clusters: 996
- Merge-required clusters: 3454
- Quarantine clusters: 1616
- Source-like impacted clusters: 3271

## Deterministic Selection Rules

1. Highest total score wins.
2. If scores tie, prefer the implementation inside the correct module root.
3. If still tied, prefer the implementation outside source-like directories.
4. If still tied, prefer the implementation used by more production targets.
5. If still tied, prefer the lexicographically earliest file path.

## Phase Boundary

- All `src/` implementations must be merge/rewire/deprecate first.
- `src/` removal is deferred until rewires complete and the convergence gate passes.

## Top Convergence Candidates

| Cluster | Resolution | Canonical | Top secondary | Risk |
| --- | --- | --- | --- | --- |
| `duplicate.cluster.001766fd09987b8e` | `quarantine` | `tests/invariant/test_optional_bundles_core_runtime.py` | `tests/invariant/test_survival_no_nondiegetic_lenses.py` | `HIGH` |
| `duplicate.cluster.0075f9b78b2784df` | `quarantine` | `src/meta_extensions_engine.py` | `src/meta/extensions/extensions_engine.py` | `HIGH` |
| `duplicate.cluster.01941b70f1147be9` | `quarantine` | `game/tests/tests/contract/dominium_perf_tests.cpp` | `game/tests/tests/contract/dominium_universe_bundle_tests.cpp` | `HIGH` |
| `duplicate.cluster.0253285ae8918910` | `quarantine` | `tools/xstack/registry_compile/bundle_profile.py` | `tools/xstack/pack_loader/loader.py` | `HIGH` |
| `duplicate.cluster.0260b746b91f764a` | `quarantine` | `src/signals/transport/__init__.py` | `src/signals/__init__.py` | `HIGH` |
| `duplicate.cluster.0284e66e92fa82a8` | `quarantine` | `game/include/dominium/rules/governance/governance_system.h` | `game/include/dominium/rules/war/war_system.h` | `HIGH` |
| `duplicate.cluster.02a76b808e9594ff` | `quarantine` | `tools/ci/validate_earth_data.py` | `tools/ci/validate_milky_way_data.py` | `HIGH` |
| `duplicate.cluster.03182cd42634b77c` | `quarantine` | `tools/xstack/testx/tests/test_no_direct_field_mutation.py` | `tools/xstack/testx/tests/test_cross_shard_field_blocked.py` | `HIGH` |
| `duplicate.cluster.03a31072d7ac07a9` | `quarantine` | `src/system/templates/__init__.py` | `src/system/templates/template_compiler.py` | `HIGH` |
| `duplicate.cluster.03ab149d795288bb` | `quarantine` | `tools/distribution/profile_inspect.py` | `tools/distribution/compat_dry_run.py` | `HIGH` |
| `duplicate.cluster.03d1718b6abbb996` | `quarantine` | `tools/xstack/testx/tests/pack_compat0_testlib.py` | `tools/xstack/testx/tests/mod_policy0_testlib.py` | `HIGH` |
| `duplicate.cluster.0631a59ef2fe2be3` | `quarantine` | `src/meta/extensions/__init__.py` | `src/meta_extensions_engine.py` | `HIGH` |
| `duplicate.cluster.065d7d23b936c46c` | `quarantine` | `src/geo/overlay/__init__.py` | `src/geo/overlay/overlay_merge_engine.py` | `HIGH` |
| `duplicate.cluster.06f2c33736385885` | `quarantine` | `tools/worldgen/worldgen_lock_common.py` | `tools/mvp/baseline_universe_common.py` | `HIGH` |
| `duplicate.cluster.0701ac0ca5fc5bc9` | `quarantine` | `tools/release/entrypoint_unify_common.py` | `tools/auditx/analyzers/e179_inline_response_curve_smell.py` | `HIGH` |
| `duplicate.cluster.07162c47dda2a254` | `quarantine` | `src/worldgen/earth/water/__init__.py` | `src/worldgen/earth/water/water_view_engine.py` | `HIGH` |
| `duplicate.cluster.07c7e7b9365cb9dc` | `quarantine` | `src/lib/provides/__init__.py` | `src/lib/provides/provider_resolution.py` | `HIGH` |
| `duplicate.cluster.07f923702826c909` | `quarantine` | `tests/share/share_bundle_tests.py` | `tests/ops/instance_manifest_tests.py` | `HIGH` |
| `duplicate.cluster.0873f4be504cdfe1` | `quarantine` | `tools/xstack/testx/tests/test_promotion_requires_replication.py` | `tools/xstack/testx/tests/test_proc9_candidate_promotion_requires_replication.py` | `HIGH` |
| `duplicate.cluster.0954e6658a2eb4fa` | `quarantine` | `src/worldgen/earth/climate_field_engine.py` | `src/worldgen/earth/tide_field_engine.py` | `HIGH` |

## Enforcement Proposals

- `INV-NO-SRC-DIRECTORY`
- `INV-NO-DUPLICATE-SEMANTIC-ENGINE`
- `INV-ARCH-GRAPH-MATCH`
- `INV-NO-HARDCODED-BUNDLE-CONTENTS`

