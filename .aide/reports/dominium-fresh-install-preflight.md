# Dominium Fresh Install Preflight

Status: `READY_FOR_Q50_WITH_WARNINGS`

Q49 confirmed this repository is `julesc013/dominium` at `C:/Inbox/Git Repos/dominium`, on branch `main`, start commit `752918d4f281aad12cdb6e892d39460172155e34`, with the branch ahead of `origin/main` by 6 commits before Q49. The starting worktree was clean.

Existing Dominium AIDE is present at q24 and passes core AIDE validation. It is not current with Q36-Q48 install/repair/upgrade/rollback/uninstall planning families, so Q50 should be an upgrade dry-run from the stable bundle, not a first install and not an apply.

The local AIDE release bundle was found at `C:/Inbox/Git Repos/aide/.aide/release/dist`; checksums and archive listings passed. The bundle is marked local preview/no-publish and `apply_mode_available: false`.

Primary evidence: `.aide/queue/DOMINIUM-AIDE-FRESH-PREFLIGHT-01/`.
