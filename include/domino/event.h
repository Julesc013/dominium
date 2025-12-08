#ifndef DOMINO_EVENT_H_INCLUDED
#define DOMINO_EVENT_H_INCLUDED

#include <stdint.h>
#include "domino/core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_event_kind {
    DOM_EVT_NONE = 0
} dom_event_kind;

typedef struct dom_event {
    uint32_t       struct_size;
    uint32_t       struct_version;
    dom_event_kind kind;
} dom_event;

typedef void (*dom_event_handler)(dom_core* core, const dom_event* evt, void* user);

bool dom_event_subscribe(dom_core* core, dom_event_kind kind, dom_event_handler fn, void* user);
bool dom_event_unsubscribe(dom_core* core, dom_event_kind kind, dom_event_handler fn, void* user);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_EVENT_H_INCLUDED */
