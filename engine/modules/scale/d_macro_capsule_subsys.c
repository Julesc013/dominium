/*
FILE: engine/modules/scale/d_macro_capsule_subsys.c
RESPONSIBILITY: Register macro capsule save chunk subsystem.
*/
#include "core/d_subsystem.h"
#include "scale/d_macro_capsule_store.h"

static int g_macro_capsule_registered = 0;

static void d_macro_capsule_init_instance(d_world* world)
{
    d_macro_capsule_store_init(world);
}

static int d_macro_capsule_save_instance(d_world* world, d_tlv_blob* out_blob)
{
    return d_macro_capsule_store_serialize(world, out_blob);
}

static int d_macro_capsule_load_instance(d_world* world, const d_tlv_blob* in_blob)
{
    return d_macro_capsule_store_deserialize(world, in_blob);
}

void d_macro_capsule_register_subsystem(void)
{
    d_subsystem_desc desc;
    const d_subsystem_desc* existing;
    int rc;

    if (g_macro_capsule_registered) {
        return;
    }
    existing = d_subsystem_get_by_id(D_SUBSYS_MACRO_CAPSULE);
    if (existing) {
        g_macro_capsule_registered = 1;
        return;
    }

    desc.subsystem_id = D_SUBSYS_MACRO_CAPSULE;
    desc.name = "macro_capsule";
    desc.version = 1u;
    desc.register_models = (void (*)(void))0;
    desc.load_protos = (void (*)(const struct d_tlv_blob*))0;
    desc.init_instance = d_macro_capsule_init_instance;
    desc.tick = (void (*)(struct d_world*, u32))0;
    desc.save_chunk = (int (*)(struct d_world*, struct d_chunk*, struct d_tlv_blob*))0;
    desc.load_chunk = (int (*)(struct d_world*, struct d_chunk*, const struct d_tlv_blob*))0;
    desc.save_instance = d_macro_capsule_save_instance;
    desc.load_instance = d_macro_capsule_load_instance;

    rc = d_subsystem_register(&desc);
    if (rc == 0) {
        g_macro_capsule_registered = 1;
    }
}
