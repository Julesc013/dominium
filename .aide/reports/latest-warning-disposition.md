# Latest Warning Disposition

## Accepted Warnings

- AIDE-MOVE-01-APPLY passes with warnings because local `origin/main` already matched the AIDE-GATE-02 commit rather than the older SHA expected by the prompt.
- Strict validators run through `python` emitted non-blocking `tomllib` fallback warnings while returning pass.
- Generated architecture registry and graph references to `ide/README.md` remain deferred review/regeneration items.
- Historical root-recycling and audit references to `ide/README.md` were preserved by design.
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
- AIDE-MOVE-01-APPLY moved the README, applied exactly six planned reference rewrites, and kept `ide/manifests/**` untouched.
