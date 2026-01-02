/*
FILE: source/dominium/setup/core/include/dsu/dsu_job.h
MODULE: Dominium Setup
PURPOSE: Resumable job journaling + execution wrapper for long setup operations.
NOTES: Job journals live under install root staging (".dsu_txn/jobs").
*/
#ifndef DSU_JOB_H_INCLUDED
#define DSU_JOB_H_INCLUDED

#include "dsu_ctx.h"
#include "dsu_txn.h"
#include "dominium/core_err.h"
#include "dominium/core_job.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DSU_JOB_INPUT_TLV_VERSION 1u
#define DSU_JOB_OPTIONS_VERSION 1u
#define DSU_JOB_PATH_MAX 1024u

typedef struct dsu_job_input_t {
    dsu_u32 schema_version;
    dsu_u32 job_type; /* core_job_type */
    dsu_u32 dry_run;
    dsu_u32 flags;
    char plan_path[DSU_JOB_PATH_MAX];
    char state_path[DSU_JOB_PATH_MAX];
    char log_path[DSU_JOB_PATH_MAX];
} dsu_job_input_t;

typedef struct dsu_job_options_t {
    dsu_u32 struct_size;
    dsu_u32 struct_version;

    /* Test-only: stop after setting current_step to this ID (0 => disabled). */
    dsu_u32 stop_after_step;

    /* Forwarded to dsu_txn_options.fail_after_entries (0 => disabled). */
    dsu_u32 fail_after_entries;
} dsu_job_options_t;

typedef struct dsu_job_run_result_t {
    core_job_state state;
    err_t err;
    dsu_txn_result_t txn_result;
} dsu_job_run_result_t;

DSU_API void dsu_job_input_init(dsu_job_input_t *in);
DSU_API void dsu_job_options_init(dsu_job_options_t *opts);

/* Build job root path from install root (e.g. "<install_root>/.dsu_txn/jobs"). */
DSU_API dsu_status_t dsu_job_build_root_for_install_root(const char *install_root,
                                                        char *out_root,
                                                        dsu_u32 out_root_cap);

/* Run a new job (writes journal + executes steps). */
DSU_API dsu_status_t dsu_job_run(dsu_ctx_t *ctx,
                                const dsu_job_input_t *input,
                                const char *job_root_override,
                                const dsu_job_options_t *opts,
                                dsu_job_run_result_t *out_result);

/* Resume an existing job by ID under job_root_override. */
DSU_API dsu_status_t dsu_job_resume(dsu_ctx_t *ctx,
                                   const char *job_root_override,
                                   dsu_u64 job_id,
                                   dsu_job_run_result_t *out_result);

/* Load job state without executing. */
DSU_API dsu_status_t dsu_job_state_load(dsu_ctx_t *ctx,
                                       const char *job_root_override,
                                       dsu_u64 job_id,
                                       core_job_state *out_state);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_JOB_H_INCLUDED */
