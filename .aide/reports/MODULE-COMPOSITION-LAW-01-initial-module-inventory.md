# MODULE-COMPOSITION-LAW-01 Initial Module Inventory

Inventory is descriptive only. MODULE-COMPOSITION-LAW-01 defines module,
Workbench workspace, and app composition law and does not migrate current app,
Workbench, runtime, pack, or tool implementations.

## Scan Summary

- Files scanned per inventory: 17,896 tracked files.
- Module validator classified candidates: 1,208.
- Workbench validator classified candidates: 194.
- App validator classified candidates: 882.
- Inventory status: warning.

## Module Inventory Categories

- Workbench module candidates: 97.
- App composition candidates: 59.
- Runtime service candidates: 100.
- Command module candidates: 220.
- Command/view/document candidates: 80.
- Pack-provided module candidates: 631.
- Provider relationship files: 11.
- Capability relationship files: 10.

## Workbench Inventory Categories

- Workbench module candidates: 97.
- Runtime UI primitive candidates: 77.
- Pack workspace candidates: 20.

## App Inventory Categories

- App/product candidates: 156.
- Default pack candidates: 631.
- Provider preference candidates: 11.
- Release profile candidates: 84.

## Examples

- Workbench module candidates: `apps/workbench/module/domain/universe/ue_commands.cpp`, `apps/workbench/module/domain/universe/ue_queries.cpp`.
- App candidates: `apps/client/CMakeLists.txt`, `apps/server/server_boot.py`.
- Runtime UI primitives: `runtime/ui/service/d_ui.c`, `runtime/ui/view/d_view.c`.
- Pack-provided module candidates: `content/packs/tool/workspace.observer.truth/**`, `content/packs/tool/workspace.player.diegetic_default/**`.
- Command module candidates: `tools/validators/**`, `contracts/command/**`.

## Registration Decision

Registered now:

- `dominium.workbench.validation` as a planned provisional module in `contracts/module/module_surface.contract.toml`.
- Module, Workbench, and app schemas and validator surfaces in the public surface registry.
- Four provisional capabilities for module/workspace/app composition.
- Eight provisional diagnostics for module/workspace/app failures.

Deferred:

- Runtime module loader.
- Workbench shell/workspace manager implementation.
- App Composer implementation.
- Pack module activation and trust runtime.
- Migration of current app/workbench folders into full descriptors.

## Risks

- Existing app and Workbench code remains path-shaped and is not migrated.
- Some pack workspace files may later become pack-provided modules, but this
  task records them as candidates only.
- Module conformance proof is fixture-only until later implementation tasks.
