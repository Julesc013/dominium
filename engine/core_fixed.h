#ifndef DOM_CORE_FIXED_H
#define DOM_CORE_FIXED_H

#include "core_types.h"

typedef i32 fix32;
typedef i16 fix16;

#define FIX32_ONE   ((fix32)0x00010000)
#define FIX32_HALF  ((fix32)0x00008000)
#define FIX16_ONE   ((fix16)0x1000)

static fix32 fix32_from_int(i32 x)
{
    return (fix32)((i64)x << 16);
}

static i32 fix32_to_int(fix32 x)
{
    return (i32)(x >> 16);
}

static fix32 fix32_mul(fix32 a, fix32 b)
{
    return (fix32)(((i64)a * (i64)b) >> 16);
}

static fix32 fix32_div(fix32 a, fix32 b)
{
    return (fix32)(((i64)a << 16) / (i64)b);
}

static fix16 fix16_from_int(i16 x)
{
    return (fix16)(x << 12);
}

static i16 fix16_to_int(fix16 x)
{
    return (i16)(x >> 12);
}

#endif /* DOM_CORE_FIXED_H */
