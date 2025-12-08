#ifndef DOMINO_LAUNCHER_EXT_H_INCLUDED
#define DOMINO_LAUNCHER_EXT_H_INCLUDED

#include <stdint.h>
#include "domino/core.h"
#include "domino/view.h"
#include "domino/event.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_launcher_ext_api {
    uint32_t            struct_size;
    uint32_t            struct_version;
    dom_view_registry*  views;
    dom_event_bus*      events;
} dom_launcher_ext_api;

typedef struct dom_launcher_ext_vtable {
    uint32_t   struct_size;
    uint32_t   struct_version;
    dom_status (*on_load)(const dom_launcher_ext_api* api, void** out_state);
    void       (*on_unload)(void* state);
} dom_launcher_ext_vtable;

typedef dom_launcher_ext_vtable* (*dom_launcher_ext_entry_fn)(const dom_launcher_ext_api* api);

#define DOM_LAUNCHER_EXT_ENTRYPOINT "dom_launcher_ext_main"

typedef struct dom_launcher_ext_handle dom_launcher_ext_handle;

dom_status dom_launcher_ext_load(const char* path, dom_launcher_ext_handle** out_handle);
dom_status dom_launcher_ext_get_vtable(dom_launcher_ext_handle* handle, const dom_launcher_ext_api* api, dom_launcher_ext_vtable** out_vtable);
void       dom_launcher_ext_unload(dom_launcher_ext_handle* handle);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_LAUNCHER_EXT_H_INCLUDED */
