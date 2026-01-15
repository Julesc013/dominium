/*
FILE: source/domino/mod/package_registry.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / mod/package_registry
RESPONSIBILITY: Implements `package_registry`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/mod.h"
#include <stdlib.h>
#include <string.h>

#define DOMINO_MAX_PACKAGES 128

struct domino_package_registry {
    domino_package_desc packages[DOMINO_MAX_PACKAGES];
    unsigned int package_count;
    domino_sys_context* sys;
};

static void domino_join_path(char* dst, size_t cap,
                             const char* a, const char* b)
{
    size_t i = 0;
    size_t j = 0;
    if (!dst || cap == 0) return;
    if (!a) a = "";
    if (!b) b = "";
    while (a[i] != '\0' && i + 1 < cap) {
        dst[i] = a[i];
        ++i;
    }
    if (i > 0 && i + 1 < cap) {
        char c = dst[i - 1];
        if (c != '/' && c != '\\') {
            dst[i++] = '/';
        }
    }
    while (b[j] != '\0' && i + 1 < cap) {
        dst[i++] = b[j++];
    }
    dst[i] = '\0';
}

static void domino_package_registry_clear(domino_package_registry* reg)
{
    if (!reg) return;
    memset(reg->packages, 0, sizeof(reg->packages));
    reg->package_count = 0;
}

domino_package_registry* domino_package_registry_create(void)
{
    domino_package_registry* reg;
    reg = (domino_package_registry*)malloc(sizeof(domino_package_registry));
    if (!reg) return NULL;
    memset(reg, 0, sizeof(*reg));
    return reg;
}

void domino_package_registry_destroy(domino_package_registry* reg)
{
    if (!reg) return;
    free(reg);
}

void domino_package_registry_set_sys(domino_package_registry* reg,
                                     domino_sys_context* sys)
{
    if (!reg) return;
    reg->sys = sys;
}

static int domino_package_registry_add(domino_package_registry* reg,
                                       const domino_package_desc* desc)
{
    unsigned int i;
    if (!reg || !desc || !desc->id[0]) return -1;
    for (i = 0; i < reg->package_count; ++i) {
        if (strcmp(reg->packages[i].id, desc->id) == 0) {
            if (domino_semver_compare(&reg->packages[i].version, &desc->version) < 0) {
                reg->packages[i] = *desc;
            }
            return 0;
        }
    }
    if (reg->package_count >= DOMINO_MAX_PACKAGES) {
        return -1;
    }
    reg->packages[reg->package_count++] = *desc;
    return 0;
}

static int domino_package_registry_scan_container(domino_package_registry* reg,
                                                  const char* root,
                                                  const char* subdir,
                                                  domino_package_kind kind)
{
    char container_path[260];
    char entry_name[260];
    domino_sys_dir_iter* it;
    int is_dir = 0;
    if (!reg || !reg->sys) return -1;
    domino_join_path(container_path, sizeof(container_path), root, subdir);
    it = domino_sys_dir_open(reg->sys, container_path);
    if (!it) return 0;
    while (domino_sys_dir_next(reg->sys, it, entry_name, sizeof(entry_name), &is_dir)) {
        domino_package_desc desc;
        char pkg_path[260];
        char manifest_path[260];
        if (!is_dir) {
            continue;
        }
        if (entry_name[0] == '.') {
            continue;
        }
        memset(&desc, 0, sizeof(desc));
        desc.kind = kind;
        domino_join_path(pkg_path, sizeof(pkg_path), container_path, entry_name);
        domino_join_path(manifest_path, sizeof(manifest_path), pkg_path, "package.toml");
        if (domino_manifest_load_from_file(manifest_path, &desc) != 0) {
            domino_join_path(manifest_path, sizeof(manifest_path), pkg_path, "manifest.toml");
            if (domino_manifest_load_from_file(manifest_path, &desc) != 0) {
                strncpy(desc.id, entry_name, sizeof(desc.id) - 1);
                desc.id[sizeof(desc.id) - 1] = '\0';
                desc.version.major = 0;
                desc.version.minor = 1;
                desc.version.patch = 0;
            }
        }
        desc.kind = kind;
        strncpy(desc.path, pkg_path, sizeof(desc.path) - 1);
        desc.path[sizeof(desc.path) - 1] = '\0';
        domino_package_registry_add(reg, &desc);
    }
    domino_sys_dir_close(reg->sys, it);
    return 0;
}

int domino_package_registry_scan_roots(domino_package_registry* reg,
                                       const char* const* roots,
                                       unsigned int root_count)
{
    unsigned int i;
    if (!reg || !roots || root_count == 0) return -1;
    if (!reg->sys) return -1;
    domino_package_registry_clear(reg);
    for (i = 0; i < root_count; ++i) {
        const char* root = roots[i];
        if (!root || !root[0]) continue;
        domino_package_registry_scan_container(reg, root, "mods", DOMINO_PACKAGE_KIND_MOD);
        domino_package_registry_scan_container(reg, root, "packs", DOMINO_PACKAGE_KIND_PACK);
    }
    return 0;
}

int domino_package_registry_visit(domino_package_registry* reg,
                                  domino_package_visit_fn fn,
                                  void* user)
{
    unsigned int i;
    if (!reg || !fn) return -1;
    for (i = 0; i < reg->package_count; ++i) {
        if (fn(&reg->packages[i], user) != 0) {
            break;
        }
    }
    return 0;
}

const domino_package_desc* domino_package_registry_find(domino_package_registry* reg,
                                                        const char* id)
{
    unsigned int i;
    if (!reg || !id) return NULL;
    for (i = 0; i < reg->package_count; ++i) {
        if (strcmp(reg->packages[i].id, id) == 0) {
            return &reg->packages[i];
        }
    }
    return NULL;
}
