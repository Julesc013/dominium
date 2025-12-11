/* Global subsystem registry (C89).
 * This describes Domino subsystems and the callbacks used to orchestrate
 * initialization, ticking, and serialization.
 */
#ifndef D_SUBSYSTEM_H
#define D_SUBSYSTEM_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u16 d_subsystem_id;

/* Subsystem IDs: define a small initial set; more will be added later. */
enum {
    D_SUBSYS_WORLD  = 1,  /* world/chunk core */
    D_SUBSYS_RES    = 2,  /* resources */
    D_SUBSYS_ENV    = 3,  /* environment */
    D_SUBSYS_BUILD  = 4,  /* buildings */
    D_SUBSYS_TRANS  = 5,  /* transport */
    D_SUBSYS_STRUCT = 6,  /* machines/structures */
    D_SUBSYS_VEH    = 7,  /* vehicles */
    D_SUBSYS_JOB    = 8,  /* jobs/AI */
    D_SUBSYS_NET    = 9,  /* networking */
    D_SUBSYS_REPLAY = 10, /* replay */
    /* Reserve 1000+ for mods/third-party subsystems in the future. */
};

/* Forward declarations to avoid circular deps. */
struct d_world;
struct d_chunk;
struct d_tlv_blob;

/* Subsystem descriptor */
typedef struct d_subsystem_desc {
    d_subsystem_id subsystem_id;
    const char    *name;       /* e.g. "res", "env", "build" */
    u32            version;    /* subsystem schema/ABI version */

    /* Called during engine global initialization to register models etc. */
    void (*register_models)(void);

    /* Called to load subsystem-specific protos from TLV content blobs. */
    void (*load_protos)(const struct d_tlv_blob *blob);

    /* Called when a world/instance is created or loaded. */
    void (*init_instance)(struct d_world *w);

    /* Called each tick, after core ECS tick dispatch, for global subsystem work. */
    void (*tick)(struct d_world *w, u32 ticks);

    /* Serialization hooks – chunk-level. */
    int (*save_chunk)(
        struct d_world    *w,
        struct d_chunk    *chunk,
        struct d_tlv_blob *out
    );

    int (*load_chunk)(
        struct d_world          *w,
        struct d_chunk          *chunk,
        const struct d_tlv_blob *in
    );

    /* Serialization hooks – instance/global-level. */
    int (*save_instance)(
        struct d_world    *w,
        struct d_tlv_blob *out
    );

    int (*load_instance)(
        struct d_world          *w,
        const struct d_tlv_blob *in
    );
} d_subsystem_desc;

/* Registry APIs */
int  d_subsystem_register(const d_subsystem_desc *desc);
/* Returns number of registered subsystems */
u32  d_subsystem_count(void);
/* Access by index (0..count-1); returns NULL on out-of-range. */
const d_subsystem_desc *d_subsystem_get_by_index(u32 index);
/* Access by id; returns NULL if not found. */
const d_subsystem_desc *d_subsystem_get_by_id(d_subsystem_id id);

#ifdef __cplusplus
}
#endif

#endif /* D_SUBSYSTEM_H */
