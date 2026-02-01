/*
FILE: source/domino/content/d_content_extra.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / content/d_content_extra
RESPONSIBILITY: Defines internal contract for `d_content_extra`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Shared TLV parameter tags for data-driven content (C89). */
#ifndef D_CONTENT_EXTRA_H
#define D_CONTENT_EXTRA_H

#include "domino/core/types.h"

/* Resource model params: generic solid strata */
#define D_TLV_RES_STRATA_MEAN_GRADE       0x01u
#define D_TLV_RES_STRATA_MEAN_QUANTITY    0x02u
#define D_TLV_RES_STRATA_NOISE_SCALE      0x03u
#define D_TLV_RES_STRATA_REGEN_RATE       0x04u

/* Generic process parameter tags */
#define D_TLV_PROCESS_RATE_PER_TICK       0x01u
#define D_TLV_PROCESS_DEPOSIT_VALUE_SLOT  0x02u
#define D_TLV_PROCESS_DEPLETION_AMOUNT    0x03u
#define D_TLV_PROCESS_OUTPUT_ITEM_ID      0x04u
#define D_TLV_PROCESS_OUTPUT_PER_TICK     0x05u

/* Structure layout tags */
#define D_TLV_STRUCT_LAYOUT_FOOTPRINT_W   0x01u
#define D_TLV_STRUCT_LAYOUT_FOOTPRINT_H   0x02u
#define D_TLV_STRUCT_LAYOUT_ANCHOR_Z      0x03u
#define D_TLV_STRUCT_LAYOUT_INV_IN_CONTAINER  0x04u /* u32 container_proto_id */
#define D_TLV_STRUCT_LAYOUT_INV_OUT_CONTAINER 0x05u /* u32 container_proto_id */

/* Structure IO/ports */
#define D_TLV_STRUCT_IO_PORT              0x10u
#define D_TLV_STRUCT_PORT_KIND            0x01u
#define D_TLV_STRUCT_PORT_POS_X           0x02u
#define D_TLV_STRUCT_PORT_POS_Y           0x03u
#define D_TLV_STRUCT_PORT_DIR_Z           0x04u

enum {
    D_STRUCT_PORT_RESOURCE_IN = 1,
    D_STRUCT_PORT_ITEM_OUT    = 2,
    D_STRUCT_PORT_ITEM_IN     = 3,

    /* Generic spline/pipe attachment ports (domain-agnostic). */
    D_STRUCT_PORT_SPLINE_ITEM_OUT = 10,
    D_STRUCT_PORT_SPLINE_ITEM_IN  = 11,
    D_STRUCT_PORT_SPLINE_VEHICLE  = 12,
    D_STRUCT_PORT_FLUID_IO        = 13
};

/* Structure process list */
#define D_TLV_STRUCT_PROCESS_ALLOWED      0x20u

/* Environmental volume graph (used inside structure.layout and vehicle.params blobs).
 * Records are TLVs whose payload is itself a TLV blob of fields.
 */
#define D_TLV_ENV_VOLUME                  0x30u
#define D_TLV_ENV_VOLUME_MIN_X            0x01u  /* q16_16 (local) */
#define D_TLV_ENV_VOLUME_MIN_Y            0x02u
#define D_TLV_ENV_VOLUME_MIN_Z            0x03u
#define D_TLV_ENV_VOLUME_MAX_X            0x04u
#define D_TLV_ENV_VOLUME_MAX_Y            0x05u
#define D_TLV_ENV_VOLUME_MAX_Z            0x06u

#define D_TLV_ENV_EDGE                    0x31u
#define D_TLV_ENV_EDGE_A                  0x01u  /* u16 (1-based local volume index) */
#define D_TLV_ENV_EDGE_B                  0x02u  /* u16 (1-based local volume index, 0 = exterior) */
#define D_TLV_ENV_EDGE_GAS_K              0x03u  /* q16_16 */
#define D_TLV_ENV_EDGE_HEAT_K             0x04u  /* q16_16 */

/* Generic hydrology interaction flags for structures/vehicles (optional). */
#define D_TLV_ENV_HYDRO_FLAGS             0x32u  /* u32 bitmask */
enum {
    D_ENV_HYDRO_WATERTIGHT = 1u << 0,
    D_ENV_HYDRO_FLOODABLE  = 1u << 1,
    D_ENV_HYDRO_DRAINS     = 1u << 2
};

/* Job template environment requirements (inside job_template.params blob). */
#define D_TLV_JOB_ENV_RANGE               0x10u  /* record payload is TLV fields */
#define D_TLV_JOB_ENV_FIELD_ID            0x01u  /* u16 */
#define D_TLV_JOB_ENV_MIN                 0x02u  /* q16_16 */
#define D_TLV_JOB_ENV_MAX                 0x03u  /* q16_16 */

/* Job template generic requirements/rewards (inside job_template.requirements/rewards). */
#define D_TLV_JOB_REQ_AGENT_TAGS          0x11u  /* u32 bitmask of required d_content_tag */
#define D_TLV_JOB_REQ_DURATION            0x12u  /* q16_16 nominal duration (optional) */

#define D_TLV_JOB_REWARD_PAYMENT          0x20u  /* record payload is TLV fields */
#define D_TLV_JOB_PAY_FROM_ACCOUNT        0x01u  /* u32 */
#define D_TLV_JOB_PAY_TO_ACCOUNT          0x02u  /* u32 */
#define D_TLV_JOB_PAY_AMOUNT              0x03u  /* q32_32 */

/* Research cost blob tags (inside d_proto_research.cost). */
#define D_TLV_RESEARCH_COST_REQUIRED      0x40u  /* q32_32 required points */

/* Research point source params (inside d_proto_research_point_source.params). */
#define D_TLV_RP_SOURCE_TARGET_RESEARCH_ID       0x01u /* repeated u32 d_research_id */
#define D_TLV_RP_SOURCE_TARGET_RESEARCH_TAGS_ALL 0x02u /* u32 d_content_tag mask */
#define D_TLV_RP_SOURCE_TARGET_RESEARCH_TAGS_ANY 0x03u /* u32 d_content_tag mask */

/* Policy scope/effect/conditions TLV tags (inside d_proto_policy_rule blobs). */
#define D_TLV_POLICY_SCOPE_SUBJECT_KIND          0x10u /* u32 */
#define D_TLV_POLICY_SCOPE_SUBJECT_ID            0x11u /* repeated u32 */
#define D_TLV_POLICY_SCOPE_SUBJECT_TAGS_ALL      0x12u /* u32 */
#define D_TLV_POLICY_SCOPE_SUBJECT_TAGS_ANY      0x13u /* u32 */
#define D_TLV_POLICY_SCOPE_ORG_ID                0x14u /* repeated u32 d_org_id */

#define D_TLV_POLICY_COND_RESEARCH_COMPLETED     0x20u /* repeated u32 d_research_id */
#define D_TLV_POLICY_COND_RESEARCH_NOT_COMPLETED 0x21u /* repeated u32 d_research_id */

#define D_TLV_POLICY_EFFECT_ALLOWED              0x30u /* u32 (0/1) */
#define D_TLV_POLICY_EFFECT_MULTIPLIER           0x31u /* q16_16 */
#define D_TLV_POLICY_EFFECT_CAP                  0x32u /* q16_16 */

/* Blueprint payload */
#define D_TLV_BLUEPRINT_STRUCTURE_PROTO   0x01u

#endif /* D_CONTENT_EXTRA_H */
