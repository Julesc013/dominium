Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: UPDATE/TRUST
Replacement Target: UPDATE-MODEL-1 operational hardening and trust-policy integration

# Update Model0 Retro Audit

## Inputs Audited

- `manifests/release_manifest.json` provides deterministic shipped-artifact identity and build metadata.
- DIST-1/DIST-2 bundle assembly and verification already define portable bundle layout and offline verification flow.
- LIB install manifests and install registry already provide deterministic install identity and discovery.
- COMPONENT-GRAPH-0 and DIST-REFINE-1 already define deterministic install-profile resolution.
- RELEASE-2 signing hooks are additive and detached; verification remains offline-capable without signatures.

## Current Hardcoded Assumptions

- Dist assembly still assumes a single bundle root per platform and channel.
- Existing installs assume one active release surface per install root.
- Setup rollback previously relied on backup ordering rather than an explicit install transaction log.
- Setup had no formal release-index surface for comparing current installed components against a target release.

## Required Additions

- A deterministic `release_index.json` colocated with the portable bundle.
- An `update_plan` model that compares current install state against a target release index through the component graph.
- A deterministic install transaction log for rollback selection.
- Setup commands for `update check`, `update plan`, `update apply`, and `rollback --to`.
