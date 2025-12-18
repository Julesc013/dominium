/*
FILE: source/dominium/setup/core/src/state/dsu_state_s5.c
MODULE: Dominium Setup
PURPOSE: Installed-state load/save + forensics (Plan S-5; deterministic TLV format).
*/
#include "../../include/dsu/dsu_state.h"

#include "dsu_state_internal.h"

#include "../../include/dsu/dsu_fs.h"

#include "../dsu_ctx_internal.h"
#include "../fs/dsu_platform_iface.h"
#include "../util/dsu_util_internal.h"

#include <stdlib.h>
#include <string.h>
#include <time.h>

/* S-5 implementation is built incrementally to avoid tool patch-size limits. */

#define DSU_STATE_MAGIC_0 'D'
#define DSU_STATE_MAGIC_1 'S'
#define DSU_STATE_MAGIC_2 'U'
#define DSU_STATE_MAGIC_3 'S'

#define DSU_STATE_FORMAT_VERSION 2u
#define DSU_STATE_ROOT_SCHEMA_VERSION 2u

#define DSU_TLV_STATE_ROOT 0x0001u
#define DSU_TLV_STATE_ROOT_VERSION 0x0002u /* u32 */

#define DSU_TLV_STATE_PRODUCT_ID 0x0010u      /* string */
#define DSU_TLV_STATE_PRODUCT_VERSION 0x0011u /* string */
#define DSU_TLV_STATE_BUILD_CHANNEL 0x0012u   /* string */
#define DSU_TLV_STATE_INSTALL_INSTANCE_ID 0x0013u /* u64 */

#define DSU_TLV_STATE_PLATFORM 0x0020u     /* string */
#define DSU_TLV_STATE_SCOPE 0x0021u        /* u8 */
#define DSU_TLV_STATE_INSTALL_ROOT 0x0022u /* string (primary; compatibility) */

#define DSU_TLV_STATE_INSTALL_ROOT_ITEM 0x0023u    /* container */
#define DSU_TLV_STATE_INSTALL_ROOT_VERSION 0x0024u /* u32 */
#define DSU_TLV_STATE_INSTALL_ROOT_ROLE 0x0025u    /* u8 */
#define DSU_TLV_STATE_INSTALL_ROOT_PATH 0x0026u    /* string (absolute canonical) */

#define DSU_TLV_STATE_MANIFEST_DIGEST64 0x0030u /* u64 */
#define DSU_TLV_STATE_RESOLVED_DIGEST64 0x0031u /* u64 */
#define DSU_TLV_STATE_PLAN_DIGEST64 0x0032u     /* u64 */

#define DSU_TLV_STATE_COMPONENT 0x0040u         /* container */
#define DSU_TLV_STATE_COMPONENT_VERSION 0x0041u /* u32 */
#define DSU_TLV_STATE_COMPONENT_ID 0x0042u      /* string */
#define DSU_TLV_STATE_COMPONENT_VERSTR 0x0043u  /* string */
#define DSU_TLV_STATE_COMPONENT_KIND 0x0044u    /* u8 */
#define DSU_TLV_STATE_COMPONENT_INSTALL_TIME_POLICY 0x0045u /* u64 */

#define DSU_TLV_STATE_COMPONENT_REGISTRATION 0x0046u /* string */
#define DSU_TLV_STATE_COMPONENT_MARKER 0x0047u       /* string */

#define DSU_TLV_STATE_FILE 0x0050u            /* container */
#define DSU_TLV_STATE_FILE_VERSION 0x0051u    /* u32 */
#define DSU_TLV_STATE_FILE_PATH 0x0052u       /* string (relative canonical) */
#define DSU_TLV_STATE_FILE_SHA256 0x0053u     /* bytes[32] (optional) */
#define DSU_TLV_STATE_FILE_SIZE 0x0054u       /* u64 */
#define DSU_TLV_STATE_FILE_DIGEST64 0x0055u   /* u64 */
#define DSU_TLV_STATE_FILE_ROOT_INDEX 0x0056u /* u32 */
#define DSU_TLV_STATE_FILE_OWNERSHIP 0x0057u  /* u8 */
#define DSU_TLV_STATE_FILE_FLAGS 0x0058u      /* u32 */

#define DSU_TLV_STATE_LAST_OPERATION 0x0060u          /* u8 */
#define DSU_TLV_STATE_LAST_JOURNAL_ID 0x0061u         /* u64 */
#define DSU_TLV_STATE_LAST_AUDIT_LOG_DIGEST64 0x0062u /* u64 */

typedef struct dsu_state_install_root_t {
    dsu_u8 role;
    dsu_u8 reserved8[3];
    char *path; /* absolute canonical DSU path */
} dsu_state_install_root_t;

typedef struct dsu_state_file_t {
    dsu_u32 root_index;
    dsu_u32 flags;
    dsu_u64 size;
    dsu_u64 digest64;
    dsu_u8 sha256[32];
    dsu_u8 ownership;
    dsu_u8 reserved8[3];
    char *path; /* relative canonical DSU path */
} dsu_state_file_t;

typedef struct dsu_state_component_t {
    char *id;
    char *version;
    dsu_u8 kind;
    dsu_u8 reserved8[3];
    dsu_u64 install_time_policy;

    dsu_u32 file_count;
    dsu_u32 file_cap;
    dsu_state_file_t *files;

    dsu_u32 registration_count;
    dsu_u32 registration_cap;
    char **registrations;

    dsu_u32 marker_count;
    dsu_u32 marker_cap;
    char **markers;
} dsu_state_component_t;

struct dsu_state {
    dsu_u32 root_version;

    char *product_id;
    char *product_version;
    char *build_channel;
    char *platform;

    dsu_u8 scope;
    dsu_u8 last_successful_operation;
    dsu_u8 has_last_audit_log_digest;
    dsu_u8 reserved8;

    dsu_u64 install_instance_id;
    dsu_u64 manifest_digest64;
    dsu_u64 resolved_digest64;
    dsu_u64 plan_digest64;

    dsu_u64 last_journal_id;
    dsu_u64 last_audit_log_digest64;

    dsu_u32 install_root_count;
    dsu_u32 install_root_cap;
    dsu_state_install_root_t *install_roots;

    dsu_u32 component_count;
    dsu_u32 component_cap;
    dsu_state_component_t *components;

    /* Flattened view for compatibility iteration. */
    dsu_u32 flat_file_count;
    dsu_state_file_t **flat_files;
};

struct dsu_state_diff {
    dsu_u32 added_component_count;
    dsu_u32 added_component_cap;
    char **added_components;

    dsu_u32 removed_component_count;
    dsu_u32 removed_component_cap;
    char **removed_components;

    dsu_u32 changed_component_count;
    dsu_u32 changed_component_cap;
    char **changed_components;

    dsu_u32 added_file_count;
    dsu_u32 added_file_cap;
    char **added_files;

    dsu_u32 removed_file_count;
    dsu_u32 removed_file_cap;
    char **removed_files;

    dsu_u32 modified_file_count;
    dsu_u32 modified_file_cap;
    char **modified_files;
};

static void dsu__str_list_free(char **items, dsu_u32 count) {
    dsu_u32 i;
    if (!items) return;
    for (i = 0u; i < count; ++i) {
        dsu__free(items[i]);
        items[i] = NULL;
    }
    dsu__free(items);
}

static dsu_status_t dsu__str_list_push(char ***io_items, dsu_u32 *io_count, dsu_u32 *io_cap, const char *s) {
    char **items;
    dsu_u32 count;
    dsu_u32 cap;
    dsu_u32 new_cap;
    char *dup;

    if (!io_items || !io_count || !io_cap) {
        return DSU_STATUS_INVALID_ARGS;
    }
    items = *io_items;
    count = *io_count;
    cap = *io_cap;
    if (!s) s = "";

    if (count == cap) {
        new_cap = (cap == 0u) ? 8u : (cap * 2u);
        items = (char **)dsu__realloc(items, new_cap * (dsu_u32)sizeof(*items));
        if (!items) {
            return DSU_STATUS_IO_ERROR;
        }
        cap = new_cap;
    }
    dup = dsu__strdup(s);
    if (!dup) {
        return DSU_STATUS_IO_ERROR;
    }
    items[count++] = dup;
    *io_items = items;
    *io_count = count;
    *io_cap = cap;
    return DSU_STATUS_SUCCESS;
}

static void dsu__state_install_root_free(dsu_state_install_root_t *r) {
    if (!r) return;
    dsu__free(r->path);
    memset(r, 0, sizeof(*r));
}

static void dsu__state_file_free(dsu_state_file_t *f) {
    if (!f) return;
    dsu__free(f->path);
    memset(f, 0, sizeof(*f));
}

static void dsu__state_component_free(dsu_state_component_t *c) {
    dsu_u32 i;
    if (!c) return;
    dsu__free(c->id);
    dsu__free(c->version);
    for (i = 0u; i < c->file_count; ++i) {
        dsu__state_file_free(&c->files[i]);
    }
    dsu__free(c->files);
    c->files = NULL;
    c->file_count = 0u;
    c->file_cap = 0u;
    dsu__str_list_free(c->registrations, c->registration_count);
    dsu__str_list_free(c->markers, c->marker_count);
    c->registrations = NULL;
    c->markers = NULL;
    c->registration_count = 0u;
    c->registration_cap = 0u;
    c->marker_count = 0u;
    c->marker_cap = 0u;
    c->install_time_policy = 0u;
    c->kind = 0u;
    memset(c->reserved8, 0, sizeof(c->reserved8));
}

static void dsu__state_free(dsu_state_t *s) {
    dsu_u32 i;
    if (!s) return;
    dsu__free(s->product_id);
    dsu__free(s->product_version);
    dsu__free(s->build_channel);
    dsu__free(s->platform);

    for (i = 0u; i < s->install_root_count; ++i) {
        dsu__state_install_root_free(&s->install_roots[i]);
    }
    dsu__free(s->install_roots);
    s->install_roots = NULL;
    s->install_root_count = 0u;
    s->install_root_cap = 0u;

    for (i = 0u; i < s->component_count; ++i) {
        dsu__state_component_free(&s->components[i]);
    }
    dsu__free(s->components);
    s->components = NULL;
    s->component_count = 0u;
    s->component_cap = 0u;

    dsu__free(s->flat_files);
    s->flat_files = NULL;
    s->flat_file_count = 0u;
}

static int dsu__is_alpha(char c) {
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z');
}

static int dsu__is_abs_path_like(const char *p) {
    if (!p) return 0;
    if (p[0] == '/' || p[0] == '\\') return 1;
    if ((p[0] == '/' && p[1] == '/') || (p[0] == '\\' && p[1] == '\\')) return 1;
    if (dsu__is_alpha(p[0]) && p[1] == ':' && (p[2] == '/' || p[2] == '\\')) return 1;
    return 0;
}

static dsu_status_t dsu__canon_abs_path(const char *in, char *out_abs, dsu_u32 out_abs_cap) {
    dsu_status_t st;
    if (!in || !out_abs || out_abs_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (in[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
    out_abs[0] = '\0';
    if (dsu__is_abs_path_like(in)) {
        st = dsu_fs_path_canonicalize(in, out_abs, out_abs_cap);
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
        if (!dsu__is_abs_path_like(out_abs)) {
            return DSU_STATUS_INVALID_ARGS;
        }
        return DSU_STATUS_SUCCESS;
    }
    {
        char cwd[1024];
        char joined[1024];
        st = dsu_platform_get_cwd(cwd, (dsu_u32)sizeof(cwd));
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
        st = dsu_fs_path_join(cwd, in, joined, (dsu_u32)sizeof(joined));
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
        st = dsu_fs_path_canonicalize(joined, out_abs, out_abs_cap);
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
        if (!dsu__is_abs_path_like(out_abs)) {
            return DSU_STATUS_INVALID_ARGS;
        }
        return DSU_STATUS_SUCCESS;
    }
}

static dsu_status_t dsu__canon_rel_path_alloc(const char *in, dsu_bool allow_empty, char **out_canon) {
    dsu_u32 i;
    dsu_u32 n;
    dsu_u32 o = 0u;
    dsu_u32 seg_start = 0u;
    char *buf;

    if (!out_canon) return DSU_STATUS_INVALID_ARGS;
    *out_canon = NULL;
    if (!in) return DSU_STATUS_INVALID_ARGS;
    if (in[0] == '\0') {
        if (allow_empty) {
            buf = (char *)dsu__malloc(1u);
            if (!buf) return DSU_STATUS_IO_ERROR;
            buf[0] = '\0';
            *out_canon = buf;
            return DSU_STATUS_SUCCESS;
        }
        return DSU_STATUS_INVALID_ARGS;
    }
    if (dsu__is_abs_path_like(in)) return DSU_STATUS_INVALID_ARGS;
    if (!dsu__is_ascii_printable(in)) return DSU_STATUS_INVALID_ARGS;
    if (strchr(in, ':') != NULL) return DSU_STATUS_INVALID_ARGS;

    n = dsu__strlen(in);
    if (n == 0xFFFFFFFFu) return DSU_STATUS_INVALID_ARGS;

    buf = (char *)dsu__malloc(n + 1u);
    if (!buf) return DSU_STATUS_IO_ERROR;

    for (i = 0u; i <= n; ++i) {
        char c = (i < n) ? in[i] : '\0';
        if (c == '\\') c = '/';
        if (c == '/' || c == '\0') {
            dsu_u32 seg_len = (dsu_u32)(i - seg_start);
            if (seg_len == 0u) {
                /* skip */
            } else if (seg_len == 1u && in[seg_start] == '.') {
                /* skip '.' */
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
    if (buf[0] == '\0' && !allow_empty) {
        dsu__free(buf);
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_canon = buf;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__install_root_push(dsu_state_t *s, const dsu_state_install_root_t *src) {
    dsu_u32 new_cap;
    dsu_state_install_root_t *p;
    if (!s || !src) return DSU_STATUS_INVALID_ARGS;
    if (s->install_root_count == s->install_root_cap) {
        new_cap = (s->install_root_cap == 0u) ? 4u : (s->install_root_cap * 2u);
        p = (dsu_state_install_root_t *)dsu__realloc(s->install_roots, new_cap * (dsu_u32)sizeof(*p));
        if (!p) return DSU_STATUS_IO_ERROR;
        if (new_cap > s->install_root_cap) {
            memset(p + s->install_root_cap, 0, (size_t)(new_cap - s->install_root_cap) * sizeof(*p));
        }
        s->install_roots = p;
        s->install_root_cap = new_cap;
    }
    s->install_roots[s->install_root_count++] = *src;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__component_push(dsu_state_t *s, const dsu_state_component_t *src) {
    dsu_u32 new_cap;
    dsu_state_component_t *p;
    if (!s || !src) return DSU_STATUS_INVALID_ARGS;
    if (s->component_count == s->component_cap) {
        new_cap = (s->component_cap == 0u) ? 8u : (s->component_cap * 2u);
        p = (dsu_state_component_t *)dsu__realloc(s->components, new_cap * (dsu_u32)sizeof(*p));
        if (!p) return DSU_STATUS_IO_ERROR;
        if (new_cap > s->component_cap) {
            memset(p + s->component_cap, 0, (size_t)(new_cap - s->component_cap) * sizeof(*p));
        }
        s->components = p;
        s->component_cap = new_cap;
    }
    s->components[s->component_count++] = *src;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__component_file_push(dsu_state_component_t *c, const dsu_state_file_t *src) {
    dsu_u32 new_cap;
    dsu_state_file_t *p;
    if (!c || !src) return DSU_STATUS_INVALID_ARGS;
    if (c->file_count == c->file_cap) {
        new_cap = (c->file_cap == 0u) ? 16u : (c->file_cap * 2u);
        p = (dsu_state_file_t *)dsu__realloc(c->files, new_cap * (dsu_u32)sizeof(*p));
        if (!p) return DSU_STATUS_IO_ERROR;
        if (new_cap > c->file_cap) {
            memset(p + c->file_cap, 0, (size_t)(new_cap - c->file_cap) * sizeof(*p));
        }
        c->files = p;
        c->file_cap = new_cap;
    }
    c->files[c->file_count++] = *src;
    return DSU_STATUS_SUCCESS;
}

static int dsu__cmp_str_ptr(const void *a, const void *b) {
    const char *sa = *(const char *const *)a;
    const char *sb = *(const char *const *)b;
    return dsu__strcmp_bytes(sa ? sa : "", sb ? sb : "");
}

static int dsu__cmp_install_root(const void *a, const void *b) {
    const dsu_state_install_root_t *ra = (const dsu_state_install_root_t *)a;
    const dsu_state_install_root_t *rb = (const dsu_state_install_root_t *)b;
    if (ra->role != rb->role) {
        return (ra->role < rb->role) ? -1 : 1;
    }
    return dsu__strcmp_bytes(ra->path ? ra->path : "", rb->path ? rb->path : "");
}

static int dsu__cmp_component(const void *a, const void *b) {
    const dsu_state_component_t *ca = (const dsu_state_component_t *)a;
    const dsu_state_component_t *cb = (const dsu_state_component_t *)b;
    return dsu__strcmp_bytes(ca->id ? ca->id : "", cb->id ? cb->id : "");
}

static int dsu__cmp_file_ptr(const void *a, const void *b) {
    const dsu_state_file_t *fa = *(dsu_state_file_t *const *)a;
    const dsu_state_file_t *fb = *(dsu_state_file_t *const *)b;
    if (fa->root_index != fb->root_index) {
        return (fa->root_index < fb->root_index) ? -1 : 1;
    }
    return dsu__strcmp_bytes(fa->path ? fa->path : "", fb->path ? fb->path : "");
}

static int dsu__cmp_file(const void *a, const void *b) {
    const dsu_state_file_t *fa = (const dsu_state_file_t *)a;
    const dsu_state_file_t *fb = (const dsu_state_file_t *)b;
    if (fa->root_index != fb->root_index) {
        return (fa->root_index < fb->root_index) ? -1 : 1;
    }
    return dsu__strcmp_bytes(fa->path ? fa->path : "", fb->path ? fb->path : "");
}

static dsu_u64 dsu__digest64_from_sha256(const dsu_u8 sha256[32]) {
    return dsu_digest64_bytes(sha256, 32u);
}

static dsu_u64 dsu__nonce64(dsu_ctx_t *ctx, dsu_u64 seed) {
    dsu_u64 t;
    dsu_u64 c;
    dsu_u64 v;
    if (ctx && (ctx->config.flags & DSU_CONFIG_FLAG_DETERMINISTIC)) {
        return seed;
    }
    t = (dsu_u64)(unsigned long)time(NULL);
    c = (dsu_u64)(unsigned long)clock();
    v = (t << 32) ^ (c & 0xFFFFFFFFu);
    return seed ^ v ^ (dsu_u64)0x9e3779b97f4a7c15ULL;
}

static dsu_status_t dsu__blob_put_tlv_u8(dsu_blob_t *b, dsu_u16 type, dsu_u8 v) {
    return dsu__blob_put_tlv(b, type, &v, 1u);
}

static dsu_status_t dsu__blob_put_tlv_u32(dsu_blob_t *b, dsu_u16 type, dsu_u32 v) {
    dsu_u8 tmp[4];
    tmp[0] = (dsu_u8)(v & 0xFFu);
    tmp[1] = (dsu_u8)((v >> 8) & 0xFFu);
    tmp[2] = (dsu_u8)((v >> 16) & 0xFFu);
    tmp[3] = (dsu_u8)((v >> 24) & 0xFFu);
    return dsu__blob_put_tlv(b, type, tmp, 4u);
}

static dsu_status_t dsu__blob_put_tlv_u64(dsu_blob_t *b, dsu_u16 type, dsu_u64 v) {
    dsu_u8 tmp[8];
    tmp[0] = (dsu_u8)(v & 0xFFu);
    tmp[1] = (dsu_u8)((v >> 8) & 0xFFu);
    tmp[2] = (dsu_u8)((v >> 16) & 0xFFu);
    tmp[3] = (dsu_u8)((v >> 24) & 0xFFu);
    tmp[4] = (dsu_u8)((v >> 32) & 0xFFu);
    tmp[5] = (dsu_u8)((v >> 40) & 0xFFu);
    tmp[6] = (dsu_u8)((v >> 48) & 0xFFu);
    tmp[7] = (dsu_u8)((v >> 56) & 0xFFu);
    return dsu__blob_put_tlv(b, type, tmp, 8u);
}

static dsu_status_t dsu__blob_put_tlv_str(dsu_blob_t *b, dsu_u16 type, const char *s) {
    dsu_u32 n;
    if (!s) s = "";
    n = dsu__strlen(s);
    if (n == 0xFFFFFFFFu) return DSU_STATUS_INVALID_ARGS;
    return dsu__blob_put_tlv(b, type, s, n);
}

static dsu_status_t dsu__dup_bytes_cstr(const dsu_u8 *bytes, dsu_u32 len, char **out_str) {
    char *s;
    dsu_u32 i;
    if (!out_str) return DSU_STATUS_INVALID_ARGS;
    *out_str = NULL;
    if (!bytes && len != 0u) return DSU_STATUS_INVALID_ARGS;
    s = (char *)dsu__malloc(len + 1u);
    if (!s) return DSU_STATUS_IO_ERROR;
    if (len) memcpy(s, bytes, (size_t)len);
    s[len] = '\0';
    for (i = 0u; i < len; ++i) {
        if (((unsigned char *)s)[i] == 0u) {
            dsu__free(s);
            return DSU_STATUS_PARSE_ERROR;
        }
    }
    *out_str = s;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__read_tlv_u8(const dsu_u8 *v, dsu_u32 len, dsu_u8 *out) {
    dsu_u32 off = 0u;
    if (!v || !out) return DSU_STATUS_INVALID_ARGS;
    if (len != 1u) return DSU_STATUS_INTEGRITY_ERROR;
    return dsu__read_u8(v, len, &off, out);
}

static dsu_status_t dsu__read_tlv_u32(const dsu_u8 *v, dsu_u32 len, dsu_u32 *out) {
    dsu_u32 off = 0u;
    if (!v || !out) return DSU_STATUS_INVALID_ARGS;
    if (len != 4u) return DSU_STATUS_INTEGRITY_ERROR;
    return dsu__read_u32le(v, len, &off, out);
}

static dsu_status_t dsu__read_tlv_u64(const dsu_u8 *v, dsu_u32 len, dsu_u64 *out) {
    dsu_u32 off = 0u;
    if (!v || !out) return DSU_STATUS_INVALID_ARGS;
    if (len != 8u) return DSU_STATUS_INTEGRITY_ERROR;
    return dsu__read_u64le(v, len, &off, out);
}

static dsu_u32 dsu__state_total_file_count(const dsu_state_t *s) {
    dsu_u32 total = 0u;
    dsu_u32 i;
    if (!s) return 0u;
    for (i = 0u; i < s->component_count; ++i) {
        if (total > 0xFFFFFFFFu - s->components[i].file_count) {
            return 0xFFFFFFFFu;
        }
        total += s->components[i].file_count;
    }
    return total;
}

dsu_status_t dsu_state_validate(dsu_state_t *state) {
    dsu_u32 i;
    dsu_u32 j;
    dsu_u32 total;

    if (!state) {
        return DSU_STATUS_INVALID_ARGS;
    }

    if (!state->product_id || state->product_id[0] == '\0') return DSU_STATUS_PARSE_ERROR;
    if (!state->product_version || state->product_version[0] == '\0') return DSU_STATUS_PARSE_ERROR;
    if (!state->build_channel) {
        state->build_channel = dsu__strdup("");
        if (!state->build_channel) return DSU_STATUS_IO_ERROR;
    }
    if (!state->platform || state->platform[0] == '\0') return DSU_STATUS_PARSE_ERROR;
    if (!dsu__is_ascii_printable(state->product_id)) return DSU_STATUS_PARSE_ERROR;
    if (!dsu__is_ascii_printable(state->product_version)) return DSU_STATUS_PARSE_ERROR;
    if (!dsu__is_ascii_printable(state->build_channel)) return DSU_STATUS_PARSE_ERROR;
    if (!dsu__is_ascii_printable(state->platform)) return DSU_STATUS_PARSE_ERROR;

    if (state->install_root_count == 0u) {
        return DSU_STATUS_PARSE_ERROR;
    }

    /* Canonicalize install roots and sort deterministically. */
    for (i = 0u; i < state->install_root_count; ++i) {
        char canon[1024];
        dsu_status_t st;
        char *dup;
        const char *p = state->install_roots[i].path ? state->install_roots[i].path : "";
        st = dsu_fs_path_canonicalize(p, canon, (dsu_u32)sizeof(canon));
        if (st != DSU_STATUS_SUCCESS) return st;
        if (!dsu__is_abs_path_like(canon)) return DSU_STATUS_PARSE_ERROR;
        if (dsu__strcmp_bytes(p, canon) != 0) {
            dup = dsu__strdup(canon);
            if (!dup) return DSU_STATUS_IO_ERROR;
            dsu__free(state->install_roots[i].path);
            state->install_roots[i].path = dup;
        }
    }
    if (state->install_root_count > 1u) {
        qsort(state->install_roots, (size_t)state->install_root_count, sizeof(*state->install_roots), dsu__cmp_install_root);
    }
    for (i = 1u; i < state->install_root_count; ++i) {
        if (state->install_roots[i - 1u].role == state->install_roots[i].role &&
            dsu__strcmp_bytes(state->install_roots[i - 1u].path, state->install_roots[i].path) == 0) {
            return DSU_STATUS_PARSE_ERROR;
        }
    }

    if (state->component_count > 1u) {
        qsort(state->components, (size_t)state->component_count, sizeof(*state->components), dsu__cmp_component);
    }
    for (i = 1u; i < state->component_count; ++i) {
        if (dsu__strcmp_bytes(state->components[i - 1u].id, state->components[i].id) == 0) {
            return DSU_STATUS_PARSE_ERROR;
        }
    }

    for (i = 0u; i < state->component_count; ++i) {
        dsu_state_component_t *c = &state->components[i];
        if (!c->id || c->id[0] == '\0') return DSU_STATUS_PARSE_ERROR;
        if (!c->version || c->version[0] == '\0') return DSU_STATUS_PARSE_ERROR;
        if (!dsu__is_ascii_printable(c->id)) return DSU_STATUS_PARSE_ERROR;
        if (!dsu__is_ascii_printable(c->version)) return DSU_STATUS_PARSE_ERROR;

        if (c->registration_count > 1u) {
            qsort(c->registrations, (size_t)c->registration_count, sizeof(*c->registrations), dsu__cmp_str_ptr);
        }
        for (j = 0u; j < c->registration_count; ++j) {
            if (!c->registrations[j]) return DSU_STATUS_PARSE_ERROR;
            if (!dsu__is_ascii_printable(c->registrations[j])) return DSU_STATUS_PARSE_ERROR;
        }

        if (c->marker_count > 1u) {
            qsort(c->markers, (size_t)c->marker_count, sizeof(*c->markers), dsu__cmp_str_ptr);
        }
        for (j = 0u; j < c->marker_count; ++j) {
            if (!c->markers[j]) return DSU_STATUS_PARSE_ERROR;
            if (!dsu__is_ascii_printable(c->markers[j])) return DSU_STATUS_PARSE_ERROR;
        }

        for (j = 0u; j < c->file_count; ++j) {
            dsu_state_file_t *f = &c->files[j];
            char *canon = NULL;
            dsu_status_t st;
            if (!f->path || f->path[0] == '\0') return DSU_STATUS_PARSE_ERROR;
            st = dsu__canon_rel_path_alloc(f->path, DSU_FALSE, &canon);
            if (st != DSU_STATUS_SUCCESS) return st;
            if (dsu__strcmp_bytes(f->path, canon) != 0) {
                dsu__free(f->path);
                f->path = canon;
            } else {
                dsu__free(canon);
            }
            if (f->root_index >= state->install_root_count) return DSU_STATUS_PARSE_ERROR;
            if (f->digest64 == 0u) {
                f->digest64 = dsu__digest64_from_sha256(f->sha256);
            }
        }
        if (c->file_count > 1u) {
            qsort(c->files, (size_t)c->file_count, sizeof(*c->files), dsu__cmp_file);
        }
        for (j = 1u; j < c->file_count; ++j) {
            if (c->files[j - 1u].root_index == c->files[j].root_index &&
                dsu__strcmp_bytes(c->files[j - 1u].path, c->files[j].path) == 0) {
                return DSU_STATUS_PARSE_ERROR;
            }
        }
    }

    /* Build flattened file view and check for overlaps across components. */
    total = dsu__state_total_file_count(state);
    if (total == 0xFFFFFFFFu) return DSU_STATUS_PARSE_ERROR;
    dsu__free(state->flat_files);
    state->flat_files = NULL;
    state->flat_file_count = 0u;
    if (total != 0u) {
        dsu_state_file_t **ptrs = (dsu_state_file_t **)dsu__malloc(total * (dsu_u32)sizeof(*ptrs));
        if (!ptrs) return DSU_STATUS_IO_ERROR;
        for (i = 0u; i < state->component_count; ++i) {
            dsu_state_component_t *c = &state->components[i];
            for (j = 0u; j < c->file_count; ++j) {
                ptrs[state->flat_file_count++] = &c->files[j];
            }
        }
        qsort(ptrs, (size_t)total, sizeof(*ptrs), dsu__cmp_file_ptr);
        for (i = 1u; i < total; ++i) {
            dsu_state_file_t *a = ptrs[i - 1u];
            dsu_state_file_t *b = ptrs[i];
            if (a->root_index == b->root_index && dsu__strcmp_bytes(a->path, b->path) == 0) {
                dsu__free(ptrs);
                return DSU_STATUS_PARSE_ERROR;
            }
        }
        state->flat_files = ptrs;
    }

    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__state_write_bytes(const dsu_state_t *state, dsu_blob_t *out_file_bytes) {
    dsu_blob_t root;
    dsu_blob_t payload;
    dsu_status_t st;
    dsu_u8 magic[4];
    dsu_u32 i;

    if (!state || !out_file_bytes) return DSU_STATUS_INVALID_ARGS;

    dsu__blob_init(out_file_bytes);
    dsu__blob_init(&root);
    dsu__blob_init(&payload);

    st = dsu__blob_put_tlv_u32(&root, (dsu_u16)DSU_TLV_STATE_ROOT_VERSION, DSU_STATE_ROOT_SCHEMA_VERSION);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&root, (dsu_u16)DSU_TLV_STATE_PRODUCT_ID, state->product_id);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&root, (dsu_u16)DSU_TLV_STATE_PRODUCT_VERSION, state->product_version);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&root, (dsu_u16)DSU_TLV_STATE_BUILD_CHANNEL, state->build_channel ? state->build_channel : "");
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&root, (dsu_u16)DSU_TLV_STATE_PLATFORM, state->platform);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&root, (dsu_u16)DSU_TLV_STATE_SCOPE, state->scope);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u64(&root, (dsu_u16)DSU_TLV_STATE_INSTALL_INSTANCE_ID, state->install_instance_id);

    /* Compatibility primary install root. */
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&root, (dsu_u16)DSU_TLV_STATE_INSTALL_ROOT, dsu_state_primary_install_root(state));

    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u64(&root, (dsu_u16)DSU_TLV_STATE_MANIFEST_DIGEST64, state->manifest_digest64);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u64(&root, (dsu_u16)DSU_TLV_STATE_RESOLVED_DIGEST64, state->resolved_digest64);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u64(&root, (dsu_u16)DSU_TLV_STATE_PLAN_DIGEST64, state->plan_digest64);

    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&root, (dsu_u16)DSU_TLV_STATE_LAST_OPERATION, state->last_successful_operation);
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u64(&root, (dsu_u16)DSU_TLV_STATE_LAST_JOURNAL_ID, state->last_journal_id);
    if (st == DSU_STATUS_SUCCESS && state->has_last_audit_log_digest) {
        st = dsu__blob_put_tlv_u64(&root, (dsu_u16)DSU_TLV_STATE_LAST_AUDIT_LOG_DIGEST64, state->last_audit_log_digest64);
    }

    for (i = 0u; st == DSU_STATUS_SUCCESS && i < state->install_root_count; ++i) {
        dsu_blob_t rb;
        dsu__blob_init(&rb);
        st = dsu__blob_put_tlv_u32(&rb, (dsu_u16)DSU_TLV_STATE_INSTALL_ROOT_VERSION, 1u);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&rb, (dsu_u16)DSU_TLV_STATE_INSTALL_ROOT_ROLE, state->install_roots[i].role);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&rb, (dsu_u16)DSU_TLV_STATE_INSTALL_ROOT_PATH, state->install_roots[i].path);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv(&root, (dsu_u16)DSU_TLV_STATE_INSTALL_ROOT_ITEM, rb.data, rb.size);
        dsu__blob_free(&rb);
    }

    for (i = 0u; st == DSU_STATUS_SUCCESS && i < state->component_count; ++i) {
        dsu_blob_t cb;
        dsu_u32 j;
        dsu_state_component_t *c = &state->components[i];
        dsu__blob_init(&cb);
        st = dsu__blob_put_tlv_u32(&cb, (dsu_u16)DSU_TLV_STATE_COMPONENT_VERSION, 2u);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&cb, (dsu_u16)DSU_TLV_STATE_COMPONENT_ID, c->id);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&cb, (dsu_u16)DSU_TLV_STATE_COMPONENT_VERSTR, c->version);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&cb, (dsu_u16)DSU_TLV_STATE_COMPONENT_KIND, c->kind);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u64(&cb, (dsu_u16)DSU_TLV_STATE_COMPONENT_INSTALL_TIME_POLICY, c->install_time_policy);

        for (j = 0u; st == DSU_STATUS_SUCCESS && j < c->registration_count; ++j) {
            st = dsu__blob_put_tlv_str(&cb, (dsu_u16)DSU_TLV_STATE_COMPONENT_REGISTRATION, c->registrations[j]);
        }
        for (j = 0u; st == DSU_STATUS_SUCCESS && j < c->marker_count; ++j) {
            st = dsu__blob_put_tlv_str(&cb, (dsu_u16)DSU_TLV_STATE_COMPONENT_MARKER, c->markers[j]);
        }

        for (j = 0u; st == DSU_STATUS_SUCCESS && j < c->file_count; ++j) {
            dsu_blob_t fb;
            dsu_state_file_t *f = &c->files[j];
            dsu__blob_init(&fb);
            st = dsu__blob_put_tlv_u32(&fb, (dsu_u16)DSU_TLV_STATE_FILE_VERSION, 2u);
            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u32(&fb, (dsu_u16)DSU_TLV_STATE_FILE_ROOT_INDEX, f->root_index);
            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&fb, (dsu_u16)DSU_TLV_STATE_FILE_PATH, f->path);
            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u64(&fb, (dsu_u16)DSU_TLV_STATE_FILE_DIGEST64, f->digest64);
            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u64(&fb, (dsu_u16)DSU_TLV_STATE_FILE_SIZE, f->size);
            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&fb, (dsu_u16)DSU_TLV_STATE_FILE_OWNERSHIP, f->ownership);
            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u32(&fb, (dsu_u16)DSU_TLV_STATE_FILE_FLAGS, f->flags);
            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv(&fb, (dsu_u16)DSU_TLV_STATE_FILE_SHA256, f->sha256, 32u);
            if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv(&cb, (dsu_u16)DSU_TLV_STATE_FILE, fb.data, fb.size);
            dsu__blob_free(&fb);
        }

        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv(&root, (dsu_u16)DSU_TLV_STATE_COMPONENT, cb.data, cb.size);
        dsu__blob_free(&cb);
    }

    if (st == DSU_STATUS_SUCCESS) {
        st = dsu__blob_put_tlv(&payload, (dsu_u16)DSU_TLV_STATE_ROOT, root.data, root.size);
    }
    dsu__blob_free(&root);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&payload);
        dsu__blob_free(out_file_bytes);
        return st;
    }

    magic[0] = (dsu_u8)DSU_STATE_MAGIC_0;
    magic[1] = (dsu_u8)DSU_STATE_MAGIC_1;
    magic[2] = (dsu_u8)DSU_STATE_MAGIC_2;
    magic[3] = (dsu_u8)DSU_STATE_MAGIC_3;

    st = dsu__file_wrap_payload(magic, (dsu_u16)DSU_STATE_FORMAT_VERSION, payload.data, payload.size, out_file_bytes);
    dsu__blob_free(&payload);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(out_file_bytes);
    }
    return st;
}

dsu_status_t dsu_state_save_atomic(dsu_ctx_t *ctx, const dsu_state_t *state, const char *path) {
    dsu_status_t st;
    dsu_blob_t bytes;
    char *tmp_path;
    dsu_u32 n;

    (void)ctx;
    if (!state || !path || path[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }

    /* Best-effort: canonicalize and sort in-place before writing. */
    st = dsu_state_validate((dsu_state_t *)state);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    st = dsu__state_write_bytes(state, &bytes);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    n = dsu__strlen(path);
    if (n == 0xFFFFFFFFu) {
        dsu__blob_free(&bytes);
        return DSU_STATUS_INVALID_ARGS;
    }
    tmp_path = (char *)dsu__malloc(n + 5u);
    if (!tmp_path) {
        dsu__blob_free(&bytes);
        return DSU_STATUS_IO_ERROR;
    }
    memcpy(tmp_path, path, (size_t)n);
    memcpy(tmp_path + n, ".tmp", 5u);

    st = dsu__fs_write_all(tmp_path, bytes.data, bytes.size);
    if (st == DSU_STATUS_SUCCESS) {
        st = dsu_platform_rename(tmp_path, path, 1u);
        if (st != DSU_STATUS_SUCCESS) {
            (void)dsu_platform_remove_file(tmp_path);
        }
    } else {
        (void)dsu_platform_remove_file(tmp_path);
    }

    dsu__free(tmp_path);
    dsu__blob_free(&bytes);
    return st;
}

static dsu_status_t dsu__state_parse_install_root_item(const dsu_u8 *buf, dsu_u32 len, dsu_state_install_root_t *out_root) {
    dsu_u32 off = 0u;
    dsu_status_t st = DSU_STATUS_SUCCESS;
    dsu_u32 version = 0u;
    dsu_state_install_root_t r;

    if (!buf || !out_root) return DSU_STATUS_INVALID_ARGS;
    memset(&r, 0, sizeof(r));

    while (off < len && st == DSU_STATUS_SUCCESS) {
        dsu_u16 t;
        dsu_u32 n;
        const dsu_u8 *v;
        st = dsu__tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) break;
        if (len - off < n) return DSU_STATUS_INTEGRITY_ERROR;
        v = buf + off;
        if (t == (dsu_u16)DSU_TLV_STATE_INSTALL_ROOT_VERSION) {
            st = dsu__read_tlv_u32(v, n, &version);
        } else if (t == (dsu_u16)DSU_TLV_STATE_INSTALL_ROOT_ROLE) {
            st = dsu__read_tlv_u8(v, n, &r.role);
        } else if (t == (dsu_u16)DSU_TLV_STATE_INSTALL_ROOT_PATH) {
            st = dsu__dup_bytes_cstr(v, n, &r.path);
        } else {
            /* skip */
        }
        off += n;
    }
    if (st != DSU_STATUS_SUCCESS) {
        dsu__state_install_root_free(&r);
        return st;
    }
    (void)version;
    if (!r.path || r.path[0] == '\0') {
        dsu__state_install_root_free(&r);
        return DSU_STATUS_PARSE_ERROR;
    }
    *out_root = r;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__state_parse_file(const dsu_u8 *buf, dsu_u32 len, dsu_state_file_t *out_file) {
    dsu_u32 off = 0u;
    dsu_status_t st = DSU_STATUS_SUCCESS;
    dsu_u32 version = 0u;
    dsu_state_file_t f;

    if (!buf || !out_file) return DSU_STATUS_INVALID_ARGS;
    memset(&f, 0, sizeof(f));
    f.ownership = (dsu_u8)DSU_STATE_FILE_OWNERSHIP_OWNED;

    while (off < len && st == DSU_STATUS_SUCCESS) {
        dsu_u16 t;
        dsu_u32 n;
        const dsu_u8 *v;
        st = dsu__tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) break;
        if (len - off < n) return DSU_STATUS_INTEGRITY_ERROR;
        v = buf + off;
        if (t == (dsu_u16)DSU_TLV_STATE_FILE_VERSION) {
            st = dsu__read_tlv_u32(v, n, &version);
        } else if (t == (dsu_u16)DSU_TLV_STATE_FILE_ROOT_INDEX) {
            st = dsu__read_tlv_u32(v, n, &f.root_index);
        } else if (t == (dsu_u16)DSU_TLV_STATE_FILE_PATH) {
            st = dsu__dup_bytes_cstr(v, n, &f.path);
        } else if (t == (dsu_u16)DSU_TLV_STATE_FILE_SHA256) {
            if (n != 32u) return DSU_STATUS_INTEGRITY_ERROR;
            memcpy(f.sha256, v, 32u);
        } else if (t == (dsu_u16)DSU_TLV_STATE_FILE_SIZE) {
            st = dsu__read_tlv_u64(v, n, &f.size);
        } else if (t == (dsu_u16)DSU_TLV_STATE_FILE_DIGEST64) {
            st = dsu__read_tlv_u64(v, n, &f.digest64);
        } else if (t == (dsu_u16)DSU_TLV_STATE_FILE_OWNERSHIP) {
            st = dsu__read_tlv_u8(v, n, &f.ownership);
        } else if (t == (dsu_u16)DSU_TLV_STATE_FILE_FLAGS) {
            st = dsu__read_tlv_u32(v, n, &f.flags);
        } else {
            /* skip */
        }
        off += n;
    }
    if (st != DSU_STATUS_SUCCESS) {
        dsu__state_file_free(&f);
        return st;
    }
    (void)version;
    if (!f.path || f.path[0] == '\0') {
        dsu__state_file_free(&f);
        return DSU_STATUS_PARSE_ERROR;
    }
    if (f.digest64 == 0u) {
        f.digest64 = dsu__digest64_from_sha256(f.sha256);
    }
    *out_file = f;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__state_parse_component(const dsu_u8 *buf, dsu_u32 len, dsu_state_component_t *out_comp) {
    dsu_u32 off = 0u;
    dsu_status_t st = DSU_STATUS_SUCCESS;
    dsu_u32 version = 0u;
    dsu_state_component_t c;

    if (!buf || !out_comp) return DSU_STATUS_INVALID_ARGS;
    memset(&c, 0, sizeof(c));
    c.kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER;

    while (off < len && st == DSU_STATUS_SUCCESS) {
        dsu_u16 t;
        dsu_u32 n;
        const dsu_u8 *v;
        st = dsu__tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) break;
        if (len - off < n) return DSU_STATUS_INTEGRITY_ERROR;
        v = buf + off;

        if (t == (dsu_u16)DSU_TLV_STATE_COMPONENT_VERSION) {
            st = dsu__read_tlv_u32(v, n, &version);
        } else if (t == (dsu_u16)DSU_TLV_STATE_COMPONENT_ID) {
            st = dsu__dup_bytes_cstr(v, n, &c.id);
        } else if (t == (dsu_u16)DSU_TLV_STATE_COMPONENT_VERSTR) {
            st = dsu__dup_bytes_cstr(v, n, &c.version);
        } else if (t == (dsu_u16)DSU_TLV_STATE_COMPONENT_KIND) {
            st = dsu__read_tlv_u8(v, n, &c.kind);
        } else if (t == (dsu_u16)DSU_TLV_STATE_COMPONENT_INSTALL_TIME_POLICY) {
            st = dsu__read_tlv_u64(v, n, &c.install_time_policy);
        } else if (t == (dsu_u16)DSU_TLV_STATE_COMPONENT_REGISTRATION) {
            char *tmp = NULL;
            st = dsu__dup_bytes_cstr(v, n, &tmp);
            if (st == DSU_STATUS_SUCCESS) {
                st = dsu__str_list_push(&c.registrations, &c.registration_count, &c.registration_cap, tmp);
                dsu__free(tmp);
            }
        } else if (t == (dsu_u16)DSU_TLV_STATE_COMPONENT_MARKER) {
            char *tmp = NULL;
            st = dsu__dup_bytes_cstr(v, n, &tmp);
            if (st == DSU_STATUS_SUCCESS) {
                st = dsu__str_list_push(&c.markers, &c.marker_count, &c.marker_cap, tmp);
                dsu__free(tmp);
            }
        } else if (t == (dsu_u16)DSU_TLV_STATE_FILE) {
            dsu_state_file_t f;
            memset(&f, 0, sizeof(f));
            st = dsu__state_parse_file(v, n, &f);
            if (st == DSU_STATUS_SUCCESS) {
                st = dsu__component_file_push(&c, &f);
                if (st != DSU_STATUS_SUCCESS) {
                    dsu__state_file_free(&f);
                }
            }
        } else {
            /* skip */
        }
        off += n;
    }

    if (st != DSU_STATUS_SUCCESS) {
        dsu__state_component_free(&c);
        return st;
    }

    (void)version;
    if (!c.id || c.id[0] == '\0' || !c.version || c.version[0] == '\0') {
        dsu__state_component_free(&c);
        return DSU_STATUS_PARSE_ERROR;
    }

    *out_comp = c;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__state_parse_root_v2(const dsu_u8 *buf, dsu_u32 len, dsu_state_t *s) {
    dsu_u32 off = 0u;
    dsu_status_t st = DSU_STATUS_SUCCESS;
    dsu_u32 root_version = 0u;
    char *primary_root = NULL;

    if (!buf || !s) return DSU_STATUS_INVALID_ARGS;

    while (off < len && st == DSU_STATUS_SUCCESS) {
        dsu_u16 t;
        dsu_u32 n;
        const dsu_u8 *v;
        st = dsu__tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) break;
        if (len - off < n) return DSU_STATUS_INTEGRITY_ERROR;
        v = buf + off;

        if (t == (dsu_u16)DSU_TLV_STATE_ROOT_VERSION) {
            st = dsu__read_tlv_u32(v, n, &root_version);
        } else if (t == (dsu_u16)DSU_TLV_STATE_PRODUCT_ID) {
            st = dsu__dup_bytes_cstr(v, n, &s->product_id);
        } else if (t == (dsu_u16)DSU_TLV_STATE_PRODUCT_VERSION) {
            st = dsu__dup_bytes_cstr(v, n, &s->product_version);
        } else if (t == (dsu_u16)DSU_TLV_STATE_BUILD_CHANNEL) {
            st = dsu__dup_bytes_cstr(v, n, &s->build_channel);
        } else if (t == (dsu_u16)DSU_TLV_STATE_PLATFORM) {
            st = dsu__dup_bytes_cstr(v, n, &s->platform);
        } else if (t == (dsu_u16)DSU_TLV_STATE_SCOPE) {
            st = dsu__read_tlv_u8(v, n, &s->scope);
        } else if (t == (dsu_u16)DSU_TLV_STATE_INSTALL_INSTANCE_ID) {
            st = dsu__read_tlv_u64(v, n, &s->install_instance_id);
        } else if (t == (dsu_u16)DSU_TLV_STATE_INSTALL_ROOT) {
            st = dsu__dup_bytes_cstr(v, n, &primary_root);
        } else if (t == (dsu_u16)DSU_TLV_STATE_INSTALL_ROOT_ITEM) {
            dsu_state_install_root_t r;
            memset(&r, 0, sizeof(r));
            st = dsu__state_parse_install_root_item(v, n, &r);
            if (st == DSU_STATUS_SUCCESS) {
                st = dsu__install_root_push(s, &r);
                if (st != DSU_STATUS_SUCCESS) {
                    dsu__state_install_root_free(&r);
                }
            }
        } else if (t == (dsu_u16)DSU_TLV_STATE_MANIFEST_DIGEST64) {
            st = dsu__read_tlv_u64(v, n, &s->manifest_digest64);
        } else if (t == (dsu_u16)DSU_TLV_STATE_RESOLVED_DIGEST64) {
            st = dsu__read_tlv_u64(v, n, &s->resolved_digest64);
        } else if (t == (dsu_u16)DSU_TLV_STATE_PLAN_DIGEST64) {
            st = dsu__read_tlv_u64(v, n, &s->plan_digest64);
        } else if (t == (dsu_u16)DSU_TLV_STATE_LAST_OPERATION) {
            st = dsu__read_tlv_u8(v, n, &s->last_successful_operation);
        } else if (t == (dsu_u16)DSU_TLV_STATE_LAST_JOURNAL_ID) {
            st = dsu__read_tlv_u64(v, n, &s->last_journal_id);
        } else if (t == (dsu_u16)DSU_TLV_STATE_LAST_AUDIT_LOG_DIGEST64) {
            st = dsu__read_tlv_u64(v, n, &s->last_audit_log_digest64);
            if (st == DSU_STATUS_SUCCESS) s->has_last_audit_log_digest = 1u;
        } else if (t == (dsu_u16)DSU_TLV_STATE_COMPONENT) {
            dsu_state_component_t c;
            memset(&c, 0, sizeof(c));
            st = dsu__state_parse_component(v, n, &c);
            if (st == DSU_STATUS_SUCCESS) {
                st = dsu__component_push(s, &c);
                if (st != DSU_STATUS_SUCCESS) {
                    dsu__state_component_free(&c);
                }
            }
        } else {
            /* skip */
        }
        off += n;
    }

    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(primary_root);
        return st;
    }

    s->root_version = root_version;
    if (s->root_version < 1u) {
        dsu__free(primary_root);
        return DSU_STATUS_PARSE_ERROR;
    }

    if (s->install_root_count == 0u) {
        if (primary_root && primary_root[0] != '\0') {
            dsu_state_install_root_t r;
            memset(&r, 0, sizeof(r));
            r.role = (dsu_u8)DSU_STATE_INSTALL_ROOT_ROLE_PRIMARY;
            r.path = primary_root;
            primary_root = NULL;
            st = dsu__install_root_push(s, &r);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__state_install_root_free(&r);
                dsu__free(primary_root);
                return st;
            }
        } else {
            dsu__free(primary_root);
            return DSU_STATUS_PARSE_ERROR;
        }
    }

    /* Ensure there is a primary install root role. */
    {
        dsu_u8 found = 0u;
        for (off = 0u; off < s->install_root_count; ++off) {
            if (s->install_roots[off].role == (dsu_u8)DSU_STATE_INSTALL_ROOT_ROLE_PRIMARY) {
                found = 1u;
                break;
            }
        }
        if (!found && s->install_root_count != 0u) {
            s->install_roots[0].role = (dsu_u8)DSU_STATE_INSTALL_ROOT_ROLE_PRIMARY;
        }
    }

    dsu__free(primary_root);
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__state_parse_root_v1(const dsu_u8 *buf, dsu_u32 len, dsu_state_t *s) {
    dsu_u32 off = 0u;
    dsu_status_t st = DSU_STATUS_SUCCESS;
    dsu_u32 root_version = 0u;
    char *install_root = NULL;

    if (!buf || !s) return DSU_STATUS_INVALID_ARGS;

    while (off < len && st == DSU_STATUS_SUCCESS) {
        dsu_u16 t;
        dsu_u32 n;
        const dsu_u8 *v;
        st = dsu__tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) break;
        if (len - off < n) return DSU_STATUS_INTEGRITY_ERROR;
        v = buf + off;

        if (t == (dsu_u16)DSU_TLV_STATE_ROOT_VERSION) {
            st = dsu__read_tlv_u32(v, n, &root_version);
        } else if (t == (dsu_u16)DSU_TLV_STATE_PRODUCT_ID) {
            st = dsu__dup_bytes_cstr(v, n, &s->product_id);
        } else if (t == (dsu_u16)DSU_TLV_STATE_PRODUCT_VERSION) {
            st = dsu__dup_bytes_cstr(v, n, &s->product_version);
        } else if (t == (dsu_u16)DSU_TLV_STATE_PLATFORM) {
            st = dsu__dup_bytes_cstr(v, n, &s->platform);
        } else if (t == (dsu_u16)DSU_TLV_STATE_SCOPE) {
            st = dsu__read_tlv_u8(v, n, &s->scope);
        } else if (t == (dsu_u16)DSU_TLV_STATE_INSTALL_ROOT) {
            st = dsu__dup_bytes_cstr(v, n, &install_root);
        } else if (t == (dsu_u16)DSU_TLV_STATE_COMPONENT) {
            dsu_state_component_t c;
            memset(&c, 0, sizeof(c));
            st = dsu__state_parse_component(v, n, &c);
            if (st == DSU_STATUS_SUCCESS) {
                st = dsu__component_push(s, &c);
                if (st != DSU_STATUS_SUCCESS) {
                    dsu__state_component_free(&c);
                }
            }
        } else if (t == (dsu_u16)DSU_TLV_STATE_FILE) {
            /* v1 allowed files at root; attach to first component if present. */
            dsu_state_file_t f;
            memset(&f, 0, sizeof(f));
            st = dsu__state_parse_file(v, n, &f);
            if (st == DSU_STATUS_SUCCESS) {
                if (s->component_count == 0u) {
                    dsu_state_component_t c;
                    memset(&c, 0, sizeof(c));
                    c.id = dsu__strdup("legacy");
                    c.version = dsu__strdup(s->product_version ? s->product_version : "0");
                    c.kind = (dsu_u8)DSU_MANIFEST_COMPONENT_KIND_OTHER;
                    c.install_time_policy = 0u;
                    if (!c.id || !c.version) {
                        dsu__state_component_free(&c);
                        dsu__state_file_free(&f);
                        dsu__free(install_root);
                        return DSU_STATUS_IO_ERROR;
                    }
                    st = dsu__component_push(s, &c);
                    if (st != DSU_STATUS_SUCCESS) {
                        dsu__state_component_free(&c);
                        dsu__state_file_free(&f);
                        dsu__free(install_root);
                        return st;
                    }
                }
                st = dsu__component_file_push(&s->components[0], &f);
                if (st != DSU_STATUS_SUCCESS) {
                    dsu__state_file_free(&f);
                }
            }
        } else {
            /* skip */
        }
        off += n;
    }

    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(install_root);
        return st;
    }

    s->root_version = root_version;
    if (!s->build_channel) {
        s->build_channel = dsu__strdup("");
        if (!s->build_channel) {
            dsu__free(install_root);
            return DSU_STATUS_IO_ERROR;
        }
    }

    if (install_root && install_root[0] != '\0') {
        dsu_state_install_root_t r;
        memset(&r, 0, sizeof(r));
        r.role = (dsu_u8)DSU_STATE_INSTALL_ROOT_ROLE_PRIMARY;
        r.path = install_root;
        install_root = NULL;
        st = dsu__install_root_push(s, &r);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__state_install_root_free(&r);
            dsu__free(install_root);
            return st;
        }
    }
    dsu__free(install_root);
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_state_load(dsu_ctx_t *ctx, const char *path, dsu_state_t **out_state) {
    dsu_status_t st;
    dsu_u8 *file_bytes = NULL;
    dsu_u32 file_len = 0u;
    dsu_u8 magic[4];
    const dsu_u8 *payload = NULL;
    dsu_u32 payload_len = 0u;
    dsu_state_t *s;
    dsu_u16 ver;
    dsu_u32 off;

    if (!ctx || !path || !out_state) return DSU_STATUS_INVALID_ARGS;
    *out_state = NULL;

    st = dsu__fs_read_all(&ctx->config, path, &file_bytes, &file_len);
    if (st != DSU_STATUS_SUCCESS) return st;
    if (file_len < DSU_FILE_HEADER_BASE_SIZE) {
        dsu__free(file_bytes);
        return DSU_STATUS_INTEGRITY_ERROR;
    }

    if (file_bytes[0] != (dsu_u8)DSU_STATE_MAGIC_0 ||
        file_bytes[1] != (dsu_u8)DSU_STATE_MAGIC_1 ||
        file_bytes[2] != (dsu_u8)DSU_STATE_MAGIC_2 ||
        file_bytes[3] != (dsu_u8)DSU_STATE_MAGIC_3) {
        dsu__free(file_bytes);
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    ver = (dsu_u16)((dsu_u16)file_bytes[4] | ((dsu_u16)file_bytes[5] << 8));

    magic[0] = (dsu_u8)DSU_STATE_MAGIC_0;
    magic[1] = (dsu_u8)DSU_STATE_MAGIC_1;
    magic[2] = (dsu_u8)DSU_STATE_MAGIC_2;
    magic[3] = (dsu_u8)DSU_STATE_MAGIC_3;

    if (ver == 1u) {
        st = dsu__file_unwrap_payload(file_bytes, file_len, magic, (dsu_u16)1u, &payload, &payload_len);
    } else {
        st = dsu__file_unwrap_payload(file_bytes, file_len, magic, (dsu_u16)DSU_STATE_FORMAT_VERSION, &payload, &payload_len);
    }
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(file_bytes);
        return st;
    }

    s = (dsu_state_t *)dsu__malloc((dsu_u32)sizeof(*s));
    if (!s) {
        dsu__free(file_bytes);
        return DSU_STATUS_IO_ERROR;
    }
    memset(s, 0, sizeof(*s));
    s->root_version = DSU_STATE_ROOT_SCHEMA_VERSION;
    s->last_successful_operation = (dsu_u8)DSU_STATE_OPERATION_INSTALL;

    off = 0u;
    while (off < payload_len && st == DSU_STATUS_SUCCESS) {
        dsu_u16 t;
        dsu_u32 n;
        const dsu_u8 *v;
        st = dsu__tlv_read_header(payload, payload_len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) break;
        if (payload_len - off < n) {
            st = DSU_STATUS_INTEGRITY_ERROR;
            break;
        }
        v = payload + off;
        if (t == (dsu_u16)DSU_TLV_STATE_ROOT) {
            if (ver == 1u) st = dsu__state_parse_root_v1(v, n, s);
            else st = dsu__state_parse_root_v2(v, n, s);
        }
        off += n;
    }

    dsu__free(file_bytes);
    file_bytes = NULL;

    if (st != DSU_STATUS_SUCCESS) {
        dsu_state_destroy(ctx, s);
        return st;
    }

    st = dsu_state_validate(s);
    if (st != DSU_STATUS_SUCCESS) {
        dsu_state_destroy(ctx, s);
        return st;
    }

    *out_state = s;
    return DSU_STATUS_SUCCESS;
}

static void dsu__state_diff_free(dsu_state_diff_t *d) {
    if (!d) return;
    dsu__str_list_free(d->added_components, d->added_component_count);
    dsu__str_list_free(d->removed_components, d->removed_component_count);
    dsu__str_list_free(d->changed_components, d->changed_component_count);
    dsu__str_list_free(d->added_files, d->added_file_count);
    dsu__str_list_free(d->removed_files, d->removed_file_count);
    dsu__str_list_free(d->modified_files, d->modified_file_count);
    memset(d, 0, sizeof(*d));
}

dsu_status_t dsu_state_diff(const dsu_state_t *old_state,
                           const dsu_state_t *new_state,
                           dsu_state_diff_t **out_diff) {
    dsu_state_diff_t *d;
    dsu_u32 i = 0u;
    dsu_u32 j = 0u;
    dsu_status_t st = DSU_STATUS_SUCCESS;

    if (!old_state || !new_state || !out_diff) return DSU_STATUS_INVALID_ARGS;
    *out_diff = NULL;

    d = (dsu_state_diff_t *)dsu__malloc((dsu_u32)sizeof(*d));
    if (!d) return DSU_STATUS_IO_ERROR;
    memset(d, 0, sizeof(*d));

    while (st == DSU_STATUS_SUCCESS && (i < old_state->component_count || j < new_state->component_count)) {
        const dsu_state_component_t *co = (i < old_state->component_count) ? &old_state->components[i] : NULL;
        const dsu_state_component_t *cn = (j < new_state->component_count) ? &new_state->components[j] : NULL;
        int cmp;

        if (!co) {
            st = dsu__str_list_push(&d->added_components, &d->added_component_count, &d->added_component_cap, cn->id);
            if (st != DSU_STATUS_SUCCESS) break;
            for (cmp = 0; st == DSU_STATUS_SUCCESS && (dsu_u32)cmp < cn->file_count; ++cmp) {
                st = dsu__str_list_push(&d->added_files, &d->added_file_count, &d->added_file_cap, cn->files[cmp].path);
            }
            ++j;
            continue;
        }
        if (!cn) {
            st = dsu__str_list_push(&d->removed_components, &d->removed_component_count, &d->removed_component_cap, co->id);
            if (st != DSU_STATUS_SUCCESS) break;
            for (cmp = 0; st == DSU_STATUS_SUCCESS && (dsu_u32)cmp < co->file_count; ++cmp) {
                st = dsu__str_list_push(&d->removed_files, &d->removed_file_count, &d->removed_file_cap, co->files[cmp].path);
            }
            ++i;
            continue;
        }

        cmp = dsu__strcmp_bytes(co->id ? co->id : "", cn->id ? cn->id : "");
        if (cmp < 0) {
            st = dsu__str_list_push(&d->removed_components, &d->removed_component_count, &d->removed_component_cap, co->id);
            if (st != DSU_STATUS_SUCCESS) break;
            for (cmp = 0; st == DSU_STATUS_SUCCESS && (dsu_u32)cmp < co->file_count; ++cmp) {
                st = dsu__str_list_push(&d->removed_files, &d->removed_file_count, &d->removed_file_cap, co->files[cmp].path);
            }
            ++i;
            continue;
        }
        if (cmp > 0) {
            st = dsu__str_list_push(&d->added_components, &d->added_component_count, &d->added_component_cap, cn->id);
            if (st != DSU_STATUS_SUCCESS) break;
            for (cmp = 0; st == DSU_STATUS_SUCCESS && (dsu_u32)cmp < cn->file_count; ++cmp) {
                st = dsu__str_list_push(&d->added_files, &d->added_file_count, &d->added_file_cap, cn->files[cmp].path);
            }
            ++j;
            continue;
        }

        /* Same component id: compare metadata + file set. */
        {
            dsu_u32 fo = 0u;
            dsu_u32 fn = 0u;
            dsu_bool changed = 0;

            if (dsu__strcmp_bytes(co->version ? co->version : "", cn->version ? cn->version : "") != 0) changed = 1;
            if (co->kind != cn->kind) changed = 1;

            while (st == DSU_STATUS_SUCCESS && (fo < co->file_count || fn < cn->file_count)) {
                const dsu_state_file_t *a = (fo < co->file_count) ? &co->files[fo] : NULL;
                const dsu_state_file_t *b = (fn < cn->file_count) ? &cn->files[fn] : NULL;
                int fcmp;

                if (!a) {
                    st = dsu__str_list_push(&d->added_files, &d->added_file_count, &d->added_file_cap, b->path);
                    ++fn;
                    continue;
                }
                if (!b) {
                    st = dsu__str_list_push(&d->removed_files, &d->removed_file_count, &d->removed_file_cap, a->path);
                    ++fo;
                    continue;
                }

                fcmp = (a->root_index != b->root_index) ? ((a->root_index < b->root_index) ? -1 : 1)
                                                       : dsu__strcmp_bytes(a->path ? a->path : "", b->path ? b->path : "");
                if (fcmp < 0) {
                    st = dsu__str_list_push(&d->removed_files, &d->removed_file_count, &d->removed_file_cap, a->path);
                    ++fo;
                    changed = 1;
                    continue;
                }
                if (fcmp > 0) {
                    st = dsu__str_list_push(&d->added_files, &d->added_file_count, &d->added_file_cap, b->path);
                    ++fn;
                    changed = 1;
                    continue;
                }

                if (a->size != b->size || a->digest64 != b->digest64 || a->ownership != b->ownership || a->flags != b->flags) {
                    st = dsu__str_list_push(&d->modified_files, &d->modified_file_count, &d->modified_file_cap, a->path);
                    changed = 1;
                }
                ++fo;
                ++fn;
            }

            if (st == DSU_STATUS_SUCCESS && changed) {
                st = dsu__str_list_push(&d->changed_components, &d->changed_component_count, &d->changed_component_cap, co->id);
            }
        }

        ++i;
        ++j;
    }

    if (st != DSU_STATUS_SUCCESS) {
        dsu__state_diff_free(d);
        dsu__free(d);
        return st;
    }
    *out_diff = d;
    return DSU_STATUS_SUCCESS;
}

void dsu_state_diff_destroy(dsu_ctx_t *ctx, dsu_state_diff_t *diff) {
    (void)ctx;
    if (!diff) return;
    dsu__state_diff_free(diff);
    dsu__free(diff);
}

dsu_status_t dsu__state_build_from_plan(dsu_ctx_t *ctx,
                                       const dsu_plan_t *plan,
                                       const dsu_state_t *prev_state,
                                       dsu_u64 last_journal_id,
                                       dsu_bool has_last_audit_log_digest64,
                                       dsu_u64 last_audit_log_digest64,
                                       dsu_state_t **out_state) {
    dsu_state_t *s;
    dsu_u32 i;
    dsu_u32 ccount;
    dsu_u32 fcount;
    dsu_status_t st;

    if (!ctx || !plan || !out_state) return DSU_STATUS_INVALID_ARGS;
    *out_state = NULL;

    /* Uninstall builds the post-uninstall installed-state by removing the plan's component set. */
    if (dsu_plan_operation(plan) == DSU_RESOLVE_OPERATION_UNINSTALL) {
        dsu_u32 plan_ccount;
        dsu_u32 prev_ccount;
        dsu_u8 *remove = NULL;
        dsu_u32 kept = 0u;
        dsu_u32 j;

        if (!prev_state) {
            return DSU_STATUS_INVALID_REQUEST;
        }
        if (dsu__strcmp_bytes(dsu_state_product_id(prev_state), dsu_plan_product_id(plan)) != 0) {
            return DSU_STATUS_INVALID_REQUEST;
        }
        if ((dsu_u8)dsu_state_install_scope(prev_state) != (dsu_u8)dsu_plan_scope(plan)) {
            return DSU_STATUS_INVALID_REQUEST;
        }
        if (dsu__strcmp_bytes(dsu_state_platform(prev_state), dsu_plan_platform(plan)) != 0) {
            return DSU_STATUS_PLATFORM_INCOMPATIBLE;
        }

        plan_ccount = dsu_plan_component_count(plan);
        prev_ccount = dsu_state_component_count(prev_state);

        remove = (dsu_u8 *)dsu__malloc(prev_ccount);
        if (!remove && prev_ccount != 0u) {
            return DSU_STATUS_IO_ERROR;
        }
        if (prev_ccount) {
            memset(remove, 0, prev_ccount);
        }

        /* Mark removed components (merge-walk: both lists are canonical and sorted by ID). */
        i = 0u;
        j = 0u;
        while (i < prev_ccount && j < plan_ccount) {
            const char *prev_id = dsu_state_component_id(prev_state, i);
            const char *plan_id = dsu_plan_component_id(plan, j);
            int cmp = dsu__strcmp_bytes(prev_id ? prev_id : "", plan_id ? plan_id : "");
            if (cmp == 0) {
                remove[i] = 1u;
                ++i;
                ++j;
            } else if (cmp < 0) {
                ++i;
            } else {
                /* Plan references a component not present in the installed-state. */
                dsu__free(remove);
                return DSU_STATUS_INVALID_REQUEST;
            }
        }
        if (j != plan_ccount) {
            dsu__free(remove);
            return DSU_STATUS_INVALID_REQUEST;
        }

        for (i = 0u; i < prev_ccount; ++i) {
            if (!remove[i]) {
                ++kept;
            }
        }

        s = (dsu_state_t *)dsu__malloc((dsu_u32)sizeof(*s));
        if (!s) {
            dsu__free(remove);
            return DSU_STATUS_IO_ERROR;
        }
        memset(s, 0, sizeof(*s));

        s->root_version = DSU_STATE_ROOT_SCHEMA_VERSION;
        s->product_id = dsu__strdup(dsu_state_product_id(prev_state));
        s->product_version = dsu__strdup(dsu_state_product_version_installed(prev_state));
        s->build_channel = dsu__strdup(dsu_state_build_channel(prev_state));
        s->platform = dsu__strdup(dsu_state_platform(prev_state));
        s->scope = (dsu_u8)dsu_state_install_scope(prev_state);

        s->manifest_digest64 = dsu_plan_manifest_digest64(plan);
        s->plan_digest64 = dsu_plan_id_hash64(plan);

        s->last_successful_operation = (dsu_u8)DSU_STATE_OPERATION_UNINSTALL;
        s->last_journal_id = last_journal_id;
        s->has_last_audit_log_digest = (dsu_u8)(has_last_audit_log_digest64 ? 1u : 0u);
        s->last_audit_log_digest64 = last_audit_log_digest64;

        if (!s->product_id || !s->product_version || !s->build_channel || !s->platform) {
            dsu_state_destroy(ctx, s);
            dsu__free(remove);
            return DSU_STATUS_IO_ERROR;
        }

        s->install_instance_id = dsu_state_install_instance_id(prev_state);
        if (s->install_instance_id == 0u) {
            s->install_instance_id = dsu__nonce64(ctx, s->plan_digest64);
        }

        /* Copy install roots. */
        for (i = 0u; i < dsu_state_install_root_count(prev_state); ++i) {
            dsu_state_install_root_t r;
            memset(&r, 0, sizeof(r));
            r.role = (dsu_u8)dsu_state_install_root_role(prev_state, i);
            r.path = dsu__strdup(dsu_state_install_root_path(prev_state, i));
            if (!r.path) {
                dsu_state_destroy(ctx, s);
                dsu__free(remove);
                return DSU_STATUS_IO_ERROR;
            }
            st = dsu__install_root_push(s, &r);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__state_install_root_free(&r);
                dsu_state_destroy(ctx, s);
                dsu__free(remove);
                return st;
            }
            memset(&r, 0, sizeof(r));
        }

        /* Copy kept components, their files, and platform metadata. */
        for (i = 0u; i < prev_ccount; ++i) {
            dsu_state_component_t c;
            dsu_u32 fi;
            dsu_u32 ri;
            dsu_u32 mi;

            if (remove[i]) {
                continue;
            }

            memset(&c, 0, sizeof(c));
            c.id = dsu__strdup(dsu_state_component_id(prev_state, i));
            c.version = dsu__strdup(dsu_state_component_version(prev_state, i));
            c.kind = (dsu_u8)dsu_state_component_kind(prev_state, i);
            c.install_time_policy = dsu_state_component_install_time_policy(prev_state, i);
            if (!c.id || !c.version) {
                dsu__state_component_free(&c);
                dsu_state_destroy(ctx, s);
                dsu__free(remove);
                return DSU_STATUS_IO_ERROR;
            }

            for (ri = 0u; ri < dsu_state_component_registration_count(prev_state, i); ++ri) {
                st = dsu__str_list_push(&c.registrations, &c.registration_count, &c.registration_cap,
                                        dsu_state_component_registration(prev_state, i, ri));
                if (st != DSU_STATUS_SUCCESS) {
                    dsu__state_component_free(&c);
                    dsu_state_destroy(ctx, s);
                    dsu__free(remove);
                    return st;
                }
            }
            for (mi = 0u; mi < dsu_state_component_marker_count(prev_state, i); ++mi) {
                st = dsu__str_list_push(&c.markers, &c.marker_count, &c.marker_cap,
                                        dsu_state_component_marker(prev_state, i, mi));
                if (st != DSU_STATUS_SUCCESS) {
                    dsu__state_component_free(&c);
                    dsu_state_destroy(ctx, s);
                    dsu__free(remove);
                    return st;
                }
            }

            for (fi = 0u; fi < dsu_state_component_file_count(prev_state, i); ++fi) {
                dsu_state_file_t f;
                const dsu_state_file_t *srcf;
                memset(&f, 0, sizeof(f));
                if (i >= prev_state->component_count || fi >= prev_state->components[i].file_count) {
                    dsu__state_component_free(&c);
                    dsu_state_destroy(ctx, s);
                    dsu__free(remove);
                    return DSU_STATUS_INTEGRITY_ERROR;
                }
                srcf = &prev_state->components[i].files[fi];
                f.root_index = srcf->root_index;
                f.flags = srcf->flags;
                f.size = srcf->size;
                f.digest64 = srcf->digest64;
                f.ownership = srcf->ownership;
                memcpy(f.sha256, srcf->sha256, 32u);
                f.path = dsu__strdup(srcf->path ? srcf->path : "");
                if (!f.path) {
                    dsu__state_component_free(&c);
                    dsu_state_destroy(ctx, s);
                    dsu__free(remove);
                    return DSU_STATUS_IO_ERROR;
                }
                if (f.path[0] == '\0') {
                    dsu__state_file_free(&f);
                    dsu__state_component_free(&c);
                    dsu_state_destroy(ctx, s);
                    dsu__free(remove);
                    return DSU_STATUS_INTEGRITY_ERROR;
                }
                st = dsu__component_file_push(&c, &f);
                if (st != DSU_STATUS_SUCCESS) {
                    dsu__state_file_free(&f);
                    dsu__state_component_free(&c);
                    dsu_state_destroy(ctx, s);
                    dsu__free(remove);
                    return st;
                }
                memset(&f, 0, sizeof(f));
            }

            st = dsu__component_push(s, &c);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__state_component_free(&c);
                dsu_state_destroy(ctx, s);
                dsu__free(remove);
                return st;
            }
            memset(&c, 0, sizeof(c));
        }

        dsu__free(remove);
        remove = NULL;

        st = dsu_state_validate(s);
        if (st != DSU_STATUS_SUCCESS) {
            dsu_state_destroy(ctx, s);
            return st;
        }

        /* Recompute resolved set digest for the remaining installed components. */
        {
            dsu_u64 h = dsu_digest64_init();
            dsu_u8 sep = 0u;
            const char *plat = s->platform ? s->platform : "";
            h = dsu_digest64_update(h, plat, dsu__strlen(plat));
            h = dsu_digest64_update(h, &sep, 1u);
            h = dsu_digest64_update(h, &s->scope, 1u);
            h = dsu_digest64_update(h, &sep, 1u);
            for (i = 0u; i < s->component_count; ++i) {
                const char *cid = s->components[i].id ? s->components[i].id : "";
                const char *cver = s->components[i].version ? s->components[i].version : "";
                h = dsu_digest64_update(h, cid, dsu__strlen(cid));
                h = dsu_digest64_update(h, &sep, 1u);
                h = dsu_digest64_update(h, cver, dsu__strlen(cver));
                h = dsu_digest64_update(h, &sep, 1u);
            }
            s->resolved_digest64 = h;
        }

        *out_state = s;
        (void)kept;
        return DSU_STATUS_SUCCESS;
    }

    s = (dsu_state_t *)dsu__malloc((dsu_u32)sizeof(*s));
    if (!s) return DSU_STATUS_IO_ERROR;
    memset(s, 0, sizeof(*s));

    s->root_version = DSU_STATE_ROOT_SCHEMA_VERSION;
    s->product_id = dsu__strdup(dsu_plan_product_id(plan));
    s->product_version = dsu__strdup(dsu_plan_version(plan));
    s->build_channel = dsu__strdup(dsu_plan_build_channel(plan));
    s->platform = dsu__strdup(dsu_plan_platform(plan));
    s->scope = (dsu_u8)dsu_plan_scope(plan);

    s->manifest_digest64 = dsu_plan_manifest_digest64(plan);
    s->resolved_digest64 = dsu_plan_resolved_set_digest64(plan);
    s->plan_digest64 = dsu_plan_id_hash64(plan);

    s->last_successful_operation = (dsu_u8)dsu_plan_operation(plan);
    s->last_journal_id = last_journal_id;
    s->has_last_audit_log_digest = (dsu_u8)(has_last_audit_log_digest64 ? 1u : 0u);
    s->last_audit_log_digest64 = last_audit_log_digest64;

    if (!s->product_id || !s->product_version || !s->build_channel || !s->platform) {
        dsu_state_destroy(ctx, s);
        return DSU_STATUS_IO_ERROR;
    }

    if (prev_state && prev_state->install_instance_id != 0u) {
        s->install_instance_id = prev_state->install_instance_id;
    } else {
        s->install_instance_id = dsu__nonce64(ctx, s->plan_digest64);
    }

    {
        dsu_state_install_root_t r;
        char canon_root[1024];
        memset(&r, 0, sizeof(r));
        r.role = (dsu_u8)DSU_STATE_INSTALL_ROOT_ROLE_PRIMARY;
        st = dsu__canon_abs_path(dsu_plan_install_root(plan), canon_root, (dsu_u32)sizeof(canon_root));
        if (st != DSU_STATUS_SUCCESS) {
            dsu_state_destroy(ctx, s);
            return st;
        }
        r.path = dsu__strdup(canon_root);
        if (!r.path) {
            dsu_state_destroy(ctx, s);
            return DSU_STATUS_IO_ERROR;
        }
        st = dsu__install_root_push(s, &r);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__state_install_root_free(&r);
            dsu_state_destroy(ctx, s);
            return st;
        }
        memset(&r, 0, sizeof(r));
    }

    ccount = dsu_plan_component_count(plan);
    for (i = 0u; i < ccount; ++i) {
        dsu_state_component_t c;
        memset(&c, 0, sizeof(c));
        c.id = dsu__strdup(dsu_plan_component_id(plan, i));
        c.version = dsu__strdup(dsu_plan_component_version(plan, i));
        c.kind = (dsu_u8)dsu_plan_component_kind(plan, i);
        c.install_time_policy = 0u;
        if (!c.id || !c.version) {
            dsu__state_component_free(&c);
            dsu_state_destroy(ctx, s);
            return DSU_STATUS_IO_ERROR;
        }
        st = dsu__component_push(s, &c);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__state_component_free(&c);
            dsu_state_destroy(ctx, s);
            return st;
        }
        memset(&c, 0, sizeof(c));
    }

    fcount = dsu_plan_file_count(plan);
    for (i = 0u; i < fcount; ++i) {
        dsu_state_file_t f;
        dsu_u32 cix = dsu_plan_file_component_index(plan, i);
        const dsu_u8 *sha = dsu_plan_file_sha256(plan, i);
        const char *path = dsu_plan_file_target_path(plan, i);
        memset(&f, 0, sizeof(f));

        if (cix >= s->component_count) {
            dsu_state_destroy(ctx, s);
            return DSU_STATUS_INTEGRITY_ERROR;
        }
        f.root_index = 0u;
        f.size = dsu_plan_file_size(plan, i);
        if (sha) memcpy(f.sha256, sha, 32u);
        f.digest64 = dsu__digest64_from_sha256(f.sha256);
        f.ownership = (dsu_u8)DSU_STATE_FILE_OWNERSHIP_OWNED;
        f.flags = 0u;
        if (dsu_plan_operation(plan) == DSU_RESOLVE_OPERATION_INSTALL) {
            f.flags |= (dsu_u32)DSU_STATE_FILE_FLAG_CREATED_BY_INSTALL;
        }
        st = dsu__canon_rel_path_alloc(path, 0, &f.path);
        if (st != DSU_STATUS_SUCCESS) {
            dsu_state_destroy(ctx, s);
            return st;
        }

        st = dsu__component_file_push(&s->components[cix], &f);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__state_file_free(&f);
            dsu_state_destroy(ctx, s);
            return st;
        }
        memset(&f, 0, sizeof(f));
    }

    /* Copy platform registrations and marker lists from plan extras (PLANX). */
    for (i = 0u; i < ccount; ++i) {
        dsu_u32 rcount = dsu_plan_component_registration_count(plan, i);
        dsu_u32 mcount = dsu_plan_component_marker_count(plan, i);
        dsu_u32 j;
        for (j = 0u; j < rcount; ++j) {
            const char *reg = dsu_plan_component_registration(plan, i, j);
            if (!reg || reg[0] == '\0') {
                dsu_state_destroy(ctx, s);
                return DSU_STATUS_INTEGRITY_ERROR;
            }
            st = dsu__str_list_push(&s->components[i].registrations,
                                    &s->components[i].registration_count,
                                    &s->components[i].registration_cap,
                                    reg);
            if (st != DSU_STATUS_SUCCESS) {
                dsu_state_destroy(ctx, s);
                return st;
            }
        }
        for (j = 0u; j < mcount; ++j) {
            const char *marker = dsu_plan_component_marker(plan, i, j);
            if (!marker || marker[0] == '\0') {
                dsu_state_destroy(ctx, s);
                return DSU_STATUS_INTEGRITY_ERROR;
            }
            st = dsu__str_list_push(&s->components[i].markers,
                                    &s->components[i].marker_count,
                                    &s->components[i].marker_cap,
                                    marker);
            if (st != DSU_STATUS_SUCCESS) {
                dsu_state_destroy(ctx, s);
                return st;
            }
        }
    }

    st = dsu_state_validate(s);
    if (st != DSU_STATUS_SUCCESS) {
        dsu_state_destroy(ctx, s);
        return st;
    }

    *out_state = s;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_state_load_file(dsu_ctx_t *ctx, const char *path, dsu_state_t **out_state) {
    return dsu_state_load(ctx, path, out_state);
}

dsu_status_t dsu_state_write_file(dsu_ctx_t *ctx, const dsu_state_t *state, const char *path) {
    return dsu_state_save_atomic(ctx, state, path);
}

void dsu_state_destroy(dsu_ctx_t *ctx, dsu_state_t *state) {
    (void)ctx;
    if (!state) return;
    dsu__state_free(state);
    dsu__free(state);
}

const char *dsu_state_product_id(const dsu_state_t *state) {
    if (!state || !state->product_id) return "";
    return state->product_id;
}

const char *dsu_state_product_version_installed(const dsu_state_t *state) {
    if (!state || !state->product_version) return "";
    return state->product_version;
}

const char *dsu_state_build_channel(const dsu_state_t *state) {
    if (!state || !state->build_channel) return "";
    return state->build_channel;
}

const char *dsu_state_platform(const dsu_state_t *state) {
    if (!state || !state->platform) return "";
    return state->platform;
}

dsu_manifest_install_scope_t dsu_state_install_scope(const dsu_state_t *state) {
    if (!state) return DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    return (dsu_manifest_install_scope_t)state->scope;
}

dsu_u64 dsu_state_install_instance_id(const dsu_state_t *state) {
    if (!state) return (dsu_u64)0u;
    return state->install_instance_id;
}

dsu_u32 dsu_state_install_root_count(const dsu_state_t *state) {
    if (!state) return 0u;
    return state->install_root_count;
}

dsu_state_install_root_role_t dsu_state_install_root_role(const dsu_state_t *state, dsu_u32 index) {
    if (!state || index >= state->install_root_count) return DSU_STATE_INSTALL_ROOT_ROLE_PRIMARY;
    return (dsu_state_install_root_role_t)state->install_roots[index].role;
}

const char *dsu_state_install_root_path(const dsu_state_t *state, dsu_u32 index) {
    if (!state || index >= state->install_root_count) return "";
    return state->install_roots[index].path ? state->install_roots[index].path : "";
}

const char *dsu_state_primary_install_root(const dsu_state_t *state) {
    dsu_u32 i;
    if (!state) return "";
    for (i = 0u; i < state->install_root_count; ++i) {
        if (state->install_roots[i].role == (dsu_u8)DSU_STATE_INSTALL_ROOT_ROLE_PRIMARY) {
            return state->install_roots[i].path ? state->install_roots[i].path : "";
        }
    }
    if (state->install_root_count != 0u) {
        return state->install_roots[0].path ? state->install_roots[0].path : "";
    }
    return "";
}

dsu_u64 dsu_state_manifest_digest64(const dsu_state_t *state) {
    if (!state) return (dsu_u64)0u;
    return state->manifest_digest64;
}

dsu_u64 dsu_state_resolved_set_digest64(const dsu_state_t *state) {
    if (!state) return (dsu_u64)0u;
    return state->resolved_digest64;
}

dsu_u64 dsu_state_plan_digest64(const dsu_state_t *state) {
    if (!state) return (dsu_u64)0u;
    return state->plan_digest64;
}

dsu_state_last_operation_t dsu_state_last_successful_operation(const dsu_state_t *state) {
    if (!state) return DSU_STATE_OPERATION_INSTALL;
    return (dsu_state_last_operation_t)state->last_successful_operation;
}

dsu_u64 dsu_state_last_journal_id(const dsu_state_t *state) {
    if (!state) return (dsu_u64)0u;
    return state->last_journal_id;
}

dsu_bool dsu_state_has_last_audit_log_digest64(const dsu_state_t *state) {
    if (!state) return DSU_FALSE;
    return state->has_last_audit_log_digest ? DSU_TRUE : DSU_FALSE;
}

dsu_u64 dsu_state_last_audit_log_digest64(const dsu_state_t *state) {
    if (!state) return (dsu_u64)0u;
    return state->last_audit_log_digest64;
}

dsu_u32 dsu_state_component_count(const dsu_state_t *state) {
    if (!state) return 0u;
    return state->component_count;
}

const char *dsu_state_component_id(const dsu_state_t *state, dsu_u32 index) {
    if (!state || index >= state->component_count) return NULL;
    return state->components[index].id;
}

const char *dsu_state_component_version(const dsu_state_t *state, dsu_u32 index) {
    if (!state || index >= state->component_count) return NULL;
    return state->components[index].version;
}

dsu_manifest_component_kind_t dsu_state_component_kind(const dsu_state_t *state, dsu_u32 index) {
    if (!state || index >= state->component_count) return DSU_MANIFEST_COMPONENT_KIND_OTHER;
    return (dsu_manifest_component_kind_t)state->components[index].kind;
}

dsu_u64 dsu_state_component_install_time_policy(const dsu_state_t *state, dsu_u32 index) {
    if (!state || index >= state->component_count) return (dsu_u64)0u;
    return state->components[index].install_time_policy;
}

dsu_u32 dsu_state_component_file_count(const dsu_state_t *state, dsu_u32 component_index) {
    if (!state || component_index >= state->component_count) return 0u;
    return state->components[component_index].file_count;
}

dsu_u32 dsu_state_component_file_root_index(const dsu_state_t *state, dsu_u32 component_index, dsu_u32 file_index) {
    if (!state || component_index >= state->component_count) return 0u;
    if (file_index >= state->components[component_index].file_count) return 0u;
    return state->components[component_index].files[file_index].root_index;
}

const char *dsu_state_component_file_path(const dsu_state_t *state, dsu_u32 component_index, dsu_u32 file_index) {
    if (!state || component_index >= state->component_count) return NULL;
    if (file_index >= state->components[component_index].file_count) return NULL;
    return state->components[component_index].files[file_index].path;
}

dsu_u64 dsu_state_component_file_size(const dsu_state_t *state, dsu_u32 component_index, dsu_u32 file_index) {
    if (!state || component_index >= state->component_count) return (dsu_u64)0u;
    if (file_index >= state->components[component_index].file_count) return (dsu_u64)0u;
    return state->components[component_index].files[file_index].size;
}

dsu_u64 dsu_state_component_file_digest64(const dsu_state_t *state, dsu_u32 component_index, dsu_u32 file_index) {
    if (!state || component_index >= state->component_count) return (dsu_u64)0u;
    if (file_index >= state->components[component_index].file_count) return (dsu_u64)0u;
    return state->components[component_index].files[file_index].digest64;
}

dsu_state_file_ownership_t dsu_state_component_file_ownership(const dsu_state_t *state, dsu_u32 component_index, dsu_u32 file_index) {
    dsu_u8 v;
    if (!state || component_index >= state->component_count) return DSU_STATE_FILE_OWNERSHIP_USER_DATA;
    if (file_index >= state->components[component_index].file_count) return DSU_STATE_FILE_OWNERSHIP_USER_DATA;
    v = state->components[component_index].files[file_index].ownership;
    if (v > (dsu_u8)DSU_STATE_FILE_OWNERSHIP_CACHE) {
        return DSU_STATE_FILE_OWNERSHIP_USER_DATA;
    }
    return (dsu_state_file_ownership_t)v;
}

dsu_u32 dsu_state_component_file_flags(const dsu_state_t *state, dsu_u32 component_index, dsu_u32 file_index) {
    if (!state || component_index >= state->component_count) return 0u;
    if (file_index >= state->components[component_index].file_count) return 0u;
    return state->components[component_index].files[file_index].flags;
}

dsu_u32 dsu_state_component_registration_count(const dsu_state_t *state, dsu_u32 component_index) {
    if (!state || component_index >= state->component_count) return 0u;
    return state->components[component_index].registration_count;
}

const char *dsu_state_component_registration(const dsu_state_t *state, dsu_u32 component_index, dsu_u32 reg_index) {
    if (!state || component_index >= state->component_count) return NULL;
    if (reg_index >= state->components[component_index].registration_count) return NULL;
    return state->components[component_index].registrations[reg_index];
}

dsu_u32 dsu_state_component_marker_count(const dsu_state_t *state, dsu_u32 component_index) {
    if (!state || component_index >= state->component_count) return 0u;
    return state->components[component_index].marker_count;
}

const char *dsu_state_component_marker(const dsu_state_t *state, dsu_u32 component_index, dsu_u32 marker_index) {
    if (!state || component_index >= state->component_count) return NULL;
    if (marker_index >= state->components[component_index].marker_count) return NULL;
    return state->components[component_index].markers[marker_index];
}

/* Compatibility API */
const char *dsu_state_product_version(const dsu_state_t *state) {
    return dsu_state_product_version_installed(state);
}

dsu_manifest_install_scope_t dsu_state_scope(const dsu_state_t *state) {
    return dsu_state_install_scope(state);
}

const char *dsu_state_install_root(const dsu_state_t *state) {
    return dsu_state_primary_install_root(state);
}

dsu_u32 dsu_state_file_count(const dsu_state_t *state) {
    if (!state) return 0u;
    return state->flat_file_count;
}

const char *dsu_state_file_path(const dsu_state_t *state, dsu_u32 index) {
    if (!state || index >= state->flat_file_count) return NULL;
    return state->flat_files[index] ? state->flat_files[index]->path : NULL;
}

dsu_u64 dsu_state_file_size(const dsu_state_t *state, dsu_u32 index) {
    if (!state || index >= state->flat_file_count) return (dsu_u64)0u;
    return state->flat_files[index] ? state->flat_files[index]->size : (dsu_u64)0u;
}

const dsu_u8 *dsu_state_file_sha256(const dsu_state_t *state, dsu_u32 index) {
    if (!state || index >= state->flat_file_count) return NULL;
    return state->flat_files[index] ? state->flat_files[index]->sha256 : NULL;
}
