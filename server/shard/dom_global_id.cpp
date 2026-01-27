/*
FILE: server/shard/dom_global_id.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic global identifier generation and packing.
*/
#include "dom_global_id.h"

#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

void dom_global_id_gen_init(dom_global_id_gen* gen, u16 shard_of_origin)
{
    if (!gen) {
        return;
    }
    memset(gen, 0, sizeof(*gen));
    gen->shard_of_origin = shard_of_origin;
}

u64 dom_global_id_pack(const dom_global_id* id)
{
    u64 packed = 0u;
    if (!id) {
        return 0u;
    }
    packed |= ((u64)id->namespace_id & 0xFFFFu) << 48;
    packed |= ((u64)id->shard_of_origin & 0xFFFFu) << 32;
    packed |= (u64)id->local_id;
    return packed;
}

void dom_global_id_unpack(u64 packed, dom_global_id* out_id)
{
    if (!out_id) {
        return;
    }
    out_id->namespace_id = (u16)((packed >> 48) & 0xFFFFu);
    out_id->shard_of_origin = (u16)((packed >> 32) & 0xFFFFu);
    out_id->local_id = (u32)(packed & 0xFFFFFFFFu);
}

int dom_global_id_gen_next(dom_global_id_gen* gen,
                           u16 namespace_id,
                           dom_global_id* out_id,
                           u64* out_packed)
{
    dom_global_id id;
    u32 next_local;
    if (!gen) {
        return -1;
    }
    if (namespace_id >= DOM_GLOBAL_ID_NAMESPACE_CAP) {
        return -2;
    }
    next_local = gen->counters[namespace_id] + 1u;
    gen->counters[namespace_id] = next_local;
    id.namespace_id = namespace_id;
    id.shard_of_origin = gen->shard_of_origin;
    id.local_id = next_local;
    if (out_id) {
        *out_id = id;
    }
    if (out_packed) {
        *out_packed = dom_global_id_pack(&id);
    }
    return 0;
}

#ifdef __cplusplus
} /* extern "C" */
#endif

