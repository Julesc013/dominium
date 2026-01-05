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
- Hash algorithm: FNV-1a 64-bit (see `docs/SPEC_CONTAINER_TLV.md`).
- Hash input is the exact UTF-8 byte sequence (no normalization).

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_REFERENCE_FRAMES.md`
- `docs/SPEC_UNIVERSE_MODEL.md`
- `docs/SPEC_UNIVERSE_BUNDLE.md`
