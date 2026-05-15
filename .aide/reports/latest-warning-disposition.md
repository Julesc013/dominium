# Latest Warning Disposition

## Accepted Warnings

- None for the AIDE root-recycling readiness surfaces covered by this pass.
- Full CTest, CMake configure/build, package generation, and product binaries
  remain out of scope for the root-recycling no-apply gate sequence.

## Cleared Warnings

- Strict repo layout and root allowlist validators now pass by excluding
  ignored, untracked local output roots from source-root enforcement.
- Strict UTF-8 JSON parsing now passes after removing a BOM from tracked AIDE
  queue evidence.
- AIDE doctor/controller/routing artifacts now pass.
- Repo validation now reports 0 unknown tracked file classifications.
- Token ledger, review-pack, verifier, outcome, and eval reports now pass with
  0 warnings.
- `git diff --check` now passes without whitespace or line-ending warnings.
