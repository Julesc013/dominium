/*
FILE: tools/standard/standard_cli.cpp
MODULE: Dominium
PURPOSE: Standards and toolchain fixture CLI for deterministic checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/rng_model.h"
#include "domino/world/standard_fields.h"

#define STANDARD_FIXTURE_HEADER "DOMINIUM_STANDARD_FIXTURE_V1"

#define STANDARD_VALIDATE_HEADER "DOMINIUM_STANDARD_VALIDATE_V1"
#define STANDARD_INSPECT_HEADER "DOMINIUM_STANDARD_INSPECT_V1"
#define STANDARD_RESOLVE_HEADER "DOMINIUM_STANDARD_RESOLVE_V1"
#define STANDARD_COLLAPSE_HEADER "DOMINIUM_STANDARD_COLLAPSE_V1"

#define STANDARD_PROVIDER_CHAIN "definitions->versions->scopes->events->tools->edges->graphs"

#define STANDARD_LINE_MAX 512u

typedef struct standard_fixture {
    char fixture_id[96];
    dom_standard_surface_desc standard_desc;
    dom_domain_policy policy;
    u32 policy_set;
    char definition_names[DOM_STANDARD_MAX_DEFINITIONS][64];
    char version_names[DOM_STANDARD_MAX_VERSIONS][64];
    char scope_names[DOM_STANDARD_MAX_SCOPES][64];
    char event_names[DOM_STANDARD_MAX_EVENTS][64];
    char tool_names[DOM_STANDARD_MAX_TOOLS][64];
    char edge_names[DOM_STANDARD_MAX_EDGES][64];
    char graph_names[DOM_STANDARD_MAX_GRAPHS][64];
    char region_names[DOM_STANDARD_MAX_REGIONS][64];
    u32 region_ids[DOM_STANDARD_MAX_REGIONS];
    u32 region_count;
} standard_fixture;

static u64 standard_hash_u64(u64 h, u64 v)
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

static u64 standard_hash_u32(u64 h, u32 v)
{
    return standard_hash_u64(h, (u64)v);
}

static u64 standard_hash_q16(u64 h, q16_16 v)
{
    return standard_hash_u64(h, (u64)(u32)v);
}

static u64 standard_hash_q48(u64 h, q48_16 v)
{
    return standard_hash_u64(h, (u64)v);
}

static char* standard_trim(char* text)
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

static int standard_parse_u32(const char* text, u32* out_value)
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

static int standard_parse_u64(const char* text, u64* out_value)
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

static int standard_parse_q16(const char* text, q16_16* out_value)
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

static int standard_parse_q48(const char* text, q48_16* out_value)
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

static int standard_parse_indexed_key(const char* key,
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

static u32 standard_process_from_text(const char* text)
{
    if (!text) {
        return DOM_STANDARD_PROCESS_UNSET;
    }
    if (strcmp(text, "propose") == 0) return DOM_STANDARD_PROCESS_PROPOSE;
    if (strcmp(text, "adopt") == 0) return DOM_STANDARD_PROCESS_ADOPT;
    if (strcmp(text, "audit") == 0) return DOM_STANDARD_PROCESS_AUDIT;
    if (strcmp(text, "enforce") == 0) return DOM_STANDARD_PROCESS_ENFORCE;
    if (strcmp(text, "revoke") == 0) return DOM_STANDARD_PROCESS_REVOKE;
    return DOM_STANDARD_PROCESS_UNSET;
}

static u32 standard_status_from_text(const char* text)
{
    if (!text) {
        return DOM_STANDARD_STATUS_UNSET;
    }
    if (strcmp(text, "active") == 0) return DOM_STANDARD_STATUS_ACTIVE;
    if (strcmp(text, "deprecated") == 0) return DOM_STANDARD_STATUS_DEPRECATED;
    if (strcmp(text, "revoked") == 0) return DOM_STANDARD_STATUS_REVOKED;
    return DOM_STANDARD_STATUS_UNSET;
}

static void standard_fixture_init(standard_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_standard_surface_desc_init(&fixture->standard_desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->policy_set = 0u;
    fixture->region_count = 0u;
    strncpy(fixture->fixture_id, "standard.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
}

static void standard_fixture_register_region(standard_fixture* fixture, const char* name, u32 id)
{
    if (!fixture || !name || !*name || id == 0u) {
        return;
    }
    for (u32 i = 0u; i < fixture->region_count; ++i) {
        if (fixture->region_ids[i] == id) {
            return;
        }
    }
    if (fixture->region_count >= DOM_STANDARD_MAX_REGIONS) {
        return;
    }
    fixture->region_ids[fixture->region_count] = id;
    strncpy(fixture->region_names[fixture->region_count], name,
            sizeof(fixture->region_names[fixture->region_count]) - 1);
    fixture->region_names[fixture->region_count][sizeof(fixture->region_names[fixture->region_count]) - 1] = '\0';
    fixture->region_count += 1u;
}

static int standard_fixture_apply_definition(standard_fixture* fixture,
                                             u32 index,
                                             const char* suffix,
                                             const char* value)
{
    dom_standard_definition_desc* def;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_STANDARD_MAX_DEFINITIONS) {
        return 0;
    }
    if (fixture->standard_desc.definition_count <= index) {
        fixture->standard_desc.definition_count = index + 1u;
    }
    def = &fixture->standard_desc.definitions[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->definition_names[index], value, sizeof(fixture->definition_names[index]) - 1);
        fixture->definition_names[index][sizeof(fixture->definition_names[index]) - 1] = '\0';
        def->standard_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "subject") == 0) {
        def->subject_domain_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "specification") == 0) {
        def->specification_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "version") == 0) {
        def->current_version_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "policy") == 0) {
        def->compatibility_policy_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "institution") == 0) {
        def->issuing_institution_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "adoption_count") == 0) {
        return standard_parse_u32(value, &def->adoption_req_count);
    }
    if (strncmp(suffix, "adoption_", 9) == 0) {
        u32 req_index = 0u;
        if (standard_parse_u32(suffix + 9, &req_index) &&
            req_index < DOM_STANDARD_MAX_ADOPTION_REQS) {
            def->adoption_req_ids[req_index] = d_rng_hash_str32(value);
            if (def->adoption_req_count <= req_index) {
                def->adoption_req_count = req_index + 1u;
            }
            return 1;
        }
    }
    if (strcmp(suffix, "enforcement_count") == 0) {
        return standard_parse_u32(value, &def->enforcement_count);
    }
    if (strncmp(suffix, "enforcement_", 12) == 0) {
        u32 enforce_index = 0u;
        if (standard_parse_u32(suffix + 12, &enforce_index) &&
            enforce_index < DOM_STANDARD_MAX_ENFORCEMENTS) {
            def->enforcement_ids[enforce_index] = d_rng_hash_str32(value);
            if (def->enforcement_count <= enforce_index) {
                def->enforcement_count = enforce_index + 1u;
            }
            return 1;
        }
    }
    if (strcmp(suffix, "provenance") == 0) {
        def->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        def->region_id = region_id;
        standard_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int standard_fixture_apply_version(standard_fixture* fixture,
                                          u32 index,
                                          const char* suffix,
                                          const char* value)
{
    dom_standard_version_desc* version;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_STANDARD_MAX_VERSIONS) {
        return 0;
    }
    if (fixture->standard_desc.version_count <= index) {
        fixture->standard_desc.version_count = index + 1u;
    }
    version = &fixture->standard_desc.versions[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->version_names[index], value, sizeof(fixture->version_names[index]) - 1);
        fixture->version_names[index][sizeof(fixture->version_names[index]) - 1] = '\0';
        version->version_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "standard") == 0) {
        version->standard_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "tag") == 0) {
        version->version_tag_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "compat_group") == 0) {
        version->compatibility_group_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "compat_score") == 0) {
        return standard_parse_q16(value, &version->compatibility_score);
    }
    if (strcmp(suffix, "adoption_threshold") == 0) {
        return standard_parse_q16(value, &version->adoption_threshold);
    }
    if (strcmp(suffix, "status") == 0) {
        version->status = standard_status_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "release_tick") == 0) {
        return standard_parse_u64(value, &version->release_tick);
    }
    if (strcmp(suffix, "provenance") == 0) {
        version->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        version->region_id = region_id;
        standard_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int standard_fixture_apply_scope(standard_fixture* fixture,
                                        u32 index,
                                        const char* suffix,
                                        const char* value)
{
    dom_standard_scope_desc* scope;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_STANDARD_MAX_SCOPES) {
        return 0;
    }
    if (fixture->standard_desc.scope_count <= index) {
        fixture->standard_desc.scope_count = index + 1u;
    }
    scope = &fixture->standard_desc.scopes[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->scope_names[index], value, sizeof(fixture->scope_names[index]) - 1);
        fixture->scope_names[index][sizeof(fixture->scope_names[index]) - 1] = '\0';
        scope->scope_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "standard") == 0) {
        scope->standard_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "version") == 0) {
        scope->version_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "spatial") == 0) {
        scope->spatial_domain_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "subject") == 0) {
        scope->subject_domain_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "adoption") == 0) {
        return standard_parse_q16(value, &scope->adoption_rate);
    }
    if (strcmp(suffix, "compliance") == 0) {
        return standard_parse_q16(value, &scope->compliance_rate);
    }
    if (strcmp(suffix, "lock_in") == 0) {
        return standard_parse_q16(value, &scope->lock_in_index);
    }
    if (strcmp(suffix, "enforcement") == 0) {
        return standard_parse_q16(value, &scope->enforcement_level);
    }
    if (strcmp(suffix, "provenance") == 0) {
        scope->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        scope->region_id = region_id;
        standard_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int standard_fixture_apply_event(standard_fixture* fixture,
                                        u32 index,
                                        const char* suffix,
                                        const char* value)
{
    dom_standard_event_desc* event;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_STANDARD_MAX_EVENTS) {
        return 0;
    }
    if (fixture->standard_desc.event_count <= index) {
        fixture->standard_desc.event_count = index + 1u;
    }
    event = &fixture->standard_desc.events[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->event_names[index], value, sizeof(fixture->event_names[index]) - 1);
        fixture->event_names[index][sizeof(fixture->event_names[index]) - 1] = '\0';
        event->event_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "process") == 0) {
        event->process_type = standard_process_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "standard") == 0) {
        event->standard_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "version") == 0) {
        event->version_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "scope") == 0) {
        event->scope_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "delta_adoption") == 0) {
        return standard_parse_q16(value, &event->delta_adoption);
    }
    if (strcmp(suffix, "delta_compliance") == 0) {
        return standard_parse_q16(value, &event->delta_compliance);
    }
    if (strcmp(suffix, "delta_lock_in") == 0) {
        return standard_parse_q16(value, &event->delta_lock_in);
    }
    if (strcmp(suffix, "tick") == 0) {
        return standard_parse_u64(value, &event->event_tick);
    }
    if (strcmp(suffix, "provenance") == 0) {
        event->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        event->region_id = region_id;
        standard_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int standard_fixture_apply_tool(standard_fixture* fixture,
                                       u32 index,
                                       const char* suffix,
                                       const char* value)
{
    dom_meta_tool_desc* tool;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_STANDARD_MAX_TOOLS) {
        return 0;
    }
    if (fixture->standard_desc.tool_count <= index) {
        fixture->standard_desc.tool_count = index + 1u;
    }
    tool = &fixture->standard_desc.tools[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->tool_names[index], value, sizeof(fixture->tool_names[index]) - 1);
        fixture->tool_names[index][sizeof(fixture->tool_names[index]) - 1] = '\0';
        tool->tool_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "type") == 0) {
        tool->tool_type_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "input") == 0) {
        tool->input_standard_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "output") == 0) {
        tool->output_standard_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "capacity") == 0) {
        return standard_parse_q48(value, &tool->capacity);
    }
    if (strcmp(suffix, "energy") == 0) {
        return standard_parse_q48(value, &tool->energy_cost);
    }
    if (strcmp(suffix, "heat") == 0) {
        return standard_parse_q48(value, &tool->heat_output);
    }
    if (strcmp(suffix, "error_rate") == 0) {
        return standard_parse_q16(value, &tool->error_rate);
    }
    if (strcmp(suffix, "bias") == 0) {
        return standard_parse_q16(value, &tool->bias);
    }
    if (strcmp(suffix, "provenance") == 0) {
        tool->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        tool->region_id = region_id;
        standard_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int standard_fixture_apply_edge(standard_fixture* fixture,
                                       u32 index,
                                       const char* suffix,
                                       const char* value)
{
    dom_toolchain_edge_desc* edge;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_STANDARD_MAX_EDGES) {
        return 0;
    }
    if (fixture->standard_desc.edge_count <= index) {
        fixture->standard_desc.edge_count = index + 1u;
    }
    edge = &fixture->standard_desc.edges[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->edge_names[index], value, sizeof(fixture->edge_names[index]) - 1);
        fixture->edge_names[index][sizeof(fixture->edge_names[index]) - 1] = '\0';
        edge->edge_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "from") == 0) {
        edge->from_tool_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "to") == 0) {
        edge->to_tool_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "input") == 0) {
        edge->input_standard_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "output") == 0) {
        edge->output_standard_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "compat_score") == 0) {
        return standard_parse_q16(value, &edge->compatibility_score);
    }
    if (strcmp(suffix, "bridge") == 0) {
        u32 flag = 0u;
        if (strcmp(value, "1") == 0 || strcmp(value, "true") == 0) {
            flag = DOM_TOOLCHAIN_EDGE_BRIDGE;
        }
        edge->flags |= flag;
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        edge->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        edge->region_id = region_id;
        standard_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int standard_fixture_apply_graph(standard_fixture* fixture,
                                        u32 index,
                                        const char* suffix,
                                        const char* value)
{
    dom_toolchain_graph_desc* graph;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_STANDARD_MAX_GRAPHS) {
        return 0;
    }
    if (fixture->standard_desc.graph_count <= index) {
        fixture->standard_desc.graph_count = index + 1u;
    }
    graph = &fixture->standard_desc.graphs[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->graph_names[index], value, sizeof(fixture->graph_names[index]) - 1);
        fixture->graph_names[index][sizeof(fixture->graph_names[index]) - 1] = '\0';
        graph->graph_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "node_count") == 0) {
        return standard_parse_u32(value, &graph->node_count);
    }
    if (strncmp(suffix, "node_", 5) == 0) {
        u32 node_index = 0u;
        if (standard_parse_u32(suffix + 5, &node_index) &&
            node_index < DOM_STANDARD_MAX_GRAPH_NODES) {
            graph->node_tool_ids[node_index] = d_rng_hash_str32(value);
            if (graph->node_count <= node_index) {
                graph->node_count = node_index + 1u;
            }
            return 1;
        }
    }
    if (strcmp(suffix, "edge_count") == 0) {
        return standard_parse_u32(value, &graph->edge_count);
    }
    if (strncmp(suffix, "edge_", 5) == 0) {
        u32 edge_index = 0u;
        if (standard_parse_u32(suffix + 5, &edge_index) &&
            edge_index < DOM_STANDARD_MAX_GRAPH_EDGES) {
            graph->edge_ids[edge_index] = d_rng_hash_str32(value);
            if (graph->edge_count <= edge_index) {
                graph->edge_count = edge_index + 1u;
            }
            return 1;
        }
    }
    if (strcmp(suffix, "provenance") == 0) {
        graph->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        graph->region_id = region_id;
        standard_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int standard_fixture_apply(standard_fixture* fixture, const char* key, const char* value)
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
        return standard_parse_u64(value, &fixture->standard_desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return standard_parse_u64(value, &fixture->standard_desc.domain_id);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return standard_parse_q16(value, &fixture->standard_desc.meters_per_unit);
    }
    if (strcmp(key, "definition_count") == 0) {
        return standard_parse_u32(value, &fixture->standard_desc.definition_count);
    }
    if (strcmp(key, "version_count") == 0) {
        return standard_parse_u32(value, &fixture->standard_desc.version_count);
    }
    if (strcmp(key, "scope_count") == 0) {
        return standard_parse_u32(value, &fixture->standard_desc.scope_count);
    }
    if (strcmp(key, "event_count") == 0) {
        return standard_parse_u32(value, &fixture->standard_desc.event_count);
    }
    if (strcmp(key, "tool_count") == 0) {
        return standard_parse_u32(value, &fixture->standard_desc.tool_count);
    }
    if (strcmp(key, "edge_count") == 0) {
        return standard_parse_u32(value, &fixture->standard_desc.edge_count);
    }
    if (strcmp(key, "graph_count") == 0) {
        return standard_parse_u32(value, &fixture->standard_desc.graph_count);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return standard_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return standard_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return standard_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return standard_parse_u32(value, &fixture->policy.cost_analytic);
    }

    if (standard_parse_indexed_key(key, "definition_", &index, &suffix)) {
        return standard_fixture_apply_definition(fixture, index, suffix, value);
    }
    if (standard_parse_indexed_key(key, "version_", &index, &suffix)) {
        return standard_fixture_apply_version(fixture, index, suffix, value);
    }
    if (standard_parse_indexed_key(key, "scope_", &index, &suffix)) {
        return standard_fixture_apply_scope(fixture, index, suffix, value);
    }
    if (standard_parse_indexed_key(key, "event_", &index, &suffix)) {
        return standard_fixture_apply_event(fixture, index, suffix, value);
    }
    if (standard_parse_indexed_key(key, "tool_", &index, &suffix)) {
        return standard_fixture_apply_tool(fixture, index, suffix, value);
    }
    if (standard_parse_indexed_key(key, "edge_", &index, &suffix)) {
        return standard_fixture_apply_edge(fixture, index, suffix, value);
    }
    if (standard_parse_indexed_key(key, "graph_", &index, &suffix)) {
        return standard_fixture_apply_graph(fixture, index, suffix, value);
    }
    return 0;
}

static int standard_fixture_load(const char* path, standard_fixture* out_fixture)
{
    FILE* file;
    char line[STANDARD_LINE_MAX];
    int header_ok = 0;
    standard_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    standard_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = standard_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, STANDARD_FIXTURE_HEADER) != 0) {
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
        standard_fixture_apply(&fixture, standard_trim(text), standard_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static const char* standard_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 standard_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = standard_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && standard_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u64 standard_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* value = standard_find_arg(argc, argv, key);
    u64 parsed = fallback;
    if (value && standard_parse_u64(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u32 standard_find_region_id(const standard_fixture* fixture, const char* name)
{
    if (!fixture || !name || !*name) {
        return 0u;
    }
    for (u32 i = 0u; i < fixture->region_count; ++i) {
        if (strcmp(fixture->region_names[i], name) == 0) {
            return fixture->region_ids[i];
        }
    }
    return d_rng_hash_str32(name);
}

static const char* standard_lookup_definition_name(const standard_fixture* fixture, u32 id)
{
    if (!fixture) {
        return "";
    }
    for (u32 i = 0u; i < fixture->standard_desc.definition_count; ++i) {
        if (fixture->standard_desc.definitions[i].standard_id == id) {
            return fixture->definition_names[i];
        }
    }
    return "";
}

static const char* standard_lookup_version_name(const standard_fixture* fixture, u32 id)
{
    if (!fixture) {
        return "";
    }
    for (u32 i = 0u; i < fixture->standard_desc.version_count; ++i) {
        if (fixture->standard_desc.versions[i].version_id == id) {
            return fixture->version_names[i];
        }
    }
    return "";
}

static const char* standard_lookup_scope_name(const standard_fixture* fixture, u32 id)
{
    if (!fixture) {
        return "";
    }
    for (u32 i = 0u; i < fixture->standard_desc.scope_count; ++i) {
        if (fixture->standard_desc.scopes[i].scope_id == id) {
            return fixture->scope_names[i];
        }
    }
    return "";
}

static const char* standard_lookup_event_name(const standard_fixture* fixture, u32 id)
{
    if (!fixture) {
        return "";
    }
    for (u32 i = 0u; i < fixture->standard_desc.event_count; ++i) {
        if (fixture->standard_desc.events[i].event_id == id) {
            return fixture->event_names[i];
        }
    }
    return "";
}

static const char* standard_lookup_tool_name(const standard_fixture* fixture, u32 id)
{
    if (!fixture) {
        return "";
    }
    for (u32 i = 0u; i < fixture->standard_desc.tool_count; ++i) {
        if (fixture->standard_desc.tools[i].tool_id == id) {
            return fixture->tool_names[i];
        }
    }
    return "";
}

static const char* standard_lookup_edge_name(const standard_fixture* fixture, u32 id)
{
    if (!fixture) {
        return "";
    }
    for (u32 i = 0u; i < fixture->standard_desc.edge_count; ++i) {
        if (fixture->standard_desc.edges[i].edge_id == id) {
            return fixture->edge_names[i];
        }
    }
    return "";
}

static const char* standard_lookup_graph_name(const standard_fixture* fixture, u32 id)
{
    if (!fixture) {
        return "";
    }
    for (u32 i = 0u; i < fixture->standard_desc.graph_count; ++i) {
        if (fixture->standard_desc.graphs[i].graph_id == id) {
            return fixture->graph_names[i];
        }
    }
    return "";
}

static d_bool standard_has_definition(const standard_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return D_FALSE;
    }
    for (u32 i = 0u; i < fixture->standard_desc.definition_count; ++i) {
        if (fixture->standard_desc.definitions[i].standard_id == id) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}

static d_bool standard_has_version(const standard_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return D_FALSE;
    }
    for (u32 i = 0u; i < fixture->standard_desc.version_count; ++i) {
        if (fixture->standard_desc.versions[i].version_id == id) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}

static d_bool standard_has_scope(const standard_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return D_FALSE;
    }
    for (u32 i = 0u; i < fixture->standard_desc.scope_count; ++i) {
        if (fixture->standard_desc.scopes[i].scope_id == id) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}

static d_bool standard_has_tool(const standard_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return D_FALSE;
    }
    for (u32 i = 0u; i < fixture->standard_desc.tool_count; ++i) {
        if (fixture->standard_desc.tools[i].tool_id == id) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}

static d_bool standard_has_edge(const standard_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return D_FALSE;
    }
    for (u32 i = 0u; i < fixture->standard_desc.edge_count; ++i) {
        if (fixture->standard_desc.edges[i].edge_id == id) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}

static int standard_run_validate(const standard_fixture* fixture)
{
    int ok = 1;
    if (!fixture) {
        return 1;
    }
    for (u32 i = 0u; i < fixture->standard_desc.definition_count; ++i) {
        const dom_standard_definition_desc* def = &fixture->standard_desc.definitions[i];
        if (def->current_version_id != 0u && !standard_has_version(fixture, def->current_version_id)) {
            fprintf(stderr, "standard: definition missing version %u\n", (unsigned int)def->current_version_id);
            ok = 0;
        }
    }
    for (u32 i = 0u; i < fixture->standard_desc.version_count; ++i) {
        const dom_standard_version_desc* ver = &fixture->standard_desc.versions[i];
        if (ver->standard_id != 0u && !standard_has_definition(fixture, ver->standard_id)) {
            fprintf(stderr, "standard: version missing standard %u\n", (unsigned int)ver->standard_id);
            ok = 0;
        }
    }
    for (u32 i = 0u; i < fixture->standard_desc.scope_count; ++i) {
        const dom_standard_scope_desc* scope = &fixture->standard_desc.scopes[i];
        if (scope->standard_id != 0u && !standard_has_definition(fixture, scope->standard_id)) {
            fprintf(stderr, "standard: scope missing standard %u\n", (unsigned int)scope->standard_id);
            ok = 0;
        }
        if (scope->version_id != 0u && !standard_has_version(fixture, scope->version_id)) {
            fprintf(stderr, "standard: scope missing version %u\n", (unsigned int)scope->version_id);
            ok = 0;
        }
    }
    for (u32 i = 0u; i < fixture->standard_desc.event_count; ++i) {
        const dom_standard_event_desc* event = &fixture->standard_desc.events[i];
        if (event->scope_id != 0u && !standard_has_scope(fixture, event->scope_id)) {
            fprintf(stderr, "standard: event missing scope %u\n", (unsigned int)event->scope_id);
            ok = 0;
        }
        if (event->standard_id != 0u && !standard_has_definition(fixture, event->standard_id)) {
            fprintf(stderr, "standard: event missing standard %u\n", (unsigned int)event->standard_id);
            ok = 0;
        }
        if (event->version_id != 0u && !standard_has_version(fixture, event->version_id)) {
            fprintf(stderr, "standard: event missing version %u\n", (unsigned int)event->version_id);
            ok = 0;
        }
    }
    for (u32 i = 0u; i < fixture->standard_desc.tool_count; ++i) {
        const dom_meta_tool_desc* tool = &fixture->standard_desc.tools[i];
        if (tool->input_standard_id != 0u && !standard_has_definition(fixture, tool->input_standard_id)) {
            fprintf(stderr, "standard: tool input standard missing %u\n", (unsigned int)tool->input_standard_id);
            ok = 0;
        }
        if (tool->output_standard_id != 0u && !standard_has_definition(fixture, tool->output_standard_id)) {
            fprintf(stderr, "standard: tool output standard missing %u\n", (unsigned int)tool->output_standard_id);
            ok = 0;
        }
    }
    for (u32 i = 0u; i < fixture->standard_desc.edge_count; ++i) {
        const dom_toolchain_edge_desc* edge = &fixture->standard_desc.edges[i];
        if (edge->from_tool_id != 0u && !standard_has_tool(fixture, edge->from_tool_id)) {
            fprintf(stderr, "standard: edge missing from tool %u\n", (unsigned int)edge->from_tool_id);
            ok = 0;
        }
        if (edge->to_tool_id != 0u && !standard_has_tool(fixture, edge->to_tool_id)) {
            fprintf(stderr, "standard: edge missing to tool %u\n", (unsigned int)edge->to_tool_id);
            ok = 0;
        }
    }
    for (u32 i = 0u; i < fixture->standard_desc.graph_count; ++i) {
        const dom_toolchain_graph_desc* graph = &fixture->standard_desc.graphs[i];
        for (u32 n = 0u; n < graph->node_count; ++n) {
            if (graph->node_tool_ids[n] != 0u &&
                !standard_has_tool(fixture, graph->node_tool_ids[n])) {
                fprintf(stderr, "standard: graph node missing tool %u\n",
                        (unsigned int)graph->node_tool_ids[n]);
                ok = 0;
            }
        }
        for (u32 e = 0u; e < graph->edge_count; ++e) {
            if (graph->edge_ids[e] != 0u &&
                !standard_has_edge(fixture, graph->edge_ids[e])) {
                fprintf(stderr, "standard: graph edge missing %u\n",
                        (unsigned int)graph->edge_ids[e]);
                ok = 0;
            }
        }
    }

    printf("%s\n", STANDARD_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STANDARD_PROVIDER_CHAIN);
    printf("definition_count=%u\n", (unsigned int)fixture->standard_desc.definition_count);
    printf("version_count=%u\n", (unsigned int)fixture->standard_desc.version_count);
    printf("scope_count=%u\n", (unsigned int)fixture->standard_desc.scope_count);
    printf("event_count=%u\n", (unsigned int)fixture->standard_desc.event_count);
    printf("tool_count=%u\n", (unsigned int)fixture->standard_desc.tool_count);
    printf("edge_count=%u\n", (unsigned int)fixture->standard_desc.edge_count);
    printf("graph_count=%u\n", (unsigned int)fixture->standard_desc.graph_count);
    printf("status=%s\n", ok ? "ok" : "invalid");

    return ok ? 0 : 1;
}

static int standard_run_inspect_definition(const standard_fixture* fixture,
                                           const char* def_name,
                                           u32 budget_max)
{
    dom_standard_domain domain;
    dom_domain_budget budget;
    dom_standard_definition_sample sample;
    u32 def_id;
    if (!def_name) {
        return 1;
    }
    def_id = d_rng_hash_str32(def_name);
    dom_standard_domain_init(&domain, &fixture->standard_desc);
    if (fixture->policy_set) {
        dom_standard_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_standard_definition_query(&domain, def_id, &budget, &sample);

    printf("%s\n", STANDARD_INSPECT_HEADER);
    printf("entity=definition\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STANDARD_PROVIDER_CHAIN);
    printf("standard_id=%u\n", (unsigned int)sample.standard_id);
    printf("standard_id_str=%s\n", standard_lookup_definition_name(fixture, sample.standard_id));
    printf("subject_domain_id=%u\n", (unsigned int)sample.subject_domain_id);
    printf("specification_id=%u\n", (unsigned int)sample.specification_id);
    printf("current_version_id=%u\n", (unsigned int)sample.current_version_id);
    printf("compatibility_policy_id=%u\n", (unsigned int)sample.compatibility_policy_id);
    printf("issuing_institution_id=%u\n", (unsigned int)sample.issuing_institution_id);
    printf("adoption_req_count=%u\n", (unsigned int)sample.adoption_req_count);
    printf("enforcement_count=%u\n", (unsigned int)sample.enforcement_count);
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

    dom_standard_domain_free(&domain);
    return 0;
}

static int standard_run_inspect_version(const standard_fixture* fixture,
                                        const char* version_name,
                                        u32 budget_max)
{
    dom_standard_domain domain;
    dom_domain_budget budget;
    dom_standard_version_sample sample;
    u32 version_id;
    if (!version_name) {
        return 1;
    }
    version_id = d_rng_hash_str32(version_name);
    dom_standard_domain_init(&domain, &fixture->standard_desc);
    if (fixture->policy_set) {
        dom_standard_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_standard_version_query(&domain, version_id, &budget, &sample);

    printf("%s\n", STANDARD_INSPECT_HEADER);
    printf("entity=version\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STANDARD_PROVIDER_CHAIN);
    printf("version_id=%u\n", (unsigned int)sample.version_id);
    printf("version_id_str=%s\n", standard_lookup_version_name(fixture, sample.version_id));
    printf("standard_id=%u\n", (unsigned int)sample.standard_id);
    printf("version_tag_id=%u\n", (unsigned int)sample.version_tag_id);
    printf("compatibility_group_id=%u\n", (unsigned int)sample.compatibility_group_id);
    printf("compatibility_score_q16=%d\n", (int)sample.compatibility_score);
    printf("adoption_threshold_q16=%d\n", (int)sample.adoption_threshold);
    printf("status=%u\n", (unsigned int)sample.status);
    printf("release_tick=%llu\n", (unsigned long long)sample.release_tick);
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

    dom_standard_domain_free(&domain);
    return 0;
}

static int standard_run_inspect_scope(const standard_fixture* fixture,
                                      const char* scope_name,
                                      u32 budget_max)
{
    dom_standard_domain domain;
    dom_domain_budget budget;
    dom_standard_scope_sample sample;
    u32 scope_id;
    if (!scope_name) {
        return 1;
    }
    scope_id = d_rng_hash_str32(scope_name);
    dom_standard_domain_init(&domain, &fixture->standard_desc);
    if (fixture->policy_set) {
        dom_standard_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_standard_scope_query(&domain, scope_id, &budget, &sample);

    printf("%s\n", STANDARD_INSPECT_HEADER);
    printf("entity=scope\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STANDARD_PROVIDER_CHAIN);
    printf("scope_id=%u\n", (unsigned int)sample.scope_id);
    printf("scope_id_str=%s\n", standard_lookup_scope_name(fixture, sample.scope_id));
    printf("standard_id=%u\n", (unsigned int)sample.standard_id);
    printf("version_id=%u\n", (unsigned int)sample.version_id);
    printf("spatial_domain_id=%u\n", (unsigned int)sample.spatial_domain_id);
    printf("subject_domain_id=%u\n", (unsigned int)sample.subject_domain_id);
    printf("adoption_rate_q16=%d\n", (int)sample.adoption_rate);
    printf("compliance_rate_q16=%d\n", (int)sample.compliance_rate);
    printf("lock_in_index_q16=%d\n", (int)sample.lock_in_index);
    printf("enforcement_level_q16=%d\n", (int)sample.enforcement_level);
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

    dom_standard_domain_free(&domain);
    return 0;
}

static int standard_run_inspect_event(const standard_fixture* fixture,
                                      const char* event_name,
                                      u32 budget_max)
{
    dom_standard_domain domain;
    dom_domain_budget budget;
    dom_standard_event_sample sample;
    u32 event_id;
    if (!event_name) {
        return 1;
    }
    event_id = d_rng_hash_str32(event_name);
    dom_standard_domain_init(&domain, &fixture->standard_desc);
    if (fixture->policy_set) {
        dom_standard_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_standard_event_query(&domain, event_id, &budget, &sample);

    printf("%s\n", STANDARD_INSPECT_HEADER);
    printf("entity=event\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STANDARD_PROVIDER_CHAIN);
    printf("event_id=%u\n", (unsigned int)sample.event_id);
    printf("event_id_str=%s\n", standard_lookup_event_name(fixture, sample.event_id));
    printf("process_type=%u\n", (unsigned int)sample.process_type);
    printf("standard_id=%u\n", (unsigned int)sample.standard_id);
    printf("version_id=%u\n", (unsigned int)sample.version_id);
    printf("scope_id=%u\n", (unsigned int)sample.scope_id);
    printf("delta_adoption_q16=%d\n", (int)sample.delta_adoption);
    printf("delta_compliance_q16=%d\n", (int)sample.delta_compliance);
    printf("delta_lock_in_q16=%d\n", (int)sample.delta_lock_in);
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

    dom_standard_domain_free(&domain);
    return 0;
}

static int standard_run_inspect_tool(const standard_fixture* fixture,
                                     const char* tool_name,
                                     u32 budget_max)
{
    dom_standard_domain domain;
    dom_domain_budget budget;
    dom_meta_tool_sample sample;
    u32 tool_id;
    if (!tool_name) {
        return 1;
    }
    tool_id = d_rng_hash_str32(tool_name);
    dom_standard_domain_init(&domain, &fixture->standard_desc);
    if (fixture->policy_set) {
        dom_standard_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_meta_tool_query(&domain, tool_id, &budget, &sample);

    printf("%s\n", STANDARD_INSPECT_HEADER);
    printf("entity=tool\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STANDARD_PROVIDER_CHAIN);
    printf("tool_id=%u\n", (unsigned int)sample.tool_id);
    printf("tool_id_str=%s\n", standard_lookup_tool_name(fixture, sample.tool_id));
    printf("tool_type_id=%u\n", (unsigned int)sample.tool_type_id);
    printf("input_standard_id=%u\n", (unsigned int)sample.input_standard_id);
    printf("output_standard_id=%u\n", (unsigned int)sample.output_standard_id);
    printf("capacity_q48=%lld\n", (long long)sample.capacity);
    printf("energy_cost_q48=%lld\n", (long long)sample.energy_cost);
    printf("heat_output_q48=%lld\n", (long long)sample.heat_output);
    printf("error_rate_q16=%d\n", (int)sample.error_rate);
    printf("bias_q16=%d\n", (int)sample.bias);
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

    dom_standard_domain_free(&domain);
    return 0;
}

static int standard_run_inspect_edge(const standard_fixture* fixture,
                                     const char* edge_name,
                                     u32 budget_max)
{
    dom_standard_domain domain;
    dom_domain_budget budget;
    dom_toolchain_edge_sample sample;
    u32 edge_id;
    if (!edge_name) {
        return 1;
    }
    edge_id = d_rng_hash_str32(edge_name);
    dom_standard_domain_init(&domain, &fixture->standard_desc);
    if (fixture->policy_set) {
        dom_standard_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_toolchain_edge_query(&domain, edge_id, &budget, &sample);

    printf("%s\n", STANDARD_INSPECT_HEADER);
    printf("entity=edge\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STANDARD_PROVIDER_CHAIN);
    printf("edge_id=%u\n", (unsigned int)sample.edge_id);
    printf("edge_id_str=%s\n", standard_lookup_edge_name(fixture, sample.edge_id));
    printf("from_tool_id=%u\n", (unsigned int)sample.from_tool_id);
    printf("to_tool_id=%u\n", (unsigned int)sample.to_tool_id);
    printf("input_standard_id=%u\n", (unsigned int)sample.input_standard_id);
    printf("output_standard_id=%u\n", (unsigned int)sample.output_standard_id);
    printf("compatibility_score_q16=%d\n", (int)sample.compatibility_score);
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

    dom_standard_domain_free(&domain);
    return 0;
}

static int standard_run_inspect_graph(const standard_fixture* fixture,
                                      const char* graph_name,
                                      u32 budget_max)
{
    dom_standard_domain domain;
    dom_domain_budget budget;
    dom_toolchain_graph_sample sample;
    u32 graph_id;
    if (!graph_name) {
        return 1;
    }
    graph_id = d_rng_hash_str32(graph_name);
    dom_standard_domain_init(&domain, &fixture->standard_desc);
    if (fixture->policy_set) {
        dom_standard_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_toolchain_graph_query(&domain, graph_id, &budget, &sample);

    printf("%s\n", STANDARD_INSPECT_HEADER);
    printf("entity=graph\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STANDARD_PROVIDER_CHAIN);
    printf("graph_id=%u\n", (unsigned int)sample.graph_id);
    printf("graph_id_str=%s\n", standard_lookup_graph_name(fixture, sample.graph_id));
    printf("node_count=%u\n", (unsigned int)sample.node_count);
    printf("edge_count=%u\n", (unsigned int)sample.edge_count);
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

    dom_standard_domain_free(&domain);
    return 0;
}

static int standard_run_inspect_region(const standard_fixture* fixture,
                                       const char* region_name,
                                       u32 budget_max)
{
    dom_standard_domain domain;
    dom_domain_budget budget;
    dom_standard_region_sample sample;
    u32 region_id = standard_find_region_id(fixture, region_name);

    dom_standard_domain_init(&domain, &fixture->standard_desc);
    if (fixture->policy_set) {
        dom_standard_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_standard_region_query(&domain, region_id, &budget, &sample);

    printf("%s\n", STANDARD_INSPECT_HEADER);
    printf("entity=region\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STANDARD_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("definition_count=%u\n", (unsigned int)sample.definition_count);
    printf("version_count=%u\n", (unsigned int)sample.version_count);
    printf("scope_count=%u\n", (unsigned int)sample.scope_count);
    printf("event_count=%u\n", (unsigned int)sample.event_count);
    printf("tool_count=%u\n", (unsigned int)sample.tool_count);
    printf("edge_count=%u\n", (unsigned int)sample.edge_count);
    printf("graph_count=%u\n", (unsigned int)sample.graph_count);
    printf("adoption_avg_q16=%d\n", (int)sample.adoption_avg);
    printf("compliance_avg_q16=%d\n", (int)sample.compliance_avg);
    printf("lock_in_avg_q16=%d\n", (int)sample.lock_in_avg);
    printf("compatibility_avg_q16=%d\n", (int)sample.compatibility_avg);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_standard_domain_free(&domain);
    return 0;
}

static int standard_run_resolve(const standard_fixture* fixture,
                                const char* region_name,
                                u64 tick,
                                u64 tick_delta,
                                u32 budget_max,
                                u32 inactive_count)
{
    dom_standard_domain domain;
    dom_standard_domain* inactive = 0;
    dom_domain_budget budget;
    dom_standard_resolve_result result;
    u32 region_id = standard_find_region_id(fixture, region_name);
    u64 hash = 14695981039346656037ULL;

    dom_standard_domain_init(&domain, &fixture->standard_desc);
    if (fixture->policy_set) {
        dom_standard_domain_set_policy(&domain, &fixture->policy);
    }

    if (inactive_count > 0u) {
        inactive = (dom_standard_domain*)malloc(sizeof(dom_standard_domain) * inactive_count);
        if (inactive) {
            for (u32 i = 0u; i < inactive_count; ++i) {
                standard_fixture temp = *fixture;
                temp.standard_desc.domain_id = fixture->standard_desc.domain_id + (u64)(i + 1u);
                dom_standard_domain_init(&inactive[i], &temp.standard_desc);
                dom_standard_domain_set_state(&inactive[i],
                                              DOM_DOMAIN_EXISTENCE_DECLARED,
                                              DOM_DOMAIN_ARCHIVAL_LIVE);
            }
        }
    }

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_standard_resolve(&domain, region_id, tick, tick_delta, &budget, &result);

    for (u32 i = 0u; i < domain.definition_count; ++i) {
        hash = standard_hash_u32(hash, domain.definitions[i].standard_id);
        hash = standard_hash_u32(hash, domain.definitions[i].current_version_id);
    }
    for (u32 i = 0u; i < domain.version_count; ++i) {
        hash = standard_hash_u32(hash, domain.versions[i].version_id);
        hash = standard_hash_u32(hash, domain.versions[i].status);
        hash = standard_hash_q16(hash, domain.versions[i].compatibility_score);
    }
    for (u32 i = 0u; i < domain.scope_count; ++i) {
        hash = standard_hash_u32(hash, domain.scopes[i].scope_id);
        hash = standard_hash_q16(hash, domain.scopes[i].adoption_rate);
        hash = standard_hash_q16(hash, domain.scopes[i].compliance_rate);
        hash = standard_hash_q16(hash, domain.scopes[i].lock_in_index);
    }
    for (u32 i = 0u; i < domain.event_count; ++i) {
        hash = standard_hash_u32(hash, domain.events[i].event_id);
        hash = standard_hash_u32(hash, domain.events[i].flags);
        hash = standard_hash_u32(hash, domain.events[i].process_type);
    }
    for (u32 i = 0u; i < domain.tool_count; ++i) {
        hash = standard_hash_u32(hash, domain.tools[i].tool_id);
        hash = standard_hash_q16(hash, domain.tools[i].error_rate);
        hash = standard_hash_q16(hash, domain.tools[i].bias);
    }
    for (u32 i = 0u; i < domain.edge_count; ++i) {
        hash = standard_hash_u32(hash, domain.edges[i].edge_id);
        hash = standard_hash_q16(hash, domain.edges[i].compatibility_score);
    }
    for (u32 i = 0u; i < domain.graph_count; ++i) {
        hash = standard_hash_u32(hash, domain.graphs[i].graph_id);
        hash = standard_hash_u32(hash, domain.graphs[i].node_count);
        hash = standard_hash_u32(hash, domain.graphs[i].edge_count);
    }

    printf("%s\n", STANDARD_RESOLVE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STANDARD_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("definition_count=%u\n", (unsigned int)result.definition_count);
    printf("version_count=%u\n", (unsigned int)result.version_count);
    printf("scope_count=%u\n", (unsigned int)result.scope_count);
    printf("event_count=%u\n", (unsigned int)result.event_count);
    printf("event_applied_count=%u\n", (unsigned int)result.event_applied_count);
    printf("tool_count=%u\n", (unsigned int)result.tool_count);
    printf("edge_count=%u\n", (unsigned int)result.edge_count);
    printf("graph_count=%u\n", (unsigned int)result.graph_count);
    printf("adoption_avg_q16=%d\n", (int)result.adoption_avg);
    printf("compliance_avg_q16=%d\n", (int)result.compliance_avg);
    printf("lock_in_avg_q16=%d\n", (int)result.lock_in_avg);
    printf("compatibility_avg_q16=%d\n", (int)result.compatibility_avg);
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);
    printf("resolve_hash=%llu\n", (unsigned long long)hash);

    dom_standard_domain_free(&domain);
    if (inactive) {
        for (u32 i = 0u; i < inactive_count; ++i) {
            dom_standard_domain_free(&inactive[i]);
        }
        free(inactive);
    }
    return 0;
}

static int standard_run_collapse(const standard_fixture* fixture, const char* region_name)
{
    dom_standard_domain domain;
    u32 region_id = standard_find_region_id(fixture, region_name);
    u32 count_before;
    u32 count_after;

    dom_standard_domain_init(&domain, &fixture->standard_desc);
    if (fixture->policy_set) {
        dom_standard_domain_set_policy(&domain, &fixture->policy);
    }
    count_before = dom_standard_domain_capsule_count(&domain);
    (void)dom_standard_domain_collapse_region(&domain, region_id);
    count_after = dom_standard_domain_capsule_count(&domain);

    printf("%s\n", STANDARD_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", STANDARD_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);

    dom_standard_domain_free(&domain);
    return 0;
}

static void standard_usage(void)
{
    printf("dom_tool_standard commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --definition <id> [--budget N]\n");
    printf("  inspect --fixture <path> --version <id> [--budget N]\n");
    printf("  inspect --fixture <path> --scope <id> [--budget N]\n");
    printf("  inspect --fixture <path> --event <id> [--budget N]\n");
    printf("  inspect --fixture <path> --tool <id> [--budget N]\n");
    printf("  inspect --fixture <path> --edge <id> [--budget N]\n");
    printf("  inspect --fixture <path> --graph <id> [--budget N]\n");
    printf("  inspect --fixture <path> --region <id> [--budget N]\n");
    printf("  resolve --fixture <path> --region <id> [--tick N] [--delta N] [--budget N] [--inactive N]\n");
    printf("  collapse --fixture <path> --region <id>\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        standard_usage();
        return 2;
    }
    cmd = argv[1];
    if (strcmp(cmd, "validate") == 0 ||
        strcmp(cmd, "inspect") == 0 ||
        strcmp(cmd, "resolve") == 0 ||
        strcmp(cmd, "collapse") == 0) {
        const char* fixture_path = standard_find_arg(argc, argv, "--fixture");
        standard_fixture fixture;
        if (!fixture_path || !standard_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "standard: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return standard_run_validate(&fixture);
        }
        if (strcmp(cmd, "inspect") == 0) {
            const char* def_name = standard_find_arg(argc, argv, "--definition");
            const char* version_name = standard_find_arg(argc, argv, "--version");
            const char* scope_name = standard_find_arg(argc, argv, "--scope");
            const char* event_name = standard_find_arg(argc, argv, "--event");
            const char* tool_name = standard_find_arg(argc, argv, "--tool");
            const char* edge_name = standard_find_arg(argc, argv, "--edge");
            const char* graph_name = standard_find_arg(argc, argv, "--graph");
            const char* region_name = standard_find_arg(argc, argv, "--region");
            u32 budget_max = standard_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_full);
            if (def_name) {
                return standard_run_inspect_definition(&fixture, def_name, budget_max);
            }
            if (version_name) {
                return standard_run_inspect_version(&fixture, version_name, budget_max);
            }
            if (scope_name) {
                return standard_run_inspect_scope(&fixture, scope_name, budget_max);
            }
            if (event_name) {
                return standard_run_inspect_event(&fixture, event_name, budget_max);
            }
            if (tool_name) {
                return standard_run_inspect_tool(&fixture, tool_name, budget_max);
            }
            if (edge_name) {
                return standard_run_inspect_edge(&fixture, edge_name, budget_max);
            }
            if (graph_name) {
                return standard_run_inspect_graph(&fixture, graph_name, budget_max);
            }
            if (region_name) {
                return standard_run_inspect_region(&fixture, region_name, budget_max);
            }
            fprintf(stderr, "standard: inspect requires --definition, --version, --scope, --event, --tool, --edge, --graph, or --region\n");
            return 2;
        }
        if (strcmp(cmd, "resolve") == 0) {
            const char* region_name = standard_find_arg(argc, argv, "--region");
            u64 tick = standard_find_arg_u64(argc, argv, "--tick", 0u);
            u64 delta = standard_find_arg_u64(argc, argv, "--delta", 1u);
            u32 budget_max = standard_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_medium);
            u32 inactive = standard_find_arg_u32(argc, argv, "--inactive", 0u);
            if (!region_name) {
                fprintf(stderr, "standard: resolve requires --region\n");
                return 2;
            }
            return standard_run_resolve(&fixture, region_name, tick, delta, budget_max, inactive);
        }
        if (strcmp(cmd, "collapse") == 0) {
            const char* region_name = standard_find_arg(argc, argv, "--region");
            if (!region_name) {
                fprintf(stderr, "standard: collapse requires --region\n");
                return 2;
            }
            return standard_run_collapse(&fixture, region_name);
        }
    }

    standard_usage();
    return 2;
}
