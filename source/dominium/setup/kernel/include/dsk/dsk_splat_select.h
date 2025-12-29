#ifndef DSK_SPLAT_SELECT_H
#define DSK_SPLAT_SELECT_H

#include "dsk_error.h"
#include "dsk_splat_caps.h"

#ifdef __cplusplus
#include <string>
#include <vector>

struct dsk_manifest_t;
struct dsk_request_t;

enum dsk_splat_reject_code_t {
    DSK_SPLAT_REJECT_NONE = 0,
    DSK_SPLAT_REJECT_REQUESTED_ID_MISMATCH = 1,
    DSK_SPLAT_REJECT_PLATFORM_UNSUPPORTED = 2,
    DSK_SPLAT_REJECT_SCOPE_UNSUPPORTED = 3,
    DSK_SPLAT_REJECT_UI_MODE_UNSUPPORTED = 4,
    DSK_SPLAT_REJECT_OWNERSHIP_INCOMPATIBLE = 5,
    DSK_SPLAT_REJECT_MANIFEST_ALLOWLIST = 6,
    DSK_SPLAT_REJECT_REQUIRED_CAPS_MISSING = 7,
    DSK_SPLAT_REJECT_PROHIBITED_CAPS_PRESENT = 8,
    DSK_SPLAT_REJECT_MANIFEST_TARGET_MISMATCH = 9
};

enum dsk_splat_selected_reason_t {
    DSK_SPLAT_SELECTED_NONE = 0,
    DSK_SPLAT_SELECTED_REQUESTED = 1,
    DSK_SPLAT_SELECTED_FIRST_COMPATIBLE = 2
};

struct dsk_splat_candidate_t {
    std::string id;
    dsk_splat_caps_t caps;
    dsk_u64 caps_digest64;
};

struct dsk_splat_rejection_t {
    std::string id;
    dsk_u16 code;
    std::string detail;
};

struct dsk_splat_selection_t {
    std::vector<dsk_splat_candidate_t> candidates;
    std::vector<dsk_splat_rejection_t> rejections;
    std::string selected_id;
    dsk_u16 selected_reason;
};

DSK_API dsk_status_t dsk_splat_select(const dsk_manifest_t &manifest,
                                      const dsk_request_t &request,
                                      dsk_splat_selection_t *out_selection);
#endif /* __cplusplus */

#endif /* DSK_SPLAT_SELECT_H */
