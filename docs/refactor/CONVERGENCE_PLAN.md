# Deterministic Convergence Plan

- Generated: 2026-03-26
- Duplicate clusters: 6065
- Actions: 27061
- Fingerprint: `a7043329ff0293679a76a72bd3b47521b69d348bdc0571e8004ec86c6b09ed2e`

## Resolution Summary

- Keep-only clusters: 1945
- Merge-required clusters: 2764
- Quarantine clusters: 1356
- Source-like impacted clusters: 3230

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
| `duplicate.cluster.0075f9b78b2784df` | `quarantine` | `src/meta_extensions_engine.py` | `src/meta/extensions/extensions_engine.py` | `HIGH` |
| `duplicate.cluster.0253285ae8918910` | `quarantine` | `tools/xstack/registry_compile/bundle_profile.py` | `tools/xstack/pack_loader/loader.py` | `HIGH` |
| `duplicate.cluster.0260b746b91f764a` | `quarantine` | `src/signals/transport/__init__.py` | `src/signals/__init__.py` | `HIGH` |
| `duplicate.cluster.0284e66e92fa82a8` | `quarantine` | `game/include/dominium/rules/governance/governance_system.h` | `game/include/dominium/rules/war/war_system.h` | `HIGH` |
| `duplicate.cluster.02a76b808e9594ff` | `quarantine` | `tools/ci/validate_earth_data.py` | `tools/ci/validate_milky_way_data.py` | `HIGH` |
| `duplicate.cluster.03a31072d7ac07a9` | `quarantine` | `src/system/templates/__init__.py` | `src/system/templates/template_compiler.py` | `HIGH` |
| `duplicate.cluster.03ab149d795288bb` | `quarantine` | `tools/distribution/profile_inspect.py` | `tools/distribution/compat_dry_run.py` | `HIGH` |
| `duplicate.cluster.03d1718b6abbb996` | `quarantine` | `tools/xstack/testx/tests/pack_compat0_testlib.py` | `tools/xstack/testx/tests/mod_policy0_testlib.py` | `HIGH` |
| `duplicate.cluster.0631a59ef2fe2be3` | `quarantine` | `src/meta/extensions/__init__.py` | `src/meta_extensions_engine.py` | `HIGH` |
| `duplicate.cluster.065d7d23b936c46c` | `quarantine` | `src/geo/overlay/__init__.py` | `src/geo/overlay/overlay_merge_engine.py` | `HIGH` |
| `duplicate.cluster.06f2c33736385885` | `quarantine` | `tools/worldgen/worldgen_lock_common.py` | `tools/mvp/baseline_universe_common.py` | `HIGH` |
| `duplicate.cluster.07162c47dda2a254` | `quarantine` | `src/worldgen/earth/water/__init__.py` | `src/worldgen/earth/water/water_view_engine.py` | `HIGH` |
| `duplicate.cluster.07c7e7b9365cb9dc` | `quarantine` | `src/lib/provides/__init__.py` | `src/lib/provides/provider_resolution.py` | `HIGH` |
| `duplicate.cluster.0873f4be504cdfe1` | `quarantine` | `tools/xstack/testx/tests/test_promotion_requires_replication.py` | `tools/xstack/testx/tests/test_proc9_candidate_promotion_requires_replication.py` | `HIGH` |
| `duplicate.cluster.0954e6658a2eb4fa` | `quarantine` | `src/worldgen/earth/climate_field_engine.py` | `src/worldgen/earth/tide_field_engine.py` | `HIGH` |
| `duplicate.cluster.0a8e71d06f3c5f95` | `quarantine` | `src/server/runtime/tick_loop.py` | `src/server/net/loopback_transport.py` | `HIGH` |
| `duplicate.cluster.0b7c5e4a1d1e1287` | `quarantine` | `src/lib/bundle/__init__.py` | `src/lib/bundle/bundle_manifest.py` | `HIGH` |
| `duplicate.cluster.0bb6cc4d90e796fb` | `quarantine` | `tests/ops/ops_manifest_tests.py` | `tests/ops/compatibility_tests.py` | `HIGH` |
| `duplicate.cluster.0bbdf1ddf2183c6a` | `quarantine` | `setup/packages/scripts/gen_launcher_ui_schema_v1.py` | `game/tests/tests/vectors/gen_tlv_vectors.py` | `HIGH` |
| `duplicate.cluster.0c2a75870f52b0dd` | `quarantine` | `src/worldgen/mw/mw_cell_generator.py` | `src/geo/worldgen/worldgen_engine.py` | `HIGH` |

## Enforcement Proposals

- `INV-NO-SRC-DIRECTORY`
- `INV-NO-DUPLICATE-SEMANTIC-ENGINE`
- `INV-ARCH-GRAPH-MATCH`
- `INV-NO-HARDCODED-BUNDLE-CONTENTS`

