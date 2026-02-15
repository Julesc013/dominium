Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/pack_manifest.schema.json` contribution fields and `docs/architecture/pack_system.md`.

# Pack Contribution Parser

## Purpose
Parse, validate, and deterministically order typed contributions declared by packs.

## Invariants
- Supported contribution types are explicit.
- Contribution IDs are globally unique across loaded packs.
- Contribution paths must exist inside owning pack directories.
- Output order is deterministic by `(contrib_type, id, pack_id)`.

## Cross-References
- `tools/xstack/pack_contrib/parser.py`
- `tools/xstack/pack_loader/constants.py`
- `docs/canon/glossary_v1.md`
