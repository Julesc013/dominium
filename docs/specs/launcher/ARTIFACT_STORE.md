Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Artifact Store

Doc Version: 1

The artifact store provides offline-capable, content-addressed storage for verified payloads. Instance state refers to artifacts by hash; the store is treated as immutable once written.

## Principles

- Content addressing: artifacts are keyed by cryptographic hash (sha256).
- Verification before use: payload hash must match the expected hash.
- Deterministic layout: paths are derived solely from hash bytes.
- Read-only semantics in launcher core: core verifies and reads; instance operations must not mutate existing artifacts.

## Layout (Conceptual)

Under the state root:

- `artifacts/<algo>/<hash_hex>/artifact.tlv`
- `artifacts/<algo>/<hash_hex>/payload/payload.bin`

Where:
- `<algo>` is currently `sha256`.
- `<hash_hex>` is lowercase hex.

## Metadata Schema

`artifact.tlv` is a versioned TLV root containing:
- hash bytes
- payload size (optional but verified when present)
- content type (engine/game/pack/mod/runtime)
- timestamp and verification status
- optional source/provenance string

Unknown tags are skipped on read and preserved on re-encode.

See `docs/specs/SPEC_ARTIFACT_STORE.md`.

## Relationship to Instances

- Instance manifests include content entries that reference artifact hash bytes.
- Transaction verification produces `payload_refs.tlv` as an auditable snapshot of which artifacts are required for the instance state.
- Offline launch is possible when all referenced artifacts are present and verified.

See `docs/launcher/INSTANCE_MODEL.md` and `docs/launcher/SECURITY_AND_TRUST.md`.