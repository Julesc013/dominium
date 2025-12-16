/*
FILE: source/domino/sim/_legacy/core_sim/world_fields.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/world_fields
RESPONSIBILITY: Defines internal contract for `world_fields`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_WORLD_FIELDS_H
#define DOM_WORLD_FIELDS_H

#include "core_fixed.h"
#include "world_addr.h"

typedef u16 FieldId;
#define FIELD_ID_ELEVATION   ((FieldId)1)
#define FIELD_ID_TEMPERATURE ((FieldId)2)

typedef struct FieldScalarSample {
    fix32 value;
} FieldScalarSample;

typedef struct FieldVectorSample {
    fix32 x;
    fix32 y;
    fix32 z;
} FieldVectorSample;

struct SurfaceRuntime;

b32 field_sample_scalar(struct SurfaceRuntime *surface, const SimPos *pos, FieldId id, FieldScalarSample *out);
b32 field_sample_vector(struct SurfaceRuntime *surface, const SimPos *pos, FieldId id, FieldVectorSample *out);

#endif /* DOM_WORLD_FIELDS_H */
