/*
FILE: tools/heat/heat_cli.cpp
MODULE: Dominium
PURPOSE: Heat fixture CLI for deterministic thermal accounting checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"
#include "domino/world/heat_fields.h"

#define HEAT_FIXTURE_HEADER "DOMINIUM_HEAT_FIXTURE_V1"

#define HEAT_VALIDATE_HEADER "DOMINIUM_HEAT_VALIDATE_V1"
#define HEAT_INSPECT_HEADER "DOMINIUM_HEAT_INSPECT_V1"
#define HEAT_RESOLVE_HEADER "DOMINIUM_HEAT_RESOLVE_V1"
#define HEAT_COLLAPSE_HEADER "DOMINIUM_HEAT_COLLAPSE_V1"

#define HEAT_PROVIDER_CHAIN "stores->flows->exchange->stress"

#define HEAT_LINE_MAX 512u

typedef struct heat_fixture {
    char fixture_id[96];
    dom_heat_surface_desc heat_desc;
    dom_domain_policy policy;
    u32 policy_set;
    char store_names[DOM_HEAT_MAX_STORES][64];
    char flow_names[DOM_HEAT_MAX_FLOWS][64];
    char stress_names[DOM_HEAT_MAX_STRESSES][64];
    char network_names[DOM_HEAT_MAX_NETWORKS][64];
    u32 network_ids[DOM_HEAT_MAX_NETWORKS];
    u32 network_count;
} heat_fixture;

static u64 heat_hash_u64(u64 h, u64 v)
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

static u64 heat_hash_u32(u64 h, u32 v)
{
    return heat_hash_u64(h, (u64)v);
}

static u64 heat_hash_q48(u64 h, q48_16 v)
{
    return heat_hash_u64(h, (u64)v);
}

static char* heat_trim(char* text)
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

static int heat_parse_u32(const char* text, u32* out_value)
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

static int heat_parse_u64(const char* text, u64* out_value)
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

static int heat_parse_q16(const char* text, q16_16* out_value)
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

static int heat_parse_q48(const char* text, q48_16* out_value)
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

static int heat_parse_triplet_q16(const char* text, q16_16* a, q16_16* b, q16_16* c)
{
    char buffer[HEAT_LINE_MAX];
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
    if (!heat_parse_q16(heat_trim(first), a)) return 0;
    if (!heat_parse_q16(heat_trim(second), b)) return 0;
    if (!heat_parse_q16(heat_trim(third), c)) return 0;
    return 1;
}

static int heat_parse_point(const char* text, dom_domain_point* out_point)
{
    q16_16 x;
    q16_16 y;
    q16_16 z;
    if (!text || !out_point) {
        return 0;
    }
    if (!heat_parse_triplet_q16(text, &x, &y, &z)) {
        return 0;
    }
    out_point->x = x;
    out_point->y = y;
    out_point->z = z;
    return 1;
}

static q48_16 heat_sample_temperature(const heat_fixture* fixture,
                                      const dom_heat_store_sample* sample)
{
    q48_16 ratio;
    if (!fixture || !sample) {
        return 0;
    }
    if (sample->capacity <= 0 || sample->amount <= 0 || fixture->heat_desc.temperature_scale <= 0) {
        return 0;
    }
    ratio = d_q48_16_div(sample->amount, sample->capacity);
    if (ratio < 0) {
        ratio = 0;
    }
    return d_q48_16_mul(ratio, fixture->heat_desc.temperature_scale);
}

static int heat_parse_indexed_key(const char* key,
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

static u32 heat_failure_mask_from_text(const char* text)
{
    char buffer[HEAT_LINE_MAX];
    char* token;
    char* cur;
    u32 mask = 0u;
    if (!text || !*text) {
        return 0u;
    }
    strncpy(buffer, text, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    cur = buffer;
    while ((token = strtok(cur, ",|")) != 0) {
        token = heat_trim(token);
        if (strcmp(token, "overload") == 0) mask |= DOM_HEAT_FAILURE_OVERLOAD;
        else if (strcmp(token, "blocked") == 0) mask |= DOM_HEAT_FAILURE_BLOCKED;
        else if (strcmp(token, "leakage") == 0) mask |= DOM_HEAT_FAILURE_LEAKAGE;
        else if (strcmp(token, "cascade") == 0) mask |= DOM_HEAT_FAILURE_CASCADE;
        cur = 0;
    }
    return mask;
}

static void heat_fixture_init(heat_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_heat_surface_desc_init(&fixture->heat_desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->policy_set = 0u;
    fixture->network_count = 0u;
    strncpy(fixture->fixture_id, "heat.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
}

static void heat_fixture_register_network(heat_fixture* fixture, const char* name, u32 id)
{
    if (!fixture || !name || !*name || id == 0u) {
        return;
    }
    for (u32 i = 0u; i < fixture->network_count; ++i) {
        if (fixture->network_ids[i] == id) {
            return;
        }
    }
    if (fixture->network_count >= DOM_HEAT_MAX_NETWORKS) {
        return;
    }
    fixture->network_ids[fixture->network_count] = id;
    strncpy(fixture->network_names[fixture->network_count], name,
            sizeof(fixture->network_names[fixture->network_count]) - 1);
    fixture->network_names[fixture->network_count][sizeof(fixture->network_names[fixture->network_count]) - 1] = '\0';
    fixture->network_count += 1u;
}

static int heat_fixture_apply_store(heat_fixture* fixture,
                                    u32 index,
                                    const char* suffix,
                                    const char* value)
{
    dom_heat_store_desc* store;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_HEAT_MAX_STORES) {
        return 0;
    }
    if (fixture->heat_desc.store_count <= index) {
        fixture->heat_desc.store_count = index + 1u;
    }
    store = &fixture->heat_desc.stores[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->store_names[index], value, sizeof(fixture->store_names[index]) - 1);
        fixture->store_names[index][sizeof(fixture->store_names[index]) - 1] = '\0';
        store->store_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "amount") == 0) {
        return heat_parse_q48(value, &store->amount);
    }
    if (strcmp(suffix, "capacity") == 0) {
        return heat_parse_q48(value, &store->capacity);
    }
    if (strcmp(suffix, "exchange") == 0) {
        return heat_parse_q16(value, &store->ambient_exchange_rate);
    }
    if (strcmp(suffix, "network") == 0) {
        u32 net_id = d_rng_hash_str32(value);
        store->network_id = net_id;
        heat_fixture_register_network(fixture, value, net_id);
        return 1;
    }
    if (strcmp(suffix, "pos") == 0) {
        return heat_parse_point(value, &store->location);
    }
    return 0;
}

static int heat_fixture_apply_flow(heat_fixture* fixture,
                                   u32 index,
                                   const char* suffix,
                                   const char* value)
{
    dom_heat_flow_desc* flow;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_HEAT_MAX_FLOWS) {
        return 0;
    }
    if (fixture->heat_desc.flow_count <= index) {
        fixture->heat_desc.flow_count = index + 1u;
    }
    flow = &fixture->heat_desc.flows[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->flow_names[index], value, sizeof(fixture->flow_names[index]) - 1);
        fixture->flow_names[index][sizeof(fixture->flow_names[index]) - 1] = '\0';
        flow->flow_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "network") == 0) {
        u32 net_id = d_rng_hash_str32(value);
        flow->network_id = net_id;
        heat_fixture_register_network(fixture, value, net_id);
        return 1;
    }
    if (strcmp(suffix, "source") == 0) {
        flow->source_store_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "sink") == 0) {
        flow->sink_store_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "max_rate") == 0) {
        return heat_parse_q48(value, &flow->max_transfer_rate);
    }
    if (strcmp(suffix, "efficiency") == 0) {
        return heat_parse_q16(value, &flow->efficiency);
    }
    if (strcmp(suffix, "latency") == 0) {
        return heat_parse_u64(value, &flow->latency_ticks);
    }
    if (strcmp(suffix, "failure") == 0) {
        flow->failure_mode_mask = heat_failure_mask_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "failure_chance") == 0) {
        return heat_parse_q16(value, &flow->failure_chance);
    }
    return 0;
}

static int heat_fixture_apply_stress(heat_fixture* fixture,
                                     u32 index,
                                     const char* suffix,
                                     const char* value)
{
    dom_thermal_stress_desc* stress;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_HEAT_MAX_STRESSES) {
        return 0;
    }
    if (fixture->heat_desc.stress_count <= index) {
        fixture->heat_desc.stress_count = index + 1u;
    }
    stress = &fixture->heat_desc.stresses[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->stress_names[index], value, sizeof(fixture->stress_names[index]) - 1);
        fixture->stress_names[index][sizeof(fixture->stress_names[index]) - 1] = '\0';
        stress->stress_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "store") == 0) {
        stress->store_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "safe_min") == 0) {
        return heat_parse_q48(value, &stress->safe_min);
    }
    if (strcmp(suffix, "safe_max") == 0) {
        return heat_parse_q48(value, &stress->safe_max);
    }
    if (strcmp(suffix, "damage_rate") == 0) {
        return heat_parse_q16(value, &stress->damage_rate);
    }
    if (strcmp(suffix, "efficiency") == 0) {
        return heat_parse_q16(value, &stress->efficiency_modifier);
    }
    return 0;
}

static int heat_fixture_apply(heat_fixture* fixture, const char* key, const char* value)
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
        return heat_parse_u64(value, &fixture->heat_desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return heat_parse_u64(value, &fixture->heat_desc.domain_id);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return heat_parse_q16(value, &fixture->heat_desc.meters_per_unit);
    }
    if (strcmp(key, "temperature_scale") == 0) {
        return heat_parse_q48(value, &fixture->heat_desc.temperature_scale);
    }
    if (strcmp(key, "store_count") == 0) {
        return heat_parse_u32(value, &fixture->heat_desc.store_count);
    }
    if (strcmp(key, "flow_count") == 0) {
        return heat_parse_u32(value, &fixture->heat_desc.flow_count);
    }
    if (strcmp(key, "stress_count") == 0) {
        return heat_parse_u32(value, &fixture->heat_desc.stress_count);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return heat_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return heat_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return heat_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return heat_parse_u32(value, &fixture->policy.cost_analytic);
    }

    if (heat_parse_indexed_key(key, "store_", &index, &suffix)) {
        return heat_fixture_apply_store(fixture, index, suffix, value);
    }
    if (heat_parse_indexed_key(key, "flow_", &index, &suffix)) {
        return heat_fixture_apply_flow(fixture, index, suffix, value);
    }
    if (heat_parse_indexed_key(key, "stress_", &index, &suffix)) {
        return heat_fixture_apply_stress(fixture, index, suffix, value);
    }
    return 0;
}

static int heat_fixture_load(const char* path, heat_fixture* out_fixture)
{
    FILE* file;
    char line[HEAT_LINE_MAX];
    int header_ok = 0;
    heat_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    heat_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = heat_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, HEAT_FIXTURE_HEADER) != 0) {
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
        heat_fixture_apply(&fixture, heat_trim(text), heat_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static const char* heat_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 heat_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = heat_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && heat_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u64 heat_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* value = heat_find_arg(argc, argv, key);
    u64 parsed = fallback;
    if (value && heat_parse_u64(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u32 heat_find_network_id(const heat_fixture* fixture, const char* name)
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

static const char* heat_lookup_store_name(const heat_fixture* fixture, u32 store_id)
{
    if (!fixture || store_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->heat_desc.store_count; ++i) {
        if (fixture->heat_desc.stores[i].store_id == store_id) {
            return fixture->store_names[i];
        }
    }
    return "";
}

static const char* heat_lookup_flow_name(const heat_fixture* fixture, u32 flow_id)
{
    if (!fixture || flow_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->heat_desc.flow_count; ++i) {
        if (fixture->heat_desc.flows[i].flow_id == flow_id) {
            return fixture->flow_names[i];
        }
    }
    return "";
}

static const char* heat_lookup_stress_name(const heat_fixture* fixture, u32 stress_id)
{
    if (!fixture || stress_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->heat_desc.stress_count; ++i) {
        if (fixture->heat_desc.stresses[i].stress_id == stress_id) {
            return fixture->stress_names[i];
        }
    }
    return "";
}

static int heat_validate_fixture(const heat_fixture* fixture)
{
    if (!fixture) {
        return 0;
    }
    if (fixture->heat_desc.store_count > DOM_HEAT_MAX_STORES) {
        return 0;
    }
    if (fixture->heat_desc.flow_count > DOM_HEAT_MAX_FLOWS) {
        return 0;
    }
    if (fixture->heat_desc.stress_count > DOM_HEAT_MAX_STRESSES) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->heat_desc.store_count; ++i) {
        const dom_heat_store_desc* store = &fixture->heat_desc.stores[i];
        if (store->store_id == 0u) {
            return 0;
        }
        if (store->capacity < store->amount) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->heat_desc.flow_count; ++i) {
        const dom_heat_flow_desc* flow = &fixture->heat_desc.flows[i];
        if (flow->flow_id == 0u) {
            return 0;
        }
        if (flow->source_store_id == 0u || flow->sink_store_id == 0u) {
            return 0;
        }
        {
            int source_ok = 0;
            int sink_ok = 0;
            for (u32 s = 0u; s < fixture->heat_desc.store_count; ++s) {
                if (fixture->heat_desc.stores[s].store_id == flow->source_store_id) {
                    source_ok = 1;
                }
                if (fixture->heat_desc.stores[s].store_id == flow->sink_store_id) {
                    sink_ok = 1;
                }
            }
            if (!source_ok || !sink_ok) {
                return 0;
            }
        }
        if (flow->efficiency < 0 || flow->efficiency > DOM_HEAT_RATIO_ONE_Q16) {
            return 0;
        }
        if (flow->failure_chance < 0 || flow->failure_chance > DOM_HEAT_RATIO_ONE_Q16) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->heat_desc.stress_count; ++i) {
        const dom_thermal_stress_desc* stress = &fixture->heat_desc.stresses[i];
        int store_ok = 0;
        if (stress->stress_id == 0u || stress->store_id == 0u) {
            return 0;
        }
        for (u32 s = 0u; s < fixture->heat_desc.store_count; ++s) {
            if (fixture->heat_desc.stores[s].store_id == stress->store_id) {
                store_ok = 1;
                break;
            }
        }
        if (!store_ok) {
            return 0;
        }
        if (stress->safe_min > stress->safe_max) {
            return 0;
        }
        if (stress->damage_rate < 0 || stress->damage_rate > DOM_HEAT_RATIO_ONE_Q16) {
            return 0;
        }
        if (stress->efficiency_modifier < 0 || stress->efficiency_modifier > DOM_HEAT_RATIO_ONE_Q16) {
            return 0;
        }
    }
    return 1;
}

static int heat_run_validate(const heat_fixture* fixture)
{
    int ok = heat_validate_fixture(fixture);
    printf("%s\n", HEAT_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HEAT_PROVIDER_CHAIN);
    printf("store_count=%u\n", (unsigned int)fixture->heat_desc.store_count);
    printf("flow_count=%u\n", (unsigned int)fixture->heat_desc.flow_count);
    printf("stress_count=%u\n", (unsigned int)fixture->heat_desc.stress_count);
    printf("ok=%u\n", (unsigned int)(ok ? 1u : 0u));
    return ok ? 0 : 1;
}

static int heat_run_inspect_store(const heat_fixture* fixture,
                                  const char* store_name,
                                  u32 budget_max)
{
    dom_heat_domain domain;
    dom_domain_budget budget;
    dom_heat_store_sample sample;
    q48_16 temperature;
    u32 store_id;

    if (!store_name) {
        return 1;
    }
    store_id = d_rng_hash_str32(store_name);
    dom_heat_domain_init(&domain, &fixture->heat_desc);
    if (fixture->policy_set) {
        dom_heat_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_heat_store_query(&domain, store_id, &budget, &sample);
    temperature = heat_sample_temperature(fixture, &sample);

    printf("%s\n", HEAT_INSPECT_HEADER);
    printf("entity=store\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HEAT_PROVIDER_CHAIN);
    printf("store_id=%u\n", (unsigned int)sample.store_id);
    printf("store_id_str=%s\n", heat_lookup_store_name(fixture, sample.store_id));
    printf("amount_q48=%lld\n", (long long)sample.amount);
    printf("capacity_q48=%lld\n", (long long)sample.capacity);
    printf("exchange_rate_q16=%d\n", (int)sample.ambient_exchange_rate);
    printf("temperature_q48=%lld\n", (long long)temperature);
    printf("network_id=%u\n", (unsigned int)sample.network_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_heat_domain_free(&domain);
    return 0;
}

static int heat_run_inspect_flow(const heat_fixture* fixture,
                                 const char* flow_name,
                                 u32 budget_max)
{
    dom_heat_domain domain;
    dom_domain_budget budget;
    dom_heat_flow_sample sample;
    u32 flow_id;

    if (!flow_name) {
        return 1;
    }
    flow_id = d_rng_hash_str32(flow_name);
    dom_heat_domain_init(&domain, &fixture->heat_desc);
    if (fixture->policy_set) {
        dom_heat_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_heat_flow_query(&domain, flow_id, &budget, &sample);

    printf("%s\n", HEAT_INSPECT_HEADER);
    printf("entity=flow\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HEAT_PROVIDER_CHAIN);
    printf("flow_id=%u\n", (unsigned int)sample.flow_id);
    printf("flow_id_str=%s\n", heat_lookup_flow_name(fixture, sample.flow_id));
    printf("network_id=%u\n", (unsigned int)sample.network_id);
    printf("source_store_id=%u\n", (unsigned int)sample.source_store_id);
    printf("sink_store_id=%u\n", (unsigned int)sample.sink_store_id);
    printf("max_rate_q48=%lld\n", (long long)sample.max_transfer_rate);
    printf("efficiency_q16=%d\n", (int)sample.efficiency);
    printf("latency_ticks=%llu\n", (unsigned long long)sample.latency_ticks);
    printf("failure_mask=%u\n", (unsigned int)sample.failure_mode_mask);
    printf("failure_chance_q16=%d\n", (int)sample.failure_chance);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_heat_domain_free(&domain);
    return 0;
}

static int heat_run_inspect_network(const heat_fixture* fixture,
                                    const char* network_name,
                                    u32 budget_max)
{
    dom_heat_domain domain;
    dom_domain_budget budget;
    dom_heat_network_sample sample;
    u32 network_id = heat_find_network_id(fixture, network_name);

    dom_heat_domain_init(&domain, &fixture->heat_desc);
    if (fixture->policy_set) {
        dom_heat_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_heat_network_query(&domain, network_id, &budget, &sample);

    printf("%s\n", HEAT_INSPECT_HEADER);
    printf("entity=network\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HEAT_PROVIDER_CHAIN);
    printf("network_id=%u\n", (unsigned int)sample.network_id);
    printf("store_count=%u\n", (unsigned int)sample.store_count);
    printf("flow_count=%u\n", (unsigned int)sample.flow_count);
    printf("heat_total_q48=%lld\n", (long long)sample.heat_total);
    printf("capacity_total_q48=%lld\n", (long long)sample.capacity_total);
    printf("dissipated_total_q48=%lld\n", (long long)sample.dissipated_total);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_heat_domain_free(&domain);
    return 0;
}

static int heat_run_inspect_stress(const heat_fixture* fixture,
                                   const char* stress_name,
                                   u32 budget_max)
{
    dom_heat_domain domain;
    dom_domain_budget budget;
    dom_thermal_stress_sample sample;
    u32 stress_id;

    if (!stress_name) {
        return 1;
    }
    stress_id = d_rng_hash_str32(stress_name);
    dom_heat_domain_init(&domain, &fixture->heat_desc);
    if (fixture->policy_set) {
        dom_heat_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_heat_stress_query(&domain, stress_id, &budget, &sample);

    printf("%s\n", HEAT_INSPECT_HEADER);
    printf("entity=stress\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HEAT_PROVIDER_CHAIN);
    printf("stress_id=%u\n", (unsigned int)sample.stress_id);
    printf("stress_id_str=%s\n", heat_lookup_stress_name(fixture, sample.stress_id));
    printf("store_id=%u\n", (unsigned int)sample.store_id);
    printf("store_id_str=%s\n", heat_lookup_store_name(fixture, sample.store_id));
    printf("operating_temperature_q48=%lld\n", (long long)sample.operating_temperature);
    printf("safe_min_q48=%lld\n", (long long)sample.safe_min);
    printf("safe_max_q48=%lld\n", (long long)sample.safe_max);
    printf("damage_rate_q16=%d\n", (int)sample.damage_rate);
    printf("efficiency_modifier_q16=%d\n", (int)sample.efficiency_modifier);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_heat_domain_free(&domain);
    return 0;
}

static int heat_run_resolve(const heat_fixture* fixture,
                            const char* network_name,
                            u64 tick,
                            u64 tick_delta,
                            u32 budget_max,
                            u32 inactive_count)
{
    dom_heat_domain domain;
    dom_heat_domain* inactive = 0;
    dom_domain_budget budget;
    dom_heat_resolve_result result;
    u32 network_id = heat_find_network_id(fixture, network_name);
    u64 hash = 14695981039346656037ULL;

    dom_heat_domain_init(&domain, &fixture->heat_desc);
    if (fixture->policy_set) {
        dom_heat_domain_set_policy(&domain, &fixture->policy);
    }

    if (inactive_count > 0u) {
        inactive = (dom_heat_domain*)malloc(sizeof(dom_heat_domain) * inactive_count);
        if (inactive) {
            for (u32 i = 0u; i < inactive_count; ++i) {
                heat_fixture temp = *fixture;
                temp.heat_desc.domain_id = fixture->heat_desc.domain_id + (u64)(i + 1u);
                dom_heat_domain_init(&inactive[i], &temp.heat_desc);
                dom_heat_domain_set_state(&inactive[i],
                                          DOM_DOMAIN_EXISTENCE_DECLARED,
                                          DOM_DOMAIN_ARCHIVAL_LIVE);
            }
        }
    }

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_heat_resolve(&domain, network_id, tick, tick_delta, &budget, &result);

    for (u32 i = 0u; i < domain.store_count; ++i) {
        hash = heat_hash_u32(hash, domain.stores[i].store_id);
        hash = heat_hash_q48(hash, domain.stores[i].amount);
    }

    printf("%s\n", HEAT_RESOLVE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HEAT_PROVIDER_CHAIN);
    printf("network_id=%u\n", (unsigned int)network_id);
    printf("store_count=%u\n", (unsigned int)result.store_count);
    printf("flow_count=%u\n", (unsigned int)result.flow_count);
    printf("stress_count=%u\n", (unsigned int)result.stress_count);
    printf("stress_overheat_count=%u\n", (unsigned int)result.stress_overheat_count);
    printf("stress_undercool_count=%u\n", (unsigned int)result.stress_undercool_count);
    printf("stress_damage_count=%u\n", (unsigned int)result.stress_damage_count);
    printf("heat_transferred_q48=%lld\n", (long long)result.heat_transferred);
    printf("heat_dissipated_q48=%lld\n", (long long)result.heat_dissipated);
    printf("heat_remaining_q48=%lld\n", (long long)result.heat_remaining);
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);
    printf("resolve_hash=%llu\n", (unsigned long long)hash);

    dom_heat_domain_free(&domain);
    if (inactive) {
        for (u32 i = 0u; i < inactive_count; ++i) {
            dom_heat_domain_free(&inactive[i]);
        }
        free(inactive);
    }
    return 0;
}

static int heat_run_collapse(const heat_fixture* fixture, const char* network_name)
{
    dom_heat_domain domain;
    u32 network_id = heat_find_network_id(fixture, network_name);
    u32 count_before;
    u32 count_after;

    dom_heat_domain_init(&domain, &fixture->heat_desc);
    if (fixture->policy_set) {
        dom_heat_domain_set_policy(&domain, &fixture->policy);
    }
    count_before = dom_heat_domain_capsule_count(&domain);
    (void)dom_heat_domain_collapse_network(&domain, network_id);
    count_after = dom_heat_domain_capsule_count(&domain);

    printf("%s\n", HEAT_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HEAT_PROVIDER_CHAIN);
    printf("network_id=%u\n", (unsigned int)network_id);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);

    dom_heat_domain_free(&domain);
    return 0;
}

static void heat_usage(void)
{
    printf("dom_tool_heat commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --store <id> [--budget N]\n");
    printf("  inspect --fixture <path> --flow <id> [--budget N]\n");
    printf("  inspect --fixture <path> --network <id> [--budget N]\n");
    printf("  inspect --fixture <path> --stress <id> [--budget N]\n");
    printf("  resolve --fixture <path> --network <id> [--tick N] [--delta N] [--budget N] [--inactive N]\n");
    printf("  collapse --fixture <path> --network <id>\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        heat_usage();
        return 2;
    }
    cmd = argv[1];
    if (strcmp(cmd, "validate") == 0 ||
        strcmp(cmd, "inspect") == 0 ||
        strcmp(cmd, "resolve") == 0 ||
        strcmp(cmd, "collapse") == 0) {
        const char* fixture_path = heat_find_arg(argc, argv, "--fixture");
        heat_fixture fixture;
        if (!fixture_path || !heat_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "heat: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return heat_run_validate(&fixture);
        }
        if (strcmp(cmd, "inspect") == 0) {
            const char* store_name = heat_find_arg(argc, argv, "--store");
            const char* flow_name = heat_find_arg(argc, argv, "--flow");
            const char* network_name = heat_find_arg(argc, argv, "--network");
            const char* stress_name = heat_find_arg(argc, argv, "--stress");
            u32 budget_max = heat_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_full);
            if (store_name) {
                return heat_run_inspect_store(&fixture, store_name, budget_max);
            }
            if (flow_name) {
                return heat_run_inspect_flow(&fixture, flow_name, budget_max);
            }
            if (network_name) {
                return heat_run_inspect_network(&fixture, network_name, budget_max);
            }
            if (stress_name) {
                return heat_run_inspect_stress(&fixture, stress_name, budget_max);
            }
            fprintf(stderr, "heat: inspect requires --store, --flow, --stress, or --network\n");
            return 2;
        }
        if (strcmp(cmd, "resolve") == 0) {
            const char* network_name = heat_find_arg(argc, argv, "--network");
            u64 tick = heat_find_arg_u64(argc, argv, "--tick", 0u);
            u64 delta = heat_find_arg_u64(argc, argv, "--delta", 1u);
            u32 budget_max = heat_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_medium);
            u32 inactive = heat_find_arg_u32(argc, argv, "--inactive", 0u);
            if (!network_name) {
                fprintf(stderr, "heat: resolve requires --network\n");
                return 2;
            }
            return heat_run_resolve(&fixture, network_name, tick, delta, budget_max, inactive);
        }
        if (strcmp(cmd, "collapse") == 0) {
            const char* network_name = heat_find_arg(argc, argv, "--network");
            if (!network_name) {
                fprintf(stderr, "heat: collapse requires --network\n");
                return 2;
            }
            return heat_run_collapse(&fixture, network_name);
        }
    }

    heat_usage();
    return 2;
}
