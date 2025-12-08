#ifndef DOM_CORE_FIXED_H
#define DOM_CORE_FIXED_H

#include "core_types.h"
#include "domino/dnumeric.h"

/* Compatibility shim: prefer domino/dnumeric.h for new code. */
typedef Q16_16 fix32;
typedef Q4_12  fix16;

#define FIX32_ONE   ((fix32)0x00010000)
#define FIX32_HALF  ((fix32)0x00008000)
#define FIX16_ONE   ((fix16)0x1000)

static fix32 fix32_from_int(i32 x)
{
    return dnum_from_int32((I32)x);
}

static i32 fix32_to_int(fix32 x)
{
    return dnum_to_int32((Q16_16)x);
}

static fix32 fix32_mul(fix32 a, fix32 b)
{
    return (fix32)(((I64)a * (I64)b) >> 16);
}

static fix32 fix32_div(fix32 a, fix32 b)
{
    return (fix32)(((I64)a << 16) / (I64)b);
}

static fix16 fix16_from_int(i16 x)
{
    return (fix16)((i16)(x << 12));
}

static i16 fix16_to_int(fix16 x)
{
    return (i16)(x >> 12);
}

#endif /* DOM_CORE_FIXED_H */
