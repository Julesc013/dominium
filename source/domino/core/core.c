#include "domino/core.h"

#include <stdlib.h>
#include <string.h>

struct dom_core {
    dom_core_desc desc;
};

dom_status dom_core_create(const dom_core_desc* desc, dom_core** out_core)
{
    dom_core* core;
    dom_core_desc local_desc;

    if (!out_core) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    *out_core = NULL;

    core = (dom_core*)malloc(sizeof(dom_core));
    if (!core) {
        return DOM_STATUS_ERROR;
    }
    memset(core, 0, sizeof(*core));

    if (desc) {
        local_desc = *desc;
    } else {
        memset(&local_desc, 0, sizeof(local_desc));
    }

    local_desc.struct_size = sizeof(dom_core_desc);
    core->desc = local_desc;
    *out_core = core;
    return DOM_STATUS_OK;
}

void dom_core_destroy(dom_core* core)
{
    if (!core) {
        return;
    }
    free(core);
}

dom_status dom_core_update(dom_core* core, uint32_t dt_millis)
{
    (void)core;
    (void)dt_millis;
    return DOM_STATUS_OK;
}

dom_status dom_core_dispatch(dom_core* core, const char* command, const void* payload)
{
    (void)core;
    (void)command;
    (void)payload;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_core_query(dom_core* core, const char* query, void* response_buffer, size_t response_buffer_size)
{
    (void)core;
    (void)query;
    (void)response_buffer;
    (void)response_buffer_size;
    return DOM_STATUS_UNSUPPORTED;
}

dsys_context* dom_core_system(dom_core* core)
{
    if (!core) {
        return NULL;
    }
    return core->desc.sys;
}

dgfx_device* dom_core_gfx(dom_core* core)
{
    if (!core) {
        return NULL;
    }
    return core->desc.gfx;
}

daudio_device* dom_core_audio(dom_core* core)
{
    if (!core) {
        return NULL;
    }
    return core->desc.audio;
}

dom_event_bus* dom_core_events(dom_core* core)
{
    if (!core) {
        return NULL;
    }
    return core->desc.event_bus;
}

dom_sim* dom_core_sim(dom_core* core)
{
    (void)core;
    return NULL;
}

dom_canvas* dom_core_canvas(dom_core* core)
{
    (void)core;
    return NULL;
}
