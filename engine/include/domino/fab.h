/*
FILE: include/domino/fab.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / fab
RESPONSIBILITY: Defines shared FAB (fabrication) enums and refusal codes.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: FAB enums and refusal codes are deterministic identifiers.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/architecture/REFUSAL_SEMANTICS.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_FAB_H
#define DOMINO_FAB_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_fab_interface_type: Canonical interface type tags (data-driven). */
typedef enum dom_fab_interface_type {
    DOM_FAB_IFACE_UNKNOWN    = 0,
    DOM_FAB_IFACE_MECHANICAL = 1,
    DOM_FAB_IFACE_ELECTRICAL = 2,
    DOM_FAB_IFACE_FLUID      = 3,
    DOM_FAB_IFACE_DATA       = 4,
    DOM_FAB_IFACE_THERMAL    = 5
} dom_fab_interface_type;

/* dom_fab_directionality: Canonical directionality tags (data-driven). */
typedef enum dom_fab_directionality {
    DOM_FAB_DIR_UNKNOWN = 0,
    DOM_FAB_DIR_INPUT = 1,
    DOM_FAB_DIR_OUTPUT = 2,
    DOM_FAB_DIR_BIDIRECTIONAL = 3
} dom_fab_directionality;

/* dom_fab_compat_result: Compatibility evaluation result. */
typedef enum dom_fab_compat_result {
    DOM_FAB_COMPAT_OK = 0,
    DOM_FAB_COMPAT_DEGRADED = 1,
    DOM_FAB_COMPAT_REFUSE = 2
} dom_fab_compat_result;

/* Canonical refusal codes (see docs/architecture/REFUSAL_SEMANTICS.md). */
enum {
    DOM_FAB_REFUSE_NONE = 0u,
    DOM_FAB_REFUSE_INVALID_INTENT = 1u,
    DOM_FAB_REFUSE_LAW_FORBIDDEN = 2u,
    DOM_FAB_REFUSE_CAPABILITY_MISSING = 3u,
    DOM_FAB_REFUSE_DOMAIN_FORBIDDEN = 4u,
    DOM_FAB_REFUSE_INTEGRITY_VIOLATION = 5u,
    DOM_FAB_REFUSE_RATE_LIMIT = 6u,
    DOM_FAB_REFUSE_BUDGET_EXCEEDED = 7u
};

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_FAB_H */
