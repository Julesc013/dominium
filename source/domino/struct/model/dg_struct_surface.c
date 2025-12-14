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

