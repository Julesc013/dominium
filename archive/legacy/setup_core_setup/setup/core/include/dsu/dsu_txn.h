/*
FILE: source/dominium/setup/core/include/dsu/dsu_txn.h
MODULE: Dominium Setup
PURPOSE: Journaled transaction engine for applying setup plans (Plan S-4).
*/
#ifndef DSU_TXN_H_INCLUDED
#define DSU_TXN_H_INCLUDED

#include "dsu_ctx.h"
#include "dsu_plan.h"
#include "dsu_state.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_txn_result_t {
    dsu_u32 struct_size;
    dsu_u32 struct_version;

    dsu_u64 journal_id;
    dsu_u64 digest64;

    char install_root[1024];
    char txn_root[1024];
    char journal_path[1024];
    char state_rel_path[256];

    dsu_u32 journal_entry_count;
    dsu_u32 commit_progress;

    dsu_u32 staged_file_count;
    dsu_u32 verified_ok;
    dsu_u32 verified_missing;
    dsu_u32 verified_mismatch;
} dsu_txn_result_t;

typedef struct dsu_txn_options_t {
    dsu_u32 struct_size;
    dsu_u32 struct_version;

    dsu_bool dry_run;

    /* Optional: override journal output path (absolute). Default: <txn_root>/txn.dsujournal */
    const char *journal_path;

    /* Optional: override txn root (absolute). Default: <install_root>.txn/<journal_id_hex> */
    const char *txn_root;

    /* Optional: failure injection for tests (0 => disabled). */
    dsu_u32 fail_after_entries;
} dsu_txn_options_t;

DSU_API void dsu_txn_result_init(dsu_txn_result_t *out_result);
DSU_API void dsu_txn_options_init(dsu_txn_options_t *opts);

/*
Apply a plan: stage -> verify -> (commit | dry-run).
The plan's operation controls install/upgrade/repair semantics.
*/
DSU_API dsu_status_t dsu_txn_apply_plan(dsu_ctx_t *ctx,
                                       const dsu_plan_t *plan,
                                       const dsu_txn_options_t *opts,
                                       dsu_txn_result_t *out_result);

/* Verify-only using an installed state snapshot (no filesystem mutation). */
DSU_API dsu_status_t dsu_txn_verify_state(dsu_ctx_t *ctx,
                                         const dsu_state_t *state,
                                         const dsu_txn_options_t *opts,
                                         dsu_txn_result_t *out_result);

/*
Uninstall using an installed state snapshot. `state_path` is the on-disk path used to load the state;
if it is under the install root, it will be removed as part of the uninstall transaction.
*/
DSU_API dsu_status_t dsu_txn_uninstall_state(dsu_ctx_t *ctx,
                                            const dsu_state_t *state,
                                            const char *state_path,
                                            const dsu_txn_options_t *opts,
                                            dsu_txn_result_t *out_result);

/* Roll back a transaction described by a journal file. */
DSU_API dsu_status_t dsu_txn_rollback_journal(dsu_ctx_t *ctx,
                                             const char *journal_path,
                                             const dsu_txn_options_t *opts,
                                             dsu_txn_result_t *out_result);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_TXN_H_INCLUDED */

