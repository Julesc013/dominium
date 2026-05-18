/*
FILE: include/dom_contracts/app_capabilities.h
MODULE: Dominium
PURPOSE: Application-layer capability catalog (data-only).
NOTES: POD-only; TLV/JSON friendly; explicit versioning.
*/
#ifndef DOMINIUM_APP_CAPABILITIES_H
#define DOMINIUM_APP_CAPABILITIES_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_APP_CAPABILITY_MAX_ENTRIES 128u

/* dom_app_capability_entry: single capability entry. */
typedef struct dom_app_capability_entry_t {
    const char* capability_id;
    const char* description;
    u32 mutation_allowed;   /* 0/1 */
    u32 network_required;   /* 0/1 */
    const char* pack_access;/* none|read|write */
    const char* authority_scope; /* none|install|launch|inspect */
    const char* provenance; /* optional */
} dom_app_capability_entry;

/* dom_app_capabilities: collection of capabilities. */
typedef struct dom_app_capabilities_t {
    u32 struct_size;
    u32 struct_version;
    u32 count;
    dom_app_capability_entry entries[DOM_APP_CAPABILITY_MAX_ENTRIES];
} dom_app_capabilities;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_APP_CAPABILITIES_H */
