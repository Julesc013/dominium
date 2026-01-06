/*
FILE: source/domino/core/dom_deterministic_math.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/dom_deterministic_math
RESPONSIBILITY: Canonical deterministic math wrappers for authoritative code paths.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: OS-specific headers; floating-point math.
*/
#ifndef DOMINO_CORE_DETERMINISTIC_MATH_H
#define DOMINO_CORE_DETERMINISTIC_MATH_H

#include "domino/core/fixed.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_sin_q16
 * Purpose: Deterministic sine for angle in turns (Q16.16, 1.0 == full turn).
 * Returns: Q16.16 sine value.
 */
q16_16 dom_sin_q16(q16_16 angle_turns);

/* dom_cos_q16
 * Purpose: Deterministic cosine for angle in turns (Q16.16, 1.0 == full turn).
 * Returns: Q16.16 cosine value.
 */
q16_16 dom_cos_q16(q16_16 angle_turns);

/* dom_sqrt_u64
 * Purpose: Deterministic integer sqrt (floor) for unsigned 64-bit inputs.
 * Returns: floor(sqrt(value)).
 */
u64 dom_sqrt_u64(u64 value);

/* dom_div_u64
 * Purpose: Deterministic unsigned divide with saturation on divide-by-zero.
 * Returns: num/den, or UINT64_MAX when den == 0.
 */
u64 dom_div_u64(u64 num, u64 den);

/* dom_angle_normalize_q16
 * Purpose: Normalize a Q16.16 turn angle into [0,1) turns.
 * Returns: normalized angle (Q16.16).
 */
q16_16 dom_angle_normalize_q16(q16_16 angle_turns);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_DETERMINISTIC_MATH_H */
