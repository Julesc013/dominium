/*
FILE: include/dominium/life/salvage.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines salvage claims and deterministic resolution.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Resolution order and IDs are deterministic.
*/
#ifndef DOMINIUM_LIFE_SALVAGE_H
#define DOMINIUM_LIFE_SALVAGE_H

#include "domino/core/dom_ledger.h"
#include "domino/core/dom_time_core.h"
#include "dominium/life/estate.h"
#include "dominium/life/remains.h"
#include "dominium/life/rights_post_death.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum life_salvage_claim_basis {
    LIFE_SALVAGE_BASIS_CONTRACT = 1,
    LIFE_SALVAGE_BASIS_ESTATE_EXECUTOR = 2,
    LIFE_SALVAGE_BASIS_JURISDICTION = 3,
    LIFE_SALVAGE_BASIS_FINDER = 4
} life_salvage_claim_basis;

typedef enum life_salvage_claim_status {
    LIFE_SALVAGE_PENDING = 1,
    LIFE_SALVAGE_ACCEPTED = 2,
    LIFE_SALVAGE_REFUSED = 3
} life_salvage_claim_status;

typedef enum life_salvage_refusal_code {
    LIFE_SALVAGE_REFUSAL_NONE = 0,
    LIFE_SALVAGE_REFUSAL_NO_RIGHTS_TO_CLAIM,
    LIFE_SALVAGE_REFUSAL_ESTATE_LOCKED,
    LIFE_SALVAGE_REFUSAL_JURISDICTION_REFUSES,
    LIFE_SALVAGE_REFUSAL_REMAINS_NOT_FOUND,
    LIFE_SALVAGE_REFUSAL_ALREADY_CLAIMED,
    LIFE_SALVAGE_REFUSAL_INSUFFICIENT_EPISTEMIC_KNOWLEDGE
} life_salvage_refusal_code;

typedef struct life_salvage_claim {
    u64 claim_id;
    u64 claimant_id;
    dom_account_id_t claimant_account_id;
    u64 remains_id;
    u32 claim_basis;
    u32 status;
    dom_act_time_t resolution_tick;
    u32 refusal_code;
} life_salvage_claim;

typedef struct life_salvage_outcome {
    u64 outcome_id;
    u64 claim_id;
    u32 tx_count;
    dom_transaction_id_t tx_ids[4];
    u64 provenance_hash;
} life_salvage_outcome;

typedef struct life_salvage_claim_registry {
    life_salvage_claim* claims;
    u32 count;
    u32 capacity;
    u64 next_id;
} life_salvage_claim_registry;

typedef struct life_salvage_outcome_registry {
    life_salvage_outcome* outcomes;
    u32 count;
    u32 capacity;
    u64 next_id;
} life_salvage_outcome_registry;

typedef struct life_salvage_context {
    life_salvage_claim_registry* claims;
    life_salvage_outcome_registry* outcomes;
    life_remains_registry* remains;
    life_post_death_rights_registry* rights;
    life_estate_registry* estates;
    life_account_owner_registry* owners;
    dom_ledger* ledger;
    const life_remains_epistemic_set* epistemic;
} life_salvage_context;

void life_salvage_claim_registry_init(life_salvage_claim_registry* reg,
                                      life_salvage_claim* storage,
                                      u32 capacity,
                                      u64 start_id);
void life_salvage_outcome_registry_init(life_salvage_outcome_registry* reg,
                                        life_salvage_outcome* storage,
                                        u32 capacity,
                                        u64 start_id);
int life_salvage_claim_create(life_salvage_context* ctx,
                              u64 claimant_id,
                              dom_account_id_t claimant_account_id,
                              u64 remains_id,
                              u32 claim_basis,
                              dom_act_time_t resolution_tick,
                              u64* out_claim_id);
int life_salvage_resolve_claim(life_salvage_context* ctx,
                               u64 claim_id,
                               life_salvage_refusal_code* out_refusal,
                               u64* out_outcome_id);

const char* life_salvage_refusal_to_string(life_salvage_refusal_code code);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_SALVAGE_H */
