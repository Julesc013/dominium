/*
FILE: include/domino/world/crafting_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/crafting_fields
RESPONSIBILITY: Deterministic, process-only crafting and disassembly over explicit inventories.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by CRAFT0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_CRAFTING_FIELDS_H
#define DOMINO_WORLD_CRAFTING_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_CRAFT_MAX_RECIPES 64u
#define DOM_CRAFT_MAX_INPUTS 16u
#define DOM_CRAFT_MAX_OUTPUTS 16u
#define DOM_CRAFT_MAX_BYPRODUCTS 8u
#define DOM_CRAFT_MAX_TOOLS 16u
#define DOM_CRAFT_MAX_INVENTORY 128u

#define DOM_CRAFT_UNKNOWN_Q16 ((q16_16)0x80000000)

enum dom_craft_item_kind {
    DOM_CRAFT_ITEM_MATERIAL = 0u,
    DOM_CRAFT_ITEM_PART = 1u,
    DOM_CRAFT_ITEM_ASSEMBLY = 2u,
    DOM_CRAFT_ITEM_TOOL = 3u
};

enum dom_craft_item_flags {
    DOM_CRAFT_ITEM_DAMAGEABLE = 1u << 0u
};

enum dom_craft_recipe_flags {
    DOM_CRAFT_RECIPE_DISASSEMBLY = 1u << 0u,
    DOM_CRAFT_RECIPE_REQUIRE_TEMP = 1u << 1u,
    DOM_CRAFT_RECIPE_REQUIRE_HUMIDITY = 1u << 2u,
    DOM_CRAFT_RECIPE_REQUIRE_ENVIRONMENT = 1u << 3u
};

enum dom_craft_failure_mode {
    DOM_CRAFT_FAILURE_REFUSE = 0u,
    DOM_CRAFT_FAILURE_WASTE = 1u,
    DOM_CRAFT_FAILURE_DAMAGE = 2u
};

enum dom_craft_result_flags {
    DOM_CRAFT_RESULT_LAW_BLOCK = 1u << 0u,
    DOM_CRAFT_RESULT_METALAW_BLOCK = 1u << 1u,
    DOM_CRAFT_RESULT_FAILURE = 1u << 2u,
    DOM_CRAFT_RESULT_WASTE = 1u << 3u,
    DOM_CRAFT_RESULT_DISASSEMBLY = 1u << 4u,
    DOM_CRAFT_RESULT_TOOL_DAMAGE = 1u << 5u
};

typedef struct dom_craft_item_req {
    u32 item_id;
    u32 kind; /* dom_craft_item_kind */
    q16_16 quantity;
} dom_craft_item_req;

typedef struct dom_craft_item_stack {
    u32 item_id;
    u32 kind; /* dom_craft_item_kind */
    q16_16 quantity;
    q16_16 integrity;
    u32 flags; /* dom_craft_item_flags */
} dom_craft_item_stack;

typedef struct dom_craft_tool_requirement {
    u32 tool_id;
    q16_16 min_integrity;
} dom_craft_tool_requirement;

typedef struct dom_craft_tool_instance {
    u32 tool_id;
    q16_16 integrity;
    q16_16 wear;
} dom_craft_tool_instance;

typedef struct dom_craft_condition_range {
    q16_16 min;
    q16_16 max;
} dom_craft_condition_range;

typedef struct dom_craft_conditions {
    q16_16 temperature;
    q16_16 humidity;
    u32 environment_id;
} dom_craft_conditions;

typedef struct dom_craft_recipe_spec {
    u32 recipe_id;
    u32 input_count;
    dom_craft_item_req inputs[DOM_CRAFT_MAX_INPUTS];
    u32 output_count;
    dom_craft_item_req outputs[DOM_CRAFT_MAX_OUTPUTS];
    u32 byproduct_count;
    dom_craft_item_req byproducts[DOM_CRAFT_MAX_BYPRODUCTS];
    u32 tool_count;
    dom_craft_tool_requirement tools[DOM_CRAFT_MAX_TOOLS];
    dom_craft_condition_range temperature;
    dom_craft_condition_range humidity;
    u32 environment_id;
    q16_16 output_integrity;
    q16_16 recycle_loss;
    q16_16 tool_wear;
    u32 failure_mode; /* dom_craft_failure_mode */
    u32 flags; /* dom_craft_recipe_flags */
    u32 maturity_tag;
} dom_craft_recipe_spec;

typedef struct dom_craft_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    u32 craft_cost_base;
    u32 craft_cost_per_input;
    u32 craft_cost_per_output;
    u32 craft_cost_per_tool;
    u32 inventory_capacity;
    u32 tool_capacity;
    u32 law_allow_crafting;
    u32 metalaw_allow_crafting;
    u32 recipe_count;
    dom_craft_recipe_spec recipes[DOM_CRAFT_MAX_RECIPES];
} dom_craft_surface_desc;

typedef struct dom_craft_result {
    u32 ok;
    u32 refusal_reason; /* dom_domain_refusal_reason */
    u32 flags; /* dom_craft_result_flags */
    u32 recipe_id;
    u32 inputs_consumed;
    u32 outputs_produced;
    u32 byproducts_produced;
    u32 tool_damage;
    u32 inventory_count;
    u32 tool_count;
    u32 process_id;
    u32 event_id;
} dom_craft_result;

typedef struct dom_craft_domain {
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_craft_surface_desc surface;
    dom_craft_item_stack inventory[DOM_CRAFT_MAX_INVENTORY];
    u32 inventory_count;
    dom_craft_tool_instance tools[DOM_CRAFT_MAX_TOOLS];
    u32 tool_count;
} dom_craft_domain;

void dom_craft_surface_desc_init(dom_craft_surface_desc* desc);
void dom_craft_domain_init(dom_craft_domain* domain,
                           const dom_craft_surface_desc* desc);
void dom_craft_domain_free(dom_craft_domain* domain);
void dom_craft_domain_set_state(dom_craft_domain* domain,
                                u32 existence_state,
                                u32 archival_state);
void dom_craft_domain_set_policy(dom_craft_domain* domain,
                                 const dom_domain_policy* policy);

int dom_craft_execute(dom_craft_domain* domain,
                      u32 recipe_index,
                      const dom_craft_conditions* conditions,
                      u64 tick,
                      dom_domain_budget* budget,
                      dom_craft_result* out_result);

u32 dom_craft_inventory_count(const dom_craft_domain* domain);
const dom_craft_item_stack* dom_craft_inventory_at(const dom_craft_domain* domain, u32 index);
u32 dom_craft_tool_count(const dom_craft_domain* domain);
const dom_craft_tool_instance* dom_craft_tool_at(const dom_craft_domain* domain, u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_CRAFTING_FIELDS_H */
