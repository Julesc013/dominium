/*
FILE: tools/crafting/crafting_cli.cpp
MODULE: Dominium
PURPOSE: Crafting fixture CLI for deterministic craft/disassembly checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"
#include "domino/world/crafting_fields.h"

#define CRAFTING_FIXTURE_HEADER "DOMINIUM_CRAFTING_FIXTURE_V1"

#define CRAFTING_VALIDATE_HEADER "DOMINIUM_CRAFTING_VALIDATE_V1"
#define CRAFTING_INSPECT_HEADER "DOMINIUM_CRAFTING_INSPECT_V1"
#define CRAFTING_EXECUTE_HEADER "DOMINIUM_CRAFTING_EXECUTE_V1"
#define CRAFTING_CORE_SAMPLE_HEADER "DOMINIUM_CRAFTING_CORE_SAMPLE_V1"

#define CRAFTING_PROVIDER_CHAIN "materials->tools->conditions->crafting"

#define CRAFTING_LINE_MAX 512u

typedef struct crafting_fixture {
    char fixture_id[96];
    dom_craft_surface_desc desc;
    dom_domain_policy policy;
    u32 policy_set;
    dom_craft_item_stack inventory[DOM_CRAFT_MAX_INVENTORY];
    u32 inventory_count;
    dom_craft_tool_instance tools[DOM_CRAFT_MAX_TOOLS];
    u32 tool_count;
    char recipe_ids[DOM_CRAFT_MAX_RECIPES][64];
} crafting_fixture;

static char* crafting_trim(char* text)
{
    char* end;
    while (text && *text && isspace((unsigned char)*text)) {
        ++text;
    }
    if (!text || !*text) {
        return text;
    }
    end = text + strlen(text);
    while (end > text && isspace((unsigned char)end[-1])) {
        --end;
    }
    *end = '\0';
    return text;
}

static int crafting_parse_u32(const char* text, u32* out_value)
{
    char* end = 0;
    unsigned long value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtoul(text, &end, 0);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = (u32)value;
    return 1;
}

static int crafting_parse_u64(const char* text, u64* out_value)
{
    char* end = 0;
    unsigned long long value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtoull(text, &end, 0);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = (u64)value;
    return 1;
}

static int crafting_parse_q16(const char* text, q16_16* out_value)
{
    char* end = 0;
    double value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtod(text, &end);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = d_q16_16_from_double(value);
    return 1;
}

static int crafting_parse_kind(const char* text, u32* out_kind)
{
    if (!text || !out_kind) {
        return 0;
    }
    if (strcmp(text, "material") == 0) {
        *out_kind = DOM_CRAFT_ITEM_MATERIAL;
        return 1;
    }
    if (strcmp(text, "part") == 0) {
        *out_kind = DOM_CRAFT_ITEM_PART;
        return 1;
    }
    if (strcmp(text, "assembly") == 0) {
        *out_kind = DOM_CRAFT_ITEM_ASSEMBLY;
        return 1;
    }
    if (strcmp(text, "tool") == 0) {
        *out_kind = DOM_CRAFT_ITEM_TOOL;
        return 1;
    }
    return crafting_parse_u32(text, out_kind);
}

static u32 crafting_parse_failure_mode(const char* text)
{
    if (!text) {
        return DOM_CRAFT_FAILURE_REFUSE;
    }
    if (strcmp(text, "refuse") == 0) return DOM_CRAFT_FAILURE_REFUSE;
    if (strcmp(text, "waste") == 0) return DOM_CRAFT_FAILURE_WASTE;
    if (strcmp(text, "damage") == 0) return DOM_CRAFT_FAILURE_DAMAGE;
    return DOM_CRAFT_FAILURE_REFUSE;
}

static int crafting_parse_flags(const char* text, u32* out_flags)
{
    char buffer[CRAFTING_LINE_MAX];
    char* token;
    char* next;
    u32 flags = 0u;
    if (!text || !out_flags) {
        return 0;
    }
    if (strcmp(text, "none") == 0) {
        *out_flags = 0u;
        return 1;
    }
    strncpy(buffer, text, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    token = strtok(buffer, "|,");
    while (token) {
        token = crafting_trim(token);
        if (strcmp(token, "disassemble") == 0) {
            flags |= DOM_CRAFT_RECIPE_DISASSEMBLY;
        } else if (strcmp(token, "require_temp") == 0) {
            flags |= DOM_CRAFT_RECIPE_REQUIRE_TEMP;
        } else if (strcmp(token, "require_humidity") == 0) {
            flags |= DOM_CRAFT_RECIPE_REQUIRE_HUMIDITY;
        } else if (strcmp(token, "require_environment") == 0) {
            flags |= DOM_CRAFT_RECIPE_REQUIRE_ENVIRONMENT;
        }
        next = strtok(NULL, "|,");
        token = next;
    }
    *out_flags = flags;
    return 1;
}

static int crafting_parse_indexed_key(const char* key,
                                      const char* prefix,
                                      u32* out_index,
                                      const char** out_suffix)
{
    size_t len;
    char* end = 0;
    unsigned long idx;
    if (!key || !prefix || !out_index || !out_suffix) {
        return 0;
    }
    len = strlen(prefix);
    if (strncmp(key, prefix, len) != 0) {
        return 0;
    }
    idx = strtoul(key + len, &end, 10);
    if (!end || end == key + len || *end != '_') {
        return 0;
    }
    *out_index = (u32)idx;
    *out_suffix = end + 1;
    return 1;
}

static void crafting_fixture_init(crafting_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_craft_surface_desc_init(&fixture->desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->policy_set = 0u;
    fixture->inventory_count = 0u;
    fixture->tool_count = 0u;
    strncpy(fixture->fixture_id, "crafting.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
}

static int crafting_fixture_apply_recipe_item(dom_craft_item_req* items,
                                              u32* count,
                                              u32 max_count,
                                              u32 index,
                                              const char* suffix,
                                              const char* value)
{
    if (!items || !count || !suffix || !value) {
        return 0;
    }
    if (index >= max_count) {
        return 0;
    }
    if (*count <= index) {
        *count = index + 1u;
    }
    if (strcmp(suffix, "id") == 0) {
        items[index].item_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "kind") == 0) {
        return crafting_parse_kind(value, &items[index].kind);
    }
    if (strcmp(suffix, "qty") == 0 || strcmp(suffix, "quantity") == 0) {
        return crafting_parse_q16(value, &items[index].quantity);
    }
    return 0;
}

static int crafting_fixture_apply_recipe(crafting_fixture* fixture,
                                         u32 recipe_index,
                                         const char* suffix,
                                         const char* value)
{
    dom_craft_recipe_spec* recipe;
    u32 index = 0u;
    const char* inner = 0;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (recipe_index >= DOM_CRAFT_MAX_RECIPES) {
        return 0;
    }
    if (fixture->desc.recipe_count <= recipe_index) {
        fixture->desc.recipe_count = recipe_index + 1u;
    }
    recipe = &fixture->desc.recipes[recipe_index];

    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->recipe_ids[recipe_index], value,
                sizeof(fixture->recipe_ids[recipe_index]) - 1);
        fixture->recipe_ids[recipe_index][sizeof(fixture->recipe_ids[recipe_index]) - 1] = '\0';
        recipe->recipe_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return crafting_parse_flags(value, &recipe->flags);
    }
    if (strcmp(suffix, "failure_mode") == 0) {
        recipe->failure_mode = crafting_parse_failure_mode(value);
        return 1;
    }
    if (strcmp(suffix, "output_integrity") == 0) {
        return crafting_parse_q16(value, &recipe->output_integrity);
    }
    if (strcmp(suffix, "recycle_loss") == 0) {
        return crafting_parse_q16(value, &recipe->recycle_loss);
    }
    if (strcmp(suffix, "tool_wear") == 0) {
        return crafting_parse_q16(value, &recipe->tool_wear);
    }
    if (strcmp(suffix, "temp_min") == 0) {
        recipe->flags |= DOM_CRAFT_RECIPE_REQUIRE_TEMP;
        return crafting_parse_q16(value, &recipe->temperature.min);
    }
    if (strcmp(suffix, "temp_max") == 0) {
        recipe->flags |= DOM_CRAFT_RECIPE_REQUIRE_TEMP;
        return crafting_parse_q16(value, &recipe->temperature.max);
    }
    if (strcmp(suffix, "humidity_min") == 0) {
        recipe->flags |= DOM_CRAFT_RECIPE_REQUIRE_HUMIDITY;
        return crafting_parse_q16(value, &recipe->humidity.min);
    }
    if (strcmp(suffix, "humidity_max") == 0) {
        recipe->flags |= DOM_CRAFT_RECIPE_REQUIRE_HUMIDITY;
        return crafting_parse_q16(value, &recipe->humidity.max);
    }
    if (strcmp(suffix, "environment") == 0) {
        recipe->flags |= DOM_CRAFT_RECIPE_REQUIRE_ENVIRONMENT;
        recipe->environment_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "maturity") == 0) {
        recipe->maturity_tag = d_rng_hash_str32(value);
        return 1;
    }

    if (crafting_parse_indexed_key(suffix, "input", &index, &inner)) {
        return crafting_fixture_apply_recipe_item(recipe->inputs, &recipe->input_count,
                                                  DOM_CRAFT_MAX_INPUTS, index, inner, value);
    }
    if (crafting_parse_indexed_key(suffix, "output", &index, &inner)) {
        return crafting_fixture_apply_recipe_item(recipe->outputs, &recipe->output_count,
                                                  DOM_CRAFT_MAX_OUTPUTS, index, inner, value);
    }
    if (crafting_parse_indexed_key(suffix, "byproduct", &index, &inner)) {
        return crafting_fixture_apply_recipe_item(recipe->byproducts, &recipe->byproduct_count,
                                                  DOM_CRAFT_MAX_BYPRODUCTS, index, inner, value);
    }
    if (crafting_parse_indexed_key(suffix, "tool", &index, &inner)) {
        if (index >= DOM_CRAFT_MAX_TOOLS) {
            return 0;
        }
        if (recipe->tool_count <= index) {
            recipe->tool_count = index + 1u;
        }
        if (strcmp(inner, "id") == 0) {
            recipe->tools[index].tool_id = d_rng_hash_str32(value);
            return 1;
        }
        if (strcmp(inner, "min_integrity") == 0) {
            return crafting_parse_q16(value, &recipe->tools[index].min_integrity);
        }
    }
    return 0;
}

static int crafting_fixture_apply_inventory(crafting_fixture* fixture,
                                            u32 index,
                                            const char* suffix,
                                            const char* value)
{
    dom_craft_item_stack* stack;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_CRAFT_MAX_INVENTORY) {
        return 0;
    }
    if (fixture->inventory_count <= index) {
        fixture->inventory_count = index + 1u;
    }
    stack = &fixture->inventory[index];
    if (strcmp(suffix, "id") == 0) {
        stack->item_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "kind") == 0) {
        return crafting_parse_kind(value, &stack->kind);
    }
    if (strcmp(suffix, "qty") == 0 || strcmp(suffix, "quantity") == 0) {
        return crafting_parse_q16(value, &stack->quantity);
    }
    if (strcmp(suffix, "integrity") == 0) {
        return crafting_parse_q16(value, &stack->integrity);
    }
    if (strcmp(suffix, "flags") == 0) {
        return crafting_parse_u32(value, &stack->flags);
    }
    return 0;
}

static int crafting_fixture_apply_tool(crafting_fixture* fixture,
                                       u32 index,
                                       const char* suffix,
                                       const char* value)
{
    dom_craft_tool_instance* tool;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_CRAFT_MAX_TOOLS) {
        return 0;
    }
    if (fixture->tool_count <= index) {
        fixture->tool_count = index + 1u;
    }
    tool = &fixture->tools[index];
    if (strcmp(suffix, "id") == 0) {
        tool->tool_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "integrity") == 0) {
        return crafting_parse_q16(value, &tool->integrity);
    }
    if (strcmp(suffix, "wear") == 0) {
        return crafting_parse_q16(value, &tool->wear);
    }
    return 0;
}

static int crafting_fixture_apply(crafting_fixture* fixture, const char* key, const char* value)
{
    u32 index = 0u;
    const char* suffix = 0;
    if (!fixture || !key || !value) {
        return 0;
    }
    if (strcmp(key, "fixture_id") == 0) {
        strncpy(fixture->fixture_id, value, sizeof(fixture->fixture_id) - 1);
        fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
        return 1;
    }
    if (strcmp(key, "world_seed") == 0) {
        return crafting_parse_u64(value, &fixture->desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return crafting_parse_u64(value, &fixture->desc.domain_id);
    }
    if (strcmp(key, "craft_cost_base") == 0) {
        return crafting_parse_u32(value, &fixture->desc.craft_cost_base);
    }
    if (strcmp(key, "craft_cost_per_input") == 0) {
        return crafting_parse_u32(value, &fixture->desc.craft_cost_per_input);
    }
    if (strcmp(key, "craft_cost_per_output") == 0) {
        return crafting_parse_u32(value, &fixture->desc.craft_cost_per_output);
    }
    if (strcmp(key, "craft_cost_per_tool") == 0) {
        return crafting_parse_u32(value, &fixture->desc.craft_cost_per_tool);
    }
    if (strcmp(key, "inventory_capacity") == 0) {
        return crafting_parse_u32(value, &fixture->desc.inventory_capacity);
    }
    if (strcmp(key, "tool_capacity") == 0) {
        return crafting_parse_u32(value, &fixture->desc.tool_capacity);
    }
    if (strcmp(key, "law_allow_crafting") == 0) {
        return crafting_parse_u32(value, &fixture->desc.law_allow_crafting);
    }
    if (strcmp(key, "metalaw_allow_crafting") == 0) {
        return crafting_parse_u32(value, &fixture->desc.metalaw_allow_crafting);
    }

    if (crafting_parse_indexed_key(key, "recipe", &index, &suffix)) {
        return crafting_fixture_apply_recipe(fixture, index, suffix, value);
    }
    if (crafting_parse_indexed_key(key, "inv", &index, &suffix)) {
        return crafting_fixture_apply_inventory(fixture, index, suffix, value);
    }
    if (crafting_parse_indexed_key(key, "tool", &index, &suffix)) {
        return crafting_fixture_apply_tool(fixture, index, suffix, value);
    }
    return 0;
}

static int crafting_fixture_load(const char* path, crafting_fixture* out_fixture)
{
    FILE* file;
    char line[CRAFTING_LINE_MAX];
    int header_ok = 0;
    crafting_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    crafting_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = crafting_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, CRAFTING_FIXTURE_HEADER) != 0) {
                fclose(file);
                return 0;
            }
            header_ok = 1;
            continue;
        }
        eq = strchr(text, '=');
        if (!eq) {
            continue;
        }
        *eq++ = '\0';
        crafting_fixture_apply(&fixture, crafting_trim(text), crafting_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static void crafting_domain_init_from_fixture(const crafting_fixture* fixture,
                                              dom_craft_domain* out_domain)
{
    dom_craft_domain_init(out_domain, &fixture->desc);
    out_domain->inventory_count = fixture->inventory_count;
    out_domain->tool_count = fixture->tool_count;
    for (u32 i = 0u; i < fixture->inventory_count; ++i) {
        out_domain->inventory[i] = fixture->inventory[i];
    }
    for (u32 i = 0u; i < fixture->tool_count; ++i) {
        out_domain->tools[i] = fixture->tools[i];
    }
    if (fixture->policy_set) {
        dom_craft_domain_set_policy(out_domain, &fixture->policy);
    }
}

static const char* crafting_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 crafting_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = crafting_find_arg(argc, argv, key);
    u32 out = fallback;
    if (!value) {
        return fallback;
    }
    if (!crafting_parse_u32(value, &out)) {
        return fallback;
    }
    return out;
}

static u64 crafting_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* value = crafting_find_arg(argc, argv, key);
    u64 out = fallback;
    if (!value) {
        return fallback;
    }
    if (!crafting_parse_u64(value, &out)) {
        return fallback;
    }
    return out;
}

static int crafting_find_arg_q16(int argc, char** argv, const char* key, q16_16* out_value)
{
    const char* value = crafting_find_arg(argc, argv, key);
    if (!value || !out_value) {
        return 0;
    }
    return crafting_parse_q16(value, out_value);
}

static int crafting_find_recipe_index(const crafting_fixture* fixture, const char* recipe_id)
{
    u32 target = 0;
    if (!fixture || fixture->desc.recipe_count == 0u) {
        return -1;
    }
    if (!recipe_id) {
        return 0;
    }
    target = d_rng_hash_str32(recipe_id);
    for (u32 i = 0u; i < fixture->desc.recipe_count; ++i) {
        if (fixture->desc.recipes[i].recipe_id == target) {
            return (int)i;
        }
    }
    return -1;
}

static u64 crafting_hash_u64(u64 h, u64 v)
{
    h ^= v;
    h *= 1099511628211ULL;
    return h;
}

static u64 crafting_hash_u32(u64 h, u32 v)
{
    return crafting_hash_u64(h, (u64)v);
}

static u64 crafting_hash_i32(u64 h, i32 v)
{
    return crafting_hash_u64(h, (u64)(u32)v);
}

static int crafting_run_validate(const crafting_fixture* fixture)
{
    if (!fixture) {
        return 1;
    }
    if (fixture->desc.recipe_count == 0u) {
        fprintf(stderr, "crafting: no recipes defined\n");
        return 1;
    }
    printf("%s\n", CRAFTING_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CRAFTING_PROVIDER_CHAIN);
    printf("recipe_count=%u\n", (unsigned int)fixture->desc.recipe_count);
    printf("inventory_count=%u\n", (unsigned int)fixture->inventory_count);
    printf("tool_count=%u\n", (unsigned int)fixture->tool_count);
    return 0;
}

static int crafting_run_inspect(const crafting_fixture* fixture)
{
    dom_craft_domain domain;
    crafting_domain_init_from_fixture(fixture, &domain);

    printf("%s\n", CRAFTING_INSPECT_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CRAFTING_PROVIDER_CHAIN);
    printf("recipe_count=%u\n", (unsigned int)domain.surface.recipe_count);
    printf("inventory_count=%u\n", (unsigned int)domain.inventory_count);
    for (u32 i = 0u; i < domain.inventory_count; ++i) {
        const dom_craft_item_stack* stack = &domain.inventory[i];
        printf("inventory.%u.id=%u\n", (unsigned int)i, (unsigned int)stack->item_id);
        printf("inventory.%u.kind=%u\n", (unsigned int)i, (unsigned int)stack->kind);
        printf("inventory.%u.qty_q16=%d\n", (unsigned int)i, (int)stack->quantity);
        printf("inventory.%u.integrity_q16=%d\n", (unsigned int)i, (int)stack->integrity);
        printf("inventory.%u.flags=%u\n", (unsigned int)i, (unsigned int)stack->flags);
    }
    printf("tool_count=%u\n", (unsigned int)domain.tool_count);
    for (u32 i = 0u; i < domain.tool_count; ++i) {
        const dom_craft_tool_instance* tool = &domain.tools[i];
        printf("tool.%u.id=%u\n", (unsigned int)i, (unsigned int)tool->tool_id);
        printf("tool.%u.integrity_q16=%d\n", (unsigned int)i, (int)tool->integrity);
    }

    dom_craft_domain_free(&domain);
    return 0;
}

static int crafting_run_execute(const crafting_fixture* fixture,
                                int recipe_index,
                                const dom_craft_conditions* conditions,
                                u64 tick,
                                u32 budget_max)
{
    dom_craft_domain domain;
    dom_domain_budget budget;
    dom_craft_result result;

    crafting_domain_init_from_fixture(fixture, &domain);
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_craft_execute(&domain, (u32)recipe_index, conditions, tick, &budget, &result);

    printf("%s\n", CRAFTING_EXECUTE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CRAFTING_PROVIDER_CHAIN);
    printf("recipe_index=%u\n", (unsigned int)recipe_index);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("inputs_consumed=%u\n", (unsigned int)result.inputs_consumed);
    printf("outputs_produced=%u\n", (unsigned int)result.outputs_produced);
    printf("byproducts_produced=%u\n", (unsigned int)result.byproducts_produced);
    printf("tool_damage=%u\n", (unsigned int)result.tool_damage);
    printf("inventory_count=%u\n", (unsigned int)domain.inventory_count);
    printf("tool_count=%u\n", (unsigned int)domain.tool_count);
    printf("process_id=%u\n", (unsigned int)result.process_id);
    printf("event_id=%u\n", (unsigned int)result.event_id);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);

    dom_craft_domain_free(&domain);
    return 0;
}

static u64 crafting_core_sample_hash(const crafting_fixture* fixture,
                                     int recipe_index,
                                     const dom_craft_conditions* conditions,
                                     u64 tick_start,
                                     u32 steps,
                                     u32 budget_max,
                                     u32 inactive,
                                     u32* out_failures,
                                     u32* out_cost_max,
                                     int* out_ok)
{
    dom_craft_domain domain;
    dom_craft_domain* inactive_domains = (dom_craft_domain*)0;
    u64 hash = 14695981039346656037ULL;
    u32 failures = 0u;
    u32 cost_max = 0u;
    if (out_ok) {
        *out_ok = 0;
    }
    if (!fixture || recipe_index < 0) {
        return 0;
    }

    crafting_domain_init_from_fixture(fixture, &domain);

    if (inactive > 0u) {
        inactive_domains = (dom_craft_domain*)malloc(sizeof(dom_craft_domain) * inactive);
        if (!inactive_domains) {
            dom_craft_domain_free(&domain);
            return 0;
        }
        for (u32 i = 0u; i < inactive; ++i) {
            crafting_domain_init_from_fixture(fixture, &inactive_domains[i]);
            dom_craft_domain_set_state(&inactive_domains[i], DOM_DOMAIN_EXISTENCE_NONEXISTENT,
                                       DOM_DOMAIN_ARCHIVAL_LIVE);
        }
    }

    if (steps == 0u) {
        steps = 1u;
    }
    for (u32 i = 0u; i < steps; ++i) {
        dom_domain_budget budget;
        dom_craft_result result;
        dom_domain_budget_init(&budget, budget_max);
        (void)dom_craft_execute(&domain, (u32)recipe_index, conditions, tick_start + i, &budget, &result);
        if (!result.ok && result.refusal_reason != DOM_DOMAIN_REFUSE_NONE) {
            failures += 1u;
        }
        if (budget.used_units > cost_max) {
            cost_max = budget.used_units;
        }
        hash = crafting_hash_u32(hash, result.ok);
        hash = crafting_hash_u32(hash, result.flags);
        hash = crafting_hash_u32(hash, result.inputs_consumed);
        hash = crafting_hash_u32(hash, result.outputs_produced);
        hash = crafting_hash_u32(hash, result.byproducts_produced);
        hash = crafting_hash_u32(hash, domain.inventory_count);
        for (u32 s = 0u; s < domain.inventory_count; ++s) {
            const dom_craft_item_stack* stack = &domain.inventory[s];
            hash = crafting_hash_u32(hash, stack->item_id);
            hash = crafting_hash_u32(hash, stack->kind);
            hash = crafting_hash_i32(hash, stack->quantity);
            hash = crafting_hash_i32(hash, stack->integrity);
        }
        for (u32 t = 0u; t < domain.tool_count; ++t) {
            const dom_craft_tool_instance* tool = &domain.tools[t];
            hash = crafting_hash_u32(hash, tool->tool_id);
            hash = crafting_hash_i32(hash, tool->integrity);
        }
    }

    dom_craft_domain_free(&domain);
    if (inactive_domains) {
        for (u32 i = 0u; i < inactive; ++i) {
            dom_craft_domain_free(&inactive_domains[i]);
        }
        free(inactive_domains);
    }
    if (out_failures) {
        *out_failures = failures;
    }
    if (out_cost_max) {
        *out_cost_max = cost_max;
    }
    if (out_ok) {
        *out_ok = 1;
    }
    return hash;
}

static int crafting_run_core_sample(const crafting_fixture* fixture,
                                    int recipe_index,
                                    const dom_craft_conditions* conditions,
                                    u64 tick_start,
                                    u32 steps,
                                    u32 budget_max,
                                    u32 inactive)
{
    u32 failures = 0u;
    u32 cost_max = 0u;
    int ok = 0;
    u64 hash = crafting_core_sample_hash(fixture, recipe_index, conditions, tick_start, steps,
                                         budget_max, inactive, &failures, &cost_max, &ok);
    if (!ok) {
        return 1;
    }
    printf("%s\n", CRAFTING_CORE_SAMPLE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", CRAFTING_PROVIDER_CHAIN);
    printf("recipe_index=%u\n", (unsigned int)recipe_index);
    printf("steps=%u\n", (unsigned int)steps);
    printf("budget_max=%u\n", (unsigned int)budget_max);
    printf("failures=%u\n", (unsigned int)failures);
    printf("cost_step_max=%u\n", (unsigned int)cost_max);
    printf("sample_hash=%llu\n", (unsigned long long)hash);
    printf("inactive_domains=%u\n", (unsigned int)inactive);
    return 0;
}

static void crafting_usage(void)
{
    printf("dom_tool_crafting commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path>\n");
    printf("  execute --fixture <path> --recipe <id> [--temp T] [--humidity H] [--environment ENV] [--tick T] [--budget N]\n");
    printf("  core-sample --fixture <path> --recipe <id> [--temp T] [--humidity H] [--environment ENV] [--tick T] [--steps N] [--budget N] [--inactive N]\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        crafting_usage();
        return 2;
    }
    cmd = argv[1];

    {
        const char* fixture_path = crafting_find_arg(argc, argv, "--fixture");
        crafting_fixture fixture;
        if (!fixture_path || !crafting_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "crafting: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return crafting_run_validate(&fixture);
        }

        if (strcmp(cmd, "inspect") == 0) {
            return crafting_run_inspect(&fixture);
        }

        if (strcmp(cmd, "execute") == 0) {
            dom_craft_conditions conditions;
            q16_16 temp = d_q16_16_from_int(0);
            q16_16 humidity = d_q16_16_from_int(0);
            const char* recipe_id = crafting_find_arg(argc, argv, "--recipe");
            const char* env = crafting_find_arg(argc, argv, "--environment");
            int recipe_index = crafting_find_recipe_index(&fixture, recipe_id);
            u64 tick = crafting_find_arg_u64(argc, argv, "--tick", 0u);
            u32 budget_max = crafting_find_arg_u32(argc, argv, "--budget", 100u);
            if (recipe_index < 0) {
                fprintf(stderr, "crafting: missing or unknown --recipe\n");
                return 2;
            }
            if (!crafting_find_arg_q16(argc, argv, "--temp", &temp)) {
                temp = d_q16_16_from_int(0);
            }
            if (!crafting_find_arg_q16(argc, argv, "--humidity", &humidity)) {
                humidity = d_q16_16_from_int(0);
            }
            conditions.temperature = temp;
            conditions.humidity = humidity;
            conditions.environment_id = env ? d_rng_hash_str32(env) : 0u;
            return crafting_run_execute(&fixture, recipe_index, &conditions, tick, budget_max);
        }

        if (strcmp(cmd, "core-sample") == 0) {
            dom_craft_conditions conditions;
            q16_16 temp = d_q16_16_from_int(0);
            q16_16 humidity = d_q16_16_from_int(0);
            const char* recipe_id = crafting_find_arg(argc, argv, "--recipe");
            const char* env = crafting_find_arg(argc, argv, "--environment");
            int recipe_index = crafting_find_recipe_index(&fixture, recipe_id);
            u64 tick = crafting_find_arg_u64(argc, argv, "--tick", 0u);
            u32 steps = crafting_find_arg_u32(argc, argv, "--steps", 4u);
            u32 budget_max = crafting_find_arg_u32(argc, argv, "--budget", 100u);
            u32 inactive = crafting_find_arg_u32(argc, argv, "--inactive", 0u);
            if (recipe_index < 0) {
                fprintf(stderr, "crafting: missing or unknown --recipe\n");
                return 2;
            }
            if (!crafting_find_arg_q16(argc, argv, "--temp", &temp)) {
                temp = d_q16_16_from_int(0);
            }
            if (!crafting_find_arg_q16(argc, argv, "--humidity", &humidity)) {
                humidity = d_q16_16_from_int(0);
            }
            conditions.temperature = temp;
            conditions.humidity = humidity;
            conditions.environment_id = env ? d_rng_hash_str32(env) : 0u;
            return crafting_run_core_sample(&fixture, recipe_index, &conditions, tick,
                                            steps, budget_max, inactive);
        }
    }

    crafting_usage();
    return 2;
}
