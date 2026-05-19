Status: DERIVED
Last Reviewed: 2026-03-30
Stability: stable
Future Series: XI-6
Replacement Target: superseded by a later explicit ARCH-GRAPH-UPDATE freeze only

# XI-6 Final

## Frozen Graph

- architecture_graph.v1 hash: `f3c7b9cde7f94c3419497cdc922c46e6cd4b09837ba224a1106d55627d16bdb6`
- architecture_graph.v1 fingerprint: `f382a8cbb8f8d786d1c73fca7bd59de94391195b5c00e5b0b65dc3762343777b`
- module boundary rules hash: `6faa981b673a6761b9141d49ce39181cfcbc5542c534154e8421e80e07db106b`
- module boundary rules fingerprint: `b6b83b9ce81dec5c3fac34a6bd92855a78bb74025d9b2e0d8c77128e97d95fcb`

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

- `apps.client.local_server` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.server` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.setup.cli` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.workbench.module.inspection.inspector` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.workbench.module.tooling.editor` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.workbench.module.tooling.host.win32` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `apps.workbench.module.ui.editor` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `engine.time` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.astronomy.ephemeris` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.chemistry.degradation` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.electricity` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.electricity.fault` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.electricity.protection` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.embodiment.tools` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.fields` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.fluids.network` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.geology` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.interior` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.logic.compile` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.logic.debug` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.logic.element` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.logic.eval` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.logic.fault` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.logic.network` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.logic.protocol` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.logic.signal` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.logic.timing` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.logistics` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.materials` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.materials.maintenance` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.materials.performance` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.mechanics` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.mobility.maintenance` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.mobility.micro` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.mobility.network` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.mobility.traffic` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.mobility.travel` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.physics` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.physics.energy` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.processes` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.processes.capsules` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.processes.software` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.reality.ledger` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.signals.transport` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.signals.trust` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.systems` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.systems.certification` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.systems.macro` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.thermal.network` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `game.domain.universe` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.diagnostics` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.network.client` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.network.server` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.platform.win32.client` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.platform.win32.launcher` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.platform.win32.launcher.win32` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.platform.win32.server` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.platform.win32.setup` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.platform.win32.setup.win32` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.shell` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.shell.command` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.shell.ipc` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.shell.lifecycle` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.shell.logging` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.shell.server` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.shell.supervisor` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.storage` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.ui` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.ui.client` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `runtime.ui.client.interaction` / `runtime_tools_contamination` -> Lift shared helpers into runtime/lib surfaces or isolate the dependency behind declared compat/control/runtime APIs before Xi-7 tightening.
- `unknown.root` / `repo_root_support_surface` -> Classify repo-root support files into a declared repo/support domain in a later non-runtime cleanup pass.

## Validation


## Xi-7 Readiness

- ready for Xi-7 CI guard integration: `true`
