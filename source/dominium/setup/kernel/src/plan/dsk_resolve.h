#ifndef DSK_RESOLVE_H
#define DSK_RESOLVE_H

#include "dsk/dsk_plan.h"

#ifdef __cplusplus
#include <string>
#include <vector>

enum dsk_plan_refusal_code_t {
    DSK_PLAN_REFUSAL_NONE = 0,
    DSK_PLAN_REFUSAL_COMPONENT_NOT_FOUND = 1,
    DSK_PLAN_REFUSAL_UNSATISFIED_DEPENDENCY = 2,
    DSK_PLAN_REFUSAL_EXPLICIT_CONFLICT = 3,
    DSK_PLAN_REFUSAL_PLATFORM_INCOMPATIBLE = 4,
    DSK_PLAN_REFUSAL_INVALID_REQUEST = 5,
    DSK_PLAN_REFUSAL_ARTIFACT_MISSING_DIGEST = 6
};

struct dsk_plan_refusal_t {
    dsk_u16 code;
    std::string detail;
};

DSK_API dsk_status_t dsk_resolve_components(const dsk_manifest_t &manifest,
                                            const dsk_request_t &request,
                                            const std::string &platform_triple,
                                            dsk_resolved_set_t *out_set,
                                            std::vector<dsk_plan_refusal_t> *out_refusals);
#endif /* __cplusplus */

#endif /* DSK_RESOLVE_H */
