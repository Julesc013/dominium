#include "dsk/dsk_audit.h"

void dsk_audit_clear(dsk_audit_t *audit) {
    if (!audit) {
        return;
    }
    audit->run_id = 0u;
    audit->manifest_digest64 = 0u;
    audit->request_digest64 = 0u;
    audit->splat_caps_digest64 = 0u;
    audit->resolved_set_digest64 = 0u;
    audit->plan_digest64 = 0u;
    audit->selected_splat.clear();
    audit->frontend_id.clear();
    audit->platform_triple.clear();
    audit->operation = 0u;
    audit->result = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    audit->selection.candidates.clear();
    audit->selection.rejections.clear();
    audit->selection.selected_id.clear();
    audit->selection.selected_reason = 0u;
    audit->refusals.clear();
    audit->jobs.clear();
    audit->events.clear();
}
