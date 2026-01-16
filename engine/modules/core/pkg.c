/*
FILE: source/domino/core/pkg.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/pkg
RESPONSIBILITY: Implements `pkg`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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
#include "core_internal.h"

#define DOM_PKG_DEFAULT_GAME_VERSION "dev"
#define DOM_PKG_MANIFEST_NAME "manifest.ini"

static dom_package_record* dom_pkg_find(dom_core* core, dom_package_id id);
static dom_package_record* dom_pkg_find_by_name(dom_core* core, const char* name);
static dom_package_kind    dom_pkg_kind_from_string(const char* s);
static void                dom_pkg_resolve_dependencies(dom_core* core);
static bool                dom_pkg_parse_manifest(const char* manifest_path, dom_package_record* out_rec);
static bool                dom_pkg_load_dir(dom_core* core,
                                            const char* root,
                                            int is_official,
                                            const char* default_author);
static uint32_t            dom_pkg_collect_dirs(const char* root,
                                                char names[][260],
                                                uint32_t max_names);
static void                dom_pkg_sort_names(char names[][260], uint32_t count);

static dom_package_kind dom_pkg_kind_from_string(const char* s)
{
    if (!s) {
        return DOM_PKG_KIND_UNKNOWN;
    }
    if (strcmp(s, "mod") == 0) {
        return DOM_PKG_KIND_MOD;
    }
    if (strcmp(s, "content") == 0) {
        return DOM_PKG_KIND_CONTENT;
    }
    if (strcmp(s, "product") == 0) {
        return DOM_PKG_KIND_PRODUCT;
    }
    if (strcmp(s, "tool") == 0) {
        return DOM_PKG_KIND_TOOL;
    }
    if (strcmp(s, "pack") == 0) {
        return DOM_PKG_KIND_PACK;
    }
    return DOM_PKG_KIND_UNKNOWN;
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

static bool dom_pkg_parse_manifest(const char* manifest_path, dom_package_record* out_rec)
{
    char   text[2048];
    size_t text_len;
    char*  line;
    char*  next;

    if (!manifest_path || !out_rec) {
        return false;
    }

    if (!dom_fs_read_text(manifest_path, text, sizeof(text), &text_len)) {
        return false;
    }
    (void)text_len;

    memset(out_rec, 0, sizeof(*out_rec));
    out_rec->info.struct_size = sizeof(dom_package_info);
    out_rec->info.struct_version = 1;
    out_rec->info.kind = DOM_PKG_KIND_UNKNOWN;
    dom_copy_string(out_rec->info.version, sizeof(out_rec->info.version), "0.0.0");
    out_rec->dep_name_count = 0;

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
            dom_copy_string(out_rec->info.name, sizeof(out_rec->info.name), val);
        } else if (strcmp(key, "kind") == 0) {
            out_rec->info.kind = dom_pkg_kind_from_string(val);
        } else if (strcmp(key, "version") == 0) {
            dom_copy_string(out_rec->info.version, sizeof(out_rec->info.version), val);
        } else if (strcmp(key, "author") == 0) {
            dom_copy_string(out_rec->info.author, sizeof(out_rec->info.author), val);
        } else if (strcmp(key, "deps") == 0) {
            char* dep;
            char* dep_next;
            dep = val;
            while (dep && *dep && out_rec->dep_name_count < DOM_MAX_PACKAGE_DEPS) {
                dep_next = strchr(dep, ',');
                if (dep_next) {
                    *dep_next = '\0';
                    dep_next += 1;
                }
                dom_trim(dep);
                if (dep[0] != '\0') {
                    dom_copy_string(out_rec->dep_names[out_rec->dep_name_count],
                                    sizeof(out_rec->dep_names[out_rec->dep_name_count]),
                                    dep);
                    out_rec->dep_name_count += 1;
                }
                dep = dep_next;
            }
        } else if (strcmp(key, "game_version_min") == 0) {
            dom_copy_string(out_rec->info.game_version_min, sizeof(out_rec->info.game_version_min), val);
        } else if (strcmp(key, "game_version_max") == 0) {
            dom_copy_string(out_rec->info.game_version_max, sizeof(out_rec->info.game_version_max), val);
        }

        line = next;
    }

    if (out_rec->info.name[0] == '\0') {
        dom_path_last_segment(manifest_path, out_rec->info.name, sizeof(out_rec->info.name));
    }
    if (out_rec->info.version[0] == '\0') {
        dom_copy_string(out_rec->info.version, sizeof(out_rec->info.version), "0.0.0");
    }

    return true;
}

static dom_package_record* dom_pkg_find(dom_core* core, dom_package_id id)
{
    uint32_t i;

    if (!core) {
        return NULL;
    }
    for (i = 0; i < core->package_count; ++i) {
        if (core->packages[i].info.id == id) {
            return &core->packages[i];
        }
    }
    return NULL;
}

static dom_package_record* dom_pkg_find_by_name(dom_core* core, const char* name)
{
    uint32_t i;

    if (!core || !name) {
        return NULL;
    }
    for (i = 0; i < core->package_count; ++i) {
        if (strcmp(core->packages[i].info.name, name) == 0) {
            return &core->packages[i];
        }
    }
    return NULL;
}

static void dom_pkg_resolve_dependencies(dom_core* core)
{
    uint32_t i;
    uint32_t j;

    if (!core) {
        return;
    }

    for (i = 0; i < core->package_count; ++i) {
        core->packages[i].info.dep_count = 0;
    }

    for (i = 0; i < core->package_count; ++i) {
        dom_package_record* rec;

        rec = &core->packages[i];
        rec->info.dep_count = 0;
        for (j = 0; j < rec->dep_name_count && rec->info.dep_count < DOM_MAX_PACKAGE_DEPS; ++j) {
            dom_package_record* dep_rec;
            dep_rec = dom_pkg_find_by_name(core, rec->dep_names[j]);
            if (dep_rec) {
                rec->info.deps[rec->info.dep_count] = dep_rec->info.id;
                rec->info.dep_count += 1;
            }
        }
    }
}

static void dom_pkg_sort_names(char names[][260], uint32_t count)
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

static uint32_t dom_pkg_collect_dirs(const char* root, char names[][260], uint32_t max_names)
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
    dom_pkg_sort_names(names, count);
    return count;
}

static bool dom_pkg_load_dir(dom_core* core,
                             const char* root,
                             int is_official,
                             const char* default_author)
{
    char manifest_path[260];
    char content_root[260];
    dom_package_record rec;
    dom_package_record* slot;

    if (!core || !root) {
        return false;
    }
    if (core->package_count >= DOM_MAX_PACKAGES) {
        return false;
    }

    if (!dom_path_join(manifest_path, sizeof(manifest_path), root, DOM_PKG_MANIFEST_NAME)) {
        return false;
    }
    if (!dom_fs_file_exists(manifest_path)) {
        return false;
    }

    if (!dom_pkg_parse_manifest(manifest_path, &rec)) {
        return false;
    }

    if (rec.info.author[0] == '\0' && default_author) {
        dom_copy_string(rec.info.author, sizeof(rec.info.author), default_author);
    }

    if (!dom_path_join(content_root, sizeof(content_root), root, "content")) {
        return false;
    }

    rec.info.id = core->next_package_id++;
    dom_copy_string(rec.info.install_path, sizeof(rec.info.install_path), root);
    dom_copy_string(rec.info.manifest_path, sizeof(rec.info.manifest_path), manifest_path);
    dom_copy_string(rec.info.content_root, sizeof(rec.info.content_root), content_root);
    rec.is_official = is_official;

    slot = &core->packages[core->package_count];
    *slot = rec;
    core->package_count += 1;
    return true;
}

void dom_core__scan_packages(dom_core* core)
{
    char app_root[260];
    char user_root[260];
    char official_root[260];
    char mods_root[260];
    uint32_t i;
    uint32_t j;

    if (!core) {
        return;
    }

    core->package_count = 0;
    core->next_package_id = 1;

    if (!dsys_get_path(DSYS_PATH_APP_ROOT, app_root, sizeof(app_root))) {
        dom_copy_string(app_root, sizeof(app_root), ".");
    }
    if (!dsys_get_path(DSYS_PATH_USER_DATA, user_root, sizeof(user_root))) {
        dom_copy_string(user_root, sizeof(user_root), ".");
    }

    /* official packages */
    if (dom_path_join(official_root, sizeof(official_root), app_root, "data") &&
        dom_path_join(official_root, sizeof(official_root), official_root, "versions") &&
        dom_path_join(official_root, sizeof(official_root), official_root, DOM_PKG_DEFAULT_GAME_VERSION) &&
        dom_fs_dir_exists(official_root)) {
        char      pkg_names[DOM_MAX_PACKAGES][260];
        uint32_t  pkg_count;
        char      pkg_path[260];

        pkg_count = dom_pkg_collect_dirs(official_root, pkg_names, DOM_MAX_PACKAGES);
        for (i = 0u; i < pkg_count && core->package_count < DOM_MAX_PACKAGES; ++i) {
            if (dom_path_join(pkg_path, sizeof(pkg_path), official_root, pkg_names[i])) {
                dom_pkg_load_dir(core, pkg_path, 1, NULL);
            }
        }
    }

    /* user mods (optional author level) */
    if (dom_path_join(mods_root, sizeof(mods_root), user_root, "mods") &&
        dom_fs_dir_exists(mods_root)) {
        char author_names[DOM_MAX_PACKAGES][260];
        uint32_t author_count;

        author_count = dom_pkg_collect_dirs(mods_root, author_names, DOM_MAX_PACKAGES);
        for (i = 0u; i < author_count && core->package_count < DOM_MAX_PACKAGES; ++i) {
            char author_path[260];
            char manifest_path[260];

            if (!dom_path_join(author_path, sizeof(author_path), mods_root, author_names[i])) {
                continue;
            }
            if (!dom_path_join(manifest_path, sizeof(manifest_path), author_path, DOM_PKG_MANIFEST_NAME) ||
                !dom_fs_file_exists(manifest_path)) {
                char pkg_names[DOM_MAX_PACKAGES][260];
                uint32_t pkg_count;
                char pkg_path[260];

                pkg_count = dom_pkg_collect_dirs(author_path,
                                                 pkg_names,
                                                 DOM_MAX_PACKAGES - core->package_count);
                for (j = 0u; j < pkg_count && core->package_count < DOM_MAX_PACKAGES; ++j) {
                    if (dom_path_join(pkg_path, sizeof(pkg_path), author_path, pkg_names[j])) {
                        dom_pkg_load_dir(core, pkg_path, 0, author_names[i]);
                    }
                }
            } else {
                dom_pkg_load_dir(core, author_path, 0, author_names[i]);
            }
        }
    }

    dom_pkg_resolve_dependencies(core);
    if (core->package_count > 0u) {
        core->next_package_id = core->packages[core->package_count - 1u].info.id + 1u;
    } else {
        core->next_package_id = 1;
    }
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
        out[i] = core->packages[i].info;
    }

    return count;
}

bool dom_pkg_get(dom_core* core, dom_package_id id, dom_package_info* out)
{
    dom_package_record* rec;

    if (!core || !out) {
        return false;
    }

    rec = dom_pkg_find(core, id);
    if (!rec) {
        return false;
    }

    *out = rec->info;
    return true;
}

bool dom_pkg_install(dom_core* core, const char* source_path, dom_package_id* out_id)
{
    char                manifest_path[260];
    char                user_root[260];
    char                mods_root[260];
    char                dest_root[260];
    char                dest_content[260];
    dom_package_record  temp;
    const char*         author_ptr;

    if (!core || !source_path) {
        return false;
    }

    if (core->package_count >= DOM_MAX_PACKAGES) {
        return false;
    }

    if (!dom_path_join(manifest_path, sizeof(manifest_path), source_path, DOM_PKG_MANIFEST_NAME)) {
        return false;
    }
    if (!dom_fs_file_exists(manifest_path)) {
        return false;
    }
    if (!dom_pkg_parse_manifest(manifest_path, &temp)) {
        return false;
    }

    if (dom_pkg_find_by_name(core, temp.info.name)) {
        return false;
    }

    if (!dsys_get_path(DSYS_PATH_USER_DATA, user_root, sizeof(user_root))) {
        dom_copy_string(user_root, sizeof(user_root), ".");
    }
    if (!dom_path_join(mods_root, sizeof(mods_root), user_root, "mods")) {
        return false;
    }

    author_ptr = temp.info.author[0] != '\0' ? temp.info.author : NULL;
    if (author_ptr) {
        if (!dom_path_join(dest_root, sizeof(dest_root), mods_root, author_ptr) ||
            !dom_path_join(dest_root, sizeof(dest_root), dest_root, temp.info.name)) {
            return false;
        }
    } else {
        if (!dom_path_join(dest_root, sizeof(dest_root), mods_root, temp.info.name)) {
            return false;
        }
    }

    dom_fs_remove_tree(dest_root);
    if (!dom_fs_copy_tree(source_path, dest_root)) {
        return false;
    }
    if (dom_path_join(dest_content, sizeof(dest_content), dest_root, "content")) {
        dom_fs_mkdirs(dest_content);
    }

    if (!dom_pkg_load_dir(core, dest_root, 0, author_ptr)) {
        return false;
    }
    dom_pkg_resolve_dependencies(core);

    if (out_id) {
        *out_id = core->packages[core->package_count - 1u].info.id;
    }
    return true;
}

bool dom_pkg_uninstall(dom_core* core, dom_package_id id)
{
    dom_package_record* rec;
    uint32_t            idx;

    if (!core) {
        return false;
    }

    rec = dom_pkg_find(core, id);
    if (!rec) {
        return false;
    }
    idx = (uint32_t)(rec - core->packages);

    if (rec->is_official) {
        return false;
    }

    if (!dom_fs_remove_tree(rec->info.install_path)) {
        return false;
    }

    for (; idx + 1u < core->package_count; ++idx) {
        core->packages[idx] = core->packages[idx + 1u];
    }
    core->package_count -= 1u;
    dom_pkg_resolve_dependencies(core);
    return true;
}
