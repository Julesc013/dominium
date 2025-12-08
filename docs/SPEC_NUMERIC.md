# Domino Numeric Policy

- Simulation is integer- and fixed-point-only; no floating point inside Domino deterministic code.
- Base fixed-point types live in `include/domino/dnumeric.h` and are implemented in `source/domino/dnumeric.c`.

## Fixed-point bases
- `Q4_12` — signed, 4 integer bits + 12 fractional, range ≈ [-8 .. +7.9998].
- `Q16_16` — signed, 16 integer bits + 16 fractional, range ≈ [-32768 .. +32767.99998].
- `Q48_16` — signed, large-range scalar with 16 fractional bits (≈ ±1.4e14).

## Semantic units
- `PosUnit`, `VelUnit`, `AccelUnit` (Q16.16): spatial units in tiles/metres.
- `Turn` (Q16.16): 1.0 == full revolution (2π).
- `MassKg`, `VolM3`, `EnergyJ`, `PowerW`, `ChargeC` (Q48.16): physical quantities.
- `TempK`, `PressurePa`, `DepthM` (Q16.16): thermal/pressure/depth.
- `FractionQ4_12` (Q4.12): small-range fractions/probabilities.
- `SimTick` (u64): global fixed-step tick index.
- `SecondsQ16` (Q16.16): durations; `g_domino_dt_s` holds the fixed dt for `DOMINO_DEFAULT_UPS` (30 Hz).

## Helpers and rules
- Integer-only helpers convert `int32` ↔ `Q16.16`, convert `Q16.16` ↔ `Q4.12`, and normalise `Turn` angles without floats.
- Angles wrap in [0,1) or [-0.5, +0.5) via `dnum_turn_normalise_*`.
- Deterministic time uses fixed dt: `g_domino_dt_s = (1 << 16) / DOMINO_DEFAULT_UPS`.
- No floating-point math in Domino core. Converting to/from floats is allowed only at UI/render/foreign API boundaries, never inside sim/state code.
