#include "dsk/dsk_audit.h"

void dsk_audit_clear(dsk_audit_t *audit) {
    if (!audit) {
        return;
    }
    audit->run_id = 0u;
    audit->manifest_digest64 = 0u;
    audit->request_digest64 = 0u;
    audit->selected_splat.clear();
    audit->operation = 0u;
    audit->result = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    audit->selection_reason.candidates.clear();
    audit->selection_reason.rejections.clear();
    audit->selection_reason.chosen.clear();
    audit->events.clear();
}
