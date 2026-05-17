# MOVE-BULK-00-GATE Deferred Batches

## Deferred

| Batch | Scope | Reason |
| --- | --- | --- |
| B | templates/models/modding | Needs content-vs-tool-vs-contract owner review and import/reference expansion. |
| C | content identity | Needs identity, manifest, registry, pack/profile/bundle, projection, and release validation gates. |
| D | authority/policy/spec/update | Needs authority/contract owner confirmation and no policy demotion proof. |
| E | active tools/modules | Needs shim/import migration gate, stale old-import static check, and affected validator proof. |
| F | runtime/core/control/net | Needs runtime ownership, build, focused CTest, product boot, and projection proof gate. |
| G | libraries/ABI | Needs ABI/build/UI-bind proof gate; `libs/CMakeLists.txt` remains a direct blocker. |

## Blocked Until Later

| Batch | Scope | Reason |
| --- | --- | --- |
| H | final exception/shim closure | Cannot run until prior batches are applied and proven. |

Deferred batches do not block Batch A because Batch A is isolated to docs/evidence/archive-only material and requires safe-subset apply behavior.
