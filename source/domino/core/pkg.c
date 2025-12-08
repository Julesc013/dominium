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

uint32_t dom_pkg_list(dom_core* core, dom_package_info* out, uint32_t max_out)
{
    uint32_t i;
    uint32_t count;

    if (!core || !out || max_out == 0) {
        return 0;
    }

    count = core->package_count;
    if (count > max_out) {
        count = max_out;
    }

    for (i = 0; i < count; ++i) {
        out[i] = core->packages[i];
    }

    return count;
}

bool dom_pkg_get(dom_core* core, dom_package_id id, dom_package_info* out)
{
    uint32_t i;

    if (!core || !out) {
        return false;
    }

    for (i = 0; i < core->package_count; ++i) {
        if (core->packages[i].id == id) {
            *out = core->packages[i];
            return true;
        }
    }

    return false;
}

bool dom_pkg_install(dom_core* core, const char* source_path, dom_package_id* out_id)
{
    dom_package_info* pkg;
    char name_buf[64];

    if (!core) {
        return false;
    }

    if (core->package_count >= DOM_MAX_PACKAGES) {
        return false;
    }

    pkg = &core->packages[core->package_count];
    memset(pkg, 0, sizeof(*pkg));
    pkg->struct_size = sizeof(dom_package_info);
    pkg->struct_version = 1;
    pkg->id = core->next_package_id++;
    pkg->kind = DOM_PKG_KIND_UNKNOWN;
    dom_copy_string(pkg->install_path, sizeof(pkg->install_path), source_path);
    dom_copy_string(pkg->version, sizeof(pkg->version), "0.0.0");
    dom_copy_string(pkg->author, sizeof(pkg->author), "unknown");
    pkg->dep_count = 0;
    pkg->game_version_min[0] = '\0';
    pkg->game_version_max[0] = '\0';

    dom_copy_string(name_buf, sizeof(name_buf), source_path);
    if (name_buf[0] == '\0') {
        dom_copy_string(name_buf, sizeof(name_buf), "package");
    }
    dom_copy_string(pkg->name, sizeof(pkg->name), name_buf);

    if (out_id) {
        *out_id = pkg->id;
    }

    core->package_count += 1;
    return true;
}

bool dom_pkg_uninstall(dom_core* core, dom_package_id id)
{
    uint32_t i;

    if (!core) {
        return false;
    }

    for (i = 0; i < core->package_count; ++i) {
        if (core->packages[i].id == id) {
            for (; i + 1 < core->package_count; ++i) {
                core->packages[i] = core->packages[i + 1];
            }
            core->package_count -= 1;
            return true;
        }
    }

    return false;
}
