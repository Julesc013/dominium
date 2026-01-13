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
    DSK_AUDIT_EVENT_PLAN_RESOLVE_OK = 8,
    DSK_AUDIT_EVENT_PLAN_RESOLVE_FAIL = 9,
    DSK_AUDIT_EVENT_PLAN_BUILD_OK = 10,
    DSK_AUDIT_EVENT_PLAN_BUILD_FAIL = 11,
    DSK_AUDIT_EVENT_WRITE_STATE_OK = 12,
    DSK_AUDIT_EVENT_WRITE_STATE_FAIL = 13,
    DSK_AUDIT_EVENT_END = 14,
    DSK_AUDIT_EVENT_APPLY_BEGIN = 15,
    DSK_AUDIT_EVENT_STAGE_OK = 16,
    DSK_AUDIT_EVENT_STAGE_FAIL = 17,
    DSK_AUDIT_EVENT_VERIFY_OK = 18,
    DSK_AUDIT_EVENT_VERIFY_FAIL = 19,
    DSK_AUDIT_EVENT_COMMIT_OK = 20,
    DSK_AUDIT_EVENT_COMMIT_FAIL = 21,
    DSK_AUDIT_EVENT_REGISTER_OK = 22,
    DSK_AUDIT_EVENT_REGISTER_FAIL = 23,
    DSK_AUDIT_EVENT_WRITE_AUDIT_OK = 24,
    DSK_AUDIT_EVENT_WRITE_AUDIT_FAIL = 25,
    DSK_AUDIT_EVENT_ROLLBACK_BEGIN = 26,
    DSK_AUDIT_EVENT_ROLLBACK_STEP_OK = 27,
    DSK_AUDIT_EVENT_ROLLBACK_STEP_FAIL = 28,
    DSK_AUDIT_EVENT_ROLLBACK_END = 29,
    DSK_AUDIT_EVENT_RESUME_BEGIN = 30,
    DSK_AUDIT_EVENT_RESUME_END = 31,
    DSK_AUDIT_EVENT_IMPORT_BEGIN = 32,
    DSK_AUDIT_EVENT_IMPORT_PARSE_OK = 33,
    DSK_AUDIT_EVENT_IMPORT_PARSE_FAIL = 34,
    DSK_AUDIT_EVENT_IMPORT_WRITE_STATE_OK = 35,
    DSK_AUDIT_EVENT_IMPORT_WRITE_STATE_FAIL = 36,
    DSK_AUDIT_EVENT_IMPORT_END = 37,
    DSK_AUDIT_EVENT_SPLAT_DEPRECATED = 38,
    DSK_AUDIT_EVENT_PARSE_STATE_OK = 39,
    DSK_AUDIT_EVENT_PARSE_STATE_FAIL = 40
};

struct dsk_audit_event_t {
    dsk_u16 event_id;
    dsk_error_t error;
};

struct dsk_audit_job_t {
    dsk_u32 job_id;
    dsk_u16 job_kind;
    dsk_u16 job_status;
};

struct dsk_audit_selection_candidate_t {
    std::string id;
    dsk_u64 caps_digest64;
};

struct dsk_audit_selection_t {
    std::vector<dsk_audit_selection_candidate_t> candidates;
    std::vector<dsk_splat_rejection_t> rejections;
    std::string selected_id;
    dsk_u16 selected_reason;
};

struct dsk_audit_refusal_t {
    dsk_u16 code;
    std::string detail;
};

struct dsk_audit_t {
    dsk_u64 run_id;
    dsk_u64 manifest_digest64;
    dsk_u64 request_digest64;
    dsk_u64 splat_caps_digest64;
    dsk_u64 resolved_set_digest64;
    dsk_u64 plan_digest64;
    std::string selected_splat;
    std::string frontend_id;
    std::string platform_triple;
    std::string import_source;
    std::vector<std::string> import_details;
    dsk_u16 operation;
    dsk_error_t result;
    dsk_audit_selection_t selection;
    std::vector<dsk_audit_refusal_t> refusals;
    std::vector<dsk_audit_job_t> jobs;
    std::vector<dsk_audit_event_t> events;
};

DSK_API void dsk_audit_clear(dsk_audit_t *audit);
DSK_API dsk_status_t dsk_audit_write(const dsk_audit_t *audit, dsk_tlv_buffer_t *out_buf);
DSK_API dsk_status_t dsk_audit_parse(const dsk_u8 *data, dsk_u32 size, dsk_audit_t *out_audit);
#endif

#endif /* DSK_AUDIT_H */
