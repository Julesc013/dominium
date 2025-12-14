#ifndef DOM_TOOL_TLV_H
#define DOM_TOOL_TLV_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/d_tlv.h"
}

namespace dom {
namespace tools {

/* TLV parser: tag (u32) + len (u32) + payload bytes. */
int tlv_next(const d_tlv_blob *blob,
             u32 *offset,
             u32 *tag,
             d_tlv_blob *payload);

/* Deterministic key/value TLV builder (schema payloads). */
class DomTlvKVBuilder {
public:
    struct Field {
        u32 tag;
        std::vector<unsigned char> payload;
    };

    DomTlvKVBuilder();

    void clear();
    void field_u32(u32 tag, u32 v);
    void field_u16(u32 tag, u16 v);
    void field_q16_16(u32 tag, q16_16 v);
    void field_q32_32(u32 tag, q32_32 v);
    void field_blob(u32 tag, const unsigned char *data, u32 len);
    void field_blob(u32 tag, const d_tlv_blob &blob);
    void field_string(u32 tag, const std::string &utf8);

    std::vector<unsigned char> finalize() const;

private:
    std::vector<Field> m_fields;
};

/* Deterministic TLV stream builder (record streams), e.g. content blobs. */
class DomTlvStreamBuilder {
public:
    struct Record {
        u32 tag;
        u32 sort_id;
        std::vector<unsigned char> payload;
    };

    DomTlvStreamBuilder();

    void clear();
    void add_record(u32 tag, const std::vector<unsigned char> &payload);
    void add_record(u32 tag, const DomTlvKVBuilder &kv_payload);

    std::vector<unsigned char> finalize() const;

private:
    std::vector<Record> m_records;
};

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_TLV_H */
