#ifndef DOMINO_CORE_H_INCLUDED
#define DOMINO_CORE_H_INCLUDED

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_status {
    DOM_STATUS_OK = 0,
    DOM_STATUS_ERROR = -1,
    DOM_STATUS_INVALID_ARGUMENT = -2,
    DOM_STATUS_UNSUPPORTED = -3,
    DOM_STATUS_NOT_FOUND = -4
} dom_status;

typedef struct dsys_context    dsys_context;
typedef struct dgfx_device     dgfx_device;
typedef struct daudio_device   daudio_device;
typedef struct dom_event_bus   dom_event_bus;
typedef struct dom_canvas      dom_canvas;
typedef struct dom_sim         dom_sim;
typedef struct dom_pkg_registry dom_pkg_registry;

typedef struct dom_core dom_core;

typedef struct dom_core_desc {
    uint32_t        struct_size;
    uint32_t        struct_version;
    dsys_context*   sys;
    dgfx_device*    gfx;
    daudio_device*  audio;
    dom_event_bus*  event_bus;
    dom_pkg_registry* pkg_registry;
    const char*     product_id;
    uint32_t        flags;
} dom_core_desc;

dom_status dom_core_create(const dom_core_desc* desc, dom_core** out_core);
void       dom_core_destroy(dom_core* core);

dom_status dom_core_update(dom_core* core, uint32_t dt_millis);
dom_status dom_core_dispatch(dom_core* core, const char* command, const void* payload);
dom_status dom_core_query(dom_core* core, const char* query, void* response_buffer, size_t response_buffer_size);

dsys_context*    dom_core_system(dom_core* core);
dgfx_device*     dom_core_gfx(dom_core* core);
daudio_device*   dom_core_audio(dom_core* core);
dom_event_bus*   dom_core_events(dom_core* core);
dom_sim*         dom_core_sim(dom_core* core);
dom_canvas*      dom_core_canvas(dom_core* core);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_CORE_H_INCLUDED */
