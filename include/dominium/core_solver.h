/*
FILE: include/dominium/core_solver.h
MODULE: Dominium
PURPOSE: Deterministic constraint solver with explainable selection output.
NOTES: Selection order and tie-breaks are stable; component IDs are ASCII tokens.
*/
#ifndef DOMINIUM_CORE_SOLVER_H
#define DOMINIUM_CORE_SOLVER_H

#include "domino/core/types.h"
#include "dominium/core_caps.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Limits (fixed; append-only if changed).
 *------------------------------------------------------------*/
#define CORE_SOLVER_MAX_COMPONENTS 128u
#define CORE_SOLVER_MAX_CATEGORIES 16u
#define CORE_SOLVER_MAX_SELECTION 32u
#define CORE_SOLVER_MAX_REJECTIONS 256u
#define CORE_SOLVER_MAX_CONSTRAINTS 16u
#define CORE_SOLVER_MAX_CONFLICTS 8u
#define CORE_SOLVER_MAX_OVERRIDES 16u
#define CORE_SOLVER_MAX_ID 64u

/*------------------------------------------------------------
 * Categories (stable numeric IDs; append-only).
 *------------------------------------------------------------*/
typedef enum core_solver_category_e {
    CORE_SOLVER_CAT_NONE = 0u,
    CORE_SOLVER_CAT_PLATFORM = 1u,
    CORE_SOLVER_CAT_UI = 2u,
    CORE_SOLVER_CAT_RENDERER = 3u,
    CORE_SOLVER_CAT_PROVIDER_NET = 10u,
    CORE_SOLVER_CAT_PROVIDER_TRUST = 11u,
    CORE_SOLVER_CAT_PROVIDER_KEYCHAIN = 12u,
    CORE_SOLVER_CAT_PROVIDER_CONTENT = 13u,
    CORE_SOLVER_CAT_PROVIDER_OS_INTEGRATION = 14u
} core_solver_category;

/*------------------------------------------------------------
 * Constraint ops (stable; append-only).
 *------------------------------------------------------------*/
typedef enum core_solver_constraint_op_e {
    CORE_SOLVER_OP_EQ = 1u,
    CORE_SOLVER_OP_NE = 2u,
    CORE_SOLVER_OP_GE = 3u,
    CORE_SOLVER_OP_LE = 4u,
    CORE_SOLVER_OP_IN_RANGE = 5u
} core_solver_constraint_op;

typedef struct core_solver_constraint_t {
    u32 key_id;
    u8 op;
    u8 type;
    u16 reserved;
    u32 weight; /* used for prefers (0 defaults to 1) */
    core_cap_value value;
} core_solver_constraint;

/*------------------------------------------------------------
 * Component descriptors.
 *------------------------------------------------------------*/
typedef struct core_solver_component_desc_t {
    const char* component_id;
    u32 category_id;
    u32 priority;
    u32 flags;

    const core_cap_entry* provides;
    u32 provides_count;

    const core_solver_constraint* requires;
    u32 requires_count;

    const core_solver_constraint* forbids;
    u32 forbids_count;

    const core_solver_constraint* prefers;
    u32 prefers_count;

    const char* const* conflicts;
    u32 conflicts_count;
} core_solver_component_desc;

typedef struct core_solver_category_desc_t {
    u32 category_id;
    u32 required; /* 0/1 */
} core_solver_category_desc;

typedef struct core_solver_override_t {
    u32 category_id;
    const char* component_id;
} core_solver_override;

/*------------------------------------------------------------
 * Explainable output.
 *------------------------------------------------------------*/
typedef enum core_solver_fail_reason_e {
    CORE_SOLVER_FAIL_NONE = 0u,
    CORE_SOLVER_FAIL_OVERRIDE_NOT_FOUND = 1u,
    CORE_SOLVER_FAIL_OVERRIDE_INELIGIBLE = 2u,
    CORE_SOLVER_FAIL_NO_ELIGIBLE = 3u
} core_solver_fail_reason;

typedef enum core_solver_select_reason_e {
    CORE_SOLVER_SELECT_SCORE = 1u,
    CORE_SOLVER_SELECT_OVERRIDE = 2u
} core_solver_select_reason;

typedef enum core_solver_reject_reason_e {
    CORE_SOLVER_REJECT_CONSTRAINT = 1u,
    CORE_SOLVER_REJECT_CONFLICT = 2u,
    CORE_SOLVER_REJECT_OVERRIDE_MISMATCH = 3u
} core_solver_reject_reason;

typedef struct core_solver_selected_t {
    u32 category_id;
    char component_id[CORE_SOLVER_MAX_ID];
    u32 reason;
    u32 score;
    u32 priority;
    u32 prefers_satisfied;
} core_solver_selected;

typedef struct core_solver_reject_t {
    u32 category_id;
    char component_id[CORE_SOLVER_MAX_ID];
    u32 reason;
    core_solver_constraint constraint;
    u32 actual_present;
    u8 actual_type;
    u8 reserved;
    u16 reserved2;
    core_cap_value actual_value;
    char conflict_component_id[CORE_SOLVER_MAX_ID];
} core_solver_reject;

typedef struct core_solver_result_t {
    u32 ok; /* 0/1 */
    u32 fail_reason;
    u32 fail_category;
    u32 selected_count;
    core_solver_selected selected[CORE_SOLVER_MAX_SELECTION];
    u32 rejected_count;
    core_solver_reject rejected[CORE_SOLVER_MAX_REJECTIONS];
} core_solver_result;

typedef u32 (*core_solver_score_fn)(const core_solver_component_desc* comp, void* user);

typedef struct core_solver_desc_t {
    const core_solver_category_desc* categories;
    u32 category_count;

    const core_solver_component_desc* components;
    u32 component_count;

    const core_caps* host_caps;

    const core_solver_constraint* profile_requires;
    u32 profile_requires_count;

    const core_solver_constraint* profile_forbids;
    u32 profile_forbids_count;

    const core_solver_override* overrides;
    u32 override_count;

    core_solver_score_fn score_fn;
    void* score_user;
} core_solver_desc;

void core_solver_result_clear(core_solver_result* out_result);
dom_abi_result core_solver_select(const core_solver_desc* desc, core_solver_result* out_result);

const char* core_solver_category_token(u32 category_id);
const char* core_solver_op_token(u32 op);
const char* core_solver_fail_reason_token(u32 reason);
const char* core_solver_reject_reason_token(u32 reason);
const char* core_solver_select_reason_token(u32 reason);

/*------------------------------------------------------------
 * TLV encoding for explain output (deterministic; canonical order).
 *------------------------------------------------------------*/
typedef dom_abi_result (*core_solver_write_fn)(void* user, const void* data, u32 len);

typedef struct core_solver_write_sink_t {
    void* user;
    core_solver_write_fn write;
} core_solver_write_sink;

dom_abi_result core_solver_explain_write_tlv(const core_solver_result* result, const core_solver_write_sink* sink);
dom_abi_result core_solver_explain_read_tlv(const unsigned char* data, u32 size, core_solver_result* out_result, u32* out_used);
u32 core_solver_explain_encoded_size(const core_solver_result* result);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_CORE_SOLVER_H */
