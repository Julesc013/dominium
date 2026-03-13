Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: RELEASE
Replacement Target: production signing and trust-chain policy after RELEASE-3

# Signing Policy

## Purpose

Signing is an additive release-integrity surface. It must not change build identity, manifest identity, or artifact hashes.

## Core Rules

- Signing is external to the build process.
- Signing material must not be embedded in the repository.
- Verification must work offline.
- CAP-NEG remains the authority for interoperability; signing never bypasses negotiation.

## Signature Placement

Preferred representation:

- detached signature file adjacent to the release manifest

Allowed representation for tooling and tests:

- inline `signatures` array on the release manifest

Canonical identity fields ignore signatures:

- `manifest_hash`
- `deterministic_fingerprint`

This ensures a signed and unsigned copy of the same release manifest share the same canonical manifest identity.

## Verification Outcomes

Verification reports one of:

- `verified`
- `signature_invalid`
- `signature_missing`

For mock-channel releases, `signature_missing` is non-fatal.

## Mock Hook Scheme

RELEASE-2 includes a deterministic mock signing hook for offline verification tests.
It is a reproducibility aid only and is not a trust or security mechanism.
