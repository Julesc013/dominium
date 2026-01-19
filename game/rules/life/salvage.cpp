/*
FILE: game/core/life/salvage.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements salvage claim resolution and ledger transfers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Resolution order and IDs are deterministic.
*/
#include "dominium/life/salvage.h"

#include <string.h>

static u64 life_hash_mix(u64 h, u64 v)
{
    const u64 prime = 1099511628211ULL;
    h ^= v;
    h *= prime;
    return h;
}

void life_salvage_claim_registry_init(life_salvage_claim_registry* reg,
                                      life_salvage_claim* storage,
                                      u32 capacity,
                                      u64 start_id)
{
    if (!reg) {
        return;
    }
    reg->claims = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    reg->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_salvage_claim) * (size_t)capacity);
    }
}

void life_salvage_outcome_registry_init(life_salvage_outcome_registry* reg,
                                        life_salvage_outcome* storage,
                                        u32 capacity,
                                        u64 start_id)
{
    if (!reg) {
        return;
    }
    reg->outcomes = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    reg->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_salvage_outcome) * (size_t)capacity);
    }
}

int life_salvage_claim_create(life_salvage_context* ctx,
                              u64 claimant_id,
                              dom_account_id_t claimant_account_id,
                              u64 remains_id,
                              u32 claim_basis,
                              dom_act_time_t resolution_tick,
                              u64* out_claim_id)
{
    life_salvage_claim* claim;
    if (!ctx || !ctx->claims || !ctx->claims->claims) {
        return -1;
    }
    if (ctx->claims->count >= ctx->claims->capacity) {
        return -2;
    }
    claim = &ctx->claims->claims[ctx->claims->count++];
    memset(claim, 0, sizeof(*claim));
    claim->claim_id = ctx->claims->next_id++;
    claim->claimant_id = claimant_id;
    claim->claimant_account_id = claimant_account_id;
    claim->remains_id = remains_id;
    claim->claim_basis = claim_basis;
    claim->status = LIFE_SALVAGE_PENDING;
    claim->resolution_tick = resolution_tick;
    claim->refusal_code = LIFE_SALVAGE_REFUSAL_NONE;
    if (out_claim_id) {
        *out_claim_id = claim->claim_id;
    }
    return 0;
}

static int life_salvage_best_basis(const life_post_death_rights* rights,
                                   const life_estate_registry* estates)
{
    if (!rights) {
        return 0;
    }
    if (rights->has_contract) {
        return LIFE_SALVAGE_BASIS_CONTRACT;
    }
    if (rights->estate_id != 0u) {
        const life_estate* estate = life_estate_find_by_id((life_estate_registry*)estates,
                                                          rights->estate_id);
        if (rights->estate_locked) {
            return -LIFE_SALVAGE_BASIS_ESTATE_EXECUTOR;
        }
        if (estate && estate->has_executor_authority) {
            return LIFE_SALVAGE_BASIS_ESTATE_EXECUTOR;
        }
    }
    if (rights->jurisdiction_allows) {
        return LIFE_SALVAGE_BASIS_JURISDICTION;
    }
    if (rights->allow_finder) {
        return LIFE_SALVAGE_BASIS_FINDER;
    }
    return 0;
}

static int life_salvage_transfer_assets(dom_ledger* ledger,
                                        dom_account_id_t from_account,
                                        dom_account_id_t to_account,
                                        dom_act_time_t act_time,
                                        dom_transaction_id_t* out_tx_id)
{
    dom_ledger_account account;
    dom_ledger_posting postings[DOM_LEDGER_MAX_POSTINGS];
    dom_ledger_transaction tx;
    dom_transaction_id_t tx_id = 0;
    u32 posting_count = 0u;
    u32 i;

    if (!ledger || from_account == 0u || to_account == 0u) {
        return -1;
    }
    if (dom_ledger_account_copy(ledger, from_account, &account) != DOM_LEDGER_OK) {
        return -2;
    }
    for (i = 0u; i < account.asset_count; ++i) {
        const dom_ledger_asset_slot* slot = &account.assets[i];
        dom_amount_t balance = slot->balance;
        if (balance == 0) {
            continue;
        }
        if (posting_count + 2u > DOM_LEDGER_MAX_POSTINGS) {
            return -3;
        }
        postings[posting_count].account_id = from_account;
        postings[posting_count].asset_id = slot->asset_id;
        postings[posting_count].amount = -balance;
        postings[posting_count].lot_id = 0u;
        postings[posting_count].provenance_id = 0u;
        posting_count += 1u;

        postings[posting_count].account_id = to_account;
        postings[posting_count].asset_id = slot->asset_id;
        postings[posting_count].amount = balance;
        postings[posting_count].lot_id = 0u;
        postings[posting_count].provenance_id = 0u;
        posting_count += 1u;
    }

    if (posting_count == 0u) {
        return 1;
    }

    if (dom_ledger_next_tx_id(ledger, &tx_id) != DOM_LEDGER_OK) {
        return -4;
    }
    tx.tx_id = tx_id;
    tx.posting_count = posting_count;
    tx.postings = postings;
    if (dom_ledger_transaction_apply(ledger, &tx, act_time) != DOM_LEDGER_OK) {
        return -5;
    }
    if (out_tx_id) {
        *out_tx_id = tx_id;
    }
    return 0;
}

int life_salvage_resolve_claim(life_salvage_context* ctx,
                               u64 claim_id,
                               life_salvage_refusal_code* out_refusal,
                               u64* out_outcome_id)
{
    u32 i;
    life_salvage_claim* claim = 0;
    life_remains* remains = 0;
    life_post_death_rights* rights = 0;
    int best_basis = 0;
    life_salvage_outcome outcome;
    life_salvage_refusal_code refusal = LIFE_SALVAGE_REFUSAL_NONE;
    dom_transaction_id_t tx_id = 0;
    int transfer_rc = 0;

    if (out_refusal) {
        *out_refusal = LIFE_SALVAGE_REFUSAL_NONE;
    }
    if (!ctx || !ctx->claims || !ctx->remains || !ctx->rights) {
        return -1;
    }
    for (i = 0u; i < ctx->claims->count; ++i) {
        if (ctx->claims->claims[i].claim_id == claim_id) {
            claim = &ctx->claims->claims[i];
            break;
        }
    }
    if (!claim) {
        refusal = LIFE_SALVAGE_REFUSAL_REMAINS_NOT_FOUND;
        goto refuse_out;
    }
    remains = life_remains_find(ctx->remains, claim->remains_id);
    if (!remains) {
        refusal = LIFE_SALVAGE_REFUSAL_REMAINS_NOT_FOUND;
        goto refuse_out;
    }
    if (ctx->epistemic && !life_remains_epistemic_knows(ctx->epistemic, remains->remains_id)) {
        refusal = LIFE_SALVAGE_REFUSAL_INSUFFICIENT_EPISTEMIC_KNOWLEDGE;
        goto refuse_out;
    }
    if (remains->active_claim_id != 0u && remains->active_claim_id != claim->claim_id) {
        refusal = LIFE_SALVAGE_REFUSAL_ALREADY_CLAIMED;
        goto refuse_out;
    }
    rights = life_post_death_rights_find(ctx->rights, remains->ownership_rights_ref);
    if (!rights) {
        refusal = LIFE_SALVAGE_REFUSAL_NO_RIGHTS_TO_CLAIM;
        goto refuse_out;
    }

    best_basis = life_salvage_best_basis(rights, ctx->estates);
    if (best_basis == 0) {
        refusal = LIFE_SALVAGE_REFUSAL_NO_RIGHTS_TO_CLAIM;
        goto refuse_out;
    }
    if (best_basis < 0) {
        refusal = LIFE_SALVAGE_REFUSAL_ESTATE_LOCKED;
        goto refuse_out;
    }
    if ((u32)best_basis != claim->claim_basis) {
        if ((u32)best_basis == LIFE_SALVAGE_BASIS_JURISDICTION &&
            claim->claim_basis == LIFE_SALVAGE_BASIS_FINDER) {
            refusal = LIFE_SALVAGE_REFUSAL_JURISDICTION_REFUSES;
        } else {
            refusal = LIFE_SALVAGE_REFUSAL_NO_RIGHTS_TO_CLAIM;
        }
        goto refuse_out;
    }

    transfer_rc = 0;
    if (ctx->ledger && remains->inventory_account_id != 0u) {
        transfer_rc = life_salvage_transfer_assets(ctx->ledger,
                                                   remains->inventory_account_id,
                                                   claim->claimant_account_id,
                                                   claim->resolution_tick,
                                                   &tx_id);
        if (transfer_rc < 0) {
            return -2;
        }
    }

    if (ctx->owners && claim->claimant_id != 0u && remains->inventory_account_id != 0u) {
        (void)life_account_owner_set(ctx->owners,
                                     remains->inventory_account_id,
                                     LIFE_ACCOUNT_OWNER_PERSON,
                                     claim->claimant_id);
    }

    memset(&outcome, 0, sizeof(outcome));
    outcome.claim_id = claim->claim_id;
    outcome.tx_count = (transfer_rc == 0 && tx_id != 0u) ? 1u : 0u;
    if (outcome.tx_count > 0u) {
        outcome.tx_ids[0] = tx_id;
    }
    outcome.provenance_hash = life_hash_mix(1469598103934665603ULL, remains->remains_id);

    if (ctx->outcomes && ctx->outcomes->outcomes) {
        if (ctx->outcomes->count >= ctx->outcomes->capacity) {
            return -3;
        }
        outcome.outcome_id = ctx->outcomes->next_id++;
        ctx->outcomes->outcomes[ctx->outcomes->count++] = outcome;
        if (out_outcome_id) {
            *out_outcome_id = outcome.outcome_id;
        }
    }

    claim->status = LIFE_SALVAGE_ACCEPTED;
    claim->refusal_code = LIFE_SALVAGE_REFUSAL_NONE;
    remains->active_claim_id = claim->claim_id;
    if (out_refusal) {
        *out_refusal = LIFE_SALVAGE_REFUSAL_NONE;
    }
    return 0;

refuse_out:
    if (claim) {
        claim->status = LIFE_SALVAGE_REFUSED;
        claim->refusal_code = refusal;
    }
    if (out_refusal) {
        *out_refusal = refusal;
    }
    return 1;
}

const char* life_salvage_refusal_to_string(life_salvage_refusal_code code)
{
    switch (code) {
        case LIFE_SALVAGE_REFUSAL_NONE: return "none";
        case LIFE_SALVAGE_REFUSAL_NO_RIGHTS_TO_CLAIM: return "no_rights_to_claim";
        case LIFE_SALVAGE_REFUSAL_ESTATE_LOCKED: return "estate_locked";
        case LIFE_SALVAGE_REFUSAL_JURISDICTION_REFUSES: return "jurisdiction_refuses";
        case LIFE_SALVAGE_REFUSAL_REMAINS_NOT_FOUND: return "remains_not_found";
        case LIFE_SALVAGE_REFUSAL_ALREADY_CLAIMED: return "already_claimed";
        case LIFE_SALVAGE_REFUSAL_INSUFFICIENT_EPISTEMIC_KNOWLEDGE: return "insufficient_epistemic_knowledge";
        default: return "unknown";
    }
}
