/*
FILE: include/dom_contracts/app_launch_result.h
MODULE: Dominium
PURPOSE: Application-layer launch result contract (data-only).
NOTES: POD-only; TLV/JSON friendly; explicit versioning.
*/
#ifndef DOMINIUM_APP_LAUNCH_RESULT_H
#define DOMINIUM_APP_LAUNCH_RESULT_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_app_launch_result: Data-only result of a launch attempt. */
typedef struct dom_app_launch_result_t {
    u32 struct_size;
    u32 struct_version;
    int exit_code;            /* process exit code (0 = success) */
    const char* failure_code; /* optional canonical failure code */
    const char* message;      /* optional human-readable message */
} dom_app_launch_result;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_APP_LAUNCH_RESULT_H */
