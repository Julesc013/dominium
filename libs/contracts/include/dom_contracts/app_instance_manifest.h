/*
FILE: include/dom_contracts/app_instance_manifest.h
MODULE: Dominium
PURPOSE: Application-layer instance manifest summary (data-only).
NOTES: POD-only; TLV/JSON friendly; explicit versioning.
*/
#ifndef DOMINIUM_APP_INSTANCE_MANIFEST_H
#define DOMINIUM_APP_INSTANCE_MANIFEST_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_app_instance_manifest: Minimal instance manifest summary. */
typedef struct dom_app_instance_manifest_t {
    u32 struct_size;
    u32 struct_version;
    const char* instance_id;      /* stable instance identifier */
    const char* instance_name;    /* optional display name */
    const char* data_root;        /* instance data root */
    const char* manifest_version; /* manifest version string */
    u32 pack_count;
    const char* const* pack_ids;  /* resolved pack ids */
} dom_app_instance_manifest;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_APP_INSTANCE_MANIFEST_H */
