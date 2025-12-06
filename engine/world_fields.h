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
