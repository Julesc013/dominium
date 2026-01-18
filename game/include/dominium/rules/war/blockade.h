/*
FILE: include/dominium/rules/war/blockade.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic blockade state and logistics effects.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Blockade updates and effects are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_BLOCKADE_H
#define DOMINIUM_RULES_WAR_BLOCKADE_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/epistemic.h"
#include "dominium/rules/governance/legitimacy_model.h"
#include "dominium/rules/infrastructure/store_model.h"
#include "dominium/rules/logistics/logistics_flow.h"

#ifdef __cplusplus
extern "C" {
#endif

#define BLOCKADE_MAX_FORCES 8u
#define BLOCKADE_MAX_SUPPLY_REFS 4u
#define BLOCKADE_CONTROL_SCALE 1000u

typedef enum blockade_policy {
    BLOCKADE_POLICY_DENY = 0,
    BLOCKADE_POLICY_THROTTLE = 1,
    BLOCKADE_POLICY_INSPECT = 2
} blockade_policy;

typedef enum blockade_status {
    BLOCKADE_STATUS_ACTIVE = 0,
    BLOCKADE_STATUS_ENDED = 1
} blockade_status;

typedef enum blockade_refusal_code {
    BLOCKADE_REFUSAL_NONE = 0,
    BLOCKADE_REFUSAL_INSUFFICIENT_FORCES = 1,
    BLOCKADE_REFUSAL_BLOCKADE_ALREADY_ACTIVE = 2,
    BLOCKADE_REFUSAL_OUT_OF_AUTHORITY = 3,
    BLOCKADE_REFUSAL_INSUFFICIENT_LOGISTICS = 4
} blockade_refusal_code;

const char* blockade_refusal_to_string(blockade_refusal_code code);

typedef struct blockade_state {
    u64 blockade_id;
    u64 domain_ref;
    u64 blockading_force_refs[BLOCKADE_MAX_FORCES];
    u32 blockading_force_count;
    dom_act_time_t start_act;
    u32 policy;
    dom_act_time_t next_due_tick;
    u32 status;
    u32 control_strength;
    u32 throttle_limit_pct;
    u32 inspect_delay_ticks;
    u64 supply_store_refs[BLOCKADE_MAX_SUPPLY_REFS];
    u32 supply_ref_count;
    u64 supply_asset_id;
    u32 supply_qty;
    u32 maintenance_interval;
    u64 legitimacy_id;
    i32 legitimacy_delta;
    u64 provenance_ref;
} blockade_state;

typedef struct blockade_registry {
    blockade_state* states;
    u32 count;
    u32 capacity;
    u64 next_id;
} blockade_registry;

typedef struct blockade_update_context {
    infra_store_registry* stores;
    legitimacy_registry* legitimacy;
    dom_act_time_t now_act;
} blockade_update_context;

typedef struct blockade_flow_effect {
    int deny;
    u32 adjusted_qty;
    dom_act_time_t adjusted_arrival_act;
    u32 delay_ticks;
} blockade_flow_effect;

typedef struct blockade_estimate {
    u64 domain_ref;
    u32 policy;
    u32 control_strength;
    u32 uncertainty_q16;
    int is_exact;
} blockade_estimate;

void blockade_registry_init(blockade_registry* reg,
                            blockade_state* storage,
                            u32 capacity,
                            u64 start_id);
blockade_state* blockade_find(blockade_registry* reg,
                              u64 blockade_id);
blockade_state* blockade_find_active(blockade_registry* reg,
                                     u64 domain_ref);
int blockade_register(blockade_registry* reg,
                      const blockade_state* input,
                      u64* out_id,
                      blockade_refusal_code* out_refusal);

int blockade_apply_maintenance(blockade_state* state,
                               blockade_update_context* ctx,
                               blockade_refusal_code* out_refusal);

int blockade_apply_to_flow(const blockade_state* state,
                           u64 domain_ref,
                           const logistics_flow_input* input,
                           blockade_flow_effect* out_effect,
                           blockade_refusal_code* out_refusal);

int blockade_estimate_from_view(const dom_epistemic_view* view,
                                const blockade_state* actual,
                                blockade_estimate* out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_BLOCKADE_H */
