Status: DERIVED
Last Reviewed: 2026-03-30
Stability: stable
Future Series: XI-6
Replacement Target: superseded by a later explicit ARCH-GRAPH-UPDATE freeze only

# XI-6 Final

## Frozen Graph

- architecture_graph.v1 hash: `a63f8a3ec1a091b9bd0737f69a652ee0232e0b734f13bfbec0e5fcf36b68bb39`
- architecture_graph.v1 fingerprint: `ff1c955301dd733e8269f2ec3c5052de98c705a6a1d487990fb6d6e45e2da5ea`
- module boundary rules hash: `25fc5fa2b333caac5bc1568eb260c9132ce1b59b1bb83bad5184cd86fc3ea9df`
- module boundary rules fingerprint: `e7bdd052713a81dafbf5a0397794af6e70929cfdea49f3308e5507db58ee0ee8`

## Single Canonical Engines

- `cap_neg` -> `compat`
- `geo_overlay_merge` -> `geo.overlay`
- `geo_id_generation` -> `geo.index`
- `mw_refinement_scheduler` -> `worldgen.refinement`
- `trust_verifier` -> `security.trust`
- `pack_compat_verifier` -> `packs.compat`
- `update_resolver` -> `release`
- `virtual_paths_resolver` -> `appshell.paths`
- `time_anchor_engine` -> `engine.time`

## Provisional Allowances

- `apps.client.interaction` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.client.local_server` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.client.net` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.client.ui` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.server` / `app_truth_surface` -> Move app-facing truth access behind declared process/runtime façades before the next boundary tightening pass.
- `apps.server` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.server.net` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.server.runtime` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `appshell.commands` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `appshell.supervisor` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `diag` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.tests.tests.contract` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `lib.export` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `lib.import` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `lib.instance` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `net.anti_cheat` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `net.policies` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `net.srz` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `packs.compat` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `universe` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `unknown.root` / `repo_root_support_surface` -> Classify repo-root support files into a declared repo/support domain in a later non-runtime cleanup pass.
- `validation` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.

## Validation

- `build_verify`: `pass`
- `validate_strict`: `pass`
- `arch_audit_2`: `pass`
- `omega_1_worldgen_lock`: `pass`
- `omega_2_baseline_universe`: `pass`
- `omega_3_gameplay_loop`: `pass`
- `omega_4_disaster_suite`: `pass`
- `omega_5_ecosystem_verify`: `pass`
- `omega_6_update_sim`: `pass`
- `trust_strict_suite`: `pass`
- `targeted_xi6_tests`: `pass`

## Xi-7 Readiness

- ready for Xi-7 CI guard integration: `true`
