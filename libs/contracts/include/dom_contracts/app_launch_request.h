/*
FILE: include/dom_contracts/app_launch_request.h
MODULE: Dominium
PURPOSE: Application-layer launch request contract (data-only).
NOTES: POD-only; TLV/JSON friendly; explicit versioning.
*/
#ifndef DOMINIUM_APP_LAUNCH_REQUEST_H
#define DOMINIUM_APP_LAUNCH_REQUEST_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_app_launch_request: Data-only launch request description. */
typedef struct dom_app_launch_request_t {
    u32 struct_size;
    u32 struct_version;
    const char* instance_id;      /* stable instance identifier; may be NULL */
    const char* profile_id;       /* profile selector; may be NULL */
    const char* role_id;          /* client/server/tools; may be NULL */
    const char* ui_mode;          /* none|tui|gui; may be NULL */
    const char* requested_mode;   /* app-defined launch mode; may be NULL */
    const char* working_dir;      /* optional working directory */
    u32 pack_count;
    const char* const* pack_ids;  /* array of pack ids; may be NULL when count=0 */
    u32 arg_count;
    const char* const* args;      /* argv-style args; may be NULL when count=0 */
} dom_app_launch_request;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_APP_LAUNCH_REQUEST_H */
