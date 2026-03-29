Status: DERIVED
Last Reviewed: 2026-03-30
Stability: stable
Future Series: XI-6
Replacement Target: superseded by a later explicit ARCH-GRAPH-UPDATE freeze only

# Module Boundaries v1

The canonical per-module rule matrix lives in `data/architecture/module_boundary_rules.v1.json`.

## Constitutional Alignment

- renderers and UI must not read TruthModel directly; Xi-6 forbids new truth-adjacent dependencies from frozen UI surfaces.
- applications must not mutate truth outside processes; Xi-6 freezes current app dependency surfaces and blocks undeclared new truth edges.
- tools must not contaminate runtime; Xi-6 blocks new runtime-to-tools dependencies outside explicit support bridges.

## Rule Summary

- module count: `1735`
- provisional module count: `22`
- boundary fingerprint: `e7bdd052713a81dafbf5a0397794af6e70929cfdea49f3308e5507db58ee0ee8`

## Provisional Allowances

- `apps.client.interaction` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.client.local_server` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.client.net` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.client.ui` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.server` -> `app_truth_surface, runtime_tools_contamination`; replacement plan: Move app-facing truth access behind declared process/runtime façades before the next boundary tightening pass.
- `apps.server.net` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.server.runtime` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `appshell.commands` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `appshell.supervisor` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `diag` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.tests.tests.contract` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `lib.export` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `lib.import` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `lib.instance` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `net.anti_cheat` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `net.policies` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `net.srz` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `packs.compat` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `universe` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `unknown.root` -> `repo_root_support_surface`; replacement plan: Classify repo-root support files into a declared repo/support domain in a later non-runtime cleanup pass.
- `validation` -> `runtime_tools_contamination`; replacement plan: Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.

## Canonical Artifact

- every frozen module rule records allowed dependencies, forbidden dependencies, allowed products, forbidden products, allowed platform adapters, stability class, and a per-rule deterministic fingerprint.
