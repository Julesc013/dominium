/*
FILE: include/dom_contracts/app_pack_state.h
MODULE: Dominium
PURPOSE: Application-layer pack state summary (data-only).
NOTES: POD-only; TLV/JSON friendly; explicit versioning.
*/
#ifndef DOMINIUM_APP_PACK_STATE_H
#define DOMINIUM_APP_PACK_STATE_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_app_pack_state: Minimal pack state summary. */
typedef struct dom_app_pack_state_t {
    u32 struct_size;
    u32 struct_version;
    const char* pack_id;
    const char* pack_version;
    u32 enabled;                 /* 0/1 */
    const char* pack_origin;     /* optional provenance */
    const char* signature_status;/* optional signature status */
    const char* compatibility_range; /* optional compatibility range */
} dom_app_pack_state;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_APP_PACK_STATE_H */
