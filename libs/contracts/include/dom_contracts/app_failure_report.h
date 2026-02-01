/*
FILE: include/dom_contracts/app_failure_report.h
MODULE: Dominium
PURPOSE: Application-layer failure report (data-only).
NOTES: POD-only; TLV/JSON friendly; explicit versioning.
*/
#ifndef DOMINIUM_APP_FAILURE_REPORT_H
#define DOMINIUM_APP_FAILURE_REPORT_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_app_failure_report: structured failure details. */
typedef struct dom_app_failure_report_t {
    u32 struct_size;
    u32 struct_version;
    const char* failure_code; /* canonical failure code */
    const char* category;     /* user_error|system_error|compatibility|integrity|permission */
    const char* severity;     /* info|warning|error|fatal */
    const char* message_key;  /* localization key */
    const char* message;      /* human-readable fallback */
    const char* provenance;   /* optional */
} dom_app_failure_report;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_APP_FAILURE_REPORT_H */
