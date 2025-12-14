/* STRUCT volume authoring model (C89).
 *
 * Volumes are parametric solid/void definitions used to derive occupancy and
 * interior voids during compilation. No baked geometry is stored as
 * authoritative truth.
 */
#ifndef DG_STRUCT_VOLUME_H
#define DG_STRUCT_VOLUME_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "struct/model/dg_struct_ids.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dg_struct_volume_kind {
    DG_STRUCT_VOLUME_NONE = 0,
    DG_STRUCT_VOLUME_EXTRUDE = 1,
    DG_STRUCT_VOLUME_SWEEP = 2,
    DG_STRUCT_VOLUME_BOOL = 3
} dg_struct_volume_kind;

typedef enum dg_struct_bool_op {
    DG_STRUCT_BOOL_UNION = 0,
    DG_STRUCT_BOOL_SUBTRACT = 1,
    DG_STRUCT_BOOL_INTERSECT = 2
} dg_struct_bool_op;

typedef struct dg_struct_volume_extrude {
    dg_struct_footprint_id footprint_id; /* local footprint profile */
    dg_q                   base_z;       /* local Z offset */
    dg_q                   height;       /* extrusion height (>= 0) */
} dg_struct_volume_extrude;

/* Sweep is reserved for later; kept as a deterministic placeholder. */
typedef struct dg_struct_volume_sweep {
    dg_struct_footprint_id footprint_id;
    dg_q                   length; /* sweep length in local frame */
    dg_q                   height;
} dg_struct_volume_sweep;

typedef struct dg_struct_volume_bool_term {
    u32               term_index; /* local ordering key */
    dg_struct_volume_id volume_id; /* referenced operand (must not be self) */
    dg_struct_bool_op op;          /* op applied against accumulator */
    u32               _pad32;
} dg_struct_volume_bool_term;

typedef struct dg_struct_volume_bool {
    dg_struct_volume_bool_term *terms; /* sorted by term_index */
    u32                         term_count;
    u32                         term_capacity;
} dg_struct_volume_bool;

typedef union dg_struct_volume_u {
    dg_struct_volume_extrude extrude;
    dg_struct_volume_sweep   sweep;
    dg_struct_volume_bool    boolean;
} dg_struct_volume_u;

typedef struct dg_struct_volume {
    dg_struct_volume_id   id;
    dg_struct_volume_kind kind;
    d_bool                is_void; /* D_TRUE means this volume defines void */
    u32                   _pad32;
    dg_struct_volume_u    u;
} dg_struct_volume;

void dg_struct_volume_init(dg_struct_volume *v);
void dg_struct_volume_free(dg_struct_volume *v);

/* Configure volume kinds (clears previous kind-specific storage). */
int dg_struct_volume_set_extrude(dg_struct_volume *v, dg_struct_footprint_id footprint_id, dg_q base_z, dg_q height, d_bool is_void);
int dg_struct_volume_set_sweep(dg_struct_volume *v, dg_struct_footprint_id footprint_id, dg_q length, dg_q height, d_bool is_void);
int dg_struct_volume_set_boolean(dg_struct_volume *v, d_bool is_void);

int dg_struct_volume_bool_reserve_terms(dg_struct_volume *v, u32 capacity);
int dg_struct_volume_bool_set_term(dg_struct_volume *v, u32 term_index, dg_struct_volume_id volume_id, dg_struct_bool_op op);

/* Validate basic invariants (does not resolve references). */
int dg_struct_volume_validate(const dg_struct_volume *v);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_STRUCT_VOLUME_H */

