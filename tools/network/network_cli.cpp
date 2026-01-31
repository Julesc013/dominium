/*
FILE: tools/network/network_cli.cpp
MODULE: Dominium
PURPOSE: Network fixture CLI for deterministic information routing checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"
#include "domino/world/information_fields.h"

#define NETWORK_FIXTURE_HEADER "DOMINIUM_NETWORK_FIXTURE_V1"

#define NETWORK_VALIDATE_HEADER "DOMINIUM_NETWORK_VALIDATE_V1"
#define NETWORK_INSPECT_HEADER "DOMINIUM_NETWORK_INSPECT_V1"
#define NETWORK_RESOLVE_HEADER "DOMINIUM_NETWORK_RESOLVE_V1"
#define NETWORK_COLLAPSE_HEADER "DOMINIUM_NETWORK_COLLAPSE_V1"

#define NETWORK_PROVIDER_CHAIN "nodes->links->data"

#define NETWORK_LINE_MAX 512u

typedef struct network_fixture {
    char fixture_id[96];
    dom_info_surface_desc info_desc;
    dom_domain_policy policy;
    u32 policy_set;
    char node_names[DOM_INFO_MAX_NODES][64];
    char link_names[DOM_INFO_MAX_LINKS][64];
    char data_names[DOM_INFO_MAX_DATA][64];
    char capacity_names[DOM_INFO_MAX_CAPACITY_PROFILES][64];
    char network_names[DOM_INFO_MAX_NETWORKS][64];
    u32 network_ids[DOM_INFO_MAX_NETWORKS];
    u32 network_count;
} network_fixture;

static u64 network_hash_u64(u64 h, u64 v)
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

static u64 network_hash_u32(u64 h, u32 v)
{
    return network_hash_u64(h, (u64)v);
}

static u64 network_hash_q48(u64 h, q48_16 v)
{
    return network_hash_u64(h, (u64)v);
}

static u64 network_hash_q16(u64 h, q16_16 v)
{
    return network_hash_u64(h, (u64)(u32)v);
}

static char* network_trim(char* text)
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

static int network_parse_u32(const char* text, u32* out_value)
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

static int network_parse_u64(const char* text, u64* out_value)
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

static int network_parse_q16(const char* text, q16_16* out_value)
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

static int network_parse_q48(const char* text, q48_16* out_value)
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

static int network_parse_triplet_q16(const char* text, q16_16* a, q16_16* b, q16_16* c)
{
    char buffer[NETWORK_LINE_MAX];
    char* first;
    char* second;
    char* third;
    if (!text || !a || !b || !c) {
        return 0;
    }
    strncpy(buffer, text, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    first = buffer;
    second = strchr(first, ',');
    if (!second) {
        return 0;
    }
    *second++ = '\0';
    third = strchr(second, ',');
    if (!third) {
        return 0;
    }
    *third++ = '\0';
    if (!network_parse_q16(network_trim(first), a)) return 0;
    if (!network_parse_q16(network_trim(second), b)) return 0;
    if (!network_parse_q16(network_trim(third), c)) return 0;
    return 1;
}

static int network_parse_point(const char* text, dom_domain_point* out_point)
{
    q16_16 x;
    q16_16 y;
    q16_16 z;
    if (!text || !out_point) {
        return 0;
    }
    if (!network_parse_triplet_q16(text, &x, &y, &z)) {
        return 0;
    }
    out_point->x = x;
    out_point->y = y;
    out_point->z = z;
    return 1;
}

static int network_parse_indexed_key(const char* key,
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

static u32 network_node_type_from_text(const char* text)
{
    if (!text) {
        return DOM_INFO_NODE_UNSET;
    }
    if (strcmp(text, "router") == 0) return DOM_INFO_NODE_ROUTER;
    if (strcmp(text, "switch") == 0) return DOM_INFO_NODE_SWITCH;
    if (strcmp(text, "antenna") == 0) return DOM_INFO_NODE_ANTENNA;
    if (strcmp(text, "satellite") == 0) return DOM_INFO_NODE_SATELLITE;
    if (strcmp(text, "compute") == 0) return DOM_INFO_NODE_COMPUTE;
    if (strcmp(text, "storage") == 0) return DOM_INFO_NODE_STORAGE;
    if (strcmp(text, "endpoint") == 0) return DOM_INFO_NODE_ENDPOINT;
    return DOM_INFO_NODE_UNSET;
}

static const char* network_node_type_to_text(u32 node_type)
{
    switch (node_type) {
        case DOM_INFO_NODE_ROUTER: return "router";
        case DOM_INFO_NODE_SWITCH: return "switch";
        case DOM_INFO_NODE_ANTENNA: return "antenna";
        case DOM_INFO_NODE_SATELLITE: return "satellite";
        case DOM_INFO_NODE_COMPUTE: return "compute";
        case DOM_INFO_NODE_STORAGE: return "storage";
        case DOM_INFO_NODE_ENDPOINT: return "endpoint";
        default: return "unset";
    }
}

static u32 network_data_type_from_text(const char* text)
{
    if (!text) {
        return DOM_INFO_DATA_UNSET;
    }
    if (strcmp(text, "control") == 0) return DOM_INFO_DATA_CONTROL;
    if (strcmp(text, "telemetry") == 0) return DOM_INFO_DATA_TELEMETRY;
    if (strcmp(text, "message") == 0) return DOM_INFO_DATA_MESSAGE;
    if (strcmp(text, "storage") == 0) return DOM_INFO_DATA_STORAGE;
    return DOM_INFO_DATA_UNSET;
}

static const char* network_data_type_to_text(u32 data_type)
{
    switch (data_type) {
        case DOM_INFO_DATA_CONTROL: return "control";
        case DOM_INFO_DATA_TELEMETRY: return "telemetry";
        case DOM_INFO_DATA_MESSAGE: return "message";
        case DOM_INFO_DATA_STORAGE: return "storage";
        default: return "unset";
    }
}

static u32 network_latency_class_from_text(const char* text)
{
    if (!text) {
        return DOM_INFO_LATENCY_LOCAL;
    }
    if (strcmp(text, "immediate") == 0) return DOM_INFO_LATENCY_IMMEDIATE;
    if (strcmp(text, "local") == 0) return DOM_INFO_LATENCY_LOCAL;
    if (strcmp(text, "regional") == 0) return DOM_INFO_LATENCY_REGIONAL;
    if (strcmp(text, "orbital") == 0) return DOM_INFO_LATENCY_ORBITAL;
    if (strcmp(text, "interplanetary") == 0) return DOM_INFO_LATENCY_INTERPLANETARY;
    return DOM_INFO_LATENCY_LOCAL;
}

static const char* network_latency_class_to_text(u32 latency_class)
{
    switch (latency_class) {
        case DOM_INFO_LATENCY_IMMEDIATE: return "immediate";
        case DOM_INFO_LATENCY_LOCAL: return "local";
        case DOM_INFO_LATENCY_REGIONAL: return "regional";
        case DOM_INFO_LATENCY_ORBITAL: return "orbital";
        case DOM_INFO_LATENCY_INTERPLANETARY: return "interplanetary";
        default: return "local";
    }
}

static u32 network_congestion_policy_from_text(const char* text)
{
    if (!text) {
        return DOM_INFO_CONGESTION_QUEUE;
    }
    if (strcmp(text, "queue") == 0) return DOM_INFO_CONGESTION_QUEUE;
    if (strcmp(text, "drop_newest") == 0) return DOM_INFO_CONGESTION_DROP_NEWEST;
    if (strcmp(text, "drop_oldest") == 0) return DOM_INFO_CONGESTION_DROP_OLDEST;
    if (strcmp(text, "degrade") == 0) return DOM_INFO_CONGESTION_DEGRADE;
    return DOM_INFO_CONGESTION_QUEUE;
}

static const char* network_congestion_policy_to_text(u32 policy)
{
    switch (policy) {
        case DOM_INFO_CONGESTION_QUEUE: return "queue";
        case DOM_INFO_CONGESTION_DROP_NEWEST: return "drop_newest";
        case DOM_INFO_CONGESTION_DROP_OLDEST: return "drop_oldest";
        case DOM_INFO_CONGESTION_DEGRADE: return "degrade";
        default: return "queue";
    }
}

static u32 network_link_direction_from_text(const char* text)
{
    if (!text) {
        return DOM_INFO_LINK_BIDIR;
    }
    if (strcmp(text, "bidir") == 0) return DOM_INFO_LINK_BIDIR;
    if (strcmp(text, "a_to_b") == 0) return DOM_INFO_LINK_A_TO_B;
    if (strcmp(text, "b_to_a") == 0) return DOM_INFO_LINK_B_TO_A;
    return DOM_INFO_LINK_BIDIR;
}

static const char* network_link_direction_to_text(u32 direction)
{
    switch (direction) {
        case DOM_INFO_LINK_A_TO_B: return "a_to_b";
        case DOM_INFO_LINK_B_TO_A: return "b_to_a";
        default: return "bidir";
    }
}

static void network_fixture_init(network_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_info_surface_desc_init(&fixture->info_desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->policy_set = 0u;
    fixture->network_count = 0u;
    strncpy(fixture->fixture_id, "network.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
}

static void network_fixture_register_network(network_fixture* fixture, const char* name, u32 id)
{
    if (!fixture || !name || !*name || id == 0u) {
        return;
    }
    for (u32 i = 0u; i < fixture->network_count; ++i) {
        if (fixture->network_ids[i] == id) {
            return;
        }
    }
    if (fixture->network_count >= DOM_INFO_MAX_NETWORKS) {
        return;
    }
    fixture->network_ids[fixture->network_count] = id;
    strncpy(fixture->network_names[fixture->network_count], name,
            sizeof(fixture->network_names[fixture->network_count]) - 1);
    fixture->network_names[fixture->network_count][sizeof(fixture->network_names[fixture->network_count]) - 1] = '\0';
    fixture->network_count += 1u;
}

static int network_fixture_apply_capacity(network_fixture* fixture,
                                          u32 index,
                                          const char* suffix,
                                          const char* value)
{
    dom_info_capacity_desc* capacity;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_INFO_MAX_CAPACITY_PROFILES) {
        return 0;
    }
    if (fixture->info_desc.capacity_count <= index) {
        fixture->info_desc.capacity_count = index + 1u;
    }
    capacity = &fixture->info_desc.capacities[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->capacity_names[index], value, sizeof(fixture->capacity_names[index]) - 1);
        fixture->capacity_names[index][sizeof(fixture->capacity_names[index]) - 1] = '\0';
        capacity->capacity_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "bandwidth") == 0) {
        return network_parse_q48(value, &capacity->bandwidth_limit);
    }
    if (strcmp(suffix, "latency") == 0) {
        capacity->latency_class = network_latency_class_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "error") == 0) {
        return network_parse_q16(value, &capacity->error_rate);
    }
    if (strcmp(suffix, "congestion") == 0) {
        capacity->congestion_policy = network_congestion_policy_from_text(value);
        return 1;
    }
    return 0;
}

static int network_fixture_apply_node(network_fixture* fixture,
                                      u32 index,
                                      const char* suffix,
                                      const char* value)
{
    dom_info_node_desc* node;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_INFO_MAX_NODES) {
        return 0;
    }
    if (fixture->info_desc.node_count <= index) {
        fixture->info_desc.node_count = index + 1u;
    }
    node = &fixture->info_desc.nodes[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->node_names[index], value, sizeof(fixture->node_names[index]) - 1);
        fixture->node_names[index][sizeof(fixture->node_names[index]) - 1] = '\0';
        node->node_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "type") == 0) {
        node->node_type = network_node_type_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "compute") == 0) {
        return network_parse_q48(value, &node->compute_capacity);
    }
    if (strcmp(suffix, "storage") == 0) {
        return network_parse_q48(value, &node->storage_capacity);
    }
    if (strcmp(suffix, "energy") == 0) {
        return network_parse_q48(value, &node->energy_per_unit);
    }
    if (strcmp(suffix, "heat") == 0) {
        return network_parse_q48(value, &node->heat_per_unit);
    }
    if (strcmp(suffix, "network") == 0) {
        u32 net_id = d_rng_hash_str32(value);
        node->network_id = net_id;
        network_fixture_register_network(fixture, value, net_id);
        return 1;
    }
    if (strcmp(suffix, "pos") == 0) {
        return network_parse_point(value, &node->location);
    }
    return 0;
}

static int network_fixture_apply_link(network_fixture* fixture,
                                      u32 index,
                                      const char* suffix,
                                      const char* value)
{
    dom_info_link_desc* link;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_INFO_MAX_LINKS) {
        return 0;
    }
    if (fixture->info_desc.link_count <= index) {
        fixture->info_desc.link_count = index + 1u;
    }
    link = &fixture->info_desc.links[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->link_names[index], value, sizeof(fixture->link_names[index]) - 1);
        fixture->link_names[index][sizeof(fixture->link_names[index]) - 1] = '\0';
        link->link_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "network") == 0) {
        u32 net_id = d_rng_hash_str32(value);
        link->network_id = net_id;
        network_fixture_register_network(fixture, value, net_id);
        return 1;
    }
    if (strcmp(suffix, "a") == 0) {
        link->node_a_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "b") == 0) {
        link->node_b_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "capacity") == 0) {
        link->capacity_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "direction") == 0) {
        link->direction = network_link_direction_from_text(value);
        return 1;
    }
    return 0;
}

static int network_fixture_apply_data(network_fixture* fixture,
                                      u32 index,
                                      const char* suffix,
                                      const char* value)
{
    dom_info_data_desc* data;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_INFO_MAX_DATA) {
        return 0;
    }
    if (fixture->info_desc.data_count <= index) {
        fixture->info_desc.data_count = index + 1u;
    }
    data = &fixture->info_desc.data[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->data_names[index], value, sizeof(fixture->data_names[index]) - 1);
        fixture->data_names[index][sizeof(fixture->data_names[index]) - 1] = '\0';
        data->data_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "type") == 0) {
        data->data_type = network_data_type_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "size") == 0) {
        return network_parse_q48(value, &data->data_size);
    }
    if (strcmp(suffix, "uncertainty") == 0) {
        return network_parse_q16(value, &data->data_uncertainty);
    }
    if (strcmp(suffix, "source") == 0) {
        data->source_node_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "sink") == 0) {
        data->sink_node_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "protocol") == 0) {
        data->protocol_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "network") == 0) {
        u32 net_id = d_rng_hash_str32(value);
        data->network_id = net_id;
        network_fixture_register_network(fixture, value, net_id);
        return 1;
    }
    if (strcmp(suffix, "send_tick") == 0) {
        return network_parse_u64(value, &data->send_tick);
    }
    return 0;
}

static int network_fixture_apply(network_fixture* fixture, const char* key, const char* value)
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
        return network_parse_u64(value, &fixture->info_desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return network_parse_u64(value, &fixture->info_desc.domain_id);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return network_parse_q16(value, &fixture->info_desc.meters_per_unit);
    }
    if (strcmp(key, "capacity_count") == 0) {
        return network_parse_u32(value, &fixture->info_desc.capacity_count);
    }
    if (strcmp(key, "node_count") == 0) {
        return network_parse_u32(value, &fixture->info_desc.node_count);
    }
    if (strcmp(key, "link_count") == 0) {
        return network_parse_u32(value, &fixture->info_desc.link_count);
    }
    if (strcmp(key, "data_count") == 0) {
        return network_parse_u32(value, &fixture->info_desc.data_count);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return network_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return network_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return network_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return network_parse_u32(value, &fixture->policy.cost_analytic);
    }

    if (network_parse_indexed_key(key, "capacity_", &index, &suffix)) {
        return network_fixture_apply_capacity(fixture, index, suffix, value);
    }
    if (network_parse_indexed_key(key, "node_", &index, &suffix)) {
        return network_fixture_apply_node(fixture, index, suffix, value);
    }
    if (network_parse_indexed_key(key, "link_", &index, &suffix)) {
        return network_fixture_apply_link(fixture, index, suffix, value);
    }
    if (network_parse_indexed_key(key, "data_", &index, &suffix)) {
        return network_fixture_apply_data(fixture, index, suffix, value);
    }
    return 0;
}

static int network_fixture_load(const char* path, network_fixture* out_fixture)
{
    FILE* file;
    char line[NETWORK_LINE_MAX];
    int header_ok = 0;
    network_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    network_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = network_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, NETWORK_FIXTURE_HEADER) != 0) {
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
        network_fixture_apply(&fixture, network_trim(text), network_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static const char* network_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 network_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = network_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && network_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u64 network_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* value = network_find_arg(argc, argv, key);
    u64 parsed = fallback;
    if (value && network_parse_u64(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u32 network_find_network_id(const network_fixture* fixture, const char* name)
{
    if (!name || !*name) {
        return 0u;
    }
    if (!fixture) {
        return d_rng_hash_str32(name);
    }
    for (u32 i = 0u; i < fixture->network_count; ++i) {
        if (strcmp(fixture->network_names[i], name) == 0) {
            return fixture->network_ids[i];
        }
    }
    return d_rng_hash_str32(name);
}

static const char* network_lookup_node_name(const network_fixture* fixture, u32 node_id)
{
    if (!fixture || node_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->info_desc.node_count; ++i) {
        if (fixture->info_desc.nodes[i].node_id == node_id) {
            return fixture->node_names[i];
        }
    }
    return "";
}

static const char* network_lookup_link_name(const network_fixture* fixture, u32 link_id)
{
    if (!fixture || link_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->info_desc.link_count; ++i) {
        if (fixture->info_desc.links[i].link_id == link_id) {
            return fixture->link_names[i];
        }
    }
    return "";
}

static const char* network_lookup_data_name(const network_fixture* fixture, u32 data_id)
{
    if (!fixture || data_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->info_desc.data_count; ++i) {
        if (fixture->info_desc.data[i].data_id == data_id) {
            return fixture->data_names[i];
        }
    }
    return "";
}

static const char* network_lookup_capacity_name(const network_fixture* fixture, u32 capacity_id)
{
    if (!fixture || capacity_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->info_desc.capacity_count; ++i) {
        if (fixture->info_desc.capacities[i].capacity_id == capacity_id) {
            return fixture->capacity_names[i];
        }
    }
    return "";
}

static int network_validate_fixture(const network_fixture* fixture)
{
    if (!fixture) {
        return 0;
    }
    if (fixture->info_desc.capacity_count > DOM_INFO_MAX_CAPACITY_PROFILES) {
        return 0;
    }
    if (fixture->info_desc.node_count > DOM_INFO_MAX_NODES) {
        return 0;
    }
    if (fixture->info_desc.link_count > DOM_INFO_MAX_LINKS) {
        return 0;
    }
    if (fixture->info_desc.data_count > DOM_INFO_MAX_DATA) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->info_desc.capacity_count; ++i) {
        const dom_info_capacity_desc* cap = &fixture->info_desc.capacities[i];
        if (cap->capacity_id == 0u) {
            return 0;
        }
        if (cap->error_rate < 0 || cap->error_rate > DOM_INFO_RATIO_ONE_Q16) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->info_desc.node_count; ++i) {
        const dom_info_node_desc* node = &fixture->info_desc.nodes[i];
        if (node->node_id == 0u) {
            return 0;
        }
        if (node->node_type == DOM_INFO_NODE_UNSET) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->info_desc.link_count; ++i) {
        const dom_info_link_desc* link = &fixture->info_desc.links[i];
        if (link->link_id == 0u) {
            return 0;
        }
        if (link->node_a_id == 0u || link->node_b_id == 0u) {
            return 0;
        }
        if (link->capacity_id == 0u) {
            return 0;
        }
        {
            int node_a_ok = 0;
            int node_b_ok = 0;
            int cap_ok = 0;
            for (u32 n = 0u; n < fixture->info_desc.node_count; ++n) {
                if (fixture->info_desc.nodes[n].node_id == link->node_a_id) {
                    node_a_ok = 1;
                }
                if (fixture->info_desc.nodes[n].node_id == link->node_b_id) {
                    node_b_ok = 1;
                }
            }
            for (u32 c = 0u; c < fixture->info_desc.capacity_count; ++c) {
                if (fixture->info_desc.capacities[c].capacity_id == link->capacity_id) {
                    cap_ok = 1;
                }
            }
            if (!node_a_ok || !node_b_ok || !cap_ok) {
                return 0;
            }
        }
    }
    for (u32 i = 0u; i < fixture->info_desc.data_count; ++i) {
        const dom_info_data_desc* data = &fixture->info_desc.data[i];
        if (data->data_id == 0u) {
            return 0;
        }
        if (data->data_type == DOM_INFO_DATA_UNSET) {
            return 0;
        }
        if (data->source_node_id == 0u || data->sink_node_id == 0u) {
            return 0;
        }
        if (data->data_uncertainty < 0 || data->data_uncertainty > DOM_INFO_RATIO_ONE_Q16) {
            return 0;
        }
    }
    return 1;
}

static int network_run_validate(const network_fixture* fixture)
{
    int ok = network_validate_fixture(fixture);
    printf("%s\n", NETWORK_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", NETWORK_PROVIDER_CHAIN);
    printf("capacity_count=%u\n", (unsigned int)fixture->info_desc.capacity_count);
    printf("node_count=%u\n", (unsigned int)fixture->info_desc.node_count);
    printf("link_count=%u\n", (unsigned int)fixture->info_desc.link_count);
    printf("data_count=%u\n", (unsigned int)fixture->info_desc.data_count);
    printf("ok=%u\n", (unsigned int)(ok ? 1u : 0u));
    return ok ? 0 : 1;
}

static int network_run_inspect_node(const network_fixture* fixture,
                                    const char* node_name,
                                    u32 budget_max)
{
    dom_info_domain domain;
    dom_domain_budget budget;
    dom_info_node_sample sample;
    u32 node_id;

    if (!node_name) {
        return 1;
    }
    node_id = d_rng_hash_str32(node_name);
    dom_info_domain_init(&domain, &fixture->info_desc);
    if (fixture->policy_set) {
        dom_info_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_info_node_query(&domain, node_id, &budget, &sample);

    printf("%s\n", NETWORK_INSPECT_HEADER);
    printf("entity=node\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", NETWORK_PROVIDER_CHAIN);
    printf("node_id=%u\n", (unsigned int)sample.node_id);
    printf("node_id_str=%s\n", network_lookup_node_name(fixture, sample.node_id));
    printf("node_type=%u\n", (unsigned int)sample.node_type);
    printf("node_type_tag=%s\n", network_node_type_to_text(sample.node_type));
    printf("compute_capacity_q48=%lld\n", (long long)sample.compute_capacity);
    printf("storage_capacity_q48=%lld\n", (long long)sample.storage_capacity);
    printf("storage_used_q48=%lld\n", (long long)sample.storage_used);
    printf("energy_per_unit_q48=%lld\n", (long long)sample.energy_per_unit);
    printf("heat_per_unit_q48=%lld\n", (long long)sample.heat_per_unit);
    printf("network_id=%u\n", (unsigned int)sample.network_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_info_domain_free(&domain);
    return 0;
}

static int network_run_inspect_link(const network_fixture* fixture,
                                    const char* link_name,
                                    u32 budget_max)
{
    dom_info_domain domain;
    dom_domain_budget budget;
    dom_info_link_sample sample;
    dom_info_capacity_sample capacity;
    u32 link_id;

    if (!link_name) {
        return 1;
    }
    link_id = d_rng_hash_str32(link_name);
    dom_info_domain_init(&domain, &fixture->info_desc);
    if (fixture->policy_set) {
        dom_info_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_info_link_query(&domain, link_id, &budget, &sample);
    (void)dom_info_capacity_query(&domain, sample.capacity_id, &budget, &capacity);

    printf("%s\n", NETWORK_INSPECT_HEADER);
    printf("entity=link\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", NETWORK_PROVIDER_CHAIN);
    printf("link_id=%u\n", (unsigned int)sample.link_id);
    printf("link_id_str=%s\n", network_lookup_link_name(fixture, sample.link_id));
    printf("network_id=%u\n", (unsigned int)sample.network_id);
    printf("node_a_id=%u\n", (unsigned int)sample.node_a_id);
    printf("node_b_id=%u\n", (unsigned int)sample.node_b_id);
    printf("capacity_id=%u\n", (unsigned int)sample.capacity_id);
    printf("capacity_id_str=%s\n", network_lookup_capacity_name(fixture, sample.capacity_id));
    printf("direction=%u\n", (unsigned int)sample.direction);
    printf("direction_tag=%s\n", network_link_direction_to_text(sample.direction));
    printf("bandwidth_limit_q48=%lld\n", (long long)capacity.bandwidth_limit);
    printf("latency_class=%u\n", (unsigned int)capacity.latency_class);
    printf("latency_class_tag=%s\n", network_latency_class_to_text(capacity.latency_class));
    printf("error_rate_q16=%d\n", (int)capacity.error_rate);
    printf("congestion_policy=%u\n", (unsigned int)capacity.congestion_policy);
    printf("congestion_policy_tag=%s\n", network_congestion_policy_to_text(capacity.congestion_policy));
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_info_domain_free(&domain);
    return 0;
}

static int network_run_inspect_capacity(const network_fixture* fixture,
                                        const char* capacity_name,
                                        u32 budget_max)
{
    dom_info_domain domain;
    dom_domain_budget budget;
    dom_info_capacity_sample sample;
    u32 capacity_id;

    if (!capacity_name) {
        return 1;
    }
    capacity_id = d_rng_hash_str32(capacity_name);
    dom_info_domain_init(&domain, &fixture->info_desc);
    if (fixture->policy_set) {
        dom_info_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_info_capacity_query(&domain, capacity_id, &budget, &sample);

    printf("%s\n", NETWORK_INSPECT_HEADER);
    printf("entity=capacity\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", NETWORK_PROVIDER_CHAIN);
    printf("capacity_id=%u\n", (unsigned int)sample.capacity_id);
    printf("capacity_id_str=%s\n", network_lookup_capacity_name(fixture, sample.capacity_id));
    printf("bandwidth_limit_q48=%lld\n", (long long)sample.bandwidth_limit);
    printf("latency_class=%u\n", (unsigned int)sample.latency_class);
    printf("latency_class_tag=%s\n", network_latency_class_to_text(sample.latency_class));
    printf("error_rate_q16=%d\n", (int)sample.error_rate);
    printf("congestion_policy=%u\n", (unsigned int)sample.congestion_policy);
    printf("congestion_policy_tag=%s\n", network_congestion_policy_to_text(sample.congestion_policy));
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_info_domain_free(&domain);
    return 0;
}

static int network_run_inspect_data(const network_fixture* fixture,
                                    const char* data_name,
                                    u32 budget_max)
{
    dom_info_domain domain;
    dom_domain_budget budget;
    dom_info_data_sample sample;
    u32 data_id;

    if (!data_name) {
        return 1;
    }
    data_id = d_rng_hash_str32(data_name);
    dom_info_domain_init(&domain, &fixture->info_desc);
    if (fixture->policy_set) {
        dom_info_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_info_data_query(&domain, data_id, &budget, &sample);

    printf("%s\n", NETWORK_INSPECT_HEADER);
    printf("entity=data\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", NETWORK_PROVIDER_CHAIN);
    printf("data_id=%u\n", (unsigned int)sample.data_id);
    printf("data_id_str=%s\n", network_lookup_data_name(fixture, sample.data_id));
    printf("data_type=%u\n", (unsigned int)sample.data_type);
    printf("data_type_tag=%s\n", network_data_type_to_text(sample.data_type));
    printf("data_size_q48=%lld\n", (long long)sample.data_size);
    printf("data_uncertainty_q16=%d\n", (int)sample.data_uncertainty);
    printf("source_node_id=%u\n", (unsigned int)sample.source_node_id);
    printf("sink_node_id=%u\n", (unsigned int)sample.sink_node_id);
    printf("protocol_id=%u\n", (unsigned int)sample.protocol_id);
    printf("network_id=%u\n", (unsigned int)sample.network_id);
    printf("send_tick=%llu\n", (unsigned long long)sample.send_tick);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_info_domain_free(&domain);
    return 0;
}

static int network_run_inspect_network(const network_fixture* fixture,
                                       const char* network_name,
                                       u32 budget_max)
{
    dom_info_domain domain;
    dom_domain_budget budget;
    dom_info_network_sample sample;
    u32 network_id = network_find_network_id(fixture, network_name);

    dom_info_domain_init(&domain, &fixture->info_desc);
    if (fixture->policy_set) {
        dom_info_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_info_network_query(&domain, network_id, &budget, &sample);

    printf("%s\n", NETWORK_INSPECT_HEADER);
    printf("entity=network\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", NETWORK_PROVIDER_CHAIN);
    printf("network_id=%u\n", (unsigned int)sample.network_id);
    printf("node_count=%u\n", (unsigned int)sample.node_count);
    printf("link_count=%u\n", (unsigned int)sample.link_count);
    printf("data_count=%u\n", (unsigned int)sample.data_count);
    printf("data_total_q48=%lld\n", (long long)sample.data_total);
    printf("queued_count=%u\n", (unsigned int)sample.queued_count);
    printf("dropped_count=%u\n", (unsigned int)sample.dropped_count);
    printf("error_rate_avg_q16=%d\n", (int)sample.error_rate_avg);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_info_domain_free(&domain);
    return 0;
}

static int network_run_resolve(const network_fixture* fixture,
                               const char* network_name,
                               u64 tick,
                               u64 tick_delta,
                               u32 budget_max,
                               u32 inactive_count)
{
    dom_info_domain domain;
    dom_info_domain* inactive = 0;
    dom_domain_budget budget;
    dom_info_resolve_result result;
    u32 network_id = network_find_network_id(fixture, network_name);
    u64 hash = 14695981039346656037ULL;

    dom_info_domain_init(&domain, &fixture->info_desc);
    if (fixture->policy_set) {
        dom_info_domain_set_policy(&domain, &fixture->policy);
    }

    if (inactive_count > 0u) {
        inactive = (dom_info_domain*)malloc(sizeof(dom_info_domain) * inactive_count);
        if (inactive) {
            for (u32 i = 0u; i < inactive_count; ++i) {
                network_fixture temp = *fixture;
                temp.info_desc.domain_id = fixture->info_desc.domain_id + (u64)(i + 1u);
                dom_info_domain_init(&inactive[i], &temp.info_desc);
                dom_info_domain_set_state(&inactive[i],
                                          DOM_DOMAIN_EXISTENCE_DECLARED,
                                          DOM_DOMAIN_ARCHIVAL_LIVE);
            }
        }
    }

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_info_resolve(&domain, network_id, tick, tick_delta, &budget, &result);

    for (u32 i = 0u; i < domain.data_count; ++i) {
        hash = network_hash_u32(hash, domain.data[i].data_id);
        hash = network_hash_u32(hash, domain.data[i].flags);
        hash = network_hash_q48(hash, domain.data[i].data_size);
        hash = network_hash_q16(hash, domain.data[i].data_uncertainty);
    }
    for (u32 i = 0u; i < domain.node_count; ++i) {
        hash = network_hash_u32(hash, domain.nodes[i].node_id);
        hash = network_hash_q48(hash, domain.nodes[i].storage_used);
    }

    printf("%s\n", NETWORK_RESOLVE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", NETWORK_PROVIDER_CHAIN);
    printf("network_id=%u\n", (unsigned int)network_id);
    printf("delivered_count=%u\n", (unsigned int)result.delivered_count);
    printf("dropped_count=%u\n", (unsigned int)result.dropped_count);
    printf("queued_count=%u\n", (unsigned int)result.queued_count);
    printf("energy_cost_q48=%lld\n", (long long)result.energy_cost_total);
    printf("heat_generated_q48=%lld\n", (long long)result.heat_generated_total);
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);
    printf("resolve_hash=%llu\n", (unsigned long long)hash);

    dom_info_domain_free(&domain);
    if (inactive) {
        for (u32 i = 0u; i < inactive_count; ++i) {
            dom_info_domain_free(&inactive[i]);
        }
        free(inactive);
    }
    return 0;
}

static int network_run_collapse(const network_fixture* fixture, const char* network_name)
{
    dom_info_domain domain;
    u32 network_id = network_find_network_id(fixture, network_name);
    u32 count_before;
    u32 count_after;

    dom_info_domain_init(&domain, &fixture->info_desc);
    if (fixture->policy_set) {
        dom_info_domain_set_policy(&domain, &fixture->policy);
    }
    count_before = dom_info_domain_capsule_count(&domain);
    (void)dom_info_domain_collapse_network(&domain, network_id);
    count_after = dom_info_domain_capsule_count(&domain);

    printf("%s\n", NETWORK_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", NETWORK_PROVIDER_CHAIN);
    printf("network_id=%u\n", (unsigned int)network_id);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);

    dom_info_domain_free(&domain);
    return 0;
}

static void network_usage(void)
{
    printf("dom_tool_network commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --node <id> [--budget N]\n");
    printf("  inspect --fixture <path> --link <id> [--budget N]\n");
    printf("  inspect --fixture <path> --capacity <id> [--budget N]\n");
    printf("  inspect --fixture <path> --data <id> [--budget N]\n");
    printf("  inspect --fixture <path> --network <id> [--budget N]\n");
    printf("  resolve --fixture <path> --network <id> [--tick N] [--delta N] [--budget N] [--inactive N]\n");
    printf("  collapse --fixture <path> --network <id>\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        network_usage();
        return 2;
    }
    cmd = argv[1];
    if (strcmp(cmd, "validate") == 0 ||
        strcmp(cmd, "inspect") == 0 ||
        strcmp(cmd, "resolve") == 0 ||
        strcmp(cmd, "collapse") == 0) {
        const char* fixture_path = network_find_arg(argc, argv, "--fixture");
        network_fixture fixture;
        if (!fixture_path || !network_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "network: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return network_run_validate(&fixture);
        }
        if (strcmp(cmd, "inspect") == 0) {
            const char* node_name = network_find_arg(argc, argv, "--node");
            const char* link_name = network_find_arg(argc, argv, "--link");
            const char* capacity_name = network_find_arg(argc, argv, "--capacity");
            const char* data_name = network_find_arg(argc, argv, "--data");
            const char* network_name = network_find_arg(argc, argv, "--network");
            u32 budget_max = network_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_full);
            if (node_name) {
                return network_run_inspect_node(&fixture, node_name, budget_max);
            }
            if (link_name) {
                return network_run_inspect_link(&fixture, link_name, budget_max);
            }
            if (capacity_name) {
                return network_run_inspect_capacity(&fixture, capacity_name, budget_max);
            }
            if (data_name) {
                return network_run_inspect_data(&fixture, data_name, budget_max);
            }
            if (network_name) {
                return network_run_inspect_network(&fixture, network_name, budget_max);
            }
            fprintf(stderr, "network: inspect requires --node, --link, --capacity, --data, or --network\n");
            return 2;
        }
        if (strcmp(cmd, "resolve") == 0) {
            const char* network_name = network_find_arg(argc, argv, "--network");
            u64 tick = network_find_arg_u64(argc, argv, "--tick", 0u);
            u64 delta = network_find_arg_u64(argc, argv, "--delta", 1u);
            u32 budget_max = network_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_medium);
            u32 inactive = network_find_arg_u32(argc, argv, "--inactive", 0u);
            if (!network_name) {
                fprintf(stderr, "network: resolve requires --network\n");
                return 2;
            }
            return network_run_resolve(&fixture, network_name, tick, delta, budget_max, inactive);
        }
        if (strcmp(cmd, "collapse") == 0) {
            const char* network_name = network_find_arg(argc, argv, "--network");
            if (!network_name) {
                fprintf(stderr, "network: collapse requires --network\n");
                return 2;
            }
            return network_run_collapse(&fixture, network_name);
        }
    }

    network_usage();
    return 2;
}
