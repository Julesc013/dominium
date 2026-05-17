# MOVE-FAMILY-00-REFINE Blockers

Status: DERIVED
Last Reviewed: 2026-05-17

## Apply Blockers

| Blocker | Affected Material | Disposition |
| --- | --- | --- |
| Direct root imports | `governance/**`, `validation/**`, `meta/identity/**`, `meta/stability/**` | Requires temporary shim/import rewrite plan before move. |
| Heterogeneous semantic ownership | most `meta/**` | Preserve current until semantic owner split. |
| Product/runtime consumers | `performance/**` | Preserve current; target owner unresolved because `tools/performance` would be misleading. |
| Manifest contract missing | `ide/manifests/**` | Plan `contracts/projections` ownership and validator first. |
| No approved map | all target roots | No move map, salvage map, import rewrite, or exception update is approved by this task. |

## Warning-Only Conditions

- The refinement produced ownership destinations for the clearest groups, but no physical move is safe yet.
- Full CTest, full eval, CMake configure/build, product binaries, package generation, and release generation remain out of scope.
- Generated `.dominium.local/` and `.aide.local/` evidence remains ignored/local and must not be committed.

## Blocking For Direct Gate

`MOVE-FAMILY-00-GATE` remains not ready. The next task must be a narrower plan, starting with IDE manifest contract/projection ownership.
