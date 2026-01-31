/*
FILE: tools/history/history_cli.cpp
MODULE: Dominium
PURPOSE: History and civilization fixture CLI for deterministic history checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/rng_model.h"
#include "domino/world/history_fields.h"

#define HISTORY_FIXTURE_HEADER "DOMINIUM_HISTORY_FIXTURE_V1"

#define HISTORY_VALIDATE_HEADER "DOMINIUM_HISTORY_VALIDATE_V1"
#define HISTORY_INSPECT_HEADER "DOMINIUM_HISTORY_INSPECT_V1"
#define HISTORY_RESOLVE_HEADER "DOMINIUM_HISTORY_RESOLVE_V1"
#define HISTORY_COLLAPSE_HEADER "DOMINIUM_HISTORY_COLLAPSE_V1"

#define HISTORY_PROVIDER_CHAIN "sources->events->epochs->nodes->edges->graphs"

#define HISTORY_LINE_MAX 512u

typedef struct history_fixture {
    char fixture_id[96];
    dom_history_surface_desc history_desc;
    dom_domain_policy policy;
    u32 policy_set;
    char source_names[DOM_HISTORY_MAX_SOURCES][64];
    char event_names[DOM_HISTORY_MAX_EVENTS][64];
    char epoch_names[DOM_HISTORY_MAX_EPOCHS][64];
    char node_names[DOM_HISTORY_MAX_NODES][64];
    char edge_names[DOM_HISTORY_MAX_EDGES][64];
    char graph_names[DOM_HISTORY_MAX_GRAPHS][64];
    char region_names[DOM_HISTORY_MAX_REGIONS][64];
    u32 region_ids[DOM_HISTORY_MAX_REGIONS];
    u32 region_count;
} history_fixture;

static u64 history_hash_u64(u64 h, u64 v)
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

static u64 history_hash_u32(u64 h, u32 v)
{
    return history_hash_u64(h, (u64)v);
}

static u64 history_hash_q16(u64 h, q16_16 v)
{
    return history_hash_u64(h, (u64)(u32)v);
}

static u64 history_hash_q48(u64 h, q48_16 v)
{
    return history_hash_u64(h, (u64)v);
}

static char* history_trim(char* text)
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

static int history_parse_u32(const char* text, u32* out_value)
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

static int history_parse_u64(const char* text, u64* out_value)
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

static int history_parse_q16(const char* text, q16_16* out_value)
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

static int history_parse_q48(const char* text, q48_16* out_value)
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

static int history_parse_indexed_key(const char* key,
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

static u32 history_role_from_text(const char* text)
{
    if (!text) {
        return DOM_HISTORY_ROLE_UNSET;
    }
    if (strcmp(text, "derived") == 0) return DOM_HISTORY_ROLE_DERIVED;
    if (strcmp(text, "process") == 0) return DOM_HISTORY_ROLE_PROCESS;
    return DOM_HISTORY_ROLE_UNSET;
}

static u32 history_category_from_text(const char* text)
{
    if (!text) {
        return DOM_HISTORY_EVENT_UNSET;
    }
    if (strcmp(text, "war") == 0) return DOM_HISTORY_EVENT_WAR;
    if (strcmp(text, "disaster") == 0) return DOM_HISTORY_EVENT_DISASTER;
    if (strcmp(text, "reform") == 0) return DOM_HISTORY_EVENT_REFORM;
    if (strcmp(text, "discovery") == 0) return DOM_HISTORY_EVENT_DISCOVERY;
    return DOM_HISTORY_EVENT_UNSET;
}

static u32 history_process_from_text(const char* text)
{
    if (!text) {
        return DOM_HISTORY_PROCESS_UNSET;
    }
    if (strcmp(text, "record") == 0) return DOM_HISTORY_PROCESS_RECORD;
    if (strcmp(text, "forget") == 0) return DOM_HISTORY_PROCESS_FORGET;
    if (strcmp(text, "revise") == 0) return DOM_HISTORY_PROCESS_REVISE;
    if (strcmp(text, "mythologize") == 0) return DOM_HISTORY_PROCESS_MYTHOLOGIZE;
    return DOM_HISTORY_PROCESS_UNSET;
}

static u32 history_source_type_from_text(const char* text)
{
    if (!text) {
        return DOM_HISTORY_SOURCE_UNSET;
    }
    if (strcmp(text, "replay") == 0) return DOM_HISTORY_SOURCE_REPLAY;
    if (strcmp(text, "archive") == 0) return DOM_HISTORY_SOURCE_ARCHIVE;
    if (strcmp(text, "oral") == 0) return DOM_HISTORY_SOURCE_ORAL;
    if (strcmp(text, "artifact") == 0) return DOM_HISTORY_SOURCE_ARTIFACT;
    if (strcmp(text, "inference") == 0) return DOM_HISTORY_SOURCE_INFERENCE;
    return DOM_HISTORY_SOURCE_UNSET;
}

static u32 history_epoch_type_from_text(const char* text)
{
    if (!text) {
        return DOM_HISTORY_EPOCH_UNSET;
    }
    if (strcmp(text, "conflict") == 0) return DOM_HISTORY_EPOCH_CONFLICT;
    if (strcmp(text, "tech") == 0) return DOM_HISTORY_EPOCH_TECH;
    if (strcmp(text, "institution") == 0) return DOM_HISTORY_EPOCH_INSTITUTION;
    if (strcmp(text, "environment") == 0) return DOM_HISTORY_EPOCH_ENVIRONMENT;
    return DOM_HISTORY_EPOCH_UNSET;
}

static u32 history_edge_type_from_text(const char* text)
{
    if (!text) {
        return DOM_CIV_EDGE_UNSET;
    }
    if (strcmp(text, "cooperation") == 0) return DOM_CIV_EDGE_COOPERATION;
    if (strcmp(text, "dependency") == 0) return DOM_CIV_EDGE_DEPENDENCY;
    if (strcmp(text, "conflict") == 0) return DOM_CIV_EDGE_CONFLICT;
    if (strcmp(text, "cultural") == 0) return DOM_CIV_EDGE_CULTURAL;
    return DOM_CIV_EDGE_UNSET;
}

static void history_fixture_init(history_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_history_surface_desc_init(&fixture->history_desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->policy_set = 0u;
    fixture->region_count = 0u;
    strncpy(fixture->fixture_id, "history.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
}

static void history_fixture_register_region(history_fixture* fixture, const char* name, u32 id)
{
    if (!fixture || !name || !*name || id == 0u) {
        return;
    }
    for (u32 i = 0u; i < fixture->region_count; ++i) {
        if (fixture->region_ids[i] == id) {
            return;
        }
    }
    if (fixture->region_count >= DOM_HISTORY_MAX_REGIONS) {
        return;
    }
    fixture->region_ids[fixture->region_count] = id;
    strncpy(fixture->region_names[fixture->region_count], name,
            sizeof(fixture->region_names[fixture->region_count]) - 1);
    fixture->region_names[fixture->region_count][sizeof(fixture->region_names[fixture->region_count]) - 1] = '\0';
    fixture->region_count += 1u;
}

static int history_fixture_apply_source(history_fixture* fixture,
                                        u32 index,
                                        const char* suffix,
                                        const char* value)
{
    dom_history_source_desc* source;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_HISTORY_MAX_SOURCES) {
        return 0;
    }
    if (fixture->history_desc.source_count <= index) {
        fixture->history_desc.source_count = index + 1u;
    }
    source = &fixture->history_desc.sources[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->source_names[index], value, sizeof(fixture->source_names[index]) - 1);
        fixture->source_names[index][sizeof(fixture->source_names[index]) - 1] = '\0';
        source->source_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "type") == 0) {
        source->source_type = history_source_type_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "event") == 0) {
        source->source_event_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "perspective") == 0) {
        source->perspective_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "confidence") == 0) {
        return history_parse_q16(value, &source->confidence);
    }
    if (strcmp(suffix, "bias") == 0) {
        return history_parse_q16(value, &source->bias);
    }
    if (strcmp(suffix, "tick") == 0) {
        return history_parse_u64(value, &source->recorded_tick);
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        source->region_id = region_id;
        history_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        source->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return history_parse_u32(value, &source->flags);
    }
    return 0;
}

static int history_fixture_apply_event(history_fixture* fixture,
                                       u32 index,
                                       const char* suffix,
                                       const char* value)
{
    dom_history_event_desc* event;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_HISTORY_MAX_EVENTS) {
        return 0;
    }
    if (fixture->history_desc.event_count <= index) {
        fixture->history_desc.event_count = index + 1u;
    }
    event = &fixture->history_desc.events[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->event_names[index], value, sizeof(fixture->event_names[index]) - 1);
        fixture->event_names[index][sizeof(fixture->event_names[index]) - 1] = '\0';
        event->event_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "role") == 0) {
        event->event_role = history_role_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "category") == 0) {
        event->category = history_category_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "process") == 0) {
        event->process_type = history_process_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "target") == 0) {
        event->target_event_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "start") == 0) {
        return history_parse_u64(value, &event->start_tick);
    }
    if (strcmp(suffix, "end") == 0) {
        return history_parse_u64(value, &event->end_tick);
    }
    if (strcmp(suffix, "source_count") == 0) {
        return history_parse_u32(value, &event->source_count);
    }
    if (strncmp(suffix, "source_", 7) == 0) {
        u32 source_index = 0u;
        if (history_parse_u32(suffix + 7, &source_index) &&
            source_index < DOM_HISTORY_MAX_SOURCE_REFS) {
            event->source_refs[source_index] = d_rng_hash_str32(value);
            if (event->source_count <= source_index) {
                event->source_count = source_index + 1u;
            }
            return 1;
        }
    }
    if (strcmp(suffix, "perspective") == 0) {
        event->perspective_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "confidence") == 0) {
        return history_parse_q16(value, &event->confidence);
    }
    if (strcmp(suffix, "uncertainty") == 0) {
        return history_parse_q16(value, &event->uncertainty);
    }
    if (strcmp(suffix, "bias") == 0) {
        return history_parse_q16(value, &event->bias);
    }
    if (strcmp(suffix, "decay") == 0) {
        return history_parse_q16(value, &event->decay_rate);
    }
    if (strcmp(suffix, "delta_confidence") == 0) {
        return history_parse_q16(value, &event->delta_confidence);
    }
    if (strcmp(suffix, "delta_uncertainty") == 0) {
        return history_parse_q16(value, &event->delta_uncertainty);
    }
    if (strcmp(suffix, "delta_bias") == 0) {
        return history_parse_q16(value, &event->delta_bias);
    }
    if (strcmp(suffix, "myth_weight") == 0) {
        return history_parse_q16(value, &event->myth_weight);
    }
    if (strcmp(suffix, "epoch") == 0) {
        event->epoch_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        event->region_id = region_id;
        history_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        event->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return history_parse_u32(value, &event->flags);
    }
    return 0;
}

static int history_fixture_apply_epoch(history_fixture* fixture,
                                       u32 index,
                                       const char* suffix,
                                       const char* value)
{
    dom_history_epoch_desc* epoch;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_HISTORY_MAX_EPOCHS) {
        return 0;
    }
    if (fixture->history_desc.epoch_count <= index) {
        fixture->history_desc.epoch_count = index + 1u;
    }
    epoch = &fixture->history_desc.epochs[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->epoch_names[index], value, sizeof(fixture->epoch_names[index]) - 1);
        fixture->epoch_names[index][sizeof(fixture->epoch_names[index]) - 1] = '\0';
        epoch->epoch_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "type") == 0) {
        epoch->epoch_type = history_epoch_type_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "start") == 0) {
        return history_parse_u64(value, &epoch->start_tick);
    }
    if (strcmp(suffix, "end") == 0) {
        return history_parse_u64(value, &epoch->end_tick);
    }
    if (strcmp(suffix, "confidence") == 0) {
        return history_parse_q16(value, &epoch->confidence);
    }
    if (strcmp(suffix, "uncertainty") == 0) {
        return history_parse_q16(value, &epoch->uncertainty);
    }
    if (strcmp(suffix, "bias") == 0) {
        return history_parse_q16(value, &epoch->bias);
    }
    if (strcmp(suffix, "perspective") == 0) {
        epoch->perspective_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        epoch->region_id = region_id;
        history_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        epoch->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return history_parse_u32(value, &epoch->flags);
    }
    return 0;
}

static int history_fixture_apply_node(history_fixture* fixture,
                                      u32 index,
                                      const char* suffix,
                                      const char* value)
{
    dom_civilization_node_desc* node;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_HISTORY_MAX_NODES) {
        return 0;
    }
    if (fixture->history_desc.node_count <= index) {
        fixture->history_desc.node_count = index + 1u;
    }
    node = &fixture->history_desc.nodes[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->node_names[index], value, sizeof(fixture->node_names[index]) - 1);
        fixture->node_names[index][sizeof(fixture->node_names[index]) - 1] = '\0';
        node->node_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "institution") == 0) {
        node->institution_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        node->region_id = region_id;
        history_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return history_parse_u32(value, &node->flags);
    }
    return 0;
}

static int history_fixture_apply_edge(history_fixture* fixture,
                                      u32 index,
                                      const char* suffix,
                                      const char* value)
{
    dom_civilization_edge_desc* edge;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_HISTORY_MAX_EDGES) {
        return 0;
    }
    if (fixture->history_desc.edge_count <= index) {
        fixture->history_desc.edge_count = index + 1u;
    }
    edge = &fixture->history_desc.edges[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->edge_names[index], value, sizeof(fixture->edge_names[index]) - 1);
        fixture->edge_names[index][sizeof(fixture->edge_names[index]) - 1] = '\0';
        edge->edge_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "from") == 0) {
        edge->from_node_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "to") == 0) {
        edge->to_node_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "type") == 0) {
        edge->edge_type = history_edge_type_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "trust") == 0) {
        return history_parse_q16(value, &edge->trust_weight);
    }
    if (strcmp(suffix, "trade") == 0) {
        return history_parse_q48(value, &edge->trade_volume);
    }
    if (strcmp(suffix, "standards") == 0) {
        return history_parse_q16(value, &edge->standard_weight);
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        edge->region_id = region_id;
        history_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return history_parse_u32(value, &edge->flags);
    }
    return 0;
}

static int history_fixture_apply_graph(history_fixture* fixture,
                                       u32 index,
                                       const char* suffix,
                                       const char* value)
{
    dom_civilization_graph_desc* graph;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_HISTORY_MAX_GRAPHS) {
        return 0;
    }
    if (fixture->history_desc.graph_count <= index) {
        fixture->history_desc.graph_count = index + 1u;
    }
    graph = &fixture->history_desc.graphs[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->graph_names[index], value, sizeof(fixture->graph_names[index]) - 1);
        fixture->graph_names[index][sizeof(fixture->graph_names[index]) - 1] = '\0';
        graph->graph_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "epoch") == 0) {
        graph->epoch_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "node_count") == 0) {
        return history_parse_u32(value, &graph->node_count);
    }
    if (strncmp(suffix, "node_", 5) == 0) {
        u32 node_index = 0u;
        if (history_parse_u32(suffix + 5, &node_index) &&
            node_index < DOM_HISTORY_MAX_NODE_REFS) {
            graph->node_refs[node_index] = d_rng_hash_str32(value);
            if (graph->node_count <= node_index) {
                graph->node_count = node_index + 1u;
            }
            return 1;
        }
    }
    if (strcmp(suffix, "edge_count") == 0) {
        return history_parse_u32(value, &graph->edge_count);
    }
    if (strncmp(suffix, "edge_", 5) == 0) {
        u32 edge_index = 0u;
        if (history_parse_u32(suffix + 5, &edge_index) &&
            edge_index < DOM_HISTORY_MAX_EDGE_REFS) {
            graph->edge_refs[edge_index] = d_rng_hash_str32(value);
            if (graph->edge_count <= edge_index) {
                graph->edge_count = edge_index + 1u;
            }
            return 1;
        }
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        graph->region_id = region_id;
        history_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        graph->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return history_parse_u32(value, &graph->flags);
    }
    return 0;
}

static int history_fixture_apply(history_fixture* fixture, const char* key, const char* value)
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
        return history_parse_u64(value, &fixture->history_desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return history_parse_u64(value, &fixture->history_desc.domain_id);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return history_parse_q16(value, &fixture->history_desc.meters_per_unit);
    }
    if (strcmp(key, "source_count") == 0) {
        return history_parse_u32(value, &fixture->history_desc.source_count);
    }
    if (strcmp(key, "event_count") == 0) {
        return history_parse_u32(value, &fixture->history_desc.event_count);
    }
    if (strcmp(key, "epoch_count") == 0) {
        return history_parse_u32(value, &fixture->history_desc.epoch_count);
    }
    if (strcmp(key, "graph_count") == 0) {
        return history_parse_u32(value, &fixture->history_desc.graph_count);
    }
    if (strcmp(key, "node_count") == 0) {
        return history_parse_u32(value, &fixture->history_desc.node_count);
    }
    if (strcmp(key, "edge_count") == 0) {
        return history_parse_u32(value, &fixture->history_desc.edge_count);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return history_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return history_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return history_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return history_parse_u32(value, &fixture->policy.cost_analytic);
    }

    if (history_parse_indexed_key(key, "source_", &index, &suffix)) {
        return history_fixture_apply_source(fixture, index, suffix, value);
    }
    if (history_parse_indexed_key(key, "event_", &index, &suffix)) {
        return history_fixture_apply_event(fixture, index, suffix, value);
    }
    if (history_parse_indexed_key(key, "epoch_", &index, &suffix)) {
        return history_fixture_apply_epoch(fixture, index, suffix, value);
    }
    if (history_parse_indexed_key(key, "node_", &index, &suffix)) {
        return history_fixture_apply_node(fixture, index, suffix, value);
    }
    if (history_parse_indexed_key(key, "edge_", &index, &suffix)) {
        return history_fixture_apply_edge(fixture, index, suffix, value);
    }
    if (history_parse_indexed_key(key, "graph_", &index, &suffix)) {
        return history_fixture_apply_graph(fixture, index, suffix, value);
    }
    return 0;
}

static int history_fixture_load(const char* path, history_fixture* out_fixture)
{
    FILE* file;
    char line[HISTORY_LINE_MAX];
    int header_ok = 0;
    history_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    history_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = history_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, HISTORY_FIXTURE_HEADER) != 0) {
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
        history_fixture_apply(&fixture, history_trim(text), history_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static const char* history_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && (i + 1) < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 history_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* text = history_find_arg(argc, argv, key);
    u32 value = 0u;
    if (!text || !history_parse_u32(text, &value)) {
        return fallback;
    }
    return value;
}

static u64 history_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* text = history_find_arg(argc, argv, key);
    u64 value = 0u;
    if (!text || !history_parse_u64(text, &value)) {
        return fallback;
    }
    return value;
}

static const char* history_lookup_source_name(const history_fixture* fixture, u32 id)
{
    if (!fixture) {
        return "";
    }
    for (u32 i = 0u; i < fixture->history_desc.source_count; ++i) {
        if (fixture->history_desc.sources[i].source_id == id) {
            return fixture->source_names[i];
        }
    }
    return "";
}

static const char* history_lookup_event_name(const history_fixture* fixture, u32 id)
{
    if (!fixture) {
        return "";
    }
    for (u32 i = 0u; i < fixture->history_desc.event_count; ++i) {
        if (fixture->history_desc.events[i].event_id == id) {
            return fixture->event_names[i];
        }
    }
    return "";
}

static const char* history_lookup_epoch_name(const history_fixture* fixture, u32 id)
{
    if (!fixture) {
        return "";
    }
    for (u32 i = 0u; i < fixture->history_desc.epoch_count; ++i) {
        if (fixture->history_desc.epochs[i].epoch_id == id) {
            return fixture->epoch_names[i];
        }
    }
    return "";
}

static const char* history_lookup_node_name(const history_fixture* fixture, u32 id)
{
    if (!fixture) {
        return "";
    }
    for (u32 i = 0u; i < fixture->history_desc.node_count; ++i) {
        if (fixture->history_desc.nodes[i].node_id == id) {
            return fixture->node_names[i];
        }
    }
    return "";
}

static const char* history_lookup_edge_name(const history_fixture* fixture, u32 id)
{
    if (!fixture) {
        return "";
    }
    for (u32 i = 0u; i < fixture->history_desc.edge_count; ++i) {
        if (fixture->history_desc.edges[i].edge_id == id) {
            return fixture->edge_names[i];
        }
    }
    return "";
}

static const char* history_lookup_graph_name(const history_fixture* fixture, u32 id)
{
    if (!fixture) {
        return "";
    }
    for (u32 i = 0u; i < fixture->history_desc.graph_count; ++i) {
        if (fixture->history_desc.graphs[i].graph_id == id) {
            return fixture->graph_names[i];
        }
    }
    return "";
}

static u32 history_find_region_id(const history_fixture* fixture, const char* name)
{
    if (!name || !*name) {
        return 0u;
    }
    if (fixture) {
        for (u32 i = 0u; i < fixture->region_count; ++i) {
            if (strcmp(fixture->region_names[i], name) == 0) {
                return fixture->region_ids[i];
            }
        }
    }
    return d_rng_hash_str32(name);
}

static int history_fixture_has_source(const history_fixture* fixture, u32 source_id)
{
    if (!fixture || source_id == 0u) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->history_desc.source_count; ++i) {
        if (fixture->history_desc.sources[i].source_id == source_id) {
            return 1;
        }
    }
    return 0;
}

static int history_fixture_has_event(const history_fixture* fixture, u32 event_id)
{
    if (!fixture || event_id == 0u) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->history_desc.event_count; ++i) {
        if (fixture->history_desc.events[i].event_id == event_id) {
            return 1;
        }
    }
    return 0;
}

static int history_fixture_has_node(const history_fixture* fixture, u32 node_id)
{
    if (!fixture || node_id == 0u) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->history_desc.node_count; ++i) {
        if (fixture->history_desc.nodes[i].node_id == node_id) {
            return 1;
        }
    }
    return 0;
}

static int history_fixture_has_edge(const history_fixture* fixture, u32 edge_id)
{
    if (!fixture || edge_id == 0u) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->history_desc.edge_count; ++i) {
        if (fixture->history_desc.edges[i].edge_id == edge_id) {
            return 1;
        }
    }
    return 0;
}

static int history_run_validate(const history_fixture* fixture)
{
    int ok = 1;
    if (!fixture) {
        return 1;
    }

    for (u32 i = 0u; i < fixture->history_desc.source_count; ++i) {
        const dom_history_source_desc* src = &fixture->history_desc.sources[i];
        if (src->source_id == 0u || src->source_event_id == 0u) {
            ok = 0;
        }
    }

    for (u32 i = 0u; i < fixture->history_desc.event_count; ++i) {
        const dom_history_event_desc* event = &fixture->history_desc.events[i];
        if (event->event_id == 0u || event->event_role == DOM_HISTORY_ROLE_UNSET) {
            ok = 0;
            continue;
        }
        if (event->event_role == DOM_HISTORY_ROLE_PROCESS) {
            if (event->process_type == DOM_HISTORY_PROCESS_UNSET || event->target_event_id == 0u) {
                ok = 0;
            }
            if (!history_fixture_has_event(fixture, event->target_event_id)) {
                ok = 0;
            }
        }
        if (event->category == DOM_HISTORY_EVENT_UNSET) {
            ok = 0;
        }
        if (event->source_count == 0u) {
            ok = 0;
        }
        for (u32 s = 0u; s < event->source_count && s < DOM_HISTORY_MAX_SOURCE_REFS; ++s) {
            if (!history_fixture_has_source(fixture, event->source_refs[s])) {
                ok = 0;
            }
        }
    }

    for (u32 i = 0u; i < fixture->history_desc.epoch_count; ++i) {
        const dom_history_epoch_desc* epoch = &fixture->history_desc.epochs[i];
        if (epoch->epoch_id == 0u) {
            ok = 0;
        }
        if (epoch->end_tick < epoch->start_tick) {
            ok = 0;
        }
    }

    for (u32 i = 0u; i < fixture->history_desc.edge_count; ++i) {
        const dom_civilization_edge_desc* edge = &fixture->history_desc.edges[i];
        if (!history_fixture_has_node(fixture, edge->from_node_id) ||
            !history_fixture_has_node(fixture, edge->to_node_id)) {
            ok = 0;
        }
    }

    for (u32 i = 0u; i < fixture->history_desc.graph_count; ++i) {
        const dom_civilization_graph_desc* graph = &fixture->history_desc.graphs[i];
        for (u32 n = 0u; n < graph->node_count && n < DOM_HISTORY_MAX_NODE_REFS; ++n) {
            if (!history_fixture_has_node(fixture, graph->node_refs[n])) {
                ok = 0;
            }
        }
        for (u32 e = 0u; e < graph->edge_count && e < DOM_HISTORY_MAX_EDGE_REFS; ++e) {
            if (!history_fixture_has_edge(fixture, graph->edge_refs[e])) {
                ok = 0;
            }
        }
    }

    printf("%s\n", HISTORY_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HISTORY_PROVIDER_CHAIN);
    printf("source_count=%u\n", (unsigned int)fixture->history_desc.source_count);
    printf("event_count=%u\n", (unsigned int)fixture->history_desc.event_count);
    printf("epoch_count=%u\n", (unsigned int)fixture->history_desc.epoch_count);
    printf("graph_count=%u\n", (unsigned int)fixture->history_desc.graph_count);
    printf("node_count=%u\n", (unsigned int)fixture->history_desc.node_count);
    printf("edge_count=%u\n", (unsigned int)fixture->history_desc.edge_count);
    printf("ok=%u\n", ok ? 1u : 0u);

    return ok ? 0 : 1;
}

static int history_run_inspect_source(const history_fixture* fixture,
                                      const char* source_name,
                                      u32 budget_max)
{
    dom_history_domain domain;
    dom_domain_budget budget;
    dom_history_source_sample sample;
    u32 source_id;
    if (!source_name) {
        return 1;
    }
    source_id = d_rng_hash_str32(source_name);
    dom_history_domain_init(&domain, &fixture->history_desc);
    if (fixture->policy_set) {
        dom_history_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_history_source_query(&domain, source_id, &budget, &sample);

    printf("%s\n", HISTORY_INSPECT_HEADER);
    printf("entity=source\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HISTORY_PROVIDER_CHAIN);
    printf("source_id=%u\n", (unsigned int)sample.source_id);
    printf("source_id_str=%s\n", history_lookup_source_name(fixture, sample.source_id));
    printf("source_type=%u\n", (unsigned int)sample.source_type);
    printf("source_event_id=%u\n", (unsigned int)sample.source_event_id);
    printf("perspective_ref_id=%u\n", (unsigned int)sample.perspective_ref_id);
    printf("confidence_q16=%d\n", (int)sample.confidence);
    printf("bias_q16=%d\n", (int)sample.bias);
    printf("recorded_tick=%llu\n", (unsigned long long)sample.recorded_tick);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_history_domain_free(&domain);
    return 0;
}

static int history_run_inspect_event(const history_fixture* fixture,
                                     const char* event_name,
                                     u32 budget_max)
{
    dom_history_domain domain;
    dom_domain_budget budget;
    dom_history_event_sample sample;
    u32 event_id;
    if (!event_name) {
        return 1;
    }
    event_id = d_rng_hash_str32(event_name);
    dom_history_domain_init(&domain, &fixture->history_desc);
    if (fixture->policy_set) {
        dom_history_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_history_event_query(&domain, event_id, &budget, &sample);

    printf("%s\n", HISTORY_INSPECT_HEADER);
    printf("entity=event\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HISTORY_PROVIDER_CHAIN);
    printf("event_id=%u\n", (unsigned int)sample.event_id);
    printf("event_id_str=%s\n", history_lookup_event_name(fixture, sample.event_id));
    printf("event_role=%u\n", (unsigned int)sample.event_role);
    printf("category=%u\n", (unsigned int)sample.category);
    printf("process_type=%u\n", (unsigned int)sample.process_type);
    printf("target_event_id=%u\n", (unsigned int)sample.target_event_id);
    printf("start_tick=%llu\n", (unsigned long long)sample.start_tick);
    printf("end_tick=%llu\n", (unsigned long long)sample.end_tick);
    printf("source_count=%u\n", (unsigned int)sample.source_count);
    printf("perspective_ref_id=%u\n", (unsigned int)sample.perspective_ref_id);
    printf("confidence_q16=%d\n", (int)sample.confidence);
    printf("uncertainty_q16=%d\n", (int)sample.uncertainty);
    printf("bias_q16=%d\n", (int)sample.bias);
    printf("decay_rate_q16=%d\n", (int)sample.decay_rate);
    printf("delta_confidence_q16=%d\n", (int)sample.delta_confidence);
    printf("delta_uncertainty_q16=%d\n", (int)sample.delta_uncertainty);
    printf("delta_bias_q16=%d\n", (int)sample.delta_bias);
    printf("myth_weight_q16=%d\n", (int)sample.myth_weight);
    printf("epoch_ref_id=%u\n", (unsigned int)sample.epoch_ref_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_history_domain_free(&domain);
    return 0;
}

static int history_run_inspect_epoch(const history_fixture* fixture,
                                     const char* epoch_name,
                                     u32 budget_max)
{
    dom_history_domain domain;
    dom_domain_budget budget;
    dom_history_epoch_sample sample;
    u32 epoch_id;
    if (!epoch_name) {
        return 1;
    }
    epoch_id = d_rng_hash_str32(epoch_name);
    dom_history_domain_init(&domain, &fixture->history_desc);
    if (fixture->policy_set) {
        dom_history_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_history_epoch_query(&domain, epoch_id, &budget, &sample);

    printf("%s\n", HISTORY_INSPECT_HEADER);
    printf("entity=epoch\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HISTORY_PROVIDER_CHAIN);
    printf("epoch_id=%u\n", (unsigned int)sample.epoch_id);
    printf("epoch_id_str=%s\n", history_lookup_epoch_name(fixture, sample.epoch_id));
    printf("epoch_type=%u\n", (unsigned int)sample.epoch_type);
    printf("start_tick=%llu\n", (unsigned long long)sample.start_tick);
    printf("end_tick=%llu\n", (unsigned long long)sample.end_tick);
    printf("confidence_q16=%d\n", (int)sample.confidence);
    printf("uncertainty_q16=%d\n", (int)sample.uncertainty);
    printf("bias_q16=%d\n", (int)sample.bias);
    printf("perspective_ref_id=%u\n", (unsigned int)sample.perspective_ref_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_history_domain_free(&domain);
    return 0;
}

static int history_run_inspect_graph(const history_fixture* fixture,
                                     const char* graph_name,
                                     u32 budget_max)
{
    dom_history_domain domain;
    dom_domain_budget budget;
    dom_civilization_graph_sample sample;
    u32 graph_id;
    if (!graph_name) {
        return 1;
    }
    graph_id = d_rng_hash_str32(graph_name);
    dom_history_domain_init(&domain, &fixture->history_desc);
    if (fixture->policy_set) {
        dom_history_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_civilization_graph_query(&domain, graph_id, &budget, &sample);

    printf("%s\n", HISTORY_INSPECT_HEADER);
    printf("entity=graph\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HISTORY_PROVIDER_CHAIN);
    printf("graph_id=%u\n", (unsigned int)sample.graph_id);
    printf("graph_id_str=%s\n", history_lookup_graph_name(fixture, sample.graph_id));
    printf("epoch_ref_id=%u\n", (unsigned int)sample.epoch_ref_id);
    printf("node_count=%u\n", (unsigned int)sample.node_count);
    printf("edge_count=%u\n", (unsigned int)sample.edge_count);
    printf("trust_weight_avg_q16=%d\n", (int)sample.trust_weight_avg);
    printf("trade_volume_total_q48=%lld\n", (long long)sample.trade_volume_total);
    printf("standard_weight_avg_q16=%d\n", (int)sample.standard_weight_avg);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_history_domain_free(&domain);
    return 0;
}

static int history_run_inspect_node(const history_fixture* fixture,
                                    const char* node_name,
                                    u32 budget_max)
{
    dom_history_domain domain;
    dom_domain_budget budget;
    dom_civilization_node_sample sample;
    u32 node_id;
    if (!node_name) {
        return 1;
    }
    node_id = d_rng_hash_str32(node_name);
    dom_history_domain_init(&domain, &fixture->history_desc);
    if (fixture->policy_set) {
        dom_history_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_civilization_node_query(&domain, node_id, &budget, &sample);

    printf("%s\n", HISTORY_INSPECT_HEADER);
    printf("entity=node\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HISTORY_PROVIDER_CHAIN);
    printf("node_id=%u\n", (unsigned int)sample.node_id);
    printf("node_id_str=%s\n", history_lookup_node_name(fixture, sample.node_id));
    printf("institution_ref_id=%u\n", (unsigned int)sample.institution_ref_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_history_domain_free(&domain);
    return 0;
}

static int history_run_inspect_edge(const history_fixture* fixture,
                                    const char* edge_name,
                                    u32 budget_max)
{
    dom_history_domain domain;
    dom_domain_budget budget;
    dom_civilization_edge_sample sample;
    u32 edge_id;
    if (!edge_name) {
        return 1;
    }
    edge_id = d_rng_hash_str32(edge_name);
    dom_history_domain_init(&domain, &fixture->history_desc);
    if (fixture->policy_set) {
        dom_history_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_civilization_edge_query(&domain, edge_id, &budget, &sample);

    printf("%s\n", HISTORY_INSPECT_HEADER);
    printf("entity=edge\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HISTORY_PROVIDER_CHAIN);
    printf("edge_id=%u\n", (unsigned int)sample.edge_id);
    printf("edge_id_str=%s\n", history_lookup_edge_name(fixture, sample.edge_id));
    printf("from_node_id=%u\n", (unsigned int)sample.from_node_id);
    printf("to_node_id=%u\n", (unsigned int)sample.to_node_id);
    printf("edge_type=%u\n", (unsigned int)sample.edge_type);
    printf("trust_weight_q16=%d\n", (int)sample.trust_weight);
    printf("trade_volume_q48=%lld\n", (long long)sample.trade_volume);
    printf("standard_weight_q16=%d\n", (int)sample.standard_weight);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_history_domain_free(&domain);
    return 0;
}

static int history_run_inspect_region(const history_fixture* fixture,
                                      const char* region_name,
                                      u32 budget_max)
{
    dom_history_domain domain;
    dom_domain_budget budget;
    dom_history_region_sample sample;
    u32 region_id = history_find_region_id(fixture, region_name);

    dom_history_domain_init(&domain, &fixture->history_desc);
    if (fixture->policy_set) {
        dom_history_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_history_region_query(&domain, region_id, &budget, &sample);

    printf("%s\n", HISTORY_INSPECT_HEADER);
    printf("entity=region\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HISTORY_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("source_count=%u\n", (unsigned int)sample.source_count);
    printf("event_count=%u\n", (unsigned int)sample.event_count);
    printf("process_count=%u\n", (unsigned int)sample.process_count);
    printf("epoch_count=%u\n", (unsigned int)sample.epoch_count);
    printf("graph_count=%u\n", (unsigned int)sample.graph_count);
    printf("node_count=%u\n", (unsigned int)sample.node_count);
    printf("edge_count=%u\n", (unsigned int)sample.edge_count);
    printf("confidence_avg_q16=%d\n", (int)sample.confidence_avg);
    printf("uncertainty_avg_q16=%d\n", (int)sample.uncertainty_avg);
    printf("bias_avg_q16=%d\n", (int)sample.bias_avg);
    printf("trust_weight_avg_q16=%d\n", (int)sample.trust_weight_avg);
    printf("trade_volume_total_q48=%lld\n", (long long)sample.trade_volume_total);
    printf("standard_weight_avg_q16=%d\n", (int)sample.standard_weight_avg);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_history_domain_free(&domain);
    return 0;
}

static int history_run_resolve(const history_fixture* fixture,
                               const char* region_name,
                               u64 tick,
                               u64 tick_delta,
                               u32 budget_max,
                               u32 inactive_count)
{
    dom_history_domain domain;
    dom_history_domain* inactive = 0;
    dom_domain_budget budget;
    dom_history_resolve_result result;
    u32 region_id = history_find_region_id(fixture, region_name);
    u64 hash = 14695981039346656037ULL;

    dom_history_domain_init(&domain, &fixture->history_desc);
    if (fixture->policy_set) {
        dom_history_domain_set_policy(&domain, &fixture->policy);
    }

    if (inactive_count > 0u) {
        inactive = (dom_history_domain*)malloc(sizeof(dom_history_domain) * inactive_count);
        if (inactive) {
            for (u32 i = 0u; i < inactive_count; ++i) {
                history_fixture temp = *fixture;
                temp.history_desc.domain_id = fixture->history_desc.domain_id + (u64)(i + 1u);
                dom_history_domain_init(&inactive[i], &temp.history_desc);
                dom_history_domain_set_state(&inactive[i],
                                             DOM_DOMAIN_EXISTENCE_DECLARED,
                                             DOM_DOMAIN_ARCHIVAL_LIVE);
            }
        }
    }

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_history_resolve(&domain, region_id, tick, tick_delta, &budget, &result);

    for (u32 i = 0u; i < domain.source_count; ++i) {
        hash = history_hash_u32(hash, domain.sources[i].source_id);
        hash = history_hash_u32(hash, domain.sources[i].source_type);
        hash = history_hash_q16(hash, domain.sources[i].confidence);
        hash = history_hash_q16(hash, domain.sources[i].bias);
    }
    for (u32 i = 0u; i < domain.event_count; ++i) {
        hash = history_hash_u32(hash, domain.events[i].event_id);
        hash = history_hash_u32(hash, domain.events[i].flags);
        hash = history_hash_q16(hash, domain.events[i].confidence);
        hash = history_hash_q16(hash, domain.events[i].uncertainty);
        hash = history_hash_q16(hash, domain.events[i].bias);
    }
    for (u32 i = 0u; i < domain.epoch_count; ++i) {
        hash = history_hash_u32(hash, domain.epochs[i].epoch_id);
        hash = history_hash_q16(hash, domain.epochs[i].confidence);
        hash = history_hash_q16(hash, domain.epochs[i].uncertainty);
    }
    for (u32 i = 0u; i < domain.edge_count; ++i) {
        hash = history_hash_u32(hash, domain.edges[i].edge_id);
        hash = history_hash_q16(hash, domain.edges[i].trust_weight);
        hash = history_hash_q48(hash, domain.edges[i].trade_volume);
        hash = history_hash_q16(hash, domain.edges[i].standard_weight);
    }
    for (u32 i = 0u; i < domain.graph_count; ++i) {
        hash = history_hash_u32(hash, domain.graphs[i].graph_id);
        hash = history_hash_q16(hash, domain.graphs[i].trust_weight_avg);
        hash = history_hash_q48(hash, domain.graphs[i].trade_volume_total);
        hash = history_hash_q16(hash, domain.graphs[i].standard_weight_avg);
    }

    printf("%s\n", HISTORY_RESOLVE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HISTORY_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("source_count=%u\n", (unsigned int)result.source_count);
    printf("event_count=%u\n", (unsigned int)result.event_count);
    printf("process_count=%u\n", (unsigned int)result.process_count);
    printf("event_applied_count=%u\n", (unsigned int)result.event_applied_count);
    printf("epoch_count=%u\n", (unsigned int)result.epoch_count);
    printf("graph_count=%u\n", (unsigned int)result.graph_count);
    printf("node_count=%u\n", (unsigned int)result.node_count);
    printf("edge_count=%u\n", (unsigned int)result.edge_count);
    printf("confidence_avg_q16=%d\n", (int)result.confidence_avg);
    printf("uncertainty_avg_q16=%d\n", (int)result.uncertainty_avg);
    printf("bias_avg_q16=%d\n", (int)result.bias_avg);
    printf("trust_weight_avg_q16=%d\n", (int)result.trust_weight_avg);
    printf("trade_volume_total_q48=%lld\n", (long long)result.trade_volume_total);
    printf("standard_weight_avg_q16=%d\n", (int)result.standard_weight_avg);
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);
    printf("resolve_hash=%llu\n", (unsigned long long)hash);

    dom_history_domain_free(&domain);
    if (inactive) {
        for (u32 i = 0u; i < inactive_count; ++i) {
            dom_history_domain_free(&inactive[i]);
        }
        free(inactive);
    }
    return 0;
}

static int history_run_collapse(const history_fixture* fixture, const char* region_name)
{
    dom_history_domain domain;
    u32 region_id = history_find_region_id(fixture, region_name);
    u32 count_before;
    u32 count_after;

    dom_history_domain_init(&domain, &fixture->history_desc);
    if (fixture->policy_set) {
        dom_history_domain_set_policy(&domain, &fixture->policy);
    }
    count_before = dom_history_domain_capsule_count(&domain);
    (void)dom_history_domain_collapse_region(&domain, region_id);
    count_after = dom_history_domain_capsule_count(&domain);

    printf("%s\n", HISTORY_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HISTORY_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);

    dom_history_domain_free(&domain);
    return 0;
}

static void history_usage(void)
{
    printf("dom_tool_history commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --source <id> [--budget N]\n");
    printf("  inspect --fixture <path> --event <id> [--budget N]\n");
    printf("  inspect --fixture <path> --epoch <id> [--budget N]\n");
    printf("  inspect --fixture <path> --graph <id> [--budget N]\n");
    printf("  inspect --fixture <path> --node <id> [--budget N]\n");
    printf("  inspect --fixture <path> --edge <id> [--budget N]\n");
    printf("  inspect --fixture <path> --region <id> [--budget N]\n");
    printf("  resolve --fixture <path> --region <id> [--tick N] [--delta N] [--budget N] [--inactive N]\n");
    printf("  collapse --fixture <path> --region <id>\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        history_usage();
        return 2;
    }
    cmd = argv[1];
    if (strcmp(cmd, "validate") == 0 ||
        strcmp(cmd, "inspect") == 0 ||
        strcmp(cmd, "resolve") == 0 ||
        strcmp(cmd, "collapse") == 0) {
        const char* fixture_path = history_find_arg(argc, argv, "--fixture");
        history_fixture fixture;
        if (!fixture_path || !history_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "history: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return history_run_validate(&fixture);
        }
        if (strcmp(cmd, "inspect") == 0) {
            const char* source_name = history_find_arg(argc, argv, "--source");
            const char* event_name = history_find_arg(argc, argv, "--event");
            const char* epoch_name = history_find_arg(argc, argv, "--epoch");
            const char* graph_name = history_find_arg(argc, argv, "--graph");
            const char* node_name = history_find_arg(argc, argv, "--node");
            const char* edge_name = history_find_arg(argc, argv, "--edge");
            const char* region_name = history_find_arg(argc, argv, "--region");
            u32 budget_max = history_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_full);
            if (source_name) {
                return history_run_inspect_source(&fixture, source_name, budget_max);
            }
            if (event_name) {
                return history_run_inspect_event(&fixture, event_name, budget_max);
            }
            if (epoch_name) {
                return history_run_inspect_epoch(&fixture, epoch_name, budget_max);
            }
            if (graph_name) {
                return history_run_inspect_graph(&fixture, graph_name, budget_max);
            }
            if (node_name) {
                return history_run_inspect_node(&fixture, node_name, budget_max);
            }
            if (edge_name) {
                return history_run_inspect_edge(&fixture, edge_name, budget_max);
            }
            if (region_name) {
                return history_run_inspect_region(&fixture, region_name, budget_max);
            }
            fprintf(stderr, "history: inspect requires --source, --event, --epoch, --graph, --node, --edge, or --region\n");
            return 2;
        }
        if (strcmp(cmd, "resolve") == 0) {
            const char* region_name = history_find_arg(argc, argv, "--region");
            u64 tick = history_find_arg_u64(argc, argv, "--tick", 0u);
            u64 delta = history_find_arg_u64(argc, argv, "--delta", 1u);
            u32 budget_max = history_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_medium);
            u32 inactive = history_find_arg_u32(argc, argv, "--inactive", 0u);
            if (!region_name) {
                fprintf(stderr, "history: resolve requires --region\n");
                return 2;
            }
            return history_run_resolve(&fixture, region_name, tick, delta, budget_max, inactive);
        }
        if (strcmp(cmd, "collapse") == 0) {
            const char* region_name = history_find_arg(argc, argv, "--region");
            if (!region_name) {
                fprintf(stderr, "history: collapse requires --region\n");
                return 2;
            }
            return history_run_collapse(&fixture, region_name);
        }
    }

    history_usage();
    return 2;
}
