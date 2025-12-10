#include "domino/mod.h"
#include "core_internal.h"

bool dom_mod_load_all(dom_core* core, dom_instance_id inst)
{
    (void)core;
    (void)inst;
    return true;
}

void dom_mod_unload_all(dom_core* core, dom_instance_id inst)
{
    (void)core;
    (void)inst;
}

uint32_t dom_launcher_ext_count(dom_core* core)
{
    if (!core) return 0u;
    return core->launcher_ext_count;
}

const dom_launcher_ext_v1* dom_launcher_ext_get(dom_core* core, uint32_t index)
{
    if (!core || index >= core->launcher_ext_count) {
        return NULL;
    }
    return &core->launcher_exts[index];
}

bool dom_launcher_ext_register(dom_core* core, const dom_launcher_ext_v1* ext)
{
    dom_launcher_ext_v1* dst;
    if (!core || !ext) {
        return false;
    }
    if (ext->struct_size < sizeof(dom_launcher_ext_v1) ||
        ext->struct_version == 0u) {
        return false;
    }
    if (core->launcher_ext_count >= DOM_MAX_LAUNCHER_EXT) {
        return false;
    }
    dst = &core->launcher_exts[core->launcher_ext_count];
    *dst = *ext;
    core->launcher_ext_count += 1u;
    return true;
}
