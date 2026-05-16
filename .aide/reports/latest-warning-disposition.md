# Latest Warning Disposition

## Accepted Warnings

- AIDE-GATE-02 passes with warnings because the reference plan has high raw reference complexity from generated AIDE/repo evidence and historical audit artifacts.
- Generated architecture registry references must be reviewed or regenerated during the apply task rather than blindly hand-edited.
- The original AIDE-MOVE-01 plan remains draft, not-approved, and no-apply; the gate report authorizes only the next scoped apply task.
- `ide/manifests/**` remains deferred because it is authoritative machine-readable projection metadata.
- The required `python` validator commands emitted non-blocking `tomllib` fallback warnings while returning pass.
- Full eval, full CTest, CMake configure/build, package generation, release generation, and product binaries remain out of scope for this gate.

## Cleared Warnings

- AIDE-GATE-02 found no target path collision at `docs/architecture/IDE_PROJECTIONS.md`.
- Plan parsing confirmed `apply_allowed = false` and `approval_status = not_approved`.
- Strict validators and supplemental docs/build/UI/ABI checks passed.
