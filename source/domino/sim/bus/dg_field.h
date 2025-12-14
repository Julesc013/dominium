/* Deterministic field system (C89).
 *
 * Fields are chunk-local fixed-point layers updated by packets and sampled via
 * deterministic kernels. No gameplay semantics are embedded here.
 */
#ifndef DG_FIELD_H
#define DG_FIELD_H

#include "sim/bus/dg_field_layer.h"
#include "sim/pkt/dg_pkt_field.h"
#include "sim/pkt/registry/dg_type_registry.h"
#include "sim/sched/dg_budget.h"
#include "sim/sched/dg_work_queue.h"

#ifdef __cplusplus
extern "C" {
#endif

struct dg_sched;

#define DG_FIELD_MAX_DIM 4u

/* Field update TLV tags (payload bytes are little-endian). */
#define DG_FIELD_TLV_SET_CELL 1u

typedef struct dg_field_pos {
    dg_chunk_id chunk_id; /* identifies chunk storage (domain mapping is external) */
    q16_16      x;        /* chunk-local grid coordinate (Q16.16) */
    q16_16      y;
    q16_16      z;
} dg_field_pos;

typedef struct dg_field_type_desc {
    dg_type_id field_type_id;
    u8         dim;    /* 1..DG_FIELD_MAX_DIM */
    u16        res;    /* grid points per axis (>= 2 recommended) */
} dg_field_type_desc;

typedef struct dg_field {
    /* Optional type registry for TLV schema validation. */
    dg_field_type_registry type_registry;

    dg_field_type_desc *types;
    u32                 type_count;
    u32                 type_capacity;

    dg_field_layer *layers;
    u32             layer_count;
    u32             layer_capacity;

    dg_work_queue update_q; /* sorted by canonical update key */

    dg_tick current_tick; /* last tick applied via apply_updates() */

    /* Probes/counters (no logging). */
    u32 probe_updates_applied;   /* update packets applied */
    u32 probe_samples_performed; /* successful samples */
    u32 probe_deferred_work;     /* updates/samples deferred by budget */
} dg_field;

void dg_field_init(dg_field *f);
void dg_field_free(dg_field *f);

int dg_field_reserve(dg_field *f, u32 type_cap, u32 layer_cap, u32 update_queue_cap);

/* Register a field type with dimension and grid resolution. */
int dg_field_register_type(dg_field *f, const dg_field_type_desc *desc);

/* Optional schema registration/validation for field packets. */
int dg_field_register_schema(dg_field *f, const dg_type_registry_entry *entry);

/* Buffer a field update packet (not applied immediately). */
int dg_field_publish_update(dg_field *f, const dg_pkt_field_update *update);

/* Apply buffered updates with tick <= current_tick under budget (1 unit per update). */
u32 dg_field_apply_updates(dg_field *f, dg_budget *budget, dg_tick current_tick);

/* Deterministic sampling API (PH_SENSE). Returns 0 on success, >0 on deferral. */
int dg_field_sample(
    dg_field      *f,
    dg_budget     *budget,
    dg_domain_id   domain_id,
    const dg_field_pos *pos,
    dg_type_id     field_type_id,
    q16_16        *out_values,
    u32            out_dim
);

/* Scheduler integration: installs update application handler in PH_SENSE. */
int dg_field_install_sense_update(dg_field *f, struct dg_sched *sched, u64 priority_key);

u32 dg_field_probe_updates_applied(const dg_field *f);
u32 dg_field_probe_samples_performed(const dg_field *f);
u32 dg_field_probe_deferred_work(const dg_field *f);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_FIELD_H */

