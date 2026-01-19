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
# SPEC_COSMO_CORE_DATA — Cosmos Core Data Schemas

Status: draft  
Version: 1

## Scope
This spec defines the core-data schemas for cosmos anchors and logical travel
edges. These schemas are compiled into TLV packs and are sim-affecting.

## COSMO_ANCHOR_NODE
Represents a logical anchor in the cosmos graph.

Fields:
- `id` (string, canonical, unique; sim-affecting)
- `kind` (SYSTEM | REGION; sim-affecting)
- `display_name` (string; non-sim)
- `system_class` (single | binary | cluster | remnant | exotic; sim-affecting)
- `region_type` (string/enum; sim-affecting for REGION only)
- `evidence_grade` (CONFIRMED | CANDIDATE | HISTORICAL | FICTIONALIZED; sim-affecting)
- `mechanics_profile_id` (string; sim-affecting)
- `anchor_weight` (u32; sim-affecting; used for procedural expansion)
- `tags` (string list; non-sim)
- `presentational_position` (optional; non-sim)

Rules:
- REGION nodes do not require fixed planet lists.
- SYSTEM nodes may define partial or procedural internal structure.
- CANDIDATE-grade anchors MUST NOT be required for progression.

## COSMO_EDGE
Represents a logical travel edge between anchors.

Fields:
- `src_id` (string; sim-affecting)
- `dst_id` (string; sim-affecting)
- `travel_duration_ticks` (u64; sim-affecting)
- `cost_profile_id` (string; sim-affecting)
- `hazard_profile_id` (string; optional, sim-affecting)
- `sim_affecting` (boolean; MUST be true)

Rules:
- Edges are directional unless explicitly declared bidirectional by authoring
  rules.
- Edges MUST be stored in deterministic order (by canonical ID).

## On-disk TLV record definitions (coredata pack)
Records are emitted as a TLV stream of records where each record is
`u32_le type_id` + `u32_le len` + payload bytes. Each record payload is a TLV
stream of fields (`u32_le tag` + `u32_le len` + payload bytes; little-endian).

Record type IDs (u32, stable):
- `COSMO_ANCHOR_NODE`: `0x00010001`
- `COSMO_EDGE`: `0x00010002`
- `COSMO_PROCEDURAL_RULES`: `0x00010003`

Record schema version: `1` (implicit in the pack; recorded in the manifest).

### COSMO_ANCHOR_NODE payload (TLV)
Tags:
- `1`: `id` (string, UTF-8)
- `2`: `id_hash` (u64_le; FNV-1a of `id`)
- `3`: `kind` (u32_le; enum)
- `4`: `display_name` (string; non-sim)
- `5`: `system_class` (u32_le; enum; SYSTEM only)
- `6`: `region_type` (u32_le; enum; REGION only)
- `7`: `evidence_grade` (u32_le; enum)
- `8`: `mechanics_profile_id` (string)
- `9`: `anchor_weight` (u32_le)
- `10`: `tag` (string, repeated; non-sim)
- `11`: `presentational_position` (bytes; 3x i32_le Q16.16, x/y/z; non-sim)

Enums:
- `kind`: 1=SYSTEM, 2=REGION
- `system_class`: 1=single, 2=binary, 3=cluster, 4=remnant, 5=exotic
- `region_type`: 1=nebula, 2=open_cluster, 3=globular_cluster, 4=galactic_core,
  5=belt, 6=cloud, 7=heliosphere
- `evidence_grade`: 1=confirmed, 2=candidate, 3=historical, 4=fictionalized

### COSMO_EDGE payload (TLV)
Tags:
- `1`: `src_id` (string)
- `2`: `src_id_hash` (u64_le)
- `3`: `dst_id` (string)
- `4`: `dst_id_hash` (u64_le)
- `5`: `travel_duration_ticks` (u64_le)
- `6`: `cost_profile_id` (string)
- `7`: `cost_profile_id_hash` (u64_le)
- `8`: `hazard_profile_id` (string, optional)
- `9`: `hazard_profile_id_hash` (u64_le, optional)

### COSMO_PROCEDURAL_RULES payload (TLV)
Tags:
- `1`: `systems_per_anchor_min` (u32_le)
- `2`: `systems_per_anchor_max` (u32_le)
- `3`: `red_dwarf_ratio_q16` (i32_le; Q16.16)
- `4`: `binary_ratio_q16` (i32_le; Q16.16)
- `5`: `exotic_ratio_q16` (i32_le; Q16.16)
- `6`: `cluster_density` (container, repeated; tags below)
- `7`: `metallicity_bias` (container, repeated; tags below)
- `8`: `hazard_frequency` (container, repeated; tags below)

Container tags (for 6/7/8):
- `1`: `region_type` (u32_le; enum above)
- `2`: `value_q16` (i32_le; Q16.16)

Procedural rule maps MUST cover the canonical procedural region types
(`nebula`, `open_cluster`, `globular_cluster`, `galactic_core`). Additional
region types (e.g., `belt`, `cloud`, `heliosphere`) are valid for anchors but
are not required in procedural maps.

## Related specs
- `docs/SPEC_CORE_DATA.md`
- `docs/SPEC_COSMO_LANE.md`
- `docs/SPEC_MECHANICS_PROFILES.md`
