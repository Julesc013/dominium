/*
FILE: include/domino/core/fixed.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / core/fixed
RESPONSIBILITY: Defines the public contract for `fixed` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Domino fixed-point declarations (C89).
 * All arithmetic is integer-only; determinism across platforms is required.
 */
#ifndef DOMINO_CORE_FIXED_H
#define DOMINO_CORE_FIXED_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef i16 q4_12;   /* 4 integer bits, 12 fractional */
typedef i32 q16_16;  /* 16 integer bits, 16 fractional */
typedef i32 q24_8;   /* 24 integer bits, 8 fractional */
typedef i64 q48_16;  /* 48 integer bits, 16 fractional */
typedef i64 q32_32;  /* 32 integer bits, 32 fractional */

#define Q4_12_FRAC_BITS   12
#define Q16_16_FRAC_BITS  16
#define Q24_8_FRAC_BITS   8
#define Q48_16_FRAC_BITS  16
#define Q32_32_FRAC_BITS  32

/* Integer conversions (truncate toward zero on to_int). */
q4_12  d_q4_12_from_int(i32 value);
i32    d_q4_12_to_int(q4_12 value);

q16_16 d_q16_16_from_int(i32 value);
i32    d_q16_16_to_int(q16_16 value);

q24_8  d_q24_8_from_int(i32 value);
i32    d_q24_8_to_int(q24_8 value);

q48_16 d_q48_16_from_int(i64 value);
i64    d_q48_16_to_int(q48_16 value);

/* Debug/tooling conversions (not for core simulation). */
double d_q4_12_to_double(q4_12 value);     /* NOTE: tools/tests only */
q4_12  d_q4_12_from_double(double value);  /* NOTE: tools/tests only */

double d_q16_16_to_double(q16_16 value);     /* NOTE: tools/tests only */
q16_16 d_q16_16_from_double(double value);   /* NOTE: tools/tests only */

double d_q24_8_to_double(q24_8 value);     /* NOTE: tools/tests only */
q24_8  d_q24_8_from_double(double value);  /* NOTE: tools/tests only */

double d_q48_16_to_double(q48_16 value);     /* NOTE: tools/tests only */
q48_16 d_q48_16_from_double(double value);   /* NOTE: tools/tests only */

/* Basic arithmetic with saturation. */
q4_12  d_q4_12_add(q4_12 a, q4_12 b);
q4_12  d_q4_12_sub(q4_12 a, q4_12 b);
q4_12  d_q4_12_mul(q4_12 a, q4_12 b);
q4_12  d_q4_12_div(q4_12 a, q4_12 b);

q16_16 d_q16_16_add(q16_16 a, q16_16 b);
q16_16 d_q16_16_sub(q16_16 a, q16_16 b);
q16_16 d_q16_16_mul(q16_16 a, q16_16 b);
q16_16 d_q16_16_div(q16_16 a, q16_16 b);

q24_8  d_q24_8_add(q24_8 a, q24_8 b);
q24_8  d_q24_8_sub(q24_8 a, q24_8 b);
q24_8  d_q24_8_mul(q24_8 a, q24_8 b);
q24_8  d_q24_8_div(q24_8 a, q24_8 b);

q48_16 d_q48_16_add(q48_16 a, q48_16 b);
q48_16 d_q48_16_sub(q48_16 a, q48_16 b);
q48_16 d_q48_16_mul(q48_16 a, q48_16 b);
q48_16 d_q48_16_div(q48_16 a, q48_16 b);

/* Cross-format helpers. */
q16_16 d_q16_16_from_q4_12(q4_12 v);
q4_12  d_q4_12_from_q16_16(q16_16 v);

q24_8  d_q24_8_from_q16_16(q16_16 v);
q16_16 d_q16_16_from_q24_8(q24_8 v);

q48_16 d_q48_16_from_q16_16(q16_16 v);
q16_16 d_q16_16_from_q48_16(q48_16 v);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_FIXED_H */
