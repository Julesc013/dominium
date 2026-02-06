Status: CANONICAL
Last Reviewed: 2026-02-06
Supersedes: none
Superseded By: none
STATUS: CANONICAL
OWNER: architecture
LAST_VERIFIED: 2026-02-06

# Build Identity Model (BUILD-ID-0)

This document is the canonical representation of PROMPT BUILD-ID-0.

Normative rules:
- BUILD-ID-0 activates in two stages (Stage 1: identity stamping; Stage 2: GBN governance).
- Per-product SemVer is manual; RepoX must not auto-bump.
- Build kinds are limited to dev, ci, beta, rc, release, hotfix.
- Channels are limited to stable, beta, nightly, pinned; channels are not build kinds.
- Version string format is <product>-<semver>+<build_kind>.<id>.
- Stage 1 requires build identity stamping in all executables and --build-info output including build_kind, BII, GBN=none, git_commit, and build_timestamp.
- Stage 2 enables dist-eligible builds (beta/rc/release/hotfix) with unique, centralized GBN allocated after build+tests.
- Dev/ci builds must use BII and must not contain a GBN.
- No dist artifact may exist without an artifact identity manifest that includes build kind, BII/GBN, and protocol/schema/API/ABI versions.
- Release policy is data-configured; forbidden branches must refuse GBN allocation.
- Update feeds and changelogs are RepoX-generated and must be consistent with artifact identities.

## Stage 2: Governance Activated (No Distribution)

Enabled:
- Dry-run release path exists and performs checks/tests.
- GBN allocator exists but remains disabled by default.
- Preview artifacts are generated for inspection only.
  - changelog.preview.md
  - artifact_identity.preview.json
  - release_plan.preview.json

Disabled:
- GBN allocation.
- Tagging, publishing, or feed updates.

Next step:
- Stage 3 enables allocator and distribution gates explicitly.
