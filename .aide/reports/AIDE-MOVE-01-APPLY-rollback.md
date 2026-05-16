# AIDE-MOVE-01-APPLY Rollback

## Reverse Move

If rollback is required before follow-up work, move the document back:

```powershell
git mv docs/architecture/IDE_PROJECTIONS.md ide/README.md
```

## Reverse Reference Rewrites

Reverse the six apply-phase edits:

- Restore `!/ide/README.md` in `.gitignore`.
- Change `docs/architecture/IDE_PROJECTIONS.md` back to `ide/README.md` in `scripts/verify_docs_sanity.py`.
- Change `/docs/architecture/IDE_PROJECTIONS.md` back to `/ide/README.md` in `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`.
- Restore the moved document heading to `# IDE Projections (/ide)`.
- Restore the moved document self-reference to `/ide/README.md`.
- Restore the prior AIDE selector wording in `tools/aide/select_move_wave.py`.

## Exception Metadata Rollback

No layout exception ledger update was applied. Only the `.gitignore` README exception was removed, and that is covered by the reverse reference rewrite list.

## Validation After Rollback

Run the same Tier 0 validation set used for apply:

- AIDE doctor/validate/test/selftest/tools/roots/repo/commit checks.
- Strict repo/root/distribution/component validators.
- Docs sanity, build target boundaries, UI shell purity, and ABI boundaries.
- `git diff --check`.
