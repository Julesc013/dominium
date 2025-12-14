/* TRANS junctions (topology nodes) (C89). */
#ifndef DG_TRANS_JUNCTION_H
#define DG_TRANS_JUNCTION_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "trans/model/dg_trans_ids.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_trans_junction_incident {
    dg_trans_alignment_id alignment_id;
    u16                   port_index; /* stable within (junction, alignment) */
    u16                   level;      /* grade-separated layer index */

    dg_q station_s; /* connection station on the alignment */

    /* Optional constraints (0 means "unspecified"). */
    dg_q min_radius;
    dg_q max_grade;
    dg_q clearance;
} dg_trans_junction_incident;

typedef struct dg_trans_junction {
    dg_trans_junction_id id;
    u64                  archetype_id; /* optional future expansion */

    dg_trans_junction_incident *incidents; /* canonical sorted by (alignment_id, port_index) */
    u32                         incident_count;
    u32                         incident_capacity;
} dg_trans_junction;

void dg_trans_junction_init(dg_trans_junction *j);
void dg_trans_junction_free(dg_trans_junction *j);

int dg_trans_junction_reserve_incidents(dg_trans_junction *j, u32 capacity);

/* Add or update an incident edge by (alignment_id, port_index). */
int dg_trans_junction_set_incident(dg_trans_junction *j, const dg_trans_junction_incident *inc);

/* Canonical comparator for incidents. */
int dg_trans_junction_incident_cmp(const dg_trans_junction_incident *a, const dg_trans_junction_incident *b);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_TRANS_JUNCTION_H */

