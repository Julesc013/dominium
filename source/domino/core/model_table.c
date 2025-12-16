/*
FILE: source/domino/core/model_table.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/model_table
RESPONSIBILITY: Implements `model_table`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>
#include <stdio.h>
#include "core_internal.h"

static const dom_table_def* dom_table_find(dom_core* core, const char* id);
static uint32_t             dom_table_row_count(dom_core* core, const char* id);
static uint32_t             dom_table_mod_count(dom_core* core);
static dom_package_record*  dom_table_mod_at(dom_core* core, uint32_t index);
static const char*          dom_table_pkg_kind_string(dom_package_kind kind);

void dom_table__register(dom_core* core,
                         const char* id,
                         const char** col_ids,
                         uint32_t col_count)
{
    dom_table_def* def;
    uint32_t       i;

    if (!core || !id || !col_ids || col_count == 0u) {
        return;
    }
    if (core->table_count >= DOM_MAX_TABLES) {
        return;
    }
    if (col_count > DOM_MAX_TABLE_COLS) {
        col_count = DOM_MAX_TABLE_COLS;
    }

    def = &core->tables[core->table_count];
    def->id = id;
    def->col_count = col_count;
    for (i = 0u; i < col_count; ++i) {
        def->col_ids[i] = col_ids[i];
    }
    core->table_count += 1u;
}

static const dom_table_def* dom_table_find(dom_core* core, const char* id)
{
    uint32_t i;

    if (!core || !id) {
        return NULL;
    }

    for (i = 0u; i < core->table_count; ++i) {
        if (strcmp(core->tables[i].id, id) == 0) {
            return &core->tables[i];
        }
    }
    return NULL;
}

static uint32_t dom_table_mod_count(dom_core* core)
{
    uint32_t i;
    uint32_t count;

    if (!core) {
        return 0u;
    }

    count = 0u;
    for (i = 0u; i < core->package_count; ++i) {
        dom_package_kind kind;
        kind = core->packages[i].info.kind;
        if (kind == DOM_PKG_KIND_MOD || kind == DOM_PKG_KIND_CONTENT) {
            count += 1u;
        }
    }
    return count;
}

static uint32_t dom_table_row_count(dom_core* core, const char* id)
{
    if (!core || !id) {
        return 0u;
    }

    if (strcmp(id, "packages_table") == 0) {
        return core->package_count;
    }
    if (strcmp(id, "instances_table") == 0) {
        return core->instance_count;
    }
    if (strcmp(id, "mods_table") == 0) {
        return dom_table_mod_count(core);
    }
    return 0u;
}

static dom_package_record* dom_table_mod_at(dom_core* core, uint32_t index)
{
    uint32_t i;
    uint32_t count;

    if (!core) {
        return NULL;
    }

    count = 0u;
    for (i = 0u; i < core->package_count; ++i) {
        dom_package_kind kind;
        kind = core->packages[i].info.kind;
        if (kind != DOM_PKG_KIND_MOD && kind != DOM_PKG_KIND_CONTENT) {
            continue;
        }
        if (count == index) {
            return &core->packages[i];
        }
        count += 1u;
    }
    return NULL;
}

static const char* dom_table_pkg_kind_string(dom_package_kind kind)
{
    switch (kind) {
    case DOM_PKG_KIND_MOD:     return "mod";
    case DOM_PKG_KIND_CONTENT: return "content";
    case DOM_PKG_KIND_PRODUCT: return "product";
    case DOM_PKG_KIND_TOOL:    return "tool";
    case DOM_PKG_KIND_PACK:    return "pack";
    default:                   break;
    }
    return "unknown";
}

bool dom_table_get_meta(dom_core* core, const char* table_id, dom_table_meta* meta)
{
    const dom_table_def* def;

    if (!core || !meta || !table_id) {
        return false;
    }

    def = dom_table_find(core, table_id);
    if (!def) {
        return false;
    }

    meta->struct_size = sizeof(dom_table_meta);
    meta->struct_version = 1;
    meta->id = def->id;
    meta->row_count = dom_table_row_count(core, def->id);
    meta->col_count = def->col_count;
    meta->col_ids = def->col_ids;
    return true;
}

bool dom_table_get_cell(dom_core* core,
                        const char* table_id,
                        uint32_t row,
                        uint32_t col,
                        char* buf,
                        size_t buf_size)
{
    const dom_table_def* def;
    uint32_t             row_count;
    char                 tmp[64];

    if (!core || !table_id || !buf || buf_size == 0u) {
        return false;
    }

    buf[0] = '\0';

    def = dom_table_find(core, table_id);
    if (!def) {
        return false;
    }

    if (col >= def->col_count) {
        return false;
    }

    row_count = dom_table_row_count(core, def->id);
    if (row >= row_count) {
        return false;
    }

    if (strcmp(def->id, "packages_table") == 0) {
        dom_package_record* rec;
        dom_package_info*   info;

        rec = &core->packages[row];
        info = &rec->info;

        switch (col) {
        case 0:
            sprintf(tmp, "%u", (unsigned int)info->id);
            dom_copy_string(buf, buf_size, tmp);
            return true;
        case 1:
            dom_copy_string(buf, buf_size, info->name);
            return true;
        case 2:
            dom_copy_string(buf, buf_size, info->version);
            return true;
        case 3:
            dom_copy_string(buf, buf_size, dom_table_pkg_kind_string(info->kind));
            return true;
        case 4:
            dom_copy_string(buf, buf_size, info->install_path);
            return true;
        default:
            break;
        }
    } else if (strcmp(def->id, "instances_table") == 0) {
        dom_instance_record* rec;
        dom_instance_info*   info;

        rec = &core->instances[row];
        info = &rec->info;

        switch (col) {
        case 0:
            sprintf(tmp, "%u", (unsigned int)info->id);
            dom_copy_string(buf, buf_size, tmp);
            return true;
        case 1:
            dom_copy_string(buf, buf_size, info->name);
            return true;
        case 2:
            dom_copy_string(buf, buf_size, info->path);
            return true;
        case 3:
            sprintf(tmp, "0x%X", (unsigned int)info->flags);
            dom_copy_string(buf, buf_size, tmp);
            return true;
        case 4:
            sprintf(tmp, "%u", (unsigned int)info->pkg_count);
            dom_copy_string(buf, buf_size, tmp);
            return true;
        case 5:
            dom_copy_string(buf, buf_size, "never");
            return true;
        default:
            break;
        }
    } else if (strcmp(def->id, "mods_table") == 0) {
        dom_package_record* rec;
        dom_package_info*   info;

        rec = dom_table_mod_at(core, row);
        if (!rec) {
            return false;
        }
        info = &rec->info;

        switch (col) {
        case 0:
            sprintf(tmp, "%u", (unsigned int)info->id);
            dom_copy_string(buf, buf_size, tmp);
            return true;
        case 1:
            dom_copy_string(buf, buf_size, info->name);
            return true;
        case 2:
            dom_copy_string(buf, buf_size, info->version);
            return true;
        case 3:
            dom_copy_string(buf, buf_size, dom_table_pkg_kind_string(info->kind));
            return true;
        case 4:
            dom_copy_string(buf, buf_size, info->install_path);
            return true;
        default:
            break;
        }
    }

    return false;
}
