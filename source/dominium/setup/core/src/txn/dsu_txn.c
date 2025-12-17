/*
FILE: source/dominium/setup/core/src/txn/dsu_txn.c
MODULE: Dominium Setup
PURPOSE: Journaled transaction engine (Plan S-4).
*/
#include "../../include/dsu/dsu_txn.h"
#include "../../include/dsu/dsu_fs.h"
#include "../../include/dsu/dsu_log.h"

#include "../dsu_ctx_internal.h"
#include "../fs/dsu_platform_iface.h"
#include "../log/dsu_events.h"
#include "../state/dsu_state_internal.h"
#include "../util/dsu_util_internal.h"
#include "dsu_journal.h"

#include <stdlib.h>
#include <string.h>
#include <time.h>

#define DSU_TXN_INTERNAL_DIR ".dsu_txn"
#define DSU_TXN_STAGE_DIR DSU_TXN_INTERNAL_DIR "/staged"
#define DSU_TXN_STATE_DIR DSU_TXN_INTERNAL_DIR "/state"
#define DSU_TXN_JOURNAL_DIR DSU_TXN_INTERNAL_DIR "/journal"
#define DSU_TXN_DEFAULT_JOURNAL_NAME "txn.dsujournal"
#define DSU_TXN_NEW_STATE_NAME "new.dsustate"
#define DSU_TXN_DEFAULT_STATE_REL ".dsu/state.dsustate"

static void dsu__safe_cpy(char *dst, dsu_u32 dst_cap, const char *src);
static int dsu__is_alpha(char c);
static int dsu__is_abs_path_like(const char *p);
static dsu_u64 dsu__nonce64(dsu_ctx_t *ctx, dsu_u64 seed);

static void dsu__u64_hex16(char out16[17], dsu_u64 v) {
    static const char *hex = "0123456789abcdef";
    int i;
    for (i = 0; i < 16; ++i) {
        int shift = (15 - i) * 4;
        out16[i] = hex[(unsigned char)((v >> shift) & 0xFu)];
    }
    out16[16] = '\0';
}

static int dsu__path_has_prefix_seg(const char *path, const char *prefix) {
    dsu_u32 n;
    dsu_u32 m;
    if (!path || !prefix) return 0;
    n = dsu__strlen(path);
    m = dsu__strlen(prefix);
    if (n == 0xFFFFFFFFu || m == 0xFFFFFFFFu) return 0;
    if (n < m) return 0;
    if (memcmp(path, prefix, (size_t)m) != 0) return 0;
    if (n == m) return 1;
    return path[m] == '/';
}

static dsu_status_t dsu__canon_rel_path_ex(const char *in, dsu_bool allow_empty, char **out_canon) {
    dsu_u32 i;
    dsu_u32 n;
    char *buf;
    dsu_u32 o = 0u;
    dsu_u32 seg_start = 0u;

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

typedef struct dsu__txn_entry_t {
    dsu_u16 type;
    dsu_u8 target_root;
    dsu_u8 source_root;
    dsu_u8 rollback_root;
    char *target_path;
    char *source_path;
    char *rollback_path;
    dsu_u32 flags;
} dsu__txn_entry_t;

static void dsu__txn_entries_free(dsu__txn_entry_t *entries, dsu_u32 count) {
    dsu_u32 i;
    if (!entries) return;
    for (i = 0u; i < count; ++i) {
        dsu__free(entries[i].target_path);
        dsu__free(entries[i].source_path);
        dsu__free(entries[i].rollback_path);
        entries[i].target_path = NULL;
        entries[i].source_path = NULL;
        entries[i].rollback_path = NULL;
    }
    dsu__free(entries);
}

static int dsu__txn_entry_group(dsu_u16 type) {
    if (type == (dsu_u16)DSU_JOURNAL_ENTRY_CREATE_DIR || type == (dsu_u16)DSU_JOURNAL_ENTRY_REMOVE_DIR) {
        return 0;
    }
    if (type == (dsu_u16)DSU_JOURNAL_ENTRY_WRITE_STATE) {
        return 2;
    }
    return 1;
}

static int dsu__txn_entry_cmp(const void *a, const void *b) {
    const dsu__txn_entry_t *ea = (const dsu__txn_entry_t *)a;
    const dsu__txn_entry_t *eb = (const dsu__txn_entry_t *)b;
    int ga;
    int gb;
    int c;
    const char *pa;
    const char *pb;

    ga = dsu__txn_entry_group(ea->type);
    gb = dsu__txn_entry_group(eb->type);
    if (ga != gb) return ga - gb;

    pa = ea->target_path ? ea->target_path : "";
    pb = eb->target_path ? eb->target_path : "";
    c = dsu__strcmp_bytes(pa, pb);
    if (c != 0) return c;

    /* Ensure backups (txn targets) precede installs (install targets) for the same logical path. */
    if (ea->target_root != eb->target_root) {
        return (int)eb->target_root - (int)ea->target_root;
    }

    if (ea->type != eb->type) {
        return (int)ea->type - (int)eb->type;
    }

    if (ea->source_root != eb->source_root) {
        return (int)ea->source_root - (int)eb->source_root;
    }
    if (ea->rollback_root != eb->rollback_root) {
        return (int)ea->rollback_root - (int)eb->rollback_root;
    }

    pa = ea->source_path ? ea->source_path : "";
    pb = eb->source_path ? eb->source_path : "";
    c = dsu__strcmp_bytes(pa, pb);
    if (c != 0) return c;

    pa = ea->rollback_path ? ea->rollback_path : "";
    pb = eb->rollback_path ? eb->rollback_path : "";
    c = dsu__strcmp_bytes(pa, pb);
    if (c != 0) return c;

    if (ea->flags != eb->flags) {
        return (ea->flags < eb->flags) ? -1 : 1;
    }
    return 0;
}

static dsu_status_t dsu__txn_entries_push_take(dsu__txn_entry_t **io_entries,
                                              dsu_u32 *io_count,
                                              dsu_u32 *io_cap,
                                              dsu__txn_entry_t *in_out_e) {
    dsu__txn_entry_t *items;
    dsu_u32 count;
    dsu_u32 cap;
    dsu_u32 new_cap;

    if (!io_entries || !io_count || !io_cap || !in_out_e) {
        return DSU_STATUS_INVALID_ARGS;
    }
    items = *io_entries;
    count = *io_count;
    cap = *io_cap;

    if (count == cap) {
        new_cap = (cap == 0u) ? 32u : (cap * 2u);
        items = (dsu__txn_entry_t *)dsu__realloc(items, new_cap * (dsu_u32)sizeof(*items));
        if (!items) {
            return DSU_STATUS_IO_ERROR;
        }
        cap = new_cap;
    }
    items[count] = *in_out_e;
    memset(in_out_e, 0, sizeof(*in_out_e));
    *io_entries = items;
    *io_count = count + 1u;
    *io_cap = cap;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__fs_path_info_rel(dsu_fs_t *fs,
                                         dsu_u32 root_index,
                                         const char *rel,
                                         dsu_u8 *out_exists,
                                         dsu_u8 *out_is_dir,
                                         dsu_u8 *out_is_symlink) {
    char abs[1024];
    dsu_status_t st;
    if (!out_exists || !out_is_dir || !out_is_symlink) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_exists = 0u;
    *out_is_dir = 0u;
    *out_is_symlink = 0u;
    st = dsu_fs_resolve_under_root(fs, root_index, rel, abs, (dsu_u32)sizeof(abs));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    return dsu_platform_path_info(abs, out_exists, out_is_dir, out_is_symlink);
}

static dsu_status_t dsu__canon_abs_path(const char *in, char *out_abs, dsu_u32 out_abs_cap) {
    dsu_status_t st;
    char in_copy[1024];
    const char *src;
    dsu_u32 n;
    if (!in || !out_abs || out_abs_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (in[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
    src = in;
    if (in == out_abs) {
        n = dsu__strlen(in);
        if (n == 0xFFFFFFFFu || n + 1u > (dsu_u32)sizeof(in_copy)) {
            return DSU_STATUS_INVALID_ARGS;
        }
        memcpy(in_copy, in, (size_t)n + 1u);
        src = in_copy;
    }
    out_abs[0] = '\0';
    if (dsu__is_abs_path_like(src)) {
        st = dsu_fs_path_canonicalize(src, out_abs, out_abs_cap);
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
        st = dsu_fs_path_join(cwd, src, joined, (dsu_u32)sizeof(joined));
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

static dsu_status_t dsu__mkdir_parent_abs(const char *abs_path) {
    char dir[1024];
    char base[256];
    dsu_status_t st;
    if (!abs_path || abs_path[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
    dir[0] = '\0';
    base[0] = '\0';
    st = dsu_fs_path_split(abs_path, dir, (dsu_u32)sizeof(dir), base, (dsu_u32)sizeof(base));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (dir[0] == '\0') {
        return DSU_STATUS_SUCCESS;
    }
    return dsu_platform_mkdir(dir);
}

static dsu_status_t dsu__dir_of_rel_path(const char *rel_path, char *out_dir, dsu_u32 out_dir_cap) {
    char base[256];
    if (!rel_path || !out_dir || out_dir_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    return dsu_fs_path_split(rel_path, out_dir, out_dir_cap, base, (dsu_u32)sizeof(base));
}

static dsu_status_t dsu__plan_state_rel(const dsu_plan_t *plan, char *out_rel, dsu_u32 out_rel_cap) {
    dsu_u32 i;
    const char *p = NULL;
    char *canon = NULL;
    dsu_status_t st;
    if (!out_rel || out_rel_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    out_rel[0] = '\0';
    if (!plan) {
        return DSU_STATUS_INVALID_ARGS;
    }
    for (i = 0u; i < dsu_plan_step_count(plan); ++i) {
        if (dsu_plan_step_kind(plan, i) == DSU_PLAN_STEP_WRITE_STATE) {
            p = dsu_plan_step_arg(plan, i);
            break;
        }
    }
    if (!p || p[0] == '\0') {
        p = DSU_TXN_DEFAULT_STATE_REL;
    }
    st = dsu__canon_rel_path_ex(p, 0, &canon);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (dsu__strlen(canon) + 1u > out_rel_cap) {
        dsu__free(canon);
        return DSU_STATUS_INVALID_ARGS;
    }
    dsu__safe_cpy(out_rel, out_rel_cap, canon);
    dsu__free(canon);
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__build_default_txn_root(const char *install_root_abs,
                                                dsu_u64 journal_id,
                                                char *out_txn_abs,
                                                dsu_u32 out_txn_abs_cap) {
    char hex16[17];
    dsu_u32 nr;
    dsu_u32 need;
    if (!install_root_abs || !out_txn_abs || out_txn_abs_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    out_txn_abs[0] = '\0';
    dsu__u64_hex16(hex16, journal_id);
    nr = dsu__strlen(install_root_abs);
    if (nr == 0xFFFFFFFFu) {
        return DSU_STATUS_INVALID_ARGS;
    }
    need = nr + 4u /* .txn */ + 1u /* / */ + 16u + 1u;
    if (need > out_txn_abs_cap) {
        return DSU_STATUS_INVALID_ARGS;
    }
    memcpy(out_txn_abs, install_root_abs, (size_t)nr);
    memcpy(out_txn_abs + nr, ".txn", 4u);
    out_txn_abs[nr + 4u] = '/';
    memcpy(out_txn_abs + nr + 5u, hex16, 16u);
    out_txn_abs[nr + 5u + 16u] = '\0';
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__build_default_journal_path(const char *txn_root_abs,
                                                    char *out_journal_abs,
                                                    dsu_u32 out_journal_abs_cap) {
    char joined[1024];
    dsu_status_t st;
    if (!txn_root_abs || !out_journal_abs || out_journal_abs_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    out_journal_abs[0] = '\0';
    st = dsu_fs_path_join(txn_root_abs, DSU_TXN_JOURNAL_DIR "/" DSU_TXN_DEFAULT_JOURNAL_NAME,
                          joined, (dsu_u32)sizeof(joined));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    return dsu__canon_abs_path(joined, out_journal_abs, out_journal_abs_cap);
}

static int dsu__same_volume_best_effort(const char *a_abs, const char *b_abs) {
    char da;
    char db;
    if (!a_abs || !b_abs) return 0;
    da = 0;
    db = 0;
    if (dsu__is_alpha(a_abs[0]) && a_abs[1] == ':') {
        da = a_abs[0];
        if (da >= 'A' && da <= 'Z') da = (char)(da - 'A' + 'a');
    }
    if (dsu__is_alpha(b_abs[0]) && b_abs[1] == ':') {
        db = b_abs[0];
        if (db >= 'A' && db <= 'Z') db = (char)(db - 'A' + 'a');
    }
    if (da && db) {
        return da == db;
    }
    return 1;
}

static void dsu__str_list_free(char **items, dsu_u32 count) {
    dsu_u32 i;
    if (!items) return;
    for (i = 0u; i < count; ++i) {
        dsu__free(items[i]);
        items[i] = NULL;
    }
    dsu__free(items);
}

static dsu_status_t dsu__str_list_add_unique(char ***io_items,
                                             dsu_u32 *io_count,
                                             dsu_u32 *io_cap,
                                             const char *canon_abs) {
    char **items;
    dsu_u32 count;
    dsu_u32 cap;
    dsu_u32 i;
    dsu_u32 new_cap;
    char *dup;

    if (!io_items || !io_count || !io_cap || !canon_abs) {
        return DSU_STATUS_INVALID_ARGS;
    }
    items = *io_items;
    count = *io_count;
    cap = *io_cap;

    for (i = 0u; i < count; ++i) {
        if (items[i] && dsu__strcmp_bytes(items[i], canon_abs) == 0) {
            return DSU_STATUS_SUCCESS;
        }
    }

    if (count == cap) {
        new_cap = (cap == 0u) ? 16u : (cap * 2u);
        items = (char **)dsu__realloc(items, new_cap * (dsu_u32)sizeof(*items));
        if (!items) {
            return DSU_STATUS_IO_ERROR;
        }
        cap = new_cap;
    }
    dup = dsu__strdup(canon_abs);
    if (!dup) {
        return DSU_STATUS_IO_ERROR;
    }
    items[count++] = dup;
    *io_items = items;
    *io_count = count;
    *io_cap = cap;
    return DSU_STATUS_SUCCESS;
}

static dsu_u32 dsu__str_list_index_of(char **items, dsu_u32 count, const char *canon_abs) {
    dsu_u32 i;
    if (!items || !canon_abs) return 0xFFFFFFFFu;
    for (i = 0u; i < count; ++i) {
        if (items[i] && dsu__strcmp_bytes(items[i], canon_abs) == 0) {
            return i;
        }
    }
    return 0xFFFFFFFFu;
}

static dsu_status_t dsu__fs_create_for_plan(dsu_ctx_t *ctx,
                                           const dsu_plan_t *plan,
                                           const char *install_root_abs,
                                           const char *txn_root_abs,
                                           dsu_fs_t **out_fs,
                                           char ***out_extra_roots,
                                           dsu_u32 *out_extra_count) {
    char **extra = NULL;
    dsu_u32 extra_count = 0u;
    dsu_u32 extra_cap = 0u;
    dsu_u32 i;
    const char **roots = NULL;
    dsu_u32 root_count;
    dsu_fs_options_t fopts;
    dsu_fs_t *fs = NULL;
    dsu_status_t st;

    if (out_fs) *out_fs = NULL;
    if (out_extra_roots) *out_extra_roots = NULL;
    if (out_extra_count) *out_extra_count = 0u;

    if (!ctx || !plan || !install_root_abs || !txn_root_abs || !out_fs) {
        return DSU_STATUS_INVALID_ARGS;
    }

    for (i = 0u; i < dsu_plan_file_count(plan); ++i) {
        dsu_manifest_payload_kind_t kind = dsu_plan_file_source_kind(plan, i);
        const char *container = dsu_plan_file_source_container_path(plan, i);
        char canon[1024];
        if (kind != DSU_MANIFEST_PAYLOAD_KIND_FILESET && kind != DSU_MANIFEST_PAYLOAD_KIND_ARCHIVE) {
            continue;
        }
        if (!container || container[0] == '\0') {
            dsu__str_list_free(extra, extra_count);
            return DSU_STATUS_INVALID_ARGS;
        }
        st = dsu__canon_abs_path(container, canon, (dsu_u32)sizeof(canon));
        if (st != DSU_STATUS_SUCCESS) {
            dsu__str_list_free(extra, extra_count);
            return st;
        }
        st = dsu__str_list_add_unique(&extra, &extra_count, &extra_cap, canon);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__str_list_free(extra, extra_count);
            return st;
        }
    }

    root_count = 2u + extra_count;
    roots = (const char **)dsu__malloc(root_count * (dsu_u32)sizeof(*roots));
    if (!roots) {
        dsu__str_list_free(extra, extra_count);
        return DSU_STATUS_IO_ERROR;
    }
    roots[0] = install_root_abs;
    roots[1] = txn_root_abs;
    for (i = 0u; i < extra_count; ++i) {
        roots[2u + i] = extra[i];
    }

    dsu_fs_options_init(&fopts);
    fopts.allowed_roots = roots;
    fopts.allowed_root_count = root_count;
    st = dsu_fs_create(ctx, &fopts, &fs);
    dsu__free(roots);
    roots = NULL;
    if (st != DSU_STATUS_SUCCESS) {
        dsu__str_list_free(extra, extra_count);
        return st;
    }

    *out_fs = fs;
    if (out_extra_roots) {
        *out_extra_roots = extra;
    } else {
        dsu__str_list_free(extra, extra_count);
        extra = NULL;
    }
    if (out_extra_count) {
        *out_extra_count = extra_count;
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__txn_stage_plan_files(dsu_fs_t *fs,
                                             char **extra_roots,
                                             dsu_u32 extra_root_count,
                                             const dsu_plan_t *plan,
                                             const char *state_rel,
                                             dsu_u32 *out_staged_count) {
    dsu_u32 i;
    dsu_status_t st;
    dsu_u32 staged = 0u;

    if (out_staged_count) *out_staged_count = 0u;
    if (!fs || !plan || !state_rel) {
        return DSU_STATUS_INVALID_ARGS;
    }

    st = dsu_fs_mkdir_p(fs, (dsu_u32)DSU_JOURNAL_ROOT_TXN, "");
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu_fs_mkdir_p(fs, (dsu_u32)DSU_JOURNAL_ROOT_TXN, DSU_TXN_INTERNAL_DIR);
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu_fs_mkdir_p(fs, (dsu_u32)DSU_JOURNAL_ROOT_TXN, DSU_TXN_STAGE_DIR);
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu_fs_mkdir_p(fs, (dsu_u32)DSU_JOURNAL_ROOT_TXN, DSU_TXN_STATE_DIR);
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu_fs_mkdir_p(fs, (dsu_u32)DSU_JOURNAL_ROOT_TXN, DSU_TXN_JOURNAL_DIR);
    if (st != DSU_STATUS_SUCCESS) return st;

    for (i = 0u; i < dsu_plan_file_count(plan); ++i) {
        dsu_manifest_payload_kind_t kind = dsu_plan_file_source_kind(plan, i);
        const char *target = dsu_plan_file_target_path(plan, i);
        const char *container = dsu_plan_file_source_container_path(plan, i);
        const char *member = dsu_plan_file_source_member_path(plan, i);
        char *target_canon = NULL;
        char *member_canon = NULL;
        char staged_rel[1024];

        st = dsu__canon_rel_path_ex(target ? target : "", 0, &target_canon);
        if (st != DSU_STATUS_SUCCESS) return st;
        if (dsu__path_has_prefix_seg(target_canon, ".dsu") ||
            dsu__path_has_prefix_seg(target_canon, DSU_TXN_INTERNAL_DIR)) {
            dsu__free(target_canon);
            return DSU_STATUS_INVALID_ARGS;
        }
        if (dsu__strcmp_bytes(target_canon, state_rel) == 0) {
            dsu__free(target_canon);
            return DSU_STATUS_INVALID_ARGS;
        }

        {
            dsu_u32 need = dsu__strlen(DSU_TXN_STAGE_DIR) + 1u + dsu__strlen(target_canon) + 1u;
            if (need > (dsu_u32)sizeof(staged_rel)) {
                dsu__free(target_canon);
                return DSU_STATUS_INVALID_ARGS;
            }
            memcpy(staged_rel, DSU_TXN_STAGE_DIR, dsu__strlen(DSU_TXN_STAGE_DIR));
            staged_rel[dsu__strlen(DSU_TXN_STAGE_DIR)] = '/';
            memcpy(staged_rel + dsu__strlen(DSU_TXN_STAGE_DIR) + 1u, target_canon, dsu__strlen(target_canon) + 1u);
        }

        if (kind == DSU_MANIFEST_PAYLOAD_KIND_FILESET) {
            char canon_container[1024];
            dsu_u32 idx;
            if (!container || !member) {
                dsu__free(target_canon);
                return DSU_STATUS_INVALID_ARGS;
            }
            st = dsu__canon_abs_path(container, canon_container, (dsu_u32)sizeof(canon_container));
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_canon);
                return st;
            }
            idx = dsu__str_list_index_of(extra_roots, extra_root_count, canon_container);
            if (idx == 0xFFFFFFFFu) {
                dsu__free(target_canon);
                return DSU_STATUS_INVALID_ARGS;
            }
            st = dsu__canon_rel_path_ex(member, 0, &member_canon);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_canon);
                return st;
            }
            st = dsu_fs_copy_file(fs,
                                  2u + idx,
                                  member_canon,
                                  (dsu_u32)DSU_JOURNAL_ROOT_TXN,
                                  staged_rel,
                                  0);
            dsu__free(member_canon);
            member_canon = NULL;
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_canon);
                return st;
            }
        } else if (kind == DSU_MANIFEST_PAYLOAD_KIND_ARCHIVE) {
            char canon_container[1024];
            char abs_dst[1024];
            char dir_rel[1024];
            dsu_u8 exists;
            dsu_u8 is_dir;
            dsu_u8 is_symlink;
            if (!container || !member) {
                dsu__free(target_canon);
                return DSU_STATUS_INVALID_ARGS;
            }
            st = dsu__canon_abs_path(container, canon_container, (dsu_u32)sizeof(canon_container));
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_canon);
                return st;
            }
            st = dsu_platform_path_info(canon_container, &exists, &is_dir, &is_symlink);
            if (st != DSU_STATUS_SUCCESS || !exists || is_dir || is_symlink) {
                dsu__free(target_canon);
                return (st == DSU_STATUS_SUCCESS) ? DSU_STATUS_IO_ERROR : st;
            }
            st = dsu__canon_rel_path_ex(member, 0, &member_canon);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_canon);
                return st;
            }
            st = dsu__dir_of_rel_path(staged_rel, dir_rel, (dsu_u32)sizeof(dir_rel));
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_canon);
                dsu__free(member_canon);
                return st;
            }
            st = dsu_fs_mkdir_p(fs, (dsu_u32)DSU_JOURNAL_ROOT_TXN, dir_rel);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_canon);
                dsu__free(member_canon);
                return st;
            }
            st = dsu_fs_resolve_under_root(fs,
                                           (dsu_u32)DSU_JOURNAL_ROOT_TXN,
                                           staged_rel,
                                           abs_dst,
                                           (dsu_u32)sizeof(abs_dst));
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_canon);
                dsu__free(member_canon);
                return st;
            }
            st = dsu__archive_extract_file(canon_container, member_canon, abs_dst);
            dsu__free(member_canon);
            member_canon = NULL;
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_canon);
                return st;
            }
        } else {
            dsu__free(target_canon);
            return DSU_STATUS_INVALID_ARGS;
        }

        dsu__free(target_canon);
        target_canon = NULL;
        staged += 1u;
    }

    if (out_staged_count) {
        *out_staged_count = staged;
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__txn_write_state_file(dsu_ctx_t *ctx,
                                             dsu_fs_t *fs,
                                             const dsu_plan_t *plan,
                                             char *out_state_txn_rel,
                                             dsu_u32 out_state_txn_rel_cap) {
    char rel[1024];
    char abs[1024];
    dsu_state_t *stobj = NULL;
    dsu_status_t st;

    if (!ctx || !fs || !plan || !out_state_txn_rel || out_state_txn_rel_cap == 0u) {
        return DSU_STATUS_INVALID_ARGS;
    }
    out_state_txn_rel[0] = '\0';

    if (dsu__strlen(DSU_TXN_STATE_DIR) + 1u + dsu__strlen(DSU_TXN_NEW_STATE_NAME) + 1u > (dsu_u32)sizeof(rel)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    memcpy(rel, DSU_TXN_STATE_DIR, dsu__strlen(DSU_TXN_STATE_DIR));
    rel[dsu__strlen(DSU_TXN_STATE_DIR)] = '/';
    memcpy(rel + dsu__strlen(DSU_TXN_STATE_DIR) + 1u, DSU_TXN_NEW_STATE_NAME, dsu__strlen(DSU_TXN_NEW_STATE_NAME) + 1u);

    st = dsu_fs_mkdir_p(fs, (dsu_u32)DSU_JOURNAL_ROOT_TXN, DSU_TXN_STATE_DIR);
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu_fs_resolve_under_root(fs,
                                   (dsu_u32)DSU_JOURNAL_ROOT_TXN,
                                   rel,
                                   abs,
                                   (dsu_u32)sizeof(abs));
    if (st != DSU_STATUS_SUCCESS) return st;

    st = dsu__state_build_from_plan(ctx, plan, &stobj);
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu_state_write_file(ctx, stobj, abs);
    dsu_state_destroy(ctx, stobj);
    stobj = NULL;
    if (st != DSU_STATUS_SUCCESS) return st;

    if (dsu__strlen(rel) + 1u > out_state_txn_rel_cap) {
        return DSU_STATUS_INVALID_ARGS;
    }
    dsu__safe_cpy(out_state_txn_rel, out_state_txn_rel_cap, rel);
    return DSU_STATUS_SUCCESS;
}

static void dsu__safe_cpy(char *dst, dsu_u32 dst_cap, const char *src) {
    dsu_u32 n;
    if (!dst || dst_cap == 0u) return;
    dst[0] = '\0';
    if (!src) return;
    n = dsu__strlen(src);
    if (n == 0xFFFFFFFFu || n + 1u > dst_cap) return;
    if (n) {
        memcpy(dst, src, (size_t)n);
    }
    dst[n] = '\0';
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

void dsu_txn_result_init(dsu_txn_result_t *out_result) {
    if (!out_result) {
        return;
    }
    memset(out_result, 0, sizeof(*out_result));
    out_result->struct_size = (dsu_u32)sizeof(*out_result);
    out_result->struct_version = 1u;
}

void dsu_txn_options_init(dsu_txn_options_t *opts) {
    if (!opts) {
        return;
    }
    memset(opts, 0, sizeof(*opts));
    opts->struct_size = (dsu_u32)sizeof(*opts);
    opts->struct_version = 1u;
    opts->dry_run = 0;
    opts->journal_path = NULL;
    opts->txn_root = NULL;
    opts->fail_after_entries = 0u;
}

static dsu_status_t dsu__txn_collect_install_dirs(const dsu_plan_t *plan,
                                                 const char *state_rel,
                                                 char ***out_dirs,
                                                 dsu_u32 *out_dir_count) {
    char **dirs = NULL;
    dsu_u32 dir_count = 0u;
    dsu_u32 dir_cap = 0u;
    dsu_u32 i;
    dsu_status_t st;

    if (out_dirs) *out_dirs = NULL;
    if (out_dir_count) *out_dir_count = 0u;
    if (!plan || !state_rel || !out_dirs || !out_dir_count) {
        return DSU_STATUS_INVALID_ARGS;
    }

    st = dsu__str_list_add_unique(&dirs, &dir_count, &dir_cap, "");
    if (st != DSU_STATUS_SUCCESS) {
        dsu__str_list_free(dirs, dir_count);
        return st;
    }

    for (i = 0u; i < dsu_plan_dir_count(plan); ++i) {
        char *canon = NULL;
        const char *p = dsu_plan_dir_path(plan, i);
        st = dsu__canon_rel_path_ex(p ? p : "", 1, &canon);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__str_list_free(dirs, dir_count);
            return st;
        }
        if (dsu__path_has_prefix_seg(canon, DSU_TXN_INTERNAL_DIR)) {
            dsu__free(canon);
            dsu__str_list_free(dirs, dir_count);
            return DSU_STATUS_INVALID_ARGS;
        }
        st = dsu__str_list_add_unique(&dirs, &dir_count, &dir_cap, canon);
        dsu__free(canon);
        canon = NULL;
        if (st != DSU_STATUS_SUCCESS) {
            dsu__str_list_free(dirs, dir_count);
            return st;
        }
    }

    /* Ensure parent directories for the state file exist. */
    {
        char dir[1024];
        st = dsu__dir_of_rel_path(state_rel, dir, (dsu_u32)sizeof(dir));
        if (st != DSU_STATUS_SUCCESS) {
            dsu__str_list_free(dirs, dir_count);
            return st;
        }
        if (dir[0] != '\0') {
            dsu_u32 n = dsu__strlen(dir);
            dsu_u32 j;
            if (n == 0xFFFFFFFFu) {
                dsu__str_list_free(dirs, dir_count);
                return DSU_STATUS_INVALID_ARGS;
            }
            for (j = 0u; j < n; ++j) {
                if (dir[j] == '/') {
                    char tmp[1024];
                    if (j + 1u > (dsu_u32)sizeof(tmp)) {
                        dsu__str_list_free(dirs, dir_count);
                        return DSU_STATUS_INVALID_ARGS;
                    }
                    memcpy(tmp, dir, (size_t)j);
                    tmp[j] = '\0';
                    st = dsu__str_list_add_unique(&dirs, &dir_count, &dir_cap, tmp);
                    if (st != DSU_STATUS_SUCCESS) {
                        dsu__str_list_free(dirs, dir_count);
                        return st;
                    }
                }
            }
            st = dsu__str_list_add_unique(&dirs, &dir_count, &dir_cap, dir);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__str_list_free(dirs, dir_count);
                return st;
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

    *out_dirs = dirs;
    *out_dir_count = dir_count;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__txn_add_create_dir_entries(dsu_fs_t *fs,
                                                   char **dirs,
                                                   dsu_u32 dir_count,
                                                   dsu__txn_entry_t **io_entries,
                                                   dsu_u32 *io_entry_count,
                                                   dsu_u32 *io_entry_cap) {
    dsu_u32 i;
    dsu_status_t st;
    if (!fs || !dirs || !io_entries || !io_entry_count || !io_entry_cap) {
        return DSU_STATUS_INVALID_ARGS;
    }
    for (i = 0u; i < dir_count; ++i) {
        dsu_u8 exists;
        dsu_u8 is_dir;
        dsu_u8 is_symlink;
        dsu__txn_entry_t e;
        memset(&e, 0, sizeof(e));

        st = dsu__fs_path_info_rel(fs, (dsu_u32)DSU_JOURNAL_ROOT_INSTALL, dirs[i], &exists, &is_dir, &is_symlink);
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
        if (exists && (!is_dir || is_symlink)) {
            return DSU_STATUS_IO_ERROR;
        }

        e.type = (dsu_u16)DSU_JOURNAL_ENTRY_CREATE_DIR;
        e.target_root = (dsu_u8)DSU_JOURNAL_ROOT_INSTALL;
        e.rollback_root = (dsu_u8)DSU_JOURNAL_ROOT_INSTALL;
        e.target_path = dsu__strdup(dirs[i]);
        e.source_path = dsu__strdup("");
        e.rollback_path = dsu__strdup(dirs[i]);
        if (!e.target_path || !e.source_path || !e.rollback_path) {
            dsu__free(e.target_path);
            dsu__free(e.source_path);
            dsu__free(e.rollback_path);
            return DSU_STATUS_IO_ERROR;
        }
        if (exists) {
            e.flags |= (dsu_u32)DSU_JOURNAL_FLAG_TARGET_PREEXISTED;
        }
        st = dsu__txn_entries_push_take(io_entries, io_entry_count, io_entry_cap, &e);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(e.target_path);
            dsu__free(e.source_path);
            dsu__free(e.rollback_path);
            return st;
        }
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__txn_add_plan_file_entries(dsu_fs_t *fs,
                                                  const dsu_plan_t *plan,
                                                  const char *state_rel,
                                                  dsu__txn_entry_t **io_entries,
                                                  dsu_u32 *io_entry_count,
                                                  dsu_u32 *io_entry_cap) {
    dsu_u32 i;
    dsu_status_t st;
    if (!fs || !plan || !state_rel || !io_entries || !io_entry_count || !io_entry_cap) {
        return DSU_STATUS_INVALID_ARGS;
    }

    for (i = 0u; i < dsu_plan_file_count(plan); ++i) {
        const char *target = dsu_plan_file_target_path(plan, i);
        char *target_canon = NULL;
        dsu_u8 exists;
        dsu_u8 is_dir;
        dsu_u8 is_symlink;
        dsu_u32 flags = 0u;
        char staged_src[1024];
        dsu__txn_entry_t e;

        st = dsu__canon_rel_path_ex(target ? target : "", 0, &target_canon);
        if (st != DSU_STATUS_SUCCESS) return st;

        if (dsu__path_has_prefix_seg(target_canon, ".dsu") ||
            dsu__path_has_prefix_seg(target_canon, DSU_TXN_INTERNAL_DIR)) {
            dsu__free(target_canon);
            return DSU_STATUS_INVALID_ARGS;
        }
        if (dsu__strcmp_bytes(target_canon, state_rel) == 0) {
            dsu__free(target_canon);
            return DSU_STATUS_INVALID_ARGS;
        }

        st = dsu__fs_path_info_rel(fs, (dsu_u32)DSU_JOURNAL_ROOT_INSTALL, target_canon, &exists, &is_dir, &is_symlink);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(target_canon);
            return st;
        }
        if (exists && (is_dir || is_symlink)) {
            dsu__free(target_canon);
            return DSU_STATUS_IO_ERROR;
        }

        if (exists) {
            memset(&e, 0, sizeof(e));
            e.type = (dsu_u16)DSU_JOURNAL_ENTRY_MOVE_FILE;
            e.source_root = (dsu_u8)DSU_JOURNAL_ROOT_INSTALL;
            e.source_path = dsu__strdup(target_canon);
            e.target_root = (dsu_u8)DSU_JOURNAL_ROOT_TXN;
            e.target_path = dsu__strdup(target_canon);
            e.rollback_root = (dsu_u8)DSU_JOURNAL_ROOT_INSTALL;
            e.rollback_path = dsu__strdup(target_canon);
            if (!e.source_path || !e.target_path || !e.rollback_path) {
                dsu__free(target_canon);
                dsu__free(e.source_path);
                dsu__free(e.target_path);
                dsu__free(e.rollback_path);
                return DSU_STATUS_IO_ERROR;
            }
            st = dsu__txn_entries_push_take(io_entries, io_entry_count, io_entry_cap, &e);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(target_canon);
                dsu__free(e.source_path);
                dsu__free(e.target_path);
                dsu__free(e.rollback_path);
                return st;
            }
            flags |= (dsu_u32)DSU_JOURNAL_FLAG_TARGET_PREEXISTED;
        }

        {
            dsu_u32 need = dsu__strlen(DSU_TXN_STAGE_DIR) + 1u + dsu__strlen(target_canon) + 1u;
            if (need > (dsu_u32)sizeof(staged_src)) {
                dsu__free(target_canon);
                return DSU_STATUS_INVALID_ARGS;
            }
            memcpy(staged_src, DSU_TXN_STAGE_DIR, dsu__strlen(DSU_TXN_STAGE_DIR));
            staged_src[dsu__strlen(DSU_TXN_STAGE_DIR)] = '/';
            memcpy(staged_src + dsu__strlen(DSU_TXN_STAGE_DIR) + 1u, target_canon, dsu__strlen(target_canon) + 1u);
        }

        memset(&e, 0, sizeof(e));
        e.type = (dsu_u16)DSU_JOURNAL_ENTRY_MOVE_FILE;
        e.source_root = (dsu_u8)DSU_JOURNAL_ROOT_TXN;
        e.source_path = dsu__strdup(staged_src);
        e.target_root = (dsu_u8)DSU_JOURNAL_ROOT_INSTALL;
        e.target_path = dsu__strdup(target_canon);
        e.rollback_root = (dsu_u8)DSU_JOURNAL_ROOT_TXN;
        e.rollback_path = dsu__strdup(staged_src);
        e.flags = flags;
        if (!e.source_path || !e.target_path || !e.rollback_path) {
            dsu__free(target_canon);
            dsu__free(e.source_path);
            dsu__free(e.target_path);
            dsu__free(e.rollback_path);
            return DSU_STATUS_IO_ERROR;
        }
        st = dsu__txn_entries_push_take(io_entries, io_entry_count, io_entry_cap, &e);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(target_canon);
            dsu__free(e.source_path);
            dsu__free(e.target_path);
            dsu__free(e.rollback_path);
            return st;
        }

        dsu__free(target_canon);
        target_canon = NULL;
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__txn_add_state_entries(dsu_fs_t *fs,
                                              const char *state_rel,
                                              const char *state_txn_rel,
                                              dsu__txn_entry_t **io_entries,
                                              dsu_u32 *io_entry_count,
                                              dsu_u32 *io_entry_cap) {
    dsu_u8 exists;
    dsu_u8 is_dir;
    dsu_u8 is_symlink;
    dsu_u32 flags = 0u;
    dsu_status_t st;
    dsu__txn_entry_t e;

    if (!fs || !state_rel || !state_txn_rel || !io_entries || !io_entry_count || !io_entry_cap) {
        return DSU_STATUS_INVALID_ARGS;
    }

    st = dsu__fs_path_info_rel(fs, (dsu_u32)DSU_JOURNAL_ROOT_INSTALL, state_rel, &exists, &is_dir, &is_symlink);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (exists && (is_dir || is_symlink)) {
        return DSU_STATUS_IO_ERROR;
    }

    if (exists) {
        memset(&e, 0, sizeof(e));
        e.type = (dsu_u16)DSU_JOURNAL_ENTRY_MOVE_FILE;
        e.source_root = (dsu_u8)DSU_JOURNAL_ROOT_INSTALL;
        e.source_path = dsu__strdup(state_rel);
        e.target_root = (dsu_u8)DSU_JOURNAL_ROOT_TXN;
        e.target_path = dsu__strdup(state_rel);
        e.rollback_root = (dsu_u8)DSU_JOURNAL_ROOT_INSTALL;
        e.rollback_path = dsu__strdup(state_rel);
        if (!e.source_path || !e.target_path || !e.rollback_path) {
            dsu__free(e.source_path);
            dsu__free(e.target_path);
            dsu__free(e.rollback_path);
            return DSU_STATUS_IO_ERROR;
        }
        st = dsu__txn_entries_push_take(io_entries, io_entry_count, io_entry_cap, &e);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(e.source_path);
            dsu__free(e.target_path);
            dsu__free(e.rollback_path);
            return st;
        }
        flags |= (dsu_u32)DSU_JOURNAL_FLAG_TARGET_PREEXISTED;
    }

    memset(&e, 0, sizeof(e));
    e.type = (dsu_u16)DSU_JOURNAL_ENTRY_WRITE_STATE;
    e.source_root = (dsu_u8)DSU_JOURNAL_ROOT_TXN;
    e.source_path = dsu__strdup(state_txn_rel);
    e.target_root = (dsu_u8)DSU_JOURNAL_ROOT_INSTALL;
    e.target_path = dsu__strdup(state_rel);
    e.rollback_root = (dsu_u8)DSU_JOURNAL_ROOT_TXN;
    e.rollback_path = dsu__strdup(state_txn_rel);
    e.flags = flags;
    if (!e.source_path || !e.target_path || !e.rollback_path) {
        dsu__free(e.source_path);
        dsu__free(e.target_path);
        dsu__free(e.rollback_path);
        return DSU_STATUS_IO_ERROR;
    }
    st = dsu__txn_entries_push_take(io_entries, io_entry_count, io_entry_cap, &e);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(e.source_path);
        dsu__free(e.target_path);
        dsu__free(e.rollback_path);
        return st;
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__txn_build_entries_for_plan(dsu_fs_t *fs,
                                                   const dsu_plan_t *plan,
                                                   const char *state_rel,
                                                   const char *state_txn_rel,
                                                   dsu__txn_entry_t **out_entries,
                                                   dsu_u32 *out_entry_count) {
    dsu__txn_entry_t *entries = NULL;
    dsu_u32 entry_count = 0u;
    dsu_u32 entry_cap = 0u;
    char **dirs = NULL;
    dsu_u32 dir_count = 0u;
    dsu_status_t st;

    if (out_entries) *out_entries = NULL;
    if (out_entry_count) *out_entry_count = 0u;
    if (!fs || !plan || !state_rel || !state_txn_rel || !out_entries || !out_entry_count) {
        return DSU_STATUS_INVALID_ARGS;
    }

    st = dsu__txn_collect_install_dirs(plan, state_rel, &dirs, &dir_count);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    st = dsu__txn_add_create_dir_entries(fs, dirs, dir_count, &entries, &entry_count, &entry_cap);
    dsu__str_list_free(dirs, dir_count);
    dirs = NULL;
    dir_count = 0u;
    if (st != DSU_STATUS_SUCCESS) {
        dsu__txn_entries_free(entries, entry_count);
        return st;
    }

    st = dsu__txn_add_plan_file_entries(fs, plan, state_rel, &entries, &entry_count, &entry_cap);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__txn_entries_free(entries, entry_count);
        return st;
    }

    st = dsu__txn_add_state_entries(fs, state_rel, state_txn_rel, &entries, &entry_count, &entry_cap);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__txn_entries_free(entries, entry_count);
        return st;
    }

    if (entry_count > 1u) {
        qsort(entries, (size_t)entry_count, sizeof(*entries), dsu__txn_entry_cmp);
    }

    *out_entries = entries;
    *out_entry_count = entry_count;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__txn_write_journal_file(const char *journal_path_abs,
                                                dsu_u64 journal_id,
                                                dsu_u64 plan_digest,
                                                const char *install_root_abs,
                                                const char *txn_root_abs,
                                                const char *state_rel,
                                                const dsu__txn_entry_t *entries,
                                                dsu_u32 entry_count) {
    dsu_journal_writer_t w;
    dsu_status_t st;
    dsu_u32 i;

    if (!journal_path_abs || !install_root_abs || !txn_root_abs || !state_rel || (!entries && entry_count != 0u)) {
        return DSU_STATUS_INVALID_ARGS;
    }

    memset(&w, 0, sizeof(w));
    st = dsu_journal_writer_open(&w, journal_path_abs, journal_id, plan_digest);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu_journal_writer_write_meta(&w, install_root_abs, txn_root_abs, state_rel);
    if (st != DSU_STATUS_SUCCESS) {
        (void)dsu_journal_writer_close(&w);
        return st;
    }

    for (i = 0u; i < entry_count; ++i) {
        const dsu__txn_entry_t *e = &entries[i];
        st = dsu_journal_writer_append_entry(&w,
                                             e->type,
                                             e->target_root,
                                             e->target_path ? e->target_path : "",
                                             e->source_root,
                                             e->source_path ? e->source_path : "",
                                             e->rollback_root,
                                             e->rollback_path ? e->rollback_path : "",
                                             e->flags);
        if (st != DSU_STATUS_SUCCESS) {
            (void)dsu_journal_writer_close(&w);
            return st;
        }
    }
    return dsu_journal_writer_close(&w);
}

static dsu_status_t dsu__txn_verify_staged_files(dsu_fs_t *fs,
                                                const dsu_plan_t *plan,
                                                const char *state_rel,
                                                dsu_txn_result_t *io_result) {
    dsu_u32 i;
    dsu_status_t st;

    if (!fs || !plan || !state_rel || !io_result) {
        return DSU_STATUS_INVALID_ARGS;
    }
    io_result->verified_ok = 0u;
    io_result->verified_missing = 0u;
    io_result->verified_mismatch = 0u;

    for (i = 0u; i < dsu_plan_file_count(plan); ++i) {
        const char *target = dsu_plan_file_target_path(plan, i);
        const dsu_u8 *expect_sha = dsu_plan_file_sha256(plan, i);
        char *target_canon = NULL;
        char staged_rel[1024];
        dsu_u8 exists;
        dsu_u8 is_dir;
        dsu_u8 is_symlink;
        dsu_u8 got[32];

        st = dsu__canon_rel_path_ex(target ? target : "", 0, &target_canon);
        if (st != DSU_STATUS_SUCCESS) return st;
        if (dsu__strcmp_bytes(target_canon, state_rel) == 0) {
            dsu__free(target_canon);
            return DSU_STATUS_INVALID_ARGS;
        }

        if (dsu__strlen(DSU_TXN_STAGE_DIR) + 1u + dsu__strlen(target_canon) + 1u > (dsu_u32)sizeof(staged_rel)) {
            dsu__free(target_canon);
            return DSU_STATUS_INVALID_ARGS;
        }
        memcpy(staged_rel, DSU_TXN_STAGE_DIR, dsu__strlen(DSU_TXN_STAGE_DIR));
        staged_rel[dsu__strlen(DSU_TXN_STAGE_DIR)] = '/';
        memcpy(staged_rel + dsu__strlen(DSU_TXN_STAGE_DIR) + 1u, target_canon, dsu__strlen(target_canon) + 1u);

        st = dsu__fs_path_info_rel(fs, (dsu_u32)DSU_JOURNAL_ROOT_TXN, staged_rel, &exists, &is_dir, &is_symlink);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(target_canon);
            return st;
        }
        if (!exists) {
            io_result->verified_missing += 1u;
            dsu__free(target_canon);
            continue;
        }
        if (is_dir || is_symlink) {
            dsu__free(target_canon);
            return DSU_STATUS_IO_ERROR;
        }

        st = dsu_fs_hash_file(fs, (dsu_u32)DSU_JOURNAL_ROOT_TXN, staged_rel, got);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(target_canon);
            return st;
        }
        if (expect_sha && memcmp(got, expect_sha, 32u) == 0) {
            io_result->verified_ok += 1u;
        } else {
            io_result->verified_mismatch += 1u;
        }
        dsu__free(target_canon);
        target_canon = NULL;
    }

    if (io_result->verified_missing != 0u || io_result->verified_mismatch != 0u) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__txn_verify_journal_paths(dsu_fs_t *fs, const dsu__txn_entry_t *entries, dsu_u32 entry_count) {
    dsu_u32 i;
    dsu_status_t st;
    char abs[1024];
    dsu_u32 root_count;

    if (!fs || (!entries && entry_count != 0u)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    root_count = dsu_fs_allowed_root_count(fs);
    for (i = 0u; i < entry_count; ++i) {
        const dsu__txn_entry_t *e = &entries[i];
        if ((dsu_u32)e->target_root >= root_count ||
            (dsu_u32)e->source_root >= root_count ||
            (dsu_u32)e->rollback_root >= root_count) {
            return DSU_STATUS_INVALID_ARGS;
        }
        st = dsu_fs_resolve_under_root(fs,
                                       (dsu_u32)e->target_root,
                                       e->target_path ? e->target_path : "",
                                       abs,
                                       (dsu_u32)sizeof(abs));
        if (st != DSU_STATUS_SUCCESS) return st;

        if (e->type == (dsu_u16)DSU_JOURNAL_ENTRY_COPY_FILE ||
            e->type == (dsu_u16)DSU_JOURNAL_ENTRY_MOVE_FILE ||
            e->type == (dsu_u16)DSU_JOURNAL_ENTRY_WRITE_STATE) {
            st = dsu_fs_resolve_under_root(fs,
                                           (dsu_u32)e->source_root,
                                           e->source_path ? e->source_path : "",
                                           abs,
                                           (dsu_u32)sizeof(abs));
            if (st != DSU_STATUS_SUCCESS) return st;
        }

        if (e->type == (dsu_u16)DSU_JOURNAL_ENTRY_CREATE_DIR ||
            e->type == (dsu_u16)DSU_JOURNAL_ENTRY_COPY_FILE ||
            e->type == (dsu_u16)DSU_JOURNAL_ENTRY_MOVE_FILE ||
            e->type == (dsu_u16)DSU_JOURNAL_ENTRY_DELETE_FILE ||
            e->type == (dsu_u16)DSU_JOURNAL_ENTRY_WRITE_STATE) {
            st = dsu_fs_resolve_under_root(fs,
                                           (dsu_u32)e->rollback_root,
                                           e->rollback_path ? e->rollback_path : "",
                                           abs,
                                           (dsu_u32)sizeof(abs));
            if (st != DSU_STATUS_SUCCESS) return st;
        }
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__txn_verify_installed_files(dsu_fs_t *fs,
                                                   const dsu_plan_t *plan,
                                                   const char *state_rel,
                                                   dsu_txn_result_t *io_result) {
    dsu_u32 i;
    dsu_status_t st;

    if (!fs || !plan || !state_rel || !io_result) {
        return DSU_STATUS_INVALID_ARGS;
    }
    io_result->verified_ok = 0u;
    io_result->verified_missing = 0u;
    io_result->verified_mismatch = 0u;

    for (i = 0u; i < dsu_plan_file_count(plan); ++i) {
        const char *target = dsu_plan_file_target_path(plan, i);
        const dsu_u8 *expect_sha = dsu_plan_file_sha256(plan, i);
        char *canon = NULL;
        dsu_u8 exists;
        dsu_u8 is_dir;
        dsu_u8 is_symlink;
        dsu_u8 got[32];

        st = dsu__canon_rel_path_ex(target ? target : "", 0, &canon);
        if (st != DSU_STATUS_SUCCESS) return st;
        if (dsu__strcmp_bytes(canon, state_rel) == 0) {
            dsu__free(canon);
            return DSU_STATUS_INVALID_ARGS;
        }

        st = dsu__fs_path_info_rel(fs, (dsu_u32)DSU_JOURNAL_ROOT_INSTALL, canon, &exists, &is_dir, &is_symlink);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(canon);
            return st;
        }
        if (!exists) {
            io_result->verified_missing += 1u;
            dsu__free(canon);
            continue;
        }
        if (is_dir || is_symlink) {
            dsu__free(canon);
            return DSU_STATUS_IO_ERROR;
        }

        st = dsu_fs_hash_file(fs, (dsu_u32)DSU_JOURNAL_ROOT_INSTALL, canon, got);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(canon);
            return st;
        }
        if (expect_sha && memcmp(got, expect_sha, 32u) == 0) {
            io_result->verified_ok += 1u;
        } else {
            io_result->verified_mismatch += 1u;
        }
        dsu__free(canon);
        canon = NULL;
    }
    if (io_result->verified_missing != 0u || io_result->verified_mismatch != 0u) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__txn_apply_entry(dsu_fs_t *fs, const dsu__txn_entry_t *e) {
    if (!fs || !e) return DSU_STATUS_INVALID_ARGS;
    switch (e->type) {
        case DSU_JOURNAL_ENTRY_CREATE_DIR:
            return dsu_fs_mkdir_p(fs, (dsu_u32)e->target_root, e->target_path ? e->target_path : "");
        case DSU_JOURNAL_ENTRY_REMOVE_DIR:
            return dsu_fs_rmdir_empty(fs, (dsu_u32)e->target_root, e->target_path ? e->target_path : "");
        case DSU_JOURNAL_ENTRY_COPY_FILE:
            return dsu_fs_copy_file(fs,
                                    (dsu_u32)e->source_root,
                                    e->source_path ? e->source_path : "",
                                    (dsu_u32)e->target_root,
                                    e->target_path ? e->target_path : "",
                                    0);
        case DSU_JOURNAL_ENTRY_MOVE_FILE:
        case DSU_JOURNAL_ENTRY_WRITE_STATE:
            return dsu_fs_move_path(fs,
                                    (dsu_u32)e->source_root,
                                    e->source_path ? e->source_path : "",
                                    (dsu_u32)e->target_root,
                                    e->target_path ? e->target_path : "",
                                    0);
        case DSU_JOURNAL_ENTRY_DELETE_FILE:
            return dsu_fs_delete_file(fs, (dsu_u32)e->target_root, e->target_path ? e->target_path : "");
        default:
            return DSU_STATUS_INVALID_ARGS;
    }
}

static dsu_status_t dsu__txn_rollback_entry(dsu_fs_t *fs, const dsu__txn_entry_t *e) {
    dsu_u8 exists;
    dsu_u8 is_dir;
    dsu_u8 is_symlink;
    dsu_status_t st;
    if (!fs || !e) return DSU_STATUS_INVALID_ARGS;
    switch (e->type) {
        case DSU_JOURNAL_ENTRY_CREATE_DIR:
            if (e->flags & (dsu_u32)DSU_JOURNAL_FLAG_TARGET_PREEXISTED) {
                return DSU_STATUS_SUCCESS;
            }
            return dsu_fs_rmdir_empty(fs, (dsu_u32)e->target_root, e->target_path ? e->target_path : "");
        case DSU_JOURNAL_ENTRY_MOVE_FILE:
        case DSU_JOURNAL_ENTRY_WRITE_STATE:
        case DSU_JOURNAL_ENTRY_COPY_FILE:
        case DSU_JOURNAL_ENTRY_DELETE_FILE:
            st = dsu__fs_path_info_rel(fs,
                                       (dsu_u32)e->target_root,
                                       e->target_path ? e->target_path : "",
                                       &exists,
                                       &is_dir,
                                       &is_symlink);
            if (st != DSU_STATUS_SUCCESS) return st;
            if (!exists) return DSU_STATUS_SUCCESS;
            if (is_dir || is_symlink) return DSU_STATUS_IO_ERROR;
            return dsu_fs_move_path(fs,
                                    (dsu_u32)e->target_root,
                                    e->target_path ? e->target_path : "",
                                    (dsu_u32)e->rollback_root,
                                    e->rollback_path ? e->rollback_path : "",
                                    0);
        case DSU_JOURNAL_ENTRY_REMOVE_DIR:
            return dsu_fs_mkdir_p(fs, (dsu_u32)e->rollback_root, e->rollback_path ? e->rollback_path : "");
        default:
            return DSU_STATUS_INVALID_ARGS;
    }
}

static dsu_status_t dsu__txn_commit(dsu_ctx_t *ctx,
                                   dsu_fs_t *fs,
                                   const char *journal_path_abs,
                                   const dsu__txn_entry_t *entries,
                                   dsu_u32 entry_count,
                                   const dsu_txn_options_t *opts,
                                   dsu_u32 *out_progress) {
    dsu_journal_writer_t w;
    dsu_status_t st;
    dsu_u32 i;
    dsu_u32 fail_after = 0u;

    if (out_progress) *out_progress = 0u;
    if (!ctx || !fs || !journal_path_abs || (!entries && entry_count != 0u)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (opts) fail_after = opts->fail_after_entries;

    memset(&w, 0, sizeof(w));
    st = dsu_journal_writer_open_append(&w, journal_path_abs);
    if (st != DSU_STATUS_SUCCESS) return st;

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_TXN_COMMIT_START,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_IO,
                      "commit start");

    for (i = 0u; i < entry_count; ++i) {
        dsu_u32 prog = i + 1u;
        st = dsu_journal_writer_append_progress(&w, prog);
        if (st != DSU_STATUS_SUCCESS) break;
        if (out_progress) {
            *out_progress = prog;
        }

        if (fail_after != 0u && prog == fail_after) {
            st = DSU_STATUS_INTERNAL_ERROR;
            break;
        }

        st = dsu__txn_apply_entry(fs, &entries[i]);
        if (st != DSU_STATUS_SUCCESS) {
            break;
        }

        (void)dsu_log_emit(ctx,
                          dsu_ctx_get_audit_log(ctx),
                          DSU_EVENT_TXN_COMMIT_ENTRY,
                          (dsu_u8)DSU_LOG_SEVERITY_INFO,
                          (dsu_u8)DSU_LOG_CATEGORY_IO,
                          "commit entry");
    }

    (void)dsu_journal_writer_close(&w);

    if (st == DSU_STATUS_SUCCESS) {
        (void)dsu_log_emit(ctx,
                          dsu_ctx_get_audit_log(ctx),
                          DSU_EVENT_TXN_COMMIT_COMPLETE,
                          (dsu_u8)DSU_LOG_SEVERITY_INFO,
                          (dsu_u8)DSU_LOG_CATEGORY_IO,
                          "commit complete");
    }
    return st;
}

static dsu_status_t dsu__txn_rollback(dsu_ctx_t *ctx,
                                     dsu_fs_t *fs,
                                     const dsu__txn_entry_t *entries,
                                     dsu_u32 entry_count,
                                     dsu_u32 progress_to_undo) {
    dsu_status_t st;
    dsu_u32 i;
    if (!ctx || !fs || (!entries && entry_count != 0u)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (progress_to_undo > entry_count) {
        progress_to_undo = entry_count;
    }

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_TXN_ROLLBACK_START,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_IO,
                      "rollback start");

    for (i = progress_to_undo; i != 0u; --i) {
        st = dsu__txn_rollback_entry(fs, &entries[i - 1u]);
        if (st != DSU_STATUS_SUCCESS) {
            return st;
        }
        (void)dsu_log_emit(ctx,
                          dsu_ctx_get_audit_log(ctx),
                          DSU_EVENT_TXN_ROLLBACK_ENTRY,
                          (dsu_u8)DSU_LOG_SEVERITY_INFO,
                          (dsu_u8)DSU_LOG_CATEGORY_IO,
                          "rollback entry");
    }

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_TXN_ROLLBACK_COMPLETE,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_IO,
                      "rollback complete");
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_txn_apply_plan(dsu_ctx_t *ctx,
                                const dsu_plan_t *plan,
                                const dsu_txn_options_t *opts,
                                dsu_txn_result_t *out_result) {
    dsu_status_t st;
    dsu_txn_options_t local_opts;
    dsu_u64 plan_digest;
    dsu_u64 journal_id;
    char install_root_abs[1024];
    char txn_root_abs[1024];
    char journal_path_abs[1024];
    char state_rel[256];
    dsu_fs_t *fs = NULL;
    char **extra_roots = NULL;
    dsu_u32 extra_root_count = 0u;
    dsu_u32 staged_count = 0u;
    char state_txn_rel[256];
    dsu__txn_entry_t *entries = NULL;
    dsu_u32 entry_count = 0u;
    dsu_u32 commit_progress = 0u;

    if (!out_result) {
        return DSU_STATUS_INVALID_ARGS;
    }
    dsu_txn_result_init(out_result);
    if (!ctx || !plan) {
        return DSU_STATUS_INVALID_ARGS;
    }

    dsu_txn_options_init(&local_opts);
    if (opts) {
        if (opts->struct_version != 1u || opts->struct_size < (dsu_u32)sizeof(*opts)) {
            return DSU_STATUS_INVALID_ARGS;
        }
        local_opts = *opts;
    }

    if (dsu_plan_operation(plan) == DSU_RESOLVE_OPERATION_UNINSTALL) {
        return DSU_STATUS_INVALID_REQUEST;
    }

    plan_digest = dsu_plan_id_hash64(plan);
    journal_id = dsu__nonce64(ctx, plan_digest);

    st = dsu__canon_abs_path(dsu_plan_install_root(plan), install_root_abs, (dsu_u32)sizeof(install_root_abs));
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu__plan_state_rel(plan, state_rel, (dsu_u32)sizeof(state_rel));
    if (st != DSU_STATUS_SUCCESS) goto done;
    if (dsu__path_has_prefix_seg(state_rel, DSU_TXN_INTERNAL_DIR)) {
        st = DSU_STATUS_INVALID_ARGS;
        goto done;
    }

    if (local_opts.txn_root && local_opts.txn_root[0] != '\0') {
        st = dsu__canon_abs_path(local_opts.txn_root, txn_root_abs, (dsu_u32)sizeof(txn_root_abs));
        if (st != DSU_STATUS_SUCCESS) goto done;
    } else {
        st = dsu__build_default_txn_root(install_root_abs, journal_id, txn_root_abs, (dsu_u32)sizeof(txn_root_abs));
        if (st != DSU_STATUS_SUCCESS) goto done;
        st = dsu__canon_abs_path(txn_root_abs, txn_root_abs, (dsu_u32)sizeof(txn_root_abs));
        if (st != DSU_STATUS_SUCCESS) goto done;
    }

    if (!dsu__same_volume_best_effort(install_root_abs, txn_root_abs)) {
        st = DSU_STATUS_INVALID_ARGS;
        goto done;
    }

    /* Ensure the txn root's parent exists (<install_root>.txn). */
    st = dsu__mkdir_parent_abs(txn_root_abs);
    if (st != DSU_STATUS_SUCCESS) goto done;

    if (local_opts.journal_path && local_opts.journal_path[0] != '\0') {
        st = dsu__canon_abs_path(local_opts.journal_path, journal_path_abs, (dsu_u32)sizeof(journal_path_abs));
        if (st != DSU_STATUS_SUCCESS) goto done;
    } else {
        st = dsu__build_default_journal_path(txn_root_abs, journal_path_abs, (dsu_u32)sizeof(journal_path_abs));
        if (st != DSU_STATUS_SUCCESS) goto done;
    }

    dsu__safe_cpy(out_result->install_root, (dsu_u32)sizeof(out_result->install_root), install_root_abs);
    dsu__safe_cpy(out_result->txn_root, (dsu_u32)sizeof(out_result->txn_root), txn_root_abs);
    dsu__safe_cpy(out_result->journal_path, (dsu_u32)sizeof(out_result->journal_path), journal_path_abs);
    dsu__safe_cpy(out_result->state_rel_path, (dsu_u32)sizeof(out_result->state_rel_path), state_rel);
    out_result->journal_id = journal_id;
    out_result->digest64 = plan_digest;

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_TXN_STAGE_START,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_IO,
                      "stage start");

    st = dsu__fs_create_for_plan(ctx, plan, install_root_abs, txn_root_abs, &fs, &extra_roots, &extra_root_count);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu__txn_stage_plan_files(fs, extra_roots, extra_root_count, plan, state_rel, &staged_count);
    if (st != DSU_STATUS_SUCCESS) goto done;
    out_result->staged_file_count = staged_count;

    st = dsu__txn_write_state_file(ctx, fs, plan, state_txn_rel, (dsu_u32)sizeof(state_txn_rel));
    if (st != DSU_STATUS_SUCCESS) goto done;

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_TXN_STAGE_COMPLETE,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_IO,
                      "stage complete");

    st = dsu__txn_build_entries_for_plan(fs, plan, state_rel, state_txn_rel, &entries, &entry_count);
    if (st != DSU_STATUS_SUCCESS) goto done;
    out_result->journal_entry_count = entry_count;

    st = dsu__txn_write_journal_file(journal_path_abs,
                                     journal_id,
                                     plan_digest,
                                     install_root_abs,
                                     txn_root_abs,
                                     state_rel,
                                     entries,
                                     entry_count);
    if (st != DSU_STATUS_SUCCESS) goto done;

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_TXN_JOURNAL_WRITTEN,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_IO,
                      "journal written");

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_TXN_VERIFY_START,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_IO,
                      "verify start");

    st = dsu__txn_verify_staged_files(fs, plan, state_rel, out_result);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu__txn_verify_journal_paths(fs, entries, entry_count);
    if (st != DSU_STATUS_SUCCESS) goto done;

    {
        dsu_u64 free_bytes = 0u;
        st = dsu_platform_disk_free_bytes(txn_root_abs, &free_bytes);
        if (st != DSU_STATUS_SUCCESS) goto done;
        if (free_bytes == 0u) {
            st = DSU_STATUS_IO_ERROR;
            goto done;
        }
    }

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_TXN_VERIFY_COMPLETE,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_IO,
                      "verify complete");

    if (local_opts.dry_run) {
        st = DSU_STATUS_SUCCESS;
        goto done;
    }

    st = dsu__txn_commit(ctx, fs, journal_path_abs, entries, entry_count, &local_opts, &commit_progress);
    out_result->commit_progress = commit_progress;
    if (st != DSU_STATUS_SUCCESS) {
        dsu_status_t rst = dsu__txn_rollback(ctx, fs, entries, entry_count, commit_progress);
        if (rst != DSU_STATUS_SUCCESS) {
            st = rst;
        }
        goto done;
    }
    out_result->commit_progress = entry_count;

    st = dsu__txn_verify_installed_files(fs, plan, state_rel, out_result);
    if (st != DSU_STATUS_SUCCESS) {
        dsu_status_t rst = dsu__txn_rollback(ctx, fs, entries, entry_count, entry_count);
        if (rst != DSU_STATUS_SUCCESS) {
            st = rst;
        }
        goto done;
    }

done:
    if (extra_roots) dsu__str_list_free(extra_roots, extra_root_count);
    if (entries) dsu__txn_entries_free(entries, entry_count);
    if (fs) dsu_fs_destroy(ctx, fs);
    return st;
}

static dsu_status_t dsu__fs_create_two_roots(dsu_ctx_t *ctx,
                                            const char *install_root_abs,
                                            const char *txn_root_abs,
                                            dsu_fs_t **out_fs) {
    const char *roots[2];
    dsu_fs_options_t fopts;
    if (out_fs) *out_fs = NULL;
    if (!ctx || !install_root_abs || !txn_root_abs || !out_fs) {
        return DSU_STATUS_INVALID_ARGS;
    }
    roots[0] = install_root_abs;
    roots[1] = txn_root_abs;
    dsu_fs_options_init(&fopts);
    fopts.allowed_roots = roots;
    fopts.allowed_root_count = 2u;
    return dsu_fs_create(ctx, &fopts, out_fs);
}

dsu_status_t dsu_txn_verify_state(dsu_ctx_t *ctx,
                                  const dsu_state_t *state,
                                  const dsu_txn_options_t *opts,
                                  dsu_txn_result_t *out_result) {
    dsu_status_t st;
    dsu_txn_options_t local_opts;
    char install_root_abs[1024];
    dsu_fs_t *fs = NULL;
    dsu_u32 i;

    if (!out_result) return DSU_STATUS_INVALID_ARGS;
    dsu_txn_result_init(out_result);
    if (!ctx || !state) return DSU_STATUS_INVALID_ARGS;

    dsu_txn_options_init(&local_opts);
    if (opts) {
        if (opts->struct_version != 1u || opts->struct_size < (dsu_u32)sizeof(*opts)) {
            return DSU_STATUS_INVALID_ARGS;
        }
        local_opts = *opts;
    }
    (void)local_opts;

    st = dsu__canon_abs_path(dsu_state_install_root(state), install_root_abs, (dsu_u32)sizeof(install_root_abs));
    if (st != DSU_STATUS_SUCCESS) return st;
    dsu__safe_cpy(out_result->install_root, (dsu_u32)sizeof(out_result->install_root), install_root_abs);

    {
        const char *roots[1];
        dsu_fs_options_t fopts;
        roots[0] = install_root_abs;
        dsu_fs_options_init(&fopts);
        fopts.allowed_roots = roots;
        fopts.allowed_root_count = 1u;
        st = dsu_fs_create(ctx, &fopts, &fs);
        if (st != DSU_STATUS_SUCCESS) return st;
    }

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_TXN_VERIFY_START,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_IO,
                      "verify start");

    out_result->verified_ok = 0u;
    out_result->verified_missing = 0u;
    out_result->verified_mismatch = 0u;

    for (i = 0u; i < dsu_state_file_count(state); ++i) {
        const char *p = dsu_state_file_path(state, i);
        const dsu_u8 *expect_sha = dsu_state_file_sha256(state, i);
        char *canon = NULL;
        dsu_u8 exists;
        dsu_u8 is_dir;
        dsu_u8 is_symlink;
        dsu_u8 got[32];

        st = dsu__canon_rel_path_ex(p ? p : "", 0, &canon);
        if (st != DSU_STATUS_SUCCESS) break;

        st = dsu__fs_path_info_rel(fs, 0u, canon, &exists, &is_dir, &is_symlink);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(canon);
            break;
        }
        if (!exists) {
            out_result->verified_missing += 1u;
            dsu__free(canon);
            continue;
        }
        if (is_dir || is_symlink) {
            dsu__free(canon);
            st = DSU_STATUS_IO_ERROR;
            break;
        }

        st = dsu_fs_hash_file(fs, 0u, canon, got);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(canon);
            break;
        }
        if (expect_sha && memcmp(got, expect_sha, 32u) == 0) {
            out_result->verified_ok += 1u;
        } else {
            out_result->verified_mismatch += 1u;
        }
        dsu__free(canon);
        canon = NULL;
    }

    if (fs) dsu_fs_destroy(ctx, fs);
    fs = NULL;

    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (out_result->verified_missing != 0u || out_result->verified_mismatch != 0u) {
        return DSU_STATUS_INTEGRITY_ERROR;
    }

    (void)dsu_log_emit(ctx,
                      dsu_ctx_get_audit_log(ctx),
                      DSU_EVENT_TXN_VERIFY_COMPLETE,
                      (dsu_u8)DSU_LOG_SEVERITY_INFO,
                      (dsu_u8)DSU_LOG_CATEGORY_IO,
                      "verify complete");
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_txn_uninstall_state(dsu_ctx_t *ctx,
                                     const dsu_state_t *state,
                                     const char *state_path,
                                     const dsu_txn_options_t *opts,
                                     dsu_txn_result_t *out_result) {
    dsu_status_t st;
    dsu_txn_options_t local_opts;
    char install_root_abs[1024];
    char txn_root_abs[1024];
    char journal_path_abs[1024];
    char state_rel_rm[256];
    dsu_u64 seed;
    dsu_u64 journal_id;
    dsu_fs_t *fs = NULL;
    char **paths = NULL;
    dsu_u32 path_count = 0u;
    dsu_u32 path_cap = 0u;
    dsu_u32 i;
    dsu__txn_entry_t *entries = NULL;
    dsu_u32 entry_count = 0u;
    dsu_u32 entry_cap = 0u;
    dsu_u32 commit_progress = 0u;

    if (!out_result) return DSU_STATUS_INVALID_ARGS;
    dsu_txn_result_init(out_result);
    if (!ctx || !state) return DSU_STATUS_INVALID_ARGS;

    dsu_txn_options_init(&local_opts);
    if (opts) {
        if (opts->struct_version != 1u || opts->struct_size < (dsu_u32)sizeof(*opts)) {
            return DSU_STATUS_INVALID_ARGS;
        }
        local_opts = *opts;
    }

    st = dsu__canon_abs_path(dsu_state_install_root(state), install_root_abs, (dsu_u32)sizeof(install_root_abs));
    if (st != DSU_STATUS_SUCCESS) return st;

    seed = ((dsu_u64)dsu_hash32_str(dsu_state_product_id(state)) << 32)
         ^ (dsu_u64)dsu_hash32_str(install_root_abs);
    journal_id = dsu__nonce64(ctx, seed);

    state_rel_rm[0] = '\0';
    if (state_path && state_path[0] != '\0') {
        char state_abs[1024];
        char *canon_rel = NULL;
        dsu_u32 root_len;
        st = dsu__canon_abs_path(state_path, state_abs, (dsu_u32)sizeof(state_abs));
        if (st != DSU_STATUS_SUCCESS) return st;
        root_len = dsu__strlen(install_root_abs);
        if (root_len != 0xFFFFFFFFu &&
            memcmp(state_abs, install_root_abs, (size_t)root_len) == 0 &&
            state_abs[root_len] == '/') {
            st = dsu__canon_rel_path_ex(state_abs + root_len + 1u, 0, &canon_rel);
            if (st != DSU_STATUS_SUCCESS) return st;
            if (dsu__strlen(canon_rel) + 1u <= (dsu_u32)sizeof(state_rel_rm)) {
                dsu__safe_cpy(state_rel_rm, (dsu_u32)sizeof(state_rel_rm), canon_rel);
            }
            dsu__free(canon_rel);
            canon_rel = NULL;
        }
    }

    if (local_opts.txn_root && local_opts.txn_root[0] != '\0') {
        st = dsu__canon_abs_path(local_opts.txn_root, txn_root_abs, (dsu_u32)sizeof(txn_root_abs));
        if (st != DSU_STATUS_SUCCESS) return st;
    } else {
        st = dsu__build_default_txn_root(install_root_abs, journal_id, txn_root_abs, (dsu_u32)sizeof(txn_root_abs));
        if (st != DSU_STATUS_SUCCESS) return st;
        st = dsu__canon_abs_path(txn_root_abs, txn_root_abs, (dsu_u32)sizeof(txn_root_abs));
        if (st != DSU_STATUS_SUCCESS) return st;
    }
    if (!dsu__same_volume_best_effort(install_root_abs, txn_root_abs)) {
        return DSU_STATUS_INVALID_ARGS;
    }

    st = dsu__mkdir_parent_abs(txn_root_abs);
    if (st != DSU_STATUS_SUCCESS) return st;

    if (local_opts.journal_path && local_opts.journal_path[0] != '\0') {
        st = dsu__canon_abs_path(local_opts.journal_path, journal_path_abs, (dsu_u32)sizeof(journal_path_abs));
        if (st != DSU_STATUS_SUCCESS) return st;
    } else {
        st = dsu__build_default_journal_path(txn_root_abs, journal_path_abs, (dsu_u32)sizeof(journal_path_abs));
        if (st != DSU_STATUS_SUCCESS) return st;
    }

    dsu__safe_cpy(out_result->install_root, (dsu_u32)sizeof(out_result->install_root), install_root_abs);
    dsu__safe_cpy(out_result->txn_root, (dsu_u32)sizeof(out_result->txn_root), txn_root_abs);
    dsu__safe_cpy(out_result->journal_path, (dsu_u32)sizeof(out_result->journal_path), journal_path_abs);
    dsu__safe_cpy(out_result->state_rel_path, (dsu_u32)sizeof(out_result->state_rel_path), state_rel_rm);
    out_result->journal_id = journal_id;
    out_result->digest64 = seed;

    st = dsu__fs_create_two_roots(ctx, install_root_abs, txn_root_abs, &fs);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_fs_mkdir_p(fs, (dsu_u32)DSU_JOURNAL_ROOT_TXN, DSU_TXN_JOURNAL_DIR);
    if (st != DSU_STATUS_SUCCESS) goto done;

    /* Collect existing installed files to remove (deterministic by path). */
    for (i = 0u; i < dsu_state_file_count(state); ++i) {
        const char *p = dsu_state_file_path(state, i);
        char *canon = NULL;
        dsu_u8 exists;
        dsu_u8 is_dir;
        dsu_u8 is_symlink;

        st = dsu__canon_rel_path_ex(p ? p : "", 0, &canon);
        if (st != DSU_STATUS_SUCCESS) goto done;
        if (dsu__path_has_prefix_seg(canon, DSU_TXN_INTERNAL_DIR)) {
            dsu__free(canon);
            st = DSU_STATUS_INVALID_ARGS;
            goto done;
        }
        st = dsu__fs_path_info_rel(fs, (dsu_u32)DSU_JOURNAL_ROOT_INSTALL, canon, &exists, &is_dir, &is_symlink);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(canon);
            goto done;
        }
        if (exists && (is_dir || is_symlink)) {
            dsu__free(canon);
            st = DSU_STATUS_IO_ERROR;
            goto done;
        }
        if (exists) {
            st = dsu__str_list_add_unique(&paths, &path_count, &path_cap, canon);
            if (st != DSU_STATUS_SUCCESS) {
                dsu__free(canon);
                goto done;
            }
        }
        dsu__free(canon);
        canon = NULL;
    }

    if (state_rel_rm[0] != '\0') {
        dsu_u8 exists;
        dsu_u8 is_dir;
        dsu_u8 is_symlink;
        st = dsu__fs_path_info_rel(fs, (dsu_u32)DSU_JOURNAL_ROOT_INSTALL, state_rel_rm, &exists, &is_dir, &is_symlink);
        if (st != DSU_STATUS_SUCCESS) goto done;
        if (exists && (is_dir || is_symlink)) {
            st = DSU_STATUS_IO_ERROR;
            goto done;
        }
        if (exists) {
            st = dsu__str_list_add_unique(&paths, &path_count, &path_cap, state_rel_rm);
            if (st != DSU_STATUS_SUCCESS) goto done;
        }
    }

    if (path_count > 1u) {
        dsu__sort_str_ptrs(paths, path_count);
    }

    for (i = 0u; i < path_count; ++i) {
        dsu__txn_entry_t e;
        memset(&e, 0, sizeof(e));
        e.type = (dsu_u16)DSU_JOURNAL_ENTRY_MOVE_FILE;
        e.source_root = (dsu_u8)DSU_JOURNAL_ROOT_INSTALL;
        e.source_path = dsu__strdup(paths[i]);
        e.target_root = (dsu_u8)DSU_JOURNAL_ROOT_TXN;
        e.target_path = dsu__strdup(paths[i]);
        e.rollback_root = (dsu_u8)DSU_JOURNAL_ROOT_INSTALL;
        e.rollback_path = dsu__strdup(paths[i]);
        if (!e.source_path || !e.target_path || !e.rollback_path) {
            dsu__free(e.source_path);
            dsu__free(e.target_path);
            dsu__free(e.rollback_path);
            st = DSU_STATUS_IO_ERROR;
            goto done;
        }
        st = dsu__txn_entries_push_take(&entries, &entry_count, &entry_cap, &e);
        if (st != DSU_STATUS_SUCCESS) {
            dsu__free(e.source_path);
            dsu__free(e.target_path);
            dsu__free(e.rollback_path);
            goto done;
        }
    }
    out_result->journal_entry_count = entry_count;

    st = dsu__txn_write_journal_file(journal_path_abs,
                                     journal_id,
                                     seed,
                                     install_root_abs,
                                     txn_root_abs,
                                     state_rel_rm,
                                     entries,
                                     entry_count);
    if (st != DSU_STATUS_SUCCESS) goto done;

    if (local_opts.dry_run) {
        st = DSU_STATUS_SUCCESS;
        goto done;
    }

    st = dsu__txn_commit(ctx, fs, journal_path_abs, entries, entry_count, &local_opts, &commit_progress);
    out_result->commit_progress = commit_progress;
    if (st != DSU_STATUS_SUCCESS) {
        dsu_status_t rst = dsu__txn_rollback(ctx, fs, entries, entry_count, commit_progress);
        if (rst != DSU_STATUS_SUCCESS) {
            st = rst;
        }
        goto done;
    }
    out_result->commit_progress = entry_count;

done:
    if (paths) dsu__str_list_free(paths, path_count);
    if (entries) dsu__txn_entries_free(entries, entry_count);
    if (fs) dsu_fs_destroy(ctx, fs);
    return st;
}

dsu_status_t dsu_txn_rollback_journal(dsu_ctx_t *ctx,
                                      const char *journal_path,
                                      const dsu_txn_options_t *opts,
                                      dsu_txn_result_t *out_result) {
    dsu_status_t st;
    dsu_txn_options_t local_opts;
    dsu_journal_t *journal = NULL;
    dsu_fs_t *fs = NULL;
    dsu__txn_entry_t *tmp = NULL;
    dsu_u32 i;
    dsu_u32 progress;

    if (!out_result) return DSU_STATUS_INVALID_ARGS;
    dsu_txn_result_init(out_result);
    if (!ctx || !journal_path || journal_path[0] == '\0') return DSU_STATUS_INVALID_ARGS;

    dsu_txn_options_init(&local_opts);
    if (opts) {
        if (opts->struct_version != 1u || opts->struct_size < (dsu_u32)sizeof(*opts)) {
            return DSU_STATUS_INVALID_ARGS;
        }
        local_opts = *opts;
    }

    st = dsu_journal_read_file(ctx, journal_path, &journal);
    if (st != DSU_STATUS_SUCCESS) goto done;

    if (!journal->install_root || !journal->txn_root) {
        st = DSU_STATUS_INTEGRITY_ERROR;
        goto done;
    }

    dsu__safe_cpy(out_result->install_root, (dsu_u32)sizeof(out_result->install_root), journal->install_root);
    dsu__safe_cpy(out_result->txn_root, (dsu_u32)sizeof(out_result->txn_root), journal->txn_root);
    dsu__safe_cpy(out_result->journal_path, (dsu_u32)sizeof(out_result->journal_path), journal_path);
    dsu__safe_cpy(out_result->state_rel_path, (dsu_u32)sizeof(out_result->state_rel_path), journal->state_path ? journal->state_path : "");
    out_result->journal_id = journal->journal_id;
    out_result->digest64 = journal->plan_digest;
    out_result->journal_entry_count = journal->entry_count;
    out_result->commit_progress = journal->commit_progress;

    st = dsu__fs_create_two_roots(ctx, journal->install_root, journal->txn_root, &fs);
    if (st != DSU_STATUS_SUCCESS) goto done;

    progress = journal->commit_progress;
    if (progress > journal->entry_count) progress = journal->entry_count;

    tmp = (dsu__txn_entry_t *)dsu__malloc(journal->entry_count * (dsu_u32)sizeof(*tmp));
    if (!tmp && journal->entry_count != 0u) {
        st = DSU_STATUS_IO_ERROR;
        goto done;
    }
    if (journal->entry_count) {
        memset(tmp, 0, (size_t)journal->entry_count * sizeof(*tmp));
    }
    for (i = 0u; i < journal->entry_count; ++i) {
        const dsu_journal_entry_t *e = &journal->entries[i];
        tmp[i].type = e->type;
        tmp[i].target_root = e->target_root;
        tmp[i].source_root = e->source_root;
        tmp[i].rollback_root = e->rollback_root;
        tmp[i].target_path = e->target_path;
        tmp[i].source_path = e->source_path;
        tmp[i].rollback_path = e->rollback_path;
        tmp[i].flags = e->flags;
    }

    if (local_opts.dry_run) {
        st = DSU_STATUS_SUCCESS;
        goto done;
    }

    st = dsu__txn_rollback(ctx, fs, tmp, journal->entry_count, progress);
    if (st != DSU_STATUS_SUCCESS) goto done;

    /* Mark rolled back (append-only). */
    {
        dsu_journal_writer_t w;
        memset(&w, 0, sizeof(w));
        if (dsu_journal_writer_open_append(&w, journal_path) == DSU_STATUS_SUCCESS) {
            (void)dsu_journal_writer_append_progress(&w, 0u);
            (void)dsu_journal_writer_close(&w);
        }
    }

done:
    dsu__free(tmp);
    tmp = NULL;
    if (fs) dsu_fs_destroy(ctx, fs);
    if (journal) dsu_journal_destroy(ctx, journal);
    return st;
}
