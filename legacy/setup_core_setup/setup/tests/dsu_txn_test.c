/*
FILE: source/dominium/setup/tests/dsu_txn_test.c
MODULE: Dominium Setup
PURPOSE: Plan S-4 transaction engine + filesystem safety tests.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#  define WIN32_LEAN_AND_MEAN
#  include <windows.h>
#endif

#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_fs.h"
#include "dsu/dsu_log.h"
#include "dsu/dsu_manifest.h"
#include "dsu/dsu_plan.h"
#include "dsu/dsu_report.h"
#include "dsu/dsu_resolve.h"
#include "dsu/dsu_state.h"
#include "dsu/dsu_txn.h"

/* Internal-only platform helpers for directory enumeration in tests. */
#include "../core/src/fs/dsu_platform_iface.h"
#include "../core/src/txn/dsu_journal.h"

static int expect(int cond, const char *msg) {
    if (!cond) {
        fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
        return 0;
    }
    return 1;
}

static int expect_st(dsu_status_t got, dsu_status_t want, const char *msg) {
    if (got != want) {
        fprintf(stderr, "FAIL: %s (got=%d want=%d)\n", msg ? msg : "(null)", (int)got, (int)want);
        return 0;
    }
    return 1;
}

static void dump_audit_log(dsu_ctx_t *ctx) {
    dsu_log_t *log;
    dsu_u32 count;
    dsu_u32 i;
    if (!ctx) return;
    log = dsu_ctx_get_audit_log(ctx);
    if (!log) return;
    count = dsu_log_event_count(log);
    fprintf(stderr, "AUDIT_LOG_COUNT=%lu\n", (unsigned long)count);
    for (i = 0u; i < count; ++i) {
        dsu_u32 event_id = 0u;
        dsu_u8 sev = 0u;
        dsu_u8 cat = 0u;
        dsu_u32 ts = 0u;
        const char *msg = NULL;
        (void)dsu_log_event_get(log, i, &event_id, &sev, &cat, &ts, &msg);
        fprintf(stderr,
                "  %lu: id=%lu sev=%u cat=%u ts=%lu msg=%s\n",
                (unsigned long)i,
                (unsigned long)event_id,
                (unsigned int)sev,
                (unsigned int)cat,
                (unsigned long)ts,
                msg ? msg : "");
    }
}

static int write_bytes_file(const char *path, const unsigned char *bytes, unsigned long len) {
    FILE *f;
    size_t n;
    if (!path || (!bytes && len != 0ul)) {
        return 0;
    }
    f = fopen(path, "wb");
    if (!f) {
        return 0;
    }
    n = (size_t)len;
    if (n != 0u) {
        if (fwrite(bytes, 1u, n, f) != n) {
            fclose(f);
            return 0;
        }
    }
    if (fclose(f) != 0) {
        return 0;
    }
    return 1;
}

static int read_all_bytes(const char *path, unsigned char **out_bytes, unsigned long *out_len) {
    FILE *f;
    long sz;
    unsigned char *buf;
    size_t nread;
    if (!path || !out_bytes || !out_len) return 0;
    *out_bytes = NULL;
    *out_len = 0ul;
    f = fopen(path, "rb");
    if (!f) return 0;
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return 0;
    }
    sz = ftell(f);
    if (sz < 0) {
        fclose(f);
        return 0;
    }
    if (fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return 0;
    }
    buf = (unsigned char *)malloc((size_t)sz);
    if (!buf && sz != 0) {
        fclose(f);
        return 0;
    }
    nread = (sz == 0) ? 0u : fread(buf, 1u, (size_t)sz, f);
    fclose(f);
    if (nread != (size_t)sz) {
        free(buf);
        return 0;
    }
    *out_bytes = buf;
    *out_len = (unsigned long)sz;
    return 1;
}

static int bytes_equal(const unsigned char *a, unsigned long a_len, const unsigned char *b, unsigned long b_len) {
    if (a_len != b_len) return 0;
    if (a_len == 0ul) return 1;
    if (!a || !b) return 0;
    return memcmp(a, b, (size_t)a_len) == 0;
}

static int bytes_replace_in_first_match(unsigned char *buf,
                                        unsigned long buf_len,
                                        const char *needle,
                                        unsigned char from,
                                        unsigned char to) {
    unsigned long i;
    unsigned long n;
    unsigned long j;
    if (!buf || !needle) return 0;
    n = (unsigned long)strlen(needle);
    if (n == 0ul || n > buf_len) return 0;
    for (i = 0ul; i + n <= buf_len; ++i) {
        if (memcmp(buf + i, needle, (size_t)n) == 0) {
            for (j = 0ul; j < n; ++j) {
                if (buf[i + j] == from) buf[i + j] = to;
            }
            return 1;
        }
    }
    return 0;
}

#if defined(_WIN32)
static int path_to_native_win32(const char *in, char *out, unsigned long out_cap) {
    unsigned long n;
    unsigned long i;
    if (!in || !out || out_cap == 0ul) return 0;
    n = (unsigned long)strlen(in);
    if (n + 1ul > out_cap) return 0;
    for (i = 0ul; i < n; ++i) {
        char c = in[i];
        if (c == '/') c = '\\';
        out[i] = c;
    }
    out[n] = '\0';
    return 1;
}
#endif

static dsu_ctx_t *create_ctx_deterministic(void) {
    dsu_config_t cfg;
    dsu_callbacks_t cbs;
    dsu_ctx_t *ctx = NULL;
    dsu_status_t st;
    dsu_config_init(&cfg);
    dsu_callbacks_init(&cbs);
    cfg.flags |= DSU_CONFIG_FLAG_DETERMINISTIC;
    st = dsu_ctx_create(&cfg, &cbs, NULL, &ctx);
    if (st != DSU_STATUS_SUCCESS) {
        return NULL;
    }
    return ctx;
}

static int path_join(const char *a, const char *b, char *out_path, unsigned long out_cap) {
    dsu_status_t st;
    if (!out_path || out_cap == 0ul) return 0;
    out_path[0] = '\0';
    st = dsu_fs_path_join(a, b, out_path, (dsu_u32)out_cap);
    return st == DSU_STATUS_SUCCESS;
}

static int file_exists(const char *path) {
    dsu_u8 exists = 0u;
    dsu_u8 is_dir = 0u;
    dsu_u8 is_symlink = 0u;
    if (!path) return 0;
    if (dsu_platform_path_info(path, &exists, &is_dir, &is_symlink) != DSU_STATUS_SUCCESS) return 0;
    return exists && !is_dir;
}

static int dir_exists(const char *path) {
    dsu_u8 exists = 0u;
    dsu_u8 is_dir = 0u;
    dsu_u8 is_symlink = 0u;
    if (!path) return 0;
    if (dsu_platform_path_info(path, &exists, &is_dir, &is_symlink) != DSU_STATUS_SUCCESS) return 0;
    return exists && is_dir && !is_symlink;
}

static int mkdir_p_rel(const char *rel_path) {
    char canon[1024];
    unsigned long i;
    unsigned long n;
    dsu_status_t st;
    if (!rel_path) return 0;
    if (rel_path[0] == '\0') return 1;
    st = dsu_fs_path_canonicalize(rel_path, canon, (dsu_u32)sizeof(canon));
    if (st != DSU_STATUS_SUCCESS) return 0;
    n = (unsigned long)strlen(canon);
    if (n == 0ul) return 1;
    for (i = 0ul; i <= n; ++i) {
        char c = canon[i];
        if (c == '/' || c == '\0') {
            char part[1024];
            if (i == 0ul) continue;
            if (i >= (unsigned long)sizeof(part)) return 0;
            memcpy(part, canon, (size_t)i);
            part[i] = '\0';
            if (dsu_platform_mkdir(part) != DSU_STATUS_SUCCESS) return 0;
        }
    }
    return 1;
}

static dsu_status_t rm_rf(const char *path) {
    dsu_u8 exists;
    dsu_u8 is_dir;
    dsu_u8 is_symlink;
    dsu_status_t st;
    dsu_platform_dir_entry_t *ents = NULL;
    dsu_u32 count = 0u;
    dsu_u32 i;
    if (!path || path[0] == '\0') return DSU_STATUS_INVALID_ARGS;
    st = dsu_platform_path_info(path, &exists, &is_dir, &is_symlink);
    if (st != DSU_STATUS_SUCCESS) return st;
    if (!exists) return DSU_STATUS_SUCCESS;
    if (is_symlink || !is_dir) {
        return dsu_platform_remove_file(path);
    }
    st = dsu_platform_list_dir(path, &ents, &count);
    if (st != DSU_STATUS_SUCCESS) return st;
    for (i = 0u; i < count; ++i) {
        const char *name = ents[i].name ? ents[i].name : "";
        char child[1024];
        if (name[0] == '\0') continue;
        if (strcmp(name, ".") == 0 || strcmp(name, "..") == 0) continue;
        if (!path_join(path, name, child, (unsigned long)sizeof(child))) {
            dsu_platform_free_dir_entries(ents, count);
            return DSU_STATUS_INVALID_ARGS;
        }
        st = rm_rf(child);
        if (st != DSU_STATUS_SUCCESS) {
            dsu_platform_free_dir_entries(ents, count);
            return st;
        }
    }
    dsu_platform_free_dir_entries(ents, count);
    return dsu_platform_rmdir(path);
}

static int set_env_var(const char *key, const char *val) {
#if defined(_WIN32)
    if (!key) return 0;
    if (!val) val = "";
    return _putenv_s(key, val) == 0;
#else
    if (!key) return 0;
    if (!val) return unsetenv(key) == 0;
    return setenv(key, val, 1) == 0;
#endif
}

typedef struct buf_t {
    unsigned char *data;
    unsigned long len;
    unsigned long cap;
} buf_t;

static void buf_free(buf_t *b) {
    if (!b) return;
    free(b->data);
    b->data = NULL;
    b->len = 0ul;
    b->cap = 0ul;
}

static int buf_reserve(buf_t *b, unsigned long add) {
    unsigned long need;
    unsigned long new_cap;
    unsigned char *p;
    if (!b) return 0;
    if (add == 0ul) return 1;
    need = b->len + add;
    if (need < b->len) return 0;
    if (need <= b->cap) return 1;
    new_cap = (b->cap == 0ul) ? 256ul : b->cap;
    while (new_cap < need) {
        if (new_cap > 0x7FFFFFFFul) {
            new_cap = need;
            break;
        }
        new_cap *= 2ul;
    }
    p = (unsigned char *)realloc(b->data, (size_t)new_cap);
    if (!p) return 0;
    b->data = p;
    b->cap = new_cap;
    return 1;
}

static int buf_append(buf_t *b, const void *bytes, unsigned long n) {
    if (!b) return 0;
    if (n == 0ul) return 1;
    if (!bytes) return 0;
    if (!buf_reserve(b, n)) return 0;
    memcpy(b->data + b->len, bytes, (size_t)n);
    b->len += n;
    return 1;
}

static int buf_put_u16le(buf_t *b, unsigned short v) {
    unsigned char tmp[2];
    tmp[0] = (unsigned char)(v & 0xFFu);
    tmp[1] = (unsigned char)((v >> 8) & 0xFFu);
    return buf_append(b, tmp, 2ul);
}

static int buf_put_u32le(buf_t *b, unsigned long v) {
    unsigned char tmp[4];
    tmp[0] = (unsigned char)(v & 0xFFul);
    tmp[1] = (unsigned char)((v >> 8) & 0xFFul);
    tmp[2] = (unsigned char)((v >> 16) & 0xFFul);
    tmp[3] = (unsigned char)((v >> 24) & 0xFFul);
    return buf_append(b, tmp, 4ul);
}

static int buf_put_tlv(buf_t *b, unsigned short type, const void *payload, unsigned long payload_len) {
    if (!buf_put_u16le(b, type)) return 0;
    if (!buf_put_u32le(b, payload_len)) return 0;
    return buf_append(b, payload, payload_len);
}

static int buf_put_tlv_u32(buf_t *b, unsigned short type, unsigned long v) {
    unsigned char tmp[4];
    tmp[0] = (unsigned char)(v & 0xFFul);
    tmp[1] = (unsigned char)((v >> 8) & 0xFFul);
    tmp[2] = (unsigned char)((v >> 16) & 0xFFul);
    tmp[3] = (unsigned char)((v >> 24) & 0xFFul);
    return buf_put_tlv(b, type, tmp, 4ul);
}

static int buf_put_tlv_u8(buf_t *b, unsigned short type, unsigned char v) {
    return buf_put_tlv(b, type, &v, 1ul);
}

static int buf_put_tlv_str(buf_t *b, unsigned short type, const char *s) {
    unsigned long n;
    if (!s) s = "";
    n = (unsigned long)strlen(s);
    return buf_put_tlv(b, type, s, n);
}

static unsigned long header_checksum32_base(const unsigned char hdr[20]) {
    unsigned long sum = 0ul;
    unsigned long i;
    for (i = 0ul; i < 16ul; ++i) {
        sum += (unsigned long)hdr[i];
    }
    return sum;
}

static int wrap_file(buf_t *out_file, const unsigned char magic[4], unsigned short version, const buf_t *payload) {
    unsigned char hdr[20];
    unsigned long checksum;
    if (!out_file || !magic || !payload) return 0;
    memset(out_file, 0, sizeof(*out_file));
    memset(hdr, 0, sizeof(hdr));
    hdr[0] = magic[0];
    hdr[1] = magic[1];
    hdr[2] = magic[2];
    hdr[3] = magic[3];
    hdr[4] = (unsigned char)(version & 0xFFu);
    hdr[5] = (unsigned char)((version >> 8) & 0xFFu);
    hdr[6] = 0xFEu;
    hdr[7] = 0xFFu;
    hdr[8] = 20u;
    hdr[9] = 0u;
    hdr[10] = 0u;
    hdr[11] = 0u;
    hdr[12] = (unsigned char)(payload->len & 0xFFul);
    hdr[13] = (unsigned char)((payload->len >> 8) & 0xFFul);
    hdr[14] = (unsigned char)((payload->len >> 16) & 0xFFul);
    hdr[15] = (unsigned char)((payload->len >> 24) & 0xFFul);
    checksum = header_checksum32_base(hdr);
    hdr[16] = (unsigned char)(checksum & 0xFFul);
    hdr[17] = (unsigned char)((checksum >> 8) & 0xFFul);
    hdr[18] = (unsigned char)((checksum >> 16) & 0xFFul);
    hdr[19] = (unsigned char)((checksum >> 24) & 0xFFul);
    if (!buf_append(out_file, hdr, 20ul)) return 0;
    if (!buf_append(out_file, payload->data, payload->len)) return 0;
    return 1;
}

static int write_manifest_fileset(const char *manifest_path,
                                  const char *install_root_path,
                                  const char *payload_path,
                                  const char *component_id) {
    /* TLV types from docs/setup/MANIFEST_SCHEMA.md */
    const unsigned short T_ROOT = 0x0001u;
    const unsigned short T_ROOT_VER = 0x0002u;
    const unsigned short T_PRODUCT_ID = 0x0010u;
    const unsigned short T_PRODUCT_VER = 0x0011u;
    const unsigned short T_BUILD_CHANNEL = 0x0012u;
    const unsigned short T_PLATFORM_TARGET = 0x0020u;
    const unsigned short T_INSTALL_ROOT = 0x0030u;
    const unsigned short T_IR_VER = 0x0031u;
    const unsigned short T_IR_SCOPE = 0x0032u;
    const unsigned short T_IR_PLATFORM = 0x0033u;
    const unsigned short T_IR_PATH = 0x0034u;
    const unsigned short T_COMPONENT = 0x0040u;
    const unsigned short T_C_VER = 0x0041u;
    const unsigned short T_C_ID = 0x0042u;
    const unsigned short T_C_KIND = 0x0044u;
    const unsigned short T_C_FLAGS = 0x0045u;
    const unsigned short T_PAYLOAD = 0x004Cu;
    const unsigned short T_P_VER = 0x004Du;
    const unsigned short T_P_KIND = 0x004Eu;
    const unsigned short T_P_PATH = 0x004Fu;
    const unsigned short T_P_SHA256 = 0x0050u;

    buf_t root;
    buf_t payload;
    buf_t ir;
    buf_t comp;
    buf_t pl;
    buf_t file;
    unsigned char magic[4];
    unsigned char sha0[32];

    memset(&root, 0, sizeof(root));
    memset(&payload, 0, sizeof(payload));
    memset(&ir, 0, sizeof(ir));
    memset(&comp, 0, sizeof(comp));
    memset(&pl, 0, sizeof(pl));
    memset(&file, 0, sizeof(file));
    memset(sha0, 0, sizeof(sha0));
    magic[0] = 'D';
    magic[1] = 'S';
    magic[2] = 'U';
    magic[3] = 'M';

    if (!manifest_path || !install_root_path || !payload_path || !component_id) {
        return 0;
    }

    if (!buf_put_tlv_u32(&root, T_ROOT_VER, 1ul)) goto fail;
    if (!buf_put_tlv_str(&root, T_PRODUCT_ID, "dominium")) goto fail;
    if (!buf_put_tlv_str(&root, T_PRODUCT_VER, "1.0.0")) goto fail;
    if (!buf_put_tlv_str(&root, T_BUILD_CHANNEL, "stable")) goto fail;
    if (!buf_put_tlv_str(&root, T_PLATFORM_TARGET, "any-any")) goto fail;

    if (!buf_put_tlv_u32(&ir, T_IR_VER, 1ul)) goto fail;
    if (!buf_put_tlv_u8(&ir, T_IR_SCOPE, 0u)) goto fail;
    if (!buf_put_tlv_str(&ir, T_IR_PLATFORM, "any-any")) goto fail;
    if (!buf_put_tlv_str(&ir, T_IR_PATH, install_root_path)) goto fail;
    if (!buf_put_tlv(&root, T_INSTALL_ROOT, ir.data, ir.len)) goto fail;

    if (!buf_put_tlv_u32(&pl, T_P_VER, 1ul)) goto fail;
    if (!buf_put_tlv_u8(&pl, T_P_KIND, 0u)) goto fail; /* fileset */
    if (!buf_put_tlv_str(&pl, T_P_PATH, payload_path)) goto fail;
    if (!buf_put_tlv(&pl, T_P_SHA256, sha0, 32ul)) goto fail;

    if (!buf_put_tlv_u32(&comp, T_C_VER, 1ul)) goto fail;
    if (!buf_put_tlv_str(&comp, T_C_ID, component_id)) goto fail;
    if (!buf_put_tlv_u8(&comp, T_C_KIND, (unsigned char)DSU_MANIFEST_COMPONENT_KIND_OTHER)) goto fail;
    if (!buf_put_tlv_u32(&comp, T_C_FLAGS, 0ul)) goto fail;
    if (!buf_put_tlv(&comp, T_PAYLOAD, pl.data, pl.len)) goto fail;
    if (!buf_put_tlv(&root, T_COMPONENT, comp.data, comp.len)) goto fail;

    if (!buf_put_tlv(&payload, T_ROOT, root.data, root.len)) goto fail;
    if (!wrap_file(&file, magic, (unsigned short)DSU_MANIFEST_FORMAT_VERSION, &payload)) goto fail;

    if (!write_bytes_file(manifest_path, file.data, file.len)) goto fail;

    buf_free(&root);
    buf_free(&payload);
    buf_free(&ir);
    buf_free(&comp);
    buf_free(&pl);
    buf_free(&file);
    return 1;

fail:
    buf_free(&root);
    buf_free(&payload);
    buf_free(&ir);
    buf_free(&comp);
    buf_free(&pl);
    buf_free(&file);
    return 0;
}

typedef struct snap_file_t {
    char *rel_path;
    dsu_u8 sha256[32];
    dsu_u64 size;
} snap_file_t;

typedef struct snap_t {
    snap_file_t *items;
    dsu_u32 count;
    dsu_u32 cap;
} snap_t;

static void snap_free(snap_t *s) {
    dsu_u32 i;
    if (!s) return;
    for (i = 0u; i < s->count; ++i) {
        free(s->items[i].rel_path);
        s->items[i].rel_path = NULL;
    }
    free(s->items);
    s->items = NULL;
    s->count = 0u;
    s->cap = 0u;
}

static int snap_push(snap_t *s, const char *rel, const dsu_u8 sha[32], dsu_u64 size) {
    snap_file_t *p;
    dsu_u32 new_cap;
    char *dup;
    unsigned long n;
    if (!s || !rel || !sha) return 0;
    if (s->count == s->cap) {
        new_cap = (s->cap == 0u) ? 16u : (s->cap * 2u);
        p = (snap_file_t *)realloc(s->items, (size_t)new_cap * sizeof(*p));
        if (!p) return 0;
        s->items = p;
        s->cap = new_cap;
    }
    n = (unsigned long)strlen(rel);
    dup = (char *)malloc((size_t)n + 1u);
    if (!dup) return 0;
    if (n) memcpy(dup, rel, (size_t)n);
    dup[n] = '\0';
    s->items[s->count].rel_path = dup;
    memcpy(s->items[s->count].sha256, sha, 32u);
    s->items[s->count].size = size;
    s->count += 1u;
    return 1;
}

static int snap_cmp(const void *a, const void *b) {
    const snap_file_t *fa = (const snap_file_t *)a;
    const snap_file_t *fb = (const snap_file_t *)b;
    const char *pa = fa->rel_path ? fa->rel_path : "";
    const char *pb = fb->rel_path ? fb->rel_path : "";
    return strcmp(pa, pb);
}

static int file_size_u64(const char *path, dsu_u64 *out_size) {
    FILE *f;
    long sz;
    if (!out_size) return 0;
    *out_size = 0u;
    if (!path) return 0;
    f = fopen(path, "rb");
    if (!f) return 0;
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return 0;
    }
    sz = ftell(f);
    fclose(f);
    if (sz < 0) return 0;
    *out_size = (dsu_u64)(unsigned long)sz;
    return 1;
}

static int snap_enum_dir(const char *root, const char *rel_dir, snap_t *io_snap) {
    char dir_path[1024];
    dsu_platform_dir_entry_t *ents = NULL;
    dsu_u32 count = 0u;
    dsu_status_t st;
    dsu_u32 i;
    if (!root || !io_snap || !rel_dir) return 0;
    if (rel_dir[0] == '\0') {
        if (strlen(root) + 1u > (unsigned long)sizeof(dir_path)) return 0;
        memcpy(dir_path, root, strlen(root) + 1u);
    } else {
        if (!path_join(root, rel_dir, dir_path, (unsigned long)sizeof(dir_path))) return 0;
    }

    st = dsu_platform_list_dir(dir_path, &ents, &count);
    if (st != DSU_STATUS_SUCCESS) return 0;

    for (i = 0u; i < count; ++i) {
        const char *name = ents[i].name ? ents[i].name : "";
        char child_rel[1024];
        char child_path[1024];
        dsu_u8 sha[32];
        dsu_u64 sz;
        if (name[0] == '\0') continue;
        if (strcmp(name, ".") == 0 || strcmp(name, "..") == 0) continue;

        if (rel_dir[0] == '\0') {
            if (strlen(name) + 1u > (unsigned long)sizeof(child_rel)) {
                dsu_platform_free_dir_entries(ents, count);
                return 0;
            }
            memcpy(child_rel, name, strlen(name) + 1u);
        } else {
            if (!path_join(rel_dir, name, child_rel, (unsigned long)sizeof(child_rel))) {
                dsu_platform_free_dir_entries(ents, count);
                return 0;
            }
        }
        if (!path_join(root, child_rel, child_path, (unsigned long)sizeof(child_path))) {
            dsu_platform_free_dir_entries(ents, count);
            return 0;
        }

        if (ents[i].is_symlink) {
            if (!file_size_u64(child_path, &sz)) {
                dsu_platform_free_dir_entries(ents, count);
                return 0;
            }
            if (dsu__sha256_file(child_path, sha) != DSU_STATUS_SUCCESS) {
                dsu_platform_free_dir_entries(ents, count);
                return 0;
            }
            if (!snap_push(io_snap, child_rel, sha, sz)) {
                dsu_platform_free_dir_entries(ents, count);
                return 0;
            }
            continue;
        }

        if (ents[i].is_dir) {
            if (!snap_enum_dir(root, child_rel, io_snap)) {
                dsu_platform_free_dir_entries(ents, count);
                return 0;
            }
        } else {
            if (!file_size_u64(child_path, &sz)) {
                dsu_platform_free_dir_entries(ents, count);
                return 0;
            }
            if (dsu__sha256_file(child_path, sha) != DSU_STATUS_SUCCESS) {
                dsu_platform_free_dir_entries(ents, count);
                return 0;
            }
            if (!snap_push(io_snap, child_rel, sha, sz)) {
                dsu_platform_free_dir_entries(ents, count);
                return 0;
            }
        }
    }

    dsu_platform_free_dir_entries(ents, count);
    return 1;
}

static int snap_build(const char *root, snap_t *out_snap) {
    dsu_u8 exists;
    dsu_u8 is_dir;
    dsu_u8 is_symlink;
    if (!out_snap) return 0;
    memset(out_snap, 0, sizeof(*out_snap));
    if (!root) return 0;
    if (dsu_platform_path_info(root, &exists, &is_dir, &is_symlink) != DSU_STATUS_SUCCESS) return 0;
    if (!exists || !is_dir || is_symlink) return 0;
    if (!snap_enum_dir(root, "", out_snap)) {
        snap_free(out_snap);
        return 0;
    }
    if (out_snap->count > 1u) {
        qsort(out_snap->items, (size_t)out_snap->count, sizeof(out_snap->items[0]), snap_cmp);
    }
    return 1;
}

static int snap_equal(const snap_t *a, const snap_t *b) {
    dsu_u32 i;
    if (!a || !b) return 0;
    if (a->count != b->count) return 0;
    for (i = 0u; i < a->count; ++i) {
        const char *pa = a->items[i].rel_path ? a->items[i].rel_path : "";
        const char *pb = b->items[i].rel_path ? b->items[i].rel_path : "";
        if (strcmp(pa, pb) != 0) return 0;
        if (a->items[i].size != b->items[i].size) return 0;
        if (memcmp(a->items[i].sha256, b->items[i].sha256, 32u) != 0) return 0;
    }
    return 1;
}

static int test_path_traversal_rejection(void) {
    dsu_ctx_t *ctx = NULL;
    dsu_fs_t *fs = NULL;
    dsu_status_t st;
    int ok = 1;
    char cwd[1024];
    char out[1024];
    const char *roots[1];
    dsu_fs_options_t fopts;

    memset(cwd, 0, sizeof(cwd));
    memset(out, 0, sizeof(out));

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create");
    if (!ok) goto done;

    st = dsu_platform_get_cwd(cwd, (dsu_u32)sizeof(cwd));
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "get cwd");
    if (!ok) goto done;

    roots[0] = cwd;
    dsu_fs_options_init(&fopts);
    fopts.allowed_roots = roots;
    fopts.allowed_root_count = 1u;
    st = dsu_fs_create(ctx, &fopts, &fs);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "fs create");
    if (!ok) goto done;

    st = dsu_fs_resolve_under_root(fs, 0u, "../evil.txt", out, (dsu_u32)sizeof(out));
    ok &= expect(st != DSU_STATUS_SUCCESS, "reject ../ traversal");

    st = dsu_fs_resolve_under_root(fs, 0u, "a/../b", out, (dsu_u32)sizeof(out));
    ok &= expect(st != DSU_STATUS_SUCCESS, "reject a/../b traversal");

    st = dsu_fs_resolve_under_root(fs, 0u, "/abs", out, (dsu_u32)sizeof(out));
    ok &= expect(st != DSU_STATUS_SUCCESS, "reject absolute injection");

done:
    if (fs) dsu_fs_destroy(ctx, fs);
    if (ctx) dsu_ctx_destroy(ctx);
    return ok;
}

static int test_fresh_install(void) {
    const char *base = "dsu_test_txn_fresh";
    char manifest_path[1024];
    char payload_root[1024];
    char install_root[1024];
    char payload_bin_dir[1024];
    char payload_data_dir[1024];
    char payload_f1[1024];
    char payload_f2[1024];
    char install_f1[1024];
    char install_f2[1024];
    char state_path[1024];
    unsigned char *bytes = NULL;
    unsigned long len = 0ul;

    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_resolve_result_t *r = NULL;
    dsu_plan_t *p = NULL;
    dsu_state_t *s = NULL;
    dsu_txn_options_t opts;
    dsu_txn_result_t res;
    dsu_status_t st;
    int ok = 1;

    (void)rm_rf(base);
    ok &= expect(mkdir_p_rel(base), "mkdir base");

    ok &= expect(path_join(base, "payload", payload_root, (unsigned long)sizeof(payload_root)), "join payload root");
    ok &= expect(path_join(payload_root, "bin", payload_bin_dir, (unsigned long)sizeof(payload_bin_dir)), "join payload/bin");
    ok &= expect(path_join(payload_root, "data", payload_data_dir, (unsigned long)sizeof(payload_data_dir)), "join payload/data");
    ok &= expect(mkdir_p_rel(payload_bin_dir), "mkdir payload/bin");
    ok &= expect(mkdir_p_rel(payload_data_dir), "mkdir payload/data");

    ok &= expect(path_join(payload_bin_dir, "hello.txt", payload_f1, (unsigned long)sizeof(payload_f1)), "join payload f1");
    ok &= expect(path_join(payload_data_dir, "config.json", payload_f2, (unsigned long)sizeof(payload_f2)), "join payload f2");
    ok &= expect(write_bytes_file(payload_f1, (const unsigned char *)"hello\n", 6ul), "write payload hello");
    ok &= expect(write_bytes_file(payload_f2, (const unsigned char *)"{\"k\":1}\n", 8ul), "write payload config");

    ok &= expect(path_join(base, "install", install_root, (unsigned long)sizeof(install_root)), "join install root");
    ok &= expect(path_join(install_root, "bin/hello.txt", install_f1, (unsigned long)sizeof(install_f1)), "join install f1");
    ok &= expect(path_join(install_root, "data/config.json", install_f2, (unsigned long)sizeof(install_f2)), "join install f2");
    ok &= expect(path_join(install_root, ".dsu/installed_state.dsustate", state_path, (unsigned long)sizeof(state_path)), "join state path");

    ok &= expect(path_join(base, "m.dsumanifest", manifest_path, (unsigned long)sizeof(manifest_path)), "join manifest path");
    ok &= expect(write_manifest_fileset(manifest_path, install_root, "payload", "core"), "write manifest");
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, manifest_path, &m);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "manifest load");
    ok &= expect(m != NULL, "manifest != NULL");
    if (!ok) goto done;

    {
        const char *const requested[] = {"core"};
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.requested_components = requested;
        req.requested_component_count = 1u;
        st = dsu_resolve_components(ctx, m, NULL, &req, &r);
    }
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "resolve");
    ok &= expect(r != NULL, "resolve != NULL");
    if (!ok) goto done;

    st = dsu_plan_build(ctx, m, manifest_path, r, 0x1111222233334444ULL, &p);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "plan build");
    ok &= expect(p != NULL, "plan != NULL");
    if (!ok) goto done;

    st = dsu_ctx_reset_audit_log(ctx);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "reset audit log");
    if (!ok) goto done;

    dsu_txn_options_init(&opts);
    dsu_txn_result_init(&res);
    st = dsu_txn_apply_plan(ctx, p, &opts, &res);
    if (st != DSU_STATUS_SUCCESS) {
        char staged1[1024];
        char staged2[1024];
        char state_txn[1024];
        fprintf(stderr, "INSTALL_ROOT=%s\n", res.install_root);
        fprintf(stderr, "TXN_ROOT=%s (dir=%d)\n", res.txn_root, dir_exists(res.txn_root));
        fprintf(stderr, "JOURNAL=%s (file=%d)\n", res.journal_path, file_exists(res.journal_path));
        if (path_join(res.txn_root, ".dsu_txn/staged/bin/hello.txt", staged1, (unsigned long)sizeof(staged1))) {
            fprintf(stderr, "STAGED1=%s (file=%d)\n", staged1, file_exists(staged1));
        }
        if (path_join(res.txn_root, ".dsu_txn/staged/data/config.json", staged2, (unsigned long)sizeof(staged2))) {
            fprintf(stderr, "STAGED2=%s (file=%d)\n", staged2, file_exists(staged2));
        }
        if (path_join(res.txn_root, ".dsu_txn/state/new.dsustate", state_txn, (unsigned long)sizeof(state_txn))) {
            fprintf(stderr, "STATE_TXN=%s (file=%d)\n", state_txn, file_exists(state_txn));
        }
        dump_audit_log(ctx);
    }
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "txn apply plan");
    if (!ok) goto done;

    ok &= expect(file_exists(install_f1), "installed file1 exists");
    ok &= expect(file_exists(install_f2), "installed file2 exists");
    ok &= expect(file_exists(state_path), "state file exists");

    ok &= expect(read_all_bytes(install_f1, &bytes, &len), "read installed file1");
    ok &= expect(bytes_equal(bytes, len, (const unsigned char *)"hello\n", 6ul), "file1 bytes match");
    free(bytes);
    bytes = NULL;
    len = 0ul;

    ok &= expect(read_all_bytes(install_f2, &bytes, &len), "read installed file2");
    ok &= expect(bytes_equal(bytes, len, (const unsigned char *)"{\"k\":1}\n", 8ul), "file2 bytes match");
    free(bytes);
    bytes = NULL;
    len = 0ul;

    st = dsu_state_load_file(ctx, state_path, &s);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "state load");
    ok &= expect(s != NULL, "state != NULL");
    if (s) {
        ok &= expect(dsu_state_file_count(s) == dsu_plan_file_count(p), "state file count matches plan");
    }

done:
    if (s) dsu_state_destroy(ctx, s);
    if (p) dsu_plan_destroy(ctx, p);
    if (r) dsu_resolve_result_destroy(ctx, r);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    free(bytes);
    (void)rm_rf(base);
    return ok;
}

static int test_verify_only_mode(void) {
    const char *base = "dsu_test_txn_verify";
    char manifest_path[1024];
    char payload_root[1024];
    char payload_bin_dir[1024];
    char payload_file[1024];
    char install_root[1024];
    char state_path[1024];

    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_resolve_result_t *r = NULL;
    dsu_plan_t *p = NULL;
    dsu_state_t *s = NULL;
    dsu_txn_options_t opts;
    dsu_txn_result_t res;
    dsu_status_t st;
    int ok = 1;

    (void)rm_rf(base);
    ok &= expect(mkdir_p_rel(base), "mkdir base");

    ok &= expect(path_join(base, "payload", payload_root, (unsigned long)sizeof(payload_root)), "join payload root");
    ok &= expect(path_join(payload_root, "bin", payload_bin_dir, (unsigned long)sizeof(payload_bin_dir)), "join payload/bin");
    ok &= expect(mkdir_p_rel(payload_bin_dir), "mkdir payload/bin");
    ok &= expect(path_join(payload_bin_dir, "hello.txt", payload_file, (unsigned long)sizeof(payload_file)), "join payload file");
    ok &= expect(write_bytes_file(payload_file, (const unsigned char *)"hello\n", 6ul), "write payload file");

    ok &= expect(path_join(base, "install", install_root, (unsigned long)sizeof(install_root)), "join install root");
    ok &= expect(path_join(install_root, ".dsu/installed_state.dsustate", state_path, (unsigned long)sizeof(state_path)), "join state path");
    ok &= expect(path_join(base, "m.dsumanifest", manifest_path, (unsigned long)sizeof(manifest_path)), "join manifest path");
    ok &= expect(write_manifest_fileset(manifest_path, install_root, "payload", "core"), "write manifest");
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, manifest_path, &m);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "manifest load");
    if (!ok) goto done;

    {
        const char *const requested[] = {"core"};
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.requested_components = requested;
        req.requested_component_count = 1u;
        st = dsu_resolve_components(ctx, m, NULL, &req, &r);
    }
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "resolve");
    if (!ok) goto done;

    st = dsu_plan_build(ctx, m, manifest_path, r, 0x1111222233334444ULL, &p);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "plan build");
    if (!ok) goto done;

    st = dsu_ctx_reset_audit_log(ctx);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "reset audit log");
    if (!ok) goto done;

    dsu_txn_options_init(&opts);
    dsu_txn_result_init(&res);
    st = dsu_txn_apply_plan(ctx, p, &opts, &res);
    if (st != DSU_STATUS_SUCCESS) {
        dump_audit_log(ctx);
    }
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "install txn");
    if (!ok) goto done;

    st = dsu_state_load_file(ctx, state_path, &s);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "state load");
    if (!ok) goto done;

    dsu_txn_result_init(&res);
    st = dsu_txn_verify_state(ctx, s, &opts, &res);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "verify-only txn");
    ok &= expect(res.verified_ok == dsu_state_file_count(s), "verified_ok equals state file count");
    ok &= expect(res.verified_missing == 0u, "verified_missing == 0");
    ok &= expect(res.verified_mismatch == 0u, "verified_mismatch == 0");

done:
    if (s) dsu_state_destroy(ctx, s);
    if (p) dsu_plan_destroy(ctx, p);
    if (r) dsu_resolve_result_destroy(ctx, r);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    (void)rm_rf(base);
    return ok;
}

static int test_state_roundtrip_and_atomic_save(void) {
    const char *base = "dsu_test_state_roundtrip";
    char manifest_path[1024];
    char payload_root[1024];
    char payload_bin_dir[1024];
    char payload_data_dir[1024];
    char payload_f1[1024];
    char payload_f2[1024];
    char install_root[1024];
    char install_f1[1024];
    char install_f2[1024];
    char state_path[1024];
    char state_mut_path[1024];
    char state_rt_path[1024];

    unsigned char *orig_bytes = NULL;
    unsigned long orig_len = 0ul;
    unsigned char *rt_bytes = NULL;
    unsigned long rt_len = 0ul;
    unsigned char *mut_bytes = NULL;

    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_resolve_result_t *r = NULL;
    dsu_plan_t *p = NULL;
    dsu_state_t *s = NULL;
    dsu_state_t *s_mut = NULL;
    dsu_txn_options_t opts;
    dsu_txn_result_t res;
    dsu_status_t st;
    int ok = 1;

    (void)rm_rf(base);
    ok &= expect(mkdir_p_rel(base), "mkdir base");

    ok &= expect(path_join(base, "payload", payload_root, (unsigned long)sizeof(payload_root)), "join payload root");
    ok &= expect(path_join(payload_root, "bin", payload_bin_dir, (unsigned long)sizeof(payload_bin_dir)), "join payload/bin");
    ok &= expect(path_join(payload_root, "data", payload_data_dir, (unsigned long)sizeof(payload_data_dir)), "join payload/data");
    ok &= expect(mkdir_p_rel(payload_bin_dir), "mkdir payload/bin");
    ok &= expect(mkdir_p_rel(payload_data_dir), "mkdir payload/data");

    ok &= expect(path_join(payload_bin_dir, "hello.txt", payload_f1, (unsigned long)sizeof(payload_f1)), "join payload f1");
    ok &= expect(path_join(payload_data_dir, "config.json", payload_f2, (unsigned long)sizeof(payload_f2)), "join payload f2");
    ok &= expect(write_bytes_file(payload_f1, (const unsigned char *)"hello\n", 6ul), "write payload f1");
    ok &= expect(write_bytes_file(payload_f2, (const unsigned char *)"{\"k\":1}\n", 8ul), "write payload f2");

    ok &= expect(path_join(base, "install", install_root, (unsigned long)sizeof(install_root)), "join install root");
    ok &= expect(path_join(install_root, "bin/hello.txt", install_f1, (unsigned long)sizeof(install_f1)), "join install f1");
    ok &= expect(path_join(install_root, "data/config.json", install_f2, (unsigned long)sizeof(install_f2)), "join install f2");
    ok &= expect(path_join(install_root, ".dsu/installed_state.dsustate", state_path, (unsigned long)sizeof(state_path)), "join state path");
    ok &= expect(path_join(base, "state_mut.dsustate", state_mut_path, (unsigned long)sizeof(state_mut_path)), "join state mut path");
    ok &= expect(path_join(base, "state_roundtrip.dsustate", state_rt_path, (unsigned long)sizeof(state_rt_path)), "join state rt path");

    ok &= expect(path_join(base, "m.dsumanifest", manifest_path, (unsigned long)sizeof(manifest_path)), "join manifest path");
    ok &= expect(write_manifest_fileset(manifest_path, install_root, "payload", "core"), "write manifest");
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, manifest_path, &m);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "manifest load");
    if (!ok) goto done;

    {
        const char *const requested[] = {"core"};
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.requested_components = requested;
        req.requested_component_count = 1u;
        st = dsu_resolve_components(ctx, m, NULL, &req, &r);
    }
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "resolve");
    if (!ok) goto done;

    st = dsu_plan_build(ctx, m, manifest_path, r, 0x1111222233334444ULL, &p);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "plan build");
    if (!ok) goto done;

    st = dsu_ctx_reset_audit_log(ctx);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "reset audit log");
    if (!ok) goto done;

    dsu_txn_options_init(&opts);
    dsu_txn_result_init(&res);
    st = dsu_txn_apply_plan(ctx, p, &opts, &res);
    if (st != DSU_STATUS_SUCCESS) {
        dump_audit_log(ctx);
    }
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "install txn");
    if (!ok) goto done;

    ok &= expect(file_exists(install_f1), "installed f1 exists");
    ok &= expect(file_exists(install_f2), "installed f2 exists");
    ok &= expect(file_exists(state_path), "state exists");
    if (!ok) goto done;

    ok &= expect(read_all_bytes(state_path, &orig_bytes, &orig_len), "read state bytes");
    if (!ok) goto done;

    mut_bytes = (unsigned char *)malloc((size_t)orig_len);
    ok &= expect(mut_bytes != NULL || orig_len == 0ul, "alloc mutated state bytes");
    if (!ok) goto done;
    if (orig_len != 0ul) {
        memcpy(mut_bytes, orig_bytes, (size_t)orig_len);
    }
    ok &= expect(bytes_replace_in_first_match(mut_bytes, orig_len, "bin/hello.txt", (unsigned char)'/', (unsigned char)'\\'),
                 "mutate bin/hello.txt path separators");
    ok &= expect(bytes_replace_in_first_match(mut_bytes, orig_len, "data/config.json", (unsigned char)'/', (unsigned char)'\\'),
                 "mutate data/config.json path separators");
    if (!ok) goto done;

    ok &= expect(write_bytes_file(state_mut_path, mut_bytes, orig_len), "write mutated state");
    if (!ok) goto done;

    st = dsu_state_load_file(ctx, state_path, &s);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "state load");
    if (!ok) goto done;

    st = dsu_state_load_file(ctx, state_mut_path, &s_mut);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "state load (mutated)");
    if (!ok) goto done;

    st = dsu_state_save_atomic(ctx, s_mut, state_rt_path);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "state save_atomic roundtrip");
    if (!ok) goto done;

    ok &= expect(read_all_bytes(state_rt_path, &rt_bytes, &rt_len), "read roundtrip state bytes");
    ok &= expect(bytes_equal(orig_bytes, orig_len, rt_bytes, rt_len), "state bytes stable across canonicalization");
    if (!ok) goto done;

    {
        char *rep_a = NULL;
        char *rep_b = NULL;
        st = dsu_report_list_installed(ctx, s, DSU_REPORT_FORMAT_JSON, &rep_a);
        ok &= expect_st(st, DSU_STATUS_SUCCESS, "list-installed report A");
        st = dsu_report_list_installed(ctx, s, DSU_REPORT_FORMAT_JSON, &rep_b);
        ok &= expect_st(st, DSU_STATUS_SUCCESS, "list-installed report B");
        ok &= expect(rep_a != NULL && rep_b != NULL && strcmp(rep_a, rep_b) == 0, "list-installed deterministic");
        dsu_report_free(ctx, rep_a);
        dsu_report_free(ctx, rep_b);
    }

#if defined(_WIN32)
    {
        char native[1024];
        HANDLE h;
        unsigned char *after_bytes = NULL;
        unsigned long after_len = 0ul;
        ok &= expect(path_to_native_win32(state_path, native, (unsigned long)sizeof(native)), "state path native");
        if (!ok) goto done;
        h = CreateFileA(native, GENERIC_READ, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
        ok &= expect(h != INVALID_HANDLE_VALUE, "lock state file");
        if (!ok) goto done;

        st = dsu_state_save_atomic(ctx, s_mut, state_path);
        ok &= expect(st != DSU_STATUS_SUCCESS, "state save_atomic fails while locked");
        CloseHandle(h);

        ok &= expect(read_all_bytes(state_path, &after_bytes, &after_len), "read state bytes after failed save");
        ok &= expect(bytes_equal(orig_bytes, orig_len, after_bytes, after_len), "failed save_atomic does not corrupt state");
        free(after_bytes);
    }
#endif

done:
    if (s_mut) dsu_state_destroy(ctx, s_mut);
    if (s) dsu_state_destroy(ctx, s);
    if (p) dsu_plan_destroy(ctx, p);
    if (r) dsu_resolve_result_destroy(ctx, r);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    free(orig_bytes);
    free(rt_bytes);
    free(mut_bytes);
    (void)rm_rf(base);
    return ok;
}

static int test_report_verify_detects_missing_and_modified(void) {
    const char *base = "dsu_test_report_verify";
    char manifest_path[1024];
    char payload_root[1024];
    char payload_bin_dir[1024];
    char payload_data_dir[1024];
    char payload_f1[1024];
    char payload_f2[1024];
    char install_root[1024];
    char install_f1[1024];
    char install_f2[1024];
    char user_file[1024];
    char state_path[1024];

    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_resolve_result_t *r = NULL;
    dsu_plan_t *p = NULL;
    dsu_state_t *s = NULL;
    dsu_txn_options_t opts;
    dsu_txn_result_t res;
    dsu_status_t st;
    int ok = 1;

    char *report = NULL;
    dsu_report_verify_summary_t summary;

    (void)rm_rf(base);
    ok &= expect(mkdir_p_rel(base), "mkdir base");

    ok &= expect(path_join(base, "payload", payload_root, (unsigned long)sizeof(payload_root)), "join payload root");
    ok &= expect(path_join(payload_root, "bin", payload_bin_dir, (unsigned long)sizeof(payload_bin_dir)), "join payload/bin");
    ok &= expect(path_join(payload_root, "data", payload_data_dir, (unsigned long)sizeof(payload_data_dir)), "join payload/data");
    ok &= expect(mkdir_p_rel(payload_bin_dir), "mkdir payload/bin");
    ok &= expect(mkdir_p_rel(payload_data_dir), "mkdir payload/data");

    ok &= expect(path_join(payload_bin_dir, "hello.txt", payload_f1, (unsigned long)sizeof(payload_f1)), "join payload f1");
    ok &= expect(path_join(payload_data_dir, "config.json", payload_f2, (unsigned long)sizeof(payload_f2)), "join payload f2");
    ok &= expect(write_bytes_file(payload_f1, (const unsigned char *)"hello\n", 6ul), "write payload f1");
    ok &= expect(write_bytes_file(payload_f2, (const unsigned char *)"{\"k\":1}\n", 8ul), "write payload f2");

    ok &= expect(path_join(base, "install", install_root, (unsigned long)sizeof(install_root)), "join install root");
    ok &= expect(path_join(install_root, "bin/hello.txt", install_f1, (unsigned long)sizeof(install_f1)), "join install f1");
    ok &= expect(path_join(install_root, "data/config.json", install_f2, (unsigned long)sizeof(install_f2)), "join install f2");
    ok &= expect(path_join(install_root, "data/user.txt", user_file, (unsigned long)sizeof(user_file)), "join user file");
    ok &= expect(path_join(install_root, ".dsu/installed_state.dsustate", state_path, (unsigned long)sizeof(state_path)), "join state path");

    ok &= expect(path_join(base, "m.dsumanifest", manifest_path, (unsigned long)sizeof(manifest_path)), "join manifest path");
    ok &= expect(write_manifest_fileset(manifest_path, install_root, "payload", "core"), "write manifest");
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, manifest_path, &m);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "manifest load");
    if (!ok) goto done;

    {
        const char *const requested[] = {"core"};
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.requested_components = requested;
        req.requested_component_count = 1u;
        st = dsu_resolve_components(ctx, m, NULL, &req, &r);
    }
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "resolve");
    if (!ok) goto done;

    st = dsu_plan_build(ctx, m, manifest_path, r, 0x1111222233334444ULL, &p);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "plan build");
    if (!ok) goto done;

    st = dsu_ctx_reset_audit_log(ctx);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "reset audit log");
    if (!ok) goto done;

    dsu_txn_options_init(&opts);
    dsu_txn_result_init(&res);
    st = dsu_txn_apply_plan(ctx, p, &opts, &res);
    if (st != DSU_STATUS_SUCCESS) {
        dump_audit_log(ctx);
    }
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "install txn");
    if (!ok) goto done;

    st = dsu_state_load_file(ctx, state_path, &s);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "state load");
    if (!ok) goto done;

    ok &= expect(write_bytes_file(install_f1, (const unsigned char *)"MOD\n", 4ul), "modify installed file1");
    ok &= expect(remove(install_f2) == 0, "delete installed file2");
    ok &= expect(write_bytes_file(user_file, (const unsigned char *)"USER\n", 5ul), "write extra user file");
    if (!ok) goto done;

    dsu_report_verify_summary_init(&summary);
    st = dsu_report_verify(ctx, s, DSU_REPORT_FORMAT_JSON, &report, &summary);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "report verify");
    ok &= expect(report != NULL, "report verify output");
    ok &= expect(summary.checked == 2u, "verify checked == 2");
    ok &= expect(summary.missing == 1u, "verify missing == 1");
    ok &= expect(summary.modified == 1u, "verify modified == 1");
    ok &= expect(summary.extra >= 1u, "verify extra >= 1");
    ok &= expect(summary.errors == 0u, "verify errors == 0");

done:
    dsu_report_free(ctx, report);
    if (s) dsu_state_destroy(ctx, s);
    if (p) dsu_plan_destroy(ctx, p);
    if (r) dsu_resolve_result_destroy(ctx, r);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    (void)rm_rf(base);
    return ok;
}

static int test_uninstall(void) {
    const char *base = "dsu_test_txn_uninstall";
    char manifest_path[1024];
    char payload_root[1024];
    char payload_bin_dir[1024];
    char payload_file[1024];
    char install_root[1024];
    char install_file[1024];
    char user_file[1024];
    char state_path[1024];

    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_resolve_result_t *r = NULL;
    dsu_plan_t *p = NULL;
    dsu_state_t *s = NULL;
    dsu_txn_options_t opts;
    dsu_txn_result_t res;
    dsu_status_t st;
    int ok = 1;

    char *preview_a = NULL;
    char *preview_b = NULL;

    (void)rm_rf(base);
    ok &= expect(mkdir_p_rel(base), "mkdir base");

    ok &= expect(path_join(base, "payload", payload_root, (unsigned long)sizeof(payload_root)), "join payload root");
    ok &= expect(path_join(payload_root, "bin", payload_bin_dir, (unsigned long)sizeof(payload_bin_dir)), "join payload/bin");
    ok &= expect(mkdir_p_rel(payload_bin_dir), "mkdir payload/bin");
    ok &= expect(path_join(payload_bin_dir, "hello.txt", payload_file, (unsigned long)sizeof(payload_file)), "join payload file");
    ok &= expect(write_bytes_file(payload_file, (const unsigned char *)"hello\n", 6ul), "write payload file");

    ok &= expect(path_join(base, "install", install_root, (unsigned long)sizeof(install_root)), "join install root");
    ok &= expect(path_join(install_root, "bin/hello.txt", install_file, (unsigned long)sizeof(install_file)), "join install file");
    ok &= expect(path_join(install_root, "bin/user.txt", user_file, (unsigned long)sizeof(user_file)), "join user file");
    ok &= expect(path_join(install_root, ".dsu/installed_state.dsustate", state_path, (unsigned long)sizeof(state_path)), "join state path");
    ok &= expect(path_join(base, "m.dsumanifest", manifest_path, (unsigned long)sizeof(manifest_path)), "join manifest path");
    ok &= expect(write_manifest_fileset(manifest_path, install_root, "payload", "core"), "write manifest");
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, manifest_path, &m);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "manifest load");
    if (!ok) goto done;

    {
        const char *const requested[] = {"core"};
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.requested_components = requested;
        req.requested_component_count = 1u;
        st = dsu_resolve_components(ctx, m, NULL, &req, &r);
    }
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "resolve");
    if (!ok) goto done;

    st = dsu_plan_build(ctx, m, manifest_path, r, 0x1111222233334444ULL, &p);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "plan build");
    if (!ok) goto done;

    st = dsu_ctx_reset_audit_log(ctx);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "reset audit log");
    if (!ok) goto done;

    dsu_txn_options_init(&opts);
    dsu_txn_result_init(&res);
    st = dsu_txn_apply_plan(ctx, p, &opts, &res);
    if (st != DSU_STATUS_SUCCESS) {
        dump_audit_log(ctx);
    }
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "install txn");
    if (!ok) goto done;

    ok &= expect(write_bytes_file(user_file, (const unsigned char *)"USER\n", 5ul), "write user file");
    if (!ok) goto done;

    st = dsu_state_load_file(ctx, state_path, &s);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "state load");
    if (!ok) goto done;

    st = dsu_report_uninstall_preview(ctx, s, NULL, 0u, DSU_REPORT_FORMAT_JSON, &preview_a);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "uninstall preview A");
    st = dsu_report_uninstall_preview(ctx, s, NULL, 0u, DSU_REPORT_FORMAT_JSON, &preview_b);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "uninstall preview B");
    ok &= expect(preview_a != NULL && preview_b != NULL && strcmp(preview_a, preview_b) == 0, "uninstall preview deterministic");
    ok &= expect(preview_a != NULL && strstr(preview_a, "bin/hello.txt") != NULL, "uninstall preview lists owned file");
    ok &= expect(preview_a != NULL && strstr(preview_a, "bin/user.txt") == NULL, "uninstall preview excludes user file");
    if (!ok) goto done;

    dsu_txn_result_init(&res);
    st = dsu_txn_uninstall_state(ctx, s, state_path, &opts, &res);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "uninstall txn");
    if (!ok) goto done;

    ok &= expect(!file_exists(install_file), "installed file removed");
    ok &= expect(!file_exists(state_path), "state file removed");
    ok &= expect(file_exists(user_file), "user file preserved");

done:
    dsu_report_free(ctx, preview_a);
    dsu_report_free(ctx, preview_b);
    if (s) dsu_state_destroy(ctx, s);
    if (p) dsu_plan_destroy(ctx, p);
    if (r) dsu_resolve_result_destroy(ctx, r);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    (void)rm_rf(base);
    return ok;
}

static int test_failed_install_rollback_pristine(void) {
    const char *base = "dsu_test_txn_fail_rollback";
    char manifest_path[1024];
    char payload_root[1024];
    char payload_bin_dir[1024];
    char payload_file[1024];
    char install_root[1024];
    char install_bin_dir[1024];
    char install_file[1024];
    char state_path[1024];

    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_resolve_result_t *r = NULL;
    dsu_plan_t *p = NULL;
    dsu_txn_options_t opts;
    dsu_txn_result_t res;
    dsu_status_t st;
    snap_t before;
    snap_t after;
    int ok = 1;

    memset(&before, 0, sizeof(before));
    memset(&after, 0, sizeof(after));

    (void)rm_rf(base);
    ok &= expect(mkdir_p_rel(base), "mkdir base");

    ok &= expect(path_join(base, "payload", payload_root, (unsigned long)sizeof(payload_root)), "join payload root");
    ok &= expect(path_join(payload_root, "bin", payload_bin_dir, (unsigned long)sizeof(payload_bin_dir)), "join payload/bin");
    ok &= expect(mkdir_p_rel(payload_bin_dir), "mkdir payload/bin");
    ok &= expect(path_join(payload_bin_dir, "hello.txt", payload_file, (unsigned long)sizeof(payload_file)), "join payload file");
    ok &= expect(write_bytes_file(payload_file, (const unsigned char *)"NEW\n", 4ul), "write payload file");

    ok &= expect(path_join(base, "install", install_root, (unsigned long)sizeof(install_root)), "join install root");
    ok &= expect(path_join(install_root, "bin", install_bin_dir, (unsigned long)sizeof(install_bin_dir)), "join install/bin");
    ok &= expect(mkdir_p_rel(install_bin_dir), "mkdir install/bin");
    ok &= expect(path_join(install_bin_dir, "hello.txt", install_file, (unsigned long)sizeof(install_file)), "join install file");
    ok &= expect(write_bytes_file(install_file, (const unsigned char *)"OLD\n", 4ul), "write preexisting file");

    ok &= expect(path_join(install_root, ".dsu/installed_state.dsustate", state_path, (unsigned long)sizeof(state_path)), "join state path");
    ok &= expect(!file_exists(state_path), "state does not exist before txn");

    ok &= expect(path_join(base, "m.dsumanifest", manifest_path, (unsigned long)sizeof(manifest_path)), "join manifest path");
    ok &= expect(write_manifest_fileset(manifest_path, install_root, "payload", "core"), "write manifest");
    if (!ok) goto done;

    ok &= expect(snap_build(install_root, &before), "snapshot before");
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, manifest_path, &m);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "manifest load");
    if (!ok) goto done;

    {
        const char *const requested[] = {"core"};
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.requested_components = requested;
        req.requested_component_count = 1u;
        st = dsu_resolve_components(ctx, m, NULL, &req, &r);
    }
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "resolve");
    if (!ok) goto done;

    st = dsu_plan_build(ctx, m, manifest_path, r, 0x1111222233334444ULL, &p);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "plan build");
    if (!ok) goto done;

    dsu_txn_options_init(&opts);
    opts.fail_after_entries = 4u; /* after backing up old file, before moving new file into place */
    dsu_txn_result_init(&res);
    st = dsu_txn_apply_plan(ctx, p, &opts, &res);
    ok &= expect(st != DSU_STATUS_SUCCESS, "txn fails (injected)");
    ok &= expect(!file_exists(state_path), "state not written on failed commit");
    if (!ok) goto done;

    ok &= expect(snap_build(install_root, &after), "snapshot after");
    ok &= expect(snap_equal(&before, &after), "rollback restores pristine tree");

done:
    snap_free(&before);
    snap_free(&after);
    if (p) dsu_plan_destroy(ctx, p);
    if (r) dsu_resolve_result_destroy(ctx, r);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    (void)rm_rf(base);
    return ok;
}

static int test_journal_roundtrip(void) {
    const char *path = "dsu_test_journal.dsujournal";
    char cwd[1024];
    char install_root[1024];
    char txn_root[1024];
    dsu_journal_writer_t w;
    dsu_ctx_t *ctx = NULL;
    dsu_journal_t *j = NULL;
    dsu_status_t st;
    int ok = 1;

    memset(&w, 0, sizeof(w));
    memset(cwd, 0, sizeof(cwd));
    memset(install_root, 0, sizeof(install_root));
    memset(txn_root, 0, sizeof(txn_root));

    ok &= expect(dsu_platform_get_cwd(cwd, (dsu_u32)sizeof(cwd)) == DSU_STATUS_SUCCESS, "get cwd (journal)");
    ok &= expect(path_join(cwd, "jr_install", install_root, (unsigned long)sizeof(install_root)), "join install_root");
    ok &= expect(path_join(cwd, "jr_txn", txn_root, (unsigned long)sizeof(txn_root)), "join txn_root");
    if (!ok) return 0;

    (void)rm_rf(install_root);
    (void)rm_rf(txn_root);
    ok &= expect(dsu_platform_mkdir(install_root) == DSU_STATUS_SUCCESS, "mkdir install_root");
    ok &= expect(dsu_platform_mkdir(txn_root) == DSU_STATUS_SUCCESS, "mkdir txn_root");
    if (!ok) return 0;

    st = dsu_journal_writer_open(&w, path, 0x1111222233334444ULL, 0xAAAABBBBCCCCDDDDULL);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "journal open");
    st = dsu_journal_writer_write_meta(&w, install_root, txn_root, ".dsu/installed_state.dsustate");
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "journal meta");
    st = dsu_journal_writer_append_entry(&w,
                                         (dsu_u16)DSU_JOURNAL_ENTRY_CREATE_DIR,
                                         (dsu_u8)DSU_JOURNAL_ROOT_INSTALL,
                                         "bin",
                                         (dsu_u8)DSU_JOURNAL_ROOT_INSTALL,
                                         "",
                                         (dsu_u8)DSU_JOURNAL_ROOT_INSTALL,
                                         "",
                                         0u);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "journal entry create_dir");
    st = dsu_journal_writer_append_entry(&w,
                                         (dsu_u16)DSU_JOURNAL_ENTRY_MOVE_FILE,
                                         (dsu_u8)DSU_JOURNAL_ROOT_INSTALL,
                                         "bin/hello.txt",
                                         (dsu_u8)DSU_JOURNAL_ROOT_TXN,
                                         "bin/hello.txt",
                                         (dsu_u8)DSU_JOURNAL_ROOT_INSTALL,
                                         "bin/hello.txt",
                                         (dsu_u32)DSU_JOURNAL_FLAG_TARGET_PREEXISTED);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "journal entry move_file");
    st = dsu_journal_writer_append_entry(&w,
                                         (dsu_u16)DSU_JOURNAL_ENTRY_WRITE_STATE,
                                         (dsu_u8)DSU_JOURNAL_ROOT_INSTALL,
                                         ".dsu/installed_state.dsustate",
                                         (dsu_u8)DSU_JOURNAL_ROOT_INSTALL,
                                         "",
                                         (dsu_u8)DSU_JOURNAL_ROOT_INSTALL,
                                         ".dsu/installed_state.dsustate",
                                         0u);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "journal entry write_state");
    st = dsu_journal_writer_append_progress(&w, 2u);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "journal progress");
    st = dsu_journal_writer_close(&w);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "journal close");
    if (!ok) goto done;

    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create (journal)");
    if (!ok) goto done;

    st = dsu_journal_read_file(ctx, path, &j);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "journal read");
    ok &= expect(j != NULL, "journal read non-null");
    if (!ok) goto done;

    ok &= expect(j->journal_id == 0x1111222233334444ULL, "journal id");
    ok &= expect(j->plan_digest == 0xAAAABBBBCCCCDDDDULL, "journal digest");
    ok &= expect(j->entry_count == 3u, "journal entry_count");
    ok &= expect(j->commit_progress == 2u, "journal progress");
    ok &= expect(j->install_root != NULL && strstr(j->install_root, "jr_install") != NULL, "journal install_root");
    ok &= expect(j->txn_root != NULL && strstr(j->txn_root, "jr_txn") != NULL, "journal txn_root");
    ok &= expect(j->state_path != NULL && strcmp(j->state_path, ".dsu/installed_state.dsustate") == 0, "journal state_path");
    ok &= expect(j->entries[0].type == (dsu_u16)DSU_JOURNAL_ENTRY_CREATE_DIR, "journal entry[0] type");
    ok &= expect(j->entries[1].type == (dsu_u16)DSU_JOURNAL_ENTRY_MOVE_FILE, "journal entry[1] type");
    ok &= expect(j->entries[2].type == (dsu_u16)DSU_JOURNAL_ENTRY_WRITE_STATE, "journal entry[2] type");

done:
    if (j && ctx) dsu_journal_destroy(ctx, j);
    if (ctx) dsu_ctx_destroy(ctx);
    remove(path);
    (void)rm_rf(install_root);
    (void)rm_rf(txn_root);
    return ok;
}

static int test_failpoint_rollback_pristine(void) {
    const char *failpoints[] = {
        "after_stage_write",
        "after_verify",
        "mid_commit:1",
        "before_state_write"
    };
    dsu_u32 fp_count = (dsu_u32)(sizeof(failpoints) / sizeof(failpoints[0]));
    dsu_u32 fi;
    int ok = 1;

    for (fi = 0u; fi < fp_count; ++fi) {
        const char *base = "dsu_test_txn_failpoints";
        char manifest_path[1024];
        char payload_root[1024];
        char payload_bin_dir[1024];
        char payload_file[1024];
        char install_root[1024];
        char install_bin_dir[1024];
        char install_file[1024];
        char state_path[1024];

        dsu_ctx_t *ctx = NULL;
        dsu_manifest_t *m = NULL;
        dsu_resolve_result_t *r = NULL;
        dsu_plan_t *p = NULL;
        dsu_txn_options_t opts;
        dsu_txn_result_t res;
        dsu_status_t st;
        snap_t before;
        snap_t after;

        memset(&before, 0, sizeof(before));
        memset(&after, 0, sizeof(after));

        (void)rm_rf(base);
        ok &= expect(mkdir_p_rel(base), "mkdir base (failpoints)");

        ok &= expect(path_join(base, "payload", payload_root, (unsigned long)sizeof(payload_root)), "join payload root");
        ok &= expect(path_join(payload_root, "bin", payload_bin_dir, (unsigned long)sizeof(payload_bin_dir)), "join payload/bin");
        ok &= expect(mkdir_p_rel(payload_bin_dir), "mkdir payload/bin");
        ok &= expect(path_join(payload_bin_dir, "hello.txt", payload_file, (unsigned long)sizeof(payload_file)), "join payload file");
        ok &= expect(write_bytes_file(payload_file, (const unsigned char *)"NEW\n", 4ul), "write payload file");

        ok &= expect(path_join(base, "install", install_root, (unsigned long)sizeof(install_root)), "join install root");
        ok &= expect(path_join(install_root, "bin", install_bin_dir, (unsigned long)sizeof(install_bin_dir)), "join install/bin");
        ok &= expect(mkdir_p_rel(install_bin_dir), "mkdir install/bin");
        ok &= expect(path_join(install_bin_dir, "hello.txt", install_file, (unsigned long)sizeof(install_file)), "join install file");
        ok &= expect(write_bytes_file(install_file, (const unsigned char *)"OLD\n", 4ul), "write preexisting file");

        ok &= expect(path_join(install_root, ".dsu/installed_state.dsustate", state_path, (unsigned long)sizeof(state_path)), "join state path");
        ok &= expect(!file_exists(state_path), "state does not exist before txn");

        ok &= expect(path_join(base, "m.dsumanifest", manifest_path, (unsigned long)sizeof(manifest_path)), "join manifest path");
        ok &= expect(write_manifest_fileset(manifest_path, install_root, "payload", "core"), "write manifest");
        if (!ok) goto fp_done;

        ok &= expect(snap_build(install_root, &before), "snapshot before (failpoints)");
        if (!ok) goto fp_done;

        ctx = create_ctx_deterministic();
        ok &= expect(ctx != NULL, "ctx create (failpoints)");
        if (!ok) goto fp_done;

        st = dsu_manifest_load_file(ctx, manifest_path, &m);
        ok &= expect_st(st, DSU_STATUS_SUCCESS, "manifest load (failpoints)");
        if (!ok) goto fp_done;

        {
            const char *const requested[] = {"core"};
            dsu_resolve_request_t req;
            dsu_resolve_request_init(&req);
            req.operation = DSU_RESOLVE_OPERATION_INSTALL;
            req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
            req.requested_components = requested;
            req.requested_component_count = 1u;
            st = dsu_resolve_components(ctx, m, NULL, &req, &r);
        }
        ok &= expect_st(st, DSU_STATUS_SUCCESS, "resolve (failpoints)");
        if (!ok) goto fp_done;

        st = dsu_plan_build(ctx, m, manifest_path, r, 0x1111222233334444ULL, &p);
        ok &= expect_st(st, DSU_STATUS_SUCCESS, "plan build (failpoints)");
        if (!ok) goto fp_done;

        dsu_txn_options_init(&opts);
        dsu_txn_result_init(&res);
        ok &= expect(set_env_var("DSU_FAILPOINT", failpoints[fi]), "set DSU_FAILPOINT");
        st = dsu_txn_apply_plan(ctx, p, &opts, &res);
        ok &= expect(set_env_var("DSU_FAILPOINT", ""), "clear DSU_FAILPOINT");
        ok &= expect(st != DSU_STATUS_SUCCESS, "txn fails (failpoint)");
        ok &= expect(!file_exists(state_path), "state not written on failpoint");
        if (!ok) goto fp_done;

        ok &= expect(snap_build(install_root, &after), "snapshot after (failpoints)");
        ok &= expect(snap_equal(&before, &after), "rollback restores pristine tree (failpoints)");

fp_done:
        snap_free(&before);
        snap_free(&after);
        if (p) dsu_plan_destroy(ctx, p);
        if (r) dsu_resolve_result_destroy(ctx, r);
        if (m) dsu_manifest_destroy(ctx, m);
        if (ctx) dsu_ctx_destroy(ctx);
        (void)rm_rf(base);
        if (!ok) break;
    }

    return ok;
}

int main(void) {
    int ok = 1;
    ok &= test_path_traversal_rejection();
    ok &= test_fresh_install();
    ok &= test_verify_only_mode();
    ok &= test_state_roundtrip_and_atomic_save();
    ok &= test_report_verify_detects_missing_and_modified();
    ok &= test_uninstall();
    ok &= test_failed_install_rollback_pristine();
    ok &= test_journal_roundtrip();
    ok &= test_failpoint_rollback_pristine();
    return ok ? 0 : 1;
}
