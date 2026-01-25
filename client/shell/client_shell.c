/*
Client shell core implementation.
*/
#include "client_shell.h"

#include "domino/app/runtime.h"

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdarg.h>
#include <ctype.h>


#define DOM_REFUSAL_INVALID "WD-REFUSAL-INVALID"
#define DOM_REFUSAL_SCHEMA "WD-REFUSAL-SCHEMA"
#define DOM_REFUSAL_TEMPLATE "WD-REFUSAL-TEMPLATE"

#define DOM_SHELL_DEFAULT_SAVE_PATH "data/saves/world.save"

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
    char buf[512];
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
    int in_events = 0;
    int have_summary = 0;
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
        if (strcmp(line, "events_begin") == 0) {
            in_events = 1;
            continue;
        }
        if (strcmp(line, "events_end") == 0) {
            in_events = 0;
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
        if (in_events) {
            dom_shell_event_ring_add(&shell->events, "replay.event", line);
            continue;
        }
    }
    fclose(f);
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
    if (!shell || !shell->world.active) {
        return 0;
    }
    if (!dom_shell_mode_allows_move(shell->world.active_mode, &adjusted_dz)) {
        return 0;
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
    strncpy(buf, cmdline, sizeof(buf) - 1u);
    buf[sizeof(buf) - 1u] = '\0';
    token = strtok(buf, " \t");
    if (!token) {
        return D_APP_EXIT_USAGE;
    }
    if (strcmp(token, "help") == 0) {
        if (emit_text) {
            printf("commands: templates new-world load save inspect-replay mode where exit\n");
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
