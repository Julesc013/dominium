/*
FILE: source/domino/struct/model/dg_struct_surface.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/model/dg_struct_surface
RESPONSIBILITY: Implements `dg_struct_surface`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT surface template authoring model (C89). */
#include "struct/model/dg_struct_surface.h"

#include <string.h>

void dg_struct_surface_template_clear(dg_struct_surface_template *t) {
    if (!t) return;
    memset(t, 0, sizeof(*t));
}

int dg_struct_surface_template_validate(const dg_struct_surface_template *t) {
    if (!t) return -1;
    if (t->id == 0u) return -2;
    switch (t->kind) {
    case DG_STRUCT_SURF_TMPL_VOLUME_FACE:
        if (t->volume_id == 0u) return -10;
        if (t->face_kind != DG_STRUCT_VOL_FACE_TOP &&
            t->face_kind != DG_STRUCT_VOL_FACE_BOTTOM &&
            t->face_kind != DG_STRUCT_VOL_FACE_SIDE) return -11;
        return 0;
    case DG_STRUCT_SURF_TMPL_ENCLOSURE_FACE:
        if (t->enclosure_id == 0u) return -20;
        if (t->face_kind != DG_STRUCT_VOL_FACE_TOP &&
            t->face_kind != DG_STRUCT_VOL_FACE_BOTTOM &&
            t->face_kind != DG_STRUCT_VOL_FACE_SIDE) return -21;
        return 0;
    default:
        return -3;
    }
}

