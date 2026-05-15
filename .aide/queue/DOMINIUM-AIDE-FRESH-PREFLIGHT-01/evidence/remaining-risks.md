# Remaining Risks

- Q50 must treat this as an upgrade dry-run because `.aide/` already exists.
- Target AIDE q24 lacks Q36-Q48 planning command families; Q50 must not assume target-local `install`, `upgrade`, `repair`, `rollback`, or `uninstall` commands exist before upgrade planning.
- The release bundle is valid locally but marked `local_preview_no_publish`, `DIRTY_SOURCE_RECORDED`, and `apply_mode_available: false`.
- Existing `.aide/memory/project-state.md` has stale source/local path references from the Q23 import.
- Existing Dominium gate systems are powerful and mutating; Q50 should not run them unless explicitly scoped.
- Changelog preview warns about malformed historical commits.
- Prior verifier warnings were tied to stale review packet references; Q50 should rerun `verify` after generating fresh Q50 evidence.
- Ignored local outputs are extensive and must remain uncommitted.
