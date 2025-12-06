#ifndef DOM_REGISTRY_MATERIAL_H
#define DOM_REGISTRY_MATERIAL_H

#include "core_types.h"
#include "core_fixed.h"
#include "core_ids.h"

typedef u16 MatId;

typedef struct MaterialDesc {
    MatId        id;
    const char  *name;
    fix32        density;
    fix32        hardness;
    fix32        melting_point;
    fix32        boiling_point;
} MaterialDesc;

typedef struct MaterialRegistry {
    MaterialDesc *materials;
    u16           count;
    u16           capacity;
} MaterialRegistry;

void material_registry_init(MaterialRegistry *reg, u16 capacity);
void material_registry_free(MaterialRegistry *reg);
MatId material_register(MaterialRegistry *reg, const MaterialDesc *desc);
const MaterialDesc *material_get(const MaterialRegistry *reg, MatId id);

#endif /* DOM_REGISTRY_MATERIAL_H */
