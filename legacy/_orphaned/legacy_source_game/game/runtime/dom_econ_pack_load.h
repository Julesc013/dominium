/*
FILE: source/dominium/game/runtime/dom_econ_pack_load.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/econ_pack_load
RESPONSIBILITY: Loads economy TLV packs and applies them to runtime registries.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_ECON_PACK_LOAD_H
#define DOM_ECON_PACK_LOAD_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

#include "dominium/econ_schema.h"
#include "runtime/dom_asset_registry.h"
#include "runtime/dom_money_standard.h"
#include "runtime/dom_contract_templates.h"
#include "runtime/dom_instrument_registry.h"

enum {
    DOM_ECON_OK = 0,
    DOM_ECON_ERR = -1,
    DOM_ECON_INVALID_ARGUMENT = -2,
    DOM_ECON_INVALID_FORMAT = -3,
    DOM_ECON_MISSING_REQUIRED = -4,
    DOM_ECON_DUPLICATE_ID = -5,
    DOM_ECON_MISSING_REFERENCE = -6,
    DOM_ECON_IO_ERROR = -7
};

struct dom_econ_asset {
    std::string id;
    u64 id_hash;
    u32 kind;
    u32 unit_scale;
    u32 divisibility;
    u32 provenance_required;
    std::string display_name;
    std::string issuer_id;
    u64 issuer_id_hash;

    dom_econ_asset();
};

struct dom_econ_money_standard {
    std::string id;
    u64 id_hash;
    std::string base_asset_id;
    u64 base_asset_id_hash;
    u32 denom_scale;
    u32 rounding_mode;
    std::string display_name;
    std::string convert_rule_id;
    u64 convert_rule_id_hash;

    dom_econ_money_standard();
};

struct dom_econ_contract_obligation {
    std::string role_from_id;
    u64 role_from_hash;
    std::string role_to_id;
    u64 role_to_hash;
    std::string asset_id;
    u64 asset_id_hash;
    i64 amount;
    u64 offset_ticks;

    dom_econ_contract_obligation();
};

struct dom_econ_contract_template {
    std::string id;
    u64 id_hash;
    std::vector<dom_econ_contract_obligation> obligations;

    dom_econ_contract_template();
};

struct dom_econ_instrument {
    std::string id;
    u64 id_hash;
    u32 kind;
    std::string contract_id;
    u64 contract_id_hash;
    std::vector<std::string> asset_ids;
    std::vector<u64> asset_id_hashes;

    dom_econ_instrument();
};

struct dom_econ_state {
    u32 pack_schema_version;
    std::string pack_id;
    u32 pack_version_num;
    std::string pack_version_str;
    u64 content_hash;
    u64 pack_hash;
    u64 sim_digest;
    std::vector<dom_econ_asset> assets;
    std::vector<dom_econ_money_standard> money_standards;
    std::vector<dom_econ_contract_template> contracts;
    std::vector<dom_econ_instrument> instruments;

    dom_econ_state();
};

int dom_econ_load_from_bytes(const unsigned char *data,
                             size_t size,
                             dom_econ_state *out_state,
                             std::string *out_error);
int dom_econ_load_from_file(const char *path,
                            dom_econ_state *out_state,
                            std::string *out_error);

u64 dom_econ_compute_sim_digest(const dom_econ_state *state);

int dom_econ_apply_to_registries(const dom_econ_state *state,
                                 dom_asset_registry *assets,
                                 dom_money_standard_registry *money,
                                 dom_contract_template_registry *contracts,
                                 dom_instrument_registry *instruments,
                                 std::string *out_error);

#endif /* DOM_ECON_PACK_LOAD_H */
