/*
Client shell core implementation.
*/
#include "client_shell.h"

#include "domino/app/runtime.h"
#include "dominium/physical/physical_audit.h"

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdarg.h>
#include <ctype.h>


#define DOM_REFUSAL_INVALID "WD-REFUSAL-INVALID"
#define DOM_REFUSAL_SCHEMA "WD-REFUSAL-SCHEMA"
#define DOM_REFUSAL_TEMPLATE "WD-REFUSAL-TEMPLATE"
#define DOM_REFUSAL_PROCESS "PROC-REFUSAL"
#define DOM_REFUSAL_PROCESS_FAIL "PROC-FAIL"
#define DOM_REFUSAL_PROCESS_EPISTEMIC "PROC-REFUSAL-EPISTEMIC"

#define DOM_SHELL_DEFAULT_SAVE_PATH "data/saves/world.save"
#define DOM_SHELL_BATCH_SCRIPT_MAX 2048

#define DOM_SHELL_ACCESSIBILITY_MAX_Q16 (5 << 16)
#define DOM_SHELL_SUPPORT_MIN_Q16 (1 << 16)
#define DOM_SHELL_SURFACE_MAX_Q16 (10 << 16)
#define DOM_SHELL_RESOURCE_AMOUNT_Q16 (1 << 16)
#define DOM_SHELL_ENERGY_LOAD_Q16 (1 << 16)
#define DOM_SHELL_ENERGY_CAPACITY_Q16 (4 << 16)
#define DOM_SHELL_AGENT_BUDGET_BASE 4u
#define DOM_SHELL_TRANSFER_AMOUNT_Q16 (1 << 16)
#define DOM_SHELL_MAINTENANCE_AMOUNT_Q16 (1 << 16)

typedef struct dom_shell_builder {
    char* buf;
    size_t len;
    size_t cap;
    int overflow;
} dom_shell_builder;

typedef struct dom_shell_node_def {
    const char* node_id;
    const char* parent_id;
    const char* frame_id;
    const char* tags[8];
    uint32_t tag_count;
} dom_shell_node_def;

typedef struct dom_shell_edge_def {
    const char* parent_id;
    const char* child_id;
} dom_shell_edge_def;

static void dom_shell_builder_init(dom_shell_builder* b, char* buf, size_t cap)
{
    if (!b) {
        return;
    }
    b->buf = buf;
    b->len = 0u;
    b->cap = cap;
    b->overflow = 0;
    if (buf && cap > 0u) {
        buf[0] = '\0';
    }
}

static void dom_shell_builder_append_char(dom_shell_builder* b, char c)
{
    if (!b || b->overflow || !b->buf || b->cap == 0u) {
        return;
    }
    if (b->len + 1u >= b->cap) {
        b->overflow = 1;
        b->buf[b->cap - 1u] = '\0';
        return;
    }
    b->buf[b->len++] = c;
    b->buf[b->len] = '\0';
}

static void dom_shell_builder_append_text(dom_shell_builder* b, const char* text)
{
    if (!b || !text) {
        return;
    }
    while (*text) {
        dom_shell_builder_append_char(b, *text++);
        if (b->overflow) {
            return;
        }
    }
}

static void dom_shell_builder_appendf(dom_shell_builder* b, const char* fmt, ...)
{
    va_list args;
    int written;
    size_t remaining;
    if (!b || !fmt || b->overflow || !b->buf || b->cap == 0u) {
        return;
    }
    remaining = (b->len < b->cap) ? (b->cap - b->len) : 0u;
    if (remaining == 0u) {
        b->overflow = 1;
        return;
    }
    va_start(args, fmt);
    written = vsnprintf(b->buf + b->len, remaining, fmt, args);
    va_end(args);
    if (written < 0 || (size_t)written >= remaining) {
        b->overflow = 1;
        b->buf[b->cap - 1u] = '\0';
        return;
    }
    b->len += (size_t)written;
}

static void dom_shell_builder_append_json_string(dom_shell_builder* b, const char* text)
{
    const char* p;
    if (!b) {
        return;
    }
    dom_shell_builder_append_char(b, '"');
    if (!text) {
        dom_shell_builder_append_char(b, '"');
        return;
    }
    p = text;
    while (*p) {
        char c = *p++;
        if (c == '"' || c == '\\') {
            dom_shell_builder_append_char(b, '\\');
            dom_shell_builder_append_char(b, c);
        } else if (c == '\n') {
            dom_shell_builder_append_text(b, "\\n");
        } else if (c == '\r') {
            dom_shell_builder_append_text(b, "\\r");
        } else if (c == '\t') {
            dom_shell_builder_append_text(b, "\\t");
        } else {
            dom_shell_builder_append_char(b, c);
        }
        if (b->overflow) {
            return;
        }
    }
    dom_shell_builder_append_char(b, '"');
}

static void dom_shell_policy_set_clear(dom_shell_policy_set* set)
{
    if (!set) {
        return;
    }
    memset(set, 0, sizeof(*set));
}

static void dom_shell_trim_span(const char* text, const char** out_begin, size_t* out_len)
{
    const char* begin = text;
    const char* end;
    if (!text) {
        if (out_begin) {
            *out_begin = 0;
        }
        if (out_len) {
            *out_len = 0u;
        }
        return;
    }
    while (*begin && isspace((unsigned char)*begin)) {
        begin++;
    }
    end = begin + strlen(begin);
    while (end > begin && isspace((unsigned char)end[-1])) {
        end--;
    }
    if (out_begin) {
        *out_begin = begin;
    }
    if (out_len) {
        *out_len = (size_t)(end - begin);
    }
}

static void dom_shell_policy_set_add(dom_shell_policy_set* set, const char* id)
{
    const char* begin = 0;
    size_t len = 0u;
    if (!set || !id || !id[0]) {
        return;
    }
    dom_shell_trim_span(id, &begin, &len);
    if (!begin || len == 0u) {
        return;
    }
    if (set->count >= DOM_SHELL_MAX_POLICIES) {
        return;
    }
    if (len >= DOM_SHELL_POLICY_ID_MAX) {
        len = DOM_SHELL_POLICY_ID_MAX - 1u;
    }
    memcpy(set->items[set->count], begin, len);
    set->items[set->count][len] = '\0';
    set->count += 1u;
}

static int dom_shell_policy_set_contains(const dom_shell_policy_set* set, const char* id)
{
    uint32_t i;
    if (!set || !id || !id[0]) {
        return 0;
    }
    for (i = 0u; i < set->count; ++i) {
        if (strcmp(set->items[i], id) == 0) {
            return 1;
        }
    }
    return 0;
}

static void dom_shell_policy_set_copy(dom_shell_policy_set* dst, const dom_shell_policy_set* src)
{
    if (!dst) {
        return;
    }
    if (!src) {
        dom_shell_policy_set_clear(dst);
        return;
    }
    *dst = *src;
}

static void dom_shell_policy_set_from_csv(dom_shell_policy_set* set, const char* csv)
{
    char buf[DOM_SHELL_BATCH_SCRIPT_MAX];
    char* token;
    char* comma;
    size_t len;
    if (!set) {
        return;
    }
    dom_shell_policy_set_clear(set);
    if (!csv || !csv[0]) {
        return;
    }
    len = strlen(csv);
    if (len >= sizeof(buf)) {
        len = sizeof(buf) - 1u;
    }
    memcpy(buf, csv, len);
    buf[len] = '\0';
    token = buf;
    while (token) {
        comma = strchr(token, ',');
        if (comma) {
            *comma = '\0';
        }
        dom_shell_policy_set_add(set, token);
        token = comma ? (comma + 1u) : 0;
    }
}

void dom_client_shell_policy_to_csv(const dom_shell_policy_set* set, char* out, size_t out_cap)
{
    uint32_t i;
    size_t pos = 0u;
    if (!out || out_cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (!set || set->count == 0u) {
        return;
    }
    for (i = 0u; i < set->count; ++i) {
        const char* item = set->items[i];
        size_t item_len = item ? strlen(item) : 0u;
        if (item_len == 0u) {
            continue;
        }
        if (pos > 0u) {
            if (pos + 1u >= out_cap) {
                break;
            }
            out[pos++] = ',';
        }
        if (pos + item_len >= out_cap) {
            item_len = out_cap - pos - 1u;
        }
        memcpy(out + pos, item, item_len);
        pos += item_len;
        out[pos] = '\0';
        if (pos + 1u >= out_cap) {
            break;
        }
    }
}

static void dom_shell_builder_append_policy_array(dom_shell_builder* b, const dom_shell_policy_set* set)
{
    uint32_t i;
    dom_shell_builder_append_char(b, '[');
    if (!set || set->count == 0u) {
        dom_shell_builder_append_char(b, ']');
        return;
    }
    for (i = 0u; i < set->count; ++i) {
        if (i > 0u) {
            dom_shell_builder_append_char(b, ',');
        }
        dom_shell_builder_append_json_string(b, set->items[i]);
        if (b->overflow) {
            return;
        }
    }
    dom_shell_builder_append_char(b, ']');
}

static uint64_t dom_shell_hash64(const void* data, size_t len)
{
    const unsigned char* bytes = (const unsigned char*)data;
    uint64_t hash = 1469598103934665603ULL;
    size_t i;
    for (i = 0u; i < len; ++i) {
        hash ^= (uint64_t)bytes[i];
        hash *= 1099511628211ULL;
    }
    return hash;
}

static void dom_shell_event_ring_add(dom_shell_event_ring* ring,
                                     const char* event_name,
                                     const char* detail)
{
    char line[DOM_SHELL_EVENT_MAX];
    if (!ring || !event_name || !event_name[0]) {
        return;
    }
    ring->seq += 1u;
    if (detail && detail[0]) {
        snprintf(line, sizeof(line), "event_seq=%u event=%s %s",
                 (unsigned int)ring->seq, event_name, detail);
    } else {
        snprintf(line, sizeof(line), "event_seq=%u event=%s",
                 (unsigned int)ring->seq, event_name);
    }
    if (ring->count < DOM_SHELL_MAX_EVENTS) {
        uint32_t idx = (ring->head + ring->count) % DOM_SHELL_MAX_EVENTS;
        strncpy(ring->lines[idx], line, DOM_SHELL_EVENT_MAX - 1u);
        ring->lines[idx][DOM_SHELL_EVENT_MAX - 1u] = '\0';
        ring->count += 1u;
    } else {
        strncpy(ring->lines[ring->head], line, DOM_SHELL_EVENT_MAX - 1u);
        ring->lines[ring->head][DOM_SHELL_EVENT_MAX - 1u] = '\0';
        ring->head = (ring->head + 1u) % DOM_SHELL_MAX_EVENTS;
    }
}

static void dom_shell_emit(dom_client_shell* shell,
                           dom_app_ui_event_log* log,
                           const char* event_name,
                           const char* detail)
{
    if (!shell || !event_name || !event_name[0]) {
        return;
    }
    if (log) {
        dom_app_ui_event_log_emit(log, event_name, detail);
    }
    dom_shell_event_ring_add(&shell->events, event_name, detail);
}

static void dom_shell_set_status(dom_client_shell* shell, const char* fmt, ...)
{
    va_list args;
    if (!shell || !fmt) {
        return;
    }
    va_start(args, fmt);
    vsnprintf(shell->last_status, sizeof(shell->last_status), fmt, args);
    va_end(args);
}

static void dom_shell_set_refusal(dom_client_shell* shell, const char* code, const char* detail)
{
    if (!shell) {
        return;
    }
    shell->last_refusal_code[0] = '\0';
    shell->last_refusal_detail[0] = '\0';
    if (code && code[0]) {
        strncpy(shell->last_refusal_code, code, sizeof(shell->last_refusal_code) - 1u);
        shell->last_refusal_code[sizeof(shell->last_refusal_code) - 1u] = '\0';
    }
    if (detail && detail[0]) {
        strncpy(shell->last_refusal_detail, detail, sizeof(shell->last_refusal_detail) - 1u);
        shell->last_refusal_detail[sizeof(shell->last_refusal_detail) - 1u] = '\0';
    }
}

static uint64_t dom_shell_mix64(uint64_t v)
{
    v ^= v >> 33;
    v *= 0xff51afd7ed558ccdULL;
    v ^= v >> 33;
    v *= 0xc4ceb9fe1a85ec53ULL;
    v ^= v >> 33;
    return v;
}

static uint32_t dom_shell_hash32(uint64_t v)
{
    return (uint32_t)dom_shell_mix64(v);
}

static char* dom_shell_trim_token(char* text)
{
    char* end;
    if (!text) {
        return text;
    }
    while (*text && isspace((unsigned char)*text)) {
        text++;
    }
    end = text + strlen(text);
    while (end > text && isspace((unsigned char)end[-1])) {
        end--;
    }
    *end = '\0';
    return text;
}

static void dom_shell_format_mask_hex(char* out, size_t cap, u32 mask)
{
    if (!out || cap == 0u) {
        return;
    }
    snprintf(out, cap, "0x%08x", (unsigned int)mask);
}

static u32 dom_shell_capability_token(const char* token)
{
    if (!token || !token[0]) {
        return 0u;
    }
    if (strcmp(token, "move") == 0) return AGENT_CAP_MOVE;
    if (strcmp(token, "trade") == 0) return AGENT_CAP_TRADE;
    if (strcmp(token, "defend") == 0) return AGENT_CAP_DEFEND;
    if (strcmp(token, "research") == 0) return AGENT_CAP_RESEARCH;
    if (strcmp(token, "survey") == 0) return AGENT_CAP_SURVEY;
    if (strcmp(token, "maintain") == 0) return AGENT_CAP_MAINTAIN;
    if (strcmp(token, "logistics") == 0) return AGENT_CAP_LOGISTICS;
    return 0u;
}

static u32 dom_shell_authority_token(const char* token)
{
    if (!token || !token[0]) {
        return 0u;
    }
    if (strcmp(token, "basic") == 0) return AGENT_AUTH_BASIC;
    if (strcmp(token, "trade") == 0) return AGENT_AUTH_TRADE;
    if (strcmp(token, "military") == 0) return AGENT_AUTH_MILITARY;
    if (strcmp(token, "infra") == 0 || strcmp(token, "infrastructure") == 0) {
        return AGENT_AUTH_INFRASTRUCTURE;
    }
    return 0u;
}

static u32 dom_shell_knowledge_token(const char* token)
{
    if (!token || !token[0]) {
        return 0u;
    }
    if (strcmp(token, "resource") == 0) return AGENT_KNOW_RESOURCE;
    if (strcmp(token, "route") == 0 || strcmp(token, "safe_route") == 0) return AGENT_KNOW_SAFE_ROUTE;
    if (strcmp(token, "threat") == 0) return AGENT_KNOW_THREAT;
    if (strcmp(token, "infra") == 0 || strcmp(token, "infrastructure") == 0) {
        return AGENT_KNOW_INFRA;
    }
    return 0u;
}

static u32 dom_shell_process_token(const char* token)
{
    if (!token || !token[0]) {
        return 0u;
    }
    if (strcmp(token, "move") == 0) return AGENT_PROCESS_KIND_BIT(AGENT_PROCESS_KIND_MOVE);
    if (strcmp(token, "acquire") == 0) return AGENT_PROCESS_KIND_BIT(AGENT_PROCESS_KIND_ACQUIRE);
    if (strcmp(token, "defend") == 0) return AGENT_PROCESS_KIND_BIT(AGENT_PROCESS_KIND_DEFEND);
    if (strcmp(token, "research") == 0) return AGENT_PROCESS_KIND_BIT(AGENT_PROCESS_KIND_RESEARCH);
    if (strcmp(token, "trade") == 0) return AGENT_PROCESS_KIND_BIT(AGENT_PROCESS_KIND_TRADE);
    if (strcmp(token, "observe") == 0) return AGENT_PROCESS_KIND_BIT(AGENT_PROCESS_KIND_OBSERVE);
    if (strcmp(token, "survey") == 0) return AGENT_PROCESS_KIND_BIT(AGENT_PROCESS_KIND_SURVEY);
    if (strcmp(token, "maintain") == 0) return AGENT_PROCESS_KIND_BIT(AGENT_PROCESS_KIND_MAINTAIN);
    if (strcmp(token, "transfer") == 0) return AGENT_PROCESS_KIND_BIT(AGENT_PROCESS_KIND_TRANSFER);
    return 0u;
}

static u32 dom_shell_parse_mask_csv(const char* csv, u32 (*token_fn)(const char*))
{
    char buf[256];
    char* token;
    size_t len;
    u32 mask = 0u;
    if (!csv || !csv[0]) {
        return 0u;
    }
    len = strlen(csv);
    if (len >= sizeof(buf)) {
        len = sizeof(buf) - 1u;
    }
    memcpy(buf, csv, len);
    buf[len] = '\0';
    token = buf;
    while (token) {
        char* comma = strchr(token, ',');
        if (comma) {
            *comma = '\0';
        }
        token = dom_shell_trim_token(token);
        if (token && token[0]) {
            char* end = 0;
            unsigned long value = strtoul(token, &end, 0);
            if (end && *end == '\0') {
                mask |= (u32)value;
            } else if (token_fn) {
                mask |= token_fn(token);
            }
        }
        token = comma ? (comma + 1u) : 0;
    }
    return mask;
}

static u32 dom_shell_goal_type_from_string(const char* value)
{
    if (!value || !value[0]) {
        return AGENT_GOAL_SURVEY;
    }
    if (strcmp(value, "survey") == 0) return AGENT_GOAL_SURVEY;
    if (strcmp(value, "maintain") == 0) return AGENT_GOAL_MAINTAIN;
    if (strcmp(value, "stabilize") == 0) return AGENT_GOAL_STABILIZE;
    if (strcmp(value, "survive") == 0) return AGENT_GOAL_SURVIVE;
    if (strcmp(value, "acquire") == 0) return AGENT_GOAL_ACQUIRE;
    if (strcmp(value, "defend") == 0) return AGENT_GOAL_DEFEND;
    if (strcmp(value, "migrate") == 0) return AGENT_GOAL_MIGRATE;
    if (strcmp(value, "research") == 0) return AGENT_GOAL_RESEARCH;
    if (strcmp(value, "trade") == 0) return AGENT_GOAL_TRADE;
    return AGENT_GOAL_SURVEY;
}

static const char* dom_shell_goal_type_name(u32 value)
{
    switch (value) {
        case AGENT_GOAL_SURVIVE: return "survive";
        case AGENT_GOAL_ACQUIRE: return "acquire";
        case AGENT_GOAL_DEFEND: return "defend";
        case AGENT_GOAL_MIGRATE: return "migrate";
        case AGENT_GOAL_RESEARCH: return "research";
        case AGENT_GOAL_TRADE: return "trade";
        case AGENT_GOAL_SURVEY: return "survey";
        case AGENT_GOAL_MAINTAIN: return "maintain";
        case AGENT_GOAL_STABILIZE: return "stabilize";
        default: return "unknown";
    }
}

static const char* dom_shell_process_kind_name(u32 value)
{
    switch (value) {
        case AGENT_PROCESS_KIND_MOVE: return "move";
        case AGENT_PROCESS_KIND_ACQUIRE: return "acquire";
        case AGENT_PROCESS_KIND_DEFEND: return "defend";
        case AGENT_PROCESS_KIND_RESEARCH: return "research";
        case AGENT_PROCESS_KIND_TRADE: return "trade";
        case AGENT_PROCESS_KIND_OBSERVE: return "observe";
        case AGENT_PROCESS_KIND_SURVEY: return "survey";
        case AGENT_PROCESS_KIND_MAINTAIN: return "maintain";
        case AGENT_PROCESS_KIND_TRANSFER: return "transfer";
        default: return "unknown";
    }
}

static u32 dom_shell_network_type_from_string(const char* value)
{
    if (!value || !value[0]) {
        return DOM_NETWORK_LOGISTICS;
    }
    if (strcmp(value, "electrical") == 0) return DOM_NETWORK_ELECTRICAL;
    if (strcmp(value, "thermal") == 0) return DOM_NETWORK_THERMAL;
    if (strcmp(value, "fluid") == 0) return DOM_NETWORK_FLUID;
    if (strcmp(value, "logistics") == 0) return DOM_NETWORK_LOGISTICS;
    if (strcmp(value, "data") == 0) return DOM_NETWORK_DATA;
    return DOM_NETWORK_LOGISTICS;
}

static const char* dom_shell_network_type_name(u32 value)
{
    switch (value) {
        case DOM_NETWORK_ELECTRICAL: return "electrical";
        case DOM_NETWORK_THERMAL: return "thermal";
        case DOM_NETWORK_FLUID: return "fluid";
        case DOM_NETWORK_LOGISTICS: return "logistics";
        case DOM_NETWORK_DATA: return "data";
        default: return "unknown";
    }
}

static int dom_shell_agent_index(const dom_client_shell* shell, u64 agent_id)
{
    u32 i;
    if (!shell) {
        return -1;
    }
    for (i = 0u; i < shell->agent_count; ++i) {
        if (shell->agents[i].agent_id == agent_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_shell_agent_add(dom_client_shell* shell,
                               u64 agent_id,
                               u32 capability_mask,
                               u32 authority_mask,
                               u32 knowledge_mask)
{
    dom_shell_agent_record* record;
    dom_agent_schedule_item* sched;
    dom_agent_belief* belief;
    dom_agent_capability* cap;
    if (!shell) {
        return 0;
    }
    if (shell->agent_count >= DOM_SHELL_AGENT_MAX) {
        return 0;
    }
    if (agent_id == 0u) {
        agent_id = shell->next_agent_id++;
        if (agent_id == 0u) {
            agent_id = shell->next_agent_id++;
        }
    } else {
        if (dom_shell_agent_index(shell, agent_id) >= 0) {
            return 0;
        }
        if (agent_id >= shell->next_agent_id) {
            shell->next_agent_id = agent_id + 1u;
        }
    }
    record = &shell->agents[shell->agent_count];
    sched = &shell->schedules[shell->agent_count];
    belief = &shell->beliefs[shell->agent_count];
    cap = &shell->caps[shell->agent_count];
    memset(record, 0, sizeof(*record));
    memset(sched, 0, sizeof(*sched));
    memset(belief, 0, sizeof(*belief));
    memset(cap, 0, sizeof(*cap));
    record->agent_id = agent_id;
    sched->agent_id = agent_id;
    sched->next_due_tick = (dom_act_time_t)shell->tick;
    sched->compute_budget = DOM_SHELL_AGENT_BUDGET_BASE;
    belief->agent_id = agent_id;
    belief->knowledge_mask = knowledge_mask;
    belief->hunger_level = 0u;
    belief->threat_level = 0u;
    belief->risk_tolerance_q16 = AGENT_CONFIDENCE_MAX;
    belief->epistemic_confidence_q16 = AGENT_CONFIDENCE_MAX;
    cap->agent_id = agent_id;
    cap->capability_mask = capability_mask;
    cap->authority_mask = authority_mask;
    shell->agent_count += 1u;
    if (shell->possessed_agent_id == 0u) {
        shell->possessed_agent_id = agent_id;
    }
    return 1;
}

static dom_shell_network_state* dom_shell_network_find(dom_client_shell* shell, u64 network_id)
{
    u32 i;
    if (!shell) {
        return 0;
    }
    for (i = 0u; i < shell->network_count; ++i) {
        if (shell->networks[i].network_id == network_id) {
            return &shell->networks[i];
        }
    }
    return 0;
}

static dom_shell_network_state* dom_shell_network_find_for_node(dom_client_shell* shell, u64 node_id)
{
    u32 i;
    if (!shell) {
        return 0;
    }
    for (i = 0u; i < shell->network_count; ++i) {
        dom_shell_network_state* net = &shell->networks[i];
        if (dom_network_find_node(&net->graph, node_id)) {
            return net;
        }
    }
    return 0;
}

static dom_shell_network_state* dom_shell_network_find_for_nodes(dom_client_shell* shell,
                                                                 u64 a,
                                                                 u64 b)
{
    u32 i;
    if (!shell) {
        return 0;
    }
    for (i = 0u; i < shell->network_count; ++i) {
        dom_shell_network_state* net = &shell->networks[i];
        if (dom_network_find_node(&net->graph, a) &&
            dom_network_find_node(&net->graph, b)) {
            return net;
        }
    }
    return 0;
}

static dom_shell_network_state* dom_shell_network_create(dom_client_shell* shell,
                                                         u64 network_id,
                                                         u32 type)
{
    dom_shell_network_state* net;
    if (!shell) {
        return 0;
    }
    if (shell->network_count >= DOM_SHELL_NETWORK_MAX) {
        return 0;
    }
    if (network_id == 0u) {
        network_id = shell->next_network_id++;
        if (network_id == 0u) {
            network_id = shell->next_network_id++;
        }
    } else if (dom_shell_network_find(shell, network_id)) {
        return 0;
    } else if (network_id >= shell->next_network_id) {
        shell->next_network_id = network_id + 1u;
    }
    net = &shell->networks[shell->network_count++];
    memset(net, 0, sizeof(*net));
    net->network_id = network_id;
    dom_network_graph_init(&net->graph,
                           type,
                           net->nodes,
                           DOM_SHELL_NETWORK_NODE_MAX,
                           net->edges,
                           DOM_SHELL_NETWORK_EDGE_MAX);
    return net;
}

static void dom_shell_fields_init(dom_shell_field_state* fields)
{
    dom_domain_volume_ref domain;
    u32 i;
    if (!fields) {
        return;
    }
    memset(fields, 0, sizeof(*fields));
    fields->field_ids[0] = DOM_FIELD_SUPPORT_CAPACITY;
    fields->field_ids[1] = DOM_FIELD_SURFACE_GRADIENT;
    fields->field_ids[2] = DOM_FIELD_LOCAL_MOISTURE;
    fields->field_ids[3] = DOM_FIELD_ACCESSIBILITY_COST;
    fields->field_count = 4u;
    memset(&domain, 0, sizeof(domain));
    dom_field_storage_init(&fields->objective,
                           domain,
                           DOM_SHELL_FIELD_GRID_W,
                           DOM_SHELL_FIELD_GRID_H,
                           0u,
                           fields->objective_layers,
                           DOM_SHELL_FIELD_MAX);
    dom_field_storage_init(&fields->subjective,
                           domain,
                           DOM_SHELL_FIELD_GRID_W,
                           DOM_SHELL_FIELD_GRID_H,
                           0u,
                           fields->subjective_layers,
                           DOM_SHELL_FIELD_MAX);
    for (i = 0u; i < fields->field_count; ++i) {
        dom_field_layer_add(&fields->objective,
                            fields->field_ids[i],
                            DOM_FIELD_VALUE_Q16_16,
                            DOM_FIELD_VALUE_UNKNOWN,
                            DOM_FIELD_VALUE_UNKNOWN,
                            fields->objective_values[i]);
        dom_field_layer_add(&fields->subjective,
                            fields->field_ids[i],
                            DOM_FIELD_VALUE_Q16_16,
                            DOM_FIELD_VALUE_UNKNOWN,
                            DOM_FIELD_VALUE_UNKNOWN,
                            fields->subjective_values[i]);
    }
    fields->knowledge_mask = 0u;
    fields->confidence_q16 = 0u;
    fields->uncertainty_q16 = 0u;
}

static void dom_shell_structure_init(dom_shell_structure_state* state)
{
    if (!state) {
        return;
    }
    memset(state, 0, sizeof(*state));
    dom_assembly_init(&state->assembly,
                      1u,
                      state->parts,
                      (u32)(sizeof(state->parts) / sizeof(state->parts[0])),
                      state->connections,
                      (u32)(sizeof(state->connections) / sizeof(state->connections[0])));
    dom_volume_claim_registry_init(&state->claims,
                                   state->claim_storage,
                                   (u32)(sizeof(state->claim_storage) / sizeof(state->claim_storage[0])));
    dom_network_graph_init(&state->network,
                           DOM_NETWORK_ELECTRICAL,
                           state->nodes,
                           (u32)(sizeof(state->nodes) / sizeof(state->nodes[0])),
                           state->edges,
                           (u32)(sizeof(state->edges) / sizeof(state->edges[0])));
    dom_network_add_node(&state->network, 1u, DOM_SHELL_ENERGY_CAPACITY_Q16);
    dom_network_add_node(&state->network, 2u, DOM_SHELL_ENERGY_CAPACITY_Q16);
    dom_network_add_edge(&state->network, 1u, 1u, 2u, DOM_SHELL_ENERGY_CAPACITY_Q16, 0);
    state->structure.structure_id = 1u;
    state->structure.built = 0u;
    state->structure.failed = 0u;
}

static void dom_shell_agents_reset(dom_client_shell* shell)
{
    if (!shell) {
        return;
    }
    memset(shell->agents, 0, sizeof(shell->agents));
    memset(shell->schedules, 0, sizeof(shell->schedules));
    memset(shell->beliefs, 0, sizeof(shell->beliefs));
    memset(shell->caps, 0, sizeof(shell->caps));
    memset(shell->goals, 0, sizeof(shell->goals));
    memset(shell->delegations, 0, sizeof(shell->delegations));
    memset(shell->delegation_assignments, 0, sizeof(shell->delegation_assignments));
    memset(shell->authority_grants, 0, sizeof(shell->authority_grants));
    memset(shell->constraints, 0, sizeof(shell->constraints));
    memset(shell->institutions, 0, sizeof(shell->institutions));
    shell->agent_count = 0u;
    shell->next_agent_id = 1u;
    shell->possessed_agent_id = 0u;
    shell->delegation_assignment_count = 0u;
    shell->next_delegation_id = 1u;
    shell->next_authority_id = 1u;
    shell->next_constraint_id = 1u;
    shell->next_institution_id = 1u;
    agent_goal_registry_init(&shell->goal_registry,
                             shell->goals,
                             DOM_SHELL_GOAL_MAX,
                             1u);
    agent_delegation_registry_init(&shell->delegation_registry,
                                   shell->delegations,
                                   DOM_SHELL_DELEGATION_MAX);
    agent_authority_registry_init(&shell->authority_registry,
                                  shell->authority_grants,
                                  DOM_SHELL_AUTH_GRANT_MAX);
    agent_constraint_registry_init(&shell->constraint_registry,
                                   shell->constraints,
                                   DOM_SHELL_CONSTRAINT_MAX);
    agent_institution_registry_init(&shell->institution_registry,
                                    shell->institutions,
                                    DOM_SHELL_INSTITUTION_MAX);
    dom_agent_goal_buffer_init(&shell->goal_buffer,
                               shell->goal_choices,
                               DOM_SHELL_AGENT_MAX);
    dom_agent_plan_buffer_init(&shell->plan_buffer,
                               shell->plan_entries,
                               DOM_SHELL_AGENT_MAX,
                               1u);
    dom_agent_command_buffer_init(&shell->command_buffer,
                                  shell->command_entries,
                                  (u32)(DOM_SHELL_AGENT_MAX * 2u),
                                  1u);
    dom_agent_audit_init(&shell->agent_audit_log,
                         shell->agent_audit_entries,
                         DOM_SHELL_AUDIT_MAX,
                         1u);
}

static void dom_shell_networks_reset(dom_client_shell* shell)
{
    if (!shell) {
        return;
    }
    memset(shell->networks, 0, sizeof(shell->networks));
    shell->network_count = 0u;
    shell->next_network_id = 1u;
}

static int dom_shell_field_index(const dom_shell_field_state* fields, u32 field_id)
{
    u32 i;
    if (!fields) {
        return -1;
    }
    for (i = 0u; i < fields->field_count; ++i) {
        if (fields->field_ids[i] == field_id) {
            return (int)i;
        }
    }
    return -1;
}

static i32 dom_shell_latent_value(const dom_client_shell* shell, u32 field_id)
{
    uint64_t seed = shell ? shell->rng_seed : 0u;
    u32 h = dom_shell_hash32(seed ^ ((uint64_t)field_id * 0x9e3779b97f4a7c15ULL));
    i32 base = 1;
    i32 span = 4;
    return (i32)((base + (int)(h % (u32)span)) << 16);
}

static int dom_shell_objective_value(dom_client_shell* shell, u32 field_id, i32* out_value)
{
    i32 value = 0;
    if (!shell || !out_value) {
        return 0;
    }
    if (dom_field_get_value(&shell->fields.objective, field_id, 0u, 0u, &value) != 0) {
        return 0;
    }
    if (value == DOM_FIELD_VALUE_UNKNOWN) {
        value = dom_shell_latent_value(shell, field_id);
        (void)dom_field_set_value(&shell->fields.objective, field_id, 0u, 0u, value);
    }
    *out_value = value;
    return 1;
}

static int dom_shell_parse_q16(const char* text, i32* out_value)
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
    if (value > 32767.0) {
        value = 32767.0;
    }
    if (value < -32768.0) {
        value = -32768.0;
    }
    *out_value = (i32)(value * 65536.0);
    return 1;
}

static const char* dom_shell_process_name(u32 kind)
{
    switch (kind) {
        case DOM_LOCAL_PROCESS_SURVEY: return "survey_local_area";
        case DOM_LOCAL_PROCESS_COLLECT: return "collect_local_material";
        case DOM_LOCAL_PROCESS_ASSEMBLE: return "assemble_simple_structure";
        case DOM_LOCAL_PROCESS_CONNECT_ENERGY: return "connect_energy_source";
        case DOM_LOCAL_PROCESS_INSPECT: return "inspect_structure";
        case DOM_LOCAL_PROCESS_REPAIR: return "repair_structure";
        default: return "unknown";
    }
}

static const char* dom_shell_failure_reason(u32 mode_id)
{
    switch (mode_id) {
        case DOM_PHYS_FAIL_NO_CAPABILITY: return "capability";
        case DOM_PHYS_FAIL_NO_AUTHORITY: return "authority";
        case DOM_PHYS_FAIL_CONSTRAINT: return "constraint";
        case DOM_PHYS_FAIL_RESOURCE_EMPTY: return "resources";
        case DOM_PHYS_FAIL_CAPACITY: return "capacity";
        case DOM_PHYS_FAIL_UNSUPPORTED: return "unsupported";
        case DOM_PHYS_FAIL_EPISTEMIC: return "epistemic";
        default: return "unknown";
    }
}

static void dom_shell_refine_required_fields(dom_client_shell* shell, u32 mask)
{
    u32 i;
    if (!shell || mask == 0u) {
        return;
    }
    for (i = 0u; i < 32u; ++i) {
        u32 bit = (1u << i);
        i32 value = 0;
        if ((mask & bit) == 0u) {
            continue;
        }
        if (dom_shell_objective_value(shell, i + 1u, &value)) {
            (void)value;
        }
    }
}

static void dom_shell_local_reset(dom_client_shell* shell)
{
    if (!shell) {
        return;
    }
    dom_shell_fields_init(&shell->fields);
    dom_shell_structure_init(&shell->structure);
    dom_shell_agents_reset(shell);
    dom_shell_networks_reset(shell);
    shell->last_intent[0] = '\0';
    shell->last_plan[0] = '\0';
    shell->next_intent_id = 1u;
    shell->rng_seed = 0u;
}

static void dom_shell_goal_desc_default(u64 agent_id,
                                        u32 goal_type,
                                        agent_goal_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->agent_id = agent_id;
    desc->type = goal_type;
    desc->base_priority = 10u;
    desc->urgency = 0u;
    desc->acceptable_risk_q16 = AGENT_CONFIDENCE_MAX;
    desc->epistemic_confidence_q16 = AGENT_CONFIDENCE_MAX;
    desc->flags = 0u;
    switch (goal_type) {
        case AGENT_GOAL_SURVEY:
            desc->preconditions.required_capabilities = AGENT_CAP_SURVEY;
            desc->preconditions.required_authority = 0u;
            desc->preconditions.required_knowledge = 0u;
            desc->flags |= AGENT_GOAL_FLAG_ALLOW_UNKNOWN;
            break;
        case AGENT_GOAL_MAINTAIN:
            desc->preconditions.required_capabilities = AGENT_CAP_MAINTAIN;
            desc->preconditions.required_authority = AGENT_AUTH_INFRASTRUCTURE;
            desc->preconditions.required_knowledge = AGENT_KNOW_INFRA;
            desc->flags |= AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE;
            break;
        case AGENT_GOAL_STABILIZE:
            desc->preconditions.required_capabilities = AGENT_CAP_LOGISTICS;
            desc->preconditions.required_authority = AGENT_AUTH_INFRASTRUCTURE;
            desc->preconditions.required_knowledge = AGENT_KNOW_INFRA;
            desc->flags |= AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE;
            desc->flags |= AGENT_GOAL_FLAG_REQUIRE_DELEGATION;
            break;
        default:
            break;
    }
}

static dom_agent_belief* dom_shell_belief_for_agent(dom_client_shell* shell, u64 agent_id)
{
    int idx = dom_shell_agent_index(shell, agent_id);
    if (!shell || idx < 0) {
        return 0;
    }
    return &shell->beliefs[idx];
}

static dom_agent_capability* dom_shell_cap_for_agent(dom_client_shell* shell, u64 agent_id)
{
    int idx = dom_shell_agent_index(shell, agent_id);
    if (!shell || idx < 0) {
        return 0;
    }
    return &shell->caps[idx];
}

static dom_agent_schedule_item* dom_shell_schedule_for_agent(dom_client_shell* shell, u64 agent_id)
{
    int idx = dom_shell_agent_index(shell, agent_id);
    if (!shell || idx < 0) {
        return 0;
    }
    return &shell->schedules[idx];
}

static const agent_plan* dom_shell_plan_for_id(const dom_agent_plan_buffer* plans, u64 plan_id)
{
    u32 i;
    if (!plans || !plans->entries) {
        return 0;
    }
    for (i = 0u; i < plans->count; ++i) {
        if (plans->entries[i].plan.plan_id == plan_id) {
            return &plans->entries[i].plan;
        }
    }
    return 0;
}

static dom_network_edge* dom_shell_network_find_edge_between(dom_network_graph* graph,
                                                             u64 a,
                                                             u64 b)
{
    u32 i;
    if (!graph || !graph->edges) {
        return 0;
    }
    for (i = 0u; i < graph->edge_count; ++i) {
        dom_network_edge* edge = &graph->edges[i];
        if ((edge->a == a && edge->b == b) || (edge->a == b && edge->b == a)) {
            return edge;
        }
    }
    return 0;
}

static const char* dom_shell_network_reason(int rc)
{
    switch (rc) {
        case -2: return "missing";
        case -3: return "failed";
        case -4: return "capacity";
        case -5: return "insufficient_storage";
        case -6: return "capacity";
        default: return "unknown";
    }
}

static void dom_shell_update_agent_records(dom_client_shell* shell,
                                           const dom_agent_goal_buffer* goals,
                                           const dom_agent_plan_buffer* plans)
{
    u32 i;
    if (!shell) {
        return;
    }
    for (i = 0u; i < shell->agent_count; ++i) {
        dom_shell_agent_record* record = &shell->agents[i];
        record->last_goal_id = 0u;
        record->last_goal_type = 0u;
        record->last_refusal = 0u;
        if (goals && i < goals->count) {
            record->last_goal_id = goals->entries[i].goal_id;
            record->last_refusal = goals->entries[i].refusal;
        }
        if (plans && i < plans->count) {
            if (plans->entries[i].refusal != 0u) {
                record->last_refusal = plans->entries[i].refusal;
            }
        }
        if (record->last_goal_id != 0u) {
            agent_goal* goal = agent_goal_find(&shell->goal_registry, record->last_goal_id);
            if (goal) {
                record->last_goal_type = goal->type;
            }
        }
    }
}

static void dom_shell_update_schedule_budget(dom_client_shell* shell, dom_act_time_t now_act)
{
    u32 i;
    if (!shell) {
        return;
    }
    for (i = 0u; i < shell->agent_count; ++i) {
        shell->schedules[i].next_due_tick = now_act;
        shell->schedules[i].compute_budget = DOM_SHELL_AGENT_BUDGET_BASE;
    }
    for (i = 0u; i < shell->delegation_registry.count; ++i) {
        const agent_delegation* del = &shell->delegations[i];
        if (del->revoked) {
            continue;
        }
        if (del->expiry_act != 0u && del->expiry_act <= now_act) {
            continue;
        }
        {
            int idx = dom_shell_agent_index(shell, del->delegatee_ref);
            if (idx >= 0 && shell->schedules[idx].compute_budget > 0u) {
                shell->schedules[idx].compute_budget -= 1u;
            }
        }
    }
}

static void dom_shell_network_tick_all(dom_client_shell* shell,
                                       dom_app_ui_event_log* log,
                                       dom_act_time_t now_act)
{
    u32 i;
    if (!shell) {
        return;
    }
    for (i = 0u; i < shell->network_count; ++i) {
        dom_shell_network_state* net = &shell->networks[i];
        u32 node_count = net->graph.node_count;
        u32 edge_count = net->graph.edge_count;
        u32 n;
        u32 e;
        u32 node_status[DOM_SHELL_NETWORK_NODE_MAX];
        u32 edge_status[DOM_SHELL_NETWORK_EDGE_MAX];
        if (node_count > DOM_SHELL_NETWORK_NODE_MAX) {
            node_count = DOM_SHELL_NETWORK_NODE_MAX;
        }
        if (edge_count > DOM_SHELL_NETWORK_EDGE_MAX) {
            edge_count = DOM_SHELL_NETWORK_EDGE_MAX;
        }
        for (n = 0u; n < node_count; ++n) {
            node_status[n] = net->nodes[n].status;
        }
        for (e = 0u; e < edge_count; ++e) {
            edge_status[e] = net->edges[e].status;
        }
        (void)dom_network_tick(&net->graph, 0, now_act);
        for (n = 0u; n < node_count; ++n) {
            if (node_status[n] == DOM_NETWORK_OK && net->nodes[n].status == DOM_NETWORK_FAILED) {
                char detail[160];
                snprintf(detail, sizeof(detail),
                         "network_id=%llu node=%llu result=failed reason=threshold",
                         (unsigned long long)net->network_id,
                         (unsigned long long)net->nodes[n].node_id);
                dom_shell_emit(shell, log, "client.network.fail", detail);
            }
        }
        for (e = 0u; e < edge_count; ++e) {
            if (edge_status[e] == DOM_NETWORK_OK && net->edges[e].status == DOM_NETWORK_FAILED) {
                char detail[160];
                snprintf(detail, sizeof(detail),
                         "network_id=%llu edge=%llu result=failed",
                         (unsigned long long)net->network_id,
                         (unsigned long long)net->edges[e].edge_id);
                dom_shell_emit(shell, log, "client.network.fail", detail);
            }
        }
    }
}

static void dom_shell_execute_agent_command(dom_client_shell* shell,
                                            const dom_agent_command* cmd,
                                            const dom_agent_plan_buffer* plans,
                                            dom_app_ui_event_log* log)
{
    dom_agent_belief* belief;
    dom_agent_capability* cap;
    agent_goal* goal;
    u32 effective_auth = 0u;
    int success = 0;
    const char* reason = "unknown";
    const char* process_name;
    if (!shell || !cmd) {
        return;
    }
    belief = dom_shell_belief_for_agent(shell, cmd->agent_id);
    cap = dom_shell_cap_for_agent(shell, cmd->agent_id);
    goal = agent_goal_find(&shell->goal_registry, cmd->goal_id);
    process_name = dom_shell_process_kind_name(cmd->process_kind);
    if (cap) {
        effective_auth = cap->authority_mask;
        if (shell->authority_registry.count > 0u) {
            effective_auth = agent_authority_effective_mask(&shell->authority_registry,
                                                            cmd->agent_id,
                                                            effective_auth,
                                                            (dom_act_time_t)shell->tick);
        }
    }
    if (!belief) {
        reason = "agent_missing";
    } else if (cmd->required_authority_mask != 0u &&
               (effective_auth & cmd->required_authority_mask) != cmd->required_authority_mask) {
        reason = "insufficient_authority";
    } else if (cmd->process_kind == AGENT_PROCESS_KIND_SURVEY) {
        if (shell->network_count == 0u) {
            reason = "unsupported";
        } else {
            belief->knowledge_mask |= AGENT_KNOW_INFRA;
            belief->epistemic_confidence_q16 = AGENT_CONFIDENCE_MAX;
            success = 1;
        }
    } else if (cmd->process_kind == AGENT_PROCESS_KIND_MAINTAIN) {
        dom_shell_network_state* net = dom_shell_network_find_for_node(shell, cmd->target_id);
        if (!net) {
            reason = "missing";
        } else {
            dom_network_node* node = dom_network_find_node(&net->graph, cmd->target_id);
            if (!node) {
                reason = "missing";
            } else {
                int rc = dom_network_store(&net->graph,
                                           node->node_id,
                                           DOM_SHELL_MAINTENANCE_AMOUNT_Q16,
                                           0,
                                           (dom_act_time_t)shell->tick);
                if (rc == 0) {
                    if (node->status == DOM_NETWORK_FAILED) {
                        node->status = DOM_NETWORK_OK;
                    }
                    success = 1;
                } else {
                    reason = dom_shell_network_reason(rc);
                }
            }
        }
    } else if (cmd->process_kind == AGENT_PROCESS_KIND_TRANSFER) {
        dom_shell_network_state* net = dom_shell_network_find_for_nodes(shell,
                                                                        belief ? belief->known_resource_ref : 0u,
                                                                        cmd->target_id);
        if (!net) {
            reason = "missing";
        } else {
            u64 from_node = belief ? belief->known_resource_ref : 0u;
            u64 to_node = cmd->target_id;
            dom_network_edge* edge = dom_shell_network_find_edge_between(&net->graph, from_node, to_node);
            u32 prev_status = edge ? edge->status : DOM_NETWORK_OK;
            int rc = dom_network_transfer(&net->graph,
                                          from_node,
                                          to_node,
                                          DOM_SHELL_TRANSFER_AMOUNT_Q16,
                                          0,
                                          (dom_act_time_t)shell->tick);
            if (rc == 0) {
                success = 1;
            } else {
                reason = dom_shell_network_reason(rc);
                if (edge && prev_status == DOM_NETWORK_OK && edge->status == DOM_NETWORK_FAILED) {
                    char detail[160];
                    snprintf(detail, sizeof(detail),
                             "network_id=%llu edge=%llu result=failed reason=capacity",
                             (unsigned long long)net->network_id,
                             (unsigned long long)edge->edge_id);
                    dom_shell_emit(shell, log, "client.network.fail", detail);
                }
            }
        }
    } else {
        reason = "unsupported";
    }

    if (success) {
        if (goal && plans) {
            const agent_plan* plan = dom_shell_plan_for_id(plans, cmd->plan_id);
            if (plan && cmd->step_index + 1u >= plan->step_count) {
                agent_goal_set_status(goal, AGENT_GOAL_SATISFIED, (dom_act_time_t)shell->tick);
            }
        }
        if (cmd->agent_id == shell->possessed_agent_id) {
            snprintf(shell->last_intent, sizeof(shell->last_intent),
                     "agent=%llu command=%llu process=%s",
                     (unsigned long long)cmd->agent_id,
                     (unsigned long long)cmd->command_id,
                     process_name);
            snprintf(shell->last_plan, sizeof(shell->last_plan),
                     "plan=%llu step=%u process=%s",
                     (unsigned long long)cmd->plan_id,
                     (unsigned int)(cmd->step_index + 1u),
                     process_name);
        }
        {
            char detail[200];
            snprintf(detail, sizeof(detail),
                     "agent_id=%llu goal_id=%llu command_id=%llu process=%s result=ok",
                     (unsigned long long)cmd->agent_id,
                     (unsigned long long)cmd->goal_id,
                     (unsigned long long)cmd->command_id,
                     process_name);
            dom_shell_emit(shell, log, "client.agent.command", detail);
        }
    } else {
        if (goal) {
            agent_goal_record_failure(goal, (dom_act_time_t)shell->tick);
        }
        {
            char detail[200];
            snprintf(detail, sizeof(detail),
                     "agent_id=%llu goal_id=%llu command_id=%llu process=%s result=failed reason=%s",
                     (unsigned long long)cmd->agent_id,
                     (unsigned long long)cmd->goal_id,
                     (unsigned long long)cmd->command_id,
                     process_name,
                     reason);
            dom_shell_emit(shell, log, "client.agent.command", detail);
        }
    }
}

static int dom_shell_simulate_tick(dom_client_shell* shell,
                                   dom_app_ui_event_log* log,
                                   int emit_text)
{
    u32 i;
    u32 commands_executed = 0u;
    if (!shell || !shell->world.active) {
        dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "no active world");
        dom_shell_set_status(shell, "simulate=refused");
        return 0;
    }
    shell->tick += 1u;
    dom_agent_goal_buffer_reset(&shell->goal_buffer);
    dom_agent_plan_buffer_reset(&shell->plan_buffer);
    dom_agent_command_buffer_reset(&shell->command_buffer);
    shell->agent_audit_log.count = 0u;
    dom_agent_audit_set_context(&shell->agent_audit_log,
                                (dom_act_time_t)shell->tick,
                                0u);
    dom_shell_update_schedule_budget(shell, (dom_act_time_t)shell->tick);

    (void)dom_agent_evaluate_goals_slice(shell->schedules,
                                         shell->agent_count,
                                         0u,
                                         shell->agent_count,
                                         &shell->goal_registry,
                                         shell->beliefs,
                                         shell->agent_count,
                                         shell->caps,
                                         shell->agent_count,
                                         &shell->goal_buffer,
                                         &shell->agent_audit_log);
    (void)dom_agent_plan_actions_slice(&shell->goal_buffer,
                                       0u,
                                       shell->goal_buffer.count,
                                       &shell->goal_registry,
                                       shell->beliefs,
                                       shell->agent_count,
                                       shell->caps,
                                       shell->agent_count,
                                       shell->schedules,
                                       shell->agent_count,
                                       &shell->plan_buffer,
                                       &shell->agent_audit_log);
    (void)dom_agent_validate_plan_slice(&shell->plan_buffer,
                                        0u,
                                        shell->plan_buffer.count,
                                        shell->caps,
                                        shell->agent_count,
                                        &shell->authority_registry,
                                        &shell->constraint_registry,
                                        0,
                                        &shell->delegation_registry,
                                        &shell->goal_registry,
                                        &shell->agent_audit_log);
    for (i = 0u; i < shell->plan_buffer.count; ++i) {
        const agent_plan* plan = &shell->plan_buffer.entries[i].plan;
        u32 refusal = shell->plan_buffer.entries[i].refusal;
        char detail[200];
        if (!plan || plan->plan_id == 0u) {
            continue;
        }
        if (shell->plan_buffer.entries[i].valid != 0u) {
            snprintf(detail, sizeof(detail),
                     "agent_id=%llu goal_id=%llu plan_id=%llu result=ok",
                     (unsigned long long)plan->agent_id,
                     (unsigned long long)plan->goal_id,
                     (unsigned long long)plan->plan_id);
        } else if (refusal != 0u) {
            snprintf(detail, sizeof(detail),
                     "agent_id=%llu goal_id=%llu plan_id=%llu result=refused reason=%s",
                     (unsigned long long)plan->agent_id,
                     (unsigned long long)plan->goal_id,
                     (unsigned long long)plan->plan_id,
                     agent_refusal_to_string((agent_refusal_code)refusal));
        } else {
            snprintf(detail, sizeof(detail),
                     "agent_id=%llu goal_id=%llu plan_id=%llu result=refused reason=unknown",
                     (unsigned long long)plan->agent_id,
                     (unsigned long long)plan->goal_id,
                     (unsigned long long)plan->plan_id);
        }
        dom_shell_emit(shell, log, "client.agent.plan", detail);
    }

    (void)dom_agent_emit_commands_slice(&shell->plan_buffer,
                                        0u,
                                        shell->plan_buffer.count,
                                        &shell->command_buffer,
                                        &shell->agent_audit_log);
    dom_shell_update_agent_records(shell, &shell->goal_buffer, &shell->plan_buffer);

    for (i = 0u; i < shell->command_buffer.count; ++i) {
        dom_shell_execute_agent_command(shell, &shell->command_buffer.entries[i], &shell->plan_buffer, log);
        commands_executed += 1u;
    }

    for (i = 0u; i < shell->plan_buffer.count; ++i) {
        const agent_plan* plan = &shell->plan_buffer.entries[i].plan;
        dom_agent_schedule_item* sched = dom_shell_schedule_for_agent(shell, plan->agent_id);
        if (!sched) {
            continue;
        }
        if (shell->plan_buffer.entries[i].valid != 0u &&
            plan->step_cursor < plan->step_count) {
            sched->active_plan_id = plan->plan_id;
            sched->active_goal_id = plan->goal_id;
            sched->resume_step = plan->step_cursor;
            sched->next_due_tick = plan->next_due_tick;
        } else {
            sched->active_plan_id = 0u;
            sched->active_goal_id = 0u;
            sched->resume_step = 0u;
        }
    }

    dom_shell_network_tick_all(shell, log, (dom_act_time_t)shell->tick);

    dom_shell_set_status(shell, "simulate=ok");
    if (emit_text) {
        printf("simulate=ok tick=%u commands=%u\n",
               (unsigned int)shell->tick,
               (unsigned int)commands_executed);
    }
    return 1;
}

static int dom_shell_field_name_to_id(const dom_shell_field_state* fields,
                                      const char* name,
                                      u32* out_id)
{
    u32 i;
    if (!fields || !name || !out_id) {
        return 0;
    }
    for (i = 0u; i < fields->field_count; ++i) {
        const dom_physical_field_desc* desc = dom_physical_field_desc_get(fields->field_ids[i]);
        if (desc && desc->name && strcmp(desc->name, name) == 0) {
            *out_id = desc->field_id;
            return 1;
        }
    }
    return 0;
}

static void dom_shell_format_q16(char* out, size_t cap, i32 value)
{
    if (!out || cap == 0u) {
        return;
    }
    if (value == DOM_FIELD_VALUE_UNKNOWN) {
        snprintf(out, cap, "unknown");
        return;
    }
    snprintf(out, cap, "%.3f", (double)value / 65536.0);
}

static void dom_shell_world_reset(dom_shell_world_state* world)
{
    if (!world) {
        return;
    }
    memset(world, 0, sizeof(*world));
    world->active = 0;
}

static void dom_shell_registry_init(dom_shell_registry* reg)
{
    if (!reg) {
        return;
    }
    memset(reg, 0, sizeof(*reg));
    strncpy(reg->templates[0].template_id, "builtin.empty_universe",
            DOM_SHELL_MAX_TEMPLATE_ID - 1u);
    strncpy(reg->templates[0].version, "1.0.0",
            DOM_SHELL_MAX_TEMPLATE_VERSION - 1u);
    strncpy(reg->templates[0].description, "Topology root only; valid but inert.",
            DOM_SHELL_MAX_TEMPLATE_DESC - 1u);
    strncpy(reg->templates[0].source, "built_in", sizeof(reg->templates[0].source) - 1u);

    strncpy(reg->templates[1].template_id, "builtin.minimal_system",
            DOM_SHELL_MAX_TEMPLATE_ID - 1u);
    strncpy(reg->templates[1].version, "1.0.0",
            DOM_SHELL_MAX_TEMPLATE_VERSION - 1u);
    strncpy(reg->templates[1].description, "One system and one body; spawn possible.",
            DOM_SHELL_MAX_TEMPLATE_DESC - 1u);
    strncpy(reg->templates[1].source, "built_in", sizeof(reg->templates[1].source) - 1u);

    strncpy(reg->templates[2].template_id, "builtin.realistic_test_universe",
            DOM_SHELL_MAX_TEMPLATE_ID - 1u);
    strncpy(reg->templates[2].version, "1.0.0",
            DOM_SHELL_MAX_TEMPLATE_VERSION - 1u);
    strncpy(reg->templates[2].description, "Labeled test universe with spheres; spawn at Earth label.",
            DOM_SHELL_MAX_TEMPLATE_DESC - 1u);
    strncpy(reg->templates[2].source, "built_in", sizeof(reg->templates[2].source) - 1u);

    reg->count = 3u;
}

static void dom_shell_write_node(dom_shell_builder* b, const dom_shell_node_def* node)
{
    uint32_t i;
    dom_shell_builder_append_char(b, '{');
    dom_shell_builder_append_text(b, "\"node_id\":");
    dom_shell_builder_append_json_string(b, node->node_id);
    if (node->parent_id && node->parent_id[0]) {
        dom_shell_builder_append_text(b, ",\"parent_refs\":[{\"node_id\":");
        dom_shell_builder_append_json_string(b, node->parent_id);
        dom_shell_builder_append_text(b, "}]");
    }
    if (node->tag_count > 0u) {
        dom_shell_builder_append_text(b, ",\"trait_tags\":[");
        for (i = 0u; i < node->tag_count; ++i) {
            if (i > 0u) {
                dom_shell_builder_append_char(b, ',');
            }
            dom_shell_builder_append_json_string(b, node->tags[i]);
        }
        dom_shell_builder_append_char(b, ']');
    }
    if (node->frame_id && node->frame_id[0]) {
        dom_shell_builder_append_text(b, ",\"coord_frame_ref\":{\"frame_id\":");
        dom_shell_builder_append_json_string(b, node->frame_id);
        dom_shell_builder_append_char(b, '}');
    }
    dom_shell_builder_append_char(b, '}');
}

static void dom_shell_write_edge(dom_shell_builder* b, const dom_shell_edge_def* edge)
{
    dom_shell_builder_append_text(b, "{\"parent_ref\":{\"node_id\":");
    dom_shell_builder_append_json_string(b, edge->parent_id);
    dom_shell_builder_append_text(b, "},\"child_ref\":{\"node_id\":");
    dom_shell_builder_append_json_string(b, edge->child_id);
    dom_shell_builder_append_text(b, "}}");
}

static int dom_shell_build_worlddef(const char* template_id,
                                    const char* template_version,
                                    uint64_t seed,
                                    const dom_shell_policy_set* movement,
                                    const dom_shell_policy_set* authority,
                                    const dom_shell_policy_set* mode,
                                    const dom_shell_policy_set* debug,
                                    const dom_shell_node_def* nodes,
                                    uint32_t node_count,
                                    const dom_shell_edge_def* edges,
                                    uint32_t edge_count,
                                    const char* spawn_node_id,
                                    const char* spawn_frame_id,
                                    char* out_json,
                                    size_t out_cap,
                                    dom_shell_world_summary* summary,
                                    char* err,
                                    size_t err_cap)
{
    dom_shell_builder b;
    char worlddef_id[DOM_SHELL_MAX_TEMPLATE_ID];
    uint32_t i;
    if (!template_id || !template_version || !nodes || node_count == 0u ||
        !spawn_node_id || !spawn_frame_id || !out_json || out_cap == 0u) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "invalid worlddef arguments");
        }
        return 0;
    }
    snprintf(worlddef_id, sizeof(worlddef_id), "%s.seed.%llu",
             template_id, (unsigned long long)seed);
    dom_shell_builder_init(&b, out_json, out_cap);
    dom_shell_builder_append_char(&b, '{');
    dom_shell_builder_append_text(&b, "\"schema_id\":");
    dom_shell_builder_append_json_string(&b, DOM_SHELL_WORLDDEF_SCHEMA_ID);
    dom_shell_builder_append_text(&b, ",\"schema_version\":");
    dom_shell_builder_appendf(&b, "%u", (unsigned int)DOM_SHELL_WORLDDEF_SCHEMA_VERSION);
    dom_shell_builder_append_text(&b, ",\"worlddef_id\":");
    dom_shell_builder_append_json_string(&b, worlddef_id);
    dom_shell_builder_append_text(&b, ",\"topology\":{\"root_node_ref\":{\"node_id\":");
    dom_shell_builder_append_json_string(&b, "universe.root");
    dom_shell_builder_append_text(&b, "},\"nodes\":[");
    for (i = 0u; i < node_count; ++i) {
        if (i > 0u) {
            dom_shell_builder_append_char(&b, ',');
        }
        dom_shell_write_node(&b, &nodes[i]);
        if (b.overflow) {
            break;
        }
    }
    dom_shell_builder_append_text(&b, "],\"edges\":[");
    for (i = 0u; i < edge_count; ++i) {
        if (i > 0u) {
            dom_shell_builder_append_char(&b, ',');
        }
        dom_shell_write_edge(&b, &edges[i]);
        if (b.overflow) {
            break;
        }
    }
    dom_shell_builder_append_text(&b, "]}");
    dom_shell_builder_append_text(&b, ",\"initial_fields\":[]");
    dom_shell_builder_append_text(&b, ",\"policy_sets\":{");
    dom_shell_builder_append_text(&b, "\"movement_policies\":");
    dom_shell_builder_append_policy_array(&b, movement);
    dom_shell_builder_append_text(&b, ",\"authority_policies\":");
    dom_shell_builder_append_policy_array(&b, authority);
    dom_shell_builder_append_text(&b, ",\"mode_policies\":");
    dom_shell_builder_append_policy_array(&b, mode);
    dom_shell_builder_append_text(&b, ",\"debug_policies\":");
    dom_shell_builder_append_policy_array(&b, debug);
    dom_shell_builder_append_char(&b, '}');
    dom_shell_builder_append_text(&b, ",\"spawn_spec\":{");
    dom_shell_builder_append_text(&b, "\"spawn_node_ref\":{\"node_id\":");
    dom_shell_builder_append_json_string(&b, spawn_node_id);
    dom_shell_builder_append_text(&b, "},\"coordinate_frame_ref\":{\"frame_id\":");
    dom_shell_builder_append_json_string(&b, spawn_frame_id);
    dom_shell_builder_append_text(&b, "},\"position\":{\"value\":{\"x\":0,\"y\":0,\"z\":0}},");
    dom_shell_builder_append_text(&b, "\"orientation\":{\"value\":{\"yaw\":0,\"pitch\":0,\"roll\":0}}");
    dom_shell_builder_append_char(&b, '}');
    dom_shell_builder_append_text(&b, ",\"provenance\":{");
    dom_shell_builder_append_text(&b, "\"template_id\":");
    dom_shell_builder_append_json_string(&b, template_id);
    dom_shell_builder_append_text(&b, ",\"template_version\":");
    dom_shell_builder_append_json_string(&b, template_version);
    dom_shell_builder_append_text(&b, ",\"generator_source\":");
    dom_shell_builder_append_json_string(&b, "built_in");
    dom_shell_builder_append_text(&b, ",\"seed\":{\"primary\":");
    dom_shell_builder_appendf(&b, "%llu", (unsigned long long)seed);
    dom_shell_builder_append_text(&b, "},\"template_params\":{\"seed.primary\":");
    dom_shell_builder_appendf(&b, "%llu", (unsigned long long)seed);
    dom_shell_builder_append_text(&b, "}}");
    dom_shell_builder_append_text(&b, ",\"extensions\":{}");
    dom_shell_builder_append_char(&b, '}');
    if (b.overflow) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "worlddef buffer overflow");
        }
        return 0;
    }
    if (summary) {
        memset(summary, 0, sizeof(*summary));
        strncpy(summary->worlddef_id, worlddef_id, sizeof(summary->worlddef_id) - 1u);
        strncpy(summary->template_id, template_id, sizeof(summary->template_id) - 1u);
        summary->schema_version = DOM_SHELL_WORLDDEF_SCHEMA_VERSION;
        strncpy(summary->spawn_node_id, spawn_node_id, sizeof(summary->spawn_node_id) - 1u);
        strncpy(summary->spawn_frame_id, spawn_frame_id, sizeof(summary->spawn_frame_id) - 1u);
        summary->spawn_pos[0] = 0.0;
        summary->spawn_pos[1] = 0.0;
        summary->spawn_pos[2] = 0.0;
        summary->spawn_orient[0] = 0.0;
        summary->spawn_orient[1] = 0.0;
        summary->spawn_orient[2] = 0.0;
        dom_shell_policy_set_copy(&summary->movement, movement);
        dom_shell_policy_set_copy(&summary->authority, authority);
        dom_shell_policy_set_copy(&summary->mode, mode);
        dom_shell_policy_set_copy(&summary->debug, debug);
    }
    return 1;
}

static int dom_shell_build_empty_universe(uint64_t seed,
                                          const dom_shell_policy_set* movement,
                                          const dom_shell_policy_set* authority,
                                          const dom_shell_policy_set* mode,
                                          const dom_shell_policy_set* debug,
                                          char* out_json,
                                          size_t out_cap,
                                          dom_shell_world_summary* summary,
                                          char* err,
                                          size_t err_cap)
{
    static const dom_shell_node_def nodes[] = {
        { "universe.root", 0, "frame.universe.root", { "topology.universe" }, 1u }
    };
    return dom_shell_build_worlddef("builtin.empty_universe", "1.0.0", seed,
                                    movement, authority, mode, debug,
                                    nodes, 1u, 0, 0u,
                                    "universe.root", "frame.universe.root",
                                    out_json, out_cap, summary, err, err_cap);
}

static int dom_shell_build_minimal_system(uint64_t seed,
                                          const dom_shell_policy_set* movement,
                                          const dom_shell_policy_set* authority,
                                          const dom_shell_policy_set* mode,
                                          const dom_shell_policy_set* debug,
                                          char* out_json,
                                          size_t out_cap,
                                          dom_shell_world_summary* summary,
                                          char* err,
                                          size_t err_cap)
{
    static const dom_shell_node_def nodes[] = {
        { "universe.root", 0, "frame.universe.root", { "topology.universe" }, 1u },
        { "system.minimal", "universe.root", "frame.system.minimal", { "topology.system" }, 1u },
        { "body.minimal.primary", "system.minimal", "frame.body.minimal.primary",
          { "topology.body", "body.sphere" }, 2u }
    };
    static const dom_shell_edge_def edges[] = {
        { "universe.root", "system.minimal" },
        { "system.minimal", "body.minimal.primary" }
    };
    return dom_shell_build_worlddef("builtin.minimal_system", "1.0.0", seed,
                                    movement, authority, mode, debug,
                                    nodes, 3u, edges, 2u,
                                    "body.minimal.primary", "frame.body.minimal.primary",
                                    out_json, out_cap, summary, err, err_cap);
}

static int dom_shell_build_realistic_test(uint64_t seed,
                                          const dom_shell_policy_set* movement,
                                          const dom_shell_policy_set* authority,
                                          const dom_shell_policy_set* mode,
                                          const dom_shell_policy_set* debug,
                                          char* out_json,
                                          size_t out_cap,
                                          dom_shell_world_summary* summary,
                                          char* err,
                                          size_t err_cap)
{
    static const dom_shell_node_def nodes[] = {
        { "universe.root", 0, "frame.universe.root", { "topology.universe" }, 1u },
        { "galaxy.test", "universe.root", "frame.galaxy.test", { "topology.galaxy" }, 1u },
        { "system.test", "galaxy.test", "frame.system.test", { "topology.system" }, 1u },
        { "body.sun", "system.test", "frame.body.sun", { "topology.body", "body.sphere", "body.star" }, 3u },
        { "body.mercury", "system.test", "frame.body.mercury", { "topology.body", "body.sphere", "body.rocky" }, 3u },
        { "body.venus", "system.test", "frame.body.venus", { "topology.body", "body.sphere", "body.rocky" }, 3u },
        { "body.earth", "system.test", "frame.body.earth",
          { "topology.body", "body.sphere", "body.rocky", "body.spawn" }, 4u },
        { "body.mars", "system.test", "frame.body.mars", { "topology.body", "body.sphere", "body.rocky" }, 3u },
        { "body.jupiter", "system.test", "frame.body.jupiter",
          { "topology.body", "body.sphere", "body.gas_giant" }, 3u },
        { "body.saturn", "system.test", "frame.body.saturn",
          { "topology.body", "body.sphere", "body.gas_giant" }, 3u },
        { "body.uranus", "system.test", "frame.body.uranus",
          { "topology.body", "body.sphere", "body.gas_giant" }, 3u },
        { "body.neptune", "system.test", "frame.body.neptune",
          { "topology.body", "body.sphere", "body.gas_giant" }, 3u }
    };
    static const dom_shell_edge_def edges[] = {
        { "universe.root", "galaxy.test" },
        { "galaxy.test", "system.test" },
        { "system.test", "body.sun" },
        { "system.test", "body.mercury" },
        { "system.test", "body.venus" },
        { "system.test", "body.earth" },
        { "system.test", "body.mars" },
        { "system.test", "body.jupiter" },
        { "system.test", "body.saturn" },
        { "system.test", "body.uranus" },
        { "system.test", "body.neptune" }
    };
    return dom_shell_build_worlddef("builtin.realistic_test_universe", "1.0.0", seed,
                                    movement, authority, mode, debug,
                                    nodes, 12u, edges, 11u,
                                    "body.earth", "frame.body.earth",
                                    out_json, out_cap, summary, err, err_cap);
}

static int dom_shell_generate_builtin(const dom_shell_template* entry,
                                      uint64_t seed,
                                      const dom_shell_policy_set* movement,
                                      const dom_shell_policy_set* authority,
                                      const dom_shell_policy_set* mode,
                                      const dom_shell_policy_set* debug,
                                      dom_shell_world_state* world,
                                      char* err,
                                      size_t err_cap)
{
    int ok = 0;
    if (!entry || !world) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "template missing");
        }
        return 0;
    }
    if (strcmp(entry->template_id, "builtin.empty_universe") == 0) {
        ok = dom_shell_build_empty_universe(seed, movement, authority, mode, debug,
                                            world->worlddef_json,
                                            sizeof(world->worlddef_json),
                                            &world->summary, err, err_cap);
    } else if (strcmp(entry->template_id, "builtin.minimal_system") == 0) {
        ok = dom_shell_build_minimal_system(seed, movement, authority, mode, debug,
                                            world->worlddef_json,
                                            sizeof(world->worlddef_json),
                                            &world->summary, err, err_cap);
    } else if (strcmp(entry->template_id, "builtin.realistic_test_universe") == 0) {
        ok = dom_shell_build_realistic_test(seed, movement, authority, mode, debug,
                                            world->worlddef_json,
                                            sizeof(world->worlddef_json),
                                            &world->summary, err, err_cap);
    } else {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "template not found");
        }
        return 0;
    }
    if (!ok) {
        return 0;
    }
    world->worlddef_len = strlen(world->worlddef_json);
    world->worlddef_hash = dom_shell_hash64(world->worlddef_json, world->worlddef_len);
    return 1;
}

void dom_client_shell_init(dom_client_shell* shell)
{
    if (!shell) {
        return;
    }
    memset(shell, 0, sizeof(*shell));
    dom_shell_registry_init(&shell->registry);
    dom_shell_world_reset(&shell->world);
    dom_shell_policy_set_clear(&shell->create_movement);
    dom_shell_policy_set_clear(&shell->create_authority);
    dom_shell_policy_set_clear(&shell->create_mode);
    dom_shell_policy_set_clear(&shell->create_debug);
    dom_shell_policy_set_add(&shell->create_authority, DOM_SHELL_AUTH_POLICY);
    dom_shell_policy_set_add(&shell->create_mode, DOM_SHELL_MODE_FREE);
    shell->create_template_index = 0u;
    shell->create_seed = 0u;
    shell->events.head = 0u;
    shell->events.count = 0u;
    shell->events.seq = 0u;
    shell->tick = 0u;
    shell->last_status[0] = '\0';
    shell->last_refusal_code[0] = '\0';
    shell->last_refusal_detail[0] = '\0';
    dom_shell_local_reset(shell);
}

void dom_client_shell_reset(dom_client_shell* shell)
{
    if (!shell) {
        return;
    }
    dom_shell_world_reset(&shell->world);
    shell->events.head = 0u;
    shell->events.count = 0u;
    shell->events.seq = 0u;
    shell->tick = 0u;
    shell->last_status[0] = '\0';
    shell->last_refusal_code[0] = '\0';
    shell->last_refusal_detail[0] = '\0';
    dom_shell_local_reset(shell);
}

void dom_client_shell_tick(dom_client_shell* shell)
{
    if (!shell) {
        return;
    }
    shell->tick += 1u;
}

const dom_shell_registry* dom_client_shell_registry(const dom_client_shell* shell)
{
    return shell ? &shell->registry : 0;
}

const dom_shell_world_state* dom_client_shell_world(const dom_client_shell* shell)
{
    return shell ? &shell->world : 0;
}

const dom_shell_event_ring* dom_client_shell_events(const dom_client_shell* shell)
{
    return shell ? &shell->events : 0;
}

int dom_client_shell_set_create_seed(dom_client_shell* shell, uint64_t seed)
{
    if (!shell) {
        return 0;
    }
    shell->create_seed = seed;
    return 1;
}

int dom_client_shell_set_create_template(dom_client_shell* shell, uint32_t index)
{
    if (!shell) {
        return 0;
    }
    if (index >= shell->registry.count) {
        return 0;
    }
    shell->create_template_index = index;
    return 1;
}

int dom_client_shell_set_create_policy(dom_client_shell* shell, const char* set_name, const char* csv)
{
    if (!shell || !set_name) {
        return 0;
    }
    if (strcmp(set_name, "policy.movement") == 0 || strcmp(set_name, "movement") == 0) {
        dom_shell_policy_set_from_csv(&shell->create_movement, csv);
        return 1;
    }
    if (strcmp(set_name, "policy.authority") == 0 || strcmp(set_name, "authority") == 0) {
        dom_shell_policy_set_from_csv(&shell->create_authority, csv);
        return 1;
    }
    if (strcmp(set_name, "policy.mode") == 0 || strcmp(set_name, "mode") == 0) {
        dom_shell_policy_set_from_csv(&shell->create_mode, csv);
        return 1;
    }
    if (strcmp(set_name, "policy.debug") == 0 || strcmp(set_name, "debug") == 0) {
        dom_shell_policy_set_from_csv(&shell->create_debug, csv);
        return 1;
    }
    return 0;
}

static int dom_shell_parse_u64(const char* text, uint64_t* out_value)
{
    char* end = 0;
    unsigned long long value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtoull(text, &end, 10);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = (uint64_t)value;
    return 1;
}

static int dom_shell_extract_seed(const char* worlddef_id, uint64_t* out_seed)
{
    const char* tag = ".seed.";
    const char* pos;
    if (!out_seed) {
        return 0;
    }
    *out_seed = 0u;
    if (!worlddef_id) {
        return 0;
    }
    pos = strstr(worlddef_id, tag);
    if (!pos) {
        return 0;
    }
    pos += strlen(tag);
    return dom_shell_parse_u64(pos, out_seed);
}

static void dom_shell_sync_world_pose(dom_shell_world_state* world)
{
    if (!world) {
        return;
    }
    world->position[0] = world->summary.spawn_pos[0];
    world->position[1] = world->summary.spawn_pos[1];
    world->position[2] = world->summary.spawn_pos[2];
    world->orientation[0] = world->summary.spawn_orient[0];
    world->orientation[1] = world->summary.spawn_orient[1];
    world->orientation[2] = world->summary.spawn_orient[2];
}

int dom_client_shell_create_world(dom_client_shell* shell,
                                  dom_app_ui_event_log* log,
                                  char* status,
                                  size_t status_cap,
                                  int emit_text)
{
    const dom_shell_template* entry;
    char err[96];
    if (!shell) {
        return D_APP_EXIT_FAILURE;
    }
    shell->last_refusal_code[0] = '\0';
    shell->last_refusal_detail[0] = '\0';
    if (shell->create_template_index >= shell->registry.count) {
        dom_shell_set_refusal(shell, DOM_REFUSAL_TEMPLATE, "template index out of range");
        dom_shell_set_status(shell, "world_create=refused");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            fprintf(stderr, "client: world create refused (template index)\n");
        }
        return D_APP_EXIT_UNAVAILABLE;
    }
    entry = &shell->registry.templates[shell->create_template_index];
    err[0] = '\0';
    if (!dom_shell_generate_builtin(entry, shell->create_seed,
                                    &shell->create_movement,
                                    &shell->create_authority,
                                    &shell->create_mode,
                                    &shell->create_debug,
                                    &shell->world,
                                    err, sizeof(err))) {
        dom_shell_set_refusal(shell, DOM_REFUSAL_TEMPLATE, err[0] ? err : "template failed");
        dom_shell_set_status(shell, "world_create=refused");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            fprintf(stderr, "client: world create refused (%s)\n",
                    err[0] ? err : "template failure");
        }
        dom_shell_emit(shell, log, "client.world.create",
                       "result=refused");
        return D_APP_EXIT_UNAVAILABLE;
    }
    shell->world.active = 1;
    strncpy(shell->world.current_node_id,
            shell->world.summary.spawn_node_id,
            sizeof(shell->world.current_node_id) - 1u);
    dom_shell_sync_world_pose(&shell->world);
    shell->world.active_mode[0] = '\0';
    if (shell->world.summary.mode.count > 0u) {
        strncpy(shell->world.active_mode,
                shell->world.summary.mode.items[0],
                sizeof(shell->world.active_mode) - 1u);
    }
    dom_shell_fields_init(&shell->fields);
    dom_shell_structure_init(&shell->structure);
    dom_shell_agents_reset(shell);
    dom_shell_networks_reset(shell);
    shell->fields.knowledge_mask = 0u;
    shell->fields.confidence_q16 = 0u;
    shell->fields.uncertainty_q16 = 0u;
    shell->last_intent[0] = '\0';
    shell->last_plan[0] = '\0';
    shell->next_intent_id = 1u;
    shell->rng_seed = shell->create_seed ? shell->create_seed : 1u;
    dom_shell_set_status(shell, "world_create=ok");
    if (status && status_cap > 0u) {
        snprintf(status, status_cap, "%s", shell->last_status);
    }
    if (emit_text) {
        printf("world_create=ok\n");
        printf("worlddef_id=%s\n", shell->world.summary.worlddef_id);
        printf("template_id=%s\n", shell->world.summary.template_id);
    }
    {
        char detail[128];
        snprintf(detail, sizeof(detail),
                 "template_id=%s seed=%llu result=ok",
                 entry->template_id, (unsigned long long)shell->create_seed);
        dom_shell_emit(shell, log, "client.world.create", detail);
    }
    return D_APP_EXIT_OK;
}

static int dom_shell_write_save(dom_client_shell* shell, const char* path, char* err, size_t err_cap)
{
    FILE* f;
    char csv[256];
    if (!shell || !path || !path[0]) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "save path missing");
        }
        return 0;
    }
    f = fopen(path, "w");
    if (!f) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "save open failed");
        }
        return 0;
    }
    fprintf(f, "%s\n", DOM_SHELL_SAVE_HEADER);
    fprintf(f, "worlddef_len=%u\n", (unsigned int)shell->world.worlddef_len);
    fprintf(f, "worlddef_hash=0x%016llx\n", (unsigned long long)shell->world.worlddef_hash);
    fprintf(f, "worlddef_begin\n");
    if (shell->world.worlddef_len > 0u) {
        fwrite(shell->world.worlddef_json, 1u, shell->world.worlddef_len, f);
    }
    fputc('\n', f);
    fprintf(f, "worlddef_end\n");
    fprintf(f, "summary_begin\n");
    fprintf(f, "worlddef_id=%s\n", shell->world.summary.worlddef_id);
    fprintf(f, "template_id=%s\n", shell->world.summary.template_id);
    fprintf(f, "schema_version=%u\n", (unsigned int)shell->world.summary.schema_version);
    fprintf(f, "spawn_node_id=%s\n", shell->world.summary.spawn_node_id);
    fprintf(f, "spawn_frame_id=%s\n", shell->world.summary.spawn_frame_id);
    fprintf(f, "spawn_pos=%.3f,%.3f,%.3f\n",
            shell->world.summary.spawn_pos[0],
            shell->world.summary.spawn_pos[1],
            shell->world.summary.spawn_pos[2]);
    fprintf(f, "spawn_orient=%.3f,%.3f,%.3f\n",
            shell->world.summary.spawn_orient[0],
            shell->world.summary.spawn_orient[1],
            shell->world.summary.spawn_orient[2]);
    dom_client_shell_policy_to_csv(&shell->world.summary.movement, csv, sizeof(csv));
    fprintf(f, "policy.movement=%s\n", csv);
    dom_client_shell_policy_to_csv(&shell->world.summary.authority, csv, sizeof(csv));
    fprintf(f, "policy.authority=%s\n", csv);
    dom_client_shell_policy_to_csv(&shell->world.summary.mode, csv, sizeof(csv));
    fprintf(f, "policy.mode=%s\n", csv);
    dom_client_shell_policy_to_csv(&shell->world.summary.debug, csv, sizeof(csv));
    fprintf(f, "policy.debug=%s\n", csv);
    fprintf(f, "summary_end\n");
    fprintf(f, "local_begin\n");
    fprintf(f, "tick=%u\n", (unsigned int)shell->tick);
    fprintf(f, "rng_seed=%llu\n", (unsigned long long)shell->rng_seed);
    fprintf(f, "knowledge_mask=0x%08x\n", (unsigned int)shell->fields.knowledge_mask);
    fprintf(f, "confidence_q16=%u\n", (unsigned int)shell->fields.confidence_q16);
    fprintf(f, "uncertainty_q16=%u\n", (unsigned int)shell->fields.uncertainty_q16);
    if (shell->fields.field_count > 0u) {
        u32 i;
        for (i = 0u; i < shell->fields.field_count; ++i) {
            u32 field_id = shell->fields.field_ids[i];
            i32 obj = DOM_FIELD_VALUE_UNKNOWN;
            i32 subj = DOM_FIELD_VALUE_UNKNOWN;
            (void)dom_field_get_value(&shell->fields.objective, field_id, 0u, 0u, &obj);
            (void)dom_field_get_value(&shell->fields.subjective, field_id, 0u, 0u, &subj);
            fprintf(f,
                    "field id=%u objective=%d subjective=%d known=%u\n",
                    (unsigned int)field_id,
                    (int)obj,
                    (int)subj,
                    (shell->fields.knowledge_mask & DOM_FIELD_BIT(field_id)) ? 1u : 0u);
        }
    }
    fprintf(f, "structure_built=%u\n", (unsigned int)shell->structure.structure.built);
    fprintf(f, "structure_failed=%u\n", (unsigned int)shell->structure.structure.failed);
    {
        dom_network_edge* edge = dom_network_find_edge(&shell->structure.network, 1u);
        fprintf(f, "energy_edge_status=%u\n",
                edge ? (unsigned int)edge->status : 0u);
    }
    fprintf(f, "local_end\n");
    fprintf(f, "agents_begin\n");
    fprintf(f, "next_agent_id=%llu\n", (unsigned long long)shell->next_agent_id);
    fprintf(f, "possessed_agent_id=%llu\n", (unsigned long long)shell->possessed_agent_id);
    if (shell->agent_count > 0u) {
        u32 i;
        for (i = 0u; i < shell->agent_count; ++i) {
            const dom_shell_agent_record* record = &shell->agents[i];
            const dom_agent_schedule_item* sched = &shell->schedules[i];
            const dom_agent_belief* belief = &shell->beliefs[i];
            const dom_agent_capability* cap = &shell->caps[i];
            fprintf(f,
                    "agent id=%llu caps=%u auth=%u know=%u record_goal_id=%llu record_goal_type=%u "
                    "record_refusal=%u sched_next=%llu sched_status=%u sched_budget=%u "
                    "sched_goal=%llu sched_plan=%llu sched_resume=%u hunger=%u threat=%u "
                    "risk_q16=%u ep_conf=%u resource_ref=%llu threat_ref=%llu dest_ref=%llu\n",
                    (unsigned long long)record->agent_id,
                    (unsigned int)cap->capability_mask,
                    (unsigned int)cap->authority_mask,
                    (unsigned int)belief->knowledge_mask,
                    (unsigned long long)record->last_goal_id,
                    (unsigned int)record->last_goal_type,
                    (unsigned int)record->last_refusal,
                    (unsigned long long)sched->next_due_tick,
                    (unsigned int)sched->status,
                    (unsigned int)sched->compute_budget,
                    (unsigned long long)sched->active_goal_id,
                    (unsigned long long)sched->active_plan_id,
                    (unsigned int)sched->resume_step,
                    (unsigned int)belief->hunger_level,
                    (unsigned int)belief->threat_level,
                    (unsigned int)belief->risk_tolerance_q16,
                    (unsigned int)belief->epistemic_confidence_q16,
                    (unsigned long long)belief->known_resource_ref,
                    (unsigned long long)belief->known_threat_ref,
                    (unsigned long long)belief->known_destination_ref);
        }
    }
    fprintf(f, "agents_end\n");
    fprintf(f, "goals_begin\n");
    fprintf(f, "next_goal_id=%llu\n", (unsigned long long)shell->goal_registry.next_goal_id);
    if (shell->goal_registry.count > 0u) {
        u32 i;
        for (i = 0u; i < shell->goal_registry.count; ++i) {
            const agent_goal* goal = &shell->goal_registry.goals[i];
            u32 c;
            fprintf(f,
                    "goal id=%llu agent=%llu type=%u status=%u flags=%u base_priority=%u "
                    "urgency=%u acceptable_risk_q16=%u horizon_act=%llu epistemic_confidence_q16=%u "
                    "precond_caps=%u precond_auth=%u precond_know=%u satisfaction_flags=%u "
                    "expiry_act=%llu failure_count=%u oscillation_count=%u abandon_after_failures=%u "
                    "abandon_after_act=%llu defer_until_act=%llu conflict_group=%u last_update_act=%llu "
                    "condition_count=%u",
                    (unsigned long long)goal->goal_id,
                    (unsigned long long)goal->agent_id,
                    (unsigned int)goal->type,
                    (unsigned int)goal->status,
                    (unsigned int)goal->flags,
                    (unsigned int)goal->base_priority,
                    (unsigned int)goal->urgency,
                    (unsigned int)goal->acceptable_risk_q16,
                    (unsigned long long)goal->horizon_act,
                    (unsigned int)goal->epistemic_confidence_q16,
                    (unsigned int)goal->preconditions.required_capabilities,
                    (unsigned int)goal->preconditions.required_authority,
                    (unsigned int)goal->preconditions.required_knowledge,
                    (unsigned int)goal->satisfaction_flags,
                    (unsigned long long)goal->expiry_act,
                    (unsigned int)goal->failure_count,
                    (unsigned int)goal->oscillation_count,
                    (unsigned int)goal->abandon_after_failures,
                    (unsigned long long)goal->abandon_after_act,
                    (unsigned long long)goal->defer_until_act,
                    (unsigned int)goal->conflict_group,
                    (unsigned long long)goal->last_update_act,
                    (unsigned int)goal->condition_count);
            for (c = 0u; c < goal->condition_count && c < AGENT_GOAL_MAX_CONDITIONS; ++c) {
                const agent_goal_condition* cond = &goal->conditions[c];
                fprintf(f,
                        " cond%u=%u,%llu,%d,%u",
                        (unsigned int)c,
                        (unsigned int)cond->kind,
                        (unsigned long long)cond->subject_ref,
                        (int)cond->threshold,
                        (unsigned int)cond->flags);
            }
            fprintf(f, "\n");
        }
    }
    fprintf(f, "goals_end\n");
    fprintf(f, "delegations_begin\n");
    fprintf(f, "next_delegation_id=%llu\n", (unsigned long long)shell->next_delegation_id);
    if (shell->delegation_registry.count > 0u) {
        u32 i;
        for (i = 0u; i < shell->delegation_registry.count; ++i) {
            const agent_delegation* del = &shell->delegations[i];
            fprintf(f,
                    "delegation id=%llu delegator=%llu delegatee=%llu kind=%u process=%u authority=%u "
                    "expiry=%llu provenance=%llu revoked=%u\n",
                    (unsigned long long)del->delegation_id,
                    (unsigned long long)del->delegator_ref,
                    (unsigned long long)del->delegatee_ref,
                    (unsigned int)del->delegation_kind,
                    (unsigned int)del->allowed_process_mask,
                    (unsigned int)del->authority_mask,
                    (unsigned long long)del->expiry_act,
                    (unsigned long long)del->provenance_ref,
                    (unsigned int)del->revoked);
        }
    }
    fprintf(f, "delegations_end\n");
    fprintf(f, "authority_begin\n");
    fprintf(f, "next_authority_id=%llu\n", (unsigned long long)shell->next_authority_id);
    if (shell->authority_registry.count > 0u) {
        u32 i;
        for (i = 0u; i < shell->authority_registry.count; ++i) {
            const agent_authority_grant* grant = &shell->authority_grants[i];
            fprintf(f,
                    "grant id=%llu granter=%llu grantee=%llu authority=%u expiry=%llu provenance=%llu revoked=%u\n",
                    (unsigned long long)grant->grant_id,
                    (unsigned long long)grant->granter_id,
                    (unsigned long long)grant->grantee_id,
                    (unsigned int)grant->authority_mask,
                    (unsigned long long)grant->expiry_act,
                    (unsigned long long)grant->provenance_id,
                    (unsigned int)grant->revoked);
        }
    }
    fprintf(f, "authority_end\n");
    fprintf(f, "constraints_begin\n");
    fprintf(f, "next_constraint_id=%llu\n", (unsigned long long)shell->next_constraint_id);
    if (shell->constraint_registry.count > 0u) {
        u32 i;
        for (i = 0u; i < shell->constraint_registry.count; ++i) {
            const agent_constraint* constraint = &shell->constraints[i];
            fprintf(f,
                    "constraint id=%llu institution=%llu target=%llu process=%u mode=%u expiry=%llu "
                    "provenance=%llu revoked=%u\n",
                    (unsigned long long)constraint->constraint_id,
                    (unsigned long long)constraint->institution_id,
                    (unsigned long long)constraint->target_agent_id,
                    (unsigned int)constraint->process_kind_mask,
                    (unsigned int)constraint->mode,
                    (unsigned long long)constraint->expiry_act,
                    (unsigned long long)constraint->provenance_id,
                    (unsigned int)constraint->revoked);
        }
    }
    fprintf(f, "constraints_end\n");
    fprintf(f, "institutions_begin\n");
    fprintf(f, "next_institution_id=%llu\n", (unsigned long long)shell->next_institution_id);
    if (shell->institution_registry.count > 0u) {
        u32 i;
        for (i = 0u; i < shell->institution_registry.count; ++i) {
            const agent_institution* inst = &shell->institutions[i];
            fprintf(f,
                    "institution id=%llu agent=%llu authority=%u legitimacy_q16=%u status=%u "
                    "founded_act=%llu collapsed_act=%llu provenance=%llu flags=%u\n",
                    (unsigned long long)inst->institution_id,
                    (unsigned long long)inst->agent_id,
                    (unsigned int)inst->authority_mask,
                    (unsigned int)inst->legitimacy_q16,
                    (unsigned int)inst->status,
                    (unsigned long long)inst->founded_act,
                    (unsigned long long)inst->collapsed_act,
                    (unsigned long long)inst->provenance_id,
                    (unsigned int)inst->flags);
        }
    }
    fprintf(f, "institutions_end\n");
    fprintf(f, "networks_begin\n");
    fprintf(f, "next_network_id=%llu\n", (unsigned long long)shell->next_network_id);
    if (shell->network_count > 0u) {
        u32 i;
        for (i = 0u; i < shell->network_count; ++i) {
            const dom_shell_network_state* net = &shell->networks[i];
            u32 n;
            u32 e;
            fprintf(f,
                    "network id=%llu type=%u nodes=%u edges=%u\n",
                    (unsigned long long)net->network_id,
                    (unsigned int)net->graph.type,
                    (unsigned int)net->graph.node_count,
                    (unsigned int)net->graph.edge_count);
            for (n = 0u; n < net->graph.node_count; ++n) {
                const dom_network_node* node = &net->nodes[n];
                fprintf(f,
                        "node network=%llu id=%llu status=%u capacity_q16=%d stored_q16=%d loss_q16=%d min_required_q16=%d\n",
                        (unsigned long long)net->network_id,
                        (unsigned long long)node->node_id,
                        (unsigned int)node->status,
                        (int)node->capacity_q16,
                        (int)node->stored_q16,
                        (int)node->loss_q16,
                        (int)node->min_required_q16);
            }
            for (e = 0u; e < net->graph.edge_count; ++e) {
                const dom_network_edge* edge = &net->edges[e];
                fprintf(f,
                        "edge network=%llu id=%llu a=%llu b=%llu status=%u capacity_q16=%d loss_q16=%d\n",
                        (unsigned long long)net->network_id,
                        (unsigned long long)edge->edge_id,
                        (unsigned long long)edge->a,
                        (unsigned long long)edge->b,
                        (unsigned int)edge->status,
                        (int)edge->capacity_q16,
                        (int)edge->loss_q16);
            }
        }
    }
    fprintf(f, "networks_end\n");
    fprintf(f, "events_begin\n");
    if (shell->events.count > 0u) {
        uint32_t i;
        uint32_t idx = shell->events.head;
        for (i = 0u; i < shell->events.count; ++i) {
            fprintf(f, "%s\n", shell->events.lines[idx]);
            idx = (idx + 1u) % DOM_SHELL_MAX_EVENTS;
        }
    }
    fprintf(f, "events_end\n");
    fclose(f);
    return 1;
}

int dom_client_shell_save_world(dom_client_shell* shell,
                                const char* path,
                                dom_app_ui_event_log* log,
                                char* status,
                                size_t status_cap,
                                int emit_text)
{
    char err[96];
    const char* out_path = path && path[0] ? path : DOM_SHELL_DEFAULT_SAVE_PATH;
    if (!shell || !shell->world.active) {
        dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "no active world");
        dom_shell_set_status(shell, "world_save=refused");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            fprintf(stderr, "client: save refused (no active world)\n");
        }
        return D_APP_EXIT_UNAVAILABLE;
    }
    err[0] = '\0';
    if (!dom_shell_write_save(shell, out_path, err, sizeof(err))) {
        dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, err[0] ? err : "save failed");
        dom_shell_set_status(shell, "world_save=refused");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            fprintf(stderr, "client: save refused (%s)\n", err[0] ? err : "save failed");
        }
        dom_shell_emit(shell, log, "client.world.save", "result=refused");
        return D_APP_EXIT_FAILURE;
    }
    dom_shell_set_status(shell, "world_save=ok");
    if (status && status_cap > 0u) {
        snprintf(status, status_cap, "%s", shell->last_status);
    }
    if (emit_text) {
        printf("world_save=ok path=%s\n", out_path);
    }
    {
        char detail[128];
        snprintf(detail, sizeof(detail), "path=%s result=ok", out_path);
        dom_shell_emit(shell, log, "client.world.save", detail);
    }
    return D_APP_EXIT_OK;
}

static int dom_shell_parse_vec3(const char* text, double* out_values)
{
    char buf[96];
    char* token;
    char* comma;
    int i = 0;
    size_t len;
    if (!text || !out_values) {
        return 0;
    }
    len = strlen(text);
    if (len >= sizeof(buf)) {
        len = sizeof(buf) - 1u;
    }
    memcpy(buf, text, len);
    buf[len] = '\0';
    token = buf;
    while (token && i < 3) {
        comma = strchr(token, ',');
        if (comma) {
            *comma = '\0';
        }
        out_values[i++] = strtod(token, 0);
        token = comma ? (comma + 1u) : 0;
    }
    return (i == 3);
}

static int dom_shell_load_save_file(dom_client_shell* shell, const char* path, char* err, size_t err_cap)
{
    FILE* f;
    char line[DOM_SHELL_WORLDDEF_MAX];
    int have_header = 0;
    int in_worlddef = 0;
    int in_summary = 0;
    int in_local = 0;
    int in_events = 0;
    int have_summary = 0;
    int in_agents = 0;
    int in_goals = 0;
    int in_delegations = 0;
    int in_authority = 0;
    int in_constraints = 0;
    int in_institutions = 0;
    int in_networks = 0;
    u64 max_agent_id = 0u;
    u64 max_goal_id = 0u;
    u64 max_delegation_id = 0u;
    u64 max_authority_id = 0u;
    u64 max_constraint_id = 0u;
    u64 max_institution_id = 0u;
    u64 max_network_id = 0u;
    u64 next_agent_id = 0u;
    u64 next_goal_id = 0u;
    u64 next_delegation_id = 0u;
    u64 next_authority_id = 0u;
    u64 next_constraint_id = 0u;
    u64 next_institution_id = 0u;
    u64 next_network_id = 0u;
    u64 possessed_agent_id = 0u;
    if (!shell || !path || !path[0]) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "load path missing");
        }
        return 0;
    }
    f = fopen(path, "r");
    if (!f) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "load open failed");
        }
        return 0;
    }
    dom_shell_world_reset(&shell->world);
    dom_shell_local_reset(shell);
    shell->tick = 0u;
    shell->events.head = 0u;
    shell->events.count = 0u;
    while (fgets(line, sizeof(line), f)) {
        size_t len = strlen(line);
        while (len > 0u && (line[len - 1u] == '\n' || line[len - 1u] == '\r')) {
            line[--len] = '\0';
        }
        if (!have_header) {
            if (strcmp(line, DOM_SHELL_SAVE_HEADER) != 0) {
                fclose(f);
                if (err && err_cap > 0u) {
                    snprintf(err, err_cap, "save header mismatch");
                }
                return 0;
            }
            have_header = 1;
            continue;
        }
        if (strcmp(line, "worlddef_begin") == 0) {
            in_worlddef = 1;
            continue;
        }
        if (strcmp(line, "worlddef_end") == 0) {
            in_worlddef = 0;
            continue;
        }
        if (strcmp(line, "summary_begin") == 0) {
            in_summary = 1;
            continue;
        }
        if (strcmp(line, "summary_end") == 0) {
            in_summary = 0;
            have_summary = 1;
            continue;
        }
        if (strcmp(line, "local_begin") == 0) {
            in_local = 1;
            continue;
        }
        if (strcmp(line, "local_end") == 0) {
            in_local = 0;
            continue;
        }
        if (strcmp(line, "events_begin") == 0) {
            in_events = 1;
            continue;
        }
        if (strcmp(line, "events_end") == 0) {
            in_events = 0;
            continue;
        }
        if (strcmp(line, "agents_begin") == 0) {
            in_agents = 1;
            continue;
        }
        if (strcmp(line, "agents_end") == 0) {
            in_agents = 0;
            continue;
        }
        if (strcmp(line, "goals_begin") == 0) {
            in_goals = 1;
            continue;
        }
        if (strcmp(line, "goals_end") == 0) {
            in_goals = 0;
            continue;
        }
        if (strcmp(line, "delegations_begin") == 0) {
            in_delegations = 1;
            continue;
        }
        if (strcmp(line, "delegations_end") == 0) {
            in_delegations = 0;
            continue;
        }
        if (strcmp(line, "authority_begin") == 0) {
            in_authority = 1;
            continue;
        }
        if (strcmp(line, "authority_end") == 0) {
            in_authority = 0;
            continue;
        }
        if (strcmp(line, "constraints_begin") == 0) {
            in_constraints = 1;
            continue;
        }
        if (strcmp(line, "constraints_end") == 0) {
            in_constraints = 0;
            continue;
        }
        if (strcmp(line, "institutions_begin") == 0) {
            in_institutions = 1;
            continue;
        }
        if (strcmp(line, "institutions_end") == 0) {
            in_institutions = 0;
            continue;
        }
        if (strcmp(line, "networks_begin") == 0) {
            in_networks = 1;
            continue;
        }
        if (strcmp(line, "networks_end") == 0) {
            in_networks = 0;
            continue;
        }
        if (in_worlddef) {
            strncpy(shell->world.worlddef_json, line, sizeof(shell->world.worlddef_json) - 1u);
            shell->world.worlddef_json[sizeof(shell->world.worlddef_json) - 1u] = '\0';
            shell->world.worlddef_len = strlen(shell->world.worlddef_json);
            shell->world.worlddef_hash = dom_shell_hash64(shell->world.worlddef_json,
                                                         shell->world.worlddef_len);
            continue;
        }
        if (in_summary) {
            char* eq = strchr(line, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            const char* key = line;
            const char* val = eq + 1;
            if (strcmp(key, "worlddef_id") == 0) {
                strncpy(shell->world.summary.worlddef_id, val,
                        sizeof(shell->world.summary.worlddef_id) - 1u);
            } else if (strcmp(key, "template_id") == 0) {
                strncpy(shell->world.summary.template_id, val,
                        sizeof(shell->world.summary.template_id) - 1u);
            } else if (strcmp(key, "schema_version") == 0) {
                shell->world.summary.schema_version = (uint32_t)strtoul(val, 0, 10);
            } else if (strcmp(key, "spawn_node_id") == 0) {
                strncpy(shell->world.summary.spawn_node_id, val,
                        sizeof(shell->world.summary.spawn_node_id) - 1u);
            } else if (strcmp(key, "spawn_frame_id") == 0) {
                strncpy(shell->world.summary.spawn_frame_id, val,
                        sizeof(shell->world.summary.spawn_frame_id) - 1u);
            } else if (strcmp(key, "spawn_pos") == 0) {
                dom_shell_parse_vec3(val, shell->world.summary.spawn_pos);
            } else if (strcmp(key, "spawn_orient") == 0) {
                dom_shell_parse_vec3(val, shell->world.summary.spawn_orient);
            } else if (strcmp(key, "policy.movement") == 0) {
                dom_shell_policy_set_from_csv(&shell->world.summary.movement, val);
            } else if (strcmp(key, "policy.authority") == 0) {
                dom_shell_policy_set_from_csv(&shell->world.summary.authority, val);
            } else if (strcmp(key, "policy.mode") == 0) {
                dom_shell_policy_set_from_csv(&shell->world.summary.mode, val);
            } else if (strcmp(key, "policy.debug") == 0) {
                dom_shell_policy_set_from_csv(&shell->world.summary.debug, val);
            }
            continue;
        }
        if (in_local) {
            if (strncmp(line, "tick=", 5) == 0) {
                shell->tick = (u32)strtoul(line + 5, 0, 10);
                continue;
            }
            if (strncmp(line, "rng_seed=", 9) == 0) {
                (void)dom_shell_parse_u64(line + 9, &shell->rng_seed);
                continue;
            }
            if (strncmp(line, "knowledge_mask=", 15) == 0) {
                shell->fields.knowledge_mask = (u32)strtoul(line + 15, 0, 0);
                continue;
            }
            if (strncmp(line, "confidence_q16=", 15) == 0) {
                shell->fields.confidence_q16 = (u32)strtoul(line + 15, 0, 10);
                continue;
            }
            if (strncmp(line, "uncertainty_q16=", 16) == 0) {
                shell->fields.uncertainty_q16 = (u32)strtoul(line + 16, 0, 10);
                continue;
            }
            if (strncmp(line, "field ", 6) == 0) {
                u32 field_id = 0u;
                int obj = 0;
                int subj = 0;
                int known = 0;
                if (sscanf(line, "field id=%u objective=%d subjective=%d known=%d",
                           &field_id, &obj, &subj, &known) == 4) {
                    if (field_id > 0u) {
                        (void)dom_field_set_value(&shell->fields.objective,
                                                  field_id, 0u, 0u, (i32)obj);
                        (void)dom_field_set_value(&shell->fields.subjective,
                                                  field_id, 0u, 0u, (i32)subj);
                        if (known) {
                            shell->fields.knowledge_mask |= DOM_FIELD_BIT(field_id);
                        }
                    }
                }
                continue;
            }
            if (strncmp(line, "structure_built=", 16) == 0) {
                shell->structure.structure.built = (u32)strtoul(line + 16, 0, 10);
                continue;
            }
            if (strncmp(line, "structure_failed=", 17) == 0) {
                shell->structure.structure.failed = (u32)strtoul(line + 17, 0, 10);
                continue;
            }
            if (strncmp(line, "energy_edge_status=", 19) == 0) {
                dom_network_edge* edge = dom_network_find_edge(&shell->structure.network, 1u);
                if (edge) {
                    edge->status = (u32)strtoul(line + 19, 0, 10);
                }
                continue;
            }
            continue;
        }
        if (in_agents) {
            if (strncmp(line, "next_agent_id=", 14) == 0) {
                dom_shell_parse_u64(line + 14, &next_agent_id);
                continue;
            }
            if (strncmp(line, "possessed_agent_id=", 19) == 0) {
                dom_shell_parse_u64(line + 19, &possessed_agent_id);
                continue;
            }
            if (strncmp(line, "agent ", 6) == 0) {
                u64 agent_id = 0u;
                u32 caps = 0u;
                u32 auth = 0u;
                u32 know = 0u;
                u64 record_goal_id = 0u;
                u32 record_goal_type = 0u;
                u32 record_refusal = 0u;
                u64 sched_next = 0u;
                u32 sched_status = 0u;
                u32 sched_budget = 0u;
                u64 sched_goal = 0u;
                u64 sched_plan = 0u;
                u32 sched_resume = 0u;
                u32 hunger = 0u;
                u32 threat = 0u;
                u32 risk_q16 = 0u;
                u32 ep_conf = 0u;
                u64 resource_ref = 0u;
                u64 threat_ref = 0u;
                u64 dest_ref = 0u;
                char* token = strtok(line + 6, " ");
                while (token) {
                    char* eq = strchr(token, '=');
                    if (eq) {
                        *eq = '\0';
                        if (strcmp(token, "id") == 0) {
                            dom_shell_parse_u64(eq + 1, &agent_id);
                        } else if (strcmp(token, "caps") == 0) {
                            caps = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "auth") == 0) {
                            auth = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "know") == 0) {
                            know = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "record_goal_id") == 0) {
                            dom_shell_parse_u64(eq + 1, &record_goal_id);
                        } else if (strcmp(token, "record_goal_type") == 0) {
                            record_goal_type = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "record_refusal") == 0) {
                            record_refusal = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "sched_next") == 0) {
                            dom_shell_parse_u64(eq + 1, &sched_next);
                        } else if (strcmp(token, "sched_status") == 0) {
                            sched_status = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "sched_budget") == 0) {
                            sched_budget = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "sched_goal") == 0) {
                            dom_shell_parse_u64(eq + 1, &sched_goal);
                        } else if (strcmp(token, "sched_plan") == 0) {
                            dom_shell_parse_u64(eq + 1, &sched_plan);
                        } else if (strcmp(token, "sched_resume") == 0) {
                            sched_resume = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "hunger") == 0) {
                            hunger = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "threat") == 0) {
                            threat = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "risk_q16") == 0) {
                            risk_q16 = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "ep_conf") == 0) {
                            ep_conf = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "resource_ref") == 0) {
                            dom_shell_parse_u64(eq + 1, &resource_ref);
                        } else if (strcmp(token, "threat_ref") == 0) {
                            dom_shell_parse_u64(eq + 1, &threat_ref);
                        } else if (strcmp(token, "dest_ref") == 0) {
                            dom_shell_parse_u64(eq + 1, &dest_ref);
                        }
                    }
                    token = strtok(0, " ");
                }
                if (agent_id != 0u && dom_shell_agent_add(shell, agent_id, caps, auth, know)) {
                    int idx = dom_shell_agent_index(shell, agent_id);
                    if (idx >= 0) {
                        dom_shell_agent_record* record = &shell->agents[idx];
                        dom_agent_schedule_item* sched = &shell->schedules[idx];
                        dom_agent_belief* belief = &shell->beliefs[idx];
                        dom_agent_capability* cap = &shell->caps[idx];
                        record->last_goal_id = record_goal_id;
                        record->last_goal_type = record_goal_type;
                        record->last_refusal = record_refusal;
                        sched->next_due_tick = (dom_act_time_t)sched_next;
                        sched->status = sched_status;
                        sched->compute_budget = sched_budget;
                        sched->active_goal_id = sched_goal;
                        sched->active_plan_id = sched_plan;
                        sched->resume_step = sched_resume;
                        belief->knowledge_mask = know;
                        belief->hunger_level = hunger;
                        belief->threat_level = threat;
                        belief->risk_tolerance_q16 = risk_q16;
                        belief->epistemic_confidence_q16 = ep_conf;
                        belief->known_resource_ref = resource_ref;
                        belief->known_threat_ref = threat_ref;
                        belief->known_destination_ref = dest_ref;
                        cap->capability_mask = caps;
                        cap->authority_mask = auth;
                    }
                    if (agent_id > max_agent_id) {
                        max_agent_id = agent_id;
                    }
                }
            }
            continue;
        }
        if (in_goals) {
            if (strncmp(line, "next_goal_id=", 13) == 0) {
                dom_shell_parse_u64(line + 13, &next_goal_id);
                continue;
            }
            if (strncmp(line, "goal ", 5) == 0) {
                agent_goal_desc desc;
                agent_goal_preconditions preconds;
                agent_goal_condition conds[AGENT_GOAL_MAX_CONDITIONS];
                u32 cond_count = 0u;
                u64 goal_id = 0u;
                u64 agent_id = 0u;
                u32 goal_type = 0u;
                u32 status = 0u;
                u32 flags = 0u;
                u32 base_priority = 0u;
                u32 urgency = 0u;
                u32 acceptable_risk_q16 = 0u;
                u64 horizon_act = 0u;
                u32 ep_conf = 0u;
                u32 satisfaction_flags = 0u;
                u64 expiry_act = 0u;
                u32 failure_count = 0u;
                u32 oscillation_count = 0u;
                u32 abandon_after_failures = 0u;
                u64 abandon_after_act = 0u;
                u64 defer_until_act = 0u;
                u32 conflict_group = 0u;
                u64 last_update_act = 0u;
                memset(&preconds, 0, sizeof(preconds));
                memset(conds, 0, sizeof(conds));
                {
                    char* token = strtok(line + 5, " ");
                    while (token) {
                        char* eq = strchr(token, '=');
                        if (eq) {
                            *eq = '\0';
                            if (strcmp(token, "id") == 0) {
                                dom_shell_parse_u64(eq + 1, &goal_id);
                            } else if (strcmp(token, "agent") == 0) {
                                dom_shell_parse_u64(eq + 1, &agent_id);
                            } else if (strcmp(token, "type") == 0) {
                                goal_type = (u32)strtoul(eq + 1, 0, 10);
                            } else if (strcmp(token, "status") == 0) {
                                status = (u32)strtoul(eq + 1, 0, 10);
                            } else if (strcmp(token, "flags") == 0) {
                                flags = (u32)strtoul(eq + 1, 0, 10);
                            } else if (strcmp(token, "base_priority") == 0) {
                                base_priority = (u32)strtoul(eq + 1, 0, 10);
                            } else if (strcmp(token, "urgency") == 0) {
                                urgency = (u32)strtoul(eq + 1, 0, 10);
                            } else if (strcmp(token, "acceptable_risk_q16") == 0) {
                                acceptable_risk_q16 = (u32)strtoul(eq + 1, 0, 10);
                            } else if (strcmp(token, "horizon_act") == 0) {
                                dom_shell_parse_u64(eq + 1, &horizon_act);
                            } else if (strcmp(token, "epistemic_confidence_q16") == 0) {
                                ep_conf = (u32)strtoul(eq + 1, 0, 10);
                            } else if (strcmp(token, "precond_caps") == 0) {
                                preconds.required_capabilities = (u32)strtoul(eq + 1, 0, 10);
                            } else if (strcmp(token, "precond_auth") == 0) {
                                preconds.required_authority = (u32)strtoul(eq + 1, 0, 10);
                            } else if (strcmp(token, "precond_know") == 0) {
                                preconds.required_knowledge = (u32)strtoul(eq + 1, 0, 10);
                            } else if (strcmp(token, "satisfaction_flags") == 0) {
                                satisfaction_flags = (u32)strtoul(eq + 1, 0, 10);
                            } else if (strcmp(token, "expiry_act") == 0) {
                                dom_shell_parse_u64(eq + 1, &expiry_act);
                            } else if (strcmp(token, "failure_count") == 0) {
                                failure_count = (u32)strtoul(eq + 1, 0, 10);
                            } else if (strcmp(token, "oscillation_count") == 0) {
                                oscillation_count = (u32)strtoul(eq + 1, 0, 10);
                            } else if (strcmp(token, "abandon_after_failures") == 0) {
                                abandon_after_failures = (u32)strtoul(eq + 1, 0, 10);
                            } else if (strcmp(token, "abandon_after_act") == 0) {
                                dom_shell_parse_u64(eq + 1, &abandon_after_act);
                            } else if (strcmp(token, "defer_until_act") == 0) {
                                dom_shell_parse_u64(eq + 1, &defer_until_act);
                            } else if (strcmp(token, "conflict_group") == 0) {
                                conflict_group = (u32)strtoul(eq + 1, 0, 10);
                            } else if (strcmp(token, "last_update_act") == 0) {
                                dom_shell_parse_u64(eq + 1, &last_update_act);
                            } else if (strncmp(token, "cond", 4) == 0) {
                                u32 idx = (u32)strtoul(token + 4, 0, 10);
                                unsigned int kind = 0u;
                                unsigned int flags_val = 0u;
                                unsigned long long subject = 0u;
                                int threshold = 0;
                                if (idx < AGENT_GOAL_MAX_CONDITIONS &&
                                    sscanf(eq + 1, "%u,%llu,%d,%u",
                                           &kind, &subject, &threshold, &flags_val) == 4) {
                                    conds[idx].kind = (u32)kind;
                                    conds[idx].subject_ref = (u64)subject;
                                    conds[idx].threshold = (i32)threshold;
                                    conds[idx].flags = (u32)flags_val;
                                    if (idx + 1u > cond_count) {
                                        cond_count = idx + 1u;
                                    }
                                }
                            }
                        }
                        token = strtok(0, " ");
                    }
                }
                if (agent_id != 0u && goal_id != 0u) {
                    agent_goal* goal;
                    memset(&desc, 0, sizeof(desc));
                    desc.agent_id = agent_id;
                    desc.goal_id = goal_id;
                    desc.type = goal_type;
                    desc.base_priority = base_priority;
                    desc.urgency = urgency;
                    desc.acceptable_risk_q16 = acceptable_risk_q16;
                    desc.horizon_act = (dom_act_time_t)horizon_act;
                    desc.epistemic_confidence_q16 = ep_conf;
                    desc.conditions = (cond_count > 0u) ? conds : 0;
                    desc.condition_count = cond_count;
                    desc.preconditions = preconds;
                    desc.satisfaction_flags = satisfaction_flags;
                    desc.expiry_act = (dom_act_time_t)expiry_act;
                    desc.abandon_after_failures = abandon_after_failures;
                    desc.abandon_after_act = (dom_act_time_t)abandon_after_act;
                    desc.conflict_group = conflict_group;
                    desc.flags = flags;
                    if (agent_goal_register(&shell->goal_registry, &desc, 0) == 0) {
                        goal = agent_goal_find(&shell->goal_registry, goal_id);
                        if (goal) {
                            goal->status = status;
                            goal->flags = flags;
                            goal->failure_count = failure_count;
                            goal->oscillation_count = oscillation_count;
                            goal->abandon_after_failures = abandon_after_failures;
                            goal->abandon_after_act = (dom_act_time_t)abandon_after_act;
                            goal->defer_until_act = (dom_act_time_t)defer_until_act;
                            goal->conflict_group = conflict_group;
                            goal->last_update_act = (dom_act_time_t)last_update_act;
                            goal->satisfaction_flags = satisfaction_flags;
                            goal->expiry_act = (dom_act_time_t)expiry_act;
                            goal->acceptable_risk_q16 = acceptable_risk_q16;
                            goal->horizon_act = (dom_act_time_t)horizon_act;
                            goal->epistemic_confidence_q16 = ep_conf;
                            goal->preconditions = preconds;
                        }
                    }
                    if (goal_id > max_goal_id) {
                        max_goal_id = goal_id;
                    }
                }
            }
            continue;
        }
        if (in_delegations) {
            if (strncmp(line, "next_delegation_id=", 19) == 0) {
                dom_shell_parse_u64(line + 19, &next_delegation_id);
                continue;
            }
            if (strncmp(line, "delegation ", 11) == 0) {
                u64 delegation_id = 0u;
                u64 delegator = 0u;
                u64 delegatee = 0u;
                u32 kind = 0u;
                u32 process_mask = 0u;
                u32 authority_mask = 0u;
                u64 expiry_act = 0u;
                u64 provenance = 0u;
                u32 revoked = 0u;
                char* token = strtok(line + 11, " ");
                while (token) {
                    char* eq = strchr(token, '=');
                    if (eq) {
                        *eq = '\0';
                        if (strcmp(token, "id") == 0) {
                            dom_shell_parse_u64(eq + 1, &delegation_id);
                        } else if (strcmp(token, "delegator") == 0) {
                            dom_shell_parse_u64(eq + 1, &delegator);
                        } else if (strcmp(token, "delegatee") == 0) {
                            dom_shell_parse_u64(eq + 1, &delegatee);
                        } else if (strcmp(token, "kind") == 0) {
                            kind = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "process") == 0) {
                            process_mask = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "authority") == 0) {
                            authority_mask = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "expiry") == 0) {
                            dom_shell_parse_u64(eq + 1, &expiry_act);
                        } else if (strcmp(token, "provenance") == 0) {
                            dom_shell_parse_u64(eq + 1, &provenance);
                        } else if (strcmp(token, "revoked") == 0) {
                            revoked = (u32)strtoul(eq + 1, 0, 10);
                        }
                    }
                    token = strtok(0, " ");
                }
                if (delegation_id != 0u &&
                    agent_delegation_register(&shell->delegation_registry,
                                              delegation_id,
                                              delegator,
                                              delegatee,
                                              kind,
                                              process_mask,
                                              authority_mask,
                                              (dom_act_time_t)expiry_act,
                                              provenance) == 0) {
                    if (revoked) {
                        agent_delegation_revoke(&shell->delegation_registry, delegation_id);
                    }
                    if (delegation_id > max_delegation_id) {
                        max_delegation_id = delegation_id;
                    }
                }
            }
            continue;
        }
        if (in_authority) {
            if (strncmp(line, "next_authority_id=", 18) == 0) {
                dom_shell_parse_u64(line + 18, &next_authority_id);
                continue;
            }
            if (strncmp(line, "grant ", 6) == 0) {
                u64 grant_id = 0u;
                u64 granter = 0u;
                u64 grantee = 0u;
                u32 mask = 0u;
                u64 expiry_act = 0u;
                u64 provenance = 0u;
                u32 revoked = 0u;
                char* token = strtok(line + 6, " ");
                while (token) {
                    char* eq = strchr(token, '=');
                    if (eq) {
                        *eq = '\0';
                        if (strcmp(token, "id") == 0) {
                            dom_shell_parse_u64(eq + 1, &grant_id);
                        } else if (strcmp(token, "granter") == 0) {
                            dom_shell_parse_u64(eq + 1, &granter);
                        } else if (strcmp(token, "grantee") == 0) {
                            dom_shell_parse_u64(eq + 1, &grantee);
                        } else if (strcmp(token, "authority") == 0) {
                            mask = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "expiry") == 0) {
                            dom_shell_parse_u64(eq + 1, &expiry_act);
                        } else if (strcmp(token, "provenance") == 0) {
                            dom_shell_parse_u64(eq + 1, &provenance);
                        } else if (strcmp(token, "revoked") == 0) {
                            revoked = (u32)strtoul(eq + 1, 0, 10);
                        }
                    }
                    token = strtok(0, " ");
                }
                if (grant_id != 0u &&
                    agent_authority_grant_register(&shell->authority_registry,
                                                   grant_id,
                                                   granter,
                                                   grantee,
                                                   mask,
                                                   (dom_act_time_t)expiry_act,
                                                   (dom_provenance_id)provenance) == 0) {
                    if (revoked) {
                        agent_authority_grant_revoke(&shell->authority_registry, grant_id);
                    }
                    if (grant_id > max_authority_id) {
                        max_authority_id = grant_id;
                    }
                }
            }
            continue;
        }
        if (in_constraints) {
            if (strncmp(line, "next_constraint_id=", 19) == 0) {
                dom_shell_parse_u64(line + 19, &next_constraint_id);
                continue;
            }
            if (strncmp(line, "constraint ", 11) == 0) {
                u64 constraint_id = 0u;
                u64 institution_id = 0u;
                u64 target_id = 0u;
                u32 process_mask = 0u;
                u32 mode = 0u;
                u64 expiry_act = 0u;
                u64 provenance = 0u;
                u32 revoked = 0u;
                char* token = strtok(line + 11, " ");
                while (token) {
                    char* eq = strchr(token, '=');
                    if (eq) {
                        *eq = '\0';
                        if (strcmp(token, "id") == 0) {
                            dom_shell_parse_u64(eq + 1, &constraint_id);
                        } else if (strcmp(token, "institution") == 0) {
                            dom_shell_parse_u64(eq + 1, &institution_id);
                        } else if (strcmp(token, "target") == 0) {
                            dom_shell_parse_u64(eq + 1, &target_id);
                        } else if (strcmp(token, "process") == 0) {
                            process_mask = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "mode") == 0) {
                            mode = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "expiry") == 0) {
                            dom_shell_parse_u64(eq + 1, &expiry_act);
                        } else if (strcmp(token, "provenance") == 0) {
                            dom_shell_parse_u64(eq + 1, &provenance);
                        } else if (strcmp(token, "revoked") == 0) {
                            revoked = (u32)strtoul(eq + 1, 0, 10);
                        }
                    }
                    token = strtok(0, " ");
                }
                if (constraint_id != 0u &&
                    agent_constraint_register(&shell->constraint_registry,
                                              constraint_id,
                                              institution_id,
                                              target_id,
                                              process_mask,
                                              mode,
                                              (dom_act_time_t)expiry_act,
                                              (dom_provenance_id)provenance) == 0) {
                    if (revoked) {
                        agent_constraint_revoke(&shell->constraint_registry, constraint_id);
                    }
                    if (constraint_id > max_constraint_id) {
                        max_constraint_id = constraint_id;
                    }
                }
            }
            continue;
        }
        if (in_institutions) {
            if (strncmp(line, "next_institution_id=", 20) == 0) {
                dom_shell_parse_u64(line + 20, &next_institution_id);
                continue;
            }
            if (strncmp(line, "institution ", 12) == 0) {
                u64 institution_id = 0u;
                u64 agent_id = 0u;
                u32 authority = 0u;
                u32 legitimacy = 0u;
                u32 status = 0u;
                u64 founded_act = 0u;
                u64 collapsed_act = 0u;
                u64 provenance = 0u;
                u32 flags = 0u;
                char* token = strtok(line + 12, " ");
                while (token) {
                    char* eq = strchr(token, '=');
                    if (eq) {
                        *eq = '\0';
                        if (strcmp(token, "id") == 0) {
                            dom_shell_parse_u64(eq + 1, &institution_id);
                        } else if (strcmp(token, "agent") == 0) {
                            dom_shell_parse_u64(eq + 1, &agent_id);
                        } else if (strcmp(token, "authority") == 0) {
                            authority = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "legitimacy_q16") == 0) {
                            legitimacy = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "status") == 0) {
                            status = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "founded_act") == 0) {
                            dom_shell_parse_u64(eq + 1, &founded_act);
                        } else if (strcmp(token, "collapsed_act") == 0) {
                            dom_shell_parse_u64(eq + 1, &collapsed_act);
                        } else if (strcmp(token, "provenance") == 0) {
                            dom_shell_parse_u64(eq + 1, &provenance);
                        } else if (strcmp(token, "flags") == 0) {
                            flags = (u32)strtoul(eq + 1, 0, 10);
                        }
                    }
                    token = strtok(0, " ");
                }
                if (institution_id != 0u &&
                    agent_institution_register(&shell->institution_registry,
                                               institution_id,
                                               agent_id,
                                               authority,
                                               legitimacy,
                                               (dom_act_time_t)founded_act,
                                               (dom_provenance_id)provenance) == 0) {
                    agent_institution* inst = agent_institution_find(&shell->institution_registry,
                                                                     institution_id);
                    if (inst) {
                        inst->status = status;
                        inst->collapsed_act = (dom_act_time_t)collapsed_act;
                        inst->flags = flags;
                    }
                    if (institution_id > max_institution_id) {
                        max_institution_id = institution_id;
                    }
                }
            }
            continue;
        }
        if (in_networks) {
            if (strncmp(line, "next_network_id=", 16) == 0) {
                dom_shell_parse_u64(line + 16, &next_network_id);
                continue;
            }
            if (strncmp(line, "network ", 8) == 0) {
                u64 network_id = 0u;
                u32 type = 0u;
                char* token = strtok(line + 8, " ");
                while (token) {
                    char* eq = strchr(token, '=');
                    if (eq) {
                        *eq = '\0';
                        if (strcmp(token, "id") == 0) {
                            dom_shell_parse_u64(eq + 1, &network_id);
                        } else if (strcmp(token, "type") == 0) {
                            type = (u32)strtoul(eq + 1, 0, 10);
                        }
                    }
                    token = strtok(0, " ");
                }
                if (network_id != 0u) {
                    (void)dom_shell_network_create(shell, network_id, type);
                    if (network_id > max_network_id) {
                        max_network_id = network_id;
                    }
                }
            } else if (strncmp(line, "node ", 5) == 0) {
                u64 network_id = 0u;
                u64 node_id = 0u;
                u32 status = DOM_NETWORK_OK;
                i32 capacity_q16 = 0;
                i32 stored_q16 = 0;
                i32 loss_q16 = 0;
                i32 min_required_q16 = 0;
                char* token = strtok(line + 5, " ");
                while (token) {
                    char* eq = strchr(token, '=');
                    if (eq) {
                        *eq = '\0';
                        if (strcmp(token, "network") == 0) {
                            dom_shell_parse_u64(eq + 1, &network_id);
                        } else if (strcmp(token, "id") == 0) {
                            dom_shell_parse_u64(eq + 1, &node_id);
                        } else if (strcmp(token, "status") == 0) {
                            status = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "capacity_q16") == 0) {
                            capacity_q16 = (i32)strtol(eq + 1, 0, 10);
                        } else if (strcmp(token, "stored_q16") == 0) {
                            stored_q16 = (i32)strtol(eq + 1, 0, 10);
                        } else if (strcmp(token, "loss_q16") == 0) {
                            loss_q16 = (i32)strtol(eq + 1, 0, 10);
                        } else if (strcmp(token, "min_required_q16") == 0) {
                            min_required_q16 = (i32)strtol(eq + 1, 0, 10);
                        }
                    }
                    token = strtok(0, " ");
                }
                if (network_id != 0u && node_id != 0u) {
                    dom_shell_network_state* net = dom_shell_network_find(shell, network_id);
                    if (net) {
                        dom_network_node* node = dom_network_add_node(&net->graph, node_id, capacity_q16);
                        if (node) {
                            node->status = status;
                            node->stored_q16 = stored_q16;
                            node->loss_q16 = loss_q16;
                            node->min_required_q16 = min_required_q16;
                        }
                    }
                }
            } else if (strncmp(line, "edge ", 5) == 0) {
                u64 network_id = 0u;
                u64 edge_id = 0u;
                u64 a = 0u;
                u64 b = 0u;
                u32 status = DOM_NETWORK_OK;
                i32 capacity_q16 = 0;
                i32 loss_q16 = 0;
                char* token = strtok(line + 5, " ");
                while (token) {
                    char* eq = strchr(token, '=');
                    if (eq) {
                        *eq = '\0';
                        if (strcmp(token, "network") == 0) {
                            dom_shell_parse_u64(eq + 1, &network_id);
                        } else if (strcmp(token, "id") == 0) {
                            dom_shell_parse_u64(eq + 1, &edge_id);
                        } else if (strcmp(token, "a") == 0) {
                            dom_shell_parse_u64(eq + 1, &a);
                        } else if (strcmp(token, "b") == 0) {
                            dom_shell_parse_u64(eq + 1, &b);
                        } else if (strcmp(token, "status") == 0) {
                            status = (u32)strtoul(eq + 1, 0, 10);
                        } else if (strcmp(token, "capacity_q16") == 0) {
                            capacity_q16 = (i32)strtol(eq + 1, 0, 10);
                        } else if (strcmp(token, "loss_q16") == 0) {
                            loss_q16 = (i32)strtol(eq + 1, 0, 10);
                        }
                    }
                    token = strtok(0, " ");
                }
                if (network_id != 0u && edge_id != 0u) {
                    dom_shell_network_state* net = dom_shell_network_find(shell, network_id);
                    if (net) {
                        dom_network_edge* edge = dom_network_add_edge(&net->graph, edge_id, a, b, capacity_q16, loss_q16);
                        if (edge) {
                            edge->status = status;
                        }
                    }
                }
            }
            continue;
        }
        if (in_events) {
            dom_shell_event_ring_add(&shell->events, "replay.event", line);
            continue;
        }
    }
    fclose(f);
    if (max_agent_id >= shell->next_agent_id) {
        shell->next_agent_id = max_agent_id + 1u;
    }
    if (next_agent_id > shell->next_agent_id) {
        shell->next_agent_id = next_agent_id;
    }
    if (possessed_agent_id != 0u && dom_shell_agent_index(shell, possessed_agent_id) >= 0) {
        shell->possessed_agent_id = possessed_agent_id;
    }
    if (max_goal_id >= shell->goal_registry.next_goal_id) {
        shell->goal_registry.next_goal_id = max_goal_id + 1u;
    }
    if (next_goal_id > shell->goal_registry.next_goal_id) {
        shell->goal_registry.next_goal_id = next_goal_id;
    }
    if (max_delegation_id >= shell->next_delegation_id) {
        shell->next_delegation_id = max_delegation_id + 1u;
    }
    if (next_delegation_id > shell->next_delegation_id) {
        shell->next_delegation_id = next_delegation_id;
    }
    if (max_authority_id >= shell->next_authority_id) {
        shell->next_authority_id = max_authority_id + 1u;
    }
    if (next_authority_id > shell->next_authority_id) {
        shell->next_authority_id = next_authority_id;
    }
    if (max_constraint_id >= shell->next_constraint_id) {
        shell->next_constraint_id = max_constraint_id + 1u;
    }
    if (next_constraint_id > shell->next_constraint_id) {
        shell->next_constraint_id = next_constraint_id;
    }
    if (max_institution_id >= shell->next_institution_id) {
        shell->next_institution_id = max_institution_id + 1u;
    }
    if (next_institution_id > shell->next_institution_id) {
        shell->next_institution_id = next_institution_id;
    }
    if (max_network_id >= shell->next_network_id) {
        shell->next_network_id = max_network_id + 1u;
    }
    if (next_network_id > shell->next_network_id) {
        shell->next_network_id = next_network_id;
    }
    if (!have_summary || shell->world.summary.schema_version == 0u) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "summary missing");
        }
        return 0;
    }
    shell->world.active = 1;
    strncpy(shell->world.current_node_id,
            shell->world.summary.spawn_node_id,
            sizeof(shell->world.current_node_id) - 1u);
    dom_shell_sync_world_pose(&shell->world);
    shell->world.active_mode[0] = '\0';
    if (shell->world.summary.mode.count > 0u) {
        strncpy(shell->world.active_mode,
                shell->world.summary.mode.items[0],
                sizeof(shell->world.active_mode) - 1u);
    }
    if (shell->rng_seed == 0u) {
        (void)dom_shell_extract_seed(shell->world.summary.worlddef_id, &shell->rng_seed);
        if (shell->rng_seed == 0u) {
            shell->rng_seed = 1u;
        }
    }
    return 1;
}

int dom_client_shell_load_world(dom_client_shell* shell,
                                const char* path,
                                dom_app_ui_event_log* log,
                                char* status,
                                size_t status_cap,
                                int emit_text)
{
    char err[96];
    const char* in_path = path && path[0] ? path : DOM_SHELL_DEFAULT_SAVE_PATH;
    if (!shell) {
        return D_APP_EXIT_FAILURE;
    }
    err[0] = '\0';
    if (!dom_shell_load_save_file(shell, in_path, err, sizeof(err))) {
        dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, err[0] ? err : "load failed");
        dom_shell_set_status(shell, "world_load=refused");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            fprintf(stderr, "client: load refused (%s)\n", err[0] ? err : "load failed");
        }
        dom_shell_emit(shell, log, "client.world.load", "result=refused");
        return D_APP_EXIT_UNAVAILABLE;
    }
    dom_shell_set_status(shell, "world_load=ok");
    if (status && status_cap > 0u) {
        snprintf(status, status_cap, "%s", shell->last_status);
    }
    if (emit_text) {
        printf("world_load=ok path=%s\n", in_path);
        printf("worlddef_id=%s\n", shell->world.summary.worlddef_id);
    }
    {
        char detail[128];
        snprintf(detail, sizeof(detail), "path=%s result=ok", in_path);
        dom_shell_emit(shell, log, "client.world.load", detail);
    }
    return D_APP_EXIT_OK;
}

static int dom_shell_load_replay_file(dom_client_shell* shell, const char* path, char* err, size_t err_cap)
{
    FILE* f;
    char line[DOM_SHELL_EVENT_MAX];
    int header_checked = 0;
    int replay_header = 0;
    if (!shell || !path || !path[0]) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "replay path missing");
        }
        return 0;
    }
    f = fopen(path, "r");
    if (!f) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "replay open failed");
        }
        return 0;
    }
    shell->events.head = 0u;
    shell->events.count = 0u;
    while (fgets(line, sizeof(line), f)) {
        size_t len = strlen(line);
        while (len > 0u && (line[len - 1u] == '\n' || line[len - 1u] == '\r')) {
            line[--len] = '\0';
        }
        if (!header_checked) {
            header_checked = 1;
            if (strcmp(line, DOM_SHELL_SAVE_HEADER) == 0) {
                replay_header = 0;
                continue;
            }
            if (strcmp(line, DOM_SHELL_REPLAY_HEADER) == 0) {
                replay_header = 1;
                continue;
            }
            replay_header = 1;
        }
        if (!replay_header) {
            if (strcmp(line, "events_begin") == 0) {
                replay_header = 2;
            }
            continue;
        }
        if (replay_header == 2) {
            if (strcmp(line, "events_end") == 0) {
                break;
            }
            dom_shell_event_ring_add(&shell->events, "replay.event", line);
            continue;
        }
        dom_shell_event_ring_add(&shell->events, "replay.event", line);
    }
    fclose(f);
    if (shell->events.count == 0u) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "replay empty");
        }
        return 0;
    }
    return 1;
}

int dom_client_shell_inspect_replay(dom_client_shell* shell,
                                    const char* path,
                                    dom_app_ui_event_log* log,
                                    char* status,
                                    size_t status_cap,
                                    int emit_text)
{
    char err[96];
    if (!shell) {
        return D_APP_EXIT_FAILURE;
    }
    err[0] = '\0';
    if (!dom_shell_load_replay_file(shell, path, err, sizeof(err))) {
        dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, err[0] ? err : "replay failed");
        dom_shell_set_status(shell, "replay_inspect=refused");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            fprintf(stderr, "client: replay refused (%s)\n", err[0] ? err : "replay failed");
        }
        dom_shell_emit(shell, log, "client.replay.inspect", "result=refused");
        return D_APP_EXIT_UNAVAILABLE;
    }
    dom_shell_set_status(shell, "replay_inspect=ok");
    if (status && status_cap > 0u) {
        snprintf(status, status_cap, "%s", shell->last_status);
    }
    if (emit_text) {
        printf("replay_inspect=ok path=%s\n", path ? path : "");
    }
    {
        char detail[128];
        snprintf(detail, sizeof(detail), "path=%s result=ok", path ? path : "");
        dom_shell_emit(shell, log, "client.replay.inspect", detail);
    }
    return D_APP_EXIT_OK;
}

int dom_client_shell_set_mode(dom_client_shell* shell,
                              const char* mode_id,
                              dom_app_ui_event_log* log,
                              char* status,
                              size_t status_cap,
                              int emit_text)
{
    if (!shell || !mode_id || !mode_id[0]) {
        return D_APP_EXIT_USAGE;
    }
    if (!shell->world.active) {
        dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "no active world");
        dom_shell_set_status(shell, "mode_set=refused");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        return D_APP_EXIT_UNAVAILABLE;
    }
    if (!dom_shell_policy_set_contains(&shell->world.summary.authority, DOM_SHELL_AUTH_POLICY)) {
        dom_shell_set_refusal(shell, DOM_REFUSAL_SCHEMA, "missing authority");
        dom_shell_set_status(shell, "mode_set=refused");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        dom_shell_emit(shell, log, "client.nav.mode", "result=refused reason=authority");
        return D_APP_EXIT_UNAVAILABLE;
    }
    if (!dom_shell_policy_set_contains(&shell->world.summary.mode, mode_id)) {
        dom_shell_set_refusal(shell, DOM_REFUSAL_SCHEMA, "mode not allowed");
        dom_shell_set_status(shell, "mode_set=refused");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        dom_shell_emit(shell, log, "client.nav.mode", "result=refused reason=policy");
        return D_APP_EXIT_UNAVAILABLE;
    }
    strncpy(shell->world.active_mode, mode_id, sizeof(shell->world.active_mode) - 1u);
    dom_shell_set_status(shell, "mode_set=ok");
    if (status && status_cap > 0u) {
        snprintf(status, status_cap, "%s", shell->last_status);
    }
    if (emit_text) {
        printf("mode_set=ok mode=%s\n", shell->world.active_mode);
    }
    {
        char detail[128];
        snprintf(detail, sizeof(detail), "mode=%s result=ok", mode_id);
        dom_shell_emit(shell, log, "client.nav.mode", detail);
    }
    return D_APP_EXIT_OK;
}

static int dom_shell_mode_allows_move(const char* mode_id, double* dz)
{
    if (!mode_id || !mode_id[0]) {
        return 0;
    }
    if (strcmp(mode_id, DOM_SHELL_MODE_FREE) == 0) {
        return 1;
    }
    if (strcmp(mode_id, DOM_SHELL_MODE_SURFACE) == 0) {
        if (dz) {
            *dz = 0.0;
        }
        return 1;
    }
    if (strcmp(mode_id, DOM_SHELL_MODE_ORBIT) == 0) {
        return 0;
    }
    return 0;
}

int dom_client_shell_move(dom_client_shell* shell, double dx, double dy, double dz,
                          dom_app_ui_event_log* log)
{
    double adjusted_dz = dz;
    i32 cost_q16 = DOM_FIELD_VALUE_UNKNOWN;
    if (!shell || !shell->world.active) {
        return 0;
    }
    if (!dom_shell_mode_allows_move(shell->world.active_mode, &adjusted_dz)) {
        return 0;
    }
    if (dom_shell_objective_value(shell, DOM_FIELD_ACCESSIBILITY_COST, &cost_q16)) {
        if (cost_q16 != DOM_FIELD_VALUE_UNKNOWN && cost_q16 > DOM_SHELL_ACCESSIBILITY_MAX_Q16) {
            dom_shell_set_refusal(shell, DOM_REFUSAL_PROCESS, "accessibility");
            dom_shell_set_status(shell, "move=refused");
            dom_shell_emit(shell, log, "client.nav.move",
                           "result=refused reason=accessibility");
            return 0;
        }
    }
    shell->world.position[0] += dx;
    shell->world.position[1] += dy;
    shell->world.position[2] += adjusted_dz;
    {
        char detail[160];
        snprintf(detail, sizeof(detail),
                 "mode=%s dx=%.2f dy=%.2f dz=%.2f",
                 shell->world.active_mode,
                 (double)dx, (double)dy, (double)adjusted_dz);
        dom_shell_emit(shell, log, "client.nav.move", detail);
    }
    return 1;
}

static int dom_shell_run_local_process(dom_client_shell* shell,
                                       u32 kind,
                                       int has_resource,
                                       i32 resource_q16,
                                       int has_energy,
                                       i32 energy_q16,
                                       int has_min_support,
                                       i32 min_support_q16,
                                       int has_max_surface,
                                       i32 max_surface_q16,
                                       dom_app_ui_event_log* log,
                                       char* status,
                                       size_t status_cap,
                                       int emit_text)
{
    dom_local_process_desc desc;
    dom_local_process_world world;
    dom_local_process_context ctx;
    dom_local_process_result result;
    u64 intent_id;
    const char* name;
    int rc;

    if (!shell || !shell->world.active) {
        dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "no active world");
        dom_shell_set_status(shell, "process=refused");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        return D_APP_EXIT_UNAVAILABLE;
    }
    shell->tick += 1u;
    dom_local_process_desc_default(kind, &desc);
    if (has_resource) {
        desc.resource_amount_q16 = resource_q16;
    }
    if (has_energy) {
        desc.energy_load_q16 = energy_q16;
    }
    if (has_min_support) {
        desc.min_support_capacity_q16 = min_support_q16;
    }
    if (has_max_surface) {
        desc.max_surface_gradient_q16 = max_surface_q16;
    }

    dom_shell_refine_required_fields(shell, desc.required_field_mask);

    memset(&world, 0, sizeof(world));
    world.objective_fields = &shell->fields.objective;
    world.subjective_fields = &shell->fields.subjective;
    world.assembly = &shell->structure.assembly;
    world.claims = &shell->structure.claims;
    world.network = &shell->structure.network;
    world.structure = &shell->structure.structure;

    memset(&ctx, 0, sizeof(ctx));
    ctx.rng_seed = dom_shell_mix64(shell->rng_seed ^ shell->next_intent_id);
    ctx.knowledge_mask = shell->fields.knowledge_mask;
    ctx.confidence_q16 = shell->fields.confidence_q16;
    ctx.phys.now_act = (dom_act_time_t)shell->tick;
    ctx.phys.capability_mask = DOM_PHYS_CAP_TERRAIN | DOM_PHYS_CAP_EXTRACTION |
                               DOM_PHYS_CAP_CONSTRUCTION | DOM_PHYS_CAP_NETWORK |
                               DOM_PHYS_CAP_MACHINE;
    if (dom_shell_policy_set_contains(&shell->world.summary.authority, DOM_SHELL_AUTH_POLICY)) {
        ctx.phys.authority_mask = DOM_PHYS_AUTH_TERRAIN | DOM_PHYS_AUTH_EXTRACTION |
                                  DOM_PHYS_AUTH_CONSTRUCTION | DOM_PHYS_AUTH_NETWORK |
                                  DOM_PHYS_AUTH_MAINTENANCE;
    }

    rc = dom_local_process_apply(&world, &desc, 0u, 0u, &ctx, &result);
    intent_id = shell->next_intent_id++;
    name = dom_shell_process_name(kind);
    snprintf(shell->last_intent, sizeof(shell->last_intent),
             "intent_id=%llu process=%s", (unsigned long long)intent_id, name);
    snprintf(shell->last_plan, sizeof(shell->last_plan),
             "plan_id=%llu step=1 process=%s", (unsigned long long)intent_id, name);

    if (rc == 0 && result.process.ok) {
        if (kind == DOM_LOCAL_PROCESS_SURVEY) {
            shell->fields.knowledge_mask |= result.surveyed_field_mask;
            shell->fields.confidence_q16 = result.confidence_q16;
            shell->fields.uncertainty_q16 = result.uncertainty_q16;
        }
        dom_shell_set_status(shell, "process=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            printf("process=ok process=%s intent_id=%llu\n",
                   name, (unsigned long long)intent_id);
        }
        {
            char detail[160];
            snprintf(detail, sizeof(detail),
                     "process=%s intent=%llu tick=%u result=ok",
                     name, (unsigned long long)intent_id, (unsigned int)shell->tick);
            dom_shell_emit(shell, log, "client.process", detail);
        }
        return D_APP_EXIT_OK;
    }

    if (result.process.failure_mode_id == DOM_PHYS_FAIL_NO_CAPABILITY ||
        result.process.failure_mode_id == DOM_PHYS_FAIL_NO_AUTHORITY) {
        dom_shell_set_refusal(shell, DOM_REFUSAL_PROCESS, dom_shell_failure_reason(result.process.failure_mode_id));
        dom_shell_set_status(shell, "process=refused");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            printf("process=refused process=%s reason=%s\n",
                   name, dom_shell_failure_reason(result.process.failure_mode_id));
        }
        {
            char detail[160];
            snprintf(detail, sizeof(detail),
                     "process=%s intent=%llu tick=%u result=refused reason=%s",
                     name, (unsigned long long)intent_id, (unsigned int)shell->tick,
                     dom_shell_failure_reason(result.process.failure_mode_id));
            dom_shell_emit(shell, log, "client.process", detail);
        }
        return D_APP_EXIT_UNAVAILABLE;
    }

    dom_shell_set_refusal(shell,
                          (result.process.failure_mode_id == DOM_PHYS_FAIL_EPISTEMIC)
                              ? DOM_REFUSAL_PROCESS_EPISTEMIC
                              : DOM_REFUSAL_PROCESS_FAIL,
                          dom_shell_failure_reason(result.process.failure_mode_id));
    dom_shell_set_status(shell, "process=failed");
    if (status && status_cap > 0u) {
        snprintf(status, status_cap, "%s", shell->last_status);
    }
    if (emit_text) {
        printf("process=failed process=%s failure=%u reason=%s\n",
               name,
               (unsigned int)result.process.failure_mode_id,
               dom_shell_failure_reason(result.process.failure_mode_id));
    }
    {
        char detail[160];
        snprintf(detail, sizeof(detail),
                 "process=%s intent=%llu tick=%u result=failed failure=%u reason=%s",
                 name, (unsigned long long)intent_id, (unsigned int)shell->tick,
                 (unsigned int)result.process.failure_mode_id,
                 dom_shell_failure_reason(result.process.failure_mode_id));
        dom_shell_emit(shell, log, "client.process", detail);
    }
    return D_APP_EXIT_OK;
}

static int dom_shell_select_template(dom_client_shell* shell, const char* value, uint32_t* out_index)
{
    uint32_t i;
    if (!shell || !value || !value[0]) {
        return 0;
    }
    for (i = 0u; i < shell->registry.count; ++i) {
        if (strcmp(shell->registry.templates[i].template_id, value) == 0) {
            if (out_index) {
                *out_index = i;
            }
            return 1;
        }
    }
    return 0;
}

static void dom_shell_list_templates(const dom_client_shell* shell, int emit_text)
{
    uint32_t i;
    if (!shell || !emit_text) {
        return;
    }
    printf("templates=%u\n", (unsigned int)shell->registry.count);
    for (i = 0u; i < shell->registry.count; ++i) {
        const dom_shell_template* t = &shell->registry.templates[i];
        printf("template_id=%s version=%s source=%s\n",
               t->template_id, t->version, t->source);
        printf("template_desc=%s\n", t->description);
    }
}

static void dom_shell_print_world(const dom_client_shell* shell, int emit_text)
{
    if (!shell || !emit_text) {
        return;
    }
    if (!shell->world.active) {
        printf("world=inactive\n");
        return;
    }
    printf("worlddef_id=%s\n", shell->world.summary.worlddef_id);
    printf("template_id=%s\n", shell->world.summary.template_id);
    printf("spawn_node_id=%s\n", shell->world.summary.spawn_node_id);
    printf("spawn_frame_id=%s\n", shell->world.summary.spawn_frame_id);
    printf("position=%.2f,%.2f,%.2f\n",
           shell->world.position[0],
           shell->world.position[1],
           shell->world.position[2]);
    printf("mode=%s\n", shell->world.active_mode[0] ? shell->world.active_mode : "none");
}

static char* dom_shell_trim_inplace(char* text)
{
    char* end;
    if (!text) {
        return text;
    }
    while (*text && isspace((unsigned char)*text)) {
        text++;
    }
    end = text + strlen(text);
    while (end > text && isspace((unsigned char)end[-1])) {
        end--;
    }
    *end = '\0';
    return text;
}

static int dom_shell_execute_batch(dom_client_shell* shell,
                                   const char* script,
                                   dom_app_ui_event_log* log,
                                   char* status,
                                   size_t status_cap,
                                   int emit_text)
{
    char* buf = 0;
    char* cursor;
    size_t script_len = 0u;
    int last = D_APP_EXIT_OK;
    if (!script || !script[0]) {
        return D_APP_EXIT_USAGE;
    }
    script_len = strlen(script);
    buf = (char*)malloc(script_len + 1u);
    if (!buf) {
        if (emit_text) {
            fprintf(stderr, "client: batch refused (out of memory)\n");
        }
        return D_APP_EXIT_FAILURE;
    }
    memcpy(buf, script, script_len + 1u);
    cursor = buf;
    while (cursor) {
        char* sep = strchr(cursor, ';');
        if (sep) {
            *sep = '\0';
        }
        cursor = dom_shell_trim_inplace(cursor);
        if (cursor && cursor[0]) {
            last = dom_client_shell_execute(shell, cursor, log, status, status_cap, emit_text);
        }
        cursor = sep ? (sep + 1u) : 0;
    }
    free(buf);
    return last;
}

int dom_client_shell_execute(dom_client_shell* shell,
                             const char* cmdline,
                             dom_app_ui_event_log* log,
                             char* status,
                             size_t status_cap,
                             int emit_text)
{
    char buf[256];
    char* token;
    char* next;
    if (status && status_cap > 0u) {
        status[0] = '\0';
    }
    if (!shell || !cmdline || !cmdline[0]) {
        return D_APP_EXIT_USAGE;
    }
    if (strncmp(cmdline, "batch", 5) == 0 &&
        (cmdline[5] == '\0' || isspace((unsigned char)cmdline[5]))) {
        const char* script = cmdline + 5;
        while (*script && isspace((unsigned char)*script)) {
            script++;
        }
        return dom_shell_execute_batch(shell, script, log, status, status_cap, emit_text);
    }
    strncpy(buf, cmdline, sizeof(buf) - 1u);
    buf[sizeof(buf) - 1u] = '\0';
    token = strtok(buf, " \t");
    if (!token) {
        return D_APP_EXIT_USAGE;
    }
    if (strcmp(token, "help") == 0) {
        if (emit_text) {
            printf("commands: templates new-world load save inspect-replay mode where fields events batch exit\n");
            printf("          survey collect assemble connect inspect repair field-set simulate\n");
            printf("          agent-add agent-list agent-possess agent-release agent-know\n");
            printf("          goal-add goal-list delegate delegations delegate-revoke\n");
            printf("          authority-grant authority-revoke authority-list\n");
            printf("          constraint-add constraint-revoke constraint-list institution-create institution-list\n");
            printf("          network-create network-node network-edge network-config network-list\n");
        }
        dom_shell_set_status(shell, "help=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "templates") == 0) {
        dom_shell_list_templates(shell, emit_text);
        dom_shell_set_status(shell, "templates=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "new-world") == 0 || strcmp(token, "new") == 0 || strcmp(token, "start") == 0) {
        uint32_t template_index = shell->create_template_index;
        uint64_t seed = shell->create_seed;
        dom_shell_policy_set movement = shell->create_movement;
        dom_shell_policy_set authority = shell->create_authority;
        dom_shell_policy_set mode = shell->create_mode;
        dom_shell_policy_set debug = shell->create_debug;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "template") == 0) {
                if (!dom_shell_select_template(shell, eq + 1, &template_index)) {
                    dom_shell_set_refusal(shell, DOM_REFUSAL_TEMPLATE, "template not found");
                }
            } else if (strcmp(next, "seed") == 0) {
                dom_shell_parse_u64(eq + 1, &seed);
            } else if (strcmp(next, "policy.movement") == 0) {
                dom_shell_policy_set_from_csv(&movement, eq + 1);
            } else if (strcmp(next, "policy.authority") == 0) {
                dom_shell_policy_set_from_csv(&authority, eq + 1);
            } else if (strcmp(next, "policy.mode") == 0) {
                dom_shell_policy_set_from_csv(&mode, eq + 1);
            } else if (strcmp(next, "policy.debug") == 0) {
                dom_shell_policy_set_from_csv(&debug, eq + 1);
            }
        }
        shell->create_template_index = template_index;
        shell->create_seed = seed;
        dom_shell_policy_set_copy(&shell->create_movement, &movement);
        dom_shell_policy_set_copy(&shell->create_authority, &authority);
        dom_shell_policy_set_copy(&shell->create_mode, &mode);
        dom_shell_policy_set_copy(&shell->create_debug, &debug);
        return dom_client_shell_create_world(shell, log, status, status_cap, emit_text);
    }
    if (strcmp(token, "field-set") == 0) {
        const char* field_name = 0;
        const char* field_value = 0;
        u32 field_id = 0u;
        i32 value_q16 = 0;
        int value_set = 0;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "field") == 0) {
                field_name = eq + 1;
            } else if (strcmp(next, "field_id") == 0) {
                field_id = (u32)strtoul(eq + 1, 0, 10);
            } else if (strcmp(next, "value") == 0) {
                field_value = eq + 1;
            }
        }
        if (field_id == 0u && field_name) {
            (void)dom_shell_field_name_to_id(&shell->fields, field_name, &field_id);
        }
        if (!field_id || !field_value) {
            return D_APP_EXIT_USAGE;
        }
        if (strcmp(field_value, "unknown") == 0 || strcmp(field_value, "latent") == 0) {
            value_q16 = DOM_FIELD_VALUE_UNKNOWN;
            value_set = 1;
        } else {
            value_set = dom_shell_parse_q16(field_value, &value_q16);
        }
        if (!value_set) {
            return D_APP_EXIT_USAGE;
        }
        if (dom_field_set_value(&shell->fields.objective, field_id, 0u, 0u, value_q16) != 0) {
            dom_shell_set_refusal(shell, DOM_REFUSAL_PROCESS, "field missing");
            dom_shell_set_status(shell, "field_set=refused");
            if (status && status_cap > 0u) {
                snprintf(status, status_cap, "%s", shell->last_status);
            }
            return D_APP_EXIT_UNAVAILABLE;
        }
        dom_shell_set_status(shell, "field_set=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            char buf[32];
            dom_shell_format_q16(buf, sizeof(buf), value_q16);
            printf("field_set=ok field_id=%u value=%s\n", (unsigned int)field_id, buf);
        }
        {
            char detail[128];
            char buf[32];
            dom_shell_format_q16(buf, sizeof(buf), value_q16);
            snprintf(detail, sizeof(detail), "field_id=%u value=%s", (unsigned int)field_id, buf);
            dom_shell_emit(shell, log, "client.field.set", detail);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "fields") == 0) {
        u32 i;
        if (emit_text) {
            printf("fields=%u\n", (unsigned int)shell->fields.field_count);
            printf("knowledge_mask=0x%08x confidence_q16=%u uncertainty_q16=%u\n",
                   (unsigned int)shell->fields.knowledge_mask,
                   (unsigned int)shell->fields.confidence_q16,
                   (unsigned int)shell->fields.uncertainty_q16);
            for (i = 0u; i < shell->fields.field_count; ++i) {
                u32 field_id = shell->fields.field_ids[i];
                i32 obj = DOM_FIELD_VALUE_UNKNOWN;
                i32 subj = DOM_FIELD_VALUE_UNKNOWN;
                char obj_buf[32];
                char subj_buf[32];
                const dom_physical_field_desc* desc = dom_physical_field_desc_get(field_id);
                const char* name = desc && desc->name ? desc->name : "field";
                (void)dom_field_get_value(&shell->fields.objective, field_id, 0u, 0u, &obj);
                (void)dom_field_get_value(&shell->fields.subjective, field_id, 0u, 0u, &subj);
                dom_shell_format_q16(obj_buf, sizeof(obj_buf), obj);
                dom_shell_format_q16(subj_buf, sizeof(subj_buf), subj);
                printf("field %s objective=%s subjective=%s known=%u\n",
                       name,
                       obj_buf,
                       subj_buf,
                       (shell->fields.knowledge_mask & DOM_FIELD_BIT(field_id)) ? 1u : 0u);
            }
        }
        dom_shell_set_status(shell, "fields=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "events") == 0) {
        if (emit_text) {
            u32 i;
            u32 idx = shell->events.head;
            printf("events=%u\n", (unsigned int)shell->events.count);
            for (i = 0u; i < shell->events.count; ++i) {
                printf("%s\n", shell->events.lines[idx]);
                idx = (idx + 1u) % DOM_SHELL_MAX_EVENTS;
            }
        }
        dom_shell_set_status(shell, "events=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "agent-add") == 0) {
        u64 agent_id = 0u;
        u32 caps = 0u;
        u32 auth = 0u;
        u32 know = 0u;
        u64 resource_ref = 0u;
        u64 dest_ref = 0u;
        u64 threat_ref = 0u;
        int has_caps = 0;
        int has_auth = 0;
        int has_know = 0;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "id") == 0) {
                (void)dom_shell_parse_u64(eq + 1, &agent_id);
            } else if (strcmp(next, "caps") == 0) {
                caps = dom_shell_parse_mask_csv(eq + 1, dom_shell_capability_token);
                has_caps = 1;
            } else if (strcmp(next, "auth") == 0 || strcmp(next, "authority") == 0) {
                auth = dom_shell_parse_mask_csv(eq + 1, dom_shell_authority_token);
                has_auth = 1;
            } else if (strcmp(next, "know") == 0 || strcmp(next, "knowledge") == 0) {
                know = dom_shell_parse_mask_csv(eq + 1, dom_shell_knowledge_token);
                has_know = 1;
            } else if (strcmp(next, "resource") == 0) {
                (void)dom_shell_parse_u64(eq + 1, &resource_ref);
            } else if (strcmp(next, "dest") == 0 || strcmp(next, "destination") == 0) {
                (void)dom_shell_parse_u64(eq + 1, &dest_ref);
            } else if (strcmp(next, "threat") == 0) {
                (void)dom_shell_parse_u64(eq + 1, &threat_ref);
            }
        }
        if (!has_caps) {
            caps = 0u;
        }
        if (!has_auth) {
            auth = 0u;
        }
        if (!has_know) {
            know = 0u;
        }
        if (resource_ref != 0u || dest_ref != 0u) {
            know |= AGENT_KNOW_INFRA;
        }
        if (!dom_shell_agent_add(shell, agent_id, caps, auth, know)) {
            dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "agent add failed");
            dom_shell_set_status(shell, "agent_add=refused");
            if (status && status_cap > 0u) {
                snprintf(status, status_cap, "%s", shell->last_status);
            }
            return D_APP_EXIT_UNAVAILABLE;
        }
        {
            dom_agent_belief* belief = dom_shell_belief_for_agent(shell,
                                                                  shell->agents[shell->agent_count - 1u].agent_id);
            if (belief) {
                belief->known_resource_ref = resource_ref;
                belief->known_destination_ref = dest_ref;
                belief->known_threat_ref = threat_ref;
            }
        }
        dom_shell_set_status(shell, "agent_add=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            printf("agent_add=ok agent_id=%llu\n",
                   (unsigned long long)shell->agents[shell->agent_count - 1u].agent_id);
        }
        {
            char detail[160];
            snprintf(detail, sizeof(detail),
                     "agent_id=%llu result=ok",
                     (unsigned long long)shell->agents[shell->agent_count - 1u].agent_id);
            dom_shell_emit(shell, log, "client.agent.add", detail);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "agent-list") == 0 || strcmp(token, "agents") == 0) {
        if (emit_text) {
            u32 i;
            printf("agents=%u\n", (unsigned int)shell->agent_count);
            for (i = 0u; i < shell->agent_count; ++i) {
                const dom_shell_agent_record* record = &shell->agents[i];
                const dom_agent_belief* belief = &shell->beliefs[i];
                const dom_agent_capability* cap = &shell->caps[i];
                char cap_buf[16];
                char auth_buf[16];
                char know_buf[16];
                dom_shell_format_mask_hex(cap_buf, sizeof(cap_buf), cap->capability_mask);
                dom_shell_format_mask_hex(auth_buf, sizeof(auth_buf), cap->authority_mask);
                dom_shell_format_mask_hex(know_buf, sizeof(know_buf), belief->knowledge_mask);
                printf("agent id=%llu caps=%s auth=%s know=%s goal=%s refusal=%s possessed=%u\n",
                       (unsigned long long)record->agent_id,
                       cap_buf,
                       auth_buf,
                       know_buf,
                       dom_shell_goal_type_name(record->last_goal_type),
                       agent_refusal_to_string((agent_refusal_code)record->last_refusal),
                       (shell->possessed_agent_id == record->agent_id) ? 1u : 0u);
            }
        }
        dom_shell_set_status(shell, "agent_list=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "agent-possess") == 0 || strcmp(token, "possess") == 0) {
        u64 agent_id = 0u;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (eq) {
                *eq = '\0';
                if (strcmp(next, "id") == 0) {
                    dom_shell_parse_u64(eq + 1, &agent_id);
                }
            } else if (agent_id == 0u) {
                dom_shell_parse_u64(next, &agent_id);
            }
        }
        if (agent_id == 0u || dom_shell_agent_index(shell, agent_id) < 0) {
            dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "agent missing");
            dom_shell_set_status(shell, "agent_possess=refused");
            if (status && status_cap > 0u) {
                snprintf(status, status_cap, "%s", shell->last_status);
            }
            return D_APP_EXIT_UNAVAILABLE;
        }
        shell->possessed_agent_id = agent_id;
        dom_shell_set_status(shell, "agent_possess=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            printf("agent_possess=ok agent_id=%llu\n", (unsigned long long)agent_id);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "agent-release") == 0 || strcmp(token, "release") == 0) {
        shell->possessed_agent_id = 0u;
        dom_shell_set_status(shell, "agent_release=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            printf("agent_release=ok\n");
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "agent-know") == 0) {
        u64 agent_id = 0u;
        u64 resource_ref = 0u;
        u64 dest_ref = 0u;
        u64 threat_ref = 0u;
        u32 know = 0u;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "id") == 0) {
                dom_shell_parse_u64(eq + 1, &agent_id);
            } else if (strcmp(next, "resource") == 0) {
                dom_shell_parse_u64(eq + 1, &resource_ref);
            } else if (strcmp(next, "dest") == 0 || strcmp(next, "destination") == 0) {
                dom_shell_parse_u64(eq + 1, &dest_ref);
            } else if (strcmp(next, "threat") == 0) {
                dom_shell_parse_u64(eq + 1, &threat_ref);
            } else if (strcmp(next, "knowledge") == 0 || strcmp(next, "know") == 0) {
                know = dom_shell_parse_mask_csv(eq + 1, dom_shell_knowledge_token);
            }
        }
        if (agent_id == 0u) {
            return D_APP_EXIT_USAGE;
        }
        {
            dom_agent_belief* belief = dom_shell_belief_for_agent(shell, agent_id);
            if (!belief) {
                dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "agent missing");
                dom_shell_set_status(shell, "agent_know=refused");
                if (status && status_cap > 0u) {
                    snprintf(status, status_cap, "%s", shell->last_status);
                }
                return D_APP_EXIT_UNAVAILABLE;
            }
            if (resource_ref != 0u) {
                belief->known_resource_ref = resource_ref;
                know |= AGENT_KNOW_INFRA;
            }
            if (dest_ref != 0u) {
                belief->known_destination_ref = dest_ref;
                know |= AGENT_KNOW_INFRA;
            }
            if (threat_ref != 0u) {
                belief->known_threat_ref = threat_ref;
                know |= AGENT_KNOW_THREAT;
            }
            if (know != 0u) {
                belief->knowledge_mask |= know;
            }
        }
        dom_shell_set_status(shell, "agent_know=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            printf("agent_know=ok agent_id=%llu\n", (unsigned long long)agent_id);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "goal-add") == 0) {
        u64 agent_id = 0u;
        u32 goal_type = AGENT_GOAL_SURVEY;
        u32 priority = 10u;
        u32 urgency = 0u;
        int require_delegation = -1;
        int allow_unknown = -1;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "agent") == 0) {
                dom_shell_parse_u64(eq + 1, &agent_id);
            } else if (strcmp(next, "type") == 0) {
                goal_type = dom_shell_goal_type_from_string(eq + 1);
            } else if (strcmp(next, "priority") == 0) {
                priority = (u32)strtoul(eq + 1, 0, 10);
            } else if (strcmp(next, "urgency") == 0) {
                urgency = (u32)strtoul(eq + 1, 0, 10);
            } else if (strcmp(next, "require_delegation") == 0) {
                require_delegation = atoi(eq + 1) ? 1 : 0;
            } else if (strcmp(next, "allow_unknown") == 0) {
                allow_unknown = atoi(eq + 1) ? 1 : 0;
            }
        }
        if (agent_id == 0u) {
            return D_APP_EXIT_USAGE;
        }
        {
            agent_goal_desc desc;
            u64 goal_id = 0u;
            dom_shell_goal_desc_default(agent_id, goal_type, &desc);
            desc.base_priority = priority;
            desc.urgency = urgency;
            if (require_delegation == 0) {
                desc.flags &= ~AGENT_GOAL_FLAG_REQUIRE_DELEGATION;
            } else if (require_delegation > 0) {
                desc.flags |= AGENT_GOAL_FLAG_REQUIRE_DELEGATION;
            }
            if (allow_unknown == 0) {
                desc.flags &= ~AGENT_GOAL_FLAG_ALLOW_UNKNOWN;
            } else if (allow_unknown > 0) {
                desc.flags |= AGENT_GOAL_FLAG_ALLOW_UNKNOWN;
            }
            if (agent_goal_register(&shell->goal_registry, &desc, &goal_id) != 0) {
                dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "goal add failed");
                dom_shell_set_status(shell, "goal_add=refused");
                if (status && status_cap > 0u) {
                    snprintf(status, status_cap, "%s", shell->last_status);
                }
                return D_APP_EXIT_UNAVAILABLE;
            }
            dom_shell_set_status(shell, "goal_add=ok");
            if (status && status_cap > 0u) {
                snprintf(status, status_cap, "%s", shell->last_status);
            }
            if (emit_text) {
                printf("goal_add=ok goal_id=%llu agent_id=%llu type=%s\n",
                       (unsigned long long)goal_id,
                       (unsigned long long)agent_id,
                       dom_shell_goal_type_name(goal_type));
            }
            {
                char detail[180];
                snprintf(detail, sizeof(detail),
                         "goal_id=%llu agent_id=%llu type=%s result=ok",
                         (unsigned long long)goal_id,
                         (unsigned long long)agent_id,
                         dom_shell_goal_type_name(goal_type));
                dom_shell_emit(shell, log, "client.agent.goal", detail);
            }
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "goal-list") == 0 || strcmp(token, "goals") == 0) {
        if (emit_text) {
            u32 i;
            printf("goals=%u\n", (unsigned int)shell->goal_registry.count);
            for (i = 0u; i < shell->goal_registry.count; ++i) {
                const agent_goal* goal = &shell->goal_registry.goals[i];
                printf("goal id=%llu agent=%llu type=%s status=%u flags=0x%08x failures=%u\n",
                       (unsigned long long)goal->goal_id,
                       (unsigned long long)goal->agent_id,
                       dom_shell_goal_type_name(goal->type),
                       (unsigned int)goal->status,
                       (unsigned int)goal->flags,
                       (unsigned int)goal->failure_count);
            }
        }
        dom_shell_set_status(shell, "goal_list=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "delegate") == 0) {
        u64 delegator = 0u;
        u64 delegatee = 0u;
        u64 goal_id = 0u;
        u64 expiry_act = 0u;
        u64 delegation_id = 0u;
        u32 process_mask = 0u;
        u32 authority_mask = 0u;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "delegator") == 0) {
                dom_shell_parse_u64(eq + 1, &delegator);
            } else if (strcmp(next, "delegatee") == 0) {
                dom_shell_parse_u64(eq + 1, &delegatee);
            } else if (strcmp(next, "goal") == 0) {
                dom_shell_parse_u64(eq + 1, &goal_id);
            } else if (strcmp(next, "expiry") == 0) {
                dom_shell_parse_u64(eq + 1, &expiry_act);
            } else if (strcmp(next, "id") == 0) {
                dom_shell_parse_u64(eq + 1, &delegation_id);
            } else if (strcmp(next, "process") == 0) {
                process_mask = dom_shell_parse_mask_csv(eq + 1, dom_shell_process_token);
            } else if (strcmp(next, "authority") == 0) {
                authority_mask = dom_shell_parse_mask_csv(eq + 1, dom_shell_authority_token);
            }
        }
        if (delegator == 0u || delegatee == 0u || goal_id == 0u) {
            return D_APP_EXIT_USAGE;
        }
        if (!process_mask) {
            process_mask = 0xFFFFFFFFu;
        }
        {
            agent_goal* goal = agent_goal_find(&shell->goal_registry, goal_id);
            dom_agent_capability* cap = dom_shell_cap_for_agent(shell, delegatee);
            dom_agent_belief* belief = dom_shell_belief_for_agent(shell, delegatee);
            u32 refusal = AGENT_REFUSAL_NONE;
            int accepted = 1;
            if (!goal || goal->agent_id != delegatee) {
                accepted = 0;
                refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
            } else if (!cap) {
                accepted = 0;
                refusal = AGENT_REFUSAL_INSUFFICIENT_CAPABILITY;
            } else if ((cap->capability_mask & goal->preconditions.required_capabilities) !=
                       goal->preconditions.required_capabilities) {
                accepted = 0;
                refusal = AGENT_REFUSAL_INSUFFICIENT_CAPABILITY;
            } else if (belief &&
                       (belief->knowledge_mask & goal->preconditions.required_knowledge) !=
                       goal->preconditions.required_knowledge &&
                       (goal->flags & AGENT_GOAL_FLAG_ALLOW_UNKNOWN) == 0u) {
                accepted = 0;
                refusal = AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE;
            }
            if (!accepted) {
                dom_shell_set_refusal(shell, DOM_REFUSAL_PROCESS, agent_refusal_to_string((agent_refusal_code)refusal));
                dom_shell_set_status(shell, "delegation=refused");
                if (status && status_cap > 0u) {
                    snprintf(status, status_cap, "%s", shell->last_status);
                }
                if (emit_text) {
                    printf("delegation=refused goal_id=%llu reason=%s\n",
                           (unsigned long long)goal_id,
                           agent_refusal_to_string((agent_refusal_code)refusal));
                }
                {
                    char detail[200];
                    snprintf(detail, sizeof(detail),
                             "goal_id=%llu delegator=%llu delegatee=%llu result=refused reason=%s",
                             (unsigned long long)goal_id,
                             (unsigned long long)delegator,
                             (unsigned long long)delegatee,
                             agent_refusal_to_string((agent_refusal_code)refusal));
                    dom_shell_emit(shell, log, "client.delegation", detail);
                }
                return D_APP_EXIT_UNAVAILABLE;
            }
            if (delegation_id == 0u) {
                delegation_id = shell->next_delegation_id++;
                if (delegation_id == 0u) {
                    delegation_id = shell->next_delegation_id++;
                }
            } else if (delegation_id >= shell->next_delegation_id) {
                shell->next_delegation_id = delegation_id + 1u;
            }
            if (agent_delegation_register(&shell->delegation_registry,
                                          delegation_id,
                                          delegator,
                                          delegatee,
                                          AGENT_DELEGATION_GOAL | (authority_mask ? AGENT_DELEGATION_AUTHORITY : 0u),
                                          process_mask,
                                          authority_mask,
                                          (dom_act_time_t)expiry_act,
                                          0u) != 0) {
                dom_shell_set_refusal(shell, DOM_REFUSAL_PROCESS, "delegation failed");
                dom_shell_set_status(shell, "delegation=refused");
                if (status && status_cap > 0u) {
                    snprintf(status, status_cap, "%s", shell->last_status);
                }
                return D_APP_EXIT_UNAVAILABLE;
            }
            dom_shell_set_status(shell, "delegation=ok");
            if (status && status_cap > 0u) {
                snprintf(status, status_cap, "%s", shell->last_status);
            }
            if (emit_text) {
                printf("delegation=ok delegation_id=%llu goal_id=%llu delegatee=%llu\n",
                       (unsigned long long)delegation_id,
                       (unsigned long long)goal_id,
                       (unsigned long long)delegatee);
            }
            {
                char detail[200];
                snprintf(detail, sizeof(detail),
                         "delegation_id=%llu goal_id=%llu delegator=%llu delegatee=%llu result=accepted",
                         (unsigned long long)delegation_id,
                         (unsigned long long)goal_id,
                         (unsigned long long)delegator,
                         (unsigned long long)delegatee);
                dom_shell_emit(shell, log, "client.delegation", detail);
            }
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "delegations") == 0) {
        if (emit_text) {
            u32 i;
            printf("delegations=%u\n", (unsigned int)shell->delegation_registry.count);
            for (i = 0u; i < shell->delegation_registry.count; ++i) {
                const agent_delegation* del = &shell->delegations[i];
                printf("delegation id=%llu delegator=%llu delegatee=%llu kind=0x%08x process=0x%08x authority=0x%08x revoked=%u\n",
                       (unsigned long long)del->delegation_id,
                       (unsigned long long)del->delegator_ref,
                       (unsigned long long)del->delegatee_ref,
                       (unsigned int)del->delegation_kind,
                       (unsigned int)del->allowed_process_mask,
                       (unsigned int)del->authority_mask,
                       (unsigned int)del->revoked);
            }
        }
        dom_shell_set_status(shell, "delegations=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "delegate-revoke") == 0) {
        u64 delegation_id = 0u;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (eq) {
                *eq = '\0';
                if (strcmp(next, "id") == 0) {
                    dom_shell_parse_u64(eq + 1, &delegation_id);
                }
            } else if (delegation_id == 0u) {
                dom_shell_parse_u64(next, &delegation_id);
            }
        }
        if (delegation_id == 0u) {
            return D_APP_EXIT_USAGE;
        }
        if (agent_delegation_revoke(&shell->delegation_registry, delegation_id) != 0) {
            dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "delegation not found");
            dom_shell_set_status(shell, "delegation_revoke=refused");
            if (status && status_cap > 0u) {
                snprintf(status, status_cap, "%s", shell->last_status);
            }
            return D_APP_EXIT_UNAVAILABLE;
        }
        dom_shell_set_status(shell, "delegation_revoke=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            printf("delegation_revoke=ok id=%llu\n", (unsigned long long)delegation_id);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "authority-grant") == 0) {
        u64 grant_id = 0u;
        u64 granter = 0u;
        u64 grantee = 0u;
        u64 expiry_act = 0u;
        u32 authority_mask = 0u;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "id") == 0) {
                dom_shell_parse_u64(eq + 1, &grant_id);
            } else if (strcmp(next, "granter") == 0) {
                dom_shell_parse_u64(eq + 1, &granter);
            } else if (strcmp(next, "grantee") == 0) {
                dom_shell_parse_u64(eq + 1, &grantee);
            } else if (strcmp(next, "authority") == 0 || strcmp(next, "mask") == 0) {
                authority_mask = dom_shell_parse_mask_csv(eq + 1, dom_shell_authority_token);
            } else if (strcmp(next, "expiry") == 0) {
                dom_shell_parse_u64(eq + 1, &expiry_act);
            }
        }
        if (granter == 0u || grantee == 0u) {
            return D_APP_EXIT_USAGE;
        }
        if (grant_id == 0u) {
            grant_id = shell->next_authority_id++;
            if (grant_id == 0u) {
                grant_id = shell->next_authority_id++;
            }
        } else if (grant_id >= shell->next_authority_id) {
            shell->next_authority_id = grant_id + 1u;
        }
        if (agent_authority_grant_register(&shell->authority_registry,
                                           grant_id,
                                           granter,
                                           grantee,
                                           authority_mask,
                                           (dom_act_time_t)expiry_act,
                                           0u) != 0) {
            dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "authority grant failed");
            dom_shell_set_status(shell, "authority_grant=refused");
            if (status && status_cap > 0u) {
                snprintf(status, status_cap, "%s", shell->last_status);
            }
            return D_APP_EXIT_UNAVAILABLE;
        }
        dom_shell_set_status(shell, "authority_grant=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            printf("authority_grant=ok grant_id=%llu grantee=%llu\n",
                   (unsigned long long)grant_id,
                   (unsigned long long)grantee);
        }
        {
            char detail[200];
            snprintf(detail, sizeof(detail),
                     "grant_id=%llu granter=%llu grantee=%llu authority=0x%08x result=ok",
                     (unsigned long long)grant_id,
                     (unsigned long long)granter,
                     (unsigned long long)grantee,
                     (unsigned int)authority_mask);
            dom_shell_emit(shell, log, "client.authority.grant", detail);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "authority-revoke") == 0) {
        u64 grant_id = 0u;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (eq) {
                *eq = '\0';
                if (strcmp(next, "id") == 0) {
                    dom_shell_parse_u64(eq + 1, &grant_id);
                }
            } else if (grant_id == 0u) {
                dom_shell_parse_u64(next, &grant_id);
            }
        }
        if (grant_id == 0u) {
            return D_APP_EXIT_USAGE;
        }
        if (agent_authority_grant_revoke(&shell->authority_registry, grant_id) != 0) {
            dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "grant not found");
            dom_shell_set_status(shell, "authority_revoke=refused");
            if (status && status_cap > 0u) {
                snprintf(status, status_cap, "%s", shell->last_status);
            }
            return D_APP_EXIT_UNAVAILABLE;
        }
        dom_shell_set_status(shell, "authority_revoke=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            printf("authority_revoke=ok id=%llu\n", (unsigned long long)grant_id);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "authority-list") == 0) {
        if (emit_text) {
            u32 i;
            printf("authority_grants=%u\n", (unsigned int)shell->authority_registry.count);
            for (i = 0u; i < shell->authority_registry.count; ++i) {
                const agent_authority_grant* grant = &shell->authority_grants[i];
                printf("grant id=%llu granter=%llu grantee=%llu authority=0x%08x revoked=%u\n",
                       (unsigned long long)grant->grant_id,
                       (unsigned long long)grant->granter_id,
                       (unsigned long long)grant->grantee_id,
                       (unsigned int)grant->authority_mask,
                       (unsigned int)grant->revoked);
            }
        }
        dom_shell_set_status(shell, "authority_list=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "constraint-add") == 0) {
        u64 constraint_id = 0u;
        u64 institution_id = 0u;
        u64 target_id = 0u;
        u64 expiry_act = 0u;
        u32 process_mask = 0u;
        u32 mode = AGENT_CONSTRAINT_DENY;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "id") == 0) {
                dom_shell_parse_u64(eq + 1, &constraint_id);
            } else if (strcmp(next, "institution") == 0) {
                dom_shell_parse_u64(eq + 1, &institution_id);
            } else if (strcmp(next, "target") == 0 || strcmp(next, "agent") == 0) {
                dom_shell_parse_u64(eq + 1, &target_id);
            } else if (strcmp(next, "process") == 0) {
                process_mask = dom_shell_parse_mask_csv(eq + 1, dom_shell_process_token);
            } else if (strcmp(next, "mode") == 0) {
                mode = (strcmp(eq + 1, "allow") == 0) ? AGENT_CONSTRAINT_ALLOW : AGENT_CONSTRAINT_DENY;
            } else if (strcmp(next, "expiry") == 0) {
                dom_shell_parse_u64(eq + 1, &expiry_act);
            }
        }
        if (institution_id == 0u || target_id == 0u) {
            return D_APP_EXIT_USAGE;
        }
        if (constraint_id == 0u) {
            constraint_id = shell->next_constraint_id++;
            if (constraint_id == 0u) {
                constraint_id = shell->next_constraint_id++;
            }
        } else if (constraint_id >= shell->next_constraint_id) {
            shell->next_constraint_id = constraint_id + 1u;
        }
        if (agent_constraint_register(&shell->constraint_registry,
                                      constraint_id,
                                      institution_id,
                                      target_id,
                                      process_mask,
                                      mode,
                                      (dom_act_time_t)expiry_act,
                                      0u) != 0) {
            dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "constraint failed");
            dom_shell_set_status(shell, "constraint_add=refused");
            if (status && status_cap > 0u) {
                snprintf(status, status_cap, "%s", shell->last_status);
            }
            return D_APP_EXIT_UNAVAILABLE;
        }
        dom_shell_set_status(shell, "constraint_add=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            printf("constraint_add=ok id=%llu target=%llu\n",
                   (unsigned long long)constraint_id,
                   (unsigned long long)target_id);
        }
        {
            char detail[200];
            snprintf(detail, sizeof(detail),
                     "constraint_id=%llu institution=%llu target=%llu result=ok",
                     (unsigned long long)constraint_id,
                     (unsigned long long)institution_id,
                     (unsigned long long)target_id);
            dom_shell_emit(shell, log, "client.constraint.apply", detail);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "constraint-revoke") == 0) {
        u64 constraint_id = 0u;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (eq) {
                *eq = '\0';
                if (strcmp(next, "id") == 0) {
                    dom_shell_parse_u64(eq + 1, &constraint_id);
                }
            } else if (constraint_id == 0u) {
                dom_shell_parse_u64(next, &constraint_id);
            }
        }
        if (constraint_id == 0u) {
            return D_APP_EXIT_USAGE;
        }
        if (agent_constraint_revoke(&shell->constraint_registry, constraint_id) != 0) {
            dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "constraint not found");
            dom_shell_set_status(shell, "constraint_revoke=refused");
            if (status && status_cap > 0u) {
                snprintf(status, status_cap, "%s", shell->last_status);
            }
            return D_APP_EXIT_UNAVAILABLE;
        }
        dom_shell_set_status(shell, "constraint_revoke=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            printf("constraint_revoke=ok id=%llu\n", (unsigned long long)constraint_id);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "constraint-list") == 0) {
        if (emit_text) {
            u32 i;
            printf("constraints=%u\n", (unsigned int)shell->constraint_registry.count);
            for (i = 0u; i < shell->constraint_registry.count; ++i) {
                const agent_constraint* c = &shell->constraints[i];
                printf("constraint id=%llu institution=%llu target=%llu process=0x%08x mode=%u revoked=%u\n",
                       (unsigned long long)c->constraint_id,
                       (unsigned long long)c->institution_id,
                       (unsigned long long)c->target_agent_id,
                       (unsigned int)c->process_kind_mask,
                       (unsigned int)c->mode,
                       (unsigned int)c->revoked);
            }
        }
        dom_shell_set_status(shell, "constraint_list=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "institution-create") == 0) {
        u64 institution_id = 0u;
        u64 agent_id = 0u;
        u32 authority_mask = 0u;
        u32 legitimacy_q16 = AGENT_CONFIDENCE_MAX;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "id") == 0) {
                dom_shell_parse_u64(eq + 1, &institution_id);
            } else if (strcmp(next, "agent") == 0) {
                dom_shell_parse_u64(eq + 1, &agent_id);
            } else if (strcmp(next, "authority") == 0) {
                authority_mask = dom_shell_parse_mask_csv(eq + 1, dom_shell_authority_token);
            } else if (strcmp(next, "legitimacy") == 0) {
                i32 value_q16 = 0;
                if (dom_shell_parse_q16(eq + 1, &value_q16)) {
                    legitimacy_q16 = (u32)value_q16;
                }
            }
        }
        if (institution_id == 0u) {
            institution_id = shell->next_institution_id++;
            if (institution_id == 0u) {
                institution_id = shell->next_institution_id++;
            }
        } else if (institution_id >= shell->next_institution_id) {
            shell->next_institution_id = institution_id + 1u;
        }
        if (agent_id == 0u) {
            if (!dom_shell_agent_add(shell, 0u, 0u, 0u, 0u)) {
                dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "agent create failed");
                dom_shell_set_status(shell, "institution=refused");
                if (status && status_cap > 0u) {
                    snprintf(status, status_cap, "%s", shell->last_status);
                }
                return D_APP_EXIT_UNAVAILABLE;
            }
            agent_id = shell->agents[shell->agent_count - 1u].agent_id;
        }
        if (agent_institution_register(&shell->institution_registry,
                                       institution_id,
                                       agent_id,
                                       authority_mask,
                                       legitimacy_q16,
                                       (dom_act_time_t)shell->tick,
                                       0u) != 0) {
            dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "institution failed");
            dom_shell_set_status(shell, "institution=refused");
            if (status && status_cap > 0u) {
                snprintf(status, status_cap, "%s", shell->last_status);
            }
            return D_APP_EXIT_UNAVAILABLE;
        }
        dom_shell_set_status(shell, "institution=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            printf("institution=ok id=%llu agent=%llu\n",
                   (unsigned long long)institution_id,
                   (unsigned long long)agent_id);
        }
        {
            char detail[200];
            snprintf(detail, sizeof(detail),
                     "institution_id=%llu agent_id=%llu result=ok",
                     (unsigned long long)institution_id,
                     (unsigned long long)agent_id);
            dom_shell_emit(shell, log, "client.institution.create", detail);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "institution-list") == 0) {
        if (emit_text) {
            u32 i;
            printf("institutions=%u\n", (unsigned int)shell->institution_registry.count);
            for (i = 0u; i < shell->institution_registry.count; ++i) {
                const agent_institution* inst = &shell->institutions[i];
                printf("institution id=%llu agent=%llu authority=0x%08x status=%u legitimacy=%u\n",
                       (unsigned long long)inst->institution_id,
                       (unsigned long long)inst->agent_id,
                       (unsigned int)inst->authority_mask,
                       (unsigned int)inst->status,
                       (unsigned int)inst->legitimacy_q16);
            }
        }
        dom_shell_set_status(shell, "institution_list=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "network-create") == 0) {
        u64 network_id = 0u;
        u32 type = DOM_NETWORK_LOGISTICS;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "id") == 0) {
                dom_shell_parse_u64(eq + 1, &network_id);
            } else if (strcmp(next, "type") == 0) {
                type = dom_shell_network_type_from_string(eq + 1);
            }
        }
        if (!dom_shell_network_create(shell, network_id, type)) {
            dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "network create failed");
            dom_shell_set_status(shell, "network=refused");
            if (status && status_cap > 0u) {
                snprintf(status, status_cap, "%s", shell->last_status);
            }
            return D_APP_EXIT_UNAVAILABLE;
        }
        dom_shell_set_status(shell, "network=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            printf("network=ok id=%llu type=%s\n",
                   (unsigned long long)shell->networks[shell->network_count - 1u].network_id,
                   dom_shell_network_type_name(type));
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "network-node") == 0) {
        u64 network_id = 0u;
        u64 node_id = 0u;
        i32 capacity_q16 = DOM_SHELL_ENERGY_CAPACITY_Q16;
        i32 stored_q16 = 0;
        i32 loss_q16 = 0;
        i32 min_q16 = 0;
        u32 status_val = DOM_NETWORK_OK;
        int has_capacity = 0;
        int has_stored = 0;
        int has_loss = 0;
        int has_min = 0;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "network") == 0) {
                dom_shell_parse_u64(eq + 1, &network_id);
            } else if (strcmp(next, "id") == 0) {
                dom_shell_parse_u64(eq + 1, &node_id);
            } else if (strcmp(next, "capacity") == 0) {
                has_capacity = dom_shell_parse_q16(eq + 1, &capacity_q16);
            } else if (strcmp(next, "stored") == 0) {
                has_stored = dom_shell_parse_q16(eq + 1, &stored_q16);
            } else if (strcmp(next, "loss") == 0) {
                has_loss = dom_shell_parse_q16(eq + 1, &loss_q16);
            } else if (strcmp(next, "min") == 0 || strcmp(next, "min_required") == 0) {
                has_min = dom_shell_parse_q16(eq + 1, &min_q16);
            } else if (strcmp(next, "status") == 0) {
                status_val = (u32)strtoul(eq + 1, 0, 10);
            }
        }
        if (network_id == 0u || node_id == 0u) {
            return D_APP_EXIT_USAGE;
        }
        {
            dom_shell_network_state* net = dom_shell_network_find(shell, network_id);
            if (!net) {
                return D_APP_EXIT_UNAVAILABLE;
            }
            if (!has_capacity) {
                capacity_q16 = DOM_SHELL_ENERGY_CAPACITY_Q16;
            }
            if (!dom_network_add_node(&net->graph, node_id, capacity_q16)) {
                dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "node add failed");
                dom_shell_set_status(shell, "network_node=refused");
                if (status && status_cap > 0u) {
                    snprintf(status, status_cap, "%s", shell->last_status);
                }
                return D_APP_EXIT_UNAVAILABLE;
            }
            if (has_stored || has_loss || has_min) {
                dom_network_node* node = dom_network_find_node(&net->graph, node_id);
                if (node) {
                    if (has_stored) {
                        node->stored_q16 = stored_q16;
                    }
                    if (has_loss) {
                        node->loss_q16 = loss_q16;
                    }
                    if (has_min) {
                        node->min_required_q16 = min_q16;
                    }
                    node->status = status_val;
                }
            }
        }
        dom_shell_set_status(shell, "network_node=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            printf("network_node=ok network=%llu node=%llu\n",
                   (unsigned long long)network_id,
                   (unsigned long long)node_id);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "network-edge") == 0) {
        u64 network_id = 0u;
        u64 edge_id = 0u;
        u64 a = 0u;
        u64 b = 0u;
        i32 capacity_q16 = DOM_SHELL_ENERGY_CAPACITY_Q16;
        i32 loss_q16 = 0;
        u32 status_val = DOM_NETWORK_OK;
        int has_capacity = 0;
        int has_loss = 0;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "network") == 0) {
                dom_shell_parse_u64(eq + 1, &network_id);
            } else if (strcmp(next, "id") == 0) {
                dom_shell_parse_u64(eq + 1, &edge_id);
            } else if (strcmp(next, "a") == 0) {
                dom_shell_parse_u64(eq + 1, &a);
            } else if (strcmp(next, "b") == 0) {
                dom_shell_parse_u64(eq + 1, &b);
            } else if (strcmp(next, "capacity") == 0) {
                has_capacity = dom_shell_parse_q16(eq + 1, &capacity_q16);
            } else if (strcmp(next, "loss") == 0) {
                has_loss = dom_shell_parse_q16(eq + 1, &loss_q16);
            } else if (strcmp(next, "status") == 0) {
                status_val = (u32)strtoul(eq + 1, 0, 10);
            }
        }
        if (network_id == 0u || edge_id == 0u || a == 0u || b == 0u) {
            return D_APP_EXIT_USAGE;
        }
        {
            dom_shell_network_state* net = dom_shell_network_find(shell, network_id);
            if (!net) {
                return D_APP_EXIT_UNAVAILABLE;
            }
            if (!has_capacity) {
                capacity_q16 = DOM_SHELL_ENERGY_CAPACITY_Q16;
            }
            if (!dom_network_add_edge(&net->graph, edge_id, a, b, capacity_q16, loss_q16)) {
                dom_shell_set_refusal(shell, DOM_REFUSAL_INVALID, "edge add failed");
                dom_shell_set_status(shell, "network_edge=refused");
                if (status && status_cap > 0u) {
                    snprintf(status, status_cap, "%s", shell->last_status);
                }
                return D_APP_EXIT_UNAVAILABLE;
            }
            if (has_loss || status_val != DOM_NETWORK_OK) {
                dom_network_edge* edge = dom_network_find_edge(&net->graph, edge_id);
                if (edge) {
                    if (has_loss) {
                        edge->loss_q16 = loss_q16;
                    }
                    edge->status = status_val;
                }
            }
        }
        dom_shell_set_status(shell, "network_edge=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            printf("network_edge=ok network=%llu edge=%llu\n",
                   (unsigned long long)network_id,
                   (unsigned long long)edge_id);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "network-config") == 0) {
        u64 network_id = 0u;
        u64 node_id = 0u;
        u64 edge_id = 0u;
        i32 stored_q16 = 0;
        i32 loss_q16 = 0;
        i32 min_q16 = 0;
        u32 status_val = DOM_NETWORK_OK;
        int has_stored = 0;
        int has_loss = 0;
        int has_min = 0;
        int has_status = 0;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "network") == 0) {
                dom_shell_parse_u64(eq + 1, &network_id);
            } else if (strcmp(next, "node") == 0) {
                dom_shell_parse_u64(eq + 1, &node_id);
            } else if (strcmp(next, "edge") == 0) {
                dom_shell_parse_u64(eq + 1, &edge_id);
            } else if (strcmp(next, "stored") == 0) {
                has_stored = dom_shell_parse_q16(eq + 1, &stored_q16);
            } else if (strcmp(next, "loss") == 0) {
                has_loss = dom_shell_parse_q16(eq + 1, &loss_q16);
            } else if (strcmp(next, "min") == 0 || strcmp(next, "min_required") == 0) {
                has_min = dom_shell_parse_q16(eq + 1, &min_q16);
            } else if (strcmp(next, "status") == 0) {
                status_val = (u32)strtoul(eq + 1, 0, 10);
                has_status = 1;
            }
        }
        if (network_id == 0u) {
            return D_APP_EXIT_USAGE;
        }
        {
            dom_shell_network_state* net = dom_shell_network_find(shell, network_id);
            if (!net) {
                return D_APP_EXIT_UNAVAILABLE;
            }
            if (node_id != 0u) {
                dom_network_node* node = dom_network_find_node(&net->graph, node_id);
                if (node) {
                    if (has_stored) node->stored_q16 = stored_q16;
                    if (has_loss) node->loss_q16 = loss_q16;
                    if (has_min) node->min_required_q16 = min_q16;
                    if (has_status) node->status = status_val;
                }
            }
            if (edge_id != 0u) {
                dom_network_edge* edge = dom_network_find_edge(&net->graph, edge_id);
                if (edge) {
                    if (has_loss) edge->loss_q16 = loss_q16;
                    if (has_status) edge->status = status_val;
                }
            }
        }
        dom_shell_set_status(shell, "network_config=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        if (emit_text) {
            printf("network_config=ok network=%llu\n", (unsigned long long)network_id);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "network-list") == 0 || strcmp(token, "networks") == 0) {
        if (emit_text) {
            u32 i;
            printf("networks=%u\n", (unsigned int)shell->network_count);
            for (i = 0u; i < shell->network_count; ++i) {
                const dom_shell_network_state* net = &shell->networks[i];
                printf("network id=%llu type=%s nodes=%u edges=%u\n",
                       (unsigned long long)net->network_id,
                       dom_shell_network_type_name(net->graph.type),
                       (unsigned int)net->graph.node_count,
                       (unsigned int)net->graph.edge_count);
            }
        }
        dom_shell_set_status(shell, "network_list=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "simulate") == 0 || strcmp(token, "agent-step") == 0) {
        u32 ticks = 1u;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (eq) {
                *eq = '\0';
                if (strcmp(next, "ticks") == 0 || strcmp(next, "count") == 0) {
                    ticks = (u32)strtoul(eq + 1, 0, 10);
                }
            } else {
                ticks = (u32)strtoul(next, 0, 10);
            }
        }
        if (ticks == 0u) {
            ticks = 1u;
        }
        while (ticks--) {
            (void)dom_shell_simulate_tick(shell, log, emit_text);
        }
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "survey") == 0) {
        return dom_shell_run_local_process(shell,
                                           DOM_LOCAL_PROCESS_SURVEY,
                                           0, 0, 0, 0, 0, 0,
                                           0, 0,
                                           log, status, status_cap, emit_text);
    }
    if (strcmp(token, "collect") == 0) {
        int has_amount = 0;
        int has_min_support = 0;
        int has_max_surface = 0;
        i32 amount_q16 = 0;
        i32 min_support_q16 = 0;
        i32 max_surface_q16 = 0;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "amount") == 0) {
                if (!dom_shell_parse_q16(eq + 1, &amount_q16)) {
                    return D_APP_EXIT_USAGE;
                }
                has_amount = 1;
            } else if (strcmp(next, "min_support") == 0) {
                if (!dom_shell_parse_q16(eq + 1, &min_support_q16)) {
                    return D_APP_EXIT_USAGE;
                }
                has_min_support = 1;
            } else if (strcmp(next, "max_gradient") == 0) {
                if (!dom_shell_parse_q16(eq + 1, &max_surface_q16)) {
                    return D_APP_EXIT_USAGE;
                }
                has_max_surface = 1;
            }
        }
        if (!has_amount) {
            amount_q16 = DOM_SHELL_RESOURCE_AMOUNT_Q16;
        }
        if (!has_min_support) {
            min_support_q16 = DOM_SHELL_SUPPORT_MIN_Q16;
        }
        if (!has_max_surface) {
            max_surface_q16 = DOM_SHELL_SURFACE_MAX_Q16;
        }
        return dom_shell_run_local_process(shell,
                                           DOM_LOCAL_PROCESS_COLLECT,
                                           1, amount_q16,
                                           0, 0,
                                           1, min_support_q16,
                                           1, max_surface_q16,
                                           log, status, status_cap, emit_text);
    }
    if (strcmp(token, "assemble") == 0) {
        int has_min_support = 0;
        int has_max_surface = 0;
        i32 min_support_q16 = 0;
        i32 max_surface_q16 = 0;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "min_support") == 0) {
                if (!dom_shell_parse_q16(eq + 1, &min_support_q16)) {
                    return D_APP_EXIT_USAGE;
                }
                has_min_support = 1;
            } else if (strcmp(next, "max_gradient") == 0) {
                if (!dom_shell_parse_q16(eq + 1, &max_surface_q16)) {
                    return D_APP_EXIT_USAGE;
                }
                has_max_surface = 1;
            }
        }
        if (!has_min_support) {
            min_support_q16 = DOM_SHELL_SUPPORT_MIN_Q16;
        }
        if (!has_max_surface) {
            max_surface_q16 = DOM_SHELL_SURFACE_MAX_Q16;
        }
        return dom_shell_run_local_process(shell,
                                           DOM_LOCAL_PROCESS_ASSEMBLE,
                                           0, 0,
                                           0, 0,
                                           1, min_support_q16,
                                           1, max_surface_q16,
                                           log, status, status_cap, emit_text);
    }
    if (strcmp(token, "connect") == 0) {
        int has_energy = 0;
        i32 energy_q16 = 0;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "energy") == 0) {
                if (!dom_shell_parse_q16(eq + 1, &energy_q16)) {
                    return D_APP_EXIT_USAGE;
                }
                has_energy = 1;
            }
        }
        if (!has_energy) {
            energy_q16 = DOM_SHELL_ENERGY_LOAD_Q16;
        }
        return dom_shell_run_local_process(shell,
                                           DOM_LOCAL_PROCESS_CONNECT_ENERGY,
                                           0, 0,
                                           1, energy_q16,
                                           0, 0,
                                           0, 0,
                                           log, status, status_cap, emit_text);
    }
    if (strcmp(token, "inspect") == 0) {
        return dom_shell_run_local_process(shell,
                                           DOM_LOCAL_PROCESS_INSPECT,
                                           0, 0,
                                           0, 0,
                                           0, 0,
                                           0, 0,
                                           log, status, status_cap, emit_text);
    }
    if (strcmp(token, "repair") == 0) {
        int has_amount = 0;
        i32 amount_q16 = 0;
        while ((next = strtok(0, " \t")) != 0) {
            char* eq = strchr(next, '=');
            if (!eq) {
                continue;
            }
            *eq = '\0';
            if (strcmp(next, "amount") == 0) {
                if (!dom_shell_parse_q16(eq + 1, &amount_q16)) {
                    return D_APP_EXIT_USAGE;
                }
                has_amount = 1;
            }
        }
        if (!has_amount) {
            amount_q16 = DOM_SHELL_RESOURCE_AMOUNT_Q16;
        }
        return dom_shell_run_local_process(shell,
                                           DOM_LOCAL_PROCESS_REPAIR,
                                           1, amount_q16,
                                           0, 0,
                                           0, 0,
                                           0, 0,
                                           log, status, status_cap, emit_text);
    }
    if (strcmp(token, "save") == 0) {
        const char* path = 0;
        if ((next = strtok(0, " \t")) != 0) {
            if (strncmp(next, "path=", 5) == 0) {
                path = next + 5;
            } else {
                path = next;
            }
        }
        return dom_client_shell_save_world(shell, path, log, status, status_cap, emit_text);
    }
    if (strcmp(token, "load") == 0 || strcmp(token, "load-save") == 0 || strcmp(token, "load-world") == 0) {
        const char* path = 0;
        if ((next = strtok(0, " \t")) != 0) {
            if (strncmp(next, "path=", 5) == 0) {
                path = next + 5;
            } else {
                path = next;
            }
        }
        return dom_client_shell_load_world(shell, path, log, status, status_cap, emit_text);
    }
    if (strcmp(token, "inspect-replay") == 0 || strcmp(token, "replay") == 0) {
        const char* path = 0;
        if ((next = strtok(0, " \t")) != 0) {
            if (strncmp(next, "path=", 5) == 0) {
                path = next + 5;
            } else {
                path = next;
            }
        }
        return dom_client_shell_inspect_replay(shell, path, log, status, status_cap, emit_text);
    }
    if (strcmp(token, "mode") == 0) {
        const char* mode_id = strtok(0, " \t");
        if (!mode_id) {
            return D_APP_EXIT_USAGE;
        }
        return dom_client_shell_set_mode(shell, mode_id, log, status, status_cap, emit_text);
    }
    if (strcmp(token, "where") == 0 || strcmp(token, "status") == 0) {
        dom_shell_print_world(shell, emit_text);
        dom_shell_set_status(shell, "world_status=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "exit") == 0 || strcmp(token, "quit") == 0) {
        dom_shell_set_status(shell, "exit=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", shell->last_status);
        }
        dom_shell_emit(shell, log, "client.exit", "result=ok");
        return D_APP_EXIT_OK;
    }
    return D_APP_EXIT_USAGE;
}

void dom_client_shell_event_lines(const dom_shell_event_ring* ring,
                                  char* lines,
                                  size_t line_cap,
                                  size_t line_stride,
                                  int* out_count)
{
    uint32_t i;
    uint32_t idx;
    int count = 0;
    if (out_count) {
        *out_count = 0;
    }
    if (!ring || !lines || line_cap == 0u || line_stride == 0u) {
        return;
    }
    idx = ring->head;
    for (i = 0u; i < ring->count && count < (int)line_cap; ++i) {
        strncpy(lines + (line_stride * count),
                ring->lines[idx],
                line_stride - 1u);
        lines[(line_stride * count) + (line_stride - 1u)] = '\0';
        idx = (idx + 1u) % DOM_SHELL_MAX_EVENTS;
        count += 1;
    }
    if (out_count) {
        *out_count = count;
    }
}
