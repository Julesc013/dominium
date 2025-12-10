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

#ifdef __cplusplus
extern "C" {
#endif

typedef unsigned char  u8;
typedef signed   char  i8;
typedef unsigned short u16;
typedef signed   short i16;
typedef unsigned long  u32;
typedef signed   long  i32;

#if defined(_MSC_VER)
typedef unsigned __int64 u64;
typedef __int64          i64;
#else
typedef unsigned long long u64;
typedef long long          i64;
#endif

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
