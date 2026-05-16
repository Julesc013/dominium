# Latest Warning Disposition

## Accepted Warnings

- AIDE-MOVE-02-REFINE passes with warnings because no second low-risk candidate survived the stricter single-file/docs/evidence filter.
- `templates/adapter_template.md` and `templates/domain_contract_template.md` are near-misses, but both are template scaffolds with conversion fates and protected spec/XStack references.
- AIDE-MOVE-02-PLAN passes with warnings because no second low-risk docs-only/evidence-only candidate was selected.
- Remaining `ide/` material is machine-readable projection metadata and remains deferred.
- `performance/`, `validation`, `governance`, and `meta` contain active Python/tooling or high-reference surfaces that require refinement before a move plan.
- AIDE-GATE-03 passes with warnings because remaining old-path references are historical, audit, generated review, or root-recycling evidence.
- AIDE-GATE-03 accepts that `ide/` remains transitional because `ide/manifests/**` remains deferred.
- AIDE-GATE-03 accepts local `main` equal to `origin/main` at the AIDE-MOVE-01-APPLY commit as a valid synced state.
- Strict validators temporarily rewrote generated migration metadata headers during AIDE-GATE-03; those timestamp/SHA-only side effects were removed because the gate cannot write `tools/migration/**`.
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
- AIDE-GATE-03 verified the post-move state and authorizes only AIDE-MOVE-02 planning.
