# SPEC_ATMOSPHERE - Atmosphere Profiles (v1)

This spec defines deterministic atmosphere profiles and sampling outputs.

## 1. Parameters
Atmospheres are defined per body via a profile:
- `top_altitude_m` (Q48.16 meters)
- `segment_count` (>= 2)
- Segments (monotonic in altitude):
  - `altitude_m` (Q48.16 meters)
  - `density_q16` (Q16.16 kg/m^3)
  - `pressure_q16` (Q16.16 Pa)
  - `temperature_q16` (Q16.16 K)

The two-point profile is a degenerate case of the segment list.

## 2. Sampling rules
Given `altitude_m`:
- If `altitude_m < 0`, clamp to `0`.
- If `altitude_m >= top_altitude_m`:
  - `density_q16 = 0`
  - `pressure_q16 = 0`
  - `temperature_q16` may return the last segment temperature.
- Otherwise, locate the enclosing segment deterministically and interpolate:
  - Linear interpolation in fixed-point only.
  - No floating-point math, no exponentials/logs.

## 3. Validation and refusal
Profiles must be validated before use:
- Altitude breakpoints are strictly increasing.
- `top_altitude_m > 0`.
- `density_q16 >= 0`, `pressure_q16 >= 0`, `temperature_q16 > 0`.
- Missing or invalid profiles must refuse.

## 4. Determinism
- Segment selection uses deterministic binary search.
- Interpolation is fixed-point and bounded.
- Sampling is a pure function: same inputs, same outputs.

## 5. Related specs
- `docs/SPEC_MEDIA_FRAMEWORK.md`
- `docs/SPEC_REENTRY_THERMAL.md`
- `docs/SPEC_LANES_AND_BUBBLES.md`
