/*
TEST: dom_money_standard_roundtrip_test
PURPOSE: Money standard render/parse round-trip determinism.
*/
#include "runtime/dom_money_standard.h"

#include <stdio.h>

#include "dominium/econ_schema.h"

extern "C" {
#include "domino/core/spacetime.h"
}

int main(void) {
    dom_money_standard_registry *reg = dom_money_standard_registry_create();
    dom_money_standard_desc desc;
    dom_money_rendered rendered;
    i64 amount_in = 12345;
    i64 amount_out = 0;
    int rc;

    if (!reg) {
        return 1;
    }

    desc.id = "credit";
    desc.id_len = 6u;
    if (dom_id_hash64(desc.id, desc.id_len, &desc.id_hash) != DOM_SPACETIME_OK) {
        dom_money_standard_registry_destroy(reg);
        return 2;
    }
    desc.base_asset_id = "asset_credit";
    desc.base_asset_id_len = 12u;
    if (dom_id_hash64(desc.base_asset_id, desc.base_asset_id_len, &desc.base_asset_id_hash) != DOM_SPACETIME_OK) {
        dom_money_standard_registry_destroy(reg);
        return 3;
    }
    desc.denom_scale = 100u;
    desc.rounding_mode = ECON_MONEY_ROUND_TRUNCATE;
    desc.display_name = "Credit";
    desc.display_name_len = 6u;
    desc.convert_rule_id = 0;
    desc.convert_rule_id_len = 0u;
    desc.convert_rule_id_hash = 0ull;

    rc = dom_money_standard_registry_register(reg, &desc);
    if (rc != DOM_MONEY_OK) {
        dom_money_standard_registry_destroy(reg);
        return 4;
    }

    rc = dom_money_standard_render(reg, desc.id_hash, amount_in, &rendered);
    if (rc != DOM_MONEY_OK) {
        dom_money_standard_registry_destroy(reg);
        return 5;
    }

    rc = dom_money_standard_parse(reg, desc.id_hash, &rendered, &amount_out);
    if (rc != DOM_MONEY_OK) {
        dom_money_standard_registry_destroy(reg);
        return 6;
    }

    if (amount_out != amount_in) {
        dom_money_standard_registry_destroy(reg);
        return 7;
    }

    dom_money_standard_registry_destroy(reg);
    return 0;
}
