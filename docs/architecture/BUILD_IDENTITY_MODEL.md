Status: CANONICAL
Last Reviewed: 2026-01-29
Supersedes: none
Superseded By: none
STATUS: CANONICAL
OWNER: architecture
LAST_VERIFIED: 2026-01-29

# Build Identity Model (BUILD-ID-0)

This document is the canonical representation of PROMPT BUILD-ID-0.

Normative rules:
- Per-product SemVer is manual; RepoX must not auto-bump.
- Build kinds are limited to dev, ci, beta, rc, release, hotfix.
- Channels are limited to stable, beta, nightly, pinned; channels are not build kinds.
- Dist-eligible builds (beta/rc/release/hotfix) require a unique, centralized GBN allocated after build+tests.
- Dev/ci builds must use BII and must not contain a GBN.
- No dist artifact may exist without an artifact identity manifest that includes build kind, BII/GBN, and protocol/schema/API/ABI versions.
- Release policy is data-configured; forbidden branches must refuse GBN allocation.
- Update feeds and changelogs are RepoX-generated and must be consistent with artifact identities.
