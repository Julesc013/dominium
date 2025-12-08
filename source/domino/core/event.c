#include "domino/event.h"

#include <stdlib.h>
#include <string.h>

struct dom_event_bus {
    dom_event_bus_desc desc;
};

dom_status dom_event_bus_create(const dom_event_bus_desc* desc, dom_event_bus** out_bus)
{
    dom_event_bus* bus;
    dom_event_bus_desc local_desc;

    if (!out_bus) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    *out_bus = NULL;

    bus = (dom_event_bus*)malloc(sizeof(dom_event_bus));
    if (!bus) {
        return DOM_STATUS_ERROR;
    }
    memset(bus, 0, sizeof(*bus));

    if (desc) {
        local_desc = *desc;
    } else {
        memset(&local_desc, 0, sizeof(local_desc));
    }
    local_desc.struct_size = sizeof(dom_event_bus_desc);
    bus->desc = local_desc;

    *out_bus = bus;
    return DOM_STATUS_OK;
}

void dom_event_bus_destroy(dom_event_bus* bus)
{
    if (!bus) {
        return;
    }
    free(bus);
}

dom_status dom_event_subscribe(dom_event_bus* bus, uint32_t category, dom_event_handler_fn handler, void* user_data)
{
    (void)bus;
    (void)category;
    (void)handler;
    (void)user_data;
    return DOM_STATUS_OK;
}

dom_status dom_event_unsubscribe(dom_event_bus* bus, dom_event_handler_fn handler, void* user_data)
{
    (void)bus;
    (void)handler;
    (void)user_data;
    return DOM_STATUS_OK;
}

dom_status dom_event_publish(dom_event_bus* bus, const dom_event_desc* event)
{
    (void)bus;
    (void)event;
    return DOM_STATUS_OK;
}
