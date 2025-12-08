#include <stdlib.h>
#include <string.h>
#include "core_internal.h"

static void dom_copy_string(char* dst, size_t cap, const char* src)
{
    size_t len;

    if (!dst || cap == 0) {
        return;
    }

    if (!src) {
        dst[0] = '\0';
        return;
    }

    len = strlen(src);
    if (len >= cap) {
        len = cap - 1;
    }
    memcpy(dst, src, len);
    dst[len] = '\0';
}

static dom_instance_record* dom_find_instance(dom_core* core, dom_instance_id id)
{
    uint32_t i;

    if (!core) {
        return NULL;
    }

    for (i = 0; i < core->instance_count; ++i) {
        if (core->instances[i].info.id == id) {
            return &core->instances[i];
        }
    }

    return NULL;
}

uint32_t dom_inst_list(dom_core* core, dom_instance_info* out, uint32_t max_out)
{
    uint32_t i;
    uint32_t count;

    if (!core || !out || max_out == 0) {
        return 0;
    }

    count = core->instance_count;
    if (count > max_out) {
        count = max_out;
    }

    for (i = 0; i < count; ++i) {
        out[i] = core->instances[i].info;
    }

    return count;
}

bool dom_inst_get(dom_core* core, dom_instance_id id, dom_instance_info* out)
{
    dom_instance_record* rec;

    if (!core || !out) {
        return false;
    }

    rec = dom_find_instance(core, id);
    if (!rec) {
        return false;
    }

    *out = rec->info;
    return true;
}

dom_instance_id dom_inst_create(dom_core* core, const dom_instance_info* desc)
{
    dom_instance_record* rec;

    if (!core) {
        return 0;
    }

    if (core->instance_count >= DOM_MAX_INSTANCES) {
        return 0;
    }

    rec = &core->instances[core->instance_count];
    memset(rec, 0, sizeof(*rec));
    rec->info.struct_size = sizeof(dom_instance_info);
    rec->info.struct_version = 1;
    rec->info.id = core->next_instance_id++;
    if (desc) {
        dom_copy_string(rec->info.name, sizeof(rec->info.name), desc->name);
        dom_copy_string(rec->info.path, sizeof(rec->info.path), desc->path);
        rec->info.flags = desc->flags;
        rec->info.pkg_count = desc->pkg_count;
        if (rec->info.pkg_count > DOM_MAX_INSTANCE_PACKAGES) {
            rec->info.pkg_count = DOM_MAX_INSTANCE_PACKAGES;
        }
        if (rec->info.pkg_count > 0) {
            memcpy(rec->info.pkgs, desc->pkgs, rec->info.pkg_count * sizeof(dom_package_id));
        }
    } else {
        dom_copy_string(rec->info.name, sizeof(rec->info.name), "instance");
        rec->info.pkg_count = 0;
    }

    rec->sim.struct_size = sizeof(dom_sim_state);
    rec->sim.struct_version = 1;
    rec->sim.ticks = 0;
    rec->sim.sim_time_s = 0.0;
    rec->sim.dt_s = 0.0;

    core->instance_count += 1;
    return rec->info.id;
}

bool dom_inst_update(dom_core* core, const dom_instance_info* desc)
{
    dom_instance_record* rec;

    if (!core || !desc) {
        return false;
    }

    rec = dom_find_instance(core, desc->id);
    if (!rec) {
        return false;
    }

    rec->info.flags = desc->flags;
    dom_copy_string(rec->info.name, sizeof(rec->info.name), desc->name);
    dom_copy_string(rec->info.path, sizeof(rec->info.path), desc->path);
    rec->info.pkg_count = desc->pkg_count;
    if (rec->info.pkg_count > DOM_MAX_INSTANCE_PACKAGES) {
        rec->info.pkg_count = DOM_MAX_INSTANCE_PACKAGES;
    }
    if (rec->info.pkg_count > 0) {
        memcpy(rec->info.pkgs, desc->pkgs, rec->info.pkg_count * sizeof(dom_package_id));
    }

    return true;
}

bool dom_inst_delete(dom_core* core, dom_instance_id id)
{
    uint32_t i;

    if (!core) {
        return false;
    }

    for (i = 0; i < core->instance_count; ++i) {
        if (core->instances[i].info.id == id) {
            for (; i + 1 < core->instance_count; ++i) {
                core->instances[i] = core->instances[i + 1];
            }
            core->instance_count -= 1;
            return true;
        }
    }

    return false;
}
