Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Deterministic Math Policy (DET1)

This document defines the only allowed math for authoritative simulation paths.
All authoritative code MUST use deterministic fixed-point math only.
Violations are merge-blocking.

## Scope

Applies to authoritative directories:
- `engine/modules/core/**`
- `engine/modules/sim/**`
- `engine/modules/world/**`
- `game/core/**` (simulation paths only)
- `game/rules/**`
- `game/economy/**`

## Allowed APIs

Use these headers only:
- `domino/core/fixed.h`
- `domino/core/fixed_math.h`
- `domino/core/dom_deterministic_math.h`

Key primitives:
- Fixed-point types: `q4_12`, `q16_16`, `q24_8`, `q48_16`, `q32_32`
- Deterministic trig/sqrt/div: `d_fixed_sin_turn`, `d_fixed_cos_turn`,
  `d_fixed_sqrt_q16_16`, `d_fixed_div_q16_16`
- Canonical wrappers: `dom_sin_q16`, `dom_cos_q16`, `dom_sqrt_u64`,
  `dom_div_u64`, `dom_angle_normalize_q16`, `dom_round_q16`

## Forbidden APIs

The following are FORBIDDEN in authoritative code:
- Floating point types: `float`, `double`, `long double`
- Standard math headers: `<math.h>`, `<cmath>`
- Standard math functions: `sin`, `cos`, `tan`, `sqrt`, `pow`, `exp`, `log`
- SIMD float math or platform-specific float intrinsics

## Rounding rules (explicit)

- Fixed-point conversions to integer use arithmetic right shifts.
  This truncates toward negative infinity for negative values and toward zero
  for non-negative values.
- Fixed-point multiply/divide uses deterministic integer arithmetic with
  explicit saturation on overflow.
- `dom_round_q16` rounds to the nearest integer with half-away-from-zero
  behavior before clearing fractional bits.

## Error bounds (documented)

These bounds are deterministic and do not depend on platform:
- `d_fixed_sin_turn` and `d_fixed_cos_turn` use a 64-sample quarter-turn LUT
  with linear interpolation (1/256 turn segments). Absolute error is bounded
  by the interpolation resolution and is < 1e-4 of full scale.
- `d_fixed_sqrt_q16_16` returns the floor of the square root; error is < 1 LSB.
- `d_fixed_div_q16_16` truncates toward zero with saturation; error is < 1 LSB
  for non-zero denominators.

## Examples

Good (deterministic):
```
#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"

q16_16 angle = d_q16_16_from_int(1);
q16_16 s = d_fixed_sin_turn(angle);
```

Bad (non-deterministic):
```
#include <math.h>

float s = sinf(0.5f);
```

## Enforcement

CI enforces the following IDs:
- `DET-FLOAT-003` (float/math headers in authoritative dirs)
- `DET-G5` (no float/OS time/RNG)

Violations are merge-blocking.