/*
FILE: source/domino/struct/model/dg_struct_surface.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/model/dg_struct_surface
RESPONSIBILITY: Defines internal contract for `dg_struct_surface`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT surface template authoring model (C89).
 *
 * Surface templates describe which derived surfaces should be exposed in the
 * compiled surface graph (facades, panels, room surfaces, etc.). They are
 * parametric selection rules, not baked geometry.
 */
#ifndef DG_STRUCT_SURFACE_H
#define DG_STRUCT_SURFACE_H

#include "domino/core/types.h"

#include "struct/model/dg_struct_ids.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dg_struct_surface_template_kind {
    DG_STRUCT_SURF_TMPL_NONE = 0,
    DG_STRUCT_SURF_TMPL_VOLUME_FACE = 1,
    DG_STRUCT_SURF_TMPL_ENCLOSURE_FACE = 2
} dg_struct_surface_template_kind;

typedef enum dg_struct_volume_face_kind {
    DG_STRUCT_VOL_FACE_TOP = 0,
    DG_STRUCT_VOL_FACE_BOTTOM = 1,
    DG_STRUCT_VOL_FACE_SIDE = 2
} dg_struct_volume_face_kind;

typedef struct dg_struct_surface_template {
    dg_struct_surface_template_id id;
    dg_struct_surface_template_kind kind;
    u32 _pad32;

    dg_struct_volume_id    volume_id;    /* required for VOLUME_FACE */
    dg_struct_enclosure_id enclosure_id; /* optional for ENCL_* (0 allowed) */

    dg_struct_volume_face_kind face_kind;
    u32                        face_index; /* only for SIDE; 0-based */
} dg_struct_surface_template;

void dg_struct_surface_template_clear(dg_struct_surface_template *t);

int dg_struct_surface_template_validate(const dg_struct_surface_template *t);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_STRUCT_SURFACE_H */

