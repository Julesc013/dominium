# MOVE-BULK-00-PLAN Batch Summary

| Batch | Title | File Count | Ready For Gate | Validation Tier | Notes |
| --- | --- | ---: | --- | --- | --- |
| A | docs/evidence/archive-only | 309 | yes | Tier 0 | Low-risk first gate candidate. |
| B | templates/models/modding | 6 | no | Tier 1 | Needs content/tool/contract owner split. |
| C | content identity | 1230 | no | Tier 2 | Requires identity/hash/registry/pack validation. |
| D | authority/policy/spec/update | 50 | no | Tier 2 | Requires authority and contract owner confirmation. |
| E | active tools/modules | 33 | no | Tier 1 | Uses MOVE-FAMILY-00C-A as first subwave; shims needed. |
| F | runtime/core/net | 54 | no | Tier 3 | Runtime/source and protocol sensitive. |
| G | libraries/ABI | 108 | no | Tier 3 | Build/ABI sensitive; `libs/CMakeLists.txt` blocked until CMake plan. |
| H | final exception/shim closure | 0 | no | Tier 4 | Runs after prior batches and closes shims/exceptions. |

## Gate Strategy

`MOVE-BULK-00-GATE` should authorize only a safe subset. Batch A is the intended first bulk apply candidate. Other batches should be split into subwaves that skip unsafe items instead of blocking all visible cleanup.
