/* Unified subsystem serialization orchestrator (C89). */
#ifndef D_SERIALIZE_H
#define D_SERIALIZE_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"

#ifdef __cplusplus
extern "C" {
#endif

struct d_world;
struct d_chunk;

/* Save all subsystems’ chunk data into a container buffer. */
int d_serialize_save_chunk_all(
    struct d_world    *w,
    struct d_chunk    *chunk,
    struct d_tlv_blob *out
);

/* Load all subsystems’ chunk data from a container buffer. */
int d_serialize_load_chunk_all(
    struct d_world          *w,
    struct d_chunk          *chunk,
    const struct d_tlv_blob *in
);

/* Save all subsystems’ instance/global data. */
int d_serialize_save_instance_all(
    struct d_world    *w,
    struct d_tlv_blob *out
);

/* Load all subsystems’ instance/global data. */
int d_serialize_load_instance_all(
    struct d_world          *w,
    const struct d_tlv_blob *in
);

#ifdef __cplusplus
}
#endif

#endif /* D_SERIALIZE_H */
