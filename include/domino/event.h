#ifndef DOMINO_EVENT_H_INCLUDED
#define DOMINO_EVENT_H_INCLUDED

#include <stdint.h>
#include "domino/core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DOM_EVT_NONE = 0,
    DOM_EVT_PKG_INSTALLED,
    DOM_EVT_PKG_UNINSTALLED,
    DOM_EVT_INST_CREATED,
    DOM_EVT_INST_UPDATED,
    DOM_EVT_INST_DELETED,
    DOM_EVT_SIM_TICKED
} dom_event_kind;

typedef struct {
    uint32_t       struct_size;
    uint32_t       struct_version;
    dom_event_kind kind;
    union {
        dom_package_id  pkg_id;
        dom_instance_id inst_id;
    } u;
} dom_event;

typedef void (*dom_event_handler)(dom_core* core, const dom_event* ev, void* user);

bool dom_event_subscribe(dom_core* core, dom_event_kind kind, dom_event_handler fn, void* user);
bool dom_event_unsubscribe(dom_core* core, dom_event_kind kind, dom_event_handler fn, void* user);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_EVENT_H_INCLUDED */
