/*
FILE: source/domino/decor/model/dg_decor_override.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/model/dg_decor_override
RESPONSIBILITY: Defines internal contract for `dg_decor_override`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR overrides (C89).
 *
 * Overrides are authoritative edit records applied deterministically to
 * baseline-generated decor candidates.
 */
#ifndef DG_DECOR_OVERRIDE_H
#define DG_DECOR_OVERRIDE_H

#include "domino/core/types.h"

#include "core/dg_pose.h"

#include "decor/model/dg_decor_ids.h"
#include "decor/model/dg_decor_item.h"
#include "decor/model/dg_decor_host.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dg_decor_override_op {
    DG_DECOR_OVERRIDE_NONE = 0,
    DG_DECOR_OVERRIDE_PIN = 1,
    DG_DECOR_OVERRIDE_SUPPRESS = 2,
    DG_DECOR_OVERRIDE_REPLACE = 3,
    DG_DECOR_OVERRIDE_MOVE = 4,
    DG_DECOR_OVERRIDE_TAG = 5
} dg_decor_override_op;

typedef struct dg_decor_suppress_region {
    dg_decor_host host; /* exact host binding */

    /* Kind-specific interval/region. All ranges are inclusive; canonicalized so lo<=hi.
     * For surfaces: (u0,u1,v0,v1) in Q48.16.
     * For corridor: (s0,s1) in Q48.16 (station along alignment).
     * For socket: (param0,param1) in Q48.16.
     */
    dg_q u0, u1;
    dg_q v0, v1;
    dg_q s0, s1;
    dg_q param0, param1;
} dg_decor_suppress_region;

typedef struct dg_decor_override_pin {
    dg_decor_item item; /* full item snapshot; decor_id must be stable */
} dg_decor_override_pin;

typedef struct dg_decor_override_suppress {
    dg_decor_suppress_region region;
} dg_decor_override_suppress;

typedef struct dg_decor_override_replace {
    dg_decor_id      target_decor_id;
    dg_decor_type_id new_decor_type_id;
    dg_decor_tlv     new_params; /* replaces params when len>0 */
    u32              new_flags_mask;  /* which flags to update */
    u32              new_flags_value; /* replacement flag bits */
} dg_decor_override_replace;

typedef struct dg_decor_override_move {
    dg_decor_id target_decor_id;
    dg_anchor   new_anchor;
    dg_pose     new_local_offset;
    d_bool      has_anchor;
    d_bool      has_local_offset;
    u32         _pad32;
} dg_decor_override_move;

typedef struct dg_decor_override_tag {
    dg_decor_id    target_decor_id;
    dg_decor_tag_id tag_id;
    u64            value;
} dg_decor_override_tag;

typedef union dg_decor_override_u {
    dg_decor_override_pin      pin;
    dg_decor_override_suppress suppress;
    dg_decor_override_replace  replace;
    dg_decor_override_move     move;
    dg_decor_override_tag      tag;
} dg_decor_override_u;

typedef struct dg_decor_override {
    dg_decor_override_id id;
    dg_decor_override_op op;
    u32                  _pad32; /* reserved; must be zero */
    dg_decor_override_u   u;
} dg_decor_override;

void dg_decor_override_clear(dg_decor_override *ovr);

/* Canonical override ordering is ascending override_id. */
int dg_decor_override_cmp_id(const dg_decor_override *a, const dg_decor_override *b);

/* Region helpers for SUPPRESS. */
void dg_decor_suppress_region_canon(dg_decor_suppress_region *r);
d_bool dg_decor_suppress_region_contains_anchor(const dg_decor_suppress_region *r, const dg_anchor *a);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DECOR_OVERRIDE_H */

