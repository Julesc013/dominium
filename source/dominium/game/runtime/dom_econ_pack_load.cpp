/*
FILE: source/dominium/game/runtime/dom_econ_pack_load.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/econ_pack_load
RESPONSIBILITY: Loads economy TLV packs and applies them to runtime registries.
*/
#include <algorithm>
#include <fstream>
#include <sstream>

#include "dominium/core_tlv.h"
#include "runtime/dom_io_guard.h"

extern "C" {
#include "domino/core/spacetime.h"
}

namespace {

static void set_error(std::string *out, const char *msg) {
    if (out) {
        out->assign(msg ? msg : "");
    }
}

static bool read_file_bytes(const char *path,
                            std::vector<unsigned char> &out,
                            std::string &err) {
    std::ifstream in;
    std::streamoff size;
    if (!path || !path[0]) {
        err = "path_empty";
        return false;
    }
    if (!dom_io_guard_io_allowed()) {
        dom_io_guard_note_violation("econ_pack_read", path);
        err = "io_not_allowed";
        return false;
    }
    in.open(path, std::ios::in | std::ios::binary);
    if (!in) {
        err = "open_failed";
        return false;
    }
    in.seekg(0, std::ios::end);
    size = in.tellg();
    if (size <= 0) {
        err = "empty_file";
        return false;
    }
    in.seekg(0, std::ios::beg);
    out.assign((size_t)size, 0u);
    in.read(reinterpret_cast<char *>(&out[0]), size);
    if (!in.good() && !in.eof()) {
        err = "read_failed";
        return false;
    }
    return true;
}

static bool id_hash64(const std::string &id, u64 &out_hash) {
    if (id.empty()) {
        out_hash = 0ull;
        return false;
    }
    return dom_id_hash64(id.c_str(), (u32)id.size(), &out_hash) == DOM_SPACETIME_OK;
}

static bool read_u32(const dom::core_tlv::TlvRecord &rec, u32 &out) {
    return dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, out);
}

static bool read_u64(const dom::core_tlv::TlvRecord &rec, u64 &out) {
    return dom::core_tlv::tlv_read_u64_le(rec.payload, rec.len, out);
}

static bool read_i64(const dom::core_tlv::TlvRecord &rec, i64 &out) {
    u64 tmp = 0ull;
    if (!dom::core_tlv::tlv_read_u64_le(rec.payload, rec.len, tmp)) {
        return false;
    }
    out = (i64)tmp;
    return true;
}

static std::string read_string(const dom::core_tlv::TlvRecord &rec) {
    return dom::core_tlv::tlv_read_string(rec.payload, rec.len);
}

static u64 hash_record(u32 type_id, u16 version, const std::vector<unsigned char> &payload) {
    unsigned char header[8];
    dom::core_tlv::tlv_write_u32_le(header, type_id);
    dom::core_tlv::tlv_write_u32_le(header + 4u, (u32)version);
    std::vector<unsigned char> tmp;
    tmp.reserve(sizeof(header) + payload.size());
    tmp.insert(tmp.end(), header, header + sizeof(header));
    if (!payload.empty()) {
        tmp.insert(tmp.end(), payload.begin(), payload.end());
    }
    return dom::core_tlv::tlv_fnv1a64(tmp.empty() ? 0 : &tmp[0], tmp.size());
}

struct RecordView {
    u32 type_id;
    std::string id;
    u64 id_hash;
    std::vector<unsigned char> payload;
    u64 record_hash;
};

static bool record_less(const RecordView &a, const RecordView &b) {
    if (a.type_id != b.type_id) {
        return a.type_id < b.type_id;
    }
    if (a.id_hash != b.id_hash) {
        return a.id_hash < b.id_hash;
    }
    return a.id < b.id;
}

static bool record_is_canonical(const std::vector<RecordView> &records) {
    size_t i;
    for (i = 1u; i < records.size(); ++i) {
        if (record_less(records[i], records[i - 1u])) {
            return false;
        }
    }
    return true;
}

static u64 hash_content(const std::vector<RecordView> &records) {
    std::vector<unsigned char> buf;
    size_t i;
    buf.reserve(records.size() * 8u);
    for (i = 0u; i < records.size(); ++i) {
        unsigned char tmp[8];
        dom::core_tlv::tlv_write_u64_le(tmp, records[i].record_hash);
        buf.insert(buf.end(), tmp, tmp + 8u);
    }
    return dom::core_tlv::tlv_fnv1a64(buf.empty() ? 0 : &buf[0], buf.size());
}

// -- pack parsing helpers -------------------------------------------------
static bool parse_pack_meta(const unsigned char *data,
                            u32 len,
                            dom_econ_state &out_state,
                            std::string &err) {
    dom::core_tlv::TlvReader r(data, len);
    dom::core_tlv::TlvRecord rec;
    bool has_schema = false;
    bool has_pack_id = false;
    bool has_ver = false;
    bool has_hash = false;

    while (r.next(rec)) {
        switch (rec.tag) {
        case ECON_META_TAG_PACK_SCHEMA_VERSION:
            if (read_u32(rec, out_state.pack_schema_version)) {
                has_schema = true;
            }
            break;
        case ECON_META_TAG_PACK_ID:
            out_state.pack_id = read_string(rec);
            has_pack_id = !out_state.pack_id.empty();
            break;
        case ECON_META_TAG_PACK_VERSION_NUM:
            if (read_u32(rec, out_state.pack_version_num)) {
                has_ver = true;
            }
            break;
        case ECON_META_TAG_PACK_VERSION_STR:
            out_state.pack_version_str = read_string(rec);
            break;
        case ECON_META_TAG_CONTENT_HASH:
            if (read_u64(rec, out_state.content_hash)) {
                has_hash = true;
            }
            break;
        default:
            err = "pack_meta_unknown_tag";
            return false;
        }
    }

    if (r.remaining() != 0u) {
        err = "pack_meta_truncated";
        return false;
    }
    if (!has_schema || !has_pack_id || !has_ver || !has_hash) {
        err = "pack_meta_missing_field";
        return false;
    }
    return true;
}

static bool parse_asset_record(const std::vector<unsigned char> &payload,
                               dom_econ_asset &out,
                               std::string &err) {
    dom::core_tlv::TlvReader r(payload.empty() ? 0 : &payload[0], payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_id = false;
    bool has_id_hash = false;
    bool has_kind = false;
    bool has_unit = false;
    bool has_div = false;
    bool has_prov = false;
    u64 computed = 0ull;

    out = dom_econ_asset();

    while (r.next(rec)) {
        switch (rec.tag) {
        case ECON_ASSET_TAG_ID:
            out.id = read_string(rec);
            has_id = !out.id.empty();
            break;
        case ECON_ASSET_TAG_ID_HASH:
            has_id_hash = read_u64(rec, out.id_hash);
            break;
        case ECON_ASSET_TAG_KIND:
            has_kind = read_u32(rec, out.kind);
            break;
        case ECON_ASSET_TAG_UNIT_SCALE:
            has_unit = read_u32(rec, out.unit_scale);
            break;
        case ECON_ASSET_TAG_DIVISIBILITY:
            has_div = read_u32(rec, out.divisibility);
            break;
        case ECON_ASSET_TAG_PROVENANCE_REQ:
            has_prov = read_u32(rec, out.provenance_required);
            break;
        case ECON_ASSET_TAG_DISPLAY_NAME:
            out.display_name = read_string(rec);
            break;
        case ECON_ASSET_TAG_ISSUER_ID:
            out.issuer_id = read_string(rec);
            break;
        case ECON_ASSET_TAG_ISSUER_ID_HASH:
            read_u64(rec, out.issuer_id_hash);
            break;
        default:
            err = "asset_unknown_tag";
            return false;
        }
    }

    if (r.remaining() != 0u) {
        err = "asset_truncated";
        return false;
    }
    if (!has_id || !has_id_hash || !has_kind || !has_unit || !has_div || !has_prov) {
        err = "asset_missing_field";
        return false;
    }
    if (!id_hash64(out.id, computed) || computed != out.id_hash) {
        err = "asset_id_hash_mismatch";
        return false;
    }
    if (!out.issuer_id.empty()) {
        if (!id_hash64(out.issuer_id, computed)) {
            err = "asset_issuer_hash_failed";
            return false;
        }
        if (out.issuer_id_hash != 0ull && computed != out.issuer_id_hash) {
            err = "asset_issuer_hash_mismatch";
            return false;
        }
        out.issuer_id_hash = computed;
    }
    return true;
}

static bool parse_money_record(const std::vector<unsigned char> &payload,
                               dom_econ_money_standard &out,
                               std::string &err) {
    dom::core_tlv::TlvReader r(payload.empty() ? 0 : &payload[0], payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_id = false;
    bool has_id_hash = false;
    bool has_base = false;
    bool has_base_hash = false;
    bool has_scale = false;
    bool has_round = false;
    u64 computed = 0ull;

    out = dom_econ_money_standard();

    while (r.next(rec)) {
        switch (rec.tag) {
        case ECON_MONEY_TAG_ID:
            out.id = read_string(rec);
            has_id = !out.id.empty();
            break;
        case ECON_MONEY_TAG_ID_HASH:
            has_id_hash = read_u64(rec, out.id_hash);
            break;
        case ECON_MONEY_TAG_BASE_ASSET_ID:
            out.base_asset_id = read_string(rec);
            has_base = !out.base_asset_id.empty();
            break;
        case ECON_MONEY_TAG_BASE_ASSET_HASH:
            has_base_hash = read_u64(rec, out.base_asset_id_hash);
            break;
        case ECON_MONEY_TAG_DENOM_SCALE:
            has_scale = read_u32(rec, out.denom_scale);
            break;
        case ECON_MONEY_TAG_ROUNDING_MODE:
            has_round = read_u32(rec, out.rounding_mode);
            break;
        case ECON_MONEY_TAG_DISPLAY_NAME:
            out.display_name = read_string(rec);
            break;
        case ECON_MONEY_TAG_CONVERT_RULE_ID:
            out.convert_rule_id = read_string(rec);
            break;
        case ECON_MONEY_TAG_CONVERT_RULE_HASH:
            read_u64(rec, out.convert_rule_id_hash);
            break;
        default:
            err = "money_unknown_tag";
            return false;
        }
    }

    if (r.remaining() != 0u) {
        err = "money_truncated";
        return false;
    }
    if (!has_id || !has_id_hash || !has_base || !has_base_hash || !has_scale || !has_round) {
        err = "money_missing_field";
        return false;
    }
    if (!id_hash64(out.id, computed) || computed != out.id_hash) {
        err = "money_id_hash_mismatch";
        return false;
    }
    if (!id_hash64(out.base_asset_id, computed) || computed != out.base_asset_id_hash) {
        err = "money_base_hash_mismatch";
        return false;
    }
    if (!out.convert_rule_id.empty()) {
        if (!id_hash64(out.convert_rule_id, computed)) {
            err = "money_convert_hash_failed";
            return false;
        }
        if (out.convert_rule_id_hash != 0ull && computed != out.convert_rule_id_hash) {
            err = "money_convert_hash_mismatch";
            return false;
        }
        out.convert_rule_id_hash = computed;
    }
    return true;
}

static bool parse_obligation(const unsigned char *payload,
                             u32 len,
                             dom_econ_contract_obligation &out,
                             std::string &err) {
    dom::core_tlv::TlvReader r(payload, len);
    dom::core_tlv::TlvRecord rec;
    bool has_from = false;
    bool has_from_hash = false;
    bool has_to = false;
    bool has_to_hash = false;
    bool has_asset = false;
    bool has_asset_hash = false;
    bool has_amount = false;
    bool has_offset = false;
    u64 computed = 0ull;

    out = dom_econ_contract_obligation();

    while (r.next(rec)) {
        switch (rec.tag) {
        case ECON_OBL_TAG_ROLE_FROM_ID:
            out.role_from_id = read_string(rec);
            has_from = !out.role_from_id.empty();
            break;
        case ECON_OBL_TAG_ROLE_FROM_HASH:
            has_from_hash = read_u64(rec, out.role_from_hash);
            break;
        case ECON_OBL_TAG_ROLE_TO_ID:
            out.role_to_id = read_string(rec);
            has_to = !out.role_to_id.empty();
            break;
        case ECON_OBL_TAG_ROLE_TO_HASH:
            has_to_hash = read_u64(rec, out.role_to_hash);
            break;
        case ECON_OBL_TAG_ASSET_ID:
            out.asset_id = read_string(rec);
            has_asset = !out.asset_id.empty();
            break;
        case ECON_OBL_TAG_ASSET_HASH:
            has_asset_hash = read_u64(rec, out.asset_id_hash);
            break;
        case ECON_OBL_TAG_AMOUNT_I64:
            has_amount = read_i64(rec, out.amount);
            break;
        case ECON_OBL_TAG_OFFSET_TICKS:
            has_offset = read_u64(rec, out.offset_ticks);
            break;
        default:
            err = "obligation_unknown_tag";
            return false;
        }
    }
    if (r.remaining() != 0u) {
        err = "obligation_truncated";
        return false;
    }
    if (!has_from || !has_from_hash || !has_to || !has_to_hash ||
        !has_asset || !has_asset_hash || !has_amount || !has_offset) {
        err = "obligation_missing_field";
        return false;
    }
    if (!id_hash64(out.role_from_id, computed) || computed != out.role_from_hash) {
        err = "obligation_from_hash_mismatch";
        return false;
    }
    if (!id_hash64(out.role_to_id, computed) || computed != out.role_to_hash) {
        err = "obligation_to_hash_mismatch";
        return false;
    }
    if (!id_hash64(out.asset_id, computed) || computed != out.asset_id_hash) {
        err = "obligation_asset_hash_mismatch";
        return false;
    }
    return true;
}

static bool parse_contract_record(const std::vector<unsigned char> &payload,
                                  dom_econ_contract_template &out,
                                  std::string &err) {
    dom::core_tlv::TlvReader r(payload.empty() ? 0 : &payload[0], payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_id = false;
    bool has_id_hash = false;
    u64 computed = 0ull;

    out = dom_econ_contract_template();

    while (r.next(rec)) {
        switch (rec.tag) {
        case ECON_CONTRACT_TAG_ID:
            out.id = read_string(rec);
            has_id = !out.id.empty();
            break;
        case ECON_CONTRACT_TAG_ID_HASH:
            has_id_hash = read_u64(rec, out.id_hash);
            break;
        case ECON_CONTRACT_TAG_OBLIGATION: {
            dom_econ_contract_obligation obl;
            if (!parse_obligation(rec.payload, rec.len, obl, err)) {
                return false;
            }
            out.obligations.push_back(obl);
            break;
        }
        default:
            err = "contract_unknown_tag";
            return false;
        }
    }
    if (r.remaining() != 0u) {
        err = "contract_truncated";
        return false;
    }
    if (!has_id || !has_id_hash || out.obligations.empty()) {
        err = "contract_missing_field";
        return false;
    }
    if (!id_hash64(out.id, computed) || computed != out.id_hash) {
        err = "contract_id_hash_mismatch";
        return false;
    }
    return true;
}

static bool parse_instrument_record(const std::vector<unsigned char> &payload,
                                    dom_econ_instrument &out,
                                    std::string &err) {
    dom::core_tlv::TlvReader r(payload.empty() ? 0 : &payload[0], payload.size());
    dom::core_tlv::TlvRecord rec;
    bool has_id = false;
    bool has_id_hash = false;
    bool has_kind = false;
    bool has_contract = false;
    bool has_contract_hash = false;
    u64 computed = 0ull;

    out = dom_econ_instrument();

    while (r.next(rec)) {
        switch (rec.tag) {
        case ECON_INSTRUMENT_TAG_ID:
            out.id = read_string(rec);
            has_id = !out.id.empty();
            break;
        case ECON_INSTRUMENT_TAG_ID_HASH:
            has_id_hash = read_u64(rec, out.id_hash);
            break;
        case ECON_INSTRUMENT_TAG_KIND:
            has_kind = read_u32(rec, out.kind);
            break;
        case ECON_INSTRUMENT_TAG_CONTRACT_ID:
            out.contract_id = read_string(rec);
            has_contract = !out.contract_id.empty();
            break;
        case ECON_INSTRUMENT_TAG_CONTRACT_HASH:
            has_contract_hash = read_u64(rec, out.contract_id_hash);
            break;
        case ECON_INSTRUMENT_TAG_ASSET_ID:
            out.asset_ids.push_back(read_string(rec));
            break;
        case ECON_INSTRUMENT_TAG_ASSET_HASH: {
            u64 asset_hash = 0ull;
            if (!read_u64(rec, asset_hash)) {
                err = "instrument_asset_hash_invalid";
                return false;
            }
            out.asset_id_hashes.push_back(asset_hash);
            break;
        }
        default:
            err = "instrument_unknown_tag";
            return false;
        }
    }
    if (r.remaining() != 0u) {
        err = "instrument_truncated";
        return false;
    }
    if (!has_id || !has_id_hash || !has_kind || !has_contract || !has_contract_hash) {
        err = "instrument_missing_field";
        return false;
    }
    if (!id_hash64(out.id, computed) || computed != out.id_hash) {
        err = "instrument_id_hash_mismatch";
        return false;
    }
    if (!id_hash64(out.contract_id, computed) || computed != out.contract_id_hash) {
        err = "instrument_contract_hash_mismatch";
        return false;
    }
    if (!out.asset_id_hashes.empty() && out.asset_ids.size() != out.asset_id_hashes.size()) {
        err = "instrument_asset_count_mismatch";
        return false;
    }
    if (!out.asset_ids.empty()) {
        size_t i;
        out.asset_id_hashes.clear();
        out.asset_id_hashes.reserve(out.asset_ids.size());
        for (i = 0u; i < out.asset_ids.size(); ++i) {
            if (!id_hash64(out.asset_ids[i], computed)) {
                err = "instrument_asset_hash_failed";
                return false;
            }
            out.asset_id_hashes.push_back(computed);
        }
    }
    return true;
}

static bool obligation_less(const dom_econ_contract_obligation &a,
                            const dom_econ_contract_obligation &b) {
    if (a.offset_ticks != b.offset_ticks) {
        return a.offset_ticks < b.offset_ticks;
    }
    if (a.role_from_hash != b.role_from_hash) {
        return a.role_from_hash < b.role_from_hash;
    }
    if (a.role_to_hash != b.role_to_hash) {
        return a.role_to_hash < b.role_to_hash;
    }
    if (a.asset_id_hash != b.asset_id_hash) {
        return a.asset_id_hash < b.asset_id_hash;
    }
    return a.amount < b.amount;
}

static u64 hash_sim_asset(const dom_econ_asset &asset) {
    dom::core_tlv::TlvWriter w;
    w.add_u64(ECON_ASSET_TAG_ID_HASH, asset.id_hash);
    w.add_u32(ECON_ASSET_TAG_KIND, asset.kind);
    w.add_u32(ECON_ASSET_TAG_UNIT_SCALE, asset.unit_scale);
    w.add_u32(ECON_ASSET_TAG_DIVISIBILITY, asset.divisibility);
    w.add_u32(ECON_ASSET_TAG_PROVENANCE_REQ, asset.provenance_required);
    if (asset.issuer_id_hash != 0ull) {
        w.add_u64(ECON_ASSET_TAG_ISSUER_ID_HASH, asset.issuer_id_hash);
    }
    return hash_record(ECON_REC_ASSET, (u16)ECON_REC_VERSION_V1, w.bytes());
}

static u64 hash_sim_money(const dom_econ_money_standard &money) {
    dom::core_tlv::TlvWriter w;
    w.add_u64(ECON_MONEY_TAG_ID_HASH, money.id_hash);
    w.add_u64(ECON_MONEY_TAG_BASE_ASSET_HASH, money.base_asset_id_hash);
    w.add_u32(ECON_MONEY_TAG_DENOM_SCALE, money.denom_scale);
    w.add_u32(ECON_MONEY_TAG_ROUNDING_MODE, money.rounding_mode);
    if (money.convert_rule_id_hash != 0ull) {
        w.add_u64(ECON_MONEY_TAG_CONVERT_RULE_HASH, money.convert_rule_id_hash);
    }
    return hash_record(ECON_REC_MONEY_STANDARD, (u16)ECON_REC_VERSION_V1, w.bytes());
}

static u64 hash_sim_contract(const dom_econ_contract_template &contract) {
    dom::core_tlv::TlvWriter w;
    std::vector<dom_econ_contract_obligation> ordered = contract.obligations;
    size_t i;
    std::sort(ordered.begin(), ordered.end(), obligation_less);
    w.add_u64(ECON_CONTRACT_TAG_ID_HASH, contract.id_hash);
    for (i = 0u; i < ordered.size(); ++i) {
        const dom_econ_contract_obligation &obl = ordered[i];
        dom::core_tlv::TlvWriter ow;
        ow.add_u64(ECON_OBL_TAG_ROLE_FROM_HASH, obl.role_from_hash);
        ow.add_u64(ECON_OBL_TAG_ROLE_TO_HASH, obl.role_to_hash);
        ow.add_u64(ECON_OBL_TAG_ASSET_HASH, obl.asset_id_hash);
        ow.add_u64(ECON_OBL_TAG_AMOUNT_I64, (u64)obl.amount);
        ow.add_u64(ECON_OBL_TAG_OFFSET_TICKS, obl.offset_ticks);
        w.add_container(ECON_CONTRACT_TAG_OBLIGATION, ow.bytes());
    }
    return hash_record(ECON_REC_CONTRACT_TEMPLATE, (u16)ECON_REC_VERSION_V1, w.bytes());
}

static u64 hash_sim_instrument(const dom_econ_instrument &inst) {
    dom::core_tlv::TlvWriter w;
    std::vector<u64> assets = inst.asset_id_hashes;
    size_t i;
    std::sort(assets.begin(), assets.end());
    w.add_u64(ECON_INSTRUMENT_TAG_ID_HASH, inst.id_hash);
    w.add_u32(ECON_INSTRUMENT_TAG_KIND, inst.kind);
    w.add_u64(ECON_INSTRUMENT_TAG_CONTRACT_HASH, inst.contract_id_hash);
    for (i = 0u; i < assets.size(); ++i) {
        w.add_u64(ECON_INSTRUMENT_TAG_ASSET_HASH, assets[i]);
    }
    return hash_record(ECON_REC_INSTRUMENT, (u16)ECON_REC_VERSION_V1, w.bytes());
}

static u64 compute_sim_digest(const dom_econ_state &state) {
    std::vector<RecordView> sim_records;
    size_t i;
    sim_records.reserve(state.assets.size() +
                        state.money_standards.size() +
                        state.contracts.size() +
                        state.instruments.size());

    for (i = 0u; i < state.assets.size(); ++i) {
        RecordView view;
        view.type_id = ECON_REC_ASSET;
        view.id = state.assets[i].id;
        view.id_hash = state.assets[i].id_hash;
        view.record_hash = hash_sim_asset(state.assets[i]);
        sim_records.push_back(view);
    }
    for (i = 0u; i < state.money_standards.size(); ++i) {
        RecordView view;
        view.type_id = ECON_REC_MONEY_STANDARD;
        view.id = state.money_standards[i].id;
        view.id_hash = state.money_standards[i].id_hash;
        view.record_hash = hash_sim_money(state.money_standards[i]);
        sim_records.push_back(view);
    }
    for (i = 0u; i < state.contracts.size(); ++i) {
        RecordView view;
        view.type_id = ECON_REC_CONTRACT_TEMPLATE;
        view.id = state.contracts[i].id;
        view.id_hash = state.contracts[i].id_hash;
        view.record_hash = hash_sim_contract(state.contracts[i]);
        sim_records.push_back(view);
    }
    for (i = 0u; i < state.instruments.size(); ++i) {
        RecordView view;
        view.type_id = ECON_REC_INSTRUMENT;
        view.id = state.instruments[i].id;
        view.id_hash = state.instruments[i].id_hash;
        view.record_hash = hash_sim_instrument(state.instruments[i]);
        sim_records.push_back(view);
    }
    std::sort(sim_records.begin(), sim_records.end(), record_less);
    return hash_content(sim_records);
}

} // namespace

// -- public API ------------------------------------------------------------
dom_econ_asset::dom_econ_asset()
    : id(),
      id_hash(0ull),
      kind(0u),
      unit_scale(0u),
      divisibility(0u),
      provenance_required(0u),
      display_name(),
      issuer_id(),
      issuer_id_hash(0ull) {
}

dom_econ_money_standard::dom_econ_money_standard()
    : id(),
      id_hash(0ull),
      base_asset_id(),
      base_asset_id_hash(0ull),
      denom_scale(0u),
      rounding_mode(0u),
      display_name(),
      convert_rule_id(),
      convert_rule_id_hash(0ull) {
}

dom_econ_contract_obligation::dom_econ_contract_obligation()
    : role_from_id(),
      role_from_hash(0ull),
      role_to_id(),
      role_to_hash(0ull),
      asset_id(),
      asset_id_hash(0ull),
      amount(0),
      offset_ticks(0ull) {
}

dom_econ_contract_template::dom_econ_contract_template()
    : id(),
      id_hash(0ull),
      obligations() {
}

dom_econ_instrument::dom_econ_instrument()
    : id(),
      id_hash(0ull),
      kind(0u),
      contract_id(),
      contract_id_hash(0ull),
      asset_ids(),
      asset_id_hashes() {
}

dom_econ_state::dom_econ_state()
    : pack_schema_version(0u),
      pack_id(),
      pack_version_num(0u),
      pack_version_str(),
      content_hash(0ull),
      pack_hash(0ull),
      sim_digest(0ull),
      assets(),
      money_standards(),
      contracts(),
      instruments() {
}

int dom_econ_load_from_bytes(const unsigned char *data,
                             size_t size,
                             dom_econ_state *out_state,
                             std::string *out_error) {
    dom::core_tlv::TlvReader r(data, size);
    dom::core_tlv::TlvRecord rec;
    std::vector<RecordView> records;
    std::vector<RecordView> content_records;
    std::string err;
    bool have_meta = false;
    size_t i;

    if (!out_state || (!data && size != 0u)) {
        set_error(out_error, "invalid_argument");
        return DOM_ECON_INVALID_ARGUMENT;
    }

    *out_state = dom_econ_state();
    out_state->pack_hash = dom::core_tlv::tlv_fnv1a64(data ? data : 0, size);

    while (r.next(rec)) {
        RecordView view;
        view.type_id = rec.tag;
        view.id_hash = 0ull;
        if (rec.len > 0u && rec.payload) {
            view.payload.assign(rec.payload, rec.payload + rec.len);
        }
        view.record_hash = hash_record(view.type_id, (u16)ECON_REC_VERSION_V1, view.payload);

        if (view.type_id == ECON_REC_PACK_META) {
            if (have_meta) {
                set_error(out_error, "pack_meta_duplicate");
                return DOM_ECON_INVALID_FORMAT;
            }
            if (!parse_pack_meta(rec.payload, rec.len, *out_state, err)) {
                set_error(out_error, err.c_str());
                return DOM_ECON_INVALID_FORMAT;
            }
            have_meta = true;
        } else if (view.type_id == ECON_REC_ASSET) {
            dom_econ_asset asset;
            if (!parse_asset_record(view.payload, asset, err)) {
                set_error(out_error, err.c_str());
                return DOM_ECON_INVALID_FORMAT;
            }
            view.id = asset.id;
            view.id_hash = asset.id_hash;
            out_state->assets.push_back(asset);
        } else if (view.type_id == ECON_REC_MONEY_STANDARD) {
            dom_econ_money_standard money;
            if (!parse_money_record(view.payload, money, err)) {
                set_error(out_error, err.c_str());
                return DOM_ECON_INVALID_FORMAT;
            }
            view.id = money.id;
            view.id_hash = money.id_hash;
            out_state->money_standards.push_back(money);
        } else if (view.type_id == ECON_REC_CONTRACT_TEMPLATE) {
            dom_econ_contract_template contract;
            if (!parse_contract_record(view.payload, contract, err)) {
                set_error(out_error, err.c_str());
                return DOM_ECON_INVALID_FORMAT;
            }
            view.id = contract.id;
            view.id_hash = contract.id_hash;
            out_state->contracts.push_back(contract);
        } else if (view.type_id == ECON_REC_INSTRUMENT) {
            dom_econ_instrument inst;
            if (!parse_instrument_record(view.payload, inst, err)) {
                set_error(out_error, err.c_str());
                return DOM_ECON_INVALID_FORMAT;
            }
            view.id = inst.id;
            view.id_hash = inst.id_hash;
            out_state->instruments.push_back(inst);
        } else {
            set_error(out_error, "record_unknown_type");
            return DOM_ECON_INVALID_FORMAT;
        }

        records.push_back(view);
        if (view.type_id != ECON_REC_PACK_META) {
            content_records.push_back(view);
        }
    }

    if (r.remaining() != 0u) {
        set_error(out_error, "pack_truncated");
        return DOM_ECON_INVALID_FORMAT;
    }
    if (!have_meta) {
        set_error(out_error, "pack_meta_missing");
        return DOM_ECON_MISSING_REQUIRED;
    }
    if (out_state->assets.empty() || out_state->money_standards.empty() ||
        out_state->contracts.empty()) {
        set_error(out_error, "required_records_missing");
        return DOM_ECON_MISSING_REQUIRED;
    }
    if (!record_is_canonical(records)) {
        set_error(out_error, "record_order_invalid");
        return DOM_ECON_INVALID_FORMAT;
    }

    std::sort(content_records.begin(), content_records.end(), record_less);
    if (out_state->content_hash != hash_content(content_records)) {
        set_error(out_error, "content_hash_mismatch");
        return DOM_ECON_INVALID_FORMAT;
    }

    for (i = 0u; i < content_records.size(); ++i) {
        if (i > 0u && record_less(content_records[i], content_records[i - 1u])) {
            set_error(out_error, "content_record_order_invalid");
            return DOM_ECON_INVALID_FORMAT;
        }
        if (i > 0u &&
            content_records[i].type_id == content_records[i - 1u].type_id &&
            content_records[i].id_hash == content_records[i - 1u].id_hash &&
            content_records[i].id == content_records[i - 1u].id) {
            set_error(out_error, "duplicate_record_id");
            return DOM_ECON_DUPLICATE_ID;
        }
    }

    {
        std::vector<u64> asset_ids;
        asset_ids.reserve(out_state->assets.size());
        for (i = 0u; i < out_state->assets.size(); ++i) {
            asset_ids.push_back(out_state->assets[i].id_hash);
        }
        for (i = 0u; i < out_state->money_standards.size(); ++i) {
            bool found = false;
            size_t j;
            for (j = 0u; j < asset_ids.size(); ++j) {
                if (asset_ids[j] == out_state->money_standards[i].base_asset_id_hash) {
                    found = true;
                    break;
                }
            }
            if (!found) {
                set_error(out_error, "money_base_asset_missing");
                return DOM_ECON_MISSING_REFERENCE;
            }
        }
        for (i = 0u; i < out_state->contracts.size(); ++i) {
            size_t j;
            for (j = 0u; j < out_state->contracts[i].obligations.size(); ++j) {
                const dom_econ_contract_obligation &obl = out_state->contracts[i].obligations[j];
                bool found = false;
                size_t k;
                for (k = 0u; k < asset_ids.size(); ++k) {
                    if (asset_ids[k] == obl.asset_id_hash) {
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    set_error(out_error, "contract_asset_missing");
                    return DOM_ECON_MISSING_REFERENCE;
                }
            }
        }
        for (i = 0u; i < out_state->instruments.size(); ++i) {
            size_t j;
            for (j = 0u; j < out_state->instruments[i].asset_id_hashes.size(); ++j) {
                bool found = false;
                size_t k;
                for (k = 0u; k < asset_ids.size(); ++k) {
                    if (asset_ids[k] == out_state->instruments[i].asset_id_hashes[j]) {
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    set_error(out_error, "instrument_asset_missing");
                    return DOM_ECON_MISSING_REFERENCE;
                }
            }
        }
    }

    {
        std::vector<u64> contract_ids;
        contract_ids.reserve(out_state->contracts.size());
        for (i = 0u; i < out_state->contracts.size(); ++i) {
            contract_ids.push_back(out_state->contracts[i].id_hash);
        }
        for (i = 0u; i < out_state->instruments.size(); ++i) {
            bool found = false;
            size_t j;
            for (j = 0u; j < contract_ids.size(); ++j) {
                if (contract_ids[j] == out_state->instruments[i].contract_id_hash) {
                    found = true;
                    break;
                }
            }
            if (!found) {
                set_error(out_error, "instrument_contract_missing");
                return DOM_ECON_MISSING_REFERENCE;
            }
        }
    }

    out_state->sim_digest = compute_sim_digest(*out_state);
    return DOM_ECON_OK;
}

int dom_econ_load_from_file(const char *path,
                            dom_econ_state *out_state,
                            std::string *out_error) {
    std::vector<unsigned char> bytes;
    std::string err;
    if (!out_state) {
        set_error(out_error, "invalid_argument");
        return DOM_ECON_INVALID_ARGUMENT;
    }
    if (!read_file_bytes(path, bytes, err)) {
        set_error(out_error, err.c_str());
        return DOM_ECON_IO_ERROR;
    }
    return dom_econ_load_from_bytes(bytes.empty() ? 0 : &bytes[0],
                                    bytes.size(),
                                    out_state,
                                    out_error);
}

u64 dom_econ_compute_sim_digest(const dom_econ_state *state) {
    if (!state) {
        return 0ull;
    }
    return compute_sim_digest(*state);
}

int dom_econ_apply_to_registries(const dom_econ_state *state,
                                 dom_asset_registry *assets,
                                 dom_money_standard_registry *money,
                                 dom_contract_template_registry *contracts,
                                 dom_instrument_registry *instruments,
                                 std::string *out_error) {
    size_t i;
    if (!state || !assets || !money || !contracts || !instruments) {
        set_error(out_error, "invalid_argument");
        return DOM_ECON_INVALID_ARGUMENT;
    }

    for (i = 0u; i < state->assets.size(); ++i) {
        const dom_econ_asset &asset = state->assets[i];
        dom_asset_desc desc;
        desc.id = asset.id.c_str();
        desc.id_len = (u32)asset.id.size();
        desc.id_hash = asset.id_hash;
        desc.kind = asset.kind;
        desc.unit_scale = asset.unit_scale;
        desc.divisibility = asset.divisibility;
        desc.provenance_required = asset.provenance_required;
        desc.display_name = asset.display_name.empty() ? 0 : asset.display_name.c_str();
        desc.display_name_len = (u32)asset.display_name.size();
        desc.issuer_id = asset.issuer_id.empty() ? 0 : asset.issuer_id.c_str();
        desc.issuer_id_len = (u32)asset.issuer_id.size();
        desc.issuer_id_hash = asset.issuer_id_hash;
        if (dom_asset_registry_register(assets, &desc) != DOM_ASSET_OK) {
            set_error(out_error, "asset_register_failed");
            return DOM_ECON_ERR;
        }
    }

    for (i = 0u; i < state->money_standards.size(); ++i) {
        const dom_econ_money_standard &ms = state->money_standards[i];
        dom_money_standard_desc desc;
        desc.id = ms.id.c_str();
        desc.id_len = (u32)ms.id.size();
        desc.id_hash = ms.id_hash;
        desc.base_asset_id = ms.base_asset_id.c_str();
        desc.base_asset_id_len = (u32)ms.base_asset_id.size();
        desc.base_asset_id_hash = ms.base_asset_id_hash;
        desc.denom_scale = ms.denom_scale;
        desc.rounding_mode = ms.rounding_mode;
        desc.display_name = ms.display_name.empty() ? 0 : ms.display_name.c_str();
        desc.display_name_len = (u32)ms.display_name.size();
        desc.convert_rule_id = ms.convert_rule_id.empty() ? 0 : ms.convert_rule_id.c_str();
        desc.convert_rule_id_len = (u32)ms.convert_rule_id.size();
        desc.convert_rule_id_hash = ms.convert_rule_id_hash;
        if (dom_money_standard_registry_register(money, &desc) != DOM_MONEY_OK) {
            set_error(out_error, "money_register_failed");
            return DOM_ECON_ERR;
        }
    }

    for (i = 0u; i < state->contracts.size(); ++i) {
        const dom_econ_contract_template &ct = state->contracts[i];
        std::vector<dom_econ_contract_obligation> ordered = ct.obligations;
        std::vector<dom_contract_obligation_desc> obligations;
        dom_contract_template_desc desc;
        size_t j;

        std::sort(ordered.begin(), ordered.end(), obligation_less);
        obligations.resize(ordered.size());
        for (j = 0u; j < ordered.size(); ++j) {
            dom_contract_obligation_desc &od = obligations[j];
            const dom_econ_contract_obligation &obl = ordered[j];
            od.role_from_id = obl.role_from_id.c_str();
            od.role_from_id_len = (u32)obl.role_from_id.size();
            od.role_from_hash = obl.role_from_hash;
            od.role_to_id = obl.role_to_id.c_str();
            od.role_to_id_len = (u32)obl.role_to_id.size();
            od.role_to_hash = obl.role_to_hash;
            od.asset_id = obl.asset_id.c_str();
            od.asset_id_len = (u32)obl.asset_id.size();
            od.asset_id_hash = obl.asset_id_hash;
            od.amount = obl.amount;
            od.offset_ticks = obl.offset_ticks;
        }

        desc.id = ct.id.c_str();
        desc.id_len = (u32)ct.id.size();
        desc.id_hash = ct.id_hash;
        desc.obligations = obligations.empty() ? 0 : &obligations[0];
        desc.obligation_count = (u32)obligations.size();
        if (dom_contract_template_registry_register(contracts, &desc) != DOM_CONTRACT_TEMPLATE_OK) {
            set_error(out_error, "contract_register_failed");
            return DOM_ECON_ERR;
        }
    }

    for (i = 0u; i < state->instruments.size(); ++i) {
        const dom_econ_instrument &inst = state->instruments[i];
        std::vector<u64> assets_sorted = inst.asset_id_hashes;
        dom_instrument_desc desc;
        std::sort(assets_sorted.begin(), assets_sorted.end());
        desc.id = inst.id.c_str();
        desc.id_len = (u32)inst.id.size();
        desc.id_hash = inst.id_hash;
        desc.kind = inst.kind;
        desc.contract_id = inst.contract_id.c_str();
        desc.contract_id_len = (u32)inst.contract_id.size();
        desc.contract_id_hash = inst.contract_id_hash;
        desc.asset_ids = assets_sorted.empty() ? 0 : &assets_sorted[0];
        desc.asset_id_count = (u32)assets_sorted.size();
        if (dom_instrument_registry_register(instruments, &desc) != DOM_INSTRUMENT_OK) {
            set_error(out_error, "instrument_register_failed");
            return DOM_ECON_ERR;
        }
    }

    return DOM_ECON_OK;
}
