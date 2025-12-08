#ifndef DOMINO_DNUMERIC_H
#define DOMINO_DNUMERIC_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Fixed-point base types */

typedef int16_t Q4_12;    /* signed, range approx [-8 .. +7.9998], 4 integer, 12 frac */
typedef int32_t Q16_16;   /* signed, range approx [-32768 .. +32767.99998] */
typedef int64_t Q48_16;   /* signed, range approx ±1.4e14 with 1/65536 resolution */

/* Unsigned/signed integer aliases */

typedef uint8_t  U8;
typedef uint16_t U16;
typedef uint32_t U32;
typedef uint64_t U64;
typedef int8_t   I8;
typedef int16_t  I16;
typedef int32_t  I32;
typedef int64_t  I64;

/* Spatial units */
typedef Q16_16 PosUnit;      /* world tile units in Q16.16, 1.0 = 1 tile = 1 m */
typedef Q16_16 VelUnit;      /* tile units per second */
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

Q4_12  dnum_q16_to_q4(Q16_16 v);
Q16_16 dnum_q4_to_q16(Q4_12 v);

/* Angle helpers */
Turn dnum_turn_normalise_0_1(Turn t);
Turn dnum_turn_normalise_neg_pos_half(Turn t);
Turn dnum_turn_add(Turn a, Turn b);
Turn dnum_turn_sub(Turn a, Turn b);

/* Global fixed UPS (updates per second). This can later be made configurable per save. */
#define DOMINO_DEFAULT_UPS 30

/* dt in seconds as Q16.16: 1 / DOMINO_DEFAULT_UPS */
extern const SecondsQ16 g_domino_dt_s;

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DNUMERIC_H */
