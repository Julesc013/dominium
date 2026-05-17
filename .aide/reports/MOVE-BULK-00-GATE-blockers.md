# MOVE-BULK-00-GATE Blockers

## Global Blockers

None block this gate from authorizing Batch A.

## Batch-Specific Blockers

| Batch | Blocker | Disposition |
| --- | --- | --- |
| G | `libs/CMakeLists.txt` requires CMake/build-target rewiring before movement. | Blocks Batch G apply, not Batch A. |
| H | Final exception/shim closure requires prior batch apply/proof. | Blocks Batch H, not Batch A. |

## Deferred Risks

- Batch B has unresolved content/tool/contract ownership.
- Batch C has identity-sensitive content, pack, profile, bundle, registry, and projection semantics.
- Batch D has authority-sensitive policy/spec/security/update surfaces.
- Batch E contains active imports and planned temporary shims.
- Batch F contains runtime/source/protocol-sensitive surfaces.
- Batch G contains ABI/build-sensitive surfaces.

## Apply Authorization Status

`MOVE-BULK-01-APPLY-DOCS-ARCHIVE` may proceed for Batch A only. All other batches and all feature work remain unauthorized.
