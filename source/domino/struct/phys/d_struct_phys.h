/*
FILE: source/domino/struct/phys/d_struct_phys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/phys/d_struct_phys
RESPONSIBILITY: Implements `d_struct_phys`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT physical representation scaffolding (C89).
 * See docs/SPEC_TRANS_STRUCT_DECOR.md
 */
#ifndef D_STRUCT_PHYS_H
#define D_STRUCT_PHYS_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque structure-physical representation state. */
typedef struct d_struct_phys d_struct_phys;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_STRUCT_PHYS_H */

