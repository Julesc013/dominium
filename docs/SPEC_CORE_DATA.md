# SPEC_CORE_DATA — Core Data Canon

Status: draft  
Version: 1

## Purpose
Core data describes **what exists in the universe**, not how simulation runs.
It is the authoritative, human-authored source of canon for cosmos/system
anchors, mechanics profiles, and other baseline world data.

## Separation of concerns
- **Authoring formats** live in `/data/core` and are human-editable.
- **Runtime formats** are compiled, versioned TLV packs consumed by the game.
- Runtime code MUST NOT consume `/data/core` directly.

## Data lifecycle
1. `/data/core` authoring sources (JSON/TOML; Lua allowed only at compile time).
2. `coredata_compile` deterministic build step:
   - schema validation
   - canonical ordering
   - TLV emission
   - manifest + hash emission
3. Runtime loads only TLV packs and verifies identity bindings.

## Determinism rules
- Canonical ordering MUST be defined per schema (stable ID ascending).
- Hashing MUST be stable and deterministic across platforms.
- All compiled formats are versioned; readers must refuse unknown required
  schema versions unless a migration is defined.

## Sim-affecting vs non-sim-affecting data
**Sim-affecting** data:
- Influences authoritative decisions (e.g., travel duration, mechanics profile
  modifiers, hazard thresholds).
- MUST be explicitly tagged, versioned, and included in identity digests.

**Non-sim-affecting** data:
- Presentation-only data (names, lore, display positions, UI hints).
- MUST NOT influence authoritative simulation or identity digests.

## Refusal rules
Compile-time refusal:
- Schema validation failure
- Ambiguous IDs or unresolved references
- Duplicate canonical IDs

Runtime refusal:
- Missing required TLV chunks
- Schema/version mismatch without migration
- Identity digest mismatch

## Related specs
- `docs/SPEC_CORE_DATA_PIPELINE.md`
- `docs/SPEC_COSMO_CORE_DATA.md`
- `docs/SPEC_MECHANICS_PROFILES.md`
- `docs/SPEC_UNIVERSE_MODEL.md`
