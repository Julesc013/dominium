/*
FILE: include/domino/capability.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / capability
RESPONSIBILITY: Defines capability descriptors and deterministic matching utilities.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Matching is deterministic and order-stable (sorted inputs).
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_CAPABILITY_H
#define DOMINO_CAPABILITY_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_capability_id: Stable, data-defined capability identifier. */
typedef u64 dom_capability_id;

/* dom_capability_provider_kind: Capability source classification. */
typedef enum dom_capability_provider_kind {
    DOM_CAPABILITY_PROVIDER_AGENT = 0,
    DOM_CAPABILITY_PROVIDER_TOOL = 1,
    DOM_CAPABILITY_PROVIDER_MACHINE = 2,
    DOM_CAPABILITY_PROVIDER_INSTITUTION = 3,
    DOM_CAPABILITY_PROVIDER_INFRASTRUCTURE = 4
} dom_capability_provider_kind;

/* dom_capability_desc: Descriptor for a single capability (data-defined). */
typedef struct dom_capability_desc {
    dom_capability_id          id;
    const char*                key;     /* stable ASCII identifier */
    u32                        version; /* data-defined version */
    dom_capability_provider_kind provider_kind;
} dom_capability_desc;

/* dom_capability_set_view: Read-only view of sorted, unique capability ids. */
typedef struct dom_capability_set_view {
    const dom_capability_id* ids;
    u32                      count;
} dom_capability_set_view;

/* Purpose: Check whether a sorted capability set contains a capability id. */
d_bool dom_capability_set_contains(const dom_capability_set_view* set,
                                   dom_capability_id id);

/* Purpose: Check whether all required capabilities are provided. */
d_bool dom_capability_set_is_subset(const dom_capability_set_view* required,
                                    const dom_capability_set_view* provided);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CAPABILITY_H */
