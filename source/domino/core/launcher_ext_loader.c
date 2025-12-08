#include "domino/launcher_ext.h"

#include <stdlib.h>
#include <string.h>

struct dom_launcher_ext_handle {
    char dummy;
};

dom_status dom_launcher_ext_load(const char* path, dom_launcher_ext_handle** out_handle)
{
    dom_launcher_ext_handle* handle;

    (void)path;
    if (!out_handle) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    *out_handle = NULL;

    handle = (dom_launcher_ext_handle*)malloc(sizeof(dom_launcher_ext_handle));
    if (!handle) {
        return DOM_STATUS_ERROR;
    }
    memset(handle, 0, sizeof(*handle));

    *out_handle = handle;
    return DOM_STATUS_OK;
}

dom_status dom_launcher_ext_get_vtable(dom_launcher_ext_handle* handle, const dom_launcher_ext_api* api, dom_launcher_ext_vtable** out_vtable)
{
    (void)handle;
    (void)api;
    if (!out_vtable) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    *out_vtable = NULL;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_launcher_ext_unload(dom_launcher_ext_handle* handle)
{
    if (!handle) {
        return;
    }
    free(handle);
}
