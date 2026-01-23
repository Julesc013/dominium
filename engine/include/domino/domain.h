/*
FILE: include/domino/domain.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / domain
RESPONSIBILITY: Defines domain kinds, bounds, and domain volume descriptors.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Bounds and descriptors are deterministic inputs to processes/snapshots.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_DOMAIN_H
#define DOMINO_DOMAIN_H

#include "domino/core/types.h"
#include "domino/world/domain_tile.h"
#include "domino/representation.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_domain_kind: Domain classification (data-defined beyond these categories). */
typedef enum dom_domain_kind {
    DOM_DOMAIN_KIND_SPATIAL = 0,
    DOM_DOMAIN_KIND_JURISDICTIONAL = 1,
    DOM_DOMAIN_KIND_ECONOMIC = 2,
    DOM_DOMAIN_KIND_INSTITUTIONAL = 3
} dom_domain_kind;

/* dom_domain_bounds_kind: Bounds encoding kind. */
typedef enum dom_domain_bounds_kind {
    DOM_DOMAIN_BOUNDS_AABB = 0,
    DOM_DOMAIN_BOUNDS_TLV = 1
} dom_domain_bounds_kind;

/* dom_domain_bounds_desc: Explicit bounds for a domain volume. */
typedef struct dom_domain_bounds_desc {
    u32              kind; /* dom_domain_bounds_kind */
    dom_domain_aabb  aabb; /* valid when kind == DOM_DOMAIN_BOUNDS_AABB */
    const void*      blob; /* optional opaque encoding when kind == DOM_DOMAIN_BOUNDS_TLV */
    u32              blob_size;
} dom_domain_bounds_desc;

/* dom_domain_volume_ref: Stable, versioned domain volume reference. */
typedef struct dom_domain_volume_ref {
    dom_domain_id id;
    u32          version;
} dom_domain_volume_ref;

/* dom_domain_volume_desc: Read-only descriptor for domain volume metadata. */
typedef struct dom_domain_volume_desc {
    dom_domain_volume_ref  ref;
    dom_domain_kind        kind;
    dom_domain_bounds_desc bounds;
    dom_representation_meta representation;
    u32                    flags;
} dom_domain_volume_desc;

/* Opaque domain volume handle. */
typedef struct dom_domain_volume_handle dom_domain_volume_handle;

/* Purpose: Describe a domain volume handle. */
int dom_domain_volume_describe(const dom_domain_volume_handle* volume,
                               dom_domain_volume_desc* out_desc);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_DOMAIN_H */
