/*
FILE: source/dominium/setup/core/src/plan/dsu_plan.c
MODULE: Dominium Setup
PURPOSE: Plan builder and deterministic dsuplan (de)serialization.
*/
#include "../../include/dsu/dsu_plan.h"
#include "../../include/dsu/dsu_fs.h"
#include "../../include/dsu/dsu_log.h"

#include "../dsu_ctx_internal.h"
#include "../fs/dsu_platform_iface.h"
#include "../log/dsu_events.h"
#include "../util/dsu_util_internal.h"

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define DSU_PLAN_MAGIC_0 'D'
#define DSU_PLAN_MAGIC_1 'S'
#define DSU_PLAN_MAGIC_2 'U'
#define DSU_PLAN_MAGIC_3 'P'
#define DSU_PLAN_FORMAT_VERSION 5u

#define DSU_PLAN_DEFAULT_STATE_REL ".dsu/state.dsustate"

typedef struct dsu_plan_component_t {
    char *id;
    char *version;
} dsu_plan_component_t;

typedef struct dsu_plan_file_t {
    dsu_u8 source_kind;
    dsu_u8 reserved8[3];
    dsu_u64 size;
    dsu_u8 sha256[32];
    char *target_path;
    char *container_path;
    char *member_path;
    dsu_u32 flags;
} dsu_plan_file_t;

typedef struct dsu_plan_step_t {
    dsu_plan_step_kind_t kind;
    char *arg;
} dsu_plan_step_t;

struct dsu_plan {
    dsu_u32 flags;
    dsu_u32 id_hash32;
    dsu_u64 id_hash64;
    dsu_u64 manifest_digest64;
    dsu_u64 resolved_digest64;
    dsu_u8 operation;
    dsu_u8 scope;
    dsu_u8 reserved8[2];
    char *product_id;
    char *version;
    char *platform;
    char *install_root;
    dsu_u32 component_count;
    dsu_plan_component_t *components;
    dsu_u32 dir_count;
    char **dirs;
    dsu_u32 file_count;
    dsu_plan_file_t *files;
    dsu_u32 step_count;
    dsu_plan_step_t *steps;
};

static void dsu__plan_file_free(dsu_plan_file_t *f) {
    if (!f) {
        return;
    }
    dsu__free(f->target_path);
    dsu__free(f->container_path);
    dsu__free(f->member_path);
    memset(f, 0, sizeof(*f));
}

static void dsu__plan_free(dsu_plan_t *p) {
    dsu_u32 i;
    if (!p) {
        return;
    }
    dsu__free(p->product_id);
    dsu__free(p->version);
    dsu__free(p->platform);
    dsu__free(p->install_root);
    for (i = 0u; i < p->component_count; ++i) {
        dsu__free(p->components[i].id);
        dsu__free(p->components[i].version);
    }
    dsu__free(p->components);
    for (i = 0u; i < p->dir_count; ++i) {
        dsu__free(p->dirs[i]);
    }
    dsu__free(p->dirs);
    for (i = 0u; i < p->file_count; ++i) {
        dsu__plan_file_free(&p->files[i]);
    }
    dsu__free(p->files);
    for (i = 0u; i < p->step_count; ++i) {
        dsu__free(p->steps[i].arg);
    }
    dsu__free(p->steps);
    p->components = NULL;
    p->dirs = NULL;
    p->files = NULL;
    p->steps = NULL;
    p->component_count = 0u;
    p->dir_count = 0u;
    p->file_count = 0u;
    p->step_count = 0u;
}

static void dsu__u64_to_le_bytes(dsu_u64 v, dsu_u8 out[8]) {
    out[0] = (dsu_u8)(v & 0xFFu);
    out[1] = (dsu_u8)((v >> 8) & 0xFFu);
    out[2] = (dsu_u8)((v >> 16) & 0xFFu);
    out[3] = (dsu_u8)((v >> 24) & 0xFFu);
    out[4] = (dsu_u8)((v >> 32) & 0xFFu);
    out[5] = (dsu_u8)((v >> 40) & 0xFFu);
    out[6] = (dsu_u8)((v >> 48) & 0xFFu);
    out[7] = (dsu_u8)((v >> 56) & 0xFFu);
}

static void dsu__plan_compute_ids(dsu_plan_t *p) {
    dsu_u32 h32;
    dsu_u64 h64;
    dsu_u32 i;
    dsu_u8 sep;
    dsu_u8 tmp8[8];
    if (!p) {
        return;
    }

    h32 = dsu_digest32_init();
    h64 = dsu_digest64_init();
    sep = 0u;

    dsu__u64_to_le_bytes(p->manifest_digest64, tmp8);
    h32 = dsu_digest32_update(h32, tmp8, 8u);
    h32 = dsu_digest32_update(h32, &sep, 1u);
    h64 = dsu_digest64_update(h64, tmp8, 8u);
    h64 = dsu_digest64_update(h64, &sep, 1u);

    dsu__u64_to_le_bytes(p->resolved_digest64, tmp8);
    h32 = dsu_digest32_update(h32, tmp8, 8u);
    h32 = dsu_digest32_update(h32, &sep, 1u);
    h64 = dsu_digest64_update(h64, tmp8, 8u);
    h64 = dsu_digest64_update(h64, &sep, 1u);

    h32 = dsu_digest32_update(h32, &p->operation, 1u);
    h32 = dsu_digest32_update(h32, &sep, 1u);
    h32 = dsu_digest32_update(h32, &p->scope, 1u);
    h32 = dsu_digest32_update(h32, &sep, 1u);

    h64 = dsu_digest64_update(h64, &p->operation, 1u);
    h64 = dsu_digest64_update(h64, &sep, 1u);
    h64 = dsu_digest64_update(h64, &p->scope, 1u);
    h64 = dsu_digest64_update(h64, &sep, 1u);

    h32 = dsu_digest32_update(h32, p->product_id, dsu__strlen(p->product_id));
    h32 = dsu_digest32_update(h32, &sep, 1u);
    h32 = dsu_digest32_update(h32, p->version, dsu__strlen(p->version));
    h32 = dsu_digest32_update(h32, &sep, 1u);
    h32 = dsu_digest32_update(h32, p->platform, dsu__strlen(p->platform));
    h32 = dsu_digest32_update(h32, &sep, 1u);
    h32 = dsu_digest32_update(h32, p->install_root, dsu__strlen(p->install_root));
    h32 = dsu_digest32_update(h32, &sep, 1u);

    h64 = dsu_digest64_update(h64, p->product_id, dsu__strlen(p->product_id));
    h64 = dsu_digest64_update(h64, &sep, 1u);
    h64 = dsu_digest64_update(h64, p->version, dsu__strlen(p->version));
    h64 = dsu_digest64_update(h64, &sep, 1u);
    h64 = dsu_digest64_update(h64, p->platform, dsu__strlen(p->platform));
    h64 = dsu_digest64_update(h64, &sep, 1u);
    h64 = dsu_digest64_update(h64, p->install_root, dsu__strlen(p->install_root));
    h64 = dsu_digest64_update(h64, &sep, 1u);

    for (i = 0u; i < p->component_count; ++i) {
        const char *cid = p->components[i].id ? p->components[i].id : "";
        const char *cver = p->components[i].version ? p->components[i].version : "";
        h32 = dsu_digest32_update(h32, cid, dsu__strlen(cid));
        h32 = dsu_digest32_update(h32, &sep, 1u);
        h32 = dsu_digest32_update(h32, cver, dsu__strlen(cver));
        h32 = dsu_digest32_update(h32, &sep, 1u);
        h64 = dsu_digest64_update(h64, cid, dsu__strlen(cid));
        h64 = dsu_digest64_update(h64, &sep, 1u);
        h64 = dsu_digest64_update(h64, cver, dsu__strlen(cver));
        h64 = dsu_digest64_update(h64, &sep, 1u);
    }
    for (i = 0u; i < p->dir_count; ++i) {
        const char *d = p->dirs[i] ? p->dirs[i] : "";
        h32 = dsu_digest32_update(h32, d, dsu__strlen(d));
        h32 = dsu_digest32_update(h32, &sep, 1u);
        h64 = dsu_digest64_update(h64, d, dsu__strlen(d));
        h64 = dsu_digest64_update(h64, &sep, 1u);
    }
    for (i = 0u; i < p->file_count; ++i) {
        const dsu_plan_file_t *f = &p->files[i];
        const char *t = f->target_path ? f->target_path : "";
        const char *cpath = f->container_path ? f->container_path : "";
        const char *mpath = f->member_path ? f->member_path : "";
        dsu_u8 kind = f->source_kind;
        dsu_u8 tmp8b[8];

        h32 = dsu_digest32_update(h32, &kind, 1u);
        h32 = dsu_digest32_update(h32, t, dsu__strlen(t));
        h32 = dsu_digest32_update(h32, &sep, 1u);
        h32 = dsu_digest32_update(h32, cpath, dsu__strlen(cpath));
        h32 = dsu_digest32_update(h32, &sep, 1u);
        h32 = dsu_digest32_update(h32, mpath, dsu__strlen(mpath));
        h32 = dsu_digest32_update(h32, &sep, 1u);
        h32 = dsu_digest32_update(h32, f->sha256, 32u);
        h32 = dsu_digest32_update(h32, &sep, 1u);
        dsu__u64_to_le_bytes(f->size, tmp8b);
        h32 = dsu_digest32_update(h32, tmp8b, 8u);
        h32 = dsu_digest32_update(h32, &sep, 1u);
        h32 = dsu_digest32_update(h32, &f->flags, 4u);
        h32 = dsu_digest32_update(h32, &sep, 1u);

        h64 = dsu_digest64_update(h64, &kind, 1u);
        h64 = dsu_digest64_update(h64, t, dsu__strlen(t));
        h64 = dsu_digest64_update(h64, &sep, 1u);
        h64 = dsu_digest64_update(h64, cpath, dsu__strlen(cpath));
        h64 = dsu_digest64_update(h64, &sep, 1u);
        h64 = dsu_digest64_update(h64, mpath, dsu__strlen(mpath));
        h64 = dsu_digest64_update(h64, &sep, 1u);
        h64 = dsu_digest64_update(h64, f->sha256, 32u);
        h64 = dsu_digest64_update(h64, &sep, 1u);
        dsu__u64_to_le_bytes(f->size, tmp8b);
        h64 = dsu_digest64_update(h64, tmp8b, 8u);
        h64 = dsu_digest64_update(h64, &sep, 1u);
        h64 = dsu_digest64_update(h64, &f->flags, 4u);
        h64 = dsu_digest64_update(h64, &sep, 1u);
    }
    for (i = 0u; i < p->step_count; ++i) {
        const dsu_plan_step_t *s = &p->steps[i];
        const char *a = s->arg ? s->arg : "";
        dsu_u8 kind_u8 = (dsu_u8)s->kind;
        h32 = dsu_digest32_update(h32, &kind_u8, 1u);
        h32 = dsu_digest32_update(h32, a, dsu__strlen(a));
        h32 = dsu_digest32_update(h32, &sep, 1u);
        h64 = dsu_digest64_update(h64, &kind_u8, 1u);
        h64 = dsu_digest64_update(h64, a, dsu__strlen(a));
        h64 = dsu_digest64_update(h64, &sep, 1u);
    }

    p->id_hash32 = h32;
    p->id_hash64 = h64;
}

static dsu_status_t dsu__str_list_push(char ***items, dsu_u32 *io_count, dsu_u32 *io_cap, char *owned) {
    dsu_u32 count;
    dsu_u32 cap;
    char **p;
    if (!items || !io_count || !io_cap || !owned) {
        return DSU_STATUS_INVALID_ARGS;
    }
    count = *io_count;
    cap = *io_cap;
    if (count == cap) {
        dsu_u32 new_cap = (cap == 0u) ? 16u : (cap * 2u);
        p = (char **)dsu__realloc(*items, new_cap * (dsu_u32)sizeof(*p));
        if (!p) {
            return DSU_STATUS_IO_ERROR;
        }
        *items = p;
        *io_cap = new_cap;
    }
    (*items)[count] = owned;
    *io_count = count + 1u;
    return DSU_STATUS_SUCCESS;
}

static void dsu__str_list_free(char **items, dsu_u32 count) {
    dsu_u32 i;
    if (!items) {
        return;
    }
    for (i = 0u; i < count; ++i) {
        dsu__free(items[i]);
    }
    dsu__free(items);
}

static dsu_status_t dsu__file_list_push_take(dsu_plan_file_t **items,
                                            dsu_u32 *io_count,
                                            dsu_u32 *io_cap,
                                            dsu_plan_file_t *io_owned) {
    dsu_u32 count;
    dsu_u32 cap;
    dsu_plan_file_t *p;
    if (!items || !io_count || !io_cap || !io_owned) {
        return DSU_STATUS_INVALID_ARGS;
    }
    count = *io_count;
    cap = *io_cap;
    if (count == cap) {
        dsu_u32 new_cap = (cap == 0u) ? 32u : (cap * 2u);
        p = (dsu_plan_file_t *)dsu__realloc(*items, new_cap * (dsu_u32)sizeof(*p));
        if (!p) {
            return DSU_STATUS_IO_ERROR;
        }
        *items = p;
        *io_cap = new_cap;
    }
    (*items)[count] = *io_owned;
    memset(io_owned, 0, sizeof(*io_owned));
    *io_count = count + 1u;
    return DSU_STATUS_SUCCESS;
}

static void dsu__file_list_free(dsu_plan_file_t *items, dsu_u32 count) {
    dsu_u32 i;
    if (!items) {
        return;
    }
    for (i = 0u; i < count; ++i) {
        dsu__plan_file_free(&items[i]);
    }
    dsu__free(items);
}

static int dsu__path_is_abs(const char *p) {
    if (!p) return 0;
    if ((p[0] == '/' && p[1] == '/') || (p[0] == '\\' && p[1] == '\\')) return 1;
    if (p[0] == '/' || p[0] == '\\') return 1;
    if (((p[0] >= 'A' && p[0] <= 'Z') || (p[0] >= 'a' && p[0] <= 'z')) &&
        p[1] == ':' &&
        (p[2] == '/' || p[2] == '\\'))
        return 1;
    return 0;
}

static dsu_status_t dsu__canon_rel_path(const char *in, char **out_canon) {
    dsu_u32 i;
    dsu_u32 n;
    dsu_u32 o = 0u;
    dsu_u32 seg_start = 0u;
    char *buf;
    if (!out_canon) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_canon = NULL;
    if (!in) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (in[0] == '\0') {
        buf = (char *)dsu__malloc(1u);
        if (!buf) return DSU_STATUS_IO_ERROR;
        buf[0] = '\0';
        *out_canon = buf;
        return DSU_STATUS_SUCCESS;
    }
    if (dsu__path_is_abs(in)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!dsu__is_ascii_printable(in)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (strchr(in, ':') != NULL) {
        return DSU_STATUS_INVALID_ARGS;
    }
    n = dsu__strlen(in);
    if (n == 0xFFFFFFFFu) {
        return DSU_STATUS_INVALID_ARGS;
    }
    buf = (char *)dsu__malloc(n + 1u);
    if (!buf) {
        return DSU_STATUS_IO_ERROR;
    }
    for (i = 0u; i <= n; ++i) {
        char c = (i < n) ? in[i] : '\0';
        if (c == '\\') c = '/';
        if (c == '/' || c == '\0') {
            dsu_u32 seg_len = (dsu_u32)(i - seg_start);
            if (seg_len == 0u) {
                /* skip */
            } else if (seg_len == 1u && in[seg_start] == '.') {
                /* skip */
            } else if (seg_len == 2u && in[seg_start] == '.' && in[seg_start + 1u] == '.') {
                dsu__free(buf);
                return DSU_STATUS_INVALID_ARGS;
            } else {
                if (o != 0u) {
                    buf[o++] = '/';
                }
                while (seg_start < i) {
                    char cc = in[seg_start++];
                    if (cc == '\\') cc = '/';
                    buf[o++] = cc;
                }
            }
            seg_start = i + 1u;
        }
    }
    buf[o] = '\0';
    *out_canon = buf;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__dirname_of_path(const char *path, char **out_dir) {
    const char *a;
    const char *b;
    dsu_u32 n;
    char *p;
    if (!out_dir) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_dir = NULL;
    if (!path || path[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
    a = strrchr(path, '/');
    b = strrchr(path, '\\');
    if (!a || (b && b > a)) {
        a = b;
    }
    if (!a) {
        p = dsu__strdup(".");
        if (!p) return DSU_STATUS_IO_ERROR;
        *out_dir = p;
        return DSU_STATUS_SUCCESS;
    }
    n = (dsu_u32)(a - path);
    if (n == 0u) {
        p = dsu__strdup("/");
        if (!p) return DSU_STATUS_IO_ERROR;
        *out_dir = p;
        return DSU_STATUS_SUCCESS;
    }
    p = (char *)dsu__malloc(n + 1u);
    if (!p) {
        return DSU_STATUS_IO_ERROR;
    }
    memcpy(p, path, (size_t)n);
    p[n] = '\0';
    *out_dir = p;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__file_size_u64(const char *path, dsu_u64 *out_size) {
    FILE *f;
    long sz;
    if (!path || !out_size) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_size = 0u;
    f = fopen(path, "rb");
    if (!f) {
        return DSU_STATUS_IO_ERROR;
    }
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return DSU_STATUS_IO_ERROR;
    }
    sz = ftell(f);
    if (sz < 0) {
        fclose(f);
        return DSU_STATUS_IO_ERROR;
    }
    fclose(f);
    *out_size = (dsu_u64)(unsigned long)sz;
    return DSU_STATUS_SUCCESS;
}

static int dsu__file_cmp_target_path(const void *a, const void *b) {
    const dsu_plan_file_t *fa = (const dsu_plan_file_t *)a;
    const dsu_plan_file_t *fb = (const dsu_plan_file_t *)b;
    return dsu__strcmp_bytes(fa->target_path, fb->target_path);
}

static dsu_status_t dsu__fileset_enum_dir(const char *container_abs,
                                         const char *dir_abs,
                                         const char *rel_prefix,
                                         dsu_plan_file_t **io_files,
                                         dsu_u32 *io_file_count,
                                         dsu_u32 *io_file_cap) {
    dsu_platform_dir_entry_t *entries = NULL;
    dsu_u32 entry_count = 0u;
    dsu_u32 i;
    dsu_status_t st;

    if (!container_abs || !dir_abs || !io_files || !io_file_count || !io_file_cap) {
        return DSU_STATUS_INVALID_ARGS;
    }

    st = dsu_platform_list_dir(dir_abs, &entries, &entry_count);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    for (i = 0u; i < entry_count; ++i) {
        dsu_platform_dir_entry_t *e = &entries[i];
        char next_abs[1024];
        char next_rel_buf[1024];
        const char *name = e->name ? e->name : "";
        dsu_u32 dir_len;
        dsu_u32 name_len;
        dsu_u32 rel_len;

        if (e->is_symlink) {
            dsu_platform_free_dir_entries(entries, entry_count);
            return DSU_STATUS_INVALID_ARGS;
        }
        if (name[0] == '\0' || strcmp(name, ".") == 0 || strcmp(name, "..") == 0) {
            dsu_platform_free_dir_entries(entries, entry_count);
            return DSU_STATUS_INVALID_ARGS;
        }

        dir_len = dsu__strlen(dir_abs);
        name_len = dsu__strlen(name);
        if (dir_len == 0xFFFFFFFFu || name_len == 0xFFFFFFFFu) {
            dsu_platform_free_dir_entries(entries, entry_count);
            return DSU_STATUS_INVALID_ARGS;
        }
        if (dir_len + 1u + name_len + 1u > (dsu_u32)sizeof(next_abs)) {
            dsu_platform_free_dir_entries(entries, entry_count);
            return DSU_STATUS_INVALID_ARGS;
        }
        memcpy(next_abs, dir_abs, (size_t)dir_len);
        next_abs[dir_len] = '/';
        memcpy(next_abs + dir_len + 1u, name, (size_t)name_len);
        next_abs[dir_len + 1u + name_len] = '\0';

        if (!rel_prefix) {
            rel_prefix = "";
        }
        rel_len = dsu__strlen(rel_prefix);
        if (rel_len == 0xFFFFFFFFu) {
            dsu_platform_free_dir_entries(entries, entry_count);
            return DSU_STATUS_INVALID_ARGS;
        }

        if (rel_len == 0u) {
            if (name_len + 1u > (dsu_u32)sizeof(next_rel_buf)) {
                dsu_platform_free_dir_entries(entries, entry_count);
                return DSU_STATUS_INVALID_ARGS;
            }
            memcpy(next_rel_buf, name, (size_t)name_len);
            next_rel_buf[name_len] = '\0';
        } else {
            if (rel_len + 1u + name_len + 1u > (dsu_u32)sizeof(next_rel_buf)) {
                dsu_platform_free_dir_entries(entries, entry_count);
                return DSU_STATUS_INVALID_ARGS;
            }
            memcpy(next_rel_buf, rel_prefix, (size_t)rel_len);
            next_rel_buf[rel_len] = '/';
            memcpy(next_rel_buf + rel_len + 1u, name, (size_t)name_len);
            next_rel_buf[rel_len + 1u + name_len] = '\0';
        }

        if (e->is_dir) {
            st = dsu__fileset_enum_dir(container_abs, next_abs, next_rel_buf, io_files, io_file_count, io_file_cap);
            if (st != DSU_STATUS_SUCCESS) {
                dsu_platform_free_dir_entries(entries, entry_count);
                return st;
            }
        } else {
            dsu_plan_file_t fitem;
            char *rel_canon = NULL;
            dsu_u64 size = 0u;
            dsu_u8 sha[32];
            char *tpath = NULL;
            char *cpath = NULL;
            char *mpath = NULL;

            memset(&fitem, 0, sizeof(fitem));
            st = dsu__canon_rel_path(next_rel_buf, &rel_canon);
            if (st != DSU_STATUS_SUCCESS) {
                dsu_platform_free_dir_entries(entries, entry_count);
                return st;
            }
            st = dsu__sha256_file(next_abs, sha);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(rel_canon);
                dsu_platform_free_dir_entries(entries, entry_count);
                return st;
            }
            st = dsu__file_size_u64(next_abs, &size);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(rel_canon);
                dsu_platform_free_dir_entries(entries, entry_count);
                return st;
            }

            tpath = dsu__strdup(rel_canon);
            cpath = dsu__strdup(container_abs);
            mpath = dsu__strdup(rel_canon);
            dsu__free(rel_canon);
            if (!tpath || !cpath || !mpath) {
                dsu__free(tpath);
                dsu__free(cpath);
                dsu__free(mpath);
                dsu_platform_free_dir_entries(entries, entry_count);
                return DSU_STATUS_IO_ERROR;
            }

            fitem.source_kind = (dsu_u8)DSU_MANIFEST_PAYLOAD_KIND_FILESET;
            fitem.size = size;
            memcpy(fitem.sha256, sha, 32u);
            fitem.target_path = tpath;
            fitem.container_path = cpath;
            fitem.member_path = mpath;
            fitem.flags = 0u;

            st = dsu__file_list_push_take(io_files, io_file_count, io_file_cap, &fitem);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__plan_file_free(&fitem);
                dsu_platform_free_dir_entries(entries, entry_count);
                return st;
            }
        }
    }

    dsu_platform_free_dir_entries(entries, entry_count);
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_plan_build(dsu_ctx_t *ctx,
                           const dsu_manifest_t *manifest,
                           const char *manifest_path,
                           const dsu_resolve_result_t *resolved,
                           dsu_plan_t **out_plan) {
    dsu_plan_t *p;
    dsu_u32 resolved_count;
    dsu_u32 apply_count;
    dsu_u32 step_count;
    dsu_u32 i;
    dsu_status_t st;

    if (!ctx || !manifest || !manifest_path || !resolved || !out_plan) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_plan = NULL;

    resolved_count = dsu_resolve_result_component_count(resolved);
    apply_count = 0u;
    for (i = 0u; i < resolved_count; ++i) {
        dsu_resolve_component_action_t a = dsu_resolve_result_component_action(resolved, i);
        if (a != DSU_RESOLVE_COMPONENT_ACTION_NONE) {
            ++apply_count;
        }
    }
    step_count = 1u + apply_count + 2u;

    p = (dsu_plan_t *)dsu__malloc((dsu_u32)sizeof(*p));
    if (!p) {
        return DSU_STATUS_IO_ERROR;
    }
    memset(p, 0, sizeof(*p));
    p->flags = ctx->config.flags;
    p->manifest_digest64 = dsu_resolve_result_manifest_digest64(resolved);
    p->resolved_digest64 = dsu_resolve_result_resolved_digest64(resolved);
    p->operation = (dsu_u8)dsu_resolve_result_operation(resolved);
    p->scope = (dsu_u8)dsu_resolve_result_scope(resolved);
    p->reserved8[0] = 0u;
    p->reserved8[1] = 0u;

    p->product_id = dsu__strdup(dsu_resolve_result_product_id(resolved));
    p->version = dsu__strdup(dsu_resolve_result_product_version(resolved));
    p->platform = dsu__strdup(dsu_resolve_result_platform(resolved));
    p->install_root = dsu__strdup(dsu_resolve_result_install_root(resolved));
    if (!p->product_id || !p->version || !p->platform || !p->install_root) {
        dsu_plan_destroy(ctx, p);
        return DSU_STATUS_IO_ERROR;
    }

    p->components = (dsu_plan_component_t *)dsu__malloc(apply_count * (dsu_u32)sizeof(*p->components));
    if (!p->components && apply_count != 0u) {
        dsu_plan_destroy(ctx, p);
        return DSU_STATUS_IO_ERROR;
    }
    if (apply_count != 0u) {
        memset(p->components, 0, (size_t)apply_count * sizeof(*p->components));
    }
    p->component_count = 0u;
    for (i = 0u; i < resolved_count; ++i) {
        dsu_resolve_component_action_t a = dsu_resolve_result_component_action(resolved, i);
        const char *id;
        const char *ver;
        if (a == DSU_RESOLVE_COMPONENT_ACTION_NONE) {
            continue;
        }
        id = dsu_resolve_result_component_id(resolved, i);
        ver = dsu_resolve_result_component_version(resolved, i);
        p->components[p->component_count].id = dsu__strdup(id ? id : "");
        p->components[p->component_count].version = dsu__strdup(ver ? ver : "");
        if (!p->components[p->component_count].id || !p->components[p->component_count].version) {
            dsu_plan_destroy(ctx, p);
            return DSU_STATUS_IO_ERROR;
        }
        ++p->component_count;
    }

    p->steps = (dsu_plan_step_t *)dsu__malloc(step_count * (dsu_u32)sizeof(*p->steps));
    if (!p->steps) {
        dsu_plan_destroy(ctx, p);
        return DSU_STATUS_IO_ERROR;
    }
    memset(p->steps, 0, (size_t)step_count * sizeof(*p->steps));

    p->steps[0].kind = DSU_PLAN_STEP_DECLARE_INSTALL_ROOT;
    p->steps[0].arg = dsu__strdup(p->install_root);
    if (!p->steps[0].arg) {
        dsu_plan_destroy(ctx, p);
        return DSU_STATUS_IO_ERROR;
    }
    {
        dsu_u32 w = 0u;
        for (i = 0u; i < resolved_count; ++i) {
            dsu_resolve_component_action_t a = dsu_resolve_result_component_action(resolved, i);
            const char *id = dsu_resolve_result_component_id(resolved, i);
            dsu_plan_step_kind_t kind = DSU_PLAN_STEP_INSTALL_COMPONENT;
            if (a == DSU_RESOLVE_COMPONENT_ACTION_NONE) {
                continue;
            }
            if (a == DSU_RESOLVE_COMPONENT_ACTION_UPGRADE) {
                kind = DSU_PLAN_STEP_UPGRADE_COMPONENT;
            } else if (a == DSU_RESOLVE_COMPONENT_ACTION_REPAIR) {
                kind = DSU_PLAN_STEP_REPAIR_COMPONENT;
            } else if (a == DSU_RESOLVE_COMPONENT_ACTION_UNINSTALL) {
                kind = DSU_PLAN_STEP_UNINSTALL_COMPONENT;
            } else {
                kind = DSU_PLAN_STEP_INSTALL_COMPONENT;
            }
            p->steps[1u + w].kind = kind;
            p->steps[1u + w].arg = dsu__strdup(id ? id : "");
            if (!p->steps[1u + w].arg) {
                dsu_plan_destroy(ctx, p);
                return DSU_STATUS_IO_ERROR;
            }
            ++w;
        }
    }
    p->steps[1u + apply_count].kind = DSU_PLAN_STEP_WRITE_STATE;
    p->steps[1u + apply_count].arg = dsu__strdup(DSU_PLAN_DEFAULT_STATE_REL);
    if (!p->steps[1u + apply_count].arg) {
        dsu_plan_destroy(ctx, p);
        return DSU_STATUS_IO_ERROR;
    }
    p->steps[2u + apply_count].kind = DSU_PLAN_STEP_WRITE_LOG;
    p->steps[2u + apply_count].arg = NULL;
    p->step_count = step_count;

    /* Plan S-4: derive explicit directories + file list from manifest payloads. */
    {
        char *manifest_dir = NULL;
        dsu_plan_file_t *files = NULL;
        dsu_u32 file_count = 0u;
        dsu_u32 file_cap = 0u;
        char **dirs = NULL;
        dsu_u32 dir_count = 0u;
        dsu_u32 dir_cap = 0u;
        dsu_u32 mi;

        st = dsu__dirname_of_path(manifest_path, &manifest_dir);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__file_list_free(files, file_count);
            dsu__str_list_free(dirs, dir_count);
            dsu_plan_destroy(ctx, p);
            return st;
        }

        for (i = 0u; i < resolved_count; ++i) {
            dsu_resolve_component_action_t a = dsu_resolve_result_component_action(resolved, i);
            const char *cid = dsu_resolve_result_component_id(resolved, i);
            dsu_u32 payload_count;
            dsu_u32 pi;

            if (a != DSU_RESOLVE_COMPONENT_ACTION_INSTALL &&
                a != DSU_RESOLVE_COMPONENT_ACTION_UPGRADE &&
                a != DSU_RESOLVE_COMPONENT_ACTION_REPAIR) {
                continue;
            }
            if (!cid || cid[0] == '\0') {
                dsu__free(manifest_dir);
                dsu__file_list_free(files, file_count);
                dsu__str_list_free(dirs, dir_count);
                dsu_plan_destroy(ctx, p);
                return DSU_STATUS_INVALID_ARGS;
            }

            /* Find component in manifest. */
            mi = 0u;
            for (; mi < dsu_manifest_component_count(manifest); ++mi) {
                const char *mid = dsu_manifest_component_id(manifest, mi);
                if (mid && dsu__strcmp_bytes(mid, cid) == 0) {
                    break;
                }
            }
            if (mi >= dsu_manifest_component_count(manifest)) {
                dsu__free(manifest_dir);
                dsu__file_list_free(files, file_count);
                dsu__str_list_free(dirs, dir_count);
                dsu_plan_destroy(ctx, p);
                return DSU_STATUS_MISSING_COMPONENT;
            }

            payload_count = dsu_manifest_component_payload_count(manifest, mi);
            for (pi = 0u; pi < payload_count; ++pi) {
                dsu_manifest_payload_kind_t kind = dsu_manifest_component_payload_kind(manifest, mi, pi);
                const char *ppath = dsu_manifest_component_payload_path(manifest, mi, pi);
                char joined[1024];
                char canon_abs[1024];
                dsu_u32 base_len;
                dsu_u32 rel_len;

                if (!ppath || ppath[0] == '\0') {
                    dsu__free(manifest_dir);
                    dsu__file_list_free(files, file_count);
                    dsu__str_list_free(dirs, dir_count);
                    dsu_plan_destroy(ctx, p);
                    return DSU_STATUS_INVALID_ARGS;
                }

                if (dsu__path_is_abs(ppath)) {
                    if (dsu__strlen(ppath) + 1u > (dsu_u32)sizeof(joined)) {
                        dsu__free(manifest_dir);
                        dsu__file_list_free(files, file_count);
                        dsu__str_list_free(dirs, dir_count);
                        dsu_plan_destroy(ctx, p);
                        return DSU_STATUS_INVALID_ARGS;
                    }
                    memcpy(joined, ppath, (size_t)dsu__strlen(ppath) + 1u);
                } else {
                    base_len = dsu__strlen(manifest_dir);
                    rel_len = dsu__strlen(ppath);
                    if (base_len == 0xFFFFFFFFu || rel_len == 0xFFFFFFFFu) {
                        dsu__free(manifest_dir);
                        dsu__file_list_free(files, file_count);
                        dsu__str_list_free(dirs, dir_count);
                        dsu_plan_destroy(ctx, p);
                        return DSU_STATUS_INVALID_ARGS;
                    }
                    if (base_len + 1u + rel_len + 1u > (dsu_u32)sizeof(joined)) {
                        dsu__free(manifest_dir);
                        dsu__file_list_free(files, file_count);
                        dsu__str_list_free(dirs, dir_count);
                        dsu_plan_destroy(ctx, p);
                        return DSU_STATUS_INVALID_ARGS;
                    }
                    memcpy(joined, manifest_dir, (size_t)base_len);
                    if (base_len != 0u && manifest_dir[base_len - 1u] != '/' && manifest_dir[base_len - 1u] != '\\') {
                        joined[base_len++] = '/';
                    }
                    memcpy(joined + base_len, ppath, (size_t)rel_len);
                    joined[base_len + rel_len] = '\0';
                }

                st = dsu_fs_path_canonicalize(joined, canon_abs, (dsu_u32)sizeof(canon_abs));
                if (st != DSU_STATUS_SUCCESS) {
                    dsu__free(manifest_dir);
                    dsu__file_list_free(files, file_count);
                    dsu__str_list_free(dirs, dir_count);
                    dsu_plan_destroy(ctx, p);
                    return st;
                }

                if (kind == DSU_MANIFEST_PAYLOAD_KIND_FILESET) {
                    st = dsu__fileset_enum_dir(canon_abs, canon_abs, "", &files, &file_count, &file_cap);
                    if (st != DSU_STATUS_SUCCESS) {
                        dsu__free(manifest_dir);
                        dsu__file_list_free(files, file_count);
                        dsu__str_list_free(dirs, dir_count);
                        dsu_plan_destroy(ctx, p);
                        return st;
                    }
                } else if (kind == DSU_MANIFEST_PAYLOAD_KIND_ARCHIVE) {
                    dsu__archive_entry_t *ae = NULL;
                    dsu_u32 ac = 0u;
                    dsu_u32 ai;
                    st = dsu__archive_list(canon_abs, &ae, &ac);
                    if (st != DSU_STATUS_SUCCESS) {
                        dsu__free(manifest_dir);
                        dsu__file_list_free(files, file_count);
                        dsu__str_list_free(dirs, dir_count);
                        dsu_plan_destroy(ctx, p);
                        return st;
                    }
                    for (ai = 0u; ai < ac; ++ai) {
                        dsu_plan_file_t fitem;
                        memset(&fitem, 0, sizeof(fitem));
                        fitem.source_kind = (dsu_u8)DSU_MANIFEST_PAYLOAD_KIND_ARCHIVE;
                        fitem.size = ae[ai].size;
                        memcpy(fitem.sha256, ae[ai].sha256, 32u);
                        fitem.target_path = dsu__strdup(ae[ai].path);
                        fitem.container_path = dsu__strdup(canon_abs);
                        fitem.member_path = dsu__strdup(ae[ai].path);
                        fitem.flags = 0u;
                        if (!fitem.target_path || !fitem.container_path || !fitem.member_path) {
                            dsu__plan_file_free(&fitem);
                            dsu__archive_free_entries(ae, ac);
                            dsu__free(manifest_dir);
                            dsu__file_list_free(files, file_count);
                            dsu__str_list_free(dirs, dir_count);
                            dsu_plan_destroy(ctx, p);
                            return DSU_STATUS_IO_ERROR;
                        }
                        st = dsu__file_list_push_take(&files, &file_count, &file_cap, &fitem);
                        if (st != DSU_STATUS_SUCCESS) {
                            dsu__plan_file_free(&fitem);
                            dsu__archive_free_entries(ae, ac);
                            dsu__free(manifest_dir);
                            dsu__file_list_free(files, file_count);
                            dsu__str_list_free(dirs, dir_count);
                            dsu_plan_destroy(ctx, p);
                            return st;
                        }
                    }
                    dsu__archive_free_entries(ae, ac);
                } else {
                    /* blob payloads are not installed via filesystem in Plan S-4. */
                }
            }
        }

        dsu__free(manifest_dir);
        manifest_dir = NULL;

        if (file_count > 1u) {
            qsort(files, (size_t)file_count, sizeof(*files), dsu__file_cmp_target_path);
            for (i = 1u; i < file_count; ++i) {
                if (dsu__strcmp_bytes(files[i - 1u].target_path, files[i].target_path) == 0) {
                    dsu__file_list_free(files, file_count);
                    dsu__str_list_free(dirs, dir_count);
                    dsu_plan_destroy(ctx, p);
                    return DSU_STATUS_EXPLICIT_CONFLICT;
                }
            }
        }

        /* Directory intents: include root "" and all parent directories. */
        {
            char *root_dir = dsu__strdup("");
            if (!root_dir) {
                dsu__file_list_free(files, file_count);
                dsu__str_list_free(dirs, dir_count);
                dsu_plan_destroy(ctx, p);
                return DSU_STATUS_IO_ERROR;
            }
            st = dsu__str_list_push(&dirs, &dir_count, &dir_cap, root_dir);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(root_dir);
                dsu__file_list_free(files, file_count);
                dsu__str_list_free(dirs, dir_count);
                dsu_plan_destroy(ctx, p);
                return st;
            }
        }

        for (i = 0u; i < file_count; ++i) {
            const char *t = files[i].target_path ? files[i].target_path : "";
            dsu_u32 tlen = dsu__strlen(t);
            dsu_u32 j;
            if (tlen == 0xFFFFFFFFu) {
                dsu__file_list_free(files, file_count);
                dsu__str_list_free(dirs, dir_count);
                dsu_plan_destroy(ctx, p);
                return DSU_STATUS_INVALID_ARGS;
            }
            for (j = 0u; j < tlen; ++j) {
                if (t[j] == '/') {
                    char *d = (char *)dsu__malloc(j + 1u);
                    if (!d) {
                        dsu__file_list_free(files, file_count);
                        dsu__str_list_free(dirs, dir_count);
                        dsu_plan_destroy(ctx, p);
                        return DSU_STATUS_IO_ERROR;
                    }
                    if (j) {
                        memcpy(d, t, (size_t)j);
                    }
                    d[j] = '\0';
                    st = dsu__str_list_push(&dirs, &dir_count, &dir_cap, d);
                    if (st != DSU_STATUS_SUCCESS) {
                        dsu__free(d);
                        dsu__file_list_free(files, file_count);
                        dsu__str_list_free(dirs, dir_count);
                        dsu_plan_destroy(ctx, p);
                        return st;
                    }
                }
            }
        }

        if (dir_count > 1u) {
            dsu__sort_str_ptrs(dirs, dir_count);
            {
                dsu_u32 w = 0u;
                for (i = 0u; i < dir_count; ++i) {
                    if (w == 0u || dsu__strcmp_bytes(dirs[w - 1u], dirs[i]) != 0) {
                        dirs[w++] = dirs[i];
                    } else {
                        dsu__free(dirs[i]);
                    }
                }
                dir_count = w;
            }
        }

        p->files = files;
        p->file_count = file_count;
        p->dirs = dirs;
        p->dir_count = dir_count;
    }

    dsu__plan_compute_ids(p);

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_PLAN_BUILT,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_PLAN,
                      "plan built");

    *out_plan = p;
    return DSU_STATUS_SUCCESS;
}

void dsu_plan_destroy(dsu_ctx_t *ctx, dsu_plan_t *plan) {
    (void)ctx;
    if (!plan) {
        return;
    }
    dsu__plan_free(plan);
    dsu__free(plan);
}

dsu_u32 dsu_plan_id_hash32(const dsu_plan_t *plan) {
    if (!plan) {
        return 0u;
    }
    return plan->id_hash32;
}

dsu_u64 dsu_plan_id_hash64(const dsu_plan_t *plan) {
    if (!plan) {
        return (dsu_u64)0u;
    }
    return plan->id_hash64;
}

dsu_resolve_operation_t dsu_plan_operation(const dsu_plan_t *plan) {
    if (!plan) {
        return DSU_RESOLVE_OPERATION_INSTALL;
    }
    return (dsu_resolve_operation_t)plan->operation;
}

dsu_manifest_install_scope_t dsu_plan_scope(const dsu_plan_t *plan) {
    if (!plan) {
        return DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    }
    return (dsu_manifest_install_scope_t)plan->scope;
}

const char *dsu_plan_product_id(const dsu_plan_t *plan) {
    if (!plan || !plan->product_id) {
        return "";
    }
    return plan->product_id;
}

const char *dsu_plan_version(const dsu_plan_t *plan) {
    if (!plan || !plan->version) {
        return "";
    }
    return plan->version;
}

const char *dsu_plan_platform(const dsu_plan_t *plan) {
    if (!plan || !plan->platform) {
        return "";
    }
    return plan->platform;
}

const char *dsu_plan_install_root(const dsu_plan_t *plan) {
    if (!plan || !plan->install_root) {
        return "";
    }
    return plan->install_root;
}

dsu_u32 dsu_plan_component_count(const dsu_plan_t *plan) {
    if (!plan) {
        return 0u;
    }
    return plan->component_count;
}

const char *dsu_plan_component_id(const dsu_plan_t *plan, dsu_u32 index) {
    if (!plan || index >= plan->component_count) {
        return NULL;
    }
    return plan->components[index].id;
}

const char *dsu_plan_component_version(const dsu_plan_t *plan, dsu_u32 index) {
    if (!plan || index >= plan->component_count) {
        return NULL;
    }
    return plan->components[index].version;
}

dsu_u32 dsu_plan_step_count(const dsu_plan_t *plan) {
    if (!plan) {
        return 0u;
    }
    return plan->step_count;
}

dsu_plan_step_kind_t dsu_plan_step_kind(const dsu_plan_t *plan, dsu_u32 index) {
    if (!plan || index >= plan->step_count) {
        return (dsu_plan_step_kind_t)0;
    }
    return plan->steps[index].kind;
}

const char *dsu_plan_step_arg(const dsu_plan_t *plan, dsu_u32 index) {
    if (!plan || index >= plan->step_count) {
        return NULL;
    }
    return plan->steps[index].arg;
}

dsu_u32 dsu_plan_dir_count(const dsu_plan_t *plan) {
    if (!plan) {
        return 0u;
    }
    return plan->dir_count;
}

const char *dsu_plan_dir_path(const dsu_plan_t *plan, dsu_u32 index) {
    if (!plan || index >= plan->dir_count) {
        return NULL;
    }
    return plan->dirs[index];
}

dsu_u32 dsu_plan_file_count(const dsu_plan_t *plan) {
    if (!plan) {
        return 0u;
    }
    return plan->file_count;
}

const char *dsu_plan_file_target_path(const dsu_plan_t *plan, dsu_u32 index) {
    if (!plan || index >= plan->file_count) {
        return NULL;
    }
    return plan->files[index].target_path;
}

dsu_manifest_payload_kind_t dsu_plan_file_source_kind(const dsu_plan_t *plan, dsu_u32 index) {
    if (!plan || index >= plan->file_count) {
        return DSU_MANIFEST_PAYLOAD_KIND_FILESET;
    }
    return (dsu_manifest_payload_kind_t)plan->files[index].source_kind;
}

const char *dsu_plan_file_source_container_path(const dsu_plan_t *plan, dsu_u32 index) {
    if (!plan || index >= plan->file_count) {
        return NULL;
    }
    return plan->files[index].container_path;
}

const char *dsu_plan_file_source_member_path(const dsu_plan_t *plan, dsu_u32 index) {
    if (!plan || index >= plan->file_count) {
        return NULL;
    }
    return plan->files[index].member_path;
}

dsu_u64 dsu_plan_file_size(const dsu_plan_t *plan, dsu_u32 index) {
    if (!plan || index >= plan->file_count) {
        return (dsu_u64)0u;
    }
    return plan->files[index].size;
}

const dsu_u8 *dsu_plan_file_sha256(const dsu_plan_t *plan, dsu_u32 index) {
    if (!plan || index >= plan->file_count) {
        return NULL;
    }
    return plan->files[index].sha256;
}

dsu_status_t dsu_plan_write_file(dsu_ctx_t *ctx, const dsu_plan_t *plan, const char *path) {
    dsu_blob_t payload;
    dsu_blob_t file_bytes;
    dsu_u8 magic[4];
    dsu_u32 i;
    dsu_status_t st;

    if (!ctx || !plan || !path) {
        return DSU_STATUS_INVALID_ARGS;
    }

    dsu__blob_init(&payload);
    dsu__blob_init(&file_bytes);

    st = dsu__blob_put_u32le(&payload, plan->flags);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u32le(&payload, plan->id_hash32);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u64le(&payload, plan->id_hash64);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u64le(&payload, plan->manifest_digest64);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u64le(&payload, plan->resolved_digest64);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u8(&payload, plan->operation);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u8(&payload, plan->scope);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u16le(&payload, 0u);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u32le(&payload, dsu__strlen(plan->product_id));
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u32le(&payload, dsu__strlen(plan->version));
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u32le(&payload, dsu__strlen(plan->platform));
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u32le(&payload, dsu__strlen(plan->install_root));
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u32le(&payload, plan->component_count);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u32le(&payload, plan->dir_count);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u32le(&payload, plan->file_count);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_u32le(&payload, plan->step_count);

    if (st == DSU_STATUS_SUCCESS && dsu__strlen(plan->product_id)) {
        st = dsu__blob_append(&payload, plan->product_id, dsu__strlen(plan->product_id));
    }
    if (st == DSU_STATUS_SUCCESS && dsu__strlen(plan->version)) {
        st = dsu__blob_append(&payload, plan->version, dsu__strlen(plan->version));
    }
    if (st == DSU_STATUS_SUCCESS && dsu__strlen(plan->platform)) {
        st = dsu__blob_append(&payload, plan->platform, dsu__strlen(plan->platform));
    }
    if (st == DSU_STATUS_SUCCESS && dsu__strlen(plan->install_root)) {
        st = dsu__blob_append(&payload, plan->install_root, dsu__strlen(plan->install_root));
    }

    for (i = 0u; st == DSU_STATUS_SUCCESS && i < plan->component_count; ++i) {
        const dsu_plan_component_t *c = &plan->components[i];
        const char *cid = c->id ? c->id : "";
        const char *cver = c->version ? c->version : "";
        dsu_u32 id_len = dsu__strlen(cid);
        dsu_u32 ver_len = dsu__strlen(cver);
        st = dsu__blob_put_u32le(&payload, id_len);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u32le(&payload, ver_len);
        if (st != DSU_STATUS_SUCCESS) break;
        if (id_len) {
            st = dsu__blob_append(&payload, cid, id_len);
            if (st != DSU_STATUS_SUCCESS) break;
        }
        if (ver_len) {
            st = dsu__blob_append(&payload, cver, ver_len);
            if (st != DSU_STATUS_SUCCESS) break;
        }
    }

    for (i = 0u; st == DSU_STATUS_SUCCESS && i < plan->dir_count; ++i) {
        const char *d = plan->dirs[i] ? plan->dirs[i] : "";
        dsu_u32 n = dsu__strlen(d);
        st = dsu__blob_put_u32le(&payload, n);
        if (st != DSU_STATUS_SUCCESS) break;
        if (n) {
            st = dsu__blob_append(&payload, d, n);
            if (st != DSU_STATUS_SUCCESS) break;
        }
    }

    for (i = 0u; st == DSU_STATUS_SUCCESS && i < plan->file_count; ++i) {
        const dsu_plan_file_t *f = &plan->files[i];
        const char *t = f->target_path ? f->target_path : "";
        const char *c = f->container_path ? f->container_path : "";
        const char *m = f->member_path ? f->member_path : "";
        dsu_u32 t_len = dsu__strlen(t);
        dsu_u32 c_len = dsu__strlen(c);
        dsu_u32 m_len = dsu__strlen(m);
        st = dsu__blob_put_u8(&payload, f->source_kind);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u8(&payload, 0u);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u16le(&payload, 0u);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u32le(&payload, f->flags);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u64le(&payload, f->size);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u32le(&payload, t_len);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u32le(&payload, c_len);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u32le(&payload, m_len);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_append(&payload, f->sha256, 32u);
        if (st != DSU_STATUS_SUCCESS) break;
        if (t_len) {
            st = dsu__blob_append(&payload, t, t_len);
            if (st != DSU_STATUS_SUCCESS) break;
        }
        if (c_len) {
            st = dsu__blob_append(&payload, c, c_len);
            if (st != DSU_STATUS_SUCCESS) break;
        }
        if (m_len) {
            st = dsu__blob_append(&payload, m, m_len);
            if (st != DSU_STATUS_SUCCESS) break;
        }
    }

    for (i = 0u; st == DSU_STATUS_SUCCESS && i < plan->step_count; ++i) {
        const dsu_plan_step_t *s = &plan->steps[i];
        const char *arg = s->arg ? s->arg : "";
        dsu_u32 arg_len = dsu__strlen(arg);
        st = dsu__blob_put_u8(&payload, (dsu_u8)s->kind);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u8(&payload, 0u);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u16le(&payload, 0u);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u32le(&payload, arg_len);
        if (st != DSU_STATUS_SUCCESS) break;
        if (arg_len) {
            st = dsu__blob_append(&payload, arg, arg_len);
            if (st != DSU_STATUS_SUCCESS) break;
        }
    }

    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&payload);
        dsu__blob_free(&file_bytes);
        return st;
    }

    magic[0] = (dsu_u8)DSU_PLAN_MAGIC_0;
    magic[1] = (dsu_u8)DSU_PLAN_MAGIC_1;
    magic[2] = (dsu_u8)DSU_PLAN_MAGIC_2;
    magic[3] = (dsu_u8)DSU_PLAN_MAGIC_3;

    st = dsu__file_wrap_payload(magic, (dsu_u16)DSU_PLAN_FORMAT_VERSION, payload.data, payload.size, &file_bytes);
    dsu__blob_free(&payload);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&file_bytes);
        return st;
    }

    st = dsu__fs_write_all(path, file_bytes.data, file_bytes.size);
    dsu__blob_free(&file_bytes);

    if (st == DSU_STATUS_SUCCESS) {
        (void)dsu_log_emit(ctx,
                          dsu_ctx_get_audit_log(ctx),
                          DSU_EVENT_PLAN_WRITTEN,
                          (dsu_u8)DSU_LOG_SEVERITY_INFO,
                          (dsu_u8)DSU_LOG_CATEGORY_PLAN,
                          "plan written");
    }
    return st;
}

static dsu_status_t dsu__read_string_alloc(const dsu_u8 *buf,
                                          dsu_u32 len,
                                          dsu_u32 *io_off,
                                          dsu_u32 n,
                                          char **out_str) {
    char *s;
    dsu_u32 i;
    if (!out_str) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_str = NULL;
    if (n == 0u) {
        s = (char *)dsu__malloc(1u);
        if (!s) {
            return DSU_STATUS_IO_ERROR;
        }
        s[0] = '\0';
        *out_str = s;
        return DSU_STATUS_SUCCESS;
    }
    if (len - *io_off < n) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    s = (char *)dsu__malloc(n + 1u);
    if (!s) {
        return DSU_STATUS_IO_ERROR;
    }
    memcpy(s, buf + *io_off, (size_t)n);
    s[n] = '\0';
    for (i = 0u; i < n; ++i) {
        if (((unsigned char *)s)[i] == 0u) {
            dsu__free(s);
            return DSU_STATUS_INTEGRITY_ERROR;
        }
    }
    *io_off += n;
    *out_str = s;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_plan_read_file(dsu_ctx_t *ctx, const char *path, dsu_plan_t **out_plan) {
    dsu_u8 *file_bytes;
    dsu_u32 file_len;
    dsu_u8 magic[4];
    const dsu_u8 *payload;
    dsu_u32 payload_len;
    dsu_u32 off;
    dsu_status_t st;
    dsu_plan_t *p;
    dsu_u32 product_len;
    dsu_u32 version_len;
    dsu_u32 platform_len;
    dsu_u32 root_len;
    dsu_u16 reserved16;
    dsu_u32 i;

    if (!ctx || !path || !out_plan) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_plan = NULL;

    st = dsu__fs_read_all(&ctx->config, path, &file_bytes, &file_len);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    magic[0] = (dsu_u8)DSU_PLAN_MAGIC_0;
    magic[1] = (dsu_u8)DSU_PLAN_MAGIC_1;
    magic[2] = (dsu_u8)DSU_PLAN_MAGIC_2;
    magic[3] = (dsu_u8)DSU_PLAN_MAGIC_3;

    st = dsu__file_unwrap_payload(file_bytes,
                                  file_len,
                                  magic,
                                  (dsu_u16)DSU_PLAN_FORMAT_VERSION,
                                  &payload,
                                  &payload_len);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(file_bytes);
        return st;
    }

    p = (dsu_plan_t *)dsu__malloc((dsu_u32)sizeof(*p));
    if (!p) {
        dsu__free(file_bytes);
        return DSU_STATUS_IO_ERROR;
    }
    memset(p, 0, sizeof(*p));

    off = 0u;
    st = dsu__read_u32le(payload, payload_len, &off, &p->flags);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u32le(payload, payload_len, &off, &p->id_hash32);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u64le(payload, payload_len, &off, &p->id_hash64);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u64le(payload, payload_len, &off, &p->manifest_digest64);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u64le(payload, payload_len, &off, &p->resolved_digest64);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u8(payload, payload_len, &off, &p->operation);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u8(payload, payload_len, &off, &p->scope);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u16le(payload, payload_len, &off, &reserved16);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u32le(payload, payload_len, &off, &product_len);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u32le(payload, payload_len, &off, &version_len);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u32le(payload, payload_len, &off, &platform_len);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u32le(payload, payload_len, &off, &root_len);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u32le(payload, payload_len, &off, &p->component_count);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u32le(payload, payload_len, &off, &p->dir_count);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u32le(payload, payload_len, &off, &p->file_count);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_u32le(payload, payload_len, &off, &p->step_count);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(file_bytes);
        dsu_plan_destroy(ctx, p);
        return st;
    }
    (void)reserved16;

    st = dsu__read_string_alloc(payload, payload_len, &off, product_len, &p->product_id);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_string_alloc(payload, payload_len, &off, version_len, &p->version);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_string_alloc(payload, payload_len, &off, platform_len, &p->platform);
    if (st == DSU_STATUS_SUCCESS) st = dsu__read_string_alloc(payload, payload_len, &off, root_len, &p->install_root);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(file_bytes);
        dsu_plan_destroy(ctx, p);
        return st;
    }

    p->components = (dsu_plan_component_t *)dsu__malloc(p->component_count * (dsu_u32)sizeof(*p->components));
    if (!p->components && p->component_count != 0u) {
        dsu__free(file_bytes);
        dsu_plan_destroy(ctx, p);
        return DSU_STATUS_IO_ERROR;
    }
    if (p->component_count != 0u) {
        memset(p->components, 0, (size_t)p->component_count * sizeof(*p->components));
    }
    for (i = 0u; i < p->component_count; ++i) {
        dsu_u32 id_len;
        dsu_u32 ver_len;
        st = dsu__read_u32le(payload, payload_len, &off, &id_len);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u32le(payload, payload_len, &off, &ver_len);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_string_alloc(payload, payload_len, &off, id_len, &p->components[i].id);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_string_alloc(payload, payload_len, &off, ver_len, &p->components[i].version);
        if (st != DSU_STATUS_SUCCESS) break;
        if (!p->components[i].id || p->components[i].id[0] == '\0' ||
            !p->components[i].version || p->components[i].version[0] == '\0') {
            st = DSU_STATUS_INTEGRITY_ERROR;
            break;
        }
    }
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(file_bytes);
        dsu_plan_destroy(ctx, p);
        return st;
    }

    p->dirs = (char **)dsu__malloc(p->dir_count * (dsu_u32)sizeof(*p->dirs));
    if (!p->dirs && p->dir_count != 0u) {
        dsu__free(file_bytes);
        dsu_plan_destroy(ctx, p);
        return DSU_STATUS_IO_ERROR;
    }
    if (p->dir_count != 0u) {
        memset(p->dirs, 0, (size_t)p->dir_count * sizeof(*p->dirs));
    }
    for (i = 0u; i < p->dir_count; ++i) {
        dsu_u32 n;
        st = dsu__read_u32le(payload, payload_len, &off, &n);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_string_alloc(payload, payload_len, &off, n, &p->dirs[i]);
        if (st != DSU_STATUS_SUCCESS) break;
    }
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(file_bytes);
        dsu_plan_destroy(ctx, p);
        return st;
    }

    p->files = (dsu_plan_file_t *)dsu__malloc(p->file_count * (dsu_u32)sizeof(*p->files));
    if (!p->files && p->file_count != 0u) {
        dsu__free(file_bytes);
        dsu_plan_destroy(ctx, p);
        return DSU_STATUS_IO_ERROR;
    }
    if (p->file_count != 0u) {
        memset(p->files, 0, (size_t)p->file_count * sizeof(*p->files));
    }
    for (i = 0u; i < p->file_count; ++i) {
        dsu_u8 kind;
        dsu_u8 reserved8;
        dsu_u16 reserved16;
        dsu_u32 t_len;
        dsu_u32 c_len;
        dsu_u32 m_len;
        st = dsu__read_u8(payload, payload_len, &off, &kind);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u8(payload, payload_len, &off, &reserved8);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u16le(payload, payload_len, &off, &reserved16);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u32le(payload, payload_len, &off, &p->files[i].flags);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u64le(payload, payload_len, &off, &p->files[i].size);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u32le(payload, payload_len, &off, &t_len);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u32le(payload, payload_len, &off, &c_len);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u32le(payload, payload_len, &off, &m_len);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_bytes(payload, payload_len, &off, p->files[i].sha256, 32u);
        if (st != DSU_STATUS_SUCCESS) break;
        p->files[i].source_kind = kind;
        (void)reserved8;
        (void)reserved16;
        st = dsu__read_string_alloc(payload, payload_len, &off, t_len, &p->files[i].target_path);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_string_alloc(payload, payload_len, &off, c_len, &p->files[i].container_path);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_string_alloc(payload, payload_len, &off, m_len, &p->files[i].member_path);
        if (st != DSU_STATUS_SUCCESS) break;
        if (!p->files[i].target_path || p->files[i].target_path[0] == '\0') {
            st = DSU_STATUS_INTEGRITY_ERROR;
            break;
        }
        if (p->files[i].container_path && p->files[i].container_path[0] == '\0') {
            dsu__free(p->files[i].container_path);
            p->files[i].container_path = NULL;
        }
        if (p->files[i].member_path && p->files[i].member_path[0] == '\0') {
            dsu__free(p->files[i].member_path);
            p->files[i].member_path = NULL;
        }
    }
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(file_bytes);
        dsu_plan_destroy(ctx, p);
        return st;
    }

    p->steps = (dsu_plan_step_t *)dsu__malloc(p->step_count * (dsu_u32)sizeof(*p->steps));
    if (!p->steps && p->step_count != 0u) {
        dsu__free(file_bytes);
        dsu_plan_destroy(ctx, p);
        return DSU_STATUS_IO_ERROR;
    }
    if (p->step_count != 0u) {
        memset(p->steps, 0, (size_t)p->step_count * sizeof(*p->steps));
    }
    for (i = 0u; i < p->step_count; ++i) {
        dsu_u8 kind;
        dsu_u8 reserved8;
        dsu_u16 reserved16;
        dsu_u32 arg_len;
        st = dsu__read_u8(payload, payload_len, &off, &kind);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u8(payload, payload_len, &off, &reserved8);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u16le(payload, payload_len, &off, &reserved16);
        if (st != DSU_STATUS_SUCCESS) break;
        (void)reserved8;
        (void)reserved16;
        st = dsu__read_u32le(payload, payload_len, &off, &arg_len);
        if (st != DSU_STATUS_SUCCESS) break;
        p->steps[i].kind = (dsu_plan_step_kind_t)kind;
        st = dsu__read_string_alloc(payload, payload_len, &off, arg_len, &p->steps[i].arg);
        if (st != DSU_STATUS_SUCCESS) break;
        if (p->steps[i].arg && p->steps[i].arg[0] == '\0') {
            dsu__free(p->steps[i].arg);
            p->steps[i].arg = NULL;
        }
    }
    dsu__free(file_bytes);
    if (st != DSU_STATUS_SUCCESS) {
        dsu_plan_destroy(ctx, p);
        return st;
    }

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_PLAN_LOADED,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_PLAN,
                      "plan loaded");

    *out_plan = p;
    return DSU_STATUS_SUCCESS;
}
