/*
FILE: include/domino/dnumeric.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dnumeric
RESPONSIBILITY: Defines the public contract for `dnumeric` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DNUMERIC_H
#define DOMINO_DNUMERIC_H

#include "domino/baseline.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Fixed-point base types */

typedef int16_t Q4_12;    /* signed, range approx [-8 .. +7.9998], 4 integer, 12 frac */
typedef int32_t Q16_16;   /* signed, range approx [-32768 .. +32767.99998] */
typedef int64_t Q48_16;   /* signed, range approx ±1.4e14 with 1/65536 resolution */

/* Unsigned/signed integer aliases */

typedef uint8_t  U8;
/* U16: Public type used by `dnumeric`. */
typedef uint16_t U16;
/* U32: Public type used by `dnumeric`. */
typedef uint32_t U32;
/* U64: Public type used by `dnumeric`. */
typedef uint64_t U64;
/* I8: Public type used by `dnumeric`. */
typedef int8_t   I8;
/* I16: Public type used by `dnumeric`. */
typedef int16_t  I16;
/* I32: Public type used by `dnumeric`. */
typedef int32_t  I32;
/* I64: Public type used by `dnumeric`. */
typedef int64_t  I64;

/* Spatial units */
typedef Q16_16 PosUnit;      /* world tile units in Q16.16, 1.0 = 1 tile = 1 m */
typedef Q16_16 VelUnit;      /* tile units per second */
/* AccelUnit: Public type used by `dnumeric`. */
typedef Q16_16 AccelUnit;

/* Angle units: Turn = 1.0 == full circle (2π rad) */
typedef Q16_16 Turn;

/* Physical quantities */
typedef Q48_16 MassKg;       /* kg */
typedef Q48_16 VolM3;        /* m^3 */

typedef Q48_16 EnergyJ;      /* Joule */
typedef Q48_16 PowerW;       /* Watt */
typedef Q48_16 ChargeC;      /* Coulomb */

typedef Q16_16 TempK;        /* Kelvin */
typedef Q16_16 PressurePa;   /* Pascal */
typedef Q16_16 DepthM;       /* metres */

/* Fractions and probabilities */
typedef Q4_12  FractionQ4_12; /* typically 0..1 or small-range fractions */

/* Time */
typedef U64    SimTick;      /* global simulation tick index */

typedef Q16_16 SecondsQ16;   /* seconds in Q16.16 for dt, durations */

/* Conversions */

Q16_16 dnum_from_int32(I32 v);            /* v * 65536 */
I32     dnum_to_int32(Q16_16 v);          /* floor(v / 65536) */

/* Purpose: Q4 dnum q16 to.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
Q4_12  dnum_q16_to_q4(Q16_16 v);
/* Purpose: Q16 dnum q4 to.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
Q16_16 dnum_q4_to_q16(Q4_12 v);

/* Angle helpers */
Turn dnum_turn_normalise_0_1(Turn t);
/* Purpose: Half dnum turn normalise neg pos.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
Turn dnum_turn_normalise_neg_pos_half(Turn t);
/* Purpose: Add turn.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
Turn dnum_turn_add(Turn a, Turn b);
/* Purpose: Sub dnum turn.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
Turn dnum_turn_sub(Turn a, Turn b);

/* Global fixed UPS (updates per second). This can later be made configurable per save. */
#define DOMINO_DEFAULT_UPS 30

/* dt in seconds as Q16.16: 1 / DOMINO_DEFAULT_UPS */
extern const SecondsQ16 g_domino_dt_s;

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DNUMERIC_H */
