/*
FILE: include/dominium/core_audit.h
MODULE: Dominium
PURPOSE: Shared audit helpers (err_t detail encoding/decoding; deterministic TLV layout).
*/
#ifndef DOMINIUM_CORE_AUDIT_H
#define DOMINIUM_CORE_AUDIT_H

extern "C" {
#include "domino/core/types.h"
}

#include "dominium/core_err.h"
#include "dominium/core_tlv.h"

typedef struct dom_core_audit_sink {
    const char *path;
} dom_core_audit_sink;

#ifdef __cplusplus
namespace dom {
namespace core_audit {

struct ErrDetailTags {
    u32 tag_key;
    u32 tag_type;
    u32 tag_value_u32;
    u32 tag_value_u64;
};

void append_err_details(core_tlv::TlvWriter &writer,
                        u32 entry_tag,
                        const err_t &err,
                        const ErrDetailTags &tags);

bool parse_err_detail_entry(const unsigned char *payload,
                            size_t len,
                            err_t &err,
                            const ErrDetailTags &tags);

u32 err_subcode(const err_t &err);

} /* namespace core_audit */
} /* namespace dom */
#endif

#endif /* DOMINIUM_CORE_AUDIT_H */
