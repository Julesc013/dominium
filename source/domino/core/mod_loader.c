#include "domino/mod.h"

#include <stdlib.h>
#include <string.h>

struct dom_mod_handle {
    char dummy;
};

dom_status dom_mod_load(const char* path, dom_mod_handle** out_handle)
{
    dom_mod_handle* handle;

    (void)path;
    if (!out_handle) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    *out_handle = NULL;

    handle = (dom_mod_handle*)malloc(sizeof(dom_mod_handle));
    if (!handle) {
        return DOM_STATUS_ERROR;
    }
    memset(handle, 0, sizeof(*handle));

    *out_handle = handle;
    return DOM_STATUS_OK;
}

dom_status dom_mod_get_vtable(dom_mod_handle* handle, const dom_mod_api* api, dom_mod_vtable** out_vtable)
{
    (void)handle;
    (void)api;
    if (!out_vtable) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    *out_vtable = NULL;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_mod_unload(dom_mod_handle* handle)
{
    if (!handle) {
        return;
    }
    free(handle);
}
