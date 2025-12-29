#ifndef DSK_SPLAT_H
#define DSK_SPLAT_H

#include "dsk_error.h"

#ifdef __cplusplus
#include <string>
#include <vector>

struct dsk_manifest_t;
struct dsk_request_t;

enum dsk_splat_reject_code_t {
    DSK_SPLAT_REJECT_NONE = 0,
    DSK_SPLAT_REJECT_NOT_REQUESTED = 1,
    DSK_SPLAT_REJECT_PLATFORM_MISMATCH = 2,
    DSK_SPLAT_REJECT_MANIFEST_MISMATCH = 3,
    DSK_SPLAT_REJECT_NOT_FOUND = 4
};

struct dsk_splat_info_t {
    std::string id;
};

struct dsk_splat_rejection_t {
    std::string id;
    dsk_u16 code;
};

struct dsk_splat_selection_t {
    std::string chosen;
    std::vector<std::string> candidates;
    std::vector<dsk_splat_rejection_t> rejections;
};

DSK_API void dsk_splat_registry_list(std::vector<dsk_splat_info_t> &out);
DSK_API int dsk_splat_registry_contains(const std::string &id);
DSK_API dsk_status_t dsk_splat_select(const dsk_manifest_t &manifest,
                                      const dsk_request_t &request,
                                      dsk_splat_selection_t *out_selection);
#endif

#endif /* DSK_SPLAT_H */
