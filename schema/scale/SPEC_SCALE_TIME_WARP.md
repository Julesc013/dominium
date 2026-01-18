--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Scale-aware warp constraints and interest binding rules.
SCHEMA:
- Time warp policy record format and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No per-domain clocks or drift.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_SCALE_TIME_WARP - Scale-Aware Time Warp (CIV4)

Status: draft  
Version: 1

## Purpose
Define deterministic time warp constraints per scale domain.

## TimeWarpPolicy schema
Required fields:
- policy_id
- domain_id
- min_warp
- max_warp
- interest_cap (max warp when interest is active)

Rules:
- All shards share ACT; warp only changes pacing.
- Interest can clamp warp but does not change ACT ordering.

## Determinism requirements
- Warp resolution is deterministic and integer-based.
- No wall-clock influence.

## Integration points
- Scale domains: `schema/scale/SPEC_SCALE_DOMAINS.md`
- Time warp core: `docs/SPEC_TIME_WARP.md`
- Interest sets: `docs/SPEC_INTEREST_SETS.md`

## Prohibitions
- No per-shard clocks.
- No warp decisions based on UI state alone.
