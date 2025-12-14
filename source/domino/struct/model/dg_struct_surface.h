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

