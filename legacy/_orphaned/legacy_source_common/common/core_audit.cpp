#include "dominium/core_audit.h"

namespace dom {
namespace core_audit {

void append_err_details(core_tlv::TlvWriter &writer,
                        u32 entry_tag,
                        const err_t &err,
                        const ErrDetailTags &tags) {
    err_t sorted = err;
    u32 i;
    if (entry_tag == 0u || sorted.detail_count == 0u) {
        return;
    }
    err_sort_details_by_key(&sorted);
    for (i = 0u; i < sorted.detail_count; ++i) {
        const err_detail &detail = sorted.details[i];
        core_tlv::TlvWriter entry;
        entry.add_u32(tags.tag_key, detail.key_id);
        entry.add_u32(tags.tag_type, detail.type);
        if (detail.type == (u32)ERR_DETAIL_TYPE_U32 ||
            detail.type == (u32)ERR_DETAIL_TYPE_MSG_ID) {
            entry.add_u32(tags.tag_value_u32, detail.v.u32_value);
        } else {
            entry.add_u64(tags.tag_value_u64, detail.v.u64_value);
        }
        writer.add_container(entry_tag, entry.bytes());
    }
}

bool parse_err_detail_entry(const unsigned char *payload,
                            size_t len,
                            err_t &err,
                            const ErrDetailTags &tags) {
    core_tlv::TlvReader reader(payload, len);
    core_tlv::TlvRecord rec;
    u32 key_id = 0u;
    u32 type = 0u;
    u32 value_u32 = 0u;
    u64 value_u64 = 0ull;
    while (reader.next(rec)) {
        if (rec.tag == tags.tag_key) {
            (void)core_tlv::tlv_read_u32_le(rec.payload, rec.len, key_id);
        } else if (rec.tag == tags.tag_type) {
            (void)core_tlv::tlv_read_u32_le(rec.payload, rec.len, type);
        } else if (rec.tag == tags.tag_value_u32) {
            (void)core_tlv::tlv_read_u32_le(rec.payload, rec.len, value_u32);
        } else if (rec.tag == tags.tag_value_u64) {
            (void)core_tlv::tlv_read_u64_le(rec.payload, rec.len, value_u64);
        } else {
            /* skip unknown */
        }
    }
    if (key_id == 0u || type == 0u) {
        return false;
    }
    if (type == (u32)ERR_DETAIL_TYPE_U32 ||
        type == (u32)ERR_DETAIL_TYPE_MSG_ID) {
        return err_add_detail_u32(&err, key_id, value_u32) != 0;
    }
    return err_add_detail_u64(&err, key_id, value_u64) != 0;
}

u32 err_subcode(const err_t &err) {
    u32 i;
    for (i = 0u; i < err.detail_count; ++i) {
        const err_detail &detail = err.details[i];
        if (detail.key_id == (u32)ERR_DETAIL_KEY_SUBCODE &&
            detail.type == (u32)ERR_DETAIL_TYPE_U32) {
            return detail.v.u32_value;
        }
    }
    return 0u;
}

} /* namespace core_audit */
} /* namespace dom */
