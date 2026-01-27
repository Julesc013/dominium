/*
FILE: server/shard/dom_global_id.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic, collision-free global identifier helpers.
ALLOWED DEPENDENCIES: engine public headers only.
FORBIDDEN DEPENDENCIES: game headers, OS/platform headers.
*/
#ifndef DOMINIUM_SERVER_SHARD_DOM_GLOBAL_ID_H
#define DOMINIUM_SERVER_SHARD_DOM_GLOBAL_ID_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_global_id {
    u16 namespace_id;
    u16 shard_of_origin;
    u32 local_id;
} dom_global_id;

/*
Logical namespaces are canon-level identifiers. The capacity is a hard
deterministic bound for server-side minting without coordination.
*/
#define DOM_GLOBAL_ID_NAMESPACE_CAP 256u

typedef struct dom_global_id_gen {
    u16 shard_of_origin;
    u32 counters[DOM_GLOBAL_ID_NAMESPACE_CAP];
} dom_global_id_gen;

void dom_global_id_gen_init(dom_global_id_gen* gen, u16 shard_of_origin);
int dom_global_id_gen_next(dom_global_id_gen* gen,
                           u16 namespace_id,
                           dom_global_id* out_id,
                           u64* out_packed);

u64 dom_global_id_pack(const dom_global_id* id);
void dom_global_id_unpack(u64 packed, dom_global_id* out_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_SHARD_DOM_GLOBAL_ID_H */

