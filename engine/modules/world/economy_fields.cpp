/*
FILE: source/domino/world/economy_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/economy_fields
RESPONSIBILITY: Implements deterministic logistics and market resolution.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/economy_fields.h"

#include "domino/core/fixed_math.h"

#include <string.h>

#define DOM_ECON_RESOLVE_COST_BASE 1u
#define DOM_ECON_PRICE_RATIO_HALF_Q16 ((q16_16)0x00008000)
#define DOM_ECON_PRICE_RATIO_DOUBLE_Q16 ((q16_16)0x00020000)
#define DOM_ECON_RISK_THRESHOLD_Q16 ((q16_16)0x00008000)

static q16_16 dom_econ_clamp_ratio(q16_16 value)
{
    if (value < 0) {
        return 0;
    }
    if (value > DOM_ECON_RATIO_ONE_Q16) {
        return DOM_ECON_RATIO_ONE_Q16;
    }
    return value;
}

static q16_16 dom_econ_ratio_from_counts(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << Q16_16_FRAC_BITS) / total);
}

static u32 dom_econ_price_bin(q16_16 ratio)
{
    q16_16 clamped = dom_econ_clamp_ratio(ratio);
    if (clamped <= DOM_ECON_PRICE_RATIO_HALF_Q16) {
        return 0u;
    }
    if (clamped <= DOM_ECON_RATIO_ONE_Q16) {
        return 1u;
    }
    if (clamped <= DOM_ECON_PRICE_RATIO_DOUBLE_Q16) {
        return 2u;
    }
    return 3u;
}

static q16_16 dom_econ_price_ratio(q48_16 price, q48_16 avg)
{
    if (avg <= 0) {
        return 0;
    }
    return d_q16_16_from_q48_16(d_q48_16_div(price, avg));
}

static void dom_econ_container_init(dom_econ_container* container)
{
    if (!container) {
        return;
    }
    memset(container, 0, sizeof(*container));
}

static void dom_econ_storage_init(dom_econ_storage* storage)
{
    if (!storage) {
        return;
    }
    memset(storage, 0, sizeof(*storage));
}

static void dom_econ_transport_init(dom_econ_transport* transport)
{
    if (!transport) {
        return;
    }
    memset(transport, 0, sizeof(*transport));
}

static void dom_econ_job_init(dom_econ_job* job)
{
    if (!job) {
        return;
    }
    memset(job, 0, sizeof(*job));
    job->job_type = DOM_ECON_JOB_UNSET;
}

static void dom_econ_market_init(dom_econ_market* market)
{
    if (!market) {
        return;
    }
    memset(market, 0, sizeof(*market));
}

static void dom_econ_offer_init(dom_econ_offer* offer)
{
    if (!offer) {
        return;
    }
    memset(offer, 0, sizeof(*offer));
}

static void dom_econ_bid_init(dom_econ_bid* bid)
{
    if (!bid) {
        return;
    }
    memset(bid, 0, sizeof(*bid));
}

static void dom_econ_transaction_init(dom_econ_transaction* txn)
{
    if (!txn) {
        return;
    }
    memset(txn, 0, sizeof(*txn));
}

static int dom_econ_find_container_index(const dom_econ_domain* domain, u32 container_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->container_count; ++i) {
        if (domain->containers[i].container_id == container_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_econ_find_storage_index(const dom_econ_domain* domain, u32 storage_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->storage_count; ++i) {
        if (domain->storages[i].storage_id == storage_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_econ_find_transport_index(const dom_econ_domain* domain, u32 transport_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->transport_count; ++i) {
        if (domain->transports[i].transport_id == transport_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_econ_find_job_index(const dom_econ_domain* domain, u32 job_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->job_count; ++i) {
        if (domain->jobs[i].job_id == job_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_econ_find_market_index(const dom_econ_domain* domain, u32 market_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->market_count; ++i) {
        if (domain->markets[i].market_id == market_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_econ_find_offer_index(const dom_econ_domain* domain, u32 offer_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->offer_count; ++i) {
        if (domain->offers[i].offer_id == offer_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_econ_find_bid_index(const dom_econ_domain* domain, u32 bid_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->bid_count; ++i) {
        if (domain->bids[i].bid_id == bid_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_econ_find_transaction_index(const dom_econ_domain* domain, u32 transaction_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->transaction_count; ++i) {
        if (domain->transactions[i].transaction_id == transaction_id) {
            return (int)i;
        }
    }
    return -1;
}

static d_bool dom_econ_domain_is_active(const dom_econ_domain* domain)
{
    if (!domain) {
        return D_FALSE;
    }
    if (domain->existence_state == DOM_DOMAIN_EXISTENCE_NONEXISTENT ||
        domain->existence_state == DOM_DOMAIN_EXISTENCE_DECLARED) {
        return D_FALSE;
    }
    return D_TRUE;
}

static d_bool dom_econ_region_collapsed(const dom_econ_domain* domain, u32 region_id)
{
    if (!domain || region_id == 0u) {
        return D_FALSE;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}

static const dom_econ_macro_capsule* dom_econ_find_capsule(const dom_econ_domain* domain,
                                                           u32 region_id)
{
    if (!domain) {
        return (const dom_econ_macro_capsule*)0;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            return &domain->capsules[i];
        }
    }
    return (const dom_econ_macro_capsule*)0;
}

static void dom_econ_query_meta_refused(dom_domain_query_meta* meta,
                                        u32 reason,
                                        const dom_domain_budget* budget)
{
    if (!meta) {
        return;
    }
    memset(meta, 0, sizeof(*meta));
    meta->status = DOM_DOMAIN_QUERY_REFUSED;
    meta->resolution = DOM_DOMAIN_RES_REFUSED;
    meta->confidence = DOM_DOMAIN_CONFIDENCE_UNKNOWN;
    meta->refusal_reason = reason;
    if (budget) {
        meta->budget_used = budget->used_units;
        meta->budget_max = budget->max_units;
    }
}

static void dom_econ_query_meta_ok(dom_domain_query_meta* meta,
                                   u32 resolution,
                                   u32 confidence,
                                   u32 cost_units,
                                   const dom_domain_budget* budget)
{
    if (!meta) {
        return;
    }
    memset(meta, 0, sizeof(*meta));
    meta->status = DOM_DOMAIN_QUERY_OK;
    meta->resolution = resolution;
    meta->confidence = confidence;
    meta->refusal_reason = DOM_DOMAIN_REFUSE_NONE;
    meta->cost_units = cost_units;
    if (budget) {
        meta->budget_used = budget->used_units;
        meta->budget_max = budget->max_units;
    }
}

static u32 dom_econ_budget_cost(u32 cost_units)
{
    return (cost_units == 0u) ? DOM_ECON_RESOLVE_COST_BASE : cost_units;
}

static d_bool dom_econ_apply_transport(dom_econ_transport* transport, u64 tick)
{
    if (!transport) {
        return D_FALSE;
    }
    if (transport->arrival_tick != 0u && transport->arrival_tick <= tick) {
        if (!(transport->flags & DOM_ECON_TRANSPORT_ARRIVED)) {
            transport->flags |= DOM_ECON_TRANSPORT_ARRIVED;
            transport->flags &= ~(DOM_ECON_TRANSPORT_IN_TRANSIT);
            return D_TRUE;
        }
        return D_FALSE;
    }
    if (transport->departure_tick != 0u && transport->departure_tick <= tick) {
        transport->flags |= DOM_ECON_TRANSPORT_IN_TRANSIT;
    }
    return D_FALSE;
}

static d_bool dom_econ_apply_job(dom_econ_job* job, u64 tick)
{
    if (!job) {
        return D_FALSE;
    }
    if (job->scheduled_tick != 0u && job->scheduled_tick <= tick) {
        if (!(job->flags & DOM_ECON_JOB_COMPLETED)) {
            job->flags |= DOM_ECON_JOB_COMPLETED;
            return D_TRUE;
        }
    }
    return D_FALSE;
}

static d_bool dom_econ_apply_transaction(dom_econ_transaction* txn, u64 tick)
{
    if (!txn) {
        return D_FALSE;
    }
    if (txn->executed_tick != 0u && txn->executed_tick <= tick) {
        if (!(txn->flags & DOM_ECON_TRANSACTION_SETTLED)) {
            txn->flags |= DOM_ECON_TRANSACTION_SETTLED;
            return D_TRUE;
        }
    }
    return D_FALSE;
}

void dom_econ_surface_desc_init(dom_econ_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->domain_id = 1u;
    desc->world_seed = 1u;
    desc->meters_per_unit = d_q16_16_from_int(1);
    desc->container_count = 0u;
    desc->storage_count = 0u;
    desc->transport_count = 0u;
    desc->job_count = 0u;
    desc->market_count = 0u;
    desc->offer_count = 0u;
    desc->bid_count = 0u;
    desc->transaction_count = 0u;
    for (u32 i = 0u; i < DOM_ECON_MAX_CONTAINERS; ++i) {
        desc->containers[i].container_id = 0u;
    }
    for (u32 i = 0u; i < DOM_ECON_MAX_STORAGES; ++i) {
        desc->storages[i].storage_id = 0u;
    }
    for (u32 i = 0u; i < DOM_ECON_MAX_TRANSPORTS; ++i) {
        desc->transports[i].transport_id = 0u;
    }
    for (u32 i = 0u; i < DOM_ECON_MAX_JOBS; ++i) {
        desc->jobs[i].job_id = 0u;
    }
    for (u32 i = 0u; i < DOM_ECON_MAX_MARKETS; ++i) {
        desc->markets[i].market_id = 0u;
    }
    for (u32 i = 0u; i < DOM_ECON_MAX_OFFERS; ++i) {
        desc->offers[i].offer_id = 0u;
    }
    for (u32 i = 0u; i < DOM_ECON_MAX_BIDS; ++i) {
        desc->bids[i].bid_id = 0u;
    }
    for (u32 i = 0u; i < DOM_ECON_MAX_TRANSACTIONS; ++i) {
        desc->transactions[i].transaction_id = 0u;
    }
}

void dom_econ_domain_init(dom_econ_domain* domain,
                          const dom_econ_surface_desc* desc)
{
    if (!domain || !desc) {
        return;
    }
    memset(domain, 0, sizeof(*domain));
    domain->surface = *desc;
    dom_domain_policy_init(&domain->policy);
    domain->existence_state = DOM_DOMAIN_EXISTENCE_REALIZED;
    domain->archival_state = DOM_DOMAIN_ARCHIVAL_LIVE;
    domain->authoring_version = 1u;

    domain->container_count = (desc->container_count > DOM_ECON_MAX_CONTAINERS)
                                ? DOM_ECON_MAX_CONTAINERS
                                : desc->container_count;
    domain->storage_count = (desc->storage_count > DOM_ECON_MAX_STORAGES)
                              ? DOM_ECON_MAX_STORAGES
                              : desc->storage_count;
    domain->transport_count = (desc->transport_count > DOM_ECON_MAX_TRANSPORTS)
                                ? DOM_ECON_MAX_TRANSPORTS
                                : desc->transport_count;
    domain->job_count = (desc->job_count > DOM_ECON_MAX_JOBS)
                          ? DOM_ECON_MAX_JOBS
                          : desc->job_count;
    domain->market_count = (desc->market_count > DOM_ECON_MAX_MARKETS)
                             ? DOM_ECON_MAX_MARKETS
                             : desc->market_count;
    domain->offer_count = (desc->offer_count > DOM_ECON_MAX_OFFERS)
                            ? DOM_ECON_MAX_OFFERS
                            : desc->offer_count;
    domain->bid_count = (desc->bid_count > DOM_ECON_MAX_BIDS)
                          ? DOM_ECON_MAX_BIDS
                          : desc->bid_count;
    domain->transaction_count = (desc->transaction_count > DOM_ECON_MAX_TRANSACTIONS)
                                  ? DOM_ECON_MAX_TRANSACTIONS
                                  : desc->transaction_count;

    for (u32 i = 0u; i < domain->container_count; ++i) {
        dom_econ_container_init(&domain->containers[i]);
        domain->containers[i].container_id = desc->containers[i].container_id;
        domain->containers[i].capacity = desc->containers[i].capacity;
        domain->containers[i].contents_amount = desc->containers[i].contents_amount;
        domain->containers[i].integrity = desc->containers[i].integrity;
        domain->containers[i].owner_ref_id = desc->containers[i].owner_ref_id;
        domain->containers[i].location_ref_id = desc->containers[i].location_ref_id;
        domain->containers[i].storage_ref_id = desc->containers[i].storage_ref_id;
        domain->containers[i].provenance_id = desc->containers[i].provenance_id;
        domain->containers[i].region_id = desc->containers[i].region_id;
        domain->containers[i].flags = desc->containers[i].flags;
    }

    for (u32 i = 0u; i < domain->storage_count; ++i) {
        dom_econ_storage_init(&domain->storages[i]);
        domain->storages[i].storage_id = desc->storages[i].storage_id;
        domain->storages[i].location_ref_id = desc->storages[i].location_ref_id;
        domain->storages[i].capacity = desc->storages[i].capacity;
        domain->storages[i].stored_amount = desc->storages[i].stored_amount;
        domain->storages[i].decay_rate = desc->storages[i].decay_rate;
        domain->storages[i].integrity = desc->storages[i].integrity;
        domain->storages[i].risk_profile_id = desc->storages[i].risk_profile_id;
        domain->storages[i].provenance_id = desc->storages[i].provenance_id;
        domain->storages[i].region_id = desc->storages[i].region_id;
        domain->storages[i].flags = desc->storages[i].flags;
    }

    for (u32 i = 0u; i < domain->transport_count; ++i) {
        dom_econ_transport_init(&domain->transports[i]);
        domain->transports[i].transport_id = desc->transports[i].transport_id;
        domain->transports[i].vehicle_ref_id = desc->transports[i].vehicle_ref_id;
        domain->transports[i].route_ref_id = desc->transports[i].route_ref_id;
        domain->transports[i].capacity = desc->transports[i].capacity;
        domain->transports[i].cargo_amount = desc->transports[i].cargo_amount;
        domain->transports[i].travel_cost = desc->transports[i].travel_cost;
        domain->transports[i].risk_modifier = desc->transports[i].risk_modifier;
        domain->transports[i].risk_profile_id = desc->transports[i].risk_profile_id;
        domain->transports[i].origin_ref_id = desc->transports[i].origin_ref_id;
        domain->transports[i].destination_ref_id = desc->transports[i].destination_ref_id;
        domain->transports[i].departure_tick = desc->transports[i].departure_tick;
        domain->transports[i].arrival_tick = desc->transports[i].arrival_tick;
        domain->transports[i].provenance_id = desc->transports[i].provenance_id;
        domain->transports[i].region_id = desc->transports[i].region_id;
        domain->transports[i].flags = desc->transports[i].flags;
    }

    for (u32 i = 0u; i < domain->job_count; ++i) {
        dom_econ_job_init(&domain->jobs[i]);
        domain->jobs[i].job_id = desc->jobs[i].job_id;
        domain->jobs[i].job_type = desc->jobs[i].job_type;
        domain->jobs[i].task_graph_ref_id = desc->jobs[i].task_graph_ref_id;
        domain->jobs[i].worker_ref_id = desc->jobs[i].worker_ref_id;
        domain->jobs[i].required_skill_ref_id = desc->jobs[i].required_skill_ref_id;
        domain->jobs[i].energy_cost = desc->jobs[i].energy_cost;
        domain->jobs[i].duration_ticks = desc->jobs[i].duration_ticks;
        domain->jobs[i].scheduled_tick = desc->jobs[i].scheduled_tick;
        domain->jobs[i].input_ref_id = desc->jobs[i].input_ref_id;
        domain->jobs[i].output_ref_id = desc->jobs[i].output_ref_id;
        domain->jobs[i].risk_profile_id = desc->jobs[i].risk_profile_id;
        domain->jobs[i].provenance_id = desc->jobs[i].provenance_id;
        domain->jobs[i].region_id = desc->jobs[i].region_id;
        domain->jobs[i].flags = desc->jobs[i].flags;
    }

    for (u32 i = 0u; i < domain->market_count; ++i) {
        dom_econ_market_init(&domain->markets[i]);
        domain->markets[i].market_id = desc->markets[i].market_id;
        domain->markets[i].location_ref_id = desc->markets[i].location_ref_id;
        domain->markets[i].jurisdiction_ref_id = desc->markets[i].jurisdiction_ref_id;
        domain->markets[i].listing_capacity = desc->markets[i].listing_capacity;
        domain->markets[i].transaction_fee = desc->markets[i].transaction_fee;
        domain->markets[i].info_delay = desc->markets[i].info_delay;
        domain->markets[i].risk_profile_id = desc->markets[i].risk_profile_id;
        domain->markets[i].trust_profile_id = desc->markets[i].trust_profile_id;
        domain->markets[i].law_ref_id = desc->markets[i].law_ref_id;
        domain->markets[i].provenance_id = desc->markets[i].provenance_id;
        domain->markets[i].region_id = desc->markets[i].region_id;
        domain->markets[i].flags = desc->markets[i].flags;
    }

    for (u32 i = 0u; i < domain->offer_count; ++i) {
        dom_econ_offer_init(&domain->offers[i]);
        domain->offers[i].offer_id = desc->offers[i].offer_id;
        domain->offers[i].market_id = desc->offers[i].market_id;
        domain->offers[i].seller_ref_id = desc->offers[i].seller_ref_id;
        domain->offers[i].goods_ref_id = desc->offers[i].goods_ref_id;
        domain->offers[i].quantity = desc->offers[i].quantity;
        domain->offers[i].price = desc->offers[i].price;
        domain->offers[i].exchange_medium_ref_id = desc->offers[i].exchange_medium_ref_id;
        domain->offers[i].expiry_tick = desc->offers[i].expiry_tick;
        domain->offers[i].risk_profile_id = desc->offers[i].risk_profile_id;
        domain->offers[i].trust_profile_id = desc->offers[i].trust_profile_id;
        domain->offers[i].provenance_id = desc->offers[i].provenance_id;
        domain->offers[i].region_id = desc->offers[i].region_id;
        domain->offers[i].flags = desc->offers[i].flags;
    }

    for (u32 i = 0u; i < domain->bid_count; ++i) {
        dom_econ_bid_init(&domain->bids[i]);
        domain->bids[i].bid_id = desc->bids[i].bid_id;
        domain->bids[i].market_id = desc->bids[i].market_id;
        domain->bids[i].buyer_ref_id = desc->bids[i].buyer_ref_id;
        domain->bids[i].goods_ref_id = desc->bids[i].goods_ref_id;
        domain->bids[i].quantity = desc->bids[i].quantity;
        domain->bids[i].price = desc->bids[i].price;
        domain->bids[i].exchange_medium_ref_id = desc->bids[i].exchange_medium_ref_id;
        domain->bids[i].expiry_tick = desc->bids[i].expiry_tick;
        domain->bids[i].risk_profile_id = desc->bids[i].risk_profile_id;
        domain->bids[i].trust_profile_id = desc->bids[i].trust_profile_id;
        domain->bids[i].provenance_id = desc->bids[i].provenance_id;
        domain->bids[i].region_id = desc->bids[i].region_id;
        domain->bids[i].flags = desc->bids[i].flags;
    }

    for (u32 i = 0u; i < domain->transaction_count; ++i) {
        dom_econ_transaction_init(&domain->transactions[i]);
        domain->transactions[i].transaction_id = desc->transactions[i].transaction_id;
        domain->transactions[i].market_id = desc->transactions[i].market_id;
        domain->transactions[i].offer_id = desc->transactions[i].offer_id;
        domain->transactions[i].bid_id = desc->transactions[i].bid_id;
        domain->transactions[i].buyer_ref_id = desc->transactions[i].buyer_ref_id;
        domain->transactions[i].seller_ref_id = desc->transactions[i].seller_ref_id;
        domain->transactions[i].goods_ref_id = desc->transactions[i].goods_ref_id;
        domain->transactions[i].quantity = desc->transactions[i].quantity;
        domain->transactions[i].price = desc->transactions[i].price;
        domain->transactions[i].exchange_medium_ref_id = desc->transactions[i].exchange_medium_ref_id;
        domain->transactions[i].transport_ref_id = desc->transactions[i].transport_ref_id;
        domain->transactions[i].executed_tick = desc->transactions[i].executed_tick;
        domain->transactions[i].risk_profile_id = desc->transactions[i].risk_profile_id;
        domain->transactions[i].provenance_id = desc->transactions[i].provenance_id;
        domain->transactions[i].region_id = desc->transactions[i].region_id;
        domain->transactions[i].flags = desc->transactions[i].flags;
    }

    domain->capsule_count = 0u;
}

void dom_econ_domain_free(dom_econ_domain* domain)
{
    if (!domain) {
        return;
    }
    domain->container_count = 0u;
    domain->storage_count = 0u;
    domain->transport_count = 0u;
    domain->job_count = 0u;
    domain->market_count = 0u;
    domain->offer_count = 0u;
    domain->bid_count = 0u;
    domain->transaction_count = 0u;
    domain->capsule_count = 0u;
}

void dom_econ_domain_set_state(dom_econ_domain* domain,
                               u32 existence_state,
                               u32 archival_state)
{
    if (!domain) {
        return;
    }
    domain->existence_state = existence_state;
    domain->archival_state = archival_state;
}

void dom_econ_domain_set_policy(dom_econ_domain* domain,
                                const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
}

int dom_econ_container_query(const dom_econ_domain* domain,
                             u32 container_id,
                             dom_domain_budget* budget,
                             dom_econ_container_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_ECON_CONTAINER_UNRESOLVED;

    if (!dom_econ_domain_is_active(domain)) {
        dom_econ_query_meta_refused(&out_sample->meta,
                                    DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_econ_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_econ_find_container_index(domain, container_id);
    if (index < 0) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_econ_region_collapsed(domain, domain->containers[index].region_id)) {
        out_sample->container_id = domain->containers[index].container_id;
        out_sample->region_id = domain->containers[index].region_id;
        out_sample->flags = DOM_ECON_CONTAINER_COLLAPSED;
        dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->container_id = domain->containers[index].container_id;
    out_sample->capacity = domain->containers[index].capacity;
    out_sample->contents_amount = domain->containers[index].contents_amount;
    out_sample->integrity = domain->containers[index].integrity;
    out_sample->owner_ref_id = domain->containers[index].owner_ref_id;
    out_sample->location_ref_id = domain->containers[index].location_ref_id;
    out_sample->storage_ref_id = domain->containers[index].storage_ref_id;
    out_sample->provenance_id = domain->containers[index].provenance_id;
    out_sample->region_id = domain->containers[index].region_id;
    out_sample->flags = domain->containers[index].flags;
    dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_econ_storage_query(const dom_econ_domain* domain,
                           u32 storage_id,
                           dom_domain_budget* budget,
                           dom_econ_storage_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_ECON_STORAGE_UNRESOLVED;

    if (!dom_econ_domain_is_active(domain)) {
        dom_econ_query_meta_refused(&out_sample->meta,
                                    DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_econ_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_econ_find_storage_index(domain, storage_id);
    if (index < 0) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_econ_region_collapsed(domain, domain->storages[index].region_id)) {
        out_sample->storage_id = domain->storages[index].storage_id;
        out_sample->region_id = domain->storages[index].region_id;
        out_sample->flags = DOM_ECON_STORAGE_COLLAPSED;
        dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->storage_id = domain->storages[index].storage_id;
    out_sample->location_ref_id = domain->storages[index].location_ref_id;
    out_sample->capacity = domain->storages[index].capacity;
    out_sample->stored_amount = domain->storages[index].stored_amount;
    out_sample->decay_rate = domain->storages[index].decay_rate;
    out_sample->integrity = domain->storages[index].integrity;
    out_sample->risk_profile_id = domain->storages[index].risk_profile_id;
    out_sample->provenance_id = domain->storages[index].provenance_id;
    out_sample->region_id = domain->storages[index].region_id;
    out_sample->flags = domain->storages[index].flags;
    dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_econ_transport_query(const dom_econ_domain* domain,
                             u32 transport_id,
                             dom_domain_budget* budget,
                             dom_econ_transport_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_ECON_TRANSPORT_UNRESOLVED;

    if (!dom_econ_domain_is_active(domain)) {
        dom_econ_query_meta_refused(&out_sample->meta,
                                    DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_econ_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_econ_find_transport_index(domain, transport_id);
    if (index < 0) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_econ_region_collapsed(domain, domain->transports[index].region_id)) {
        out_sample->transport_id = domain->transports[index].transport_id;
        out_sample->region_id = domain->transports[index].region_id;
        out_sample->flags = DOM_ECON_TRANSPORT_IN_TRANSIT;
        dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->transport_id = domain->transports[index].transport_id;
    out_sample->vehicle_ref_id = domain->transports[index].vehicle_ref_id;
    out_sample->route_ref_id = domain->transports[index].route_ref_id;
    out_sample->capacity = domain->transports[index].capacity;
    out_sample->cargo_amount = domain->transports[index].cargo_amount;
    out_sample->travel_cost = domain->transports[index].travel_cost;
    out_sample->risk_modifier = domain->transports[index].risk_modifier;
    out_sample->risk_profile_id = domain->transports[index].risk_profile_id;
    out_sample->origin_ref_id = domain->transports[index].origin_ref_id;
    out_sample->destination_ref_id = domain->transports[index].destination_ref_id;
    out_sample->departure_tick = domain->transports[index].departure_tick;
    out_sample->arrival_tick = domain->transports[index].arrival_tick;
    out_sample->provenance_id = domain->transports[index].provenance_id;
    out_sample->region_id = domain->transports[index].region_id;
    out_sample->flags = domain->transports[index].flags;
    dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_econ_job_query(const dom_econ_domain* domain,
                       u32 job_id,
                       dom_domain_budget* budget,
                       dom_econ_job_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_ECON_JOB_UNRESOLVED;

    if (!dom_econ_domain_is_active(domain)) {
        dom_econ_query_meta_refused(&out_sample->meta,
                                    DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_econ_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_econ_find_job_index(domain, job_id);
    if (index < 0) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_econ_region_collapsed(domain, domain->jobs[index].region_id)) {
        out_sample->job_id = domain->jobs[index].job_id;
        out_sample->region_id = domain->jobs[index].region_id;
        out_sample->flags = DOM_ECON_JOB_UNRESOLVED;
        dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->job_id = domain->jobs[index].job_id;
    out_sample->job_type = domain->jobs[index].job_type;
    out_sample->task_graph_ref_id = domain->jobs[index].task_graph_ref_id;
    out_sample->worker_ref_id = domain->jobs[index].worker_ref_id;
    out_sample->required_skill_ref_id = domain->jobs[index].required_skill_ref_id;
    out_sample->energy_cost = domain->jobs[index].energy_cost;
    out_sample->duration_ticks = domain->jobs[index].duration_ticks;
    out_sample->scheduled_tick = domain->jobs[index].scheduled_tick;
    out_sample->input_ref_id = domain->jobs[index].input_ref_id;
    out_sample->output_ref_id = domain->jobs[index].output_ref_id;
    out_sample->risk_profile_id = domain->jobs[index].risk_profile_id;
    out_sample->provenance_id = domain->jobs[index].provenance_id;
    out_sample->region_id = domain->jobs[index].region_id;
    out_sample->flags = domain->jobs[index].flags;
    dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_econ_market_query(const dom_econ_domain* domain,
                          u32 market_id,
                          dom_domain_budget* budget,
                          dom_econ_market_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_ECON_MARKET_UNRESOLVED;

    if (!dom_econ_domain_is_active(domain)) {
        dom_econ_query_meta_refused(&out_sample->meta,
                                    DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_econ_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_econ_find_market_index(domain, market_id);
    if (index < 0) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_econ_region_collapsed(domain, domain->markets[index].region_id)) {
        out_sample->market_id = domain->markets[index].market_id;
        out_sample->region_id = domain->markets[index].region_id;
        out_sample->flags = DOM_ECON_MARKET_COLLAPSED;
        dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->market_id = domain->markets[index].market_id;
    out_sample->location_ref_id = domain->markets[index].location_ref_id;
    out_sample->jurisdiction_ref_id = domain->markets[index].jurisdiction_ref_id;
    out_sample->listing_capacity = domain->markets[index].listing_capacity;
    out_sample->transaction_fee = domain->markets[index].transaction_fee;
    out_sample->info_delay = domain->markets[index].info_delay;
    out_sample->risk_profile_id = domain->markets[index].risk_profile_id;
    out_sample->trust_profile_id = domain->markets[index].trust_profile_id;
    out_sample->law_ref_id = domain->markets[index].law_ref_id;
    out_sample->provenance_id = domain->markets[index].provenance_id;
    out_sample->region_id = domain->markets[index].region_id;
    out_sample->flags = domain->markets[index].flags;
    dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_econ_offer_query(const dom_econ_domain* domain,
                         u32 offer_id,
                         dom_domain_budget* budget,
                         dom_econ_offer_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_ECON_OFFER_UNRESOLVED;

    if (!dom_econ_domain_is_active(domain)) {
        dom_econ_query_meta_refused(&out_sample->meta,
                                    DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_econ_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_econ_find_offer_index(domain, offer_id);
    if (index < 0) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_econ_region_collapsed(domain, domain->offers[index].region_id)) {
        out_sample->offer_id = domain->offers[index].offer_id;
        out_sample->region_id = domain->offers[index].region_id;
        out_sample->flags = DOM_ECON_OFFER_OPEN;
        dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->offer_id = domain->offers[index].offer_id;
    out_sample->market_id = domain->offers[index].market_id;
    out_sample->seller_ref_id = domain->offers[index].seller_ref_id;
    out_sample->goods_ref_id = domain->offers[index].goods_ref_id;
    out_sample->quantity = domain->offers[index].quantity;
    out_sample->price = domain->offers[index].price;
    out_sample->exchange_medium_ref_id = domain->offers[index].exchange_medium_ref_id;
    out_sample->expiry_tick = domain->offers[index].expiry_tick;
    out_sample->risk_profile_id = domain->offers[index].risk_profile_id;
    out_sample->trust_profile_id = domain->offers[index].trust_profile_id;
    out_sample->provenance_id = domain->offers[index].provenance_id;
    out_sample->region_id = domain->offers[index].region_id;
    out_sample->flags = domain->offers[index].flags;
    dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_econ_bid_query(const dom_econ_domain* domain,
                       u32 bid_id,
                       dom_domain_budget* budget,
                       dom_econ_bid_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_ECON_BID_UNRESOLVED;

    if (!dom_econ_domain_is_active(domain)) {
        dom_econ_query_meta_refused(&out_sample->meta,
                                    DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_econ_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_econ_find_bid_index(domain, bid_id);
    if (index < 0) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_econ_region_collapsed(domain, domain->bids[index].region_id)) {
        out_sample->bid_id = domain->bids[index].bid_id;
        out_sample->region_id = domain->bids[index].region_id;
        out_sample->flags = DOM_ECON_BID_OPEN;
        dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->bid_id = domain->bids[index].bid_id;
    out_sample->market_id = domain->bids[index].market_id;
    out_sample->buyer_ref_id = domain->bids[index].buyer_ref_id;
    out_sample->goods_ref_id = domain->bids[index].goods_ref_id;
    out_sample->quantity = domain->bids[index].quantity;
    out_sample->price = domain->bids[index].price;
    out_sample->exchange_medium_ref_id = domain->bids[index].exchange_medium_ref_id;
    out_sample->expiry_tick = domain->bids[index].expiry_tick;
    out_sample->risk_profile_id = domain->bids[index].risk_profile_id;
    out_sample->trust_profile_id = domain->bids[index].trust_profile_id;
    out_sample->provenance_id = domain->bids[index].provenance_id;
    out_sample->region_id = domain->bids[index].region_id;
    out_sample->flags = domain->bids[index].flags;
    dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_econ_transaction_query(const dom_econ_domain* domain,
                               u32 transaction_id,
                               dom_domain_budget* budget,
                               dom_econ_transaction_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_ECON_TRANSACTION_UNRESOLVED;

    if (!dom_econ_domain_is_active(domain)) {
        dom_econ_query_meta_refused(&out_sample->meta,
                                    DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_econ_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_econ_find_transaction_index(domain, transaction_id);
    if (index < 0) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_econ_region_collapsed(domain, domain->transactions[index].region_id)) {
        out_sample->transaction_id = domain->transactions[index].transaction_id;
        out_sample->region_id = domain->transactions[index].region_id;
        out_sample->flags = DOM_ECON_TRANSACTION_UNRESOLVED;
        dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->transaction_id = domain->transactions[index].transaction_id;
    out_sample->market_id = domain->transactions[index].market_id;
    out_sample->offer_id = domain->transactions[index].offer_id;
    out_sample->bid_id = domain->transactions[index].bid_id;
    out_sample->buyer_ref_id = domain->transactions[index].buyer_ref_id;
    out_sample->seller_ref_id = domain->transactions[index].seller_ref_id;
    out_sample->goods_ref_id = domain->transactions[index].goods_ref_id;
    out_sample->quantity = domain->transactions[index].quantity;
    out_sample->price = domain->transactions[index].price;
    out_sample->exchange_medium_ref_id = domain->transactions[index].exchange_medium_ref_id;
    out_sample->transport_ref_id = domain->transactions[index].transport_ref_id;
    out_sample->executed_tick = domain->transactions[index].executed_tick;
    out_sample->risk_profile_id = domain->transactions[index].risk_profile_id;
    out_sample->provenance_id = domain->transactions[index].provenance_id;
    out_sample->region_id = domain->transactions[index].region_id;
    out_sample->flags = domain->transactions[index].flags;
    dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_econ_region_query(const dom_econ_domain* domain,
                          u32 region_id,
                          dom_domain_budget* budget,
                          dom_econ_region_sample* out_sample)
{
    u32 cost_base;
    u32 cost_container;
    u32 cost_storage;
    u32 cost_transport;
    u32 cost_job;
    u32 cost_market;
    u32 cost_offer;
    u32 cost_bid;
    u32 cost_txn;
    q48_16 goods_total = 0;
    q48_16 price_total = 0;
    q48_16 txn_volume_total = 0;
    u32 price_seen = 0u;
    u32 flags = 0u;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_econ_domain_is_active(domain)) {
        dom_econ_query_meta_refused(&out_sample->meta,
                                    DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost_base = dom_econ_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        dom_econ_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    if (region_id != 0u && dom_econ_region_collapsed(domain, region_id)) {
        const dom_econ_macro_capsule* capsule = dom_econ_find_capsule(domain, region_id);
        if (capsule) {
            out_sample->region_id = capsule->region_id;
            out_sample->container_count = capsule->container_count;
            out_sample->storage_count = capsule->storage_count;
            out_sample->transport_count = capsule->transport_count;
            out_sample->job_count = capsule->job_count;
            out_sample->market_count = capsule->market_count;
            out_sample->offer_count = capsule->offer_count;
            out_sample->bid_count = capsule->bid_count;
            out_sample->transaction_count = capsule->transaction_count;
            out_sample->goods_total = capsule->goods_total;
            out_sample->price_avg = capsule->price_avg;
            out_sample->transaction_volume_total = capsule->transaction_volume_total;
        }
        out_sample->flags = DOM_ECON_RESOLVE_PARTIAL;
        dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost_base, budget);
        return 0;
    }

    cost_container = dom_econ_budget_cost(domain->policy.cost_medium);
    cost_storage = dom_econ_budget_cost(domain->policy.cost_coarse);
    cost_transport = dom_econ_budget_cost(domain->policy.cost_coarse);
    cost_job = dom_econ_budget_cost(domain->policy.cost_coarse);
    cost_market = dom_econ_budget_cost(domain->policy.cost_coarse);
    cost_offer = dom_econ_budget_cost(domain->policy.cost_medium);
    cost_bid = dom_econ_budget_cost(domain->policy.cost_medium);
    cost_txn = dom_econ_budget_cost(domain->policy.cost_medium);

    for (u32 i = 0u; i < domain->container_count; ++i) {
        u32 container_region = domain->containers[i].region_id;
        if (region_id != 0u && container_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_econ_region_collapsed(domain, container_region)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_container)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            break;
        }
        goods_total = d_q48_16_add(goods_total, domain->containers[i].contents_amount);
        out_sample->container_count += 1u;
    }

    for (u32 i = 0u; i < domain->storage_count; ++i) {
        u32 storage_region = domain->storages[i].region_id;
        if (region_id != 0u && storage_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_econ_region_collapsed(domain, storage_region)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_storage)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            break;
        }
        goods_total = d_q48_16_add(goods_total, domain->storages[i].stored_amount);
        out_sample->storage_count += 1u;
        if (domain->storages[i].stored_amount > domain->storages[i].capacity) {
            flags |= DOM_ECON_RESOLVE_CONGESTED;
        }
    }

    for (u32 i = 0u; i < domain->transport_count; ++i) {
        u32 transport_region = domain->transports[i].region_id;
        if (region_id != 0u && transport_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_econ_region_collapsed(domain, transport_region)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_transport)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            break;
        }
        out_sample->transport_count += 1u;
        if (domain->transports[i].flags & DOM_ECON_TRANSPORT_DELAYED) {
            flags |= DOM_ECON_RESOLVE_CONGESTED;
        }
        if (domain->transports[i].risk_modifier >= DOM_ECON_RISK_THRESHOLD_Q16 ||
            domain->transports[i].risk_profile_id != 0u) {
            flags |= DOM_ECON_RESOLVE_RISK;
        }
    }

    for (u32 i = 0u; i < domain->job_count; ++i) {
        u32 job_region = domain->jobs[i].region_id;
        if (region_id != 0u && job_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_econ_region_collapsed(domain, job_region)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_job)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            break;
        }
        out_sample->job_count += 1u;
        if (domain->jobs[i].risk_profile_id != 0u) {
            flags |= DOM_ECON_RESOLVE_RISK;
        }
    }

    for (u32 i = 0u; i < domain->market_count; ++i) {
        u32 market_region = domain->markets[i].region_id;
        if (region_id != 0u && market_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_econ_region_collapsed(domain, market_region)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_market)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            break;
        }
        out_sample->market_count += 1u;
        if (domain->markets[i].flags & DOM_ECON_MARKET_BLACK_MARKET) {
            flags |= DOM_ECON_RESOLVE_BLACK_MARKET;
        }
        if (domain->markets[i].risk_profile_id != 0u) {
            flags |= DOM_ECON_RESOLVE_RISK;
        }
    }

    for (u32 i = 0u; i < domain->offer_count; ++i) {
        u32 offer_region = domain->offers[i].region_id;
        if (region_id != 0u && offer_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_econ_region_collapsed(domain, offer_region)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_offer)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            break;
        }
        out_sample->offer_count += 1u;
        price_total = d_q48_16_add(price_total, domain->offers[i].price);
        price_seen += 1u;
        if (domain->offers[i].flags & DOM_ECON_OFFER_BLACK_MARKET) {
            flags |= DOM_ECON_RESOLVE_BLACK_MARKET;
        }
        if (domain->offers[i].risk_profile_id != 0u) {
            flags |= DOM_ECON_RESOLVE_RISK;
        }
    }

    for (u32 i = 0u; i < domain->bid_count; ++i) {
        u32 bid_region = domain->bids[i].region_id;
        if (region_id != 0u && bid_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_econ_region_collapsed(domain, bid_region)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_bid)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            break;
        }
        out_sample->bid_count += 1u;
        price_total = d_q48_16_add(price_total, domain->bids[i].price);
        price_seen += 1u;
        if (domain->bids[i].flags & DOM_ECON_BID_BLACK_MARKET) {
            flags |= DOM_ECON_RESOLVE_BLACK_MARKET;
        }
        if (domain->bids[i].risk_profile_id != 0u) {
            flags |= DOM_ECON_RESOLVE_RISK;
        }
    }

    for (u32 i = 0u; i < domain->transaction_count; ++i) {
        u32 txn_region = domain->transactions[i].region_id;
        if (region_id != 0u && txn_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_econ_region_collapsed(domain, txn_region)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_txn)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            break;
        }
        out_sample->transaction_count += 1u;
        price_total = d_q48_16_add(price_total, domain->transactions[i].price);
        price_seen += 1u;
        txn_volume_total = d_q48_16_add(txn_volume_total, domain->transactions[i].quantity);
        if (domain->transactions[i].risk_profile_id != 0u) {
            flags |= DOM_ECON_RESOLVE_RISK;
        }
    }

    if (out_sample->bid_count > out_sample->offer_count && out_sample->bid_count > 0u) {
        flags |= DOM_ECON_RESOLVE_SHORTAGE;
    }

    out_sample->region_id = region_id;
    out_sample->goods_total = goods_total;
    out_sample->transaction_volume_total = txn_volume_total;
    if (price_seen > 0u) {
        out_sample->price_avg = d_q48_16_div(price_total, d_q48_16_from_int((i64)price_seen));
    }
    out_sample->flags = flags;
    dom_econ_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           flags ? DOM_DOMAIN_CONFIDENCE_UNKNOWN : DOM_DOMAIN_CONFIDENCE_EXACT,
                           cost_base, budget);
    return 0;
}

int dom_econ_resolve(dom_econ_domain* domain,
                     u32 region_id,
                     u64 tick,
                     u64 tick_delta,
                     dom_domain_budget* budget,
                     dom_econ_resolve_result* out_result)
{
    u32 cost_base;
    u32 cost_container;
    u32 cost_storage;
    u32 cost_transport;
    u32 cost_job;
    u32 cost_market;
    u32 cost_offer;
    u32 cost_bid;
    u32 cost_txn;
    q48_16 goods_total = 0;
    q48_16 price_total = 0;
    q48_16 txn_volume_total = 0;
    u32 price_seen = 0u;
    u32 flags = 0u;
    if (!domain || !out_result) {
        return -1;
    }
    memset(out_result, 0, sizeof(*out_result));

    if (!dom_econ_domain_is_active(domain)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_ECON_REFUSE_DOMAIN_INACTIVE;
        return 0;
    }

    cost_base = dom_econ_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_ECON_REFUSE_BUDGET;
        return 0;
    }

    if (region_id != 0u && dom_econ_region_collapsed(domain, region_id)) {
        const dom_econ_macro_capsule* capsule = dom_econ_find_capsule(domain, region_id);
        if (capsule) {
            out_result->container_count = capsule->container_count;
            out_result->storage_count = capsule->storage_count;
            out_result->transport_count = capsule->transport_count;
            out_result->job_count = capsule->job_count;
            out_result->market_count = capsule->market_count;
            out_result->offer_count = capsule->offer_count;
            out_result->bid_count = capsule->bid_count;
            out_result->transaction_count = capsule->transaction_count;
            out_result->goods_total = capsule->goods_total;
            out_result->price_avg = capsule->price_avg;
            out_result->transaction_volume_total = capsule->transaction_volume_total;
        }
        out_result->ok = 1u;
        out_result->flags = DOM_ECON_RESOLVE_PARTIAL;
        return 0;
    }

    if (tick_delta == 0u) {
        tick_delta = 1u;
    }

    cost_container = dom_econ_budget_cost(domain->policy.cost_medium);
    cost_storage = dom_econ_budget_cost(domain->policy.cost_coarse);
    cost_transport = dom_econ_budget_cost(domain->policy.cost_coarse);
    cost_job = dom_econ_budget_cost(domain->policy.cost_coarse);
    cost_market = dom_econ_budget_cost(domain->policy.cost_coarse);
    cost_offer = dom_econ_budget_cost(domain->policy.cost_medium);
    cost_bid = dom_econ_budget_cost(domain->policy.cost_medium);
    cost_txn = dom_econ_budget_cost(domain->policy.cost_medium);

    for (u32 i = 0u; i < domain->container_count; ++i) {
        u32 container_region = domain->containers[i].region_id;
        if (region_id != 0u && container_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_econ_region_collapsed(domain, container_region)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_container)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_ECON_REFUSE_NONE) {
                out_result->refusal_reason = DOM_ECON_REFUSE_BUDGET;
            }
            break;
        }
        out_result->container_count += 1u;
        goods_total = d_q48_16_add(goods_total, domain->containers[i].contents_amount);
    }

    for (u32 i = 0u; i < domain->storage_count; ++i) {
        u32 storage_region = domain->storages[i].region_id;
        if (region_id != 0u && storage_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_econ_region_collapsed(domain, storage_region)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_storage)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_ECON_REFUSE_NONE) {
                out_result->refusal_reason = DOM_ECON_REFUSE_BUDGET;
            }
            break;
        }
        out_result->storage_count += 1u;
        goods_total = d_q48_16_add(goods_total, domain->storages[i].stored_amount);
        if (domain->storages[i].stored_amount > domain->storages[i].capacity) {
            domain->storages[i].flags |= DOM_ECON_STORAGE_OVERFLOW;
            flags |= DOM_ECON_RESOLVE_CONGESTED;
        }
        if (domain->storages[i].risk_profile_id != 0u) {
            flags |= DOM_ECON_RESOLVE_RISK;
        }
    }

    for (u32 i = 0u; i < domain->transport_count; ++i) {
        dom_econ_transport* transport = &domain->transports[i];
        u32 transport_region = transport->region_id;
        if (region_id != 0u && transport_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_econ_region_collapsed(domain, transport_region)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_transport)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_ECON_REFUSE_NONE) {
                out_result->refusal_reason = DOM_ECON_REFUSE_BUDGET;
            }
            break;
        }
        out_result->transport_count += 1u;
        if (dom_econ_apply_transport(transport, tick)) {
            out_result->transport_arrived_count += 1u;
        }
        if (transport->flags & DOM_ECON_TRANSPORT_DELAYED) {
            flags |= DOM_ECON_RESOLVE_CONGESTED;
        }
        if (transport->risk_modifier >= DOM_ECON_RISK_THRESHOLD_Q16 ||
            transport->risk_profile_id != 0u) {
            flags |= DOM_ECON_RESOLVE_RISK;
        }
    }

    for (u32 i = 0u; i < domain->job_count; ++i) {
        dom_econ_job* job = &domain->jobs[i];
        u32 job_region = job->region_id;
        if (region_id != 0u && job_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_econ_region_collapsed(domain, job_region)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_job)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_ECON_REFUSE_NONE) {
                out_result->refusal_reason = DOM_ECON_REFUSE_BUDGET;
            }
            break;
        }
        out_result->job_count += 1u;
        if (dom_econ_apply_job(job, tick)) {
            out_result->job_completed_count += 1u;
        }
        if (job->risk_profile_id != 0u) {
            flags |= DOM_ECON_RESOLVE_RISK;
        }
    }

    for (u32 i = 0u; i < domain->market_count; ++i) {
        u32 market_region = domain->markets[i].region_id;
        if (region_id != 0u && market_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_econ_region_collapsed(domain, market_region)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_market)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_ECON_REFUSE_NONE) {
                out_result->refusal_reason = DOM_ECON_REFUSE_BUDGET;
            }
            break;
        }
        out_result->market_count += 1u;
        if (domain->markets[i].flags & DOM_ECON_MARKET_BLACK_MARKET) {
            flags |= DOM_ECON_RESOLVE_BLACK_MARKET;
        }
        if (domain->markets[i].risk_profile_id != 0u) {
            flags |= DOM_ECON_RESOLVE_RISK;
        }
    }

    for (u32 i = 0u; i < domain->offer_count; ++i) {
        dom_econ_offer* offer = &domain->offers[i];
        u32 offer_region = offer->region_id;
        if (region_id != 0u && offer_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_econ_region_collapsed(domain, offer_region)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_offer)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_ECON_REFUSE_NONE) {
                out_result->refusal_reason = DOM_ECON_REFUSE_BUDGET;
            }
            break;
        }
        out_result->offer_count += 1u;
        if (offer->expiry_tick != 0u && offer->expiry_tick <= tick) {
            offer->flags |= DOM_ECON_OFFER_EXPIRED;
        }
        price_total = d_q48_16_add(price_total, offer->price);
        price_seen += 1u;
        if (offer->flags & DOM_ECON_OFFER_BLACK_MARKET) {
            flags |= DOM_ECON_RESOLVE_BLACK_MARKET;
        }
        if (offer->risk_profile_id != 0u) {
            flags |= DOM_ECON_RESOLVE_RISK;
        }
    }

    for (u32 i = 0u; i < domain->bid_count; ++i) {
        dom_econ_bid* bid = &domain->bids[i];
        u32 bid_region = bid->region_id;
        if (region_id != 0u && bid_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_econ_region_collapsed(domain, bid_region)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_bid)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_ECON_REFUSE_NONE) {
                out_result->refusal_reason = DOM_ECON_REFUSE_BUDGET;
            }
            break;
        }
        out_result->bid_count += 1u;
        if (bid->expiry_tick != 0u && bid->expiry_tick <= tick) {
            bid->flags |= DOM_ECON_BID_EXPIRED;
        }
        price_total = d_q48_16_add(price_total, bid->price);
        price_seen += 1u;
        if (bid->flags & DOM_ECON_BID_BLACK_MARKET) {
            flags |= DOM_ECON_RESOLVE_BLACK_MARKET;
        }
        if (bid->risk_profile_id != 0u) {
            flags |= DOM_ECON_RESOLVE_RISK;
        }
    }

    for (u32 i = 0u; i < domain->transaction_count; ++i) {
        dom_econ_transaction* txn = &domain->transactions[i];
        u32 txn_region = txn->region_id;
        if (region_id != 0u && txn_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_econ_region_collapsed(domain, txn_region)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_txn)) {
            flags |= DOM_ECON_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_ECON_REFUSE_NONE) {
                out_result->refusal_reason = DOM_ECON_REFUSE_BUDGET;
            }
            break;
        }
        out_result->transaction_count += 1u;
        if (dom_econ_apply_transaction(txn, tick)) {
            out_result->transaction_settled_count += 1u;
        }
        if (txn->flags & DOM_ECON_TRANSACTION_SETTLED) {
            txn_volume_total = d_q48_16_add(txn_volume_total, txn->quantity);
        }
        price_total = d_q48_16_add(price_total, txn->price);
        price_seen += 1u;
        if (txn->risk_profile_id != 0u) {
            flags |= DOM_ECON_RESOLVE_RISK;
        }
    }

    if (out_result->bid_count > out_result->offer_count && out_result->bid_count > 0u) {
        flags |= DOM_ECON_RESOLVE_SHORTAGE;
    }

    out_result->ok = 1u;
    out_result->flags = flags;
    out_result->goods_total = goods_total;
    out_result->transaction_volume_total = txn_volume_total;
    if (price_seen > 0u) {
        out_result->price_avg = d_q48_16_div(price_total, d_q48_16_from_int((i64)price_seen));
    }
    return 0;
}

int dom_econ_domain_collapse_region(dom_econ_domain* domain, u32 region_id)
{
    dom_econ_macro_capsule capsule;
    u32 price_bins[DOM_ECON_HIST_BINS];
    q48_16 goods_total = 0;
    q48_16 price_total = 0;
    q48_16 txn_volume_total = 0;
    u32 price_seen = 0u;
    if (!domain || region_id == 0u) {
        return -1;
    }
    if (dom_econ_region_collapsed(domain, region_id)) {
        return 0;
    }
    if (domain->capsule_count >= DOM_ECON_MAX_CAPSULES) {
        return -2;
    }
    memset(&capsule, 0, sizeof(capsule));
    memset(price_bins, 0, sizeof(price_bins));
    capsule.capsule_id = (u64)region_id;
    capsule.region_id = region_id;

    for (u32 i = 0u; i < domain->container_count; ++i) {
        if (domain->containers[i].region_id != region_id) {
            continue;
        }
        capsule.container_count += 1u;
        goods_total = d_q48_16_add(goods_total, domain->containers[i].contents_amount);
    }

    for (u32 i = 0u; i < domain->storage_count; ++i) {
        if (domain->storages[i].region_id != region_id) {
            continue;
        }
        capsule.storage_count += 1u;
        goods_total = d_q48_16_add(goods_total, domain->storages[i].stored_amount);
    }

    for (u32 i = 0u; i < domain->transport_count; ++i) {
        if (domain->transports[i].region_id != region_id) {
            continue;
        }
        capsule.transport_count += 1u;
    }

    for (u32 i = 0u; i < domain->job_count; ++i) {
        if (domain->jobs[i].region_id != region_id) {
            continue;
        }
        capsule.job_count += 1u;
    }

    for (u32 i = 0u; i < domain->market_count; ++i) {
        if (domain->markets[i].region_id != region_id) {
            continue;
        }
        capsule.market_count += 1u;
    }

    for (u32 i = 0u; i < domain->offer_count; ++i) {
        if (domain->offers[i].region_id != region_id) {
            continue;
        }
        capsule.offer_count += 1u;
        price_total = d_q48_16_add(price_total, domain->offers[i].price);
        price_seen += 1u;
    }

    for (u32 i = 0u; i < domain->bid_count; ++i) {
        if (domain->bids[i].region_id != region_id) {
            continue;
        }
        capsule.bid_count += 1u;
        price_total = d_q48_16_add(price_total, domain->bids[i].price);
        price_seen += 1u;
    }

    for (u32 i = 0u; i < domain->transaction_count; ++i) {
        if (domain->transactions[i].region_id != region_id) {
            continue;
        }
        capsule.transaction_count += 1u;
        price_total = d_q48_16_add(price_total, domain->transactions[i].price);
        price_seen += 1u;
        txn_volume_total = d_q48_16_add(txn_volume_total, domain->transactions[i].quantity);
    }

    capsule.goods_total = goods_total;
    capsule.transaction_volume_total = txn_volume_total;
    if (price_seen > 0u) {
        capsule.price_avg = d_q48_16_div(price_total, d_q48_16_from_int((i64)price_seen));
    }

    if (price_seen > 0u && capsule.price_avg > 0) {
        for (u32 i = 0u; i < domain->offer_count; ++i) {
            if (domain->offers[i].region_id != region_id) {
                continue;
            }
            {
                q16_16 ratio = dom_econ_price_ratio(domain->offers[i].price, capsule.price_avg);
                price_bins[dom_econ_price_bin(ratio)] += 1u;
            }
        }
        for (u32 i = 0u; i < domain->bid_count; ++i) {
            if (domain->bids[i].region_id != region_id) {
                continue;
            }
            {
                q16_16 ratio = dom_econ_price_ratio(domain->bids[i].price, capsule.price_avg);
                price_bins[dom_econ_price_bin(ratio)] += 1u;
            }
        }
        for (u32 i = 0u; i < domain->transaction_count; ++i) {
            if (domain->transactions[i].region_id != region_id) {
                continue;
            }
            {
                q16_16 ratio = dom_econ_price_ratio(domain->transactions[i].price,
                                                    capsule.price_avg);
                price_bins[dom_econ_price_bin(ratio)] += 1u;
            }
        }
    }

    for (u32 b = 0u; b < DOM_ECON_HIST_BINS; ++b) {
        capsule.price_hist[b] = dom_econ_ratio_from_counts(price_bins[b], price_seen);
        capsule.rng_cursor[b] = 0u;
    }

    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_econ_domain_expand_region(dom_econ_domain* domain, u32 region_id)
{
    if (!domain || region_id == 0u) {
        return -1;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            domain->capsules[i] = domain->capsules[domain->capsule_count - 1u];
            domain->capsule_count -= 1u;
            return 0;
        }
    }
    return -2;
}

u32 dom_econ_domain_capsule_count(const dom_econ_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_econ_macro_capsule* dom_econ_domain_capsule_at(const dom_econ_domain* domain,
                                                         u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_econ_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
