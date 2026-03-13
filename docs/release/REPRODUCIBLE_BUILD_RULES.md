Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: RELEASE
Replacement Target: signed build and toolchain constitution after RELEASE-3

# Reproducible Build Rules

## Purpose

RELEASE-2 defines the deterministic build constraints required so identical inputs produce identical release identity surfaces.

## Build Inputs

The governed build identity surface may depend only on deterministic inputs:

- semantic contract registry hash
- source revision identifier, when available
- otherwise explicit build number
- compilation options fingerprint
- product identifier
- platform tag when the emitted binary surface must distinguish ABI or packaging targets

Compilation options fingerprint must cover:

- runtime family
- negotiated protocol surface
- feature capability projection
- build configuration such as `release` or `debug`

## Forbidden Inputs

The governed build identity surface must not depend on:

- wall-clock timestamps
- hostname or machine name
- absolute paths
- random environment state
- unordered traversal of build inputs

## Build Environment Requirements

Build and packaging tooling must preserve deterministic ordering for:

- compiled object enumeration
- archive member ordering
- manifest entry ordering
- resource embedding order

If toolchains cannot produce bitwise-identical binaries across hosts, they must still preserve:

- identical `build_id`
- identical endpoint descriptor hash
- identical release manifest hash
- identical pack, profile, lock, bundle, and manifest hashes

## Cross-Checks

Reproducibility verification compares:

- previous release manifest
- current artifacts
- live descriptor-emitted build metadata

Mismatch classes are:

- build ID mismatch
- artifact content hash mismatch
- descriptor hash mismatch
- manifest hash mismatch

## Non-Goals

RELEASE-2 does not require:

- online attestation services
- private key management in-repo
- bitwise identity across distinct toolchains
