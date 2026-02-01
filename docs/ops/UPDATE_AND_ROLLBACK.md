Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Update and Rollback (DEV-OPS-0)

Scope: update channels, feeds, and rollback behavior.

Channels
- stable: release + hotfix
- beta: beta + rc
- nightly: CI-only, non-distributed unless explicitly configured
- pinned: explicit GBN selection

Update flow
1) Launcher/Setup reads update feed for selected channel.
2) User reviews changelog + compatibility report.
3) User confirms update.
4) Setup applies update transactionally.

Rollback flow
1) User selects previous known-good artifact.
2) Setup performs transactional rollback.
3) Launcher verifies compat_report and refuses if incompatible.

Rules
- No automatic downloads.
- No silent updates.
- Compatibility mismatches are refusals.

Artifacts
- Update feeds live under updates/<channel>.json
- Rollback pointers are included in each feed entry.
