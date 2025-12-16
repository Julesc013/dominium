/*
FILE: source/domino/struct/model/d_struct_model.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/model/d_struct_model
RESPONSIBILITY: Implements `d_struct_model`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT model scaffolding (C89).
 * See docs/SPEC_TRANS_STRUCT_DECOR.md
 */
#ifndef D_STRUCT_MODEL_H
#define D_STRUCT_MODEL_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque authored/semantic structure model representation. */
typedef struct d_struct_model d_struct_model;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_STRUCT_MODEL_H */

