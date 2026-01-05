# SPEC_CALENDARS - Derived Time Labels

Calendars are derived, non-authoritative transforms from the tick timebase to
human-readable labels. They never mutate simulation state.

## 1. Inputs (authoritative)
- `tick_index` (u64)
- `ups` (u32)

## 2. Calendar kinds
- **Fixed-ratio**: constant day/year lengths defined as rational seconds.
- **Orbit-synced**: derives days/years from a body rotation/orbit period.
- **Hybrid**: fixed-ratio base with periodic corrections from an orbit source.

Only fixed-ratio calendars are implemented in v1; others return
`NOT_IMPLEMENTED`.

## 3. Determinism rules
- Integer-only math; no floating-point.
- No locale, timezone, or wall-clock dependencies.
- Output is a presentation label only (not canonical state).

## 4. Output fields
Fixed-ratio output uses integer fields:
- `year`
- `day_of_year`
- `hour`, `minute`, `second`
- Optional subsecond fields derived from tick remainder.

## Related specs
- `docs/SPEC_SPACETIME.md`
- `docs/SPEC_DETERMINISM.md`
