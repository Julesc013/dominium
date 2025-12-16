/*
FILE: include/domino/baseline.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / baseline
RESPONSIBILITY: Defines the public contract for `baseline` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_BASELINE_H
#define DOMINO_BASELINE_H
/*
 * Baseline integer + boolean types for public headers.
 *
 * Requirements:
 * - C89/C++98 friendly (no system stdint/stdbool headers in public headers).
 * - Fixed-width integer typedefs compatible with common toolchains.
 */

/* Detect whether the build already provides fixed-width integer limits (stdint-like). */
#if defined(UINT8_MAX) && defined(UINT16_MAX) && defined(UINT32_MAX) && defined(UINT64_MAX) && \
    defined(INT8_MAX) && defined(INT16_MAX) && defined(INT32_MAX) && defined(INT64_MAX)
#define DOMINO_BASELINE_STDINT_PRESENT 1
#endif

/* Fixed-width integers (only if not already provided by stdint.h or equivalent) */
#if !defined(DOMINO_BASELINE_STDINT_PRESENT)
# if defined(_MSC_VER)
typedef signed __int8       int8_t;
/* uint8_t: Public type used by `baseline`. */
typedef unsigned __int8     uint8_t;
/* int16_t: Public type used by `baseline`. */
typedef signed __int16      int16_t;
/* uint16_t: Public type used by `baseline`. */
typedef unsigned __int16    uint16_t;
/* int32_t: Public type used by `baseline`. */
typedef signed __int32      int32_t;
/* uint32_t: Public type used by `baseline`. */
typedef unsigned __int32    uint32_t;
/* int64_t: Public type used by `baseline`. */
typedef signed __int64      int64_t;
/* uint64_t: Public type used by `baseline`. */
typedef unsigned __int64    uint64_t;
# elif defined(__clang__) || defined(__GNUC__)
/* int8_t: Public type used by `baseline`. */
typedef __INT8_TYPE__       int8_t;
/* uint8_t: Public type used by `baseline`. */
typedef __UINT8_TYPE__      uint8_t;
/* int16_t: Public type used by `baseline`. */
typedef __INT16_TYPE__      int16_t;
/* uint16_t: Public type used by `baseline`. */
typedef __UINT16_TYPE__     uint16_t;
/* int32_t: Public type used by `baseline`. */
typedef __INT32_TYPE__      int32_t;
/* uint32_t: Public type used by `baseline`. */
typedef __UINT32_TYPE__     uint32_t;
/* int64_t: Public type used by `baseline`. */
typedef __INT64_TYPE__      int64_t;
/* uint64_t: Public type used by `baseline`. */
typedef __UINT64_TYPE__     uint64_t;
# else
/* int8_t: Public type used by `baseline`. */
typedef signed char         int8_t;
/* uint8_t: Public type used by `baseline`. */
typedef unsigned char       uint8_t;
/* int16_t: Public type used by `baseline`. */
typedef signed short        int16_t;
/* uint16_t: Public type used by `baseline`. */
typedef unsigned short      uint16_t;
/* int32_t: Public type used by `baseline`. */
typedef signed long         int32_t;
/* uint32_t: Public type used by `baseline`. */
typedef unsigned long       uint32_t;
#  error "domino/baseline.h: no known 64-bit integer type for this toolchain"
# endif
#endif /* !defined(DOMINO_BASELINE_STDINT_PRESENT) */

/* Boolean for C89 */
#ifndef __cplusplus
# if !defined(__bool_true_false_are_defined)
/* bool: Public type used by `baseline`. */
typedef unsigned char bool;
#  define true  1
#  define false 0
#  define __bool_true_false_are_defined 1
# endif
#endif

#endif /* DOMINO_BASELINE_H */
