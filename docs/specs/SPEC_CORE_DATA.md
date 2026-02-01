Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

SCHEMA:
- Canonical formats and migrations defined here live under `schema/`.

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
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

## On-disk TLV record definitions (coredata pack)
Records are emitted as a TLV stream of records where each record is
`u32_le type_id` + `u32_le len` + payload bytes. Each record payload is a TLV
stream of fields (`u32_le tag` + `u32_le len` + payload bytes; little-endian).

Record type IDs (u32, stable):
- `PACK_META`: `0x00000001`
- `ASTRO_BODY_CONSTANTS`: `0x00030001`

Chunk/record version: `1` (implicit in the pack; recorded in the manifest).

### ASTRO_BODY_CONSTANTS payload (TLV)
Tags:
- `1`: `id` (string, UTF-8)
- `2`: `id_hash` (u64_le; FNV-1a of `id`)
- `3`: `radius_m` (u64_le, optional)
- `4`: `mu_m3_s2_mantissa` (u64_le)
- `5`: `mu_m3_s2_exp10` (i32_le; base-10 exponent)
- `6`: `rotation_rate_rad_s_q16` (i32_le; Q16.16, optional)
- `7`: `atmosphere_profile_id` (string, optional)

### PACK_META payload (TLV)
Tags:
- `1`: `pack_schema_version` (u32_le)
- `2`: `pack_id` (string)
- `3`: `pack_version_num` (u32_le)
- `4`: `pack_version_str` (string, optional)
- `5`: `content_hash` (u64_le)

Notes:
- The pack `content_hash` covers full record payloads (including non-sim fields).
- The runtime computes a separate **coredata sim digest** that hashes only
  sim-affecting fields for identity binding.

## Related specs
- `docs/specs/SPEC_CORE_DATA_PIPELINE.md`
- `docs/specs/SPEC_COSMO_CORE_DATA.md`
- `docs/specs/SPEC_MECHANICS_PROFILES.md`
- `docs/specs/SPEC_UNIVERSE_MODEL.md`