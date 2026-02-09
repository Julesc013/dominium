Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# dompkg Manifest Contract

## Scope

This document defines the manifest payload carried inside the canonical TLV block
for `.dompkg` artifacts. The TLV payload is canonical; JSON files are exported
inspection views only.

## Required Fields

- `pkg_id`: reverse-DNS identifier
- `pkg_version`: semver string
- `pkg_format_version`: integer format revision
- `platform`: target platform id
- `arch`: target architecture id
- `abi`: ABI token
- `requires_capabilities`: explicit capability id list
- `provides_capabilities`: explicit capability id list
- `entitlements`: explicit entitlement id list
- `compression`: compression algorithm id
- `chunk_size_bytes`: integer chunk size, v1 = 1048576
- `file_exports`: deterministic file export table
- `content_hash`: package identity hash (signature excluded)
- `extensions`: open map

## Optional Fields

- `optional_capabilities`: explicit optional capability ids
- `signature`: signature metadata map
- `provenance_ref`: provenance pointer map

## File Export Record

Each entry in `file_exports` includes:

- `path`
- `size_bytes`
- `sha256`
- `mode`
- `chunk_count`

`path` is normalized to forward slashes and must not contain `..`.

## Refusal Codes

Manifest validation MUST use deterministic refusal codes:

- `refuse.manifest_missing_field`
- `refuse.manifest_invalid_type`
- `refuse.manifest_invalid_value`
- `refuse.capability_missing`
- `refuse.entitlement_missing`
- `refuse.path_invalid`

## Determinism

- Manifest key ordering is canonicalized before TLV encoding.
- Lists required for resolution (`requires_capabilities`, `provides_capabilities`,
  `entitlements`, `file_exports`) are serialized in deterministic order.
