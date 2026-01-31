/*
FILE: tools/autonomy/autonomy_cli.cpp
MODULE: Dominium
PURPOSE: AI autonomy fixture CLI for deterministic checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/rng_model.h"
#include "domino/world/autonomy_fields.h"

#define AUTONOMY_FIXTURE_HEADER "DOMINIUM_AUTONOMY_FIXTURE_V1"

#define AUTONOMY_VALIDATE_HEADER "DOMINIUM_AUTONOMY_VALIDATE_V1"
#define AUTONOMY_INSPECT_HEADER "DOMINIUM_AUTONOMY_INSPECT_V1"
#define AUTONOMY_RESOLVE_HEADER "DOMINIUM_AUTONOMY_RESOLVE_V1"
#define AUTONOMY_COLLAPSE_HEADER "DOMINIUM_AUTONOMY_COLLAPSE_V1"

#define AUTONOMY_PROVIDER_CHAIN "goals->delegations->budgets->plans->events"

#define AUTONOMY_LINE_MAX 512u

typedef struct autonomy_fixture {
    char fixture_id[96];
    dom_autonomy_surface_desc autonomy_desc;
    dom_domain_policy policy;
    u32 policy_set;
    char goal_names[DOM_AUTONOMY_MAX_GOALS][64];
    char delegation_names[DOM_AUTONOMY_MAX_DELEGATIONS][64];
    char budget_names[DOM_AUTONOMY_MAX_BUDGETS][64];
    char plan_names[DOM_AUTONOMY_MAX_PLANS][64];
    char event_names[DOM_AUTONOMY_MAX_EVENTS][64];
    char region_names[DOM_AUTONOMY_MAX_REGIONS][64];
    u32 region_ids[DOM_AUTONOMY_MAX_REGIONS];
    u32 region_count;
} autonomy_fixture;

static u64 autonomy_hash_u64(u64 h, u64 v)
{
    unsigned char bytes[8];
    bytes[0] = (unsigned char)((v >> 56) & 0xFFu);
    bytes[1] = (unsigned char)((v >> 48) & 0xFFu);
    bytes[2] = (unsigned char)((v >> 40) & 0xFFu);
    bytes[3] = (unsigned char)((v >> 32) & 0xFFu);
    bytes[4] = (unsigned char)((v >> 24) & 0xFFu);
    bytes[5] = (unsigned char)((v >> 16) & 0xFFu);
    bytes[6] = (unsigned char)((v >> 8) & 0xFFu);
    bytes[7] = (unsigned char)(v & 0xFFu);
    for (u32 i = 0u; i < 8u; ++i) {
        h ^= (u64)bytes[i];
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 autonomy_hash_u32(u64 h, u32 v)
{
    return autonomy_hash_u64(h, (u64)v);
}

static u64 autonomy_hash_q16(u64 h, q16_16 v)
{
    return autonomy_hash_u64(h, (u64)(u32)v);
}

static u64 autonomy_hash_q48(u64 h, q48_16 v)
{
    return autonomy_hash_u64(h, (u64)v);
}

static char* autonomy_trim(char* text)
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

static int autonomy_parse_u32(const char* text, u32* out_value)
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

static int autonomy_parse_u64(const char* text, u64* out_value)
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

static int autonomy_parse_q16(const char* text, q16_16* out_value)
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

static int autonomy_parse_q48(const char* text, q48_16* out_value)
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
    *out_value = d_q48_16_from_double(value);
    return 1;
}

static int autonomy_parse_indexed_key(const char* key,
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

static u32 autonomy_parse_ref(const char* text)
{
    u32 value = 0u;
    if (!text) {
        return 0u;
    }
    if (autonomy_parse_u32(text, &value)) {
        return value;
    }
    return d_rng_hash_str32(text);
}

static u32 autonomy_process_from_text(const char* text)
{
    if (!text) {
        return DOM_AUTONOMY_PROCESS_UNSET;
    }
    if (strcmp(text, "plan") == 0) return DOM_AUTONOMY_PROCESS_PLAN;
    if (strcmp(text, "execute") == 0) return DOM_AUTONOMY_PROCESS_EXECUTE;
    if (strcmp(text, "revise") == 0) return DOM_AUTONOMY_PROCESS_REVISE;
    if (strcmp(text, "revoke") == 0) return DOM_AUTONOMY_PROCESS_REVOKE;
    if (strcmp(text, "expire") == 0) return DOM_AUTONOMY_PROCESS_EXPIRE;
    if (strcmp(text, "fail") == 0) return DOM_AUTONOMY_PROCESS_FAIL;
    if (strcmp(text, "complete") == 0) return DOM_AUTONOMY_PROCESS_COMPLETE;
    return DOM_AUTONOMY_PROCESS_UNSET;
}

static u32 autonomy_process_parse(const char* text)
{
    u32 value = autonomy_process_from_text(text);
    if (value != DOM_AUTONOMY_PROCESS_UNSET) {
        return value;
    }
    if (autonomy_parse_u32(text, &value)) {
        return value;
    }
    return DOM_AUTONOMY_PROCESS_UNSET;
}

static u32 autonomy_process_id_from_text(const char* text)
{
    u32 value = autonomy_process_from_text(text);
    if (value != DOM_AUTONOMY_PROCESS_UNSET) {
        return value;
    }
    return autonomy_parse_ref(text);
}

static u32 autonomy_status_from_text(const char* text)
{
    if (!text) {
        return DOM_AUTONOMY_PLAN_UNSET;
    }
    if (strcmp(text, "proposed") == 0) return DOM_AUTONOMY_PLAN_PROPOSED;
    if (strcmp(text, "active") == 0) return DOM_AUTONOMY_PLAN_ACTIVE;
    if (strcmp(text, "failed") == 0) return DOM_AUTONOMY_PLAN_FAILED;
    if (strcmp(text, "completed") == 0) return DOM_AUTONOMY_PLAN_COMPLETED;
    if (strcmp(text, "revoked") == 0) return DOM_AUTONOMY_PLAN_REVOKED;
    return DOM_AUTONOMY_PLAN_UNSET;
}

static u32 autonomy_status_parse(const char* text)
{
    u32 value = autonomy_status_from_text(text);
    if (value != DOM_AUTONOMY_PLAN_UNSET) {
        return value;
    }
    if (autonomy_parse_u32(text, &value)) {
        return value;
    }
    return DOM_AUTONOMY_PLAN_UNSET;
}

static u32 autonomy_goal_flags_from_text(const char* text)
{
    char buffer[AUTONOMY_LINE_MAX];
    char* token;
    char* cur;
    u32 flags = 0u;
    if (!text || !*text) {
        return 0u;
    }
    if (autonomy_parse_u32(text, &flags)) {
        return flags;
    }
    strncpy(buffer, text, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    cur = buffer;
    while ((token = strtok(cur, ",|")) != 0) {
        token = autonomy_trim(token);
        if (strcmp(token, "unresolved") == 0) flags |= DOM_AUTONOMY_GOAL_UNRESOLVED;
        else if (strcmp(token, "collapsed") == 0) flags |= DOM_AUTONOMY_GOAL_COLLAPSED;
        else if (strcmp(token, "expired") == 0) flags |= DOM_AUTONOMY_GOAL_EXPIRED;
        cur = 0;
    }
    return flags;
}

static u32 autonomy_delegation_flags_from_text(const char* text)
{
    char buffer[AUTONOMY_LINE_MAX];
    char* token;
    char* cur;
    u32 flags = 0u;
    if (!text || !*text) {
        return 0u;
    }
    if (autonomy_parse_u32(text, &flags)) {
        return flags;
    }
    strncpy(buffer, text, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    cur = buffer;
    while ((token = strtok(cur, ",|")) != 0) {
        token = autonomy_trim(token);
        if (strcmp(token, "unresolved") == 0) flags |= DOM_AUTONOMY_DELEGATION_UNRESOLVED;
        else if (strcmp(token, "collapsed") == 0) flags |= DOM_AUTONOMY_DELEGATION_COLLAPSED;
        else if (strcmp(token, "revoked") == 0) flags |= DOM_AUTONOMY_DELEGATION_REVOKED;
        cur = 0;
    }
    return flags;
}

static u32 autonomy_budget_flags_from_text(const char* text)
{
    char buffer[AUTONOMY_LINE_MAX];
    char* token;
    char* cur;
    u32 flags = 0u;
    if (!text || !*text) {
        return 0u;
    }
    if (autonomy_parse_u32(text, &flags)) {
        return flags;
    }
    strncpy(buffer, text, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    cur = buffer;
    while ((token = strtok(cur, ",|")) != 0) {
        token = autonomy_trim(token);
        if (strcmp(token, "unresolved") == 0) flags |= DOM_AUTONOMY_BUDGET_UNRESOLVED;
        else if (strcmp(token, "collapsed") == 0) flags |= DOM_AUTONOMY_BUDGET_COLLAPSED;
        else if (strcmp(token, "exhausted") == 0) flags |= DOM_AUTONOMY_BUDGET_EXHAUSTED;
        cur = 0;
    }
    return flags;
}

static u32 autonomy_plan_flags_from_text(const char* text)
{
    char buffer[AUTONOMY_LINE_MAX];
    char* token;
    char* cur;
    u32 flags = 0u;
    if (!text || !*text) {
        return 0u;
    }
    if (autonomy_parse_u32(text, &flags)) {
        return flags;
    }
    strncpy(buffer, text, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    cur = buffer;
    while ((token = strtok(cur, ",|")) != 0) {
        token = autonomy_trim(token);
        if (strcmp(token, "unresolved") == 0) flags |= DOM_AUTONOMY_PLAN_UNRESOLVED;
        else if (strcmp(token, "collapsed") == 0) flags |= DOM_AUTONOMY_PLAN_COLLAPSED;
        else if (strcmp(token, "failed") == 0) flags |= DOM_AUTONOMY_PLAN_FAILED_FLAG;
        else if (strcmp(token, "completed") == 0) flags |= DOM_AUTONOMY_PLAN_COMPLETED_FLAG;
        else if (strcmp(token, "revoked") == 0) flags |= DOM_AUTONOMY_PLAN_REVOKED_FLAG;
        cur = 0;
    }
    return flags;
}

static u32 autonomy_event_flags_from_text(const char* text)
{
    char buffer[AUTONOMY_LINE_MAX];
    char* token;
    char* cur;
    u32 flags = 0u;
    if (!text || !*text) {
        return 0u;
    }
    if (autonomy_parse_u32(text, &flags)) {
        return flags;
    }
    strncpy(buffer, text, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    cur = buffer;
    while ((token = strtok(cur, ",|")) != 0) {
        token = autonomy_trim(token);
        if (strcmp(token, "unresolved") == 0) flags |= DOM_AUTONOMY_EVENT_UNRESOLVED;
        else if (strcmp(token, "applied") == 0) flags |= DOM_AUTONOMY_EVENT_APPLIED;
        else if (strcmp(token, "failed") == 0) flags |= DOM_AUTONOMY_EVENT_FAILED;
        cur = 0;
    }
    return flags;
}

static int autonomy_ratio_valid(q16_16 value)
{
    if (value < 0) {
        return 0;
    }
    if (value > DOM_AUTONOMY_RATIO_ONE_Q16) {
        return 0;
    }
    return 1;
}

static void autonomy_fixture_init(autonomy_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_autonomy_surface_desc_init(&fixture->autonomy_desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->policy_set = 0u;
    fixture->region_count = 0u;
    strncpy(fixture->fixture_id, "autonomy.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
}

static void autonomy_fixture_register_region(autonomy_fixture* fixture, const char* name, u32 id)
{
    if (!fixture || !name || !*name || id == 0u) {
        return;
    }
    for (u32 i = 0u; i < fixture->region_count; ++i) {
        if (fixture->region_ids[i] == id) {
            return;
        }
    }
    if (fixture->region_count >= DOM_AUTONOMY_MAX_REGIONS) {
        return;
    }
    fixture->region_ids[fixture->region_count] = id;
    strncpy(fixture->region_names[fixture->region_count], name,
            sizeof(fixture->region_names[fixture->region_count]) - 1);
    fixture->region_names[fixture->region_count][sizeof(fixture->region_names[fixture->region_count]) - 1] = '\0';
    fixture->region_count += 1u;
}

static int autonomy_fixture_apply_goal(autonomy_fixture* fixture,
                                       u32 index,
                                       const char* suffix,
                                       const char* value)
{
    dom_autonomy_goal_desc* goal;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_AUTONOMY_MAX_GOALS) {
        return 0;
    }
    if (fixture->autonomy_desc.goal_count <= index) {
        fixture->autonomy_desc.goal_count = index + 1u;
    }
    goal = &fixture->autonomy_desc.goals[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->goal_names[index], value, sizeof(fixture->goal_names[index]) - 1);
        fixture->goal_names[index][sizeof(fixture->goal_names[index]) - 1] = '\0';
        goal->goal_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "objective") == 0) {
        goal->objective_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "success") == 0) {
        goal->success_condition_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "constraint") == 0) {
        goal->constraint_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "priority") == 0) {
        return autonomy_parse_q16(value, &goal->priority);
    }
    if (strcmp(suffix, "expiry") == 0 || strcmp(suffix, "expiry_tick") == 0) {
        return autonomy_parse_u64(value, &goal->expiry_tick);
    }
    if (strcmp(suffix, "delegator") == 0) {
        goal->delegator_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        goal->provenance_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        goal->region_id = region_id;
        autonomy_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        goal->flags = autonomy_goal_flags_from_text(value);
        return 1;
    }
    return 0;
}

static int autonomy_fixture_apply_delegation(autonomy_fixture* fixture,
                                             u32 index,
                                             const char* suffix,
                                             const char* value)
{
    dom_autonomy_delegation_desc* delegation;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_AUTONOMY_MAX_DELEGATIONS) {
        return 0;
    }
    if (fixture->autonomy_desc.delegation_count <= index) {
        fixture->autonomy_desc.delegation_count = index + 1u;
    }
    delegation = &fixture->autonomy_desc.delegations[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->delegation_names[index], value,
                sizeof(fixture->delegation_names[index]) - 1);
        fixture->delegation_names[index][sizeof(fixture->delegation_names[index]) - 1] = '\0';
        delegation->delegation_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "delegator") == 0) {
        delegation->delegator_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "delegate") == 0) {
        delegation->delegate_agent_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "allowed_count") == 0) {
        return autonomy_parse_u32(value, &delegation->allowed_process_count);
    }
    if (strncmp(suffix, "allowed_", 8) == 0) {
        u32 allowed_index = 0u;
        if (autonomy_parse_u32(suffix + 8, &allowed_index) &&
            allowed_index < DOM_AUTONOMY_MAX_PROCESS_REFS) {
            delegation->allowed_process_ids[allowed_index] = autonomy_process_id_from_text(value);
            if (delegation->allowed_process_count <= allowed_index) {
                delegation->allowed_process_count = allowed_index + 1u;
            }
            return 1;
        }
    }
    if (strcmp(suffix, "time_budget") == 0) {
        return autonomy_parse_u64(value, &delegation->time_budget_ticks);
    }
    if (strcmp(suffix, "energy_budget") == 0) {
        return autonomy_parse_q48(value, &delegation->energy_budget);
    }
    if (strcmp(suffix, "risk_budget") == 0) {
        return autonomy_parse_q16(value, &delegation->risk_budget);
    }
    if (strcmp(suffix, "oversight") == 0) {
        delegation->oversight_policy_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "revocation") == 0) {
        delegation->revocation_policy_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        delegation->provenance_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        delegation->region_id = region_id;
        autonomy_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        delegation->flags = autonomy_delegation_flags_from_text(value);
        return 1;
    }
    return 0;
}

static int autonomy_fixture_apply_budget(autonomy_fixture* fixture,
                                         u32 index,
                                         const char* suffix,
                                         const char* value)
{
    dom_autonomy_budget_desc* budget;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_AUTONOMY_MAX_BUDGETS) {
        return 0;
    }
    if (fixture->autonomy_desc.budget_count <= index) {
        fixture->autonomy_desc.budget_count = index + 1u;
    }
    budget = &fixture->autonomy_desc.budgets[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->budget_names[index], value, sizeof(fixture->budget_names[index]) - 1);
        fixture->budget_names[index][sizeof(fixture->budget_names[index]) - 1] = '\0';
        budget->budget_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "delegation") == 0) {
        budget->delegation_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "time_budget") == 0) {
        return autonomy_parse_u64(value, &budget->time_budget_ticks);
    }
    if (strcmp(suffix, "time_used") == 0) {
        return autonomy_parse_u64(value, &budget->time_used_ticks);
    }
    if (strcmp(suffix, "energy_budget") == 0) {
        return autonomy_parse_q48(value, &budget->energy_budget);
    }
    if (strcmp(suffix, "energy_used") == 0) {
        return autonomy_parse_q48(value, &budget->energy_used);
    }
    if (strcmp(suffix, "risk_budget") == 0) {
        return autonomy_parse_q16(value, &budget->risk_budget);
    }
    if (strcmp(suffix, "risk_used") == 0) {
        return autonomy_parse_q16(value, &budget->risk_used);
    }
    if (strcmp(suffix, "planning_budget") == 0) {
        return autonomy_parse_u32(value, &budget->planning_budget);
    }
    if (strcmp(suffix, "planning_used") == 0) {
        return autonomy_parse_u32(value, &budget->planning_used);
    }
    if (strcmp(suffix, "provenance") == 0) {
        budget->provenance_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        budget->region_id = region_id;
        autonomy_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        budget->flags = autonomy_budget_flags_from_text(value);
        return 1;
    }
    return 0;
}

static int autonomy_fixture_apply_plan(autonomy_fixture* fixture,
                                       u32 index,
                                       const char* suffix,
                                       const char* value)
{
    dom_autonomy_plan_desc* plan;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_AUTONOMY_MAX_PLANS) {
        return 0;
    }
    if (fixture->autonomy_desc.plan_count <= index) {
        fixture->autonomy_desc.plan_count = index + 1u;
    }
    plan = &fixture->autonomy_desc.plans[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->plan_names[index], value, sizeof(fixture->plan_names[index]) - 1);
        fixture->plan_names[index][sizeof(fixture->plan_names[index]) - 1] = '\0';
        plan->plan_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "goal") == 0) {
        plan->goal_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "delegation") == 0) {
        plan->delegation_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "step_count") == 0) {
        return autonomy_parse_u32(value, &plan->step_count);
    }
    if (strncmp(suffix, "step_", 5) == 0) {
        u32 step_index = 0u;
        if (autonomy_parse_u32(suffix + 5, &step_index) &&
            step_index < DOM_AUTONOMY_MAX_PLAN_STEPS) {
            plan->step_process_ids[step_index] = autonomy_process_id_from_text(value);
            if (plan->step_count <= step_index) {
                plan->step_count = step_index + 1u;
            }
            return 1;
        }
    }
    if (strcmp(suffix, "success") == 0) {
        return autonomy_parse_q16(value, &plan->success_score);
    }
    if (strcmp(suffix, "cost") == 0) {
        return autonomy_parse_q48(value, &plan->estimated_cost);
    }
    if (strcmp(suffix, "created") == 0 || strcmp(suffix, "created_tick") == 0) {
        return autonomy_parse_u64(value, &plan->created_tick);
    }
    if (strcmp(suffix, "updated") == 0 || strcmp(suffix, "updated_tick") == 0) {
        return autonomy_parse_u64(value, &plan->last_update_tick);
    }
    if (strcmp(suffix, "status") == 0) {
        plan->status = autonomy_status_parse(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        plan->provenance_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        plan->region_id = region_id;
        autonomy_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        plan->flags = autonomy_plan_flags_from_text(value);
        return 1;
    }
    return 0;
}

static int autonomy_fixture_apply_event(autonomy_fixture* fixture,
                                        u32 index,
                                        const char* suffix,
                                        const char* value)
{
    dom_autonomy_event_desc* event;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_AUTONOMY_MAX_EVENTS) {
        return 0;
    }
    if (fixture->autonomy_desc.event_count <= index) {
        fixture->autonomy_desc.event_count = index + 1u;
    }
    event = &fixture->autonomy_desc.events[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->event_names[index], value, sizeof(fixture->event_names[index]) - 1);
        fixture->event_names[index][sizeof(fixture->event_names[index]) - 1] = '\0';
        event->event_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "process") == 0) {
        event->process_type = autonomy_process_parse(value);
        return 1;
    }
    if (strcmp(suffix, "goal") == 0) {
        event->goal_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "delegation") == 0) {
        event->delegation_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "plan") == 0) {
        event->plan_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "budget") == 0) {
        event->budget_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "delta_priority") == 0) {
        return autonomy_parse_q16(value, &event->delta_priority);
    }
    if (strcmp(suffix, "delta_energy") == 0) {
        return autonomy_parse_q48(value, &event->delta_energy_used);
    }
    if (strcmp(suffix, "delta_risk") == 0) {
        return autonomy_parse_q16(value, &event->delta_risk_used);
    }
    if (strcmp(suffix, "delta_time") == 0) {
        return autonomy_parse_u64(value, &event->delta_time_used);
    }
    if (strcmp(suffix, "delta_planning") == 0) {
        return autonomy_parse_u32(value, &event->delta_planning_used);
    }
    if (strcmp(suffix, "tick") == 0) {
        return autonomy_parse_u64(value, &event->event_tick);
    }
    if (strcmp(suffix, "provenance") == 0) {
        event->provenance_id = autonomy_parse_ref(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        event->region_id = region_id;
        autonomy_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        event->flags = autonomy_event_flags_from_text(value);
        return 1;
    }
    return 0;
}

static int autonomy_fixture_apply(autonomy_fixture* fixture, const char* key, const char* value)
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
        return autonomy_parse_u64(value, &fixture->autonomy_desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return autonomy_parse_u64(value, &fixture->autonomy_desc.domain_id);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return autonomy_parse_q16(value, &fixture->autonomy_desc.meters_per_unit);
    }
    if (strcmp(key, "goal_count") == 0) {
        return autonomy_parse_u32(value, &fixture->autonomy_desc.goal_count);
    }
    if (strcmp(key, "delegation_count") == 0) {
        return autonomy_parse_u32(value, &fixture->autonomy_desc.delegation_count);
    }
    if (strcmp(key, "budget_count") == 0) {
        return autonomy_parse_u32(value, &fixture->autonomy_desc.budget_count);
    }
    if (strcmp(key, "plan_count") == 0) {
        return autonomy_parse_u32(value, &fixture->autonomy_desc.plan_count);
    }
    if (strcmp(key, "event_count") == 0) {
        return autonomy_parse_u32(value, &fixture->autonomy_desc.event_count);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return autonomy_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return autonomy_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return autonomy_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return autonomy_parse_u32(value, &fixture->policy.cost_analytic);
    }

    if (autonomy_parse_indexed_key(key, "goal_", &index, &suffix)) {
        return autonomy_fixture_apply_goal(fixture, index, suffix, value);
    }
    if (autonomy_parse_indexed_key(key, "delegation_", &index, &suffix)) {
        return autonomy_fixture_apply_delegation(fixture, index, suffix, value);
    }
    if (autonomy_parse_indexed_key(key, "budget_", &index, &suffix)) {
        return autonomy_fixture_apply_budget(fixture, index, suffix, value);
    }
    if (autonomy_parse_indexed_key(key, "plan_", &index, &suffix)) {
        return autonomy_fixture_apply_plan(fixture, index, suffix, value);
    }
    if (autonomy_parse_indexed_key(key, "event_", &index, &suffix)) {
        return autonomy_fixture_apply_event(fixture, index, suffix, value);
    }
    return 0;
}

static int autonomy_fixture_load(const char* path, autonomy_fixture* out_fixture)
{
    FILE* file;
    char line[AUTONOMY_LINE_MAX];
    int header_ok = 0;
    autonomy_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    autonomy_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = autonomy_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, AUTONOMY_FIXTURE_HEADER) != 0) {
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
        autonomy_fixture_apply(&fixture, autonomy_trim(text), autonomy_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static const char* autonomy_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 autonomy_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = autonomy_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && autonomy_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u64 autonomy_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* value = autonomy_find_arg(argc, argv, key);
    u64 parsed = fallback;
    if (value && autonomy_parse_u64(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u32 autonomy_find_region_id(const autonomy_fixture* fixture, const char* name)
{
    if (!name || !*name) {
        return 0u;
    }
    if (!fixture) {
        return d_rng_hash_str32(name);
    }
    for (u32 i = 0u; i < fixture->region_count; ++i) {
        if (strcmp(fixture->region_names[i], name) == 0) {
            return fixture->region_ids[i];
        }
    }
    return d_rng_hash_str32(name);
}

static const char* autonomy_lookup_goal_name(const autonomy_fixture* fixture, u32 goal_id)
{
    if (!fixture || goal_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->autonomy_desc.goal_count; ++i) {
        if (fixture->autonomy_desc.goals[i].goal_id == goal_id) {
            return fixture->goal_names[i];
        }
    }
    return "";
}

static const char* autonomy_lookup_delegation_name(const autonomy_fixture* fixture, u32 delegation_id)
{
    if (!fixture || delegation_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->autonomy_desc.delegation_count; ++i) {
        if (fixture->autonomy_desc.delegations[i].delegation_id == delegation_id) {
            return fixture->delegation_names[i];
        }
    }
    return "";
}

static const char* autonomy_lookup_budget_name(const autonomy_fixture* fixture, u32 budget_id)
{
    if (!fixture || budget_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->autonomy_desc.budget_count; ++i) {
        if (fixture->autonomy_desc.budgets[i].budget_id == budget_id) {
            return fixture->budget_names[i];
        }
    }
    return "";
}

static const char* autonomy_lookup_plan_name(const autonomy_fixture* fixture, u32 plan_id)
{
    if (!fixture || plan_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->autonomy_desc.plan_count; ++i) {
        if (fixture->autonomy_desc.plans[i].plan_id == plan_id) {
            return fixture->plan_names[i];
        }
    }
    return "";
}

static const char* autonomy_lookup_event_name(const autonomy_fixture* fixture, u32 event_id)
{
    if (!fixture || event_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->autonomy_desc.event_count; ++i) {
        if (fixture->autonomy_desc.events[i].event_id == event_id) {
            return fixture->event_names[i];
        }
    }
    return "";
}

static int autonomy_goal_exists(const autonomy_fixture* fixture, u32 goal_id)
{
    if (!fixture || goal_id == 0u) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->autonomy_desc.goal_count; ++i) {
        if (fixture->autonomy_desc.goals[i].goal_id == goal_id) {
            return 1;
        }
    }
    return 0;
}

static int autonomy_delegation_exists(const autonomy_fixture* fixture, u32 delegation_id)
{
    if (!fixture || delegation_id == 0u) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->autonomy_desc.delegation_count; ++i) {
        if (fixture->autonomy_desc.delegations[i].delegation_id == delegation_id) {
            return 1;
        }
    }
    return 0;
}

static int autonomy_budget_exists(const autonomy_fixture* fixture, u32 budget_id)
{
    if (!fixture || budget_id == 0u) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->autonomy_desc.budget_count; ++i) {
        if (fixture->autonomy_desc.budgets[i].budget_id == budget_id) {
            return 1;
        }
    }
    return 0;
}

static int autonomy_plan_exists(const autonomy_fixture* fixture, u32 plan_id)
{
    if (!fixture || plan_id == 0u) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->autonomy_desc.plan_count; ++i) {
        if (fixture->autonomy_desc.plans[i].plan_id == plan_id) {
            return 1;
        }
    }
    return 0;
}

static int autonomy_validate_fixture(const autonomy_fixture* fixture)
{
    if (!fixture) {
        return 0;
    }
    if (fixture->autonomy_desc.goal_count > DOM_AUTONOMY_MAX_GOALS) {
        return 0;
    }
    if (fixture->autonomy_desc.delegation_count > DOM_AUTONOMY_MAX_DELEGATIONS) {
        return 0;
    }
    if (fixture->autonomy_desc.budget_count > DOM_AUTONOMY_MAX_BUDGETS) {
        return 0;
    }
    if (fixture->autonomy_desc.plan_count > DOM_AUTONOMY_MAX_PLANS) {
        return 0;
    }
    if (fixture->autonomy_desc.event_count > DOM_AUTONOMY_MAX_EVENTS) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->autonomy_desc.goal_count; ++i) {
        const dom_autonomy_goal_desc* goal = &fixture->autonomy_desc.goals[i];
        if (goal->goal_id == 0u) {
            return 0;
        }
        if (!autonomy_ratio_valid(goal->priority)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->autonomy_desc.delegation_count; ++i) {
        const dom_autonomy_delegation_desc* delegation = &fixture->autonomy_desc.delegations[i];
        if (delegation->delegation_id == 0u) {
            return 0;
        }
        if (delegation->delegator_id == 0u || delegation->delegate_agent_id == 0u) {
            return 0;
        }
        if (delegation->allowed_process_count > DOM_AUTONOMY_MAX_PROCESS_REFS) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->autonomy_desc.budget_count; ++i) {
        const dom_autonomy_budget_desc* budget = &fixture->autonomy_desc.budgets[i];
        if (budget->budget_id == 0u) {
            return 0;
        }
        if (budget->delegation_id == 0u) {
            return 0;
        }
        if (!autonomy_delegation_exists(fixture, budget->delegation_id)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->autonomy_desc.plan_count; ++i) {
        const dom_autonomy_plan_desc* plan = &fixture->autonomy_desc.plans[i];
        if (plan->plan_id == 0u) {
            return 0;
        }
        if (plan->step_count > DOM_AUTONOMY_MAX_PLAN_STEPS) {
            return 0;
        }
        if (!autonomy_ratio_valid(plan->success_score)) {
            return 0;
        }
        if (plan->goal_id != 0u && !autonomy_goal_exists(fixture, plan->goal_id)) {
            return 0;
        }
        if (plan->delegation_id != 0u && !autonomy_delegation_exists(fixture, plan->delegation_id)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->autonomy_desc.event_count; ++i) {
        const dom_autonomy_event_desc* event = &fixture->autonomy_desc.events[i];
        if (event->event_id == 0u) {
            return 0;
        }
        if (event->process_type == DOM_AUTONOMY_PROCESS_UNSET) {
            return 0;
        }
        if (event->goal_id != 0u && !autonomy_goal_exists(fixture, event->goal_id)) {
            return 0;
        }
        if (event->delegation_id != 0u &&
            !autonomy_delegation_exists(fixture, event->delegation_id)) {
            return 0;
        }
        if (event->plan_id != 0u && !autonomy_plan_exists(fixture, event->plan_id)) {
            return 0;
        }
        if (event->budget_id != 0u && !autonomy_budget_exists(fixture, event->budget_id)) {
            return 0;
        }
    }
    return 1;
}

static int autonomy_run_validate(const autonomy_fixture* fixture)
{
    int ok = autonomy_validate_fixture(fixture);
    printf("%s\n", AUTONOMY_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", AUTONOMY_PROVIDER_CHAIN);
    printf("goal_count=%u\n", (unsigned int)fixture->autonomy_desc.goal_count);
    printf("delegation_count=%u\n", (unsigned int)fixture->autonomy_desc.delegation_count);
    printf("budget_count=%u\n", (unsigned int)fixture->autonomy_desc.budget_count);
    printf("plan_count=%u\n", (unsigned int)fixture->autonomy_desc.plan_count);
    printf("event_count=%u\n", (unsigned int)fixture->autonomy_desc.event_count);
    printf("ok=%u\n", (unsigned int)(ok ? 1u : 0u));
    return ok ? 0 : 1;
}

static int autonomy_run_inspect_goal(const autonomy_fixture* fixture,
                                     const char* goal_name,
                                     u32 budget_max)
{
    dom_autonomy_domain domain;
    dom_domain_budget budget;
    dom_autonomy_goal_sample sample;
    u32 goal_id;
    if (!goal_name) {
        return 1;
    }
    goal_id = autonomy_parse_ref(goal_name);
    dom_autonomy_domain_init(&domain, &fixture->autonomy_desc);
    if (fixture->policy_set) {
        dom_autonomy_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_autonomy_goal_query(&domain, goal_id, &budget, &sample);

    printf("%s\n", AUTONOMY_INSPECT_HEADER);
    printf("entity=goal\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", AUTONOMY_PROVIDER_CHAIN);
    printf("goal_id=%u\n", (unsigned int)sample.goal_id);
    printf("goal_id_str=%s\n", autonomy_lookup_goal_name(fixture, sample.goal_id));
    printf("objective_id=%u\n", (unsigned int)sample.objective_id);
    printf("success_condition_id=%u\n", (unsigned int)sample.success_condition_id);
    printf("constraint_id=%u\n", (unsigned int)sample.constraint_id);
    printf("priority_q16=%d\n", (int)sample.priority);
    printf("expiry_tick=%llu\n", (unsigned long long)sample.expiry_tick);
    printf("delegator_id=%u\n", (unsigned int)sample.delegator_id);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_autonomy_domain_free(&domain);
    return 0;
}

static int autonomy_run_inspect_delegation(const autonomy_fixture* fixture,
                                           const char* delegation_name,
                                           u32 budget_max)
{
    dom_autonomy_domain domain;
    dom_domain_budget budget;
    dom_autonomy_delegation_sample sample;
    u32 delegation_id;
    if (!delegation_name) {
        return 1;
    }
    delegation_id = autonomy_parse_ref(delegation_name);
    dom_autonomy_domain_init(&domain, &fixture->autonomy_desc);
    if (fixture->policy_set) {
        dom_autonomy_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_autonomy_delegation_query(&domain, delegation_id, &budget, &sample);

    printf("%s\n", AUTONOMY_INSPECT_HEADER);
    printf("entity=delegation\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", AUTONOMY_PROVIDER_CHAIN);
    printf("delegation_id=%u\n", (unsigned int)sample.delegation_id);
    printf("delegation_id_str=%s\n", autonomy_lookup_delegation_name(fixture, sample.delegation_id));
    printf("delegator_id=%u\n", (unsigned int)sample.delegator_id);
    printf("delegate_agent_id=%u\n", (unsigned int)sample.delegate_agent_id);
    printf("allowed_process_count=%u\n", (unsigned int)sample.allowed_process_count);
    printf("time_budget_ticks=%llu\n", (unsigned long long)sample.time_budget_ticks);
    printf("energy_budget_q48=%lld\n", (long long)sample.energy_budget);
    printf("risk_budget_q16=%d\n", (int)sample.risk_budget);
    printf("oversight_policy_id=%u\n", (unsigned int)sample.oversight_policy_id);
    printf("revocation_policy_id=%u\n", (unsigned int)sample.revocation_policy_id);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_autonomy_domain_free(&domain);
    return 0;
}

static int autonomy_run_inspect_budget(const autonomy_fixture* fixture,
                                       const char* budget_name,
                                       u32 budget_max)
{
    dom_autonomy_domain domain;
    dom_domain_budget budget;
    dom_autonomy_budget_sample sample;
    u32 budget_id;
    if (!budget_name) {
        return 1;
    }
    budget_id = autonomy_parse_ref(budget_name);
    dom_autonomy_domain_init(&domain, &fixture->autonomy_desc);
    if (fixture->policy_set) {
        dom_autonomy_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_autonomy_budget_query(&domain, budget_id, &budget, &sample);

    printf("%s\n", AUTONOMY_INSPECT_HEADER);
    printf("entity=budget\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", AUTONOMY_PROVIDER_CHAIN);
    printf("budget_id=%u\n", (unsigned int)sample.budget_id);
    printf("budget_id_str=%s\n", autonomy_lookup_budget_name(fixture, sample.budget_id));
    printf("delegation_id=%u\n", (unsigned int)sample.delegation_id);
    printf("time_budget_ticks=%llu\n", (unsigned long long)sample.time_budget_ticks);
    printf("time_used_ticks=%llu\n", (unsigned long long)sample.time_used_ticks);
    printf("energy_budget_q48=%lld\n", (long long)sample.energy_budget);
    printf("energy_used_q48=%lld\n", (long long)sample.energy_used);
    printf("risk_budget_q16=%d\n", (int)sample.risk_budget);
    printf("risk_used_q16=%d\n", (int)sample.risk_used);
    printf("planning_budget=%u\n", (unsigned int)sample.planning_budget);
    printf("planning_used=%u\n", (unsigned int)sample.planning_used);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_autonomy_domain_free(&domain);
    return 0;
}

static int autonomy_run_inspect_plan(const autonomy_fixture* fixture,
                                     const char* plan_name,
                                     u32 budget_max)
{
    dom_autonomy_domain domain;
    dom_domain_budget budget;
    dom_autonomy_plan_sample sample;
    u32 plan_id;
    if (!plan_name) {
        return 1;
    }
    plan_id = autonomy_parse_ref(plan_name);
    dom_autonomy_domain_init(&domain, &fixture->autonomy_desc);
    if (fixture->policy_set) {
        dom_autonomy_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_autonomy_plan_query(&domain, plan_id, &budget, &sample);

    printf("%s\n", AUTONOMY_INSPECT_HEADER);
    printf("entity=plan\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", AUTONOMY_PROVIDER_CHAIN);
    printf("plan_id=%u\n", (unsigned int)sample.plan_id);
    printf("plan_id_str=%s\n", autonomy_lookup_plan_name(fixture, sample.plan_id));
    printf("goal_id=%u\n", (unsigned int)sample.goal_id);
    printf("delegation_id=%u\n", (unsigned int)sample.delegation_id);
    printf("step_count=%u\n", (unsigned int)sample.step_count);
    printf("success_score_q16=%d\n", (int)sample.success_score);
    printf("estimated_cost_q48=%lld\n", (long long)sample.estimated_cost);
    printf("created_tick=%llu\n", (unsigned long long)sample.created_tick);
    printf("last_update_tick=%llu\n", (unsigned long long)sample.last_update_tick);
    printf("status=%u\n", (unsigned int)sample.status);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_autonomy_domain_free(&domain);
    return 0;
}

static int autonomy_run_inspect_event(const autonomy_fixture* fixture,
                                      const char* event_name,
                                      u32 budget_max)
{
    dom_autonomy_domain domain;
    dom_domain_budget budget;
    dom_autonomy_event_sample sample;
    u32 event_id;
    if (!event_name) {
        return 1;
    }
    event_id = autonomy_parse_ref(event_name);
    dom_autonomy_domain_init(&domain, &fixture->autonomy_desc);
    if (fixture->policy_set) {
        dom_autonomy_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_autonomy_event_query(&domain, event_id, &budget, &sample);

    printf("%s\n", AUTONOMY_INSPECT_HEADER);
    printf("entity=event\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", AUTONOMY_PROVIDER_CHAIN);
    printf("event_id=%u\n", (unsigned int)sample.event_id);
    printf("event_id_str=%s\n", autonomy_lookup_event_name(fixture, sample.event_id));
    printf("process_type=%u\n", (unsigned int)sample.process_type);
    printf("goal_id=%u\n", (unsigned int)sample.goal_id);
    printf("delegation_id=%u\n", (unsigned int)sample.delegation_id);
    printf("plan_id=%u\n", (unsigned int)sample.plan_id);
    printf("budget_id=%u\n", (unsigned int)sample.budget_id);
    printf("delta_priority_q16=%d\n", (int)sample.delta_priority);
    printf("delta_energy_used_q48=%lld\n", (long long)sample.delta_energy_used);
    printf("delta_risk_used_q16=%d\n", (int)sample.delta_risk_used);
    printf("delta_time_used=%llu\n", (unsigned long long)sample.delta_time_used);
    printf("delta_planning_used=%u\n", (unsigned int)sample.delta_planning_used);
    printf("event_tick=%llu\n", (unsigned long long)sample.event_tick);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_autonomy_domain_free(&domain);
    return 0;
}

static int autonomy_run_inspect_region(const autonomy_fixture* fixture,
                                       const char* region_name,
                                       u32 budget_max)
{
    dom_autonomy_domain domain;
    dom_domain_budget budget;
    dom_autonomy_region_sample sample;
    u32 region_id = autonomy_find_region_id(fixture, region_name);

    dom_autonomy_domain_init(&domain, &fixture->autonomy_desc);
    if (fixture->policy_set) {
        dom_autonomy_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_autonomy_region_query(&domain, region_id, &budget, &sample);

    printf("%s\n", AUTONOMY_INSPECT_HEADER);
    printf("entity=region\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", AUTONOMY_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("goal_count=%u\n", (unsigned int)sample.goal_count);
    printf("delegation_count=%u\n", (unsigned int)sample.delegation_count);
    printf("budget_count=%u\n", (unsigned int)sample.budget_count);
    printf("plan_count=%u\n", (unsigned int)sample.plan_count);
    printf("event_count=%u\n", (unsigned int)sample.event_count);
    printf("priority_avg_q16=%d\n", (int)sample.priority_avg);
    printf("success_avg_q16=%d\n", (int)sample.success_avg);
    printf("budget_utilization_avg_q16=%d\n", (int)sample.budget_utilization_avg);
    for (u32 i = 0u; i < DOM_AUTONOMY_EVENT_BINS; ++i) {
        printf("event_type_count_%u=%u\n", (unsigned int)i,
               (unsigned int)sample.event_type_counts[i]);
    }
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_autonomy_domain_free(&domain);
    return 0;
}

static int autonomy_run_resolve(const autonomy_fixture* fixture,
                                const char* region_name,
                                u64 tick,
                                u64 tick_delta,
                                u32 budget_max,
                                u32 inactive_count)
{
    dom_autonomy_domain domain;
    dom_autonomy_domain* inactive = 0;
    dom_domain_budget budget;
    dom_autonomy_resolve_result result;
    u32 region_id = autonomy_find_region_id(fixture, region_name);
    u64 hash = 14695981039346656037ULL;

    dom_autonomy_domain_init(&domain, &fixture->autonomy_desc);
    if (fixture->policy_set) {
        dom_autonomy_domain_set_policy(&domain, &fixture->policy);
    }

    if (inactive_count > 0u) {
        inactive = (dom_autonomy_domain*)malloc(sizeof(dom_autonomy_domain) * inactive_count);
        if (inactive) {
            for (u32 i = 0u; i < inactive_count; ++i) {
                autonomy_fixture temp = *fixture;
                temp.autonomy_desc.domain_id = fixture->autonomy_desc.domain_id + (u64)(i + 1u);
                dom_autonomy_domain_init(&inactive[i], &temp.autonomy_desc);
                dom_autonomy_domain_set_state(&inactive[i],
                                              DOM_DOMAIN_EXISTENCE_DECLARED,
                                              DOM_DOMAIN_ARCHIVAL_LIVE);
            }
        }
    }

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_autonomy_resolve(&domain, region_id, tick, tick_delta, &budget, &result);

    for (u32 i = 0u; i < domain.goal_count; ++i) {
        hash = autonomy_hash_u32(hash, domain.goals[i].goal_id);
        hash = autonomy_hash_q16(hash, domain.goals[i].priority);
        hash = autonomy_hash_u32(hash, domain.goals[i].flags);
    }
    for (u32 i = 0u; i < domain.delegation_count; ++i) {
        hash = autonomy_hash_u32(hash, domain.delegations[i].delegation_id);
        hash = autonomy_hash_u32(hash, domain.delegations[i].flags);
    }
    for (u32 i = 0u; i < domain.budget_count; ++i) {
        hash = autonomy_hash_u32(hash, domain.budgets[i].budget_id);
        hash = autonomy_hash_u64(hash, domain.budgets[i].time_used_ticks);
        hash = autonomy_hash_q48(hash, domain.budgets[i].energy_used);
        hash = autonomy_hash_q16(hash, domain.budgets[i].risk_used);
        hash = autonomy_hash_u32(hash, domain.budgets[i].planning_used);
        hash = autonomy_hash_u32(hash, domain.budgets[i].flags);
    }
    for (u32 i = 0u; i < domain.plan_count; ++i) {
        hash = autonomy_hash_u32(hash, domain.plans[i].plan_id);
        hash = autonomy_hash_u32(hash, domain.plans[i].status);
        hash = autonomy_hash_q16(hash, domain.plans[i].success_score);
        hash = autonomy_hash_u32(hash, domain.plans[i].flags);
    }
    for (u32 i = 0u; i < domain.event_count; ++i) {
        hash = autonomy_hash_u32(hash, domain.events[i].event_id);
        hash = autonomy_hash_u32(hash, domain.events[i].process_type);
        hash = autonomy_hash_u32(hash, domain.events[i].flags);
    }

    printf("%s\n", AUTONOMY_RESOLVE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", AUTONOMY_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("goal_count=%u\n", (unsigned int)result.goal_count);
    printf("delegation_count=%u\n", (unsigned int)result.delegation_count);
    printf("budget_count=%u\n", (unsigned int)result.budget_count);
    printf("plan_count=%u\n", (unsigned int)result.plan_count);
    printf("event_count=%u\n", (unsigned int)result.event_count);
    printf("event_applied_count=%u\n", (unsigned int)result.event_applied_count);
    printf("priority_avg_q16=%d\n", (int)result.priority_avg);
    printf("success_avg_q16=%d\n", (int)result.success_avg);
    printf("budget_utilization_avg_q16=%d\n", (int)result.budget_utilization_avg);
    for (u32 i = 0u; i < DOM_AUTONOMY_EVENT_BINS; ++i) {
        printf("event_type_count_%u=%u\n", (unsigned int)i,
               (unsigned int)result.event_type_counts[i]);
    }
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);
    printf("resolve_hash=%llu\n", (unsigned long long)hash);

    dom_autonomy_domain_free(&domain);
    if (inactive) {
        for (u32 i = 0u; i < inactive_count; ++i) {
            dom_autonomy_domain_free(&inactive[i]);
        }
        free(inactive);
    }
    return 0;
}

static int autonomy_run_collapse(const autonomy_fixture* fixture, const char* region_name)
{
    dom_autonomy_domain domain;
    u32 region_id = autonomy_find_region_id(fixture, region_name);
    u32 count_before;
    u32 count_after;

    dom_autonomy_domain_init(&domain, &fixture->autonomy_desc);
    if (fixture->policy_set) {
        dom_autonomy_domain_set_policy(&domain, &fixture->policy);
    }
    count_before = dom_autonomy_domain_capsule_count(&domain);
    (void)dom_autonomy_domain_collapse_region(&domain, region_id);
    count_after = dom_autonomy_domain_capsule_count(&domain);

    printf("%s\n", AUTONOMY_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", AUTONOMY_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);

    dom_autonomy_domain_free(&domain);
    return 0;
}

static void autonomy_usage(void)
{
    printf("dom_tool_autonomy commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --goal <id> [--budget N]\n");
    printf("  inspect --fixture <path> --delegation <id> [--budget N]\n");
    printf("  inspect --fixture <path> --budget_id <id> [--budget N]\n");
    printf("  inspect --fixture <path> --plan <id> [--budget N]\n");
    printf("  inspect --fixture <path> --event <id> [--budget N]\n");
    printf("  inspect --fixture <path> --region <id> [--budget N]\n");
    printf("  resolve --fixture <path> --region <id> [--tick N] [--delta N] [--budget N] [--inactive N]\n");
    printf("  collapse --fixture <path> --region <id>\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        autonomy_usage();
        return 2;
    }
    cmd = argv[1];
    if (strcmp(cmd, "validate") == 0 ||
        strcmp(cmd, "inspect") == 0 ||
        strcmp(cmd, "resolve") == 0 ||
        strcmp(cmd, "collapse") == 0) {
        const char* fixture_path = autonomy_find_arg(argc, argv, "--fixture");
        autonomy_fixture fixture;
        if (!fixture_path || !autonomy_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "autonomy: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return autonomy_run_validate(&fixture);
        }
        if (strcmp(cmd, "inspect") == 0) {
            const char* goal_name = autonomy_find_arg(argc, argv, "--goal");
            const char* delegation_name = autonomy_find_arg(argc, argv, "--delegation");
            const char* budget_name = autonomy_find_arg(argc, argv, "--budget_id");
            const char* plan_name = autonomy_find_arg(argc, argv, "--plan");
            const char* event_name = autonomy_find_arg(argc, argv, "--event");
            const char* region_name = autonomy_find_arg(argc, argv, "--region");
            u32 budget_max = autonomy_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_full);
            if (goal_name) {
                return autonomy_run_inspect_goal(&fixture, goal_name, budget_max);
            }
            if (delegation_name) {
                return autonomy_run_inspect_delegation(&fixture, delegation_name, budget_max);
            }
            if (budget_name) {
                return autonomy_run_inspect_budget(&fixture, budget_name, budget_max);
            }
            if (plan_name) {
                return autonomy_run_inspect_plan(&fixture, plan_name, budget_max);
            }
            if (event_name) {
                return autonomy_run_inspect_event(&fixture, event_name, budget_max);
            }
            if (region_name) {
                return autonomy_run_inspect_region(&fixture, region_name, budget_max);
            }
            fprintf(stderr, "autonomy: inspect requires --goal, --delegation, --budget_id, --plan, --event, or --region\n");
            return 2;
        }
        if (strcmp(cmd, "resolve") == 0) {
            const char* region_name = autonomy_find_arg(argc, argv, "--region");
            u64 tick = autonomy_find_arg_u64(argc, argv, "--tick", 0u);
            u64 delta = autonomy_find_arg_u64(argc, argv, "--delta", 1u);
            u32 budget_max = autonomy_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_medium);
            u32 inactive = autonomy_find_arg_u32(argc, argv, "--inactive", 0u);
            if (!region_name) {
                fprintf(stderr, "autonomy: resolve requires --region\n");
                return 2;
            }
            return autonomy_run_resolve(&fixture, region_name, tick, delta, budget_max, inactive);
        }
        if (strcmp(cmd, "collapse") == 0) {
            const char* region_name = autonomy_find_arg(argc, argv, "--region");
            if (!region_name) {
                fprintf(stderr, "autonomy: collapse requires --region\n");
                return 2;
            }
            return autonomy_run_collapse(&fixture, region_name);
        }
    }

    autonomy_usage();
    return 2;
}
