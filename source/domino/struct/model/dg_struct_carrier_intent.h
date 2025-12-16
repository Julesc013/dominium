/*
FILE: source/domino/struct/model/dg_struct_carrier_intent.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/model/dg_struct_carrier_intent
RESPONSIBILITY: Implements `dg_struct_carrier_intent`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT carrier intent authoring model (C89).
 *
 * Carrier intents are parametric requests describing structure/terrain/corridor
 * interactions (bridges, tunnels, cut/fill). They are not baked geometry.
 */
#ifndef DG_STRUCT_CARRIER_INTENT_H
#define DG_STRUCT_CARRIER_INTENT_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"

#include "core/dg_pose.h"
#include "struct/model/dg_struct_ids.h"
#include "world/frame/dg_anchor.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dg_struct_carrier_kind {
    DG_STRUCT_CARRIER_BRIDGE = 1,
    DG_STRUCT_CARRIER_VIADUCT = 2,
    DG_STRUCT_CARRIER_TUNNEL = 3,
    DG_STRUCT_CARRIER_CUT = 4,
    DG_STRUCT_CARRIER_FILL = 5
} dg_struct_carrier_kind;

typedef struct dg_struct_carrier_intent {
    dg_struct_carrier_intent_id id;
    dg_struct_carrier_kind      kind;
    u32                         _pad32;

    dg_anchor a0;
    dg_anchor a1;

    /* Generic size parameters (interpretation depends on kind). */
    dg_q width;
    dg_q height;
    dg_q depth;

    /* Optional param extension. If ptr is non-null, it is owned by this struct. */
    d_tlv_blob params;
} dg_struct_carrier_intent;

void dg_struct_carrier_intent_init(dg_struct_carrier_intent *c);
void dg_struct_carrier_intent_free(dg_struct_carrier_intent *c);
void dg_struct_carrier_intent_clear(dg_struct_carrier_intent *c);

int dg_struct_carrier_intent_set_params_copy(dg_struct_carrier_intent *c, const unsigned char *bytes, u32 len);

int dg_struct_carrier_intent_validate(const dg_struct_carrier_intent *c);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_STRUCT_CARRIER_INTENT_H */

