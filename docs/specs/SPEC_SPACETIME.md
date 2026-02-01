Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

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
# SPEC_SPACETIME - Canonical Time and Space

This spec defines the authoritative timebase and spatial units used by
deterministic systems. It is shared by Domino core and Dominium runtime code.

## 1. Authoritative timebase (tick-first)
- Canonical time is expressed as `(tick_index: u64, ups: u32)`.
- `ups` is ticks-per-second; default is 60 when unspecified.
- `tick_index` is monotonically increasing and authoritative.
- Wall-clock time is never authoritative and must not mutate sim state.
- Calendar labels (days/months/years) are derived for presentation only.

Deterministic conversions (integer-only):
- `ticks_to_us(ticks, ups) = floor((ticks * 1_000_000) / ups)`
- `ticks_to_ns(ticks, ups) = floor((ticks * 1_000_000_000) / ups)`
- Implementations must be overflow-safe and deterministic (reject or saturate
  using a documented policy).

## 2. Spatial units (meters, fixed-point)
- Canonical length unit is meters.
- Local positions are stored as fixed-point Q16.16 meters.
- No floating-point state is permitted in authoritative coordinates.

### 2.1 Segmented coordinates (large domains)
Large domains use segmented coordinates to avoid floats:
```
dom_posseg_q16 {
  i32 seg[3];   // coarse segment indices
  fix32 loc[3]; // Q16.16 meters, local within segment
}
```
- `seg_size_m` is an integer, domain-defined constant.
- `loc` is constrained to `[0 .. seg_size_m)` in each axis.
- Segment math must be integer-only and deterministic.

## 3. Stable ID hashing (string to u64)
- Stable IDs are derived from UTF-8 strings (case-sensitive).
- Hash algorithm: FNV-1a 64-bit (see `docs/specs/SPEC_CONTAINER_TLV.md`).
- Hash input is the exact UTF-8 byte sequence (no normalization).

## Related specs
- `docs/specs/SPEC_DETERMINISM.md`
- `docs/specs/SPEC_REFERENCE_FRAMES.md`
- `docs/specs/SPEC_UNIVERSE_MODEL.md`
- `docs/specs/SPEC_UNIVERSE_BUNDLE.md`