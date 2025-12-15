#ifndef DOMINO_BASELINE_H
#define DOMINO_BASELINE_H
/*
 * Baseline integer + boolean types for public headers.
 *
 * Requirements:
 * - C89/C++98 friendly (no system stdint/stdbool headers in public headers).
 * - Fixed-width integer typedefs compatible with common toolchains.
 */

#if defined(UINT8_MAX) && defined(UINT16_MAX) && defined(UINT32_MAX) && defined(UINT64_MAX) && \
    defined(INT8_MAX) && defined(INT16_MAX) && defined(INT32_MAX) && defined(INT64_MAX)
#define DOMINO_BASELINE_STDINT_PRESENT 1
#endif

/* Fixed-width integers (only if not already provided by stdint.h or equivalent) */
#if !defined(DOMINO_BASELINE_STDINT_PRESENT)
# if defined(_MSC_VER)
typedef signed __int8       int8_t;
typedef unsigned __int8     uint8_t;
typedef signed __int16      int16_t;
typedef unsigned __int16    uint16_t;
typedef signed __int32      int32_t;
typedef unsigned __int32    uint32_t;
typedef signed __int64      int64_t;
typedef unsigned __int64    uint64_t;
# elif defined(__clang__) || defined(__GNUC__)
typedef __INT8_TYPE__       int8_t;
typedef __UINT8_TYPE__      uint8_t;
typedef __INT16_TYPE__      int16_t;
typedef __UINT16_TYPE__     uint16_t;
typedef __INT32_TYPE__      int32_t;
typedef __UINT32_TYPE__     uint32_t;
typedef __INT64_TYPE__      int64_t;
typedef __UINT64_TYPE__     uint64_t;
# else
typedef signed char         int8_t;
typedef unsigned char       uint8_t;
typedef signed short        int16_t;
typedef unsigned short      uint16_t;
typedef signed long         int32_t;
typedef unsigned long       uint32_t;
#  error "domino/baseline.h: no known 64-bit integer type for this toolchain"
# endif
#endif /* !defined(DOMINO_BASELINE_STDINT_PRESENT) */

/* Boolean for C89 */
#ifndef __cplusplus
# if !defined(__bool_true_false_are_defined)
typedef unsigned char bool;
#  define true  1
#  define false 0
#  define __bool_true_false_are_defined 1
# endif
#endif

#endif /* DOMINO_BASELINE_H */
