#include "core_internal.h"

uint32_t dom_ui_list_views(dom_core* core, dom_view_desc* out, uint32_t max_out)
{
    uint32_t i;
    uint32_t count;

    if (!core) {
        return 0;
    }

    count = core->view_count;
    if (!out || max_out == 0u) {
        return count;
    }
    if (count > max_out) {
        count = max_out;
    }

    for (i = 0; i < count; ++i) {
        out[i] = core->views[i];
    }

    return count;
}
