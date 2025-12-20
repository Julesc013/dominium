/*
FILE: source/dominium/setup/core/src/txn/dsu_journal.h
MODULE: Dominium Setup
PURPOSE: Binary transaction journal format + IO (Plan S-4).
*/
#ifndef DSU_JOURNAL_H_INCLUDED
#define DSU_JOURNAL_H_INCLUDED

#include "../util/dsu_util_internal.h"
#include "../../include/dsu/dsu_ctx.h"

#include <stdio.h>

#define DSU_JOURNAL_MAGIC_0 'D'
#define DSU_JOURNAL_MAGIC_1 'S'
#define DSU_JOURNAL_MAGIC_2 'U'
#define DSU_JOURNAL_MAGIC_3 'J'

#define DSU_JOURNAL_FORMAT_VERSION 1u

/* Entry record types (outer TLV "type"). */
typedef enum dsu_journal_entry_type_t {
    DSU_JOURNAL_ENTRY_NOOP = 0x0000u,
    DSU_JOURNAL_ENTRY_CREATE_DIR = 0x0001u,
    DSU_JOURNAL_ENTRY_REMOVE_DIR = 0x0002u,
    DSU_JOURNAL_ENTRY_COPY_FILE = 0x0003u,
    DSU_JOURNAL_ENTRY_MOVE_FILE = 0x0004u,
    DSU_JOURNAL_ENTRY_DELETE_FILE = 0x0005u,
    DSU_JOURNAL_ENTRY_WRITE_STATE = 0x0006u
} dsu_journal_entry_type_t;

/* Root indices used by journal entries (mapped by the metadata NOOP record). */
typedef enum dsu_journal_root_index_t {
    DSU_JOURNAL_ROOT_INSTALL = 0u,
    DSU_JOURNAL_ROOT_TXN = 1u
} dsu_journal_root_index_t;

/* Entry flags (u32). */
#define DSU_JOURNAL_FLAG_TARGET_PREEXISTED 0x00000001u

typedef struct dsu_journal_entry_t {
    dsu_u16 type;

    dsu_u8 target_root;
    dsu_u8 source_root;
    dsu_u8 rollback_root;
    dsu_u8 reserved8;

    char *target_path;   /* relative DSU path */
    char *source_path;   /* relative DSU path */
    char *rollback_path; /* relative DSU path */

    dsu_u32 flags;
} dsu_journal_entry_t;

typedef struct dsu_journal_t {
    dsu_u64 journal_id;
    dsu_u64 plan_digest;

    char *install_root; /* absolute canonical */
    char *txn_root;     /* absolute canonical */
    char *state_path;   /* relative to install root (canonical) */

    dsu_u32 commit_progress; /* count of forward entries completed */

    dsu_u32 entry_count;
    dsu_journal_entry_t *entries; /* forward mutation entries only (no NOOP) */
} dsu_journal_t;

typedef struct dsu_journal_writer_t {
    FILE *f;
    dsu_u64 journal_id;
    dsu_u64 plan_digest;
} dsu_journal_writer_t;

dsu_status_t dsu_journal_writer_open(dsu_journal_writer_t *w,
                                    const char *path,
                                    dsu_u64 journal_id,
                                    dsu_u64 plan_digest);
dsu_status_t dsu_journal_writer_open_append(dsu_journal_writer_t *w, const char *path);
dsu_status_t dsu_journal_writer_write_meta(dsu_journal_writer_t *w,
                                          const char *install_root_abs,
                                          const char *txn_root_abs,
                                          const char *state_rel);
dsu_status_t dsu_journal_writer_append_progress(dsu_journal_writer_t *w, dsu_u32 commit_progress);
dsu_status_t dsu_journal_writer_append_entry(dsu_journal_writer_t *w,
                                            dsu_u16 entry_type,
                                            dsu_u8 target_root,
                                            const char *target_path,
                                            dsu_u8 source_root,
                                            const char *source_path,
                                            dsu_u8 rollback_root,
                                            const char *rollback_path,
                                            dsu_u32 flags);
dsu_status_t dsu_journal_writer_close(dsu_journal_writer_t *w);

dsu_status_t dsu_journal_read_file(dsu_ctx_t *ctx, const char *path, dsu_journal_t **out_journal);
void dsu_journal_destroy(dsu_ctx_t *ctx, dsu_journal_t *journal);

#endif /* DSU_JOURNAL_H_INCLUDED */
