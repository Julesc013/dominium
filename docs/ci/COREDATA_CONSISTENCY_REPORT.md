# COREDATA_CONSISTENCY_REPORT

Status: draft  
Scope: Core data specs, compiler, validator, and pack format alignment.

## 1) Spec compliance matrix
- `docs/SPEC_CORE_DATA.md`: aligned with `coredata_compile` TLV stream format and
  implicit record schema version; sim vs non-sim hashing clarified.
- `docs/SPEC_COSMO_CORE_DATA.md`: aligned with TLV record format and implicit
  record schema version.
- `docs/SPEC_MECHANICS_PROFILES.md`: aligned with TLV record format and implicit
  record schema version.
- `docs/SPEC_CORE_DATA_PIPELINE.md`: output layout and manifest behavior match
  `coredata_compile` implementation.
- `docs/SPEC_CORE_DATA_VALIDATION.md`: validator behavior matches error taxonomy
  and refusal-first rules.
- Region type enums (`belt`, `cloud`, `heliosphere`) are aligned across spec,
  schema constants, compiler mapping, and validator acceptance.

## 2) Directory / paths
- Authoring root: `/data/core/**` present.
- Pack output layout: `repo/packs/<pack_id>/<version_8digit>/pack.tlv` and
  `pack_manifest.tlv` (matches compiler and spec).

## 3) Record type IDs and versions
- Record type IDs and tag definitions are implemented in
  `source/dominium/tools/coredata_compile/coredata_schema.h` and mirrored in
  the specs listed above.
- Record schema version is currently **implicit** in `pack.tlv` (constant `1`);
  the manifest records per-record version for auditing.

## 4) Sim-affecting vs non-sim
- `coredata_compile` content hash covers full record payloads (including
  non-sim fields such as display names and presentation positions).
- Runtime identity binding uses a **coredata sim digest** that hashes only
  sim-affecting fields and ignores presentation-only data.
- Game startup cross-checks the launcher handshake coredata sim hash against the
  runtime-loaded coredata sim digest (refusal on mismatch).

## 5) Refusal behavior
- `coredata_compile` refuses schema violations, ambiguous IDs, and unresolved
  references.
- `coredata_validate` enforces schema, reference, determinism, and policy rules.
- Runtime ingestion refuses missing required record types, duplicate IDs, and
  invalid references.

## 6) Determinism
- Determinism tests exist for `coredata_compile` (byte-identical output),
  `coredata_validate` (stable ordering/hashing), and coredata ingestion
  (stable graph hash and sim digest).

## 7) Resolutions applied in this pass
- Updated spec wording to reflect **TLV record streams** (not DTLV containers).
- Clarified **implicit record schema version** and manifest recording.
- Clarified separation between pack content hash and sim-only digest.
