/* Domino core base types (C89 only).
 * This is the single source of truth for engine integer/boolean types.
 * Assumed widths:
 *  - u8/i8   : 8-bit
 *  - u16/i16 : 16-bit
 *  - u32/i32 : 32-bit
 *  - u64/i64 : 64-bit
 * Platforms that violate these assumptions are unsupported until a portability
 * layer is added.
 */
#ifndef DOMINO_CORE_TYPES_H
#define DOMINO_CORE_TYPES_H

#include "domino/baseline.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint8_t  u8;
typedef int8_t   i8;
typedef uint16_t u16;
typedef int16_t  i16;
typedef uint32_t u32;
typedef int32_t  i32;
typedef uint64_t u64;
typedef int64_t  i64;

typedef int d_bool;
#define D_TRUE  1
#define D_FALSE 0

#define D_MIN(a,b) (((a) < (b)) ? (a) : (b))
#define D_MAX(a,b) (((a) > (b)) ? (a) : (b))
#define D_CLAMP(x,lo,hi) (((x) < (lo)) ? (lo) : (((x) > (hi)) ? (hi) : (x)))

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_TYPES_H */
