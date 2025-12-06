#include "registry_volume.h"

#include <stdlib.h>
#include <string.h>

void volume_registry_init(VolumeRegistry *reg, u16 capacity)
{
    if (!reg) return;
    memset(reg, 0, sizeof(*reg));
    if (capacity > 0) {
        reg->volumes = (VolumeDesc *)malloc(sizeof(VolumeDesc) * capacity);
        if (reg->volumes) {
            reg->capacity = capacity;
        }
    }
}

void volume_registry_free(VolumeRegistry *reg)
{
    if (!reg) return;
    if (reg->volumes) {
        free(reg->volumes);
        reg->volumes = NULL;
    }
    reg->capacity = 0;
    reg->count = 0;
}

VolumeId volume_register(VolumeRegistry *reg, const VolumeDesc *desc)
{
    VolumeDesc *slot;
    if (!reg || !desc) return 0;
    if (reg->count >= reg->capacity) {
        u16 new_cap = (reg->capacity == 0) ? 4U : (u16)(reg->capacity * 2U);
        VolumeDesc *new_arr = (VolumeDesc *)realloc(reg->volumes, sizeof(VolumeDesc) * new_cap);
        if (!new_arr) {
            return 0;
        }
        reg->volumes = new_arr;
        reg->capacity = new_cap;
    }
    slot = &reg->volumes[reg->count];
    *slot = *desc;
    slot->id = reg->count;
    reg->count++;
    return slot->id;
}

const VolumeDesc *volume_get(const VolumeRegistry *reg, VolumeId id)
{
    if (!reg) return NULL;
    if (id >= reg->count) return NULL;
    return &reg->volumes[id];
}
