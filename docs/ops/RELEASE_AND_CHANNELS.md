Status: DERIVED
Last Reviewed: 2026-02-06
Supersedes: none
Superseded By: none

# Release and Channels (BUILD-ID-0 Stage 2)

Scope: release governance and channel policy (dry-run only).

Build kinds
- dev, ci, beta, rc, release, hotfix
- Build kind is part of the build identity string.

Channels
- stable, beta, nightly, pinned
- Channels are distribution lanes, not build kinds.

Stage 2: dry-run release check
- repox release runs preflight + tests and generates preview artifacts only.
- No GBN allocation, no tags, no publishing, and no feed updates.
- Preview artifacts are emitted to build/:
  - changelog.preview.md
  - artifact_identity.preview.json
  - release_plan.preview.json

Release identity, build kinds, and global build numbers
are governed by docs/architecture/BUILD_IDENTITY_MODEL.md.
