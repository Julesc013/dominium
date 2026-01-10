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

## Related specs
- `docs/SPEC_CORE_DATA.md`
- `docs/SPEC_COSMO_LANE.md`
- `docs/SPEC_MECHANICS_PROFILES.md`
