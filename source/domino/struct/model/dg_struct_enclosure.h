/*
FILE: source/domino/struct/model/dg_struct_enclosure.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/model/dg_struct_enclosure
RESPONSIBILITY: Implements `dg_struct_enclosure`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT enclosure authoring model (C89).
 *
 * Enclosures define interior spaces and adjacency. They reference volumes
 * (typically void volumes) and define apertures (doors/vents/openings) for
 * room graph compilation.
 */
#ifndef DG_STRUCT_ENCLOSURE_H
#define DG_STRUCT_ENCLOSURE_H

#include "domino/core/types.h"

#include "struct/model/dg_struct_ids.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dg_struct_aperture_kind {
    DG_STRUCT_APERTURE_DOOR = 1,
    DG_STRUCT_APERTURE_VENT = 2,
    DG_STRUCT_APERTURE_OPENING = 3
} dg_struct_aperture_kind;

typedef struct dg_struct_aperture {
    u64                   aperture_id;     /* stable within enclosure */
    dg_struct_enclosure_id to_enclosure_id; /* 0 means exterior */
    dg_struct_aperture_kind kind;
    u32                   _pad32;
} dg_struct_aperture;

typedef struct dg_struct_enclosure {
    dg_struct_enclosure_id id;

    /* Referenced volumes (canonical sorted by volume_id). */
    dg_struct_volume_id *volume_ids;
    u32                  volume_count;
    u32                  volume_capacity;

    /* Apertures (canonical sorted by aperture_id). */
    dg_struct_aperture *apertures;
    u32                 aperture_count;
    u32                 aperture_capacity;
} dg_struct_enclosure;

void dg_struct_enclosure_init(dg_struct_enclosure *e);
void dg_struct_enclosure_free(dg_struct_enclosure *e);

int dg_struct_enclosure_reserve_volumes(dg_struct_enclosure *e, u32 capacity);
int dg_struct_enclosure_add_volume(dg_struct_enclosure *e, dg_struct_volume_id volume_id);

int dg_struct_enclosure_reserve_apertures(dg_struct_enclosure *e, u32 capacity);
int dg_struct_enclosure_set_aperture(dg_struct_enclosure *e, const dg_struct_aperture *ap);

/* Validate basic invariants (does not resolve referenced IDs). */
int dg_struct_enclosure_validate(const dg_struct_enclosure *e);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_STRUCT_ENCLOSURE_H */

