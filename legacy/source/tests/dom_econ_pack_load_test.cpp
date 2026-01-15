/*
TEST: dom_econ_pack_load_test
PURPOSE: TLV econ pack load + sim digest stability across display-only changes.
*/
#include "runtime/dom_econ_pack_load.h"

#include <string>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
}

#include "dominium/core_tlv.h"
#include "dominium/econ_schema.h"

static u64 hash_record(u32 type_id, const std::vector<unsigned char> &payload) {
    unsigned char header[8];
    dom::core_tlv::tlv_write_u32_le(header, type_id);
    dom::core_tlv::tlv_write_u32_le(header + 4u, ECON_REC_VERSION_V1);
    std::vector<unsigned char> tmp;
    tmp.reserve(sizeof(header) + payload.size());
    tmp.insert(tmp.end(), header, header + sizeof(header));
    if (!payload.empty()) {
        tmp.insert(tmp.end(), payload.begin(), payload.end());
    }
    return dom::core_tlv::tlv_fnv1a64(tmp.empty() ? 0 : &tmp[0], tmp.size());
}

static void append_record(std::vector<unsigned char> &out,
                          u32 type_id,
                          const std::vector<unsigned char> &payload) {
    unsigned char header[8];
    dom::core_tlv::tlv_write_u32_le(header, type_id);
    dom::core_tlv::tlv_write_u32_le(header + 4u, (u32)payload.size());
    out.insert(out.end(), header, header + sizeof(header));
    if (!payload.empty()) {
        out.insert(out.end(), payload.begin(), payload.end());
    }
}

static bool build_pack(std::vector<unsigned char> &out_bytes,
                       const std::string &asset_display,
                       u64 &out_sim_digest) {
    dom::core_tlv::TlvWriter asset_w;
    dom::core_tlv::TlvWriter money_w;
    dom::core_tlv::TlvWriter contract_w;
    dom::core_tlv::TlvWriter obligation_w;
    dom::core_tlv::TlvWriter instrument_w;
    dom::core_tlv::TlvWriter meta_w;
    std::vector<unsigned char> payloads[4];
    u64 record_hashes[4];
    u64 content_hash = 0ull;
    std::vector<unsigned char> pack;
    std::vector<unsigned char> content_hash_buf;
    u64 asset_hash = 0ull;
    u64 money_hash = 0ull;
    u64 contract_hash = 0ull;
    u64 instrument_hash = 0ull;
    u64 role_from_hash = 0ull;
    u64 role_to_hash = 0ull;

    if (dom_id_hash64("asset_credit", 12u, &asset_hash) != DOM_SPACETIME_OK) {
        return false;
    }
    if (dom_id_hash64("money_credit", 12u, &money_hash) != DOM_SPACETIME_OK) {
        return false;
    }
    if (dom_id_hash64("contract_rent", 13u, &contract_hash) != DOM_SPACETIME_OK) {
        return false;
    }
    if (dom_id_hash64("instrument_lease", 16u, &instrument_hash) != DOM_SPACETIME_OK) {
        return false;
    }
    if (dom_id_hash64("payer", 5u, &role_from_hash) != DOM_SPACETIME_OK) {
        return false;
    }
    if (dom_id_hash64("payee", 5u, &role_to_hash) != DOM_SPACETIME_OK) {
        return false;
    }

    asset_w.add_string(ECON_ASSET_TAG_ID, "asset_credit");
    asset_w.add_u64(ECON_ASSET_TAG_ID_HASH, asset_hash);
    asset_w.add_u32(ECON_ASSET_TAG_KIND, ECON_ASSET_KIND_FUNGIBLE);
    asset_w.add_u32(ECON_ASSET_TAG_UNIT_SCALE, 1u);
    asset_w.add_u32(ECON_ASSET_TAG_DIVISIBILITY, 1u);
    asset_w.add_u32(ECON_ASSET_TAG_PROVENANCE_REQ, 0u);
    asset_w.add_string(ECON_ASSET_TAG_DISPLAY_NAME, asset_display);
    payloads[0] = asset_w.bytes();

    money_w.add_string(ECON_MONEY_TAG_ID, "money_credit");
    money_w.add_u64(ECON_MONEY_TAG_ID_HASH, money_hash);
    money_w.add_string(ECON_MONEY_TAG_BASE_ASSET_ID, "asset_credit");
    money_w.add_u64(ECON_MONEY_TAG_BASE_ASSET_HASH, asset_hash);
    money_w.add_u32(ECON_MONEY_TAG_DENOM_SCALE, 100u);
    money_w.add_u32(ECON_MONEY_TAG_ROUNDING_MODE, ECON_MONEY_ROUND_TRUNCATE);
    money_w.add_string(ECON_MONEY_TAG_DISPLAY_NAME, "Credit");
    payloads[1] = money_w.bytes();

    obligation_w.add_string(ECON_OBL_TAG_ROLE_FROM_ID, "payer");
    obligation_w.add_u64(ECON_OBL_TAG_ROLE_FROM_HASH, role_from_hash);
    obligation_w.add_string(ECON_OBL_TAG_ROLE_TO_ID, "payee");
    obligation_w.add_u64(ECON_OBL_TAG_ROLE_TO_HASH, role_to_hash);
    obligation_w.add_string(ECON_OBL_TAG_ASSET_ID, "asset_credit");
    obligation_w.add_u64(ECON_OBL_TAG_ASSET_HASH, asset_hash);
    obligation_w.add_u64(ECON_OBL_TAG_AMOUNT_I64, (u64)100);
    obligation_w.add_u64(ECON_OBL_TAG_OFFSET_TICKS, 10ull);

    contract_w.add_string(ECON_CONTRACT_TAG_ID, "contract_rent");
    contract_w.add_u64(ECON_CONTRACT_TAG_ID_HASH, contract_hash);
    contract_w.add_container(ECON_CONTRACT_TAG_OBLIGATION, obligation_w.bytes());
    payloads[2] = contract_w.bytes();

    instrument_w.add_string(ECON_INSTRUMENT_TAG_ID, "instrument_lease");
    instrument_w.add_u64(ECON_INSTRUMENT_TAG_ID_HASH, instrument_hash);
    instrument_w.add_u32(ECON_INSTRUMENT_TAG_KIND, ECON_INSTRUMENT_LEASE);
    instrument_w.add_string(ECON_INSTRUMENT_TAG_CONTRACT_ID, "contract_rent");
    instrument_w.add_u64(ECON_INSTRUMENT_TAG_CONTRACT_HASH, contract_hash);
    instrument_w.add_string(ECON_INSTRUMENT_TAG_ASSET_ID, "asset_credit");
    payloads[3] = instrument_w.bytes();

    record_hashes[0] = hash_record(ECON_REC_ASSET, payloads[0]);
    record_hashes[1] = hash_record(ECON_REC_MONEY_STANDARD, payloads[1]);
    record_hashes[2] = hash_record(ECON_REC_CONTRACT_TEMPLATE, payloads[2]);
    record_hashes[3] = hash_record(ECON_REC_INSTRUMENT, payloads[3]);

    {
        unsigned char buf[8];
        size_t i;
        for (i = 0u; i < 4u; ++i) {
            dom::core_tlv::tlv_write_u64_le(buf, record_hashes[i]);
            content_hash_buf.insert(content_hash_buf.end(), buf, buf + 8u);
        }
        content_hash = dom::core_tlv::tlv_fnv1a64(content_hash_buf.empty() ? 0 : &content_hash_buf[0],
                                                  content_hash_buf.size());
    }

    meta_w.add_u32(ECON_META_TAG_PACK_SCHEMA_VERSION, 1u);
    meta_w.add_string(ECON_META_TAG_PACK_ID, "test_pack");
    meta_w.add_u32(ECON_META_TAG_PACK_VERSION_NUM, 1u);
    meta_w.add_string(ECON_META_TAG_PACK_VERSION_STR, "1.0");
    meta_w.add_u64(ECON_META_TAG_CONTENT_HASH, content_hash);

    append_record(pack, ECON_REC_PACK_META, meta_w.bytes());
    append_record(pack, ECON_REC_ASSET, payloads[0]);
    append_record(pack, ECON_REC_MONEY_STANDARD, payloads[1]);
    append_record(pack, ECON_REC_CONTRACT_TEMPLATE, payloads[2]);
    append_record(pack, ECON_REC_INSTRUMENT, payloads[3]);

    out_bytes.swap(pack);
    {
        dom_econ_state state;
        std::string err;
        if (dom_econ_load_from_bytes(out_bytes.empty() ? 0 : &out_bytes[0],
                                     out_bytes.size(),
                                     &state,
                                     &err) != DOM_ECON_OK) {
            return false;
        }
        out_sim_digest = state.sim_digest;
    }
    return true;
}

int main(void) {
    std::vector<unsigned char> pack_a;
    std::vector<unsigned char> pack_b;
    u64 digest_a = 0ull;
    u64 digest_b = 0ull;

    if (!build_pack(pack_a, "Credit Asset", digest_a)) {
        return 1;
    }
    if (!build_pack(pack_b, "Credit Asset Renamed", digest_b)) {
        return 2;
    }
    if (digest_a == 0ull || digest_b == 0ull) {
        return 3;
    }
    if (digest_a != digest_b) {
        return 4;
    }
    return 0;
}
