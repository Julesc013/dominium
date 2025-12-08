#ifndef DOMINO_EVENT_H_INCLUDED
#define DOMINO_EVENT_H_INCLUDED

#include <stdint.h>
#include "domino/core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_event_bus dom_event_bus;

typedef struct dom_event_desc {
    uint32_t    struct_size;
    uint32_t    struct_version;
    uint32_t    category;
    uint32_t    type;
    const void* payload;
    uint32_t    payload_size;
} dom_event_desc;

typedef struct dom_event_bus_desc {
    uint32_t struct_size;
    uint32_t struct_version;
} dom_event_bus_desc;

typedef void (*dom_event_handler_fn)(const dom_event_desc* event, void* user_data);

dom_status dom_event_bus_create(const dom_event_bus_desc* desc, dom_event_bus** out_bus);
void       dom_event_bus_destroy(dom_event_bus* bus);
dom_status dom_event_subscribe(dom_event_bus* bus, uint32_t category, dom_event_handler_fn handler, void* user_data);
dom_status dom_event_unsubscribe(dom_event_bus* bus, dom_event_handler_fn handler, void* user_data);
dom_status dom_event_publish(dom_event_bus* bus, const dom_event_desc* event);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_EVENT_H_INCLUDED */
