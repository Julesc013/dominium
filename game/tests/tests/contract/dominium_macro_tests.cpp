/*
FILE: tests/contract/dominium_macro_tests.cpp
MODULE: Repository
LAYER / SUBSYSTEM: tests/contract
RESPONSIBILITY: Contract tests for macro economy and macro event determinism.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Macro economy/events must be deterministic under batching.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <cstdio>
#include <cstring>
#include <vector>

#include "runtime/dom_macro_economy.h"
#include "runtime/dom_macro_events.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static void append_u32_le(std::vector<unsigned char> &out, u32 v) {
    out.push_back((unsigned char)(v & 0xffu));
    out.push_back((unsigned char)((v >> 8u) & 0xffu));
    out.push_back((unsigned char)((v >> 16u) & 0xffu));
    out.push_back((unsigned char)((v >> 24u) & 0xffu));
}

static void append_u64_le(std::vector<unsigned char> &out, u64 v) {
    append_u32_le(out, (u32)(v & 0xffffffffull));
    append_u32_le(out, (u32)((v >> 32u) & 0xffffffffull));
}

static void append_i64_le(std::vector<unsigned char> &out, i64 v) {
    append_u64_le(out, (u64)v);
}

static int append_scope_entries(const dom_macro_economy *econ,
                                u32 scope_kind,
                                std::vector<unsigned char> &out) {
    u32 scope_count = 0u;
    if (!econ) {
        append_u32_le(out, 0u);
        return 1;
    }
    if (dom_macro_economy_list_scopes(econ, scope_kind, 0, 0u, &scope_count)
        != DOM_MACRO_ECONOMY_OK) {
        return 0;
    }
    append_u32_le(out, scope_count);
    if (scope_count == 0u) {
        return 1;
    }
    {
        std::vector<dom_macro_scope_info> scopes;
        scopes.resize(scope_count);
        if (dom_macro_economy_list_scopes(econ,
                                          scope_kind,
                                          &scopes[0],
                                          scope_count,
                                          &scope_count) != DOM_MACRO_ECONOMY_OK) {
            return 0;
        }
        if (scopes.size() != scope_count) {
            return 0;
        }
        for (u32 i = 0u; i < scope_count; ++i) {
            const dom_macro_scope_info &info = scopes[i];
            u32 prod_count = 0u;
            u32 demand_count = 0u;
            u32 stock_count = 0u;

            if (dom_macro_economy_list_production(econ,
                                                  scope_kind,
                                                  info.scope_id,
                                                  0,
                                                  0u,
                                                  &prod_count) != DOM_MACRO_ECONOMY_OK) {
                return 0;
            }
            if (dom_macro_economy_list_demand(econ,
                                              scope_kind,
                                              info.scope_id,
                                              0,
                                              0u,
                                              &demand_count) != DOM_MACRO_ECONOMY_OK) {
                return 0;
            }
            if (dom_macro_economy_list_stockpile(econ,
                                                 scope_kind,
                                                 info.scope_id,
                                                 0,
                                                 0u,
                                                 &stock_count) != DOM_MACRO_ECONOMY_OK) {
                return 0;
            }

            append_u64_le(out, info.scope_id);
            append_u32_le(out, info.flags);
            append_u32_le(out, prod_count);
            append_u32_le(out, demand_count);
            append_u32_le(out, stock_count);

            if (prod_count > 0u) {
                std::vector<dom_macro_rate_entry> prod;
                u32 actual = prod_count;
                prod.resize(prod_count);
                if (dom_macro_economy_list_production(econ,
                                                      scope_kind,
                                                      info.scope_id,
                                                      &prod[0],
                                                      prod_count,
                                                      &actual) != DOM_MACRO_ECONOMY_OK) {
                    return 0;
                }
                if (actual != prod_count) {
                    return 0;
                }
                for (u32 j = 0u; j < prod_count; ++j) {
                    append_u64_le(out, prod[j].resource_id);
                    append_i64_le(out, prod[j].rate_per_tick);
                }
            }
            if (demand_count > 0u) {
                std::vector<dom_macro_rate_entry> demand;
                u32 actual = demand_count;
                demand.resize(demand_count);
                if (dom_macro_economy_list_demand(econ,
                                                  scope_kind,
                                                  info.scope_id,
                                                  &demand[0],
                                                  demand_count,
                                                  &actual) != DOM_MACRO_ECONOMY_OK) {
                    return 0;
                }
                if (actual != demand_count) {
                    return 0;
                }
                for (u32 j = 0u; j < demand_count; ++j) {
                    append_u64_le(out, demand[j].resource_id);
                    append_i64_le(out, demand[j].rate_per_tick);
                }
            }
            if (stock_count > 0u) {
                std::vector<dom_macro_stock_entry> stock;
                u32 actual = stock_count;
                stock.resize(stock_count);
                if (dom_macro_economy_list_stockpile(econ,
                                                     scope_kind,
                                                     info.scope_id,
                                                     &stock[0],
                                                     stock_count,
                                                     &actual) != DOM_MACRO_ECONOMY_OK) {
                    return 0;
                }
                if (actual != stock_count) {
                    return 0;
                }
                for (u32 j = 0u; j < stock_count; ++j) {
                    append_u64_le(out, stock[j].resource_id);
                    append_i64_le(out, stock[j].quantity);
                }
            }
        }
    }
    return 1;
}

static int serialize_economy(const dom_macro_economy *econ,
                             std::vector<unsigned char> &out) {
    out.clear();
    if (!append_scope_entries(econ, DOM_MACRO_SCOPE_SYSTEM, out)) {
        return 0;
    }
    if (!append_scope_entries(econ, DOM_MACRO_SCOPE_GALAXY, out)) {
        return 0;
    }
    return 1;
}

static int seed_economy(dom_macro_economy *econ, int reverse_order) {
    if (!econ) {
        return 0;
    }
    if (!reverse_order) {
        if (dom_macro_economy_register_system(econ, 50ull) != DOM_MACRO_ECONOMY_OK) return 0;
        if (dom_macro_economy_register_system(econ, 100ull) != DOM_MACRO_ECONOMY_OK) return 0;
        if (dom_macro_economy_register_galaxy(econ, 2ull) != DOM_MACRO_ECONOMY_OK) return 0;
    } else {
        if (dom_macro_economy_register_galaxy(econ, 2ull) != DOM_MACRO_ECONOMY_OK) return 0;
        if (dom_macro_economy_register_system(econ, 100ull) != DOM_MACRO_ECONOMY_OK) return 0;
        if (dom_macro_economy_register_system(econ, 50ull) != DOM_MACRO_ECONOMY_OK) return 0;
    }

    if (dom_macro_economy_rate_set(econ, DOM_MACRO_SCOPE_SYSTEM, 100ull, 7ull, 10, 20)
        != DOM_MACRO_ECONOMY_OK) return 0;
    if (dom_macro_economy_rate_set(econ, DOM_MACRO_SCOPE_SYSTEM, 50ull, 9ull, -3, 0)
        != DOM_MACRO_ECONOMY_OK) return 0;
    if (dom_macro_economy_rate_set(econ, DOM_MACRO_SCOPE_GALAXY, 2ull, 7ull, 1000, 2000)
        != DOM_MACRO_ECONOMY_OK) return 0;

    if (dom_macro_economy_stockpile_set(econ, DOM_MACRO_SCOPE_SYSTEM, 100ull, 12ull, 500)
        != DOM_MACRO_ECONOMY_OK) return 0;
    if (dom_macro_economy_stockpile_set(econ, DOM_MACRO_SCOPE_GALAXY, 2ull, 12ull, 9000)
        != DOM_MACRO_ECONOMY_OK) return 0;

    if (dom_macro_economy_flags_apply(econ, DOM_MACRO_SCOPE_SYSTEM, 100ull, 0x4u, 0u)
        != DOM_MACRO_ECONOMY_OK) return 0;
    return 1;
}

static int test_macro_economy_determinism(void) {
    dom_macro_economy *a = dom_macro_economy_create();
    dom_macro_economy *b = dom_macro_economy_create();
    std::vector<unsigned char> bytes_a;
    std::vector<unsigned char> bytes_b;

    if (!a || !b) {
        dom_macro_economy_destroy(a);
        dom_macro_economy_destroy(b);
        return fail("macro economy create failed");
    }
    if (!seed_economy(a, 0) || !seed_economy(b, 1)) {
        dom_macro_economy_destroy(a);
        dom_macro_economy_destroy(b);
        return fail("macro economy seed failed");
    }
    if (!serialize_economy(a, bytes_a) || !serialize_economy(b, bytes_b)) {
        dom_macro_economy_destroy(a);
        dom_macro_economy_destroy(b);
        return fail("macro economy serialize failed");
    }
    if (bytes_a.size() != bytes_b.size() ||
        (bytes_a.size() > 0u && std::memcmp(&bytes_a[0], &bytes_b[0], bytes_a.size()) != 0)) {
        dom_macro_economy_destroy(a);
        dom_macro_economy_destroy(b);
        return fail("macro economy determinism mismatch");
    }

    dom_macro_economy_destroy(a);
    dom_macro_economy_destroy(b);
    return 0;
}

static int test_macro_event_fire(void) {
    dom_macro_economy *econ = dom_macro_economy_create();
    dom_macro_economy *econ_batch = dom_macro_economy_create();
    dom_macro_events *events = dom_macro_events_create();
    dom_macro_events *events_batch = dom_macro_events_create();
    dom_macro_event_effect effect;
    dom_macro_event_desc desc;
    dom_macro_scope_info info;
    i64 prod = 0;
    i64 dem = 0;

    if (!econ || !econ_batch || !events || !events_batch) {
        dom_macro_economy_destroy(econ);
        dom_macro_economy_destroy(econ_batch);
        dom_macro_events_destroy(events);
        dom_macro_events_destroy(events_batch);
        return fail("macro events create failed");
    }

    if (dom_macro_economy_register_system(econ, 42ull) != DOM_MACRO_ECONOMY_OK ||
        dom_macro_economy_register_system(econ_batch, 42ull) != DOM_MACRO_ECONOMY_OK) {
        return fail("macro economy register failed");
    }

    effect.resource_id = 7ull;
    effect.production_delta = 5;
    effect.demand_delta = -2;
    effect.flags_set = 0x2u;
    effect.flags_clear = 0u;

    desc.event_id = 1ull;
    desc.scope_kind = DOM_MACRO_SCOPE_SYSTEM;
    desc.scope_id = 42ull;
    desc.trigger_tick = 10ull;
    desc.effect_count = 1u;
    desc.effects = &effect;

    if (dom_macro_events_schedule(events, &desc) != DOM_MACRO_EVENTS_OK ||
        dom_macro_events_schedule(events_batch, &desc) != DOM_MACRO_EVENTS_OK) {
        return fail("macro events schedule failed");
    }

    if (dom_macro_events_update(events, econ, 9ull) != DOM_MACRO_EVENTS_OK) {
        return fail("macro events update pre failed");
    }
    if (dom_macro_economy_rate_get(econ, DOM_MACRO_SCOPE_SYSTEM, 42ull, 7ull, &prod, &dem)
        != DOM_MACRO_ECONOMY_OK) {
        return fail("macro economy rate get failed");
    }
    if (prod != 0 || dem != 0) {
        return fail("macro event applied too early");
    }
    if (dom_macro_economy_get_scope(econ, DOM_MACRO_SCOPE_SYSTEM, 42ull, &info)
        != DOM_MACRO_ECONOMY_OK) {
        return fail("macro economy scope get failed");
    }
    if (info.flags != 0u) {
        return fail("macro event flags applied too early");
    }

    if (dom_macro_events_update(events, econ, 10ull) != DOM_MACRO_EVENTS_OK) {
        return fail("macro events update apply failed");
    }
    if (dom_macro_economy_rate_get(econ, DOM_MACRO_SCOPE_SYSTEM, 42ull, 7ull, &prod, &dem)
        != DOM_MACRO_ECONOMY_OK) {
        return fail("macro economy rate get apply failed");
    }
    if (prod != 5 || dem != -2) {
        return fail("macro event effect mismatch");
    }
    if (dom_macro_economy_get_scope(econ, DOM_MACRO_SCOPE_SYSTEM, 42ull, &info)
        != DOM_MACRO_ECONOMY_OK) {
        return fail("macro economy scope get apply failed");
    }
    if (info.flags != 0x2u) {
        return fail("macro event flags mismatch");
    }

    if (dom_macro_events_update(events, econ, 20ull) != DOM_MACRO_EVENTS_OK) {
        return fail("macro events update post failed");
    }
    if (dom_macro_economy_rate_get(econ, DOM_MACRO_SCOPE_SYSTEM, 42ull, 7ull, &prod, &dem)
        != DOM_MACRO_ECONOMY_OK) {
        return fail("macro economy rate get post failed");
    }
    if (prod != 5 || dem != -2) {
        return fail("macro event reapplied unexpectedly");
    }

    if (dom_macro_events_update(events_batch, econ_batch, 20ull) != DOM_MACRO_EVENTS_OK) {
        return fail("macro events update batch failed");
    }
    if (dom_macro_economy_rate_get(econ_batch, DOM_MACRO_SCOPE_SYSTEM, 42ull, 7ull, &prod, &dem)
        != DOM_MACRO_ECONOMY_OK) {
        return fail("macro economy rate get batch failed");
    }
    if (prod != 5 || dem != -2) {
        return fail("macro event batch mismatch");
    }
    if (dom_macro_economy_get_scope(econ_batch, DOM_MACRO_SCOPE_SYSTEM, 42ull, &info)
        != DOM_MACRO_ECONOMY_OK) {
        return fail("macro economy scope get batch failed");
    }
    if (info.flags != 0x2u) {
        return fail("macro event flags batch mismatch");
    }

    dom_macro_economy_destroy(econ);
    dom_macro_economy_destroy(econ_batch);
    dom_macro_events_destroy(events);
    dom_macro_events_destroy(events_batch);
    return 0;
}

int main(void) {
    int rc = 0;
    if ((rc = test_macro_economy_determinism()) != 0) return rc;
    if ((rc = test_macro_event_fire()) != 0) return rc;
    std::printf("dominium macro tests passed\n");
    return 0;
}
