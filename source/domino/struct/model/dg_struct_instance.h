/*
FILE: source/domino/struct/model/dg_struct_instance.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/model/dg_struct_instance
RESPONSIBILITY: Implements `dg_struct_instance`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT instance authoring model (C89).
 *
 * Authoring instances are the canonical source of truth for structures.
 * They contain placement (anchor + local pose) and references to parametric
 * templates (footprints, volumes, enclosures, surfaces, sockets, carriers).
 *
 * No baked geometry is stored here.
 */
#ifndef DG_STRUCT_INSTANCE_H
#define DG_STRUCT_INSTANCE_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"

#include "core/dg_pose.h"
#include "struct/model/dg_struct_ids.h"
#include "world/frame/dg_anchor.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_struct_instance {
    dg_struct_id id;

    dg_anchor anchor;    /* authoritative host reference */
    dg_pose   local_pose; /* local offset pose from anchor */

    dg_struct_footprint_id footprint_id;

    /* Template references (canonical sorted unique). */
    dg_struct_volume_id *volume_ids;
    u32                  volume_count;
    u32                  volume_capacity;

    dg_struct_enclosure_id *enclosure_ids;
    u32                     enclosure_count;
    u32                     enclosure_capacity;

    dg_struct_surface_template_id *surface_template_ids;
    u32                           surface_template_count;
    u32                           surface_template_capacity;

    dg_struct_socket_id *socket_ids;
    u32                  socket_count;
    u32                  socket_capacity;

    dg_struct_carrier_intent_id *carrier_intent_ids;
    u32                         carrier_intent_count;
    u32                         carrier_intent_capacity;

    /* Optional param overrides (canonical TLV container; opaque here).
     * If ptr is non-null, it is owned by this instance.
     */
    d_tlv_blob overrides;
} dg_struct_instance;

void dg_struct_instance_init(dg_struct_instance *s);
void dg_struct_instance_free(dg_struct_instance *s);
void dg_struct_instance_clear(dg_struct_instance *s);

int dg_struct_instance_set_overrides_copy(dg_struct_instance *s, const unsigned char *bytes, u32 len);

int dg_struct_instance_add_volume(dg_struct_instance *s, dg_struct_volume_id volume_id);
int dg_struct_instance_add_enclosure(dg_struct_instance *s, dg_struct_enclosure_id enclosure_id);
int dg_struct_instance_add_surface_template(dg_struct_instance *s, dg_struct_surface_template_id surface_template_id);
int dg_struct_instance_add_socket(dg_struct_instance *s, dg_struct_socket_id socket_id);
int dg_struct_instance_add_carrier_intent(dg_struct_instance *s, dg_struct_carrier_intent_id carrier_intent_id);

int dg_struct_instance_validate(const dg_struct_instance *s);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_STRUCT_INSTANCE_H */

