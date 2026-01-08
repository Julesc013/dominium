/*
FILE: include/domino/core/fixed_math.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / core/fixed_math
RESPONSIBILITY: Deterministic fixed-point trig/sqrt/div helpers for authoritative code.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; no floating-point math.
*/
#ifndef DOMINO_CORE_FIXED_MATH_H
#define DOMINO_CORE_FIXED_MATH_H

#include "domino/core/fixed.h"

#ifdef __cplusplus
extern "C" {
#endif

/* d_fixed_sin_turn
 * Purpose: Deterministic sine approximation for Turn values (Q16.16 turns).
 * Parameters:
 *   turn (in): Angle in turns (1.0 == full revolution).
 * Returns:
 *   Sine result in Q16.16.
 */
q16_16 d_fixed_sin_turn(q16_16 turn);

/* d_fixed_cos_turn
 * Purpose: Deterministic cosine approximation for Turn values (Q16.16 turns).
 * Parameters:
 *   turn (in): Angle in turns (1.0 == full revolution).
 * Returns:
 *   Cosine result in Q16.16.
 */
q16_16 d_fixed_cos_turn(q16_16 turn);

/* d_fixed_sqrt_q16_16
 * Purpose: Deterministic square-root for Q16.16 values.
 * Parameters:
 *   value (in): Q16.16 value (non-negative).
 * Returns:
 *   Q16.16 square-root; returns 0 for negative input.
 */
q16_16 d_fixed_sqrt_q16_16(q16_16 value);

/* d_fixed_div_q16_16
 * Purpose: Deterministic divide for Q16.16 values.
 * Parameters:
 *   numer/denom (in): Q16.16 numerator/denominator.
 * Returns:
 *   Q16.16 quotient; saturates on divide-by-zero and overflow.
 */
q16_16 d_fixed_div_q16_16(q16_16 numer, q16_16 denom);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_FIXED_MATH_H */
