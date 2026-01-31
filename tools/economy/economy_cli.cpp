/*
FILE: tools/economy/economy_cli.cpp
MODULE: Dominium
PURPOSE: Economy fixture CLI for deterministic logistics and market checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/rng_model.h"
#include "domino/world/economy_fields.h"

#define ECON_FIXTURE_HEADER "DOMINIUM_ECONOMY_FIXTURE_V1"

#define ECON_VALIDATE_HEADER "DOMINIUM_ECONOMY_VALIDATE_V1"
#define ECON_INSPECT_HEADER "DOMINIUM_ECONOMY_INSPECT_V1"
#define ECON_RESOLVE_HEADER "DOMINIUM_ECONOMY_RESOLVE_V1"
#define ECON_COLLAPSE_HEADER "DOMINIUM_ECONOMY_COLLAPSE_V1"

#define ECON_PROVIDER_CHAIN \
    "containers->storages->transports->jobs->markets->offers->bids->transactions"

#define ECON_LINE_MAX 512u

typedef struct economy_fixture {
    char fixture_id[96];
    dom_econ_surface_desc econ_desc;
    dom_domain_policy policy;
    u32 policy_set;
    char container_names[DOM_ECON_MAX_CONTAINERS][64];
    char storage_names[DOM_ECON_MAX_STORAGES][64];
    char transport_names[DOM_ECON_MAX_TRANSPORTS][64];
    char job_names[DOM_ECON_MAX_JOBS][64];
    char market_names[DOM_ECON_MAX_MARKETS][64];
    char offer_names[DOM_ECON_MAX_OFFERS][64];
    char bid_names[DOM_ECON_MAX_BIDS][64];
    char transaction_names[DOM_ECON_MAX_TRANSACTIONS][64];
    char region_names[DOM_ECON_MAX_REGIONS][64];
    u32 region_ids[DOM_ECON_MAX_REGIONS];
    u32 region_count;
} economy_fixture;

static u64 economy_hash_u64(u64 h, u64 v)
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

static u64 economy_hash_u32(u64 h, u32 v)
{
    return economy_hash_u64(h, (u64)v);
}

static u64 economy_hash_q16(u64 h, q16_16 v)
{
    return economy_hash_u64(h, (u64)(u32)v);
}

static u64 economy_hash_q48(u64 h, q48_16 v)
{
    return economy_hash_u64(h, (u64)v);
}

static char* economy_trim(char* text)
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

static int economy_parse_u32(const char* text, u32* out_value)
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

static int economy_parse_u64(const char* text, u64* out_value)
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

static int economy_parse_q16(const char* text, q16_16* out_value)
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

static int economy_parse_q48(const char* text, q48_16* out_value)
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

static int economy_parse_indexed_key(const char* key,
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

static u32 economy_job_type_from_text(const char* text)
{
    if (!text) {
        return DOM_ECON_JOB_UNSET;
    }
    if (strcmp(text, "move") == 0) return DOM_ECON_JOB_MOVE;
    if (strcmp(text, "store") == 0) return DOM_ECON_JOB_STORE;
    if (strcmp(text, "maintain") == 0) return DOM_ECON_JOB_MAINTAIN;
    if (strcmp(text, "transform") == 0) return DOM_ECON_JOB_TRANSFORM;
    return DOM_ECON_JOB_UNSET;
}

static void economy_fixture_init(economy_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_econ_surface_desc_init(&fixture->econ_desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->policy_set = 0u;
    fixture->region_count = 0u;
    strncpy(fixture->fixture_id, "economy.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
}

static void economy_fixture_register_region(economy_fixture* fixture,
                                            const char* name,
                                            u32 id)
{
    if (!fixture || !name || !*name || id == 0u) {
        return;
    }
    for (u32 i = 0u; i < fixture->region_count; ++i) {
        if (fixture->region_ids[i] == id) {
            return;
        }
    }
    if (fixture->region_count >= DOM_ECON_MAX_REGIONS) {
        return;
    }
    fixture->region_ids[fixture->region_count] = id;
    strncpy(fixture->region_names[fixture->region_count], name,
            sizeof(fixture->region_names[fixture->region_count]) - 1);
    fixture->region_names[fixture->region_count][sizeof(fixture->region_names[fixture->region_count]) - 1] = '\0';
    fixture->region_count += 1u;
}

static int economy_fixture_apply_container(economy_fixture* fixture,
                                           u32 index,
                                           const char* suffix,
                                           const char* value)
{
    dom_econ_container_desc* container;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_ECON_MAX_CONTAINERS) {
        return 0;
    }
    if (fixture->econ_desc.container_count <= index) {
        fixture->econ_desc.container_count = index + 1u;
    }
    container = &fixture->econ_desc.containers[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->container_names[index], value,
                sizeof(fixture->container_names[index]) - 1);
        fixture->container_names[index][sizeof(fixture->container_names[index]) - 1] = '\0';
        container->container_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "capacity") == 0) {
        return economy_parse_q48(value, &container->capacity);
    }
    if (strcmp(suffix, "contents") == 0) {
        return economy_parse_q48(value, &container->contents_amount);
    }
    if (strcmp(suffix, "integrity") == 0) {
        return economy_parse_q16(value, &container->integrity);
    }
    if (strcmp(suffix, "owner") == 0) {
        container->owner_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "location") == 0) {
        container->location_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "storage") == 0) {
        container->storage_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        container->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        container->region_id = region_id;
        economy_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return economy_parse_u32(value, &container->flags);
    }
    return 0;
}

static int economy_fixture_apply_storage(economy_fixture* fixture,
                                         u32 index,
                                         const char* suffix,
                                         const char* value)
{
    dom_econ_storage_desc* storage;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_ECON_MAX_STORAGES) {
        return 0;
    }
    if (fixture->econ_desc.storage_count <= index) {
        fixture->econ_desc.storage_count = index + 1u;
    }
    storage = &fixture->econ_desc.storages[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->storage_names[index], value,
                sizeof(fixture->storage_names[index]) - 1);
        fixture->storage_names[index][sizeof(fixture->storage_names[index]) - 1] = '\0';
        storage->storage_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "location") == 0) {
        storage->location_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "capacity") == 0) {
        return economy_parse_q48(value, &storage->capacity);
    }
    if (strcmp(suffix, "stored") == 0) {
        return economy_parse_q48(value, &storage->stored_amount);
    }
    if (strcmp(suffix, "decay_rate") == 0) {
        return economy_parse_q16(value, &storage->decay_rate);
    }
    if (strcmp(suffix, "integrity") == 0) {
        return economy_parse_q16(value, &storage->integrity);
    }
    if (strcmp(suffix, "risk_profile") == 0) {
        storage->risk_profile_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        storage->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        storage->region_id = region_id;
        economy_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return economy_parse_u32(value, &storage->flags);
    }
    return 0;
}

static int economy_fixture_apply_transport(economy_fixture* fixture,
                                           u32 index,
                                           const char* suffix,
                                           const char* value)
{
    dom_econ_transport_desc* transport;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_ECON_MAX_TRANSPORTS) {
        return 0;
    }
    if (fixture->econ_desc.transport_count <= index) {
        fixture->econ_desc.transport_count = index + 1u;
    }
    transport = &fixture->econ_desc.transports[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->transport_names[index], value,
                sizeof(fixture->transport_names[index]) - 1);
        fixture->transport_names[index][sizeof(fixture->transport_names[index]) - 1] = '\0';
        transport->transport_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "vehicle") == 0) {
        transport->vehicle_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "route") == 0) {
        transport->route_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "capacity") == 0) {
        return economy_parse_q48(value, &transport->capacity);
    }
    if (strcmp(suffix, "cargo") == 0) {
        return economy_parse_q48(value, &transport->cargo_amount);
    }
    if (strcmp(suffix, "travel_cost") == 0) {
        return economy_parse_q16(value, &transport->travel_cost);
    }
    if (strcmp(suffix, "risk_modifier") == 0) {
        return economy_parse_q16(value, &transport->risk_modifier);
    }
    if (strcmp(suffix, "risk_profile") == 0) {
        transport->risk_profile_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "origin") == 0) {
        transport->origin_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "destination") == 0) {
        transport->destination_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "depart_tick") == 0) {
        return economy_parse_u64(value, &transport->departure_tick);
    }
    if (strcmp(suffix, "arrive_tick") == 0) {
        return economy_parse_u64(value, &transport->arrival_tick);
    }
    if (strcmp(suffix, "provenance") == 0) {
        transport->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        transport->region_id = region_id;
        economy_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return economy_parse_u32(value, &transport->flags);
    }
    return 0;
}

static int economy_fixture_apply_job(economy_fixture* fixture,
                                     u32 index,
                                     const char* suffix,
                                     const char* value)
{
    dom_econ_job_desc* job;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_ECON_MAX_JOBS) {
        return 0;
    }
    if (fixture->econ_desc.job_count <= index) {
        fixture->econ_desc.job_count = index + 1u;
    }
    job = &fixture->econ_desc.jobs[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->job_names[index], value,
                sizeof(fixture->job_names[index]) - 1);
        fixture->job_names[index][sizeof(fixture->job_names[index]) - 1] = '\0';
        job->job_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "type") == 0) {
        job->job_type = economy_job_type_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "task") == 0) {
        job->task_graph_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "worker") == 0) {
        job->worker_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "skill") == 0) {
        job->required_skill_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "energy_cost") == 0) {
        return economy_parse_q48(value, &job->energy_cost);
    }
    if (strcmp(suffix, "duration") == 0) {
        return economy_parse_u64(value, &job->duration_ticks);
    }
    if (strcmp(suffix, "scheduled_tick") == 0) {
        return economy_parse_u64(value, &job->scheduled_tick);
    }
    if (strcmp(suffix, "input") == 0) {
        job->input_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "output") == 0) {
        job->output_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "risk_profile") == 0) {
        job->risk_profile_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        job->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        job->region_id = region_id;
        economy_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return economy_parse_u32(value, &job->flags);
    }
    return 0;
}

static int economy_fixture_apply_market(economy_fixture* fixture,
                                        u32 index,
                                        const char* suffix,
                                        const char* value)
{
    dom_econ_market_desc* market;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_ECON_MAX_MARKETS) {
        return 0;
    }
    if (fixture->econ_desc.market_count <= index) {
        fixture->econ_desc.market_count = index + 1u;
    }
    market = &fixture->econ_desc.markets[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->market_names[index], value,
                sizeof(fixture->market_names[index]) - 1);
        fixture->market_names[index][sizeof(fixture->market_names[index]) - 1] = '\0';
        market->market_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "location") == 0) {
        market->location_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "jurisdiction") == 0) {
        market->jurisdiction_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "capacity") == 0) {
        return economy_parse_q48(value, &market->listing_capacity);
    }
    if (strcmp(suffix, "fee") == 0) {
        return economy_parse_q16(value, &market->transaction_fee);
    }
    if (strcmp(suffix, "info_delay") == 0) {
        return economy_parse_u64(value, &market->info_delay);
    }
    if (strcmp(suffix, "risk_profile") == 0) {
        market->risk_profile_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "trust_profile") == 0) {
        market->trust_profile_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "law") == 0) {
        market->law_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        market->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        market->region_id = region_id;
        economy_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return economy_parse_u32(value, &market->flags);
    }
    return 0;
}

static int economy_fixture_apply_offer(economy_fixture* fixture,
                                       u32 index,
                                       const char* suffix,
                                       const char* value)
{
    dom_econ_offer_desc* offer;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_ECON_MAX_OFFERS) {
        return 0;
    }
    if (fixture->econ_desc.offer_count <= index) {
        fixture->econ_desc.offer_count = index + 1u;
    }
    offer = &fixture->econ_desc.offers[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->offer_names[index], value,
                sizeof(fixture->offer_names[index]) - 1);
        fixture->offer_names[index][sizeof(fixture->offer_names[index]) - 1] = '\0';
        offer->offer_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "market") == 0) {
        offer->market_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "seller") == 0) {
        offer->seller_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "goods") == 0) {
        offer->goods_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "quantity") == 0) {
        return economy_parse_q48(value, &offer->quantity);
    }
    if (strcmp(suffix, "price") == 0) {
        return economy_parse_q48(value, &offer->price);
    }
    if (strcmp(suffix, "medium") == 0) {
        offer->exchange_medium_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "expiry") == 0) {
        return economy_parse_u64(value, &offer->expiry_tick);
    }
    if (strcmp(suffix, "risk_profile") == 0) {
        offer->risk_profile_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "trust_profile") == 0) {
        offer->trust_profile_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        offer->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        offer->region_id = region_id;
        economy_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return economy_parse_u32(value, &offer->flags);
    }
    return 0;
}

static int economy_fixture_apply_bid(economy_fixture* fixture,
                                     u32 index,
                                     const char* suffix,
                                     const char* value)
{
    dom_econ_bid_desc* bid;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_ECON_MAX_BIDS) {
        return 0;
    }
    if (fixture->econ_desc.bid_count <= index) {
        fixture->econ_desc.bid_count = index + 1u;
    }
    bid = &fixture->econ_desc.bids[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->bid_names[index], value,
                sizeof(fixture->bid_names[index]) - 1);
        fixture->bid_names[index][sizeof(fixture->bid_names[index]) - 1] = '\0';
        bid->bid_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "market") == 0) {
        bid->market_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "buyer") == 0) {
        bid->buyer_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "goods") == 0) {
        bid->goods_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "quantity") == 0) {
        return economy_parse_q48(value, &bid->quantity);
    }
    if (strcmp(suffix, "price") == 0) {
        return economy_parse_q48(value, &bid->price);
    }
    if (strcmp(suffix, "medium") == 0) {
        bid->exchange_medium_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "expiry") == 0) {
        return economy_parse_u64(value, &bid->expiry_tick);
    }
    if (strcmp(suffix, "risk_profile") == 0) {
        bid->risk_profile_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "trust_profile") == 0) {
        bid->trust_profile_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        bid->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        bid->region_id = region_id;
        economy_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return economy_parse_u32(value, &bid->flags);
    }
    return 0;
}

static int economy_fixture_apply_transaction(economy_fixture* fixture,
                                             u32 index,
                                             const char* suffix,
                                             const char* value)
{
    dom_econ_transaction_desc* txn;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_ECON_MAX_TRANSACTIONS) {
        return 0;
    }
    if (fixture->econ_desc.transaction_count <= index) {
        fixture->econ_desc.transaction_count = index + 1u;
    }
    txn = &fixture->econ_desc.transactions[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->transaction_names[index], value,
                sizeof(fixture->transaction_names[index]) - 1);
        fixture->transaction_names[index][sizeof(fixture->transaction_names[index]) - 1] = '\0';
        txn->transaction_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "market") == 0) {
        txn->market_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "offer") == 0) {
        txn->offer_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "bid") == 0) {
        txn->bid_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "buyer") == 0) {
        txn->buyer_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "seller") == 0) {
        txn->seller_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "goods") == 0) {
        txn->goods_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "quantity") == 0) {
        return economy_parse_q48(value, &txn->quantity);
    }
    if (strcmp(suffix, "price") == 0) {
        return economy_parse_q48(value, &txn->price);
    }
    if (strcmp(suffix, "medium") == 0) {
        txn->exchange_medium_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "transport") == 0) {
        txn->transport_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "executed_tick") == 0) {
        return economy_parse_u64(value, &txn->executed_tick);
    }
    if (strcmp(suffix, "risk_profile") == 0) {
        txn->risk_profile_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        txn->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        txn->region_id = region_id;
        economy_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return economy_parse_u32(value, &txn->flags);
    }
    return 0;
}

static int economy_fixture_apply(economy_fixture* fixture,
                                 const char* key,
                                 const char* value)
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
        return economy_parse_u64(value, &fixture->econ_desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return economy_parse_u64(value, &fixture->econ_desc.domain_id);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return economy_parse_q16(value, &fixture->econ_desc.meters_per_unit);
    }
    if (strcmp(key, "container_count") == 0) {
        return economy_parse_u32(value, &fixture->econ_desc.container_count);
    }
    if (strcmp(key, "storage_count") == 0) {
        return economy_parse_u32(value, &fixture->econ_desc.storage_count);
    }
    if (strcmp(key, "transport_count") == 0) {
        return economy_parse_u32(value, &fixture->econ_desc.transport_count);
    }
    if (strcmp(key, "job_count") == 0) {
        return economy_parse_u32(value, &fixture->econ_desc.job_count);
    }
    if (strcmp(key, "market_count") == 0) {
        return economy_parse_u32(value, &fixture->econ_desc.market_count);
    }
    if (strcmp(key, "offer_count") == 0) {
        return economy_parse_u32(value, &fixture->econ_desc.offer_count);
    }
    if (strcmp(key, "bid_count") == 0) {
        return economy_parse_u32(value, &fixture->econ_desc.bid_count);
    }
    if (strcmp(key, "transaction_count") == 0) {
        return economy_parse_u32(value, &fixture->econ_desc.transaction_count);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return economy_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return economy_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return economy_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return economy_parse_u32(value, &fixture->policy.cost_analytic);
    }
    if (economy_parse_indexed_key(key, "container_", &index, &suffix)) {
        return economy_fixture_apply_container(fixture, index, suffix, value);
    }
    if (economy_parse_indexed_key(key, "storage_", &index, &suffix)) {
        return economy_fixture_apply_storage(fixture, index, suffix, value);
    }
    if (economy_parse_indexed_key(key, "transport_", &index, &suffix)) {
        return economy_fixture_apply_transport(fixture, index, suffix, value);
    }
    if (economy_parse_indexed_key(key, "job_", &index, &suffix)) {
        return economy_fixture_apply_job(fixture, index, suffix, value);
    }
    if (economy_parse_indexed_key(key, "market_", &index, &suffix)) {
        return economy_fixture_apply_market(fixture, index, suffix, value);
    }
    if (economy_parse_indexed_key(key, "offer_", &index, &suffix)) {
        return economy_fixture_apply_offer(fixture, index, suffix, value);
    }
    if (economy_parse_indexed_key(key, "bid_", &index, &suffix)) {
        return economy_fixture_apply_bid(fixture, index, suffix, value);
    }
    if (economy_parse_indexed_key(key, "transaction_", &index, &suffix)) {
        return economy_fixture_apply_transaction(fixture, index, suffix, value);
    }
    return 0;
}

static int economy_fixture_load(const char* path, economy_fixture* fixture)
{
    char line[ECON_LINE_MAX];
    FILE* fp;
    u32 line_no = 0u;
    if (!path || !fixture) {
        return 0;
    }
    fp = fopen(path, "rb");
    if (!fp) {
        return 0;
    }
    economy_fixture_init(fixture);
    while (fgets(line, (int)sizeof(line), fp)) {
        char* key;
        char* value;
        char* sep;
        line_no += 1u;
        if (line_no == 1u) {
            if (strncmp(line, ECON_FIXTURE_HEADER, strlen(ECON_FIXTURE_HEADER)) != 0) {
                fclose(fp);
                return 0;
            }
            continue;
        }
        key = economy_trim(line);
        if (!*key || *key == '#') {
            continue;
        }
        sep = strchr(key, '=');
        if (!sep) {
            fclose(fp);
            return 0;
        }
        *sep = '\0';
        value = economy_trim(sep + 1);
        key = economy_trim(key);
        if (!economy_fixture_apply(fixture, key, value)) {
            fclose(fp);
            return 0;
        }
    }
    fclose(fp);
    return 1;
}

static const char* economy_lookup_container_name(const economy_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return "unknown";
    }
    for (u32 i = 0u; i < fixture->econ_desc.container_count; ++i) {
        if (fixture->econ_desc.containers[i].container_id == id) {
            return fixture->container_names[i];
        }
    }
    return "unknown";
}

static const char* economy_lookup_storage_name(const economy_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return "unknown";
    }
    for (u32 i = 0u; i < fixture->econ_desc.storage_count; ++i) {
        if (fixture->econ_desc.storages[i].storage_id == id) {
            return fixture->storage_names[i];
        }
    }
    return "unknown";
}

static const char* economy_lookup_transport_name(const economy_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return "unknown";
    }
    for (u32 i = 0u; i < fixture->econ_desc.transport_count; ++i) {
        if (fixture->econ_desc.transports[i].transport_id == id) {
            return fixture->transport_names[i];
        }
    }
    return "unknown";
}

static const char* economy_lookup_job_name(const economy_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return "unknown";
    }
    for (u32 i = 0u; i < fixture->econ_desc.job_count; ++i) {
        if (fixture->econ_desc.jobs[i].job_id == id) {
            return fixture->job_names[i];
        }
    }
    return "unknown";
}

static const char* economy_lookup_market_name(const economy_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return "unknown";
    }
    for (u32 i = 0u; i < fixture->econ_desc.market_count; ++i) {
        if (fixture->econ_desc.markets[i].market_id == id) {
            return fixture->market_names[i];
        }
    }
    return "unknown";
}

static const char* economy_lookup_offer_name(const economy_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return "unknown";
    }
    for (u32 i = 0u; i < fixture->econ_desc.offer_count; ++i) {
        if (fixture->econ_desc.offers[i].offer_id == id) {
            return fixture->offer_names[i];
        }
    }
    return "unknown";
}

static const char* economy_lookup_bid_name(const economy_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return "unknown";
    }
    for (u32 i = 0u; i < fixture->econ_desc.bid_count; ++i) {
        if (fixture->econ_desc.bids[i].bid_id == id) {
            return fixture->bid_names[i];
        }
    }
    return "unknown";
}

static const char* economy_lookup_transaction_name(const economy_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return "unknown";
    }
    for (u32 i = 0u; i < fixture->econ_desc.transaction_count; ++i) {
        if (fixture->econ_desc.transactions[i].transaction_id == id) {
            return fixture->transaction_names[i];
        }
    }
    return "unknown";
}

static u32 economy_find_region_id(const economy_fixture* fixture, const char* name)
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

static const char* economy_find_arg(int argc, char** argv, const char* name)
{
    if (!argv || !name) {
        return 0;
    }
    for (int i = 1; i < argc - 1; ++i) {
        if (strcmp(argv[i], name) == 0) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 economy_find_arg_u32(int argc, char** argv, const char* name, u32 fallback)
{
    const char* value = economy_find_arg(argc, argv, name);
    u32 result = fallback;
    if (value && economy_parse_u32(value, &result)) {
        return result;
    }
    return fallback;
}

static u64 economy_find_arg_u64(int argc, char** argv, const char* name, u64 fallback)
{
    const char* value = economy_find_arg(argc, argv, name);
    u64 result = fallback;
    if (value && economy_parse_u64(value, &result)) {
        return result;
    }
    return fallback;
}

static int economy_run_validate(const economy_fixture* fixture)
{
    u32 ok = 1u;
    if (!fixture) {
        return 1;
    }
    if (fixture->econ_desc.container_count > DOM_ECON_MAX_CONTAINERS) ok = 0u;
    if (fixture->econ_desc.storage_count > DOM_ECON_MAX_STORAGES) ok = 0u;
    if (fixture->econ_desc.transport_count > DOM_ECON_MAX_TRANSPORTS) ok = 0u;
    if (fixture->econ_desc.job_count > DOM_ECON_MAX_JOBS) ok = 0u;
    if (fixture->econ_desc.market_count > DOM_ECON_MAX_MARKETS) ok = 0u;
    if (fixture->econ_desc.offer_count > DOM_ECON_MAX_OFFERS) ok = 0u;
    if (fixture->econ_desc.bid_count > DOM_ECON_MAX_BIDS) ok = 0u;
    if (fixture->econ_desc.transaction_count > DOM_ECON_MAX_TRANSACTIONS) ok = 0u;

    printf("%s\n", ECON_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", ECON_PROVIDER_CHAIN);
    printf("container_count=%u\n", (unsigned int)fixture->econ_desc.container_count);
    printf("storage_count=%u\n", (unsigned int)fixture->econ_desc.storage_count);
    printf("transport_count=%u\n", (unsigned int)fixture->econ_desc.transport_count);
    printf("job_count=%u\n", (unsigned int)fixture->econ_desc.job_count);
    printf("market_count=%u\n", (unsigned int)fixture->econ_desc.market_count);
    printf("offer_count=%u\n", (unsigned int)fixture->econ_desc.offer_count);
    printf("bid_count=%u\n", (unsigned int)fixture->econ_desc.bid_count);
    printf("transaction_count=%u\n", (unsigned int)fixture->econ_desc.transaction_count);
    printf("ok=%u\n", (unsigned int)ok);
    return ok ? 0 : 1;
}

static int economy_run_inspect_container(const economy_fixture* fixture,
                                         const char* name,
                                         u32 budget_max)
{
    dom_econ_domain domain;
    dom_domain_budget budget;
    dom_econ_container_sample sample;
    u32 container_id;
    if (!name) {
        return 1;
    }
    container_id = d_rng_hash_str32(name);
    dom_econ_domain_init(&domain, &fixture->econ_desc);
    if (fixture->policy_set) {
        dom_econ_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_econ_container_query(&domain, container_id, &budget, &sample);

    printf("%s\n", ECON_INSPECT_HEADER);
    printf("entity=container\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", ECON_PROVIDER_CHAIN);
    printf("container_id=%u\n", (unsigned int)sample.container_id);
    printf("container_id_str=%s\n", economy_lookup_container_name(fixture, sample.container_id));
    printf("capacity_q48=%lld\n", (long long)sample.capacity);
    printf("contents_amount_q48=%lld\n", (long long)sample.contents_amount);
    printf("integrity_q16=%d\n", (int)sample.integrity);
    printf("owner_ref_id=%u\n", (unsigned int)sample.owner_ref_id);
    printf("location_ref_id=%u\n", (unsigned int)sample.location_ref_id);
    printf("storage_ref_id=%u\n", (unsigned int)sample.storage_ref_id);
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

    dom_econ_domain_free(&domain);
    return 0;
}

static int economy_run_inspect_storage(const economy_fixture* fixture,
                                       const char* name,
                                       u32 budget_max)
{
    dom_econ_domain domain;
    dom_domain_budget budget;
    dom_econ_storage_sample sample;
    u32 storage_id;
    if (!name) {
        return 1;
    }
    storage_id = d_rng_hash_str32(name);
    dom_econ_domain_init(&domain, &fixture->econ_desc);
    if (fixture->policy_set) {
        dom_econ_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_econ_storage_query(&domain, storage_id, &budget, &sample);

    printf("%s\n", ECON_INSPECT_HEADER);
    printf("entity=storage\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", ECON_PROVIDER_CHAIN);
    printf("storage_id=%u\n", (unsigned int)sample.storage_id);
    printf("storage_id_str=%s\n", economy_lookup_storage_name(fixture, sample.storage_id));
    printf("location_ref_id=%u\n", (unsigned int)sample.location_ref_id);
    printf("capacity_q48=%lld\n", (long long)sample.capacity);
    printf("stored_amount_q48=%lld\n", (long long)sample.stored_amount);
    printf("decay_rate_q16=%d\n", (int)sample.decay_rate);
    printf("integrity_q16=%d\n", (int)sample.integrity);
    printf("risk_profile_id=%u\n", (unsigned int)sample.risk_profile_id);
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

    dom_econ_domain_free(&domain);
    return 0;
}

static int economy_run_inspect_transport(const economy_fixture* fixture,
                                         const char* name,
                                         u32 budget_max)
{
    dom_econ_domain domain;
    dom_domain_budget budget;
    dom_econ_transport_sample sample;
    u32 transport_id;
    if (!name) {
        return 1;
    }
    transport_id = d_rng_hash_str32(name);
    dom_econ_domain_init(&domain, &fixture->econ_desc);
    if (fixture->policy_set) {
        dom_econ_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_econ_transport_query(&domain, transport_id, &budget, &sample);

    printf("%s\n", ECON_INSPECT_HEADER);
    printf("entity=transport\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", ECON_PROVIDER_CHAIN);
    printf("transport_id=%u\n", (unsigned int)sample.transport_id);
    printf("transport_id_str=%s\n", economy_lookup_transport_name(fixture, sample.transport_id));
    printf("vehicle_ref_id=%u\n", (unsigned int)sample.vehicle_ref_id);
    printf("route_ref_id=%u\n", (unsigned int)sample.route_ref_id);
    printf("capacity_q48=%lld\n", (long long)sample.capacity);
    printf("cargo_amount_q48=%lld\n", (long long)sample.cargo_amount);
    printf("travel_cost_q16=%d\n", (int)sample.travel_cost);
    printf("risk_modifier_q16=%d\n", (int)sample.risk_modifier);
    printf("risk_profile_id=%u\n", (unsigned int)sample.risk_profile_id);
    printf("origin_ref_id=%u\n", (unsigned int)sample.origin_ref_id);
    printf("destination_ref_id=%u\n", (unsigned int)sample.destination_ref_id);
    printf("departure_tick=%llu\n", (unsigned long long)sample.departure_tick);
    printf("arrival_tick=%llu\n", (unsigned long long)sample.arrival_tick);
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

    dom_econ_domain_free(&domain);
    return 0;
}

static int economy_run_inspect_job(const economy_fixture* fixture,
                                   const char* name,
                                   u32 budget_max)
{
    dom_econ_domain domain;
    dom_domain_budget budget;
    dom_econ_job_sample sample;
    u32 job_id;
    if (!name) {
        return 1;
    }
    job_id = d_rng_hash_str32(name);
    dom_econ_domain_init(&domain, &fixture->econ_desc);
    if (fixture->policy_set) {
        dom_econ_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_econ_job_query(&domain, job_id, &budget, &sample);

    printf("%s\n", ECON_INSPECT_HEADER);
    printf("entity=job\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", ECON_PROVIDER_CHAIN);
    printf("job_id=%u\n", (unsigned int)sample.job_id);
    printf("job_id_str=%s\n", economy_lookup_job_name(fixture, sample.job_id));
    printf("job_type=%u\n", (unsigned int)sample.job_type);
    printf("task_graph_ref_id=%u\n", (unsigned int)sample.task_graph_ref_id);
    printf("worker_ref_id=%u\n", (unsigned int)sample.worker_ref_id);
    printf("required_skill_ref_id=%u\n", (unsigned int)sample.required_skill_ref_id);
    printf("energy_cost_q48=%lld\n", (long long)sample.energy_cost);
    printf("duration_ticks=%llu\n", (unsigned long long)sample.duration_ticks);
    printf("scheduled_tick=%llu\n", (unsigned long long)sample.scheduled_tick);
    printf("input_ref_id=%u\n", (unsigned int)sample.input_ref_id);
    printf("output_ref_id=%u\n", (unsigned int)sample.output_ref_id);
    printf("risk_profile_id=%u\n", (unsigned int)sample.risk_profile_id);
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

    dom_econ_domain_free(&domain);
    return 0;
}

static int economy_run_inspect_market(const economy_fixture* fixture,
                                      const char* name,
                                      u32 budget_max)
{
    dom_econ_domain domain;
    dom_domain_budget budget;
    dom_econ_market_sample sample;
    u32 market_id;
    if (!name) {
        return 1;
    }
    market_id = d_rng_hash_str32(name);
    dom_econ_domain_init(&domain, &fixture->econ_desc);
    if (fixture->policy_set) {
        dom_econ_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_econ_market_query(&domain, market_id, &budget, &sample);

    printf("%s\n", ECON_INSPECT_HEADER);
    printf("entity=market\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", ECON_PROVIDER_CHAIN);
    printf("market_id=%u\n", (unsigned int)sample.market_id);
    printf("market_id_str=%s\n", economy_lookup_market_name(fixture, sample.market_id));
    printf("location_ref_id=%u\n", (unsigned int)sample.location_ref_id);
    printf("jurisdiction_ref_id=%u\n", (unsigned int)sample.jurisdiction_ref_id);
    printf("listing_capacity_q48=%lld\n", (long long)sample.listing_capacity);
    printf("transaction_fee_q16=%d\n", (int)sample.transaction_fee);
    printf("info_delay=%llu\n", (unsigned long long)sample.info_delay);
    printf("risk_profile_id=%u\n", (unsigned int)sample.risk_profile_id);
    printf("trust_profile_id=%u\n", (unsigned int)sample.trust_profile_id);
    printf("law_ref_id=%u\n", (unsigned int)sample.law_ref_id);
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

    dom_econ_domain_free(&domain);
    return 0;
}

static int economy_run_inspect_offer(const economy_fixture* fixture,
                                     const char* name,
                                     u32 budget_max)
{
    dom_econ_domain domain;
    dom_domain_budget budget;
    dom_econ_offer_sample sample;
    u32 offer_id;
    if (!name) {
        return 1;
    }
    offer_id = d_rng_hash_str32(name);
    dom_econ_domain_init(&domain, &fixture->econ_desc);
    if (fixture->policy_set) {
        dom_econ_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_econ_offer_query(&domain, offer_id, &budget, &sample);

    printf("%s\n", ECON_INSPECT_HEADER);
    printf("entity=offer\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", ECON_PROVIDER_CHAIN);
    printf("offer_id=%u\n", (unsigned int)sample.offer_id);
    printf("offer_id_str=%s\n", economy_lookup_offer_name(fixture, sample.offer_id));
    printf("market_id=%u\n", (unsigned int)sample.market_id);
    printf("seller_ref_id=%u\n", (unsigned int)sample.seller_ref_id);
    printf("goods_ref_id=%u\n", (unsigned int)sample.goods_ref_id);
    printf("quantity_q48=%lld\n", (long long)sample.quantity);
    printf("price_q48=%lld\n", (long long)sample.price);
    printf("exchange_medium_ref_id=%u\n", (unsigned int)sample.exchange_medium_ref_id);
    printf("expiry_tick=%llu\n", (unsigned long long)sample.expiry_tick);
    printf("risk_profile_id=%u\n", (unsigned int)sample.risk_profile_id);
    printf("trust_profile_id=%u\n", (unsigned int)sample.trust_profile_id);
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

    dom_econ_domain_free(&domain);
    return 0;
}

static int economy_run_inspect_bid(const economy_fixture* fixture,
                                   const char* name,
                                   u32 budget_max)
{
    dom_econ_domain domain;
    dom_domain_budget budget;
    dom_econ_bid_sample sample;
    u32 bid_id;
    if (!name) {
        return 1;
    }
    bid_id = d_rng_hash_str32(name);
    dom_econ_domain_init(&domain, &fixture->econ_desc);
    if (fixture->policy_set) {
        dom_econ_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_econ_bid_query(&domain, bid_id, &budget, &sample);

    printf("%s\n", ECON_INSPECT_HEADER);
    printf("entity=bid\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", ECON_PROVIDER_CHAIN);
    printf("bid_id=%u\n", (unsigned int)sample.bid_id);
    printf("bid_id_str=%s\n", economy_lookup_bid_name(fixture, sample.bid_id));
    printf("market_id=%u\n", (unsigned int)sample.market_id);
    printf("buyer_ref_id=%u\n", (unsigned int)sample.buyer_ref_id);
    printf("goods_ref_id=%u\n", (unsigned int)sample.goods_ref_id);
    printf("quantity_q48=%lld\n", (long long)sample.quantity);
    printf("price_q48=%lld\n", (long long)sample.price);
    printf("exchange_medium_ref_id=%u\n", (unsigned int)sample.exchange_medium_ref_id);
    printf("expiry_tick=%llu\n", (unsigned long long)sample.expiry_tick);
    printf("risk_profile_id=%u\n", (unsigned int)sample.risk_profile_id);
    printf("trust_profile_id=%u\n", (unsigned int)sample.trust_profile_id);
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

    dom_econ_domain_free(&domain);
    return 0;
}

static int economy_run_inspect_transaction(const economy_fixture* fixture,
                                           const char* name,
                                           u32 budget_max)
{
    dom_econ_domain domain;
    dom_domain_budget budget;
    dom_econ_transaction_sample sample;
    u32 transaction_id;
    if (!name) {
        return 1;
    }
    transaction_id = d_rng_hash_str32(name);
    dom_econ_domain_init(&domain, &fixture->econ_desc);
    if (fixture->policy_set) {
        dom_econ_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_econ_transaction_query(&domain, transaction_id, &budget, &sample);

    printf("%s\n", ECON_INSPECT_HEADER);
    printf("entity=transaction\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", ECON_PROVIDER_CHAIN);
    printf("transaction_id=%u\n", (unsigned int)sample.transaction_id);
    printf("transaction_id_str=%s\n", economy_lookup_transaction_name(fixture, sample.transaction_id));
    printf("market_id=%u\n", (unsigned int)sample.market_id);
    printf("offer_id=%u\n", (unsigned int)sample.offer_id);
    printf("bid_id=%u\n", (unsigned int)sample.bid_id);
    printf("buyer_ref_id=%u\n", (unsigned int)sample.buyer_ref_id);
    printf("seller_ref_id=%u\n", (unsigned int)sample.seller_ref_id);
    printf("goods_ref_id=%u\n", (unsigned int)sample.goods_ref_id);
    printf("quantity_q48=%lld\n", (long long)sample.quantity);
    printf("price_q48=%lld\n", (long long)sample.price);
    printf("exchange_medium_ref_id=%u\n", (unsigned int)sample.exchange_medium_ref_id);
    printf("transport_ref_id=%u\n", (unsigned int)sample.transport_ref_id);
    printf("executed_tick=%llu\n", (unsigned long long)sample.executed_tick);
    printf("risk_profile_id=%u\n", (unsigned int)sample.risk_profile_id);
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

    dom_econ_domain_free(&domain);
    return 0;
}

static int economy_run_inspect_region(const economy_fixture* fixture,
                                      const char* region_name,
                                      u32 budget_max)
{
    dom_econ_domain domain;
    dom_domain_budget budget;
    dom_econ_region_sample sample;
    u32 region_id = economy_find_region_id(fixture, region_name);

    dom_econ_domain_init(&domain, &fixture->econ_desc);
    if (fixture->policy_set) {
        dom_econ_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_econ_region_query(&domain, region_id, &budget, &sample);

    printf("%s\n", ECON_INSPECT_HEADER);
    printf("entity=region\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", ECON_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("container_count=%u\n", (unsigned int)sample.container_count);
    printf("storage_count=%u\n", (unsigned int)sample.storage_count);
    printf("transport_count=%u\n", (unsigned int)sample.transport_count);
    printf("job_count=%u\n", (unsigned int)sample.job_count);
    printf("market_count=%u\n", (unsigned int)sample.market_count);
    printf("offer_count=%u\n", (unsigned int)sample.offer_count);
    printf("bid_count=%u\n", (unsigned int)sample.bid_count);
    printf("transaction_count=%u\n", (unsigned int)sample.transaction_count);
    printf("goods_total_q48=%lld\n", (long long)sample.goods_total);
    printf("price_avg_q48=%lld\n", (long long)sample.price_avg);
    printf("transaction_volume_total_q48=%lld\n", (long long)sample.transaction_volume_total);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_econ_domain_free(&domain);
    return 0;
}

static int economy_run_resolve(const economy_fixture* fixture,
                               const char* region_name,
                               u64 tick,
                               u64 tick_delta,
                               u32 budget_max,
                               u32 inactive_count)
{
    dom_econ_domain domain;
    dom_econ_domain* inactive = 0;
    dom_domain_budget budget;
    dom_econ_resolve_result result;
    u32 region_id = economy_find_region_id(fixture, region_name);
    u64 hash = 14695981039346656037ULL;

    dom_econ_domain_init(&domain, &fixture->econ_desc);
    if (fixture->policy_set) {
        dom_econ_domain_set_policy(&domain, &fixture->policy);
    }

    if (inactive_count > 0u) {
        inactive = (dom_econ_domain*)malloc(sizeof(dom_econ_domain) * inactive_count);
        if (inactive) {
            for (u32 i = 0u; i < inactive_count; ++i) {
                economy_fixture temp = *fixture;
                temp.econ_desc.domain_id = fixture->econ_desc.domain_id + (u64)(i + 1u);
                dom_econ_domain_init(&inactive[i], &temp.econ_desc);
                dom_econ_domain_set_state(&inactive[i],
                                          DOM_DOMAIN_EXISTENCE_DECLARED,
                                          DOM_DOMAIN_ARCHIVAL_LIVE);
            }
        }
    }

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_econ_resolve(&domain, region_id, tick, tick_delta, &budget, &result);

    for (u32 i = 0u; i < domain.container_count; ++i) {
        hash = economy_hash_u32(hash, domain.containers[i].container_id);
        hash = economy_hash_q48(hash, domain.containers[i].contents_amount);
        hash = economy_hash_u32(hash, domain.containers[i].flags);
    }
    for (u32 i = 0u; i < domain.transport_count; ++i) {
        hash = economy_hash_u32(hash, domain.transports[i].transport_id);
        hash = economy_hash_q48(hash, domain.transports[i].cargo_amount);
        hash = economy_hash_u32(hash, domain.transports[i].flags);
    }
    for (u32 i = 0u; i < domain.offer_count; ++i) {
        hash = economy_hash_u32(hash, domain.offers[i].offer_id);
        hash = economy_hash_q48(hash, domain.offers[i].price);
        hash = economy_hash_u32(hash, domain.offers[i].flags);
    }
    for (u32 i = 0u; i < domain.bid_count; ++i) {
        hash = economy_hash_u32(hash, domain.bids[i].bid_id);
        hash = economy_hash_q48(hash, domain.bids[i].price);
        hash = economy_hash_u32(hash, domain.bids[i].flags);
    }
    for (u32 i = 0u; i < domain.transaction_count; ++i) {
        hash = economy_hash_u32(hash, domain.transactions[i].transaction_id);
        hash = economy_hash_q48(hash, domain.transactions[i].price);
        hash = economy_hash_u32(hash, domain.transactions[i].flags);
    }

    printf("%s\n", ECON_RESOLVE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", ECON_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("container_count=%u\n", (unsigned int)result.container_count);
    printf("storage_count=%u\n", (unsigned int)result.storage_count);
    printf("transport_count=%u\n", (unsigned int)result.transport_count);
    printf("transport_arrived_count=%u\n", (unsigned int)result.transport_arrived_count);
    printf("job_count=%u\n", (unsigned int)result.job_count);
    printf("job_completed_count=%u\n", (unsigned int)result.job_completed_count);
    printf("market_count=%u\n", (unsigned int)result.market_count);
    printf("offer_count=%u\n", (unsigned int)result.offer_count);
    printf("bid_count=%u\n", (unsigned int)result.bid_count);
    printf("transaction_count=%u\n", (unsigned int)result.transaction_count);
    printf("transaction_settled_count=%u\n", (unsigned int)result.transaction_settled_count);
    printf("goods_total_q48=%lld\n", (long long)result.goods_total);
    printf("price_avg_q48=%lld\n", (long long)result.price_avg);
    printf("transaction_volume_total_q48=%lld\n", (long long)result.transaction_volume_total);
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);
    printf("resolve_hash=%llu\n", (unsigned long long)hash);

    dom_econ_domain_free(&domain);
    if (inactive) {
        for (u32 i = 0u; i < inactive_count; ++i) {
            dom_econ_domain_free(&inactive[i]);
        }
        free(inactive);
    }
    return 0;
}

static int economy_run_collapse(const economy_fixture* fixture, const char* region_name)
{
    dom_econ_domain domain;
    u32 region_id = economy_find_region_id(fixture, region_name);
    u32 count_before;
    u32 count_after;

    dom_econ_domain_init(&domain, &fixture->econ_desc);
    if (fixture->policy_set) {
        dom_econ_domain_set_policy(&domain, &fixture->policy);
    }
    count_before = dom_econ_domain_capsule_count(&domain);
    (void)dom_econ_domain_collapse_region(&domain, region_id);
    count_after = dom_econ_domain_capsule_count(&domain);

    printf("%s\n", ECON_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", ECON_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);

    dom_econ_domain_free(&domain);
    return 0;
}

static void economy_usage(void)
{
    printf("dom_tool_economy commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --container <id> [--budget N]\n");
    printf("  inspect --fixture <path> --storage <id> [--budget N]\n");
    printf("  inspect --fixture <path> --transport <id> [--budget N]\n");
    printf("  inspect --fixture <path> --job <id> [--budget N]\n");
    printf("  inspect --fixture <path> --market <id> [--budget N]\n");
    printf("  inspect --fixture <path> --offer <id> [--budget N]\n");
    printf("  inspect --fixture <path> --bid <id> [--budget N]\n");
    printf("  inspect --fixture <path> --transaction <id> [--budget N]\n");
    printf("  inspect --fixture <path> --region <id> [--budget N]\n");
    printf("  resolve --fixture <path> --region <id> [--tick N] [--delta N] [--budget N] [--inactive N]\n");
    printf("  collapse --fixture <path> --region <id>\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        economy_usage();
        return 2;
    }
    cmd = argv[1];
    if (strcmp(cmd, "validate") == 0 ||
        strcmp(cmd, "inspect") == 0 ||
        strcmp(cmd, "resolve") == 0 ||
        strcmp(cmd, "collapse") == 0) {
        const char* fixture_path = economy_find_arg(argc, argv, "--fixture");
        economy_fixture fixture;
        if (!fixture_path || !economy_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "economy: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return economy_run_validate(&fixture);
        }
        if (strcmp(cmd, "inspect") == 0) {
            const char* container_name = economy_find_arg(argc, argv, "--container");
            const char* storage_name = economy_find_arg(argc, argv, "--storage");
            const char* transport_name = economy_find_arg(argc, argv, "--transport");
            const char* job_name = economy_find_arg(argc, argv, "--job");
            const char* market_name = economy_find_arg(argc, argv, "--market");
            const char* offer_name = economy_find_arg(argc, argv, "--offer");
            const char* bid_name = economy_find_arg(argc, argv, "--bid");
            const char* transaction_name = economy_find_arg(argc, argv, "--transaction");
            const char* region_name = economy_find_arg(argc, argv, "--region");
            u32 budget_max = economy_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_full);
            if (container_name) {
                return economy_run_inspect_container(&fixture, container_name, budget_max);
            }
            if (storage_name) {
                return economy_run_inspect_storage(&fixture, storage_name, budget_max);
            }
            if (transport_name) {
                return economy_run_inspect_transport(&fixture, transport_name, budget_max);
            }
            if (job_name) {
                return economy_run_inspect_job(&fixture, job_name, budget_max);
            }
            if (market_name) {
                return economy_run_inspect_market(&fixture, market_name, budget_max);
            }
            if (offer_name) {
                return economy_run_inspect_offer(&fixture, offer_name, budget_max);
            }
            if (bid_name) {
                return economy_run_inspect_bid(&fixture, bid_name, budget_max);
            }
            if (transaction_name) {
                return economy_run_inspect_transaction(&fixture, transaction_name, budget_max);
            }
            if (region_name) {
                return economy_run_inspect_region(&fixture, region_name, budget_max);
            }
            fprintf(stderr,
                    "economy: inspect requires --container, --storage, --transport, --job, --market, --offer, --bid, --transaction, or --region\n");
            return 2;
        }
        if (strcmp(cmd, "resolve") == 0) {
            const char* region_name = economy_find_arg(argc, argv, "--region");
            u64 tick = economy_find_arg_u64(argc, argv, "--tick", 0u);
            u64 delta = economy_find_arg_u64(argc, argv, "--delta", 1u);
            u32 budget_max = economy_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_medium);
            u32 inactive = economy_find_arg_u32(argc, argv, "--inactive", 0u);
            if (!region_name) {
                fprintf(stderr, "economy: resolve requires --region\n");
                return 2;
            }
            return economy_run_resolve(&fixture, region_name, tick, delta, budget_max, inactive);
        }
        if (strcmp(cmd, "collapse") == 0) {
            const char* region_name = economy_find_arg(argc, argv, "--region");
            if (!region_name) {
                fprintf(stderr, "economy: collapse requires --region\n");
                return 2;
            }
            return economy_run_collapse(&fixture, region_name);
        }
    }

    economy_usage();
    return 2;
}
