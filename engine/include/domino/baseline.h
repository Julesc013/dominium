/*
FILE: include/domino/baseline.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / baseline
RESPONSIBILITY: Defines the public contract for `baseline` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_BASELINE_H
#define DOMINO_BASELINE_H
/* Purpose: Provide fixed-width integer typedefs and a C89 boolean for baseline-visible public headers.
 *
 * This header intentionally avoids including `<stdint.h>` / `<stdbool.h>` so that
 * baseline-visible headers remain valid C89 (and usable from C++98 TUs).
 *
 * Preconditions:
 * - None. If the translation unit/toolchain already defines `INT*_MAX` and `UINT*_MAX`
 *   limit macros, `DOMINO_BASELINE_STDINT_PRESENT` is set and this header will not
 *   redeclare the fixed-width integer typedef names.
 *
 * Postconditions:
 * - The typedef names `int8_t`/`uint8_t` ... `int64_t`/`uint64_t` are available
 *   (either from the toolchain or from the fallbacks below).
 * - In C builds (not C++), `bool`/`true`/`false` are provided when not already defined.
 *
 * Side effects:
 * - May define `DOMINO_BASELINE_STDINT_PRESENT` as a probe result.
 * - In C, may define `__bool_true_false_are_defined` plus `bool`/`true`/`false`.
 *
 * Determinism: N/A (compile-time types/macros only).
 * Thread-safety: N/A.
 *
 * See also:
 * - `docs/specs/SPEC_LANGUAGE_BASELINES.md` (baseline visibility rules)
 * - `docs/specs/SPEC_CORE.md#Types and ids` (engine base types)
 */

/* Detect whether the build already provides fixed-width integer limits (stdint-like). */
#if defined(UINT8_MAX) && defined(UINT16_MAX) && defined(UINT32_MAX) && defined(UINT64_MAX) && \
    defined(INT8_MAX) && defined(INT16_MAX) && defined(INT32_MAX) && defined(INT64_MAX)
/* Purpose: Probe result indicating stdint-like limit macros are already available. */
#define DOMINO_BASELINE_STDINT_PRESENT 1
#endif

/* Fixed-width integers (only if not already provided by stdint.h or equivalent) */
#if !defined(DOMINO_BASELINE_STDINT_PRESENT)
# if defined(_MSC_VER)
/* Purpose: Fixed-width signed 8-bit integer type (C99 `stdint.h` name). */
typedef signed __int8       int8_t;
/* Purpose: Fixed-width unsigned 8-bit integer type (C99 `stdint.h` name). */
typedef unsigned __int8     uint8_t;
/* Purpose: Fixed-width signed 16-bit integer type (C99 `stdint.h` name). */
typedef signed __int16      int16_t;
/* Purpose: Fixed-width unsigned 16-bit integer type (C99 `stdint.h` name). */
typedef unsigned __int16    uint16_t;
/* Purpose: Fixed-width signed 32-bit integer type (C99 `stdint.h` name). */
typedef signed __int32      int32_t;
/* Purpose: Fixed-width unsigned 32-bit integer type (C99 `stdint.h` name). */
typedef unsigned __int32    uint32_t;
/* Purpose: Fixed-width signed 64-bit integer type (C99 `stdint.h` name). */
typedef signed __int64      int64_t;
/* Purpose: Fixed-width unsigned 64-bit integer type (C99 `stdint.h` name). */
typedef unsigned __int64    uint64_t;
# elif defined(__clang__) || defined(__GNUC__)
/* Purpose: Fixed-width signed 8-bit integer type (C99 `stdint.h` name). */
typedef __INT8_TYPE__       int8_t;
/* Purpose: Fixed-width unsigned 8-bit integer type (C99 `stdint.h` name). */
typedef __UINT8_TYPE__      uint8_t;
/* Purpose: Fixed-width signed 16-bit integer type (C99 `stdint.h` name). */
typedef __INT16_TYPE__      int16_t;
/* Purpose: Fixed-width unsigned 16-bit integer type (C99 `stdint.h` name). */
typedef __UINT16_TYPE__     uint16_t;
/* Purpose: Fixed-width signed 32-bit integer type (C99 `stdint.h` name). */
typedef __INT32_TYPE__      int32_t;
/* Purpose: Fixed-width unsigned 32-bit integer type (C99 `stdint.h` name). */
typedef __UINT32_TYPE__     uint32_t;
/* Purpose: Fixed-width signed 64-bit integer type (C99 `stdint.h` name). */
typedef __INT64_TYPE__      int64_t;
/* Purpose: Fixed-width unsigned 64-bit integer type (C99 `stdint.h` name). */
typedef __UINT64_TYPE__     uint64_t;
# else
/* Purpose: Fixed-width signed 8-bit integer type (C99 `stdint.h` name). */
typedef signed char         int8_t;
/* Purpose: Fixed-width unsigned 8-bit integer type (C99 `stdint.h` name). */
typedef unsigned char       uint8_t;
/* Purpose: Fixed-width signed 16-bit integer type (C99 `stdint.h` name). */
typedef signed short        int16_t;
/* Purpose: Fixed-width unsigned 16-bit integer type (C99 `stdint.h` name). */
typedef unsigned short      uint16_t;
/* Purpose: Fixed-width signed 32-bit integer type (C99 `stdint.h` name). */
typedef signed long         int32_t;
/* Purpose: Fixed-width unsigned 32-bit integer type (C99 `stdint.h` name). */
typedef unsigned long       uint32_t;
#  error "domino/baseline.h: no known 64-bit integer type for this toolchain"
# endif
#endif /* !defined(DOMINO_BASELINE_STDINT_PRESENT) */

/* Boolean for C89 */
#ifndef __cplusplus
# if !defined(__bool_true_false_are_defined)
/* Purpose: Boolean type for C89-visible headers when not compiling as C++. */
typedef unsigned char bool;
#  define true  1
#  define false 0
#  define __bool_true_false_are_defined 1
# elif !defined(bool)
typedef unsigned char bool;
#  if !defined(true)
#   define true 1
#  endif
#  if !defined(false)
#   define false 0
#  endif
# endif
#endif

#endif /* DOMINO_BASELINE_H */
