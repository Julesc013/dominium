/*
FILE: include/domino/execution/access_set.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / execution/access_set
RESPONSIBILITY: Defines the public contract for AccessSet (Access IR runtime).
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` and EXEC0.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant specs.
*/
#ifndef DOMINO_EXECUTION_ACCESS_SET_H
#define DOMINO_EXECUTION_ACCESS_SET_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Access range kind (explicit and bounded). */
typedef enum dom_access_range_kind {
    DOM_RANGE_ENTITY_SET   = 0,
    DOM_RANGE_COMPONENT_SET = 1,
    DOM_RANGE_INTEREST_SET = 2,
    DOM_RANGE_INDEX_RANGE  = 3,
    DOM_RANGE_SINGLE       = 4
} dom_access_range_kind;

/* Deterministic reduction operator identifiers. */
typedef enum dom_reduction_op {
    DOM_REDUCE_NONE = 0,
    DOM_REDUCE_INT_SUM,
    DOM_REDUCE_INT_MIN,
    DOM_REDUCE_INT_MAX,
    DOM_REDUCE_FIXED_SUM,
    DOM_REDUCE_BIT_OR,
    DOM_REDUCE_BIT_AND,
    DOM_REDUCE_BIT_XOR,
    DOM_REDUCE_HISTOGRAM_MERGE,
    DOM_REDUCE_SET_UNION
} dom_reduction_op;

/* Access range declaration. */
typedef struct dom_access_range {
    u32 kind;        /* dom_access_range_kind */
    u32 component_id;
    u32 field_id;
    u64 start_id;    /* for INDEX_RANGE/SINGLE */
    u64 end_id;      /* for INDEX_RANGE/SINGLE */
    u64 set_id;      /* for *_SET kinds */
} dom_access_range;

/* AccessSet runtime structure. */
typedef struct dom_access_set {
    u64 access_id;
    const dom_access_range *read_ranges;
    u32 read_count;
    const dom_access_range *write_ranges;
    u32 write_count;
    const dom_access_range *reduce_ranges;
    u32 reduce_count;
    u32 reduction_op; /* dom_reduction_op (applies to reduce_ranges) */
    d_bool commutative;
} dom_access_set;

/* Check if two access ranges overlap (conservative). */
d_bool dom_access_ranges_overlap(const dom_access_range *a, const dom_access_range *b);

/* Detect conflicts between two AccessSets. */
d_bool dom_detect_access_conflicts(const dom_access_set *a, const dom_access_set *b);

/* Verify deterministic reduction rules for a single AccessSet. */
d_bool dom_verify_reduction_rules(const dom_access_set *set);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_EXECUTION_ACCESS_SET_H */
