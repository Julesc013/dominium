/*
FILE: source/dominium/setup/core/src/fs/dsu_fs.c
MODULE: Dominium Setup
PURPOSE: Strict, root-scoped filesystem abstraction for journaled transactions (Plan S-4).
*/
#include "../../include/dsu/dsu_fs.h"

#include "dsu_platform_iface.h"
#include "../util/dsu_util_internal.h"

#include <stdio.h>
#include <string.h>

struct dsu_fs {
    dsu_u32 root_count;
    char **roots; /* canonical absolute roots */
};

void dsu_fs_options_init(dsu_fs_options_t *opts) {
    if (!opts) {
        return;
    }
    memset(opts, 0, sizeof(*opts));
    opts->struct_size = (dsu_u32)sizeof(*opts);
    opts->struct_version = 1u;
}

static int dsu__is_alpha(char c) {
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z');
}

static char dsu__to_lower(char c) {
    if (c >= 'A' && c <= 'Z') {
        return (char)(c - 'A' + 'a');
    }
    return c;
}

static int dsu__is_abs_drive_path(const char *p) {
    if (!p) return 0;
    if (!dsu__is_alpha(p[0]) || p[1] != ':') return 0;
    if (p[2] == '/' || p[2] == '\\') return 1;
    return 0;
}

static int dsu__is_abs_unc_path(const char *p) {
    if (!p) return 0;
    if ((p[0] == '\\' && p[1] == '\\') || (p[0] == '/' && p[1] == '/')) {
        return 1;
    }
    return 0;
}

static int dsu__is_abs_posix_path(const char *p) {
    if (!p) return 0;
    return (p[0] == '/' || p[0] == '\\');
}

static int dsu__is_abs_path(const char *p) {
    return dsu__is_abs_drive_path(p) || dsu__is_abs_unc_path(p) || dsu__is_abs_posix_path(p);
}

static int dsu__contains_forbidden_char(const char *p, dsu_u8 allow_drive_prefix) {
    dsu_u32 i = 0u;
    const unsigned char *s = (const unsigned char *)(p ? p : "");
    while (s[i]) {
        unsigned char c = s[i];
        if (c < 0x20u) {
            return 1;
        }
        if (c == ':') {
            if (!(allow_drive_prefix && i == 1u && dsu__is_alpha((char)s[0]))) {
                return 1;
            }
        }
        ++i;
    }
    return 0;
}

static dsu_status_t dsu__path_canon(const char *in,
                                    char *out,
                                    dsu_u32 out_cap,
                                    dsu_u8 allow_absolute,
                                    dsu_u8 allow_empty) {
    dsu_u32 i;
    dsu_u32 o;
    dsu_u32 in_len;
    dsu_u8 prefix_drive = 0u;
    dsu_u8 prefix_unc = 0u;
    dsu_u8 prefix_root = 0u;
    dsu_u32 start;

    if (!in || !out || out_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    out[0] = '\0';

    in_len = dsu__strlen(in);
    if (in_len == 0xFFFFFFFFu) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (in_len == 0u) {
        return allow_empty ? DSU_STATUS_SUCCESS : DSU_STATUS_INVALID_ARGS;
    }
    if (dsu__contains_forbidden_char(in, allow_absolute ? 1u : 0u)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!allow_absolute && dsu__is_abs_path(in)) {
        return DSU_STATUS_INVALID_ARGS;
    }

    o = 0u;
    start = 0u;

    if (allow_absolute && dsu__is_abs_drive_path(in)) {
        if (out_cap < 4u) {
            return DSU_STATUS_INVALID_ARGS;
        }
        out[o++] = dsu__to_lower(in[0]);
        out[o++] = ':';
        out[o++] = '/';
        prefix_drive = 1u;
        start = 3u;
        while (start < in_len && (in[start] == '/' || in[start] == '\\')) {
            ++start;
        }
    } else if (allow_absolute && dsu__is_abs_unc_path(in)) {
        if (out_cap < 3u) {
            return DSU_STATUS_INVALID_ARGS;
        }
        out[o++] = '/';
        out[o++] = '/';
        prefix_unc = 1u;
        start = 2u;
        while (start < in_len && (in[start] == '/' || in[start] == '\\')) {
            ++start;
        }
    } else if (allow_absolute && dsu__is_abs_posix_path(in)) {
        if (out_cap < 2u) {
            return DSU_STATUS_INVALID_ARGS;
        }
        out[o++] = '/';
        prefix_root = 1u;
        start = 1u;
        while (start < in_len && (in[start] == '/' || in[start] == '\\')) {
            ++start;
        }
    }

    {
        dsu_u32 seg_start = start;
        for (i = start; i <= in_len; ++i) {
            char c = (i < in_len) ? in[i] : '\0';
            if (c == '\\') c = '/';
            if (c == '/' || c == '\0') {
                dsu_u32 seg_len = (dsu_u32)(i - seg_start);
                if (seg_len == 0u) {
                    /* skip */
                } else if (seg_len == 1u && in[seg_start] == '.') {
                    /* skip '.' */
                } else if (seg_len == 2u && in[seg_start] == '.' && in[seg_start + 1u] == '.') {
                    return DSU_STATUS_INVALID_ARGS;
                } else {
                    if (o != 0u && out[o - 1u] != '/') {
                        if (o + 1u >= out_cap) {
                            return DSU_STATUS_INVALID_ARGS;
                        }
                        out[o++] = '/';
                    }
                    for (; seg_start < i; ++seg_start) {
                        char cc = in[seg_start];
                        if (cc == '\\') cc = '/';
                        if (cc == '\0') {
                            return DSU_STATUS_INVALID_ARGS;
                        }
                        if (!allow_absolute && cc == ':') {
                            return DSU_STATUS_INVALID_ARGS;
                        }
                        if (o + 1u >= out_cap) {
                            return DSU_STATUS_INVALID_ARGS;
                        }
                        out[o++] = cc;
                    }
                }
                seg_start = i + 1u;
            }
        }
    }

    /* Trim trailing '/' unless it's a root prefix. */
    if (o > 1u && out[o - 1u] == '/') {
        if (prefix_drive) {
            if (o > 3u) {
                --o;
            }
        } else if (prefix_unc) {
            if (o > 2u) {
                --o;
            }
        } else if (prefix_root) {
            if (o > 1u) {
                --o;
            }
        } else {
            --o;
        }
    }
    out[o] = '\0';

    if (!allow_empty && out[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_fs_path_canonicalize(const char *path_in, char *path_out, dsu_u32 path_out_cap) {
    return dsu__path_canon(path_in, path_out, path_out_cap, 1u, 0u);
}

dsu_status_t dsu_fs_path_join(const char *a, const char *b, char *out_path, dsu_u32 out_cap) {
    char tmp[2048];
    dsu_u32 na;
    dsu_u32 nb;
    if (!a || !b || !out_path || out_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    na = dsu__strlen(a);
    nb = dsu__strlen(b);
    if (na == 0xFFFFFFFFu || nb == 0xFFFFFFFFu) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (na + 1u + nb + 1u > (dsu_u32)sizeof(tmp)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    memcpy(tmp, a, (size_t)na);
    tmp[na] = '/';
    memcpy(tmp + na + 1u, b, (size_t)nb);
    tmp[na + 1u + nb] = '\0';
    return dsu_fs_path_canonicalize(tmp, out_path, out_cap);
}

dsu_status_t dsu_fs_path_split(const char *path,
                               char *out_dir,
                               dsu_u32 out_dir_cap,
                               char *out_base,
                               dsu_u32 out_base_cap) {
    const char *last;
    dsu_u32 dir_len;
    dsu_u32 base_len;

    if (!path || !out_dir || !out_base || out_dir_cap == 0u || out_base_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    out_dir[0] = '\0';
    out_base[0] = '\0';

    last = strrchr(path, '/');
    if (!last) {
        base_len = dsu__strlen(path);
        if (base_len == 0xFFFFFFFFu || base_len + 1u > out_base_cap) {
            return DSU_STATUS_INVALID_ARGS;
        }
        memcpy(out_base, path, (size_t)base_len);
        out_base[base_len] = '\0';
        return DSU_STATUS_SUCCESS;
    }

    dir_len = (dsu_u32)(last - path);
    base_len = dsu__strlen(last + 1);
    if (base_len == 0xFFFFFFFFu) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (dir_len + 1u > out_dir_cap || base_len + 1u > out_base_cap) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (dir_len) {
        memcpy(out_dir, path, (size_t)dir_len);
    }
    out_dir[dir_len] = '\0';
    if (base_len) {
        memcpy(out_base, last + 1, (size_t)base_len);
    }
    out_base[base_len] = '\0';
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__dup_cstr(const char *s, char **out) {
    dsu_u32 n;
    char *p;
    if (!out) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out = NULL;
    if (!s) {
        return DSU_STATUS_INVALID_ARGS;
    }
    n = dsu__strlen(s);
    if (n == 0xFFFFFFFFu) {
        return DSU_STATUS_INVALID_ARGS;
    }
    p = (char *)dsu__malloc(n + 1u);
    if (!p) {
        return DSU_STATUS_IO_ERROR;
    }
    if (n) {
        memcpy(p, s, (size_t)n);
    }
    p[n] = '\0';
    *out = p;
    return DSU_STATUS_SUCCESS;
}

static void dsu__fs_free(dsu_fs_t *fs) {
    dsu_u32 i;
    if (!fs) {
        return;
    }
    for (i = 0u; i < fs->root_count; ++i) {
        dsu__free(fs->roots[i]);
        fs->roots[i] = NULL;
    }
    dsu__free(fs->roots);
    fs->roots = NULL;
    fs->root_count = 0u;
}

dsu_status_t dsu_fs_create(dsu_ctx_t *ctx, const dsu_fs_options_t *opts, dsu_fs_t **out_fs) {
    dsu_fs_t *fs;
    dsu_u32 i;
    (void)ctx;

    if (!opts || !out_fs) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (opts->struct_version != 1u || opts->struct_size < (dsu_u32)sizeof(*opts)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!opts->allowed_roots && opts->allowed_root_count != 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }

    fs = (dsu_fs_t *)dsu__malloc((dsu_u32)sizeof(*fs));
    if (!fs) {
        return DSU_STATUS_IO_ERROR;
    }
    memset(fs, 0, sizeof(*fs));

    fs->root_count = opts->allowed_root_count;
    fs->roots = (char **)dsu__malloc(fs->root_count * (dsu_u32)sizeof(*fs->roots));
    if (!fs->roots && fs->root_count != 0u) {
        dsu__free(fs);
        return DSU_STATUS_IO_ERROR;
    }
    if (fs->root_count) {
        memset(fs->roots, 0, (size_t)fs->root_count * sizeof(*fs->roots));
    }

    for (i = 0u; i < fs->root_count; ++i) {
        char canon[1024];
        dsu_status_t st;
        const char *root = opts->allowed_roots[i];
        if (!root || root[0] == '\0') {
            dsu_fs_destroy(ctx, fs);
            return DSU_STATUS_INVALID_ARGS;
        }
        st = dsu__path_canon(root, canon, (dsu_u32)sizeof(canon), 1u, 0u);
        if (st != DSU_STATUS_SUCCESS) {
            dsu_fs_destroy(ctx, fs);
            return st;
        }
        if (!dsu__is_abs_path(canon)) {
            dsu_fs_destroy(ctx, fs);
            return DSU_STATUS_INVALID_ARGS;
        }
        st = dsu__dup_cstr(canon, &fs->roots[i]);
        if (st != DSU_STATUS_SUCCESS) {
            dsu_fs_destroy(ctx, fs);
            return st;
        }
    }

    *out_fs = fs;
    return DSU_STATUS_SUCCESS;
}

void dsu_fs_destroy(dsu_ctx_t *ctx, dsu_fs_t *fs) {
    (void)ctx;
    if (!fs) {
        return;
    }
    dsu__fs_free(fs);
    dsu__free(fs);
}

dsu_u32 dsu_fs_allowed_root_count(const dsu_fs_t *fs) {
    if (!fs) {
        return 0u;
    }
    return fs->root_count;
}

const char *dsu_fs_allowed_root(const dsu_fs_t *fs, dsu_u32 index) {
    if (!fs || index >= fs->root_count) {
        return NULL;
    }
    return fs->roots[index];
}

static dsu_status_t dsu__canon_rel(const char *rel_in, char *rel_out, dsu_u32 rel_out_cap) {
    dsu_status_t st;
    if (!rel_in || !rel_out || rel_out_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (dsu__is_abs_path(rel_in)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    st = dsu__path_canon(rel_in, rel_out, rel_out_cap, 0u, 1u);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (rel_out[0] != '\0' && dsu__is_abs_path(rel_out)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__join_root_rel(const char *root, const char *rel, char *out_abs, dsu_u32 out_cap) {
    dsu_u32 nr;
    dsu_u32 nl;
    if (!root || !rel || !out_abs || out_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    nr = dsu__strlen(root);
    nl = dsu__strlen(rel);
    if (nr == 0xFFFFFFFFu || nl == 0xFFFFFFFFu) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (rel[0] == '\0') {
        if (nr + 1u > out_cap) {
            return DSU_STATUS_INVALID_ARGS;
        }
        memcpy(out_abs, root, (size_t)nr);
        out_abs[nr] = '\0';
        return DSU_STATUS_SUCCESS;
    }
    if (nr + 1u + nl + 1u > out_cap) {
        return DSU_STATUS_INVALID_ARGS;
    }
    memcpy(out_abs, root, (size_t)nr);
    out_abs[nr] = '/';
    memcpy(out_abs + nr + 1u, rel, (size_t)nl);
    out_abs[nr + 1u + nl] = '\0';
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__validate_no_symlink_prefixes(const char *abs_root, const char *rel) {
    char tmp[1024];
    dsu_u32 root_len;
    dsu_u32 rel_len;
    dsu_u32 i;
    dsu_u32 o;
    dsu_u8 exists;
    dsu_u8 is_dir;
    dsu_u8 is_symlink;

    if (!abs_root || !rel) {
        return DSU_STATUS_INVALID_ARGS;
    }
    root_len = dsu__strlen(abs_root);
    rel_len = dsu__strlen(rel);
    if (root_len == 0xFFFFFFFFu || rel_len == 0xFFFFFFFFu) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (root_len + 1u + rel_len + 1u > (dsu_u32)sizeof(tmp)) {
        return DSU_STATUS_INVALID_ARGS;
    }

    memcpy(tmp, abs_root, (size_t)root_len);
    o = root_len;
    tmp[o] = '\0';

    if (dsu_platform_path_info(tmp, &exists, &is_dir, &is_symlink) == DSU_STATUS_SUCCESS) {
        if (exists && is_symlink) {
            return DSU_STATUS_INVALID_ARGS;
        }
    }

    if (rel[0] == '\0') {
        return DSU_STATUS_SUCCESS;
    }
    if (o + 1u >= (dsu_u32)sizeof(tmp)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    tmp[o++] = '/';
    tmp[o] = '\0';

    for (i = 0u; i <= rel_len; ++i) {
        char c = (i < rel_len) ? rel[i] : '\0';
        if (c == '/' || c == '\0') {
            if (dsu_platform_path_info(tmp, &exists, &is_dir, &is_symlink) == DSU_STATUS_SUCCESS) {
                if (exists && is_symlink) {
                    return DSU_STATUS_INVALID_ARGS;
                }
                if (!exists) {
                    /* Remaining prefixes cannot exist if this one doesn't. */
                    return DSU_STATUS_SUCCESS;
                }
            }
            if (c == '\0') {
                break;
            }
            if (o + 1u >= (dsu_u32)sizeof(tmp)) {
                return DSU_STATUS_INVALID_ARGS;
            }
            tmp[o++] = '/';
            tmp[o] = '\0';
        } else {
            if (o + 1u >= (dsu_u32)sizeof(tmp)) {
                return DSU_STATUS_INVALID_ARGS;
            }
            tmp[o++] = c;
            tmp[o] = '\0';
        }
    }
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_fs_resolve_under_root(dsu_fs_t *fs,
                                      dsu_u32 root_index,
                                      const char *rel,
                                      char *out_abs,
                                      dsu_u32 out_abs_cap) {
    char canon_rel[1024];
    char abs[1024];
    dsu_status_t st;
    if (!fs || root_index >= fs->root_count || !rel || !out_abs || out_abs_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    st = dsu__canon_rel(rel, canon_rel, (dsu_u32)sizeof(canon_rel));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu__join_root_rel(fs->roots[root_index], canon_rel, abs, (dsu_u32)sizeof(abs));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu__validate_no_symlink_prefixes(fs->roots[root_index], canon_rel);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (dsu__strlen(abs) + 1u > out_abs_cap) {
        return DSU_STATUS_INVALID_ARGS;
    }
    memcpy(out_abs, abs, (size_t)dsu__strlen(abs) + 1u);
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_fs_mkdir_p(dsu_fs_t *fs, dsu_u32 root_index, const char *rel_dir) {
    char canon_rel[1024];
    char abs[1024];
    dsu_u32 i;
    dsu_u32 len;
    dsu_status_t st;

    if (!fs || root_index >= fs->root_count || !rel_dir) {
        return DSU_STATUS_INVALID_ARGS;
    }
    st = dsu__canon_rel(rel_dir, canon_rel, (dsu_u32)sizeof(canon_rel));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    /* Ensure root exists. */
    st = dsu_platform_mkdir(fs->roots[root_index]);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (canon_rel[0] == '\0') {
        return DSU_STATUS_SUCCESS;
    }

    len = dsu__strlen(canon_rel);
    if (len == 0xFFFFFFFFu) {
        return DSU_STATUS_INVALID_ARGS;
    }

    for (i = 0u; i <= len; ++i) {
        char c = (i < len) ? canon_rel[i] : '\0';
        if (c == '/' || c == '\0') {
            char part[1024];
            if (i >= (dsu_u32)sizeof(part)) {
                return DSU_STATUS_INVALID_ARGS;
            }
            memcpy(part, canon_rel, (size_t)i);
            part[i] = '\0';
            st = dsu_fs_resolve_under_root(fs, root_index, part, abs, (dsu_u32)sizeof(abs));
            if (st != DSU_STATUS_SUCCESS) {
                return st;
            }
            st = dsu_platform_mkdir(abs);
            if (st != DSU_STATUS_SUCCESS) {
                return st;
            }
        }
    }
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_fs_rmdir_empty(dsu_fs_t *fs, dsu_u32 root_index, const char *rel_dir) {
    char abs[1024];
    dsu_status_t st;
    dsu_u8 exists;
    dsu_u8 is_dir;
    dsu_u8 is_symlink;
    dsu_platform_dir_entry_t *entries = NULL;
    dsu_u32 entry_count = 0u;

    if (!fs || root_index >= fs->root_count || !rel_dir) {
        return DSU_STATUS_INVALID_ARGS;
    }
    st = dsu_fs_resolve_under_root(fs, root_index, rel_dir, abs, (dsu_u32)sizeof(abs));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu_platform_path_info(abs, &exists, &is_dir, &is_symlink);
    if (st == DSU_STATUS_SUCCESS && !exists) {
        return DSU_STATUS_SUCCESS;
    }
    if (st == DSU_STATUS_SUCCESS && (!is_dir || is_symlink)) {
        return DSU_STATUS_IO_ERROR;
    }

    /* Best-effort safety: only remove if currently empty. */
    st = dsu_platform_list_dir(abs, &entries, &entry_count);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (entry_count != 0u) {
        dsu_platform_free_dir_entries(entries, entry_count);
        return DSU_STATUS_SUCCESS;
    }
    dsu_platform_free_dir_entries(entries, entry_count);
    return dsu_platform_rmdir(abs);
}

static dsu_status_t dsu__copy_file_stdio(const char *src_abs, const char *dst_abs) {
    FILE *in;
    FILE *out;
    unsigned char buf[32768];
    size_t n;

    if (!src_abs || !dst_abs) {
        return DSU_STATUS_INVALID_ARGS;
    }
    in = fopen(src_abs, "rb");
    if (!in) {
        return DSU_STATUS_IO_ERROR;
    }
    out = fopen(dst_abs, "wb");
    if (!out) {
        fclose(in);
        return DSU_STATUS_IO_ERROR;
    }
    while ((n = fread(buf, 1u, sizeof(buf), in)) != 0u) {
        if (fwrite(buf, 1u, n, out) != n) {
            fclose(in);
            fclose(out);
            return DSU_STATUS_IO_ERROR;
        }
    }
    if (ferror(in)) {
        fclose(in);
        fclose(out);
        return DSU_STATUS_IO_ERROR;
    }
    if (fclose(in) != 0) {
        fclose(out);
        return DSU_STATUS_IO_ERROR;
    }
    if (fclose(out) != 0) {
        return DSU_STATUS_IO_ERROR;
    }
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_fs_copy_file(dsu_fs_t *fs,
                              dsu_u32 src_root,
                              const char *src_rel,
                              dsu_u32 dst_root,
                              const char *dst_rel,
                              dsu_bool replace_existing) {
    char src_abs[1024];
    char dst_abs[1024];
    char dst_dir[1024];
    char dst_base[256];
    dsu_status_t st;
    dsu_u8 exists;
    dsu_u8 is_dir;
    dsu_u8 is_symlink;

    if (!fs || src_root >= fs->root_count || dst_root >= fs->root_count) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!src_rel || !dst_rel) {
        return DSU_STATUS_INVALID_ARGS;
    }

    st = dsu_fs_resolve_under_root(fs, src_root, src_rel, src_abs, (dsu_u32)sizeof(src_abs));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu_fs_resolve_under_root(fs, dst_root, dst_rel, dst_abs, (dsu_u32)sizeof(dst_abs));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    st = dsu_fs_path_split(dst_rel, dst_dir, (dsu_u32)sizeof(dst_dir), dst_base, (dsu_u32)sizeof(dst_base));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu_fs_mkdir_p(fs, dst_root, dst_dir);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    st = dsu_platform_path_info(dst_abs, &exists, &is_dir, &is_symlink);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (exists) {
        if (!replace_existing) {
            return DSU_STATUS_IO_ERROR;
        }
        if (is_dir || is_symlink) {
            return DSU_STATUS_IO_ERROR;
        }
        (void)dsu_platform_remove_file(dst_abs);
    }

    return dsu__copy_file_stdio(src_abs, dst_abs);
}

dsu_status_t dsu_fs_move_path(dsu_fs_t *fs,
                              dsu_u32 src_root,
                              const char *src_rel,
                              dsu_u32 dst_root,
                              const char *dst_rel,
                              dsu_bool replace_existing) {
    char src_abs[1024];
    char dst_abs[1024];
    char dst_dir[1024];
    char dst_base[256];
    dsu_status_t st;
    dsu_u8 exists;
    dsu_u8 is_dir;
    dsu_u8 is_symlink;

    if (!fs || src_root >= fs->root_count || dst_root >= fs->root_count) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!src_rel || !dst_rel) {
        return DSU_STATUS_INVALID_ARGS;
    }

    st = dsu_fs_resolve_under_root(fs, src_root, src_rel, src_abs, (dsu_u32)sizeof(src_abs));
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu_fs_resolve_under_root(fs, dst_root, dst_rel, dst_abs, (dsu_u32)sizeof(dst_abs));
    if (st != DSU_STATUS_SUCCESS) return st;

    st = dsu_fs_path_split(dst_rel, dst_dir, (dsu_u32)sizeof(dst_dir), dst_base, (dsu_u32)sizeof(dst_base));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu_fs_mkdir_p(fs, dst_root, dst_dir);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    if (!replace_existing) {
        st = dsu_platform_path_info(dst_abs, &exists, &is_dir, &is_symlink);
        if (st == DSU_STATUS_SUCCESS && exists) {
            return DSU_STATUS_IO_ERROR;
        }
    }

    st = dsu_platform_rename(src_abs, dst_abs, (dsu_u8)(replace_existing ? 1u : 0u));
    if (st == DSU_STATUS_SUCCESS) {
        return DSU_STATUS_SUCCESS;
    }

    /* Fallback for files only. */
    st = dsu_platform_path_info(src_abs, &exists, &is_dir, &is_symlink);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (!exists || is_dir) {
        return DSU_STATUS_IO_ERROR;
    }
    st = dsu__copy_file_stdio(src_abs, dst_abs);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    return dsu_platform_remove_file(src_abs);
}

dsu_status_t dsu_fs_delete_file(dsu_fs_t *fs, dsu_u32 root_index, const char *rel_path) {
    char abs[1024];
    dsu_status_t st;
    dsu_u8 exists;
    dsu_u8 is_dir;
    dsu_u8 is_symlink;

    if (!fs || root_index >= fs->root_count || !rel_path) {
        return DSU_STATUS_INVALID_ARGS;
    }
    st = dsu_fs_resolve_under_root(fs, root_index, rel_path, abs, (dsu_u32)sizeof(abs));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu_platform_path_info(abs, &exists, &is_dir, &is_symlink);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (!exists) {
        return DSU_STATUS_SUCCESS;
    }
    if (is_dir || is_symlink) {
        return DSU_STATUS_IO_ERROR;
    }
    return dsu_platform_remove_file(abs);
}

static dsu_status_t dsu__write_all(const char *abs_path, const dsu_u8 *bytes, dsu_u32 len) {
    FILE *f;
    size_t nw;
    if (!abs_path || (!bytes && len != 0u)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    f = fopen(abs_path, "wb");
    if (!f) {
        return DSU_STATUS_IO_ERROR;
    }
    if (len) {
        nw = fwrite(bytes, 1u, (size_t)len, f);
        if (nw != (size_t)len) {
            fclose(f);
            return DSU_STATUS_IO_ERROR;
        }
    }
    if (fclose(f) != 0) {
        return DSU_STATUS_IO_ERROR;
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__tmp_rel_for_target(const char *rel_path, char *out_tmp, dsu_u32 out_cap) {
    dsu_u32 n;
    if (!rel_path || !out_tmp || out_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    n = dsu__strlen(rel_path);
    if (n == 0xFFFFFFFFu) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (n + 5u + 1u > out_cap) {
        return DSU_STATUS_INVALID_ARGS;
    }
    memcpy(out_tmp, rel_path, (size_t)n);
    memcpy(out_tmp + n, ".tmp", 5u);
    out_tmp[n + 4u] = '\0';
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_fs_write_file_atomic(dsu_fs_t *fs,
                                      dsu_u32 root_index,
                                      const char *rel_path,
                                      const dsu_u8 *bytes,
                                      dsu_u32 len,
                                      dsu_bool replace_existing) {
    char tmp_rel[1024];
    char abs_tmp[1024];
    char abs_dst[1024];
    char dir[1024];
    char base[256];
    dsu_status_t st;
    dsu_u8 exists;
    dsu_u8 is_dir;
    dsu_u8 is_symlink;

    if (!fs || root_index >= fs->root_count || !rel_path) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (!bytes && len != 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    st = dsu__tmp_rel_for_target(rel_path, tmp_rel, (dsu_u32)sizeof(tmp_rel));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    st = dsu_fs_path_split(rel_path, dir, (dsu_u32)sizeof(dir), base, (dsu_u32)sizeof(base));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu_fs_mkdir_p(fs, root_index, dir);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    st = dsu_fs_resolve_under_root(fs, root_index, tmp_rel, abs_tmp, (dsu_u32)sizeof(abs_tmp));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu_fs_resolve_under_root(fs, root_index, rel_path, abs_dst, (dsu_u32)sizeof(abs_dst));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    st = dsu__write_all(abs_tmp, bytes, len);
    if (st != DSU_STATUS_SUCCESS) {
        (void)dsu_platform_remove_file(abs_tmp);
        return st;
    }

    st = dsu_platform_path_info(abs_dst, &exists, &is_dir, &is_symlink);
    if (st != DSU_STATUS_SUCCESS) {
        (void)dsu_platform_remove_file(abs_tmp);
        return st;
    }
    if (exists) {
        if (!replace_existing) {
            (void)dsu_platform_remove_file(abs_tmp);
            return DSU_STATUS_IO_ERROR;
        }
        if (is_dir || is_symlink) {
            (void)dsu_platform_remove_file(abs_tmp);
            return DSU_STATUS_IO_ERROR;
        }
    }

    st = dsu_platform_rename(abs_tmp, abs_dst, (dsu_u8)(replace_existing ? 1u : 0u));
    if (st != DSU_STATUS_SUCCESS) {
        (void)dsu_platform_remove_file(abs_tmp);
        return st;
    }
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_fs_hash_file(dsu_fs_t *fs,
                              dsu_u32 root_index,
                              const char *rel_path,
                              dsu_u8 out_sha256[32]) {
    char abs[1024];
    dsu_status_t st;
    dsu_u8 exists;
    dsu_u8 is_dir;
    dsu_u8 is_symlink;
    if (!fs || root_index >= fs->root_count || !rel_path || !out_sha256) {
        return DSU_STATUS_INVALID_ARGS;
    }
    st = dsu_fs_resolve_under_root(fs, root_index, rel_path, abs, (dsu_u32)sizeof(abs));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu_platform_path_info(abs, &exists, &is_dir, &is_symlink);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (!exists) {
        return DSU_STATUS_IO_ERROR;
    }
    if (is_dir || is_symlink) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    return dsu__sha256_file(abs, out_sha256);
}

dsu_status_t dsu_fs_query_permissions(dsu_fs_t *fs,
                                      dsu_u32 root_index,
                                      const char *rel_path,
                                      dsu_u32 *out_perm_flags) {
    (void)fs;
    (void)root_index;
    (void)rel_path;
    if (!out_perm_flags) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_perm_flags = 0u;
    return DSU_STATUS_SUCCESS;
}
