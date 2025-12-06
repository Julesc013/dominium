#ifndef DOM_REGISTRY_VOLUME_H
#define DOM_REGISTRY_VOLUME_H

#include "core_types.h"
#include "core_ids.h"

typedef struct VolumeDesc {
    VolumeId    id;
    const char *name;
} VolumeDesc;

typedef struct VolumeRegistry {
    VolumeDesc *volumes;
    u16         count;
    u16         capacity;
} VolumeRegistry;

void volume_registry_init(VolumeRegistry *reg, u16 capacity);
void volume_registry_free(VolumeRegistry *reg);
VolumeId volume_register(VolumeRegistry *reg, const VolumeDesc *desc);
const VolumeDesc *volume_get(const VolumeRegistry *reg, VolumeId id);

#endif /* DOM_REGISTRY_VOLUME_H */
