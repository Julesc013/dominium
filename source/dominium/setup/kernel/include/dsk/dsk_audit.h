#ifndef DSK_AUDIT_H
#define DSK_AUDIT_H

#include "dsk_error.h"
#include "dsk_splat.h"
#include "dsk_tlv.h"
#include "dsk_types.h"

#ifdef __cplusplus
#include <string>
#include <vector>

enum dsk_audit_event_id_t {
    DSK_AUDIT_EVENT_BEGIN = 1,
    DSK_AUDIT_EVENT_PARSE_MANIFEST_OK = 2,
    DSK_AUDIT_EVENT_PARSE_MANIFEST_FAIL = 3,
    DSK_AUDIT_EVENT_PARSE_REQUEST_OK = 4,
    DSK_AUDIT_EVENT_PARSE_REQUEST_FAIL = 5,
    DSK_AUDIT_EVENT_SPLAT_SELECT_OK = 6,
    DSK_AUDIT_EVENT_SPLAT_SELECT_FAIL = 7,
    DSK_AUDIT_EVENT_WRITE_STATE_OK = 8,
    DSK_AUDIT_EVENT_WRITE_STATE_FAIL = 9,
    DSK_AUDIT_EVENT_END = 10
};

struct dsk_audit_event_t {
    dsk_u16 event_id;
    dsk_error_t error;
};

struct dsk_audit_selection_reason_t {
    std::vector<std::string> candidates;
    std::vector<dsk_splat_rejection_t> rejections;
    std::string chosen;
};

struct dsk_audit_t {
    dsk_u64 run_id;
    dsk_u64 manifest_digest64;
    dsk_u64 request_digest64;
    std::string selected_splat;
    dsk_u16 operation;
    dsk_error_t result;
    dsk_audit_selection_reason_t selection_reason;
    std::vector<dsk_audit_event_t> events;
};

DSK_API void dsk_audit_clear(dsk_audit_t *audit);
DSK_API dsk_status_t dsk_audit_write(const dsk_audit_t *audit, dsk_tlv_buffer_t *out_buf);
DSK_API dsk_status_t dsk_audit_parse(const dsk_u8 *data, dsk_u32 size, dsk_audit_t *out_audit);
#endif

#endif /* DSK_AUDIT_H */
