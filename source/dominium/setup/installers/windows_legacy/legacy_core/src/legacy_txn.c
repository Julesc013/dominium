/*
FILE: source/dominium/setup/installers/macos_classic/core_legacy/src/legacy_txn.c
MODULE: Dominium Setup (Legacy Core)
PURPOSE: Legacy apply flow, component selection, and rollback.
*/
#include "legacy_internal.h"

#include <stdio.h>

#define DSU_MANIFEST_COMPONENT_FLAG_OPTIONAL          0x00000001u
#define DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED  0x00000002u
#define DSU_MANIFEST_COMPONENT_FLAG_HIDDEN            0x00000004u

typedef struct dsu_legacy_txn_t {
    char **files;
    dsu_legacy_u32 file_count;
    dsu_legacy_u32 file_cap;
    dsu_legacy_log_t *log;
    dsu_legacy_state_t *state;
} dsu_legacy_txn_t;

static dsu_legacy_status_t dsu_legacy_txn_push_file(dsu_legacy_txn_t *txn, const char *rel_path) {
    char **p;
    dsu_legacy_u32 count;
    dsu_legacy_u32 cap;
    char *dup;
    if (!txn || !rel_path) return DSU_LEGACY_STATUS_INVALID_ARGS;
    dup = dsu_legacy_strdup(rel_path);
    if (!dup) return DSU_LEGACY_STATUS_IO_ERROR;
    count = txn->file_count;
    cap = txn->file_cap;
    if (count == cap) {
        dsu_legacy_u32 new_cap = (cap == 0u) ? 16u : (cap * 2u);
        p = (char **)realloc(txn->files, (size_t)new_cap * sizeof(*p));
        if (!p) {
            free(dup);
            return DSU_LEGACY_STATUS_IO_ERROR;
        }
        txn->files = p;
        txn->file_cap = new_cap;
    }
    txn->files[count] = dup;
    txn->file_count = count + 1u;
    return DSU_LEGACY_STATUS_SUCCESS;
}

static void dsu_legacy_txn_free(dsu_legacy_txn_t *txn) {
    dsu_legacy_u32 i;
    if (!txn) return;
    for (i = 0u; i < txn->file_count; ++i) {
        free(txn->files[i]);
    }
    free(txn->files);
    txn->files = NULL;
    txn->file_count = 0u;
    txn->file_cap = 0u;
}

static dsu_legacy_status_t dsu_legacy_txn_on_copy(const char *rel_path,
                                                  const char *dst_path,
                                                  void *user) {
    dsu_legacy_txn_t *txn = (dsu_legacy_txn_t *)user;
    dsu_legacy_status_t st;
    dsu_legacy_u64 size = 0u;
    FILE *f;
    if (!txn || !rel_path || !dst_path) return DSU_LEGACY_STATUS_INVALID_ARGS;
    st = dsu_legacy_txn_push_file(txn, rel_path);
    if (st != DSU_LEGACY_STATUS_SUCCESS) return st;

    f = fopen(dst_path, "rb");
    if (f) {
        if (fseek(f, 0, SEEK_END) == 0) {
            long sz = ftell(f);
            if (sz >= 0) size = (dsu_legacy_u64)(unsigned long)sz;
        }
        fclose(f);
    }
    if (txn->state) {
        st = dsu_legacy_state_add_file(txn->state, rel_path, size);
        if (st != DSU_LEGACY_STATUS_SUCCESS) return st;
    }
    if (txn->log) {
        dsu_legacy_log_printf(txn->log, "FILE %s", rel_path);
    }
    return DSU_LEGACY_STATUS_SUCCESS;
}

static dsu_legacy_status_t dsu_legacy_txn_rollback(const char *install_root, dsu_legacy_txn_t *txn) {
    dsu_legacy_u32 i;
    if (!install_root || !txn) return DSU_LEGACY_STATUS_INVALID_ARGS;
    for (i = txn->file_count; i > 0u; --i) {
        char *rel = txn->files[i - 1u];
        char *full = NULL;
        dsu_legacy_u32 n = dsu_legacy_strlen(install_root) + dsu_legacy_strlen(rel) + 2u;
        full = (char *)malloc((size_t)n);
        if (!full) continue;
        sprintf(full, "%s/%s", install_root, rel);
        remove(full);
        free(full);
    }
    return DSU_LEGACY_STATUS_SUCCESS;
}

static int dsu_legacy_list_contains(char **items, dsu_legacy_u32 count, const char *id) {
    dsu_legacy_u32 i;
    if (!items || !id) return 0;
    for (i = 0u; i < count; ++i) {
        if (items[i] && strcmp(items[i], id) == 0) {
            return 1;
        }
    }
    return 0;
}

static int dsu_legacy_component_should_install(const dsu_legacy_manifest_component_t *c,
                                               const dsu_legacy_invocation_t *inv,
                                               int have_defaults) {
    int hidden;
    if (!c || !inv) return 0;
    hidden = ((c->flags & DSU_MANIFEST_COMPONENT_FLAG_HIDDEN) != 0u);
    if (hidden) return 0;
    if (inv->selected_component_count != 0u) {
        if (!dsu_legacy_list_contains(inv->selected_components, inv->selected_component_count, c->id)) {
            return 0;
        }
    } else if (have_defaults) {
        if ((c->flags & DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED) == 0u) {
            return 0;
        }
    }
    if (inv->excluded_component_count != 0u) {
        if (dsu_legacy_list_contains(inv->excluded_components, inv->excluded_component_count, c->id)) {
            return 0;
        }
    }
    return 1;
}

static const char *dsu_legacy_select_install_root(const dsu_legacy_manifest_t *m,
                                                  const dsu_legacy_invocation_t *inv) {
    dsu_legacy_u32 i;
    if (inv && inv->install_root_count > 0u && inv->install_roots[0]) {
        return inv->install_roots[0];
    }
    if (!m || !inv) return NULL;
    for (i = 0u; i < m->install_root_count; ++i) {
        const dsu_legacy_manifest_install_root_t *r = &m->install_roots[i];
        if (r->scope == inv->scope) {
            if (!inv->platform_triple || !r->platform || strcmp(inv->platform_triple, r->platform) == 0) {
                return r->path;
            }
        }
    }
    if (m->install_root_count != 0u) {
        return m->install_roots[0].path;
    }
    return NULL;
}

static char *dsu_legacy_join_path(const char *a, const char *b) {
    dsu_legacy_u32 na;
    dsu_legacy_u32 nb;
    char *out;
    if (!a || !b) return NULL;
    na = dsu_legacy_strlen(a);
    nb = dsu_legacy_strlen(b);
    out = (char *)malloc((size_t)(na + nb + 2u));
    if (!out) return NULL;
    memcpy(out, a, (size_t)na);
    out[na] = '/';
    memcpy(out + na + 1u, b, (size_t)nb);
    out[na + 1u + nb] = '\0';
    return out;
}

dsu_legacy_status_t dsu_legacy_apply(const dsu_legacy_manifest_t *manifest,
                                     const dsu_legacy_invocation_t *invocation,
                                     const char *payload_root,
                                     const char *state_path,
                                     const char *log_path) {
    dsu_legacy_status_t st;
    dsu_legacy_u32 i;
    dsu_legacy_log_t log;
    dsu_legacy_txn_t txn;
    dsu_legacy_state_t *state;
    const char *install_root;
    int have_defaults = 0;

    if (!manifest || !invocation || !payload_root || !state_path) {
        return DSU_LEGACY_STATUS_INVALID_ARGS;
    }
    if (invocation->operation == (dsu_legacy_u8)DSU_LEGACY_OPERATION_UNINSTALL) {
        return dsu_legacy_uninstall(state_path, log_path);
    }

    memset(&log, 0, sizeof(log));
    if (log_path && log_path[0] != '\0') {
        st = dsu_legacy_log_open(&log, log_path);
        if (st != DSU_LEGACY_STATUS_SUCCESS) {
            return st;
        }
    }

    install_root = dsu_legacy_select_install_root(manifest, invocation);
    if (!install_root || install_root[0] == '\0') {
        dsu_legacy_log_close(&log);
        return DSU_LEGACY_STATUS_INVALID_ARGS;
    }

    state = (dsu_legacy_state_t *)malloc(sizeof(*state));
    if (!state) {
        dsu_legacy_log_close(&log);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }
    memset(state, 0, sizeof(*state));
    state->product_id = dsu_legacy_strdup(manifest->product_id ? manifest->product_id : "dominium");
    state->product_version = dsu_legacy_strdup(manifest->product_version ? manifest->product_version : "0.0.0");
    state->platform_triple = dsu_legacy_strdup(invocation->platform_triple ? invocation->platform_triple : "macos-x86");
    state->scope = invocation->scope;
    state->install_root = dsu_legacy_strdup(install_root);
    if (!state->product_id || !state->product_version || !state->platform_triple || !state->install_root) {
        dsu_legacy_state_free(state);
        dsu_legacy_log_close(&log);
        return DSU_LEGACY_STATUS_IO_ERROR;
    }

    for (i = 0u; i < manifest->component_count; ++i) {
        if ((manifest->components[i].flags & DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED) != 0u) {
            have_defaults = 1;
            break;
        }
    }

    memset(&txn, 0, sizeof(txn));
    txn.log = (log.f ? &log : NULL);
    txn.state = state;

    for (i = 0u; i < manifest->component_count; ++i) {
        const dsu_legacy_manifest_component_t *c = &manifest->components[i];
        dsu_legacy_u32 j;
        if (!dsu_legacy_component_should_install(c, invocation, have_defaults)) {
            continue;
        }
        {
            const char *ver = (c->version && c->version[0] != '\0') ?
                c->version : (manifest->product_version ? manifest->product_version : "");
            if (dsu_legacy_state_add_component(state, c->id ? c->id : "", ver) != DSU_LEGACY_STATUS_SUCCESS) {
            st = DSU_LEGACY_STATUS_IO_ERROR;
            goto rollback;
            }
        }
        if (txn.log) {
            dsu_legacy_log_printf(txn.log, "COMPONENT %s", c->id ? c->id : "");
        }
        for (j = 0u; j < c->payload_count; ++j) {
            const dsu_legacy_manifest_payload_t *p = &c->payloads[j];
            char *payload_path = dsu_legacy_join_path(payload_root, p->path ? p->path : "");
            if (!payload_path) {
                st = DSU_LEGACY_STATUS_IO_ERROR;
                goto rollback;
            }
            if (p->kind == (dsu_legacy_u8)DSU_LEGACY_PAYLOAD_ARCHIVE) {
                st = dsu_legacy_fs_extract_archive(payload_path, install_root, dsu_legacy_txn_on_copy, &txn);
            } else if (p->kind == (dsu_legacy_u8)DSU_LEGACY_PAYLOAD_FILESET) {
                st = dsu_legacy_fs_copy_tree(payload_path, install_root, dsu_legacy_txn_on_copy, &txn);
            } else {
                /* blob: copy the payload file into install root */
                char *dst = NULL;
                char *name = p->path ? strrchr(p->path, '/') : NULL;
                if (!name) name = p->path ? strrchr(p->path, '\\') : NULL;
                if (!name) name = (char *)(p->path ? p->path : "payload.bin");
                else name += 1;
                dst = dsu_legacy_join_path(install_root, name);
                if (!dst) {
                    free(payload_path);
                    st = DSU_LEGACY_STATUS_IO_ERROR;
                    goto rollback;
                }
                st = dsu_legacy_fs_copy_file(payload_path, dst);
                if (st == DSU_LEGACY_STATUS_SUCCESS) {
                    st = dsu_legacy_txn_on_copy(name, dst, &txn);
                }
                free(dst);
            }
            free(payload_path);
            if (st != DSU_LEGACY_STATUS_SUCCESS) {
                goto rollback;
            }
        }
    }

    st = dsu_legacy_state_write(state, state_path);
    if (st != DSU_LEGACY_STATUS_SUCCESS) goto rollback;

    dsu_legacy_txn_free(&txn);
    dsu_legacy_state_free(state);
    dsu_legacy_log_close(&log);
    return DSU_LEGACY_STATUS_SUCCESS;

rollback:
    (void)dsu_legacy_txn_rollback(install_root, &txn);
    dsu_legacy_txn_free(&txn);
    dsu_legacy_state_free(state);
    dsu_legacy_log_close(&log);
    return st;
}
