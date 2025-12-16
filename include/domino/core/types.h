/*
FILE: include/domino/core/types.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / core/types
RESPONSIBILITY: Defines the public contract for `types` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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

/* Purpose: Unsigned 8-bit integer used by Domino public ABI.
 * ABI: Exactly 8 bits.
 */
typedef uint8_t  u8;
/* Purpose: Signed 8-bit integer used by Domino public ABI.
 * ABI: Exactly 8 bits.
 */
typedef int8_t   i8;
/* Purpose: Unsigned 16-bit integer used by Domino public ABI.
 * ABI: Exactly 16 bits.
 */
typedef uint16_t u16;
/* Purpose: Signed 16-bit integer used by Domino public ABI.
 * ABI: Exactly 16 bits.
 */
typedef int16_t  i16;
/* Purpose: Unsigned 32-bit integer used by Domino public ABI.
 * ABI: Exactly 32 bits.
 */
typedef uint32_t u32;
/* Purpose: Signed 32-bit integer used by Domino public ABI.
 * ABI: Exactly 32 bits.
 */
typedef int32_t  i32;
/* Purpose: Unsigned 64-bit integer used by Domino public ABI.
 * ABI: Exactly 64 bits.
 */
typedef uint64_t u64;
/* Purpose: Signed 64-bit integer used by Domino public ABI.
 * ABI: Exactly 64 bits.
 */
typedef int64_t  i64;

/* Purpose: Boolean value type used by Domino C89-visible APIs.
 * Valid values: `D_FALSE` (0) and `D_TRUE` (1).
 * ABI: `int`.
 */
typedef int d_bool;
/* Purpose: Canonical true value for `d_bool` (0/1 convention). */
#define D_TRUE  1
/* Purpose: Canonical false value for `d_bool` (0/1 convention). */
#define D_FALSE 0

/* Purpose: Select the smaller of two values.
 * Side effects: Arguments may be evaluated more than once.
 */
#define D_MIN(a,b) (((a) < (b)) ? (a) : (b))
/* Purpose: Select the larger of two values.
 * Side effects: Arguments may be evaluated more than once.
 */
#define D_MAX(a,b) (((a) > (b)) ? (a) : (b))
/* Purpose: Clamp `x` into the inclusive range [`lo`, `hi`].
 * Side effects: Arguments may be evaluated more than once.
 */
#define D_CLAMP(x,lo,hi) (((x) < (lo)) ? (lo) : (((x) > (hi)) ? (hi) : (x)))

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_TYPES_H */
