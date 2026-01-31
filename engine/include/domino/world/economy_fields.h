/*
FILE: include/domino/world/economy_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / world/economy_fields
RESPONSIBILITY: Deterministic logistics, markets, and economic field sampling.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 headers as needed.
FORBIDDEN DEPENDENCIES: Engine private headers outside `include/domino/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned by ECON0 specs.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_WORLD_ECONOMY_FIELDS_H
#define DOMINO_WORLD_ECONOMY_FIELDS_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/world/domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_ECON_MAX_CONTAINERS 128u
#define DOM_ECON_MAX_STORAGES 64u
#define DOM_ECON_MAX_TRANSPORTS 128u
#define DOM_ECON_MAX_JOBS 128u
#define DOM_ECON_MAX_MARKETS 64u
#define DOM_ECON_MAX_OFFERS 256u
#define DOM_ECON_MAX_BIDS 256u
#define DOM_ECON_MAX_TRANSACTIONS 256u
#define DOM_ECON_MAX_REGIONS 16u
#define DOM_ECON_MAX_CAPSULES 64u
#define DOM_ECON_HIST_BINS 4u

#define DOM_ECON_RATIO_ONE_Q16 ((q16_16)0x00010000)

enum dom_econ_job_type {
    DOM_ECON_JOB_UNSET = 0u,
    DOM_ECON_JOB_MOVE = 1u,
    DOM_ECON_JOB_STORE = 2u,
    DOM_ECON_JOB_MAINTAIN = 3u,
    DOM_ECON_JOB_TRANSFORM = 4u
};

enum dom_econ_container_flags {
    DOM_ECON_CONTAINER_UNRESOLVED = 1u << 0u,
    DOM_ECON_CONTAINER_COLLAPSED = 1u << 1u,
    DOM_ECON_CONTAINER_DAMAGED = 1u << 2u
};

enum dom_econ_storage_flags {
    DOM_ECON_STORAGE_UNRESOLVED = 1u << 0u,
    DOM_ECON_STORAGE_COLLAPSED = 1u << 1u,
    DOM_ECON_STORAGE_OVERFLOW = 1u << 2u
};

enum dom_econ_transport_flags {
    DOM_ECON_TRANSPORT_UNRESOLVED = 1u << 0u,
    DOM_ECON_TRANSPORT_IN_TRANSIT = 1u << 1u,
    DOM_ECON_TRANSPORT_ARRIVED = 1u << 2u,
    DOM_ECON_TRANSPORT_DELAYED = 1u << 3u
};

enum dom_econ_job_flags {
    DOM_ECON_JOB_UNRESOLVED = 1u << 0u,
    DOM_ECON_JOB_ASSIGNED = 1u << 1u,
    DOM_ECON_JOB_COMPLETED = 1u << 2u,
    DOM_ECON_JOB_FAILED = 1u << 3u
};

enum dom_econ_market_flags {
    DOM_ECON_MARKET_UNRESOLVED = 1u << 0u,
    DOM_ECON_MARKET_COLLAPSED = 1u << 1u,
    DOM_ECON_MARKET_RESTRICTED = 1u << 2u,
    DOM_ECON_MARKET_BLACK_MARKET = 1u << 3u
};

enum dom_econ_offer_flags {
    DOM_ECON_OFFER_UNRESOLVED = 1u << 0u,
    DOM_ECON_OFFER_OPEN = 1u << 1u,
    DOM_ECON_OFFER_MATCHED = 1u << 2u,
    DOM_ECON_OFFER_EXPIRED = 1u << 3u,
    DOM_ECON_OFFER_BLACK_MARKET = 1u << 4u
};

enum dom_econ_bid_flags {
    DOM_ECON_BID_UNRESOLVED = 1u << 0u,
    DOM_ECON_BID_OPEN = 1u << 1u,
    DOM_ECON_BID_MATCHED = 1u << 2u,
    DOM_ECON_BID_EXPIRED = 1u << 3u,
    DOM_ECON_BID_BLACK_MARKET = 1u << 4u
};

enum dom_econ_transaction_flags {
    DOM_ECON_TRANSACTION_UNRESOLVED = 1u << 0u,
    DOM_ECON_TRANSACTION_SETTLED = 1u << 1u,
    DOM_ECON_TRANSACTION_FAILED = 1u << 2u
};

enum dom_econ_resolve_flags {
    DOM_ECON_RESOLVE_PARTIAL = 1u << 0u,
    DOM_ECON_RESOLVE_SHORTAGE = 1u << 1u,
    DOM_ECON_RESOLVE_CONGESTED = 1u << 2u,
    DOM_ECON_RESOLVE_RISK = 1u << 3u,
    DOM_ECON_RESOLVE_BLACK_MARKET = 1u << 4u
};

enum dom_econ_refusal_reason {
    DOM_ECON_REFUSE_NONE = 0u,
    DOM_ECON_REFUSE_BUDGET = 1u,
    DOM_ECON_REFUSE_DOMAIN_INACTIVE = 2u,
    DOM_ECON_REFUSE_CONTAINER_MISSING = 3u,
    DOM_ECON_REFUSE_STORAGE_MISSING = 4u,
    DOM_ECON_REFUSE_TRANSPORT_MISSING = 5u,
    DOM_ECON_REFUSE_JOB_MISSING = 6u,
    DOM_ECON_REFUSE_MARKET_MISSING = 7u,
    DOM_ECON_REFUSE_OFFER_MISSING = 8u,
    DOM_ECON_REFUSE_BID_MISSING = 9u,
    DOM_ECON_REFUSE_TRANSACTION_MISSING = 10u,
    DOM_ECON_REFUSE_POLICY = 11u,
    DOM_ECON_REFUSE_INTERNAL = 12u
};

typedef struct dom_econ_container_desc {
    u32 container_id;
    q48_16 capacity;
    q48_16 contents_amount;
    q16_16 integrity;
    u32 owner_ref_id;
    u32 location_ref_id;
    u32 storage_ref_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_container_flags */
} dom_econ_container_desc;

typedef struct dom_econ_storage_desc {
    u32 storage_id;
    u32 location_ref_id;
    q48_16 capacity;
    q48_16 stored_amount;
    q16_16 decay_rate;
    q16_16 integrity;
    u32 risk_profile_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_storage_flags */
} dom_econ_storage_desc;

typedef struct dom_econ_transport_desc {
    u32 transport_id;
    u32 vehicle_ref_id;
    u32 route_ref_id;
    q48_16 capacity;
    q48_16 cargo_amount;
    q16_16 travel_cost;
    q16_16 risk_modifier;
    u32 risk_profile_id;
    u32 origin_ref_id;
    u32 destination_ref_id;
    u64 departure_tick;
    u64 arrival_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_transport_flags */
} dom_econ_transport_desc;

typedef struct dom_econ_job_desc {
    u32 job_id;
    u32 job_type; /* dom_econ_job_type */
    u32 task_graph_ref_id;
    u32 worker_ref_id;
    u32 required_skill_ref_id;
    q48_16 energy_cost;
    u64 duration_ticks;
    u64 scheduled_tick;
    u32 input_ref_id;
    u32 output_ref_id;
    u32 risk_profile_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_job_flags */
} dom_econ_job_desc;

typedef struct dom_econ_market_desc {
    u32 market_id;
    u32 location_ref_id;
    u32 jurisdiction_ref_id;
    q48_16 listing_capacity;
    q16_16 transaction_fee;
    u64 info_delay;
    u32 risk_profile_id;
    u32 trust_profile_id;
    u32 law_ref_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_market_flags */
} dom_econ_market_desc;

typedef struct dom_econ_offer_desc {
    u32 offer_id;
    u32 market_id;
    u32 seller_ref_id;
    u32 goods_ref_id;
    q48_16 quantity;
    q48_16 price;
    u32 exchange_medium_ref_id;
    u64 expiry_tick;
    u32 risk_profile_id;
    u32 trust_profile_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_offer_flags */
} dom_econ_offer_desc;

typedef struct dom_econ_bid_desc {
    u32 bid_id;
    u32 market_id;
    u32 buyer_ref_id;
    u32 goods_ref_id;
    q48_16 quantity;
    q48_16 price;
    u32 exchange_medium_ref_id;
    u64 expiry_tick;
    u32 risk_profile_id;
    u32 trust_profile_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_bid_flags */
} dom_econ_bid_desc;

typedef struct dom_econ_transaction_desc {
    u32 transaction_id;
    u32 market_id;
    u32 offer_id;
    u32 bid_id;
    u32 buyer_ref_id;
    u32 seller_ref_id;
    u32 goods_ref_id;
    q48_16 quantity;
    q48_16 price;
    u32 exchange_medium_ref_id;
    u32 transport_ref_id;
    u64 executed_tick;
    u32 risk_profile_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_transaction_flags */
} dom_econ_transaction_desc;

typedef struct dom_econ_container {
    u32 container_id;
    q48_16 capacity;
    q48_16 contents_amount;
    q16_16 integrity;
    u32 owner_ref_id;
    u32 location_ref_id;
    u32 storage_ref_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_container_flags */
} dom_econ_container;

typedef struct dom_econ_storage {
    u32 storage_id;
    u32 location_ref_id;
    q48_16 capacity;
    q48_16 stored_amount;
    q16_16 decay_rate;
    q16_16 integrity;
    u32 risk_profile_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_storage_flags */
} dom_econ_storage;

typedef struct dom_econ_transport {
    u32 transport_id;
    u32 vehicle_ref_id;
    u32 route_ref_id;
    q48_16 capacity;
    q48_16 cargo_amount;
    q16_16 travel_cost;
    q16_16 risk_modifier;
    u32 risk_profile_id;
    u32 origin_ref_id;
    u32 destination_ref_id;
    u64 departure_tick;
    u64 arrival_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_transport_flags */
} dom_econ_transport;

typedef struct dom_econ_job {
    u32 job_id;
    u32 job_type; /* dom_econ_job_type */
    u32 task_graph_ref_id;
    u32 worker_ref_id;
    u32 required_skill_ref_id;
    q48_16 energy_cost;
    u64 duration_ticks;
    u64 scheduled_tick;
    u32 input_ref_id;
    u32 output_ref_id;
    u32 risk_profile_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_job_flags */
} dom_econ_job;

typedef struct dom_econ_market {
    u32 market_id;
    u32 location_ref_id;
    u32 jurisdiction_ref_id;
    q48_16 listing_capacity;
    q16_16 transaction_fee;
    u64 info_delay;
    u32 risk_profile_id;
    u32 trust_profile_id;
    u32 law_ref_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_market_flags */
} dom_econ_market;

typedef struct dom_econ_offer {
    u32 offer_id;
    u32 market_id;
    u32 seller_ref_id;
    u32 goods_ref_id;
    q48_16 quantity;
    q48_16 price;
    u32 exchange_medium_ref_id;
    u64 expiry_tick;
    u32 risk_profile_id;
    u32 trust_profile_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_offer_flags */
} dom_econ_offer;

typedef struct dom_econ_bid {
    u32 bid_id;
    u32 market_id;
    u32 buyer_ref_id;
    u32 goods_ref_id;
    q48_16 quantity;
    q48_16 price;
    u32 exchange_medium_ref_id;
    u64 expiry_tick;
    u32 risk_profile_id;
    u32 trust_profile_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_bid_flags */
} dom_econ_bid;

typedef struct dom_econ_transaction {
    u32 transaction_id;
    u32 market_id;
    u32 offer_id;
    u32 bid_id;
    u32 buyer_ref_id;
    u32 seller_ref_id;
    u32 goods_ref_id;
    q48_16 quantity;
    q48_16 price;
    u32 exchange_medium_ref_id;
    u32 transport_ref_id;
    u64 executed_tick;
    u32 risk_profile_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_transaction_flags */
} dom_econ_transaction;

typedef struct dom_econ_surface_desc {
    dom_domain_id domain_id;
    u64 world_seed;
    q16_16 meters_per_unit;
    u32 container_count;
    dom_econ_container_desc containers[DOM_ECON_MAX_CONTAINERS];
    u32 storage_count;
    dom_econ_storage_desc storages[DOM_ECON_MAX_STORAGES];
    u32 transport_count;
    dom_econ_transport_desc transports[DOM_ECON_MAX_TRANSPORTS];
    u32 job_count;
    dom_econ_job_desc jobs[DOM_ECON_MAX_JOBS];
    u32 market_count;
    dom_econ_market_desc markets[DOM_ECON_MAX_MARKETS];
    u32 offer_count;
    dom_econ_offer_desc offers[DOM_ECON_MAX_OFFERS];
    u32 bid_count;
    dom_econ_bid_desc bids[DOM_ECON_MAX_BIDS];
    u32 transaction_count;
    dom_econ_transaction_desc transactions[DOM_ECON_MAX_TRANSACTIONS];
} dom_econ_surface_desc;

typedef struct dom_econ_container_sample {
    u32 container_id;
    q48_16 capacity;
    q48_16 contents_amount;
    q16_16 integrity;
    u32 owner_ref_id;
    u32 location_ref_id;
    u32 storage_ref_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_container_flags */
    dom_domain_query_meta meta;
} dom_econ_container_sample;

typedef struct dom_econ_storage_sample {
    u32 storage_id;
    u32 location_ref_id;
    q48_16 capacity;
    q48_16 stored_amount;
    q16_16 decay_rate;
    q16_16 integrity;
    u32 risk_profile_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_storage_flags */
    dom_domain_query_meta meta;
} dom_econ_storage_sample;

typedef struct dom_econ_transport_sample {
    u32 transport_id;
    u32 vehicle_ref_id;
    u32 route_ref_id;
    q48_16 capacity;
    q48_16 cargo_amount;
    q16_16 travel_cost;
    q16_16 risk_modifier;
    u32 risk_profile_id;
    u32 origin_ref_id;
    u32 destination_ref_id;
    u64 departure_tick;
    u64 arrival_tick;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_transport_flags */
    dom_domain_query_meta meta;
} dom_econ_transport_sample;

typedef struct dom_econ_job_sample {
    u32 job_id;
    u32 job_type; /* dom_econ_job_type */
    u32 task_graph_ref_id;
    u32 worker_ref_id;
    u32 required_skill_ref_id;
    q48_16 energy_cost;
    u64 duration_ticks;
    u64 scheduled_tick;
    u32 input_ref_id;
    u32 output_ref_id;
    u32 risk_profile_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_job_flags */
    dom_domain_query_meta meta;
} dom_econ_job_sample;

typedef struct dom_econ_market_sample {
    u32 market_id;
    u32 location_ref_id;
    u32 jurisdiction_ref_id;
    q48_16 listing_capacity;
    q16_16 transaction_fee;
    u64 info_delay;
    u32 risk_profile_id;
    u32 trust_profile_id;
    u32 law_ref_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_market_flags */
    dom_domain_query_meta meta;
} dom_econ_market_sample;

typedef struct dom_econ_offer_sample {
    u32 offer_id;
    u32 market_id;
    u32 seller_ref_id;
    u32 goods_ref_id;
    q48_16 quantity;
    q48_16 price;
    u32 exchange_medium_ref_id;
    u64 expiry_tick;
    u32 risk_profile_id;
    u32 trust_profile_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_offer_flags */
    dom_domain_query_meta meta;
} dom_econ_offer_sample;

typedef struct dom_econ_bid_sample {
    u32 bid_id;
    u32 market_id;
    u32 buyer_ref_id;
    u32 goods_ref_id;
    q48_16 quantity;
    q48_16 price;
    u32 exchange_medium_ref_id;
    u64 expiry_tick;
    u32 risk_profile_id;
    u32 trust_profile_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_bid_flags */
    dom_domain_query_meta meta;
} dom_econ_bid_sample;

typedef struct dom_econ_transaction_sample {
    u32 transaction_id;
    u32 market_id;
    u32 offer_id;
    u32 bid_id;
    u32 buyer_ref_id;
    u32 seller_ref_id;
    u32 goods_ref_id;
    q48_16 quantity;
    q48_16 price;
    u32 exchange_medium_ref_id;
    u32 transport_ref_id;
    u64 executed_tick;
    u32 risk_profile_id;
    u32 provenance_id;
    u32 region_id;
    u32 flags; /* dom_econ_transaction_flags */
    dom_domain_query_meta meta;
} dom_econ_transaction_sample;

typedef struct dom_econ_region_sample {
    u32 region_id;
    u32 container_count;
    u32 storage_count;
    u32 transport_count;
    u32 job_count;
    u32 market_count;
    u32 offer_count;
    u32 bid_count;
    u32 transaction_count;
    q48_16 goods_total;
    q48_16 price_avg;
    q48_16 transaction_volume_total;
    u32 flags; /* dom_econ_resolve_flags */
    dom_domain_query_meta meta;
} dom_econ_region_sample;

typedef struct dom_econ_resolve_result {
    u32 ok;
    u32 refusal_reason; /* dom_econ_refusal_reason */
    u32 flags; /* dom_econ_resolve_flags */
    u32 container_count;
    u32 storage_count;
    u32 transport_count;
    u32 transport_arrived_count;
    u32 job_count;
    u32 job_completed_count;
    u32 market_count;
    u32 offer_count;
    u32 bid_count;
    u32 transaction_count;
    u32 transaction_settled_count;
    q48_16 goods_total;
    q48_16 price_avg;
    q48_16 transaction_volume_total;
} dom_econ_resolve_result;

typedef struct dom_econ_macro_capsule {
    u64 capsule_id;
    u32 region_id;
    u32 container_count;
    u32 storage_count;
    u32 transport_count;
    u32 job_count;
    u32 market_count;
    u32 offer_count;
    u32 bid_count;
    u32 transaction_count;
    q48_16 goods_total;
    q48_16 price_avg;
    q48_16 transaction_volume_total;
    q16_16 price_hist[DOM_ECON_HIST_BINS];
    u32 rng_cursor[DOM_ECON_HIST_BINS];
} dom_econ_macro_capsule;

typedef struct dom_econ_domain {
    dom_domain_policy policy;
    u32 existence_state;
    u32 archival_state;
    u32 authoring_version;
    dom_econ_surface_desc surface;
    dom_econ_container containers[DOM_ECON_MAX_CONTAINERS];
    u32 container_count;
    dom_econ_storage storages[DOM_ECON_MAX_STORAGES];
    u32 storage_count;
    dom_econ_transport transports[DOM_ECON_MAX_TRANSPORTS];
    u32 transport_count;
    dom_econ_job jobs[DOM_ECON_MAX_JOBS];
    u32 job_count;
    dom_econ_market markets[DOM_ECON_MAX_MARKETS];
    u32 market_count;
    dom_econ_offer offers[DOM_ECON_MAX_OFFERS];
    u32 offer_count;
    dom_econ_bid bids[DOM_ECON_MAX_BIDS];
    u32 bid_count;
    dom_econ_transaction transactions[DOM_ECON_MAX_TRANSACTIONS];
    u32 transaction_count;
    dom_econ_macro_capsule capsules[DOM_ECON_MAX_CAPSULES];
    u32 capsule_count;
} dom_econ_domain;

void dom_econ_surface_desc_init(dom_econ_surface_desc* desc);

void dom_econ_domain_init(dom_econ_domain* domain,
                          const dom_econ_surface_desc* desc);
void dom_econ_domain_free(dom_econ_domain* domain);
void dom_econ_domain_set_state(dom_econ_domain* domain,
                               u32 existence_state,
                               u32 archival_state);
void dom_econ_domain_set_policy(dom_econ_domain* domain,
                                const dom_domain_policy* policy);

int dom_econ_container_query(const dom_econ_domain* domain,
                             u32 container_id,
                             dom_domain_budget* budget,
                             dom_econ_container_sample* out_sample);

int dom_econ_storage_query(const dom_econ_domain* domain,
                           u32 storage_id,
                           dom_domain_budget* budget,
                           dom_econ_storage_sample* out_sample);

int dom_econ_transport_query(const dom_econ_domain* domain,
                             u32 transport_id,
                             dom_domain_budget* budget,
                             dom_econ_transport_sample* out_sample);

int dom_econ_job_query(const dom_econ_domain* domain,
                       u32 job_id,
                       dom_domain_budget* budget,
                       dom_econ_job_sample* out_sample);

int dom_econ_market_query(const dom_econ_domain* domain,
                          u32 market_id,
                          dom_domain_budget* budget,
                          dom_econ_market_sample* out_sample);

int dom_econ_offer_query(const dom_econ_domain* domain,
                         u32 offer_id,
                         dom_domain_budget* budget,
                         dom_econ_offer_sample* out_sample);

int dom_econ_bid_query(const dom_econ_domain* domain,
                       u32 bid_id,
                       dom_domain_budget* budget,
                       dom_econ_bid_sample* out_sample);

int dom_econ_transaction_query(const dom_econ_domain* domain,
                               u32 transaction_id,
                               dom_domain_budget* budget,
                               dom_econ_transaction_sample* out_sample);

int dom_econ_region_query(const dom_econ_domain* domain,
                          u32 region_id,
                          dom_domain_budget* budget,
                          dom_econ_region_sample* out_sample);

int dom_econ_resolve(dom_econ_domain* domain,
                     u32 region_id,
                     u64 tick,
                     u64 tick_delta,
                     dom_domain_budget* budget,
                     dom_econ_resolve_result* out_result);

int dom_econ_domain_collapse_region(dom_econ_domain* domain, u32 region_id);
int dom_econ_domain_expand_region(dom_econ_domain* domain, u32 region_id);

u32 dom_econ_domain_capsule_count(const dom_econ_domain* domain);
const dom_econ_macro_capsule* dom_econ_domain_capsule_at(const dom_econ_domain* domain,
                                                         u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_WORLD_ECONOMY_FIELDS_H */
