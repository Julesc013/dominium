/*
FILE: source/domino/system/core/base/core_types.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/base/core_types
RESPONSIBILITY: Implements `core_types`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_CORE_TYPES_H
#define DOM_CORE_TYPES_H

#include <stddef.h>

typedef unsigned char      u8;
typedef signed char        i8;
typedef unsigned short     u16;
typedef signed short       i16;
typedef unsigned int       u32;
typedef signed int         i32;

#if defined(_MSC_VER)
typedef unsigned __int64   u64;
typedef signed __int64     i64;
#else
typedef unsigned long long u64;
typedef signed long long   i64;
#endif

typedef int b32;
#define TRUE 1
#define FALSE 0

#endif /* DOM_CORE_TYPES_H */
