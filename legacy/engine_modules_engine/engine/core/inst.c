/*
FILE: source/domino/core/inst.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/inst
RESPONSIBILITY: Implements `inst`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "core_internal.h"

#define DOM_INST_DESCRIPTOR_NAME "instance.ini"

static dom_instance_record* dom_find_instance(dom_core* core, dom_instance_id id);
static dom_package_id       dom_inst_find_package_id(dom_core* core, const char* name);
static const char*          dom_inst_package_name(dom_core* core, dom_package_id id);
static void                 dom_trim(char* s);
static bool                 dom_inst_parse_descriptor(dom_core* core,
                                                      const char* path,
                                                      dom_instance_record* out_rec);
static bool                 dom_inst_write_descriptor(dom_core* core,
                                                      const dom_instance_record* rec);
static uint32_t             dom_inst_collect_dirs(const char* root,
                                                  char names[][260],
                                                  uint32_t max_names);
static void                 dom_inst_sort_names(char names[][260], uint32_t count);
static bool                 dom_inst_append_token(char* dst, size_t cap, const char* token, char sep);
static void                 dom_inst_dirname(const char* path, char* out, size_t cap);

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

static dom_package_id dom_inst_find_package_id(dom_core* core, const char* name)
{
    uint32_t i;

    if (!core || !name) {
        return 0;
    }

    for (i = 0; i < core->package_count; ++i) {
        if (strcmp(core->packages[i].info.name, name) == 0) {
            return core->packages[i].info.id;
        }
    }

    return 0;
}

static const char* dom_inst_package_name(dom_core* core, dom_package_id id)
{
    uint32_t i;

    if (!core || id == 0u) {
        return NULL;
    }

    for (i = 0; i < core->package_count; ++i) {
        if (core->packages[i].info.id == id) {
            return core->packages[i].info.name;
        }
    }
    return NULL;
}

static void dom_trim(char* s)
{
    size_t len;
    size_t start;

    if (!s) {
        return;
    }

    len = strlen(s);
    start = 0u;
    while (start < len && (s[start] == ' ' || s[start] == '\t' || s[start] == '\r' || s[start] == '\n')) {
        start += 1u;
    }
    if (start > 0u) {
        memmove(s, s + start, len - start + 1u);
        len -= start;
    }
    while (len > 0u && (s[len - 1u] == ' ' || s[len - 1u] == '\t' || s[len - 1u] == '\r' || s[len - 1u] == '\n')) {
        s[len - 1u] = '\0';
        len -= 1u;
    }
}

static void dom_inst_sort_names(char names[][260], uint32_t count)
{
    uint32_t i;
    uint32_t j;

    for (i = 0; i + 1u < count; ++i) {
        for (j = i + 1u; j < count; ++j) {
            if (strcmp(names[j], names[i]) < 0) {
                char tmp[260];
                dom_copy_string(tmp, sizeof(tmp), names[i]);
                dom_copy_string(names[i], 260u, names[j]);
                dom_copy_string(names[j], 260u, tmp);
            }
        }
    }
}

static uint32_t dom_inst_collect_dirs(const char* root, char names[][260], uint32_t max_names)
{
    dsys_dir_iter* it;
    dsys_dir_entry ent;
    uint32_t       count;

    if (!root || max_names == 0u) {
        return 0u;
    }

    it = dsys_dir_open(root);
    if (!it) {
        return 0u;
    }

    count = 0u;
    while (dsys_dir_next(it, &ent)) {
        if (!ent.is_dir) {
            continue;
        }
        if (ent.name[0] == '.' && (ent.name[1] == '\0' ||
                                   (ent.name[1] == '.' && ent.name[2] == '\0'))) {
            continue;
        }
        if (count >= max_names) {
            break;
        }
        dom_copy_string(names[count], 260u, ent.name);
        count += 1u;
    }

    dsys_dir_close(it);
    dom_inst_sort_names(names, count);
    return count;
}

static bool dom_inst_append_token(char* dst, size_t cap, const char* token, char sep)
{
    size_t len;
    size_t i;

    if (!dst || !token || cap == 0u) {
        return false;
    }

    len = strlen(dst);
    if (token[0] == '\0') {
        return true;
    }
    if (len > 0u) {
        if (len + 1u >= cap) {
            return false;
        }
        dst[len] = sep;
        len += 1u;
        dst[len] = '\0';
    }
    for (i = 0u; token[i] != '\0'; ++i) {
        if (len + 1u >= cap) {
            dst[len] = '\0';
            return false;
        }
        dst[len] = token[i];
        len += 1u;
    }
    dst[len] = '\0';
    return true;
}

static void dom_inst_dirname(const char* path, char* out, size_t cap)
{
    const char* last;
    size_t      len;

    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (!path) {
        return;
    }

    last = strrchr(path, '/');
    if (!last) {
        last = strrchr(path, '\\');
    }
    if (last) {
        len = (size_t)(last - path);
        if (len >= cap) {
            len = cap - 1u;
        }
        memcpy(out, path, len);
        out[len] = '\0';
    } else {
        dom_copy_string(out, cap, path);
    }
}

static bool dom_inst_write_line(void* fh, const char* text)
{
    size_t len;

    len = strlen(text);
    return dsys_file_write(fh, text, len) == len;
}

static bool dom_inst_write_descriptor(dom_core* core, const dom_instance_record* rec)
{
    void* fh;
    char  line[512];
    char  pkg_line[512];
    uint32_t i;
    const char* pkg_name;

    if (!core || !rec) {
        return false;
    }

    if (!dom_fs_mkdirs(rec->info.path)) {
        return false;
    }

    pkg_line[0] = '\0';
    for (i = 0u; i < rec->info.pkg_count; ++i) {
        pkg_name = dom_inst_package_name(core, rec->info.pkgs[i]);
        if (pkg_name) {
            if (!dom_inst_append_token(pkg_line, sizeof(pkg_line), pkg_name, ',')) {
                return false;
            }
        }
    }

    fh = dsys_file_open(rec->info.descriptor_path, "wb");
    if (!fh) {
        return false;
    }

    sprintf(line, "id=%u\n", (unsigned int)rec->info.id);
    if (!dom_inst_write_line(fh, line)) {
        dsys_file_close(fh);
        return false;
    }
    sprintf(line, "name=%s\n", rec->info.name);
    if (!dom_inst_write_line(fh, line)) {
        dsys_file_close(fh);
        return false;
    }
    sprintf(line, "path=%s\n", rec->info.path);
    if (!dom_inst_write_line(fh, line)) {
        dsys_file_close(fh);
        return false;
    }
    sprintf(line, "flags=%u\n", (unsigned int)rec->info.flags);
    if (!dom_inst_write_line(fh, line)) {
        dsys_file_close(fh);
        return false;
    }
    sprintf(line, "packages=%s\n", pkg_line);
    if (!dom_inst_write_line(fh, line)) {
        dsys_file_close(fh);
        return false;
    }
    sprintf(line, "saves_path=%s\n", rec->info.saves_path);
    if (!dom_inst_write_line(fh, line)) {
        dsys_file_close(fh);
        return false;
    }
    sprintf(line, "config_path=%s\n", rec->info.config_path);
    if (!dom_inst_write_line(fh, line)) {
        dsys_file_close(fh);
        return false;
    }
    sprintf(line, "logs_path=%s\n", rec->info.logs_path);
    if (!dom_inst_write_line(fh, line)) {
        dsys_file_close(fh);
        return false;
    }

    dsys_file_close(fh);
    return true;
}

static bool dom_inst_parse_descriptor(dom_core* core,
                                      const char* path,
                                      dom_instance_record* out_rec)
{
    char   text[2048];
    size_t text_len;
    char*  line;
    char*  next;
    char   pkg_names[DOM_MAX_INSTANCE_PACKAGES][64];
    uint32_t pkg_name_count;

    if (!core || !path || !out_rec) {
        return false;
    }

    if (!dom_fs_read_text(path, text, sizeof(text), &text_len)) {
        return false;
    }
    (void)text_len;

    memset(out_rec, 0, sizeof(*out_rec));
    out_rec->info.struct_size = sizeof(dom_instance_info);
    out_rec->info.struct_version = 1;
    dom_copy_string(out_rec->info.descriptor_path, sizeof(out_rec->info.descriptor_path), path);

    pkg_name_count = 0u;
    line = text;
    while (line && *line) {
        char* eq;
        char* key;
        char* val;

        next = strchr(line, '\n');
        if (next) {
            *next = '\0';
            next += 1;
        }

        dom_trim(line);
        if (line[0] == '\0' || line[0] == '#' || line[0] == ';') {
            line = next;
            continue;
        }

        eq = strchr(line, '=');
        if (!eq) {
            line = next;
            continue;
        }
        *eq = '\0';
        key = line;
        val = eq + 1;
        dom_trim(key);
        dom_trim(val);

        if (strcmp(key, "id") == 0) {
            out_rec->info.id = (dom_instance_id)strtoul(val, NULL, 10);
        } else if (strcmp(key, "name") == 0) {
            dom_copy_string(out_rec->info.name, sizeof(out_rec->info.name), val);
        } else if (strcmp(key, "path") == 0) {
            dom_copy_string(out_rec->info.path, sizeof(out_rec->info.path), val);
        } else if (strcmp(key, "flags") == 0) {
            out_rec->info.flags = (uint32_t)strtoul(val, NULL, 10);
        } else if (strcmp(key, "packages") == 0) {
            char* dep;
            char* dep_next;
            dep = val;
            while (dep && *dep && pkg_name_count < DOM_MAX_INSTANCE_PACKAGES) {
                dep_next = strchr(dep, ',');
                if (dep_next) {
                    *dep_next = '\0';
                    dep_next += 1;
                }
                dom_trim(dep);
                if (dep[0] != '\0') {
                    dom_copy_string(pkg_names[pkg_name_count], sizeof(pkg_names[pkg_name_count]), dep);
                    pkg_name_count += 1u;
                }
                dep = dep_next;
            }
        } else if (strcmp(key, "saves_path") == 0) {
            dom_copy_string(out_rec->info.saves_path, sizeof(out_rec->info.saves_path), val);
        } else if (strcmp(key, "config_path") == 0) {
            dom_copy_string(out_rec->info.config_path, sizeof(out_rec->info.config_path), val);
        } else if (strcmp(key, "logs_path") == 0) {
            dom_copy_string(out_rec->info.logs_path, sizeof(out_rec->info.logs_path), val);
        }

        line = next;
    }

    if (out_rec->info.path[0] == '\0') {
        dom_inst_dirname(path, out_rec->info.path, sizeof(out_rec->info.path));
    }
    if (out_rec->info.name[0] == '\0') {
        dom_path_last_segment(out_rec->info.path, out_rec->info.name, sizeof(out_rec->info.name));
    }
    if (out_rec->info.saves_path[0] == '\0') {
        dom_path_join(out_rec->info.saves_path, sizeof(out_rec->info.saves_path), out_rec->info.path, "saves");
    }
    if (out_rec->info.config_path[0] == '\0') {
        dom_path_join(out_rec->info.config_path, sizeof(out_rec->info.config_path), out_rec->info.path, "config");
    }
    if (out_rec->info.logs_path[0] == '\0') {
        dom_path_join(out_rec->info.logs_path, sizeof(out_rec->info.logs_path), out_rec->info.path, "logs");
    }

    out_rec->info.pkg_count = 0u;
    if (pkg_name_count > 0u) {
        uint32_t i;
        for (i = 0u; i < pkg_name_count && out_rec->info.pkg_count < DOM_MAX_INSTANCE_PACKAGES; ++i) {
            dom_package_id pid;
            pid = dom_inst_find_package_id(core, pkg_names[i]);
            if (pid != 0u) {
                out_rec->info.pkgs[out_rec->info.pkg_count] = pid;
                out_rec->info.pkg_count += 1u;
            }
        }
    }

    return true;
}

void dom_core__scan_instances(dom_core* core)
{
    char user_root[260];
    char inst_root[260];
    uint32_t i;

    if (!core) {
        return;
    }

    core->instance_count = 0;
    core->next_instance_id = 1;

    if (!dsys_get_path(DSYS_PATH_USER_DATA, user_root, sizeof(user_root))) {
        dom_copy_string(user_root, sizeof(user_root), ".");
    }

    if (!dom_path_join(inst_root, sizeof(inst_root), user_root, "instances") ||
        !dom_fs_dir_exists(inst_root)) {
        return;
    }

    {
        char inst_names[DOM_MAX_INSTANCES][260];
        uint32_t inst_count;

        inst_count = dom_inst_collect_dirs(inst_root, inst_names, DOM_MAX_INSTANCES);
        for (i = 0u; i < inst_count && core->instance_count < DOM_MAX_INSTANCES; ++i) {
            char descriptor_path[260];
            dom_instance_record rec;

            if (!dom_path_join(descriptor_path, sizeof(descriptor_path), inst_root, inst_names[i]) ||
                !dom_path_join(descriptor_path, sizeof(descriptor_path), descriptor_path, DOM_INST_DESCRIPTOR_NAME)) {
                continue;
            }
            if (!dom_fs_file_exists(descriptor_path)) {
                continue;
            }
            if (!dom_inst_parse_descriptor(core, descriptor_path, &rec)) {
                continue;
            }

            if (rec.info.id == 0u) {
                rec.info.id = core->next_instance_id++;
            } else if (rec.info.id >= core->next_instance_id) {
                core->next_instance_id = rec.info.id + 1u;
            }

            core->instances[core->instance_count] = rec;
            core->instance_count += 1u;
        }
    }
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
    dom_instance_record rec;
    dom_instance_record* slot;
    char user_root[260];
    char inst_root[260];
    char descriptor_path[260];
    char saves_path[260];
    char config_path[260];
    char logs_path[260];
    uint32_t i;

    if (!core || !desc) {
        return 0;
    }

    if (desc->struct_size != sizeof(dom_instance_info) ||
        desc->struct_version != 1) {
        return 0;
    }

    if (core->instance_count >= DOM_MAX_INSTANCES) {
        return 0;
    }

    if (!dsys_get_path(DSYS_PATH_USER_DATA, user_root, sizeof(user_root))) {
        dom_copy_string(user_root, sizeof(user_root), ".");
    }

    if (desc->path[0] != '\0') {
        dom_copy_string(inst_root, sizeof(inst_root), desc->path);
    } else {
        char inst_name[64];
        if (desc->name[0] != '\0') {
            dom_copy_string(inst_name, sizeof(inst_name), desc->name);
        } else {
            dom_copy_string(inst_name, sizeof(inst_name), "instance");
        }
        if (!dom_path_join(inst_root, sizeof(inst_root), user_root, "instances") ||
            !dom_path_join(inst_root, sizeof(inst_root), inst_root, inst_name)) {
            return 0;
        }
    }

    if (!dom_path_join(descriptor_path, sizeof(descriptor_path), inst_root, DOM_INST_DESCRIPTOR_NAME) ||
        !dom_path_join(saves_path, sizeof(saves_path), inst_root, "saves") ||
        !dom_path_join(config_path, sizeof(config_path), inst_root, "config") ||
        !dom_path_join(logs_path, sizeof(logs_path), inst_root, "logs")) {
        return 0;
    }

    if (!dom_fs_mkdirs(inst_root) ||
        !dom_fs_mkdirs(saves_path) ||
        !dom_fs_mkdirs(config_path) ||
        !dom_fs_mkdirs(logs_path)) {
        return 0;
    }

    memset(&rec, 0, sizeof(rec));
    rec.info.struct_size = sizeof(dom_instance_info);
    rec.info.struct_version = 1;
    rec.info.id = core->next_instance_id++;
    dom_copy_string(rec.info.name, sizeof(rec.info.name), desc->name[0] ? desc->name : "instance");
    dom_copy_string(rec.info.path, sizeof(rec.info.path), inst_root);
    dom_copy_string(rec.info.descriptor_path, sizeof(rec.info.descriptor_path), descriptor_path);
    dom_copy_string(rec.info.saves_path, sizeof(rec.info.saves_path), saves_path);
    dom_copy_string(rec.info.config_path, sizeof(rec.info.config_path), config_path);
    dom_copy_string(rec.info.logs_path, sizeof(rec.info.logs_path), logs_path);
    rec.info.flags = desc->flags;
    rec.info.pkg_count = 0u;
    for (i = 0u; i < desc->pkg_count && rec.info.pkg_count < DOM_MAX_INSTANCE_PACKAGES; ++i) {
        if (dom_inst_package_name(core, desc->pkgs[i])) {
            rec.info.pkgs[rec.info.pkg_count] = desc->pkgs[i];
            rec.info.pkg_count += 1u;
        }
    }

    if (!dom_inst_write_descriptor(core, &rec)) {
        return 0;
    }

    slot = &core->instances[core->instance_count];
    *slot = rec;
    core->instance_count += 1u;
    return rec.info.id;
}

bool dom_inst_update(dom_core* core, const dom_instance_info* desc)
{
    dom_instance_record* rec;
    int                 path_changed;
    uint32_t i;

    if (!core || !desc) {
        return false;
    }

    if (desc->struct_size != sizeof(dom_instance_info) ||
        desc->struct_version != 1) {
        return false;
    }

    rec = dom_find_instance(core, desc->id);
    if (!rec) {
        return false;
    }

    path_changed = 0;
    rec->info.flags = desc->flags;
    if (desc->name[0] != '\0') {
        dom_copy_string(rec->info.name, sizeof(rec->info.name), desc->name);
    }
    if (desc->path[0] != '\0') {
        dom_copy_string(rec->info.path, sizeof(rec->info.path), desc->path);
        path_changed = 1;
    }
    if (desc->saves_path[0] != '\0') {
        dom_copy_string(rec->info.saves_path, sizeof(rec->info.saves_path), desc->saves_path);
    } else if (path_changed) {
        dom_path_join(rec->info.saves_path, sizeof(rec->info.saves_path), rec->info.path, "saves");
    }
    if (desc->config_path[0] != '\0') {
        dom_copy_string(rec->info.config_path, sizeof(rec->info.config_path), desc->config_path);
    } else if (path_changed) {
        dom_path_join(rec->info.config_path, sizeof(rec->info.config_path), rec->info.path, "config");
    }
    if (desc->logs_path[0] != '\0') {
        dom_copy_string(rec->info.logs_path, sizeof(rec->info.logs_path), desc->logs_path);
    } else if (path_changed) {
        dom_path_join(rec->info.logs_path, sizeof(rec->info.logs_path), rec->info.path, "logs");
    }

    rec->info.pkg_count = 0u;
    for (i = 0u; i < desc->pkg_count && rec->info.pkg_count < DOM_MAX_INSTANCE_PACKAGES; ++i) {
        if (dom_inst_package_name(core, desc->pkgs[i])) {
            rec->info.pkgs[rec->info.pkg_count] = desc->pkgs[i];
            rec->info.pkg_count += 1u;
        }
    }

    if (path_changed) {
        dom_path_join(rec->info.descriptor_path,
                      sizeof(rec->info.descriptor_path),
                      rec->info.path,
                      DOM_INST_DESCRIPTOR_NAME);
    }

    (void)dom_fs_mkdirs(rec->info.path);
    (void)dom_fs_mkdirs(rec->info.saves_path);
    (void)dom_fs_mkdirs(rec->info.config_path);
    (void)dom_fs_mkdirs(rec->info.logs_path);

    return dom_inst_write_descriptor(core, rec);
}

bool dom_inst_delete(dom_core* core, dom_instance_id id)
{
    dom_instance_record* rec;
    uint32_t            idx;

    if (!core) {
        return false;
    }

    rec = dom_find_instance(core, id);
    if (!rec) {
        return false;
    }
    idx = (uint32_t)(rec - core->instances);

    if (!dom_fs_remove_tree(rec->info.path)) {
        return false;
    }

    for (; idx + 1u < core->instance_count; ++idx) {
        core->instances[idx] = core->instances[idx + 1u];
    }
    core->instance_count -= 1u;
    return true;
}
