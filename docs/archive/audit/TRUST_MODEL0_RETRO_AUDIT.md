Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: TRUST
Replacement Target: updated trust audit after trust-root bundles, revocation, and signed pack artifacts are finalized

# TRUST-MODEL-0 Retro Audit

## Existing Surfaces

- RELEASE-2 already supports deterministic detached signature hooks for release manifests.
- MOD-POLICY already classifies packs as `trust.official_signed`, `trust.thirdparty_signed`, `trust.unsigned`, or `trust.local_dev`.
- PACK-COMPAT already checks `trust_level_id` consistency between `pack.compat.json` and `pack.trust.json`.
- Setup and DIST verification already perform offline hash verification, but trust-policy decisions are implicit.

## Implicit Decisions Found

- unsigned release manifests currently warn, regardless of environment
- pack verification currently relies on mod policy only and has no separate release/update trust policy
- update resolution has a placeholder trust-tier comparison but no release-index signature policy
- server config does not yet declare an explicit trust policy id

## Safest Integration Points

- release manifest verification remains the authoritative hash and detached-signature surface
- AppShell pack verifier adapter is the cleanest place to add policy enforcement without forking PACK-COMPAT
- Setup verify and update command flows already centralize offline verification decisions
- distribution verification already routes through release-manifest verification
