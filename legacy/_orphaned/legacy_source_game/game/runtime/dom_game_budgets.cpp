/*
FILE: source/dominium/game/runtime/dom_game_budgets.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_budgets
RESPONSIBILITY: Provides deterministic budget profiles by perf tier (non-sim).
*/
#include "runtime/dom_game_budgets.h"

#include <cstring>

#include "dominium/caps_split.h"

namespace {

static u32 sanitize_tier(u32 tier) {
    if (tier == dom::DOM_PERF_TIER_MODERN || tier == dom::DOM_PERF_TIER_SERVER) {
        return tier;
    }
    return dom::DOM_PERF_TIER_BASELINE;
}

static void set_baseline(dom_game_budget_profile *out_profile) {
    out_profile->derived_budget_ms = 2u;
    out_profile->derived_budget_io_bytes = 256u * 1024u;
    out_profile->derived_budget_jobs = 4u;
    out_profile->ai_max_ops_per_tick = 8u;
    out_profile->ai_max_factions_per_tick = 4u;
}

static void set_modern(dom_game_budget_profile *out_profile) {
    out_profile->derived_budget_ms = 4u;
    out_profile->derived_budget_io_bytes = 512u * 1024u;
    out_profile->derived_budget_jobs = 8u;
    out_profile->ai_max_ops_per_tick = 16u;
    out_profile->ai_max_factions_per_tick = 8u;
}

static void set_server(dom_game_budget_profile *out_profile) {
    out_profile->derived_budget_ms = 8u;
    out_profile->derived_budget_io_bytes = 2u * 1024u * 1024u;
    out_profile->derived_budget_jobs = 16u;
    out_profile->ai_max_ops_per_tick = 32u;
    out_profile->ai_max_factions_per_tick = 16u;
}

} // namespace

int dom_game_budget_profile_for_tier(u32 perf_tier,
                                     dom_game_budget_profile *out_profile) {
    if (!out_profile) {
        return DOM_GAME_BUDGET_INVALID_ARGUMENT;
    }
    std::memset(out_profile, 0, sizeof(*out_profile));
    out_profile->struct_size = (u32)sizeof(*out_profile);
    out_profile->struct_version = DOM_GAME_BUDGET_PROFILE_VERSION;

    perf_tier = sanitize_tier(perf_tier);
    out_profile->perf_tier = perf_tier;
    switch (perf_tier) {
    case dom::DOM_PERF_TIER_MODERN:
        set_modern(out_profile);
        break;
    case dom::DOM_PERF_TIER_SERVER:
        set_server(out_profile);
        break;
    case dom::DOM_PERF_TIER_BASELINE:
    default:
        set_baseline(out_profile);
        break;
    }
    return DOM_GAME_BUDGET_OK;
}
