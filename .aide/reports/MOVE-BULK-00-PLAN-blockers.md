# MOVE-BULK-00-PLAN Blockers

## Blocking Issues

No blocker prevents this no-apply global plan from proceeding to `MOVE-BULK-00-GATE`.

One planned file action is explicitly blocked from direct application:

| Source | Batch | Reason |
| --- | --- | --- |
| `libs/CMakeLists.txt` | Batch G | CMake target rewiring is build/ABI sensitive and requires a build-focused gate before movement. |

## Non-Blocking Warnings

- Batch A is the only batch currently ready for gate as a low-risk docs/evidence/archive subset.
- Batches B-G require gate expansion before apply because they contain active imports, identity-sensitive content, authority-sensitive contracts, runtime/source surfaces, or build/ABI surfaces.
- Batch H is a proof/closure batch and cannot be run until prior batches have applied successfully.
- Broad path-reference counts are intentionally conservative `rg` counts and must be filtered by each batch gate.
- Historical/audit/generated references are expected to remain when classified as `never_historical`.
- Full CTest, full eval, CMake configure/build, product binaries, package/release generation, and projection regeneration are out of scope for this planning task.

## Authorization Status

No apply task is authorized by MOVE-BULK-00-PLAN. `MOVE-BULK-00-GATE` may inspect and select the first approved apply scope. Feature work remains unauthorized.
