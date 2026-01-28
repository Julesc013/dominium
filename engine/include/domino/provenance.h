/*
FILE: include/domino/provenance.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / provenance
RESPONSIBILITY: Defines seed namespaces and provenance records for deterministic lineage.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: All derivations MUST be deterministic and namespace-scoped.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/architectureitecture/**`.
*/
#ifndef DOMINO_PROVENANCE_H
#define DOMINO_PROVENANCE_H

#include "domino/dnumeric.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_seed_namespace: Explicit seed namespace (data-defined). */
typedef u32 dom_seed_namespace;

/* dom_seed: Deterministic 64-bit seed value. */
typedef u64 dom_seed;

/* dom_seed_ref: Universe seed + namespace + per-stream selector. */
typedef struct dom_seed_ref {
    dom_seed          universe_seed;
    dom_seed_namespace namespace_id;
    u64               stream_id;
    u64               salt;
} dom_seed_ref;

/* dom_provenance_id: Stable identifier for provenance records. */
typedef u64 dom_provenance_id;

/* dom_provenance_record: Lineage metadata for processes, fields, and snapshots. */
typedef struct dom_provenance_record {
    dom_provenance_id id;
    dom_provenance_id parent_id;
    dom_seed_ref      seed;
    u64               process_id;
    u64               authority_id;
    SimTick           tick;
} dom_provenance_record;

/* Purpose: Derive a deterministic seed value from a seed reference. */
dom_seed dom_seed_derive(const dom_seed_ref* seed_ref);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_PROVENANCE_H */
