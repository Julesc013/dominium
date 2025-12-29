/*
FILE: include/dominium/core_job.h
MODULE: Dominium
PURPOSE: Resumable job model (POD structs + deterministic TLV serialization).
NOTES: Job types and message catalogs are append-only; never renumber.
*/
#ifndef DOMINIUM_CORE_JOB_H
#define DOMINIUM_CORE_JOB_H

#include "domino/abi.h"
#include "domino/core/types.h"
#include "dominium/core_err.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Limits (fixed; append-only if changed).
 *------------------------------------------------------------*/
#define CORE_JOB_MAX_STEPS 32u
#define CORE_JOB_MAX_DEPS  8u

enum {
    CORE_JOB_DEF_TLV_VERSION = 1u,
    CORE_JOB_STATE_TLV_VERSION = 1u
};

/*------------------------------------------------------------
 * Job types (stable; append-only).
 *------------------------------------------------------------*/
typedef enum core_job_type_e {
    CORE_JOB_TYPE_NONE = 0u,

    /* Launcher */
    CORE_JOB_TYPE_LAUNCHER_VERIFY_INSTANCE = 1u,
    CORE_JOB_TYPE_LAUNCHER_REPAIR_INSTANCE = 2u,
    CORE_JOB_TYPE_LAUNCHER_APPLY_PACKS = 3u,
    CORE_JOB_TYPE_LAUNCHER_EXPORT_INSTANCE = 4u,
    CORE_JOB_TYPE_LAUNCHER_IMPORT_INSTANCE = 5u,
    CORE_JOB_TYPE_LAUNCHER_DIAG_BUNDLE = 6u,
    CORE_JOB_TYPE_LAUNCHER_LAUNCH_PREPARE = 7u,

    /* Setup */
    CORE_JOB_TYPE_SETUP_INSTALL = 100u,
    CORE_JOB_TYPE_SETUP_UPGRADE = 101u,
    CORE_JOB_TYPE_SETUP_REPAIR = 102u,
    CORE_JOB_TYPE_SETUP_UNINSTALL = 103u,
    CORE_JOB_TYPE_SETUP_VERIFY = 104u
} core_job_type;

/*------------------------------------------------------------
 * Step flags (stable).
 *------------------------------------------------------------*/
typedef enum core_job_step_flags_e {
    CORE_JOB_STEP_NONE = 0u,
    CORE_JOB_STEP_IDEMPOTENT = 1u << 0u,
    CORE_JOB_STEP_RETRYABLE = 1u << 1u,
    CORE_JOB_STEP_REVERSIBLE = 1u << 2u,
    CORE_JOB_STEP_HAS_CHECKPOINT = 1u << 3u
} core_job_step_flags;

/*------------------------------------------------------------
 * Outcome (stable).
 *------------------------------------------------------------*/
typedef enum core_job_outcome_e {
    CORE_JOB_OUTCOME_NONE = 0u,
    CORE_JOB_OUTCOME_OK = 1u,
    CORE_JOB_OUTCOME_FAILED = 2u,
    CORE_JOB_OUTCOME_REFUSED = 3u,
    CORE_JOB_OUTCOME_CANCELLED = 4u,
    CORE_JOB_OUTCOME_PARTIAL = 5u
} core_job_outcome;

/*------------------------------------------------------------
 * Job model (POD).
 *------------------------------------------------------------*/
typedef struct core_job_step_t {
    u32 step_id;            /* stable within job def */
    u32 flags;              /* core_job_step_flags */
    u32 depends_on_count;
    u32 depends_on[CORE_JOB_MAX_DEPS];
} core_job_step;

typedef struct core_job_def_t {
    u32 schema_version;
    u32 job_type;           /* core_job_type */
    u32 step_count;
    core_job_step steps[CORE_JOB_MAX_STEPS];
} core_job_def;

typedef struct core_job_state_t {
    u64 job_id;
    u32 job_type;           /* core_job_type */
    u32 current_step;       /* step_id or 0 if idle */
    u32 completed_steps_bitset; /* bit per step index (0..CORE_JOB_MAX_STEPS-1) */
    u32 retry_count[CORE_JOB_MAX_STEPS];
    u32 outcome;            /* core_job_outcome */
    err_t last_error;       /* last failure/refusal */
} core_job_state;

/*------------------------------------------------------------
 * Helpers (C89 compatible; no allocation).
 *------------------------------------------------------------*/
void core_job_def_clear(core_job_def* def);
void core_job_state_clear(core_job_state* st);
void core_job_state_init(core_job_state* st, u64 job_id, u32 job_type, u32 step_count);

int core_job_def_validate(const core_job_def* def);
int core_job_def_find_step_index(const core_job_def* def, u32 step_id, u32* out_index);
int core_job_state_step_complete(const core_job_state* st, u32 step_index);
void core_job_state_mark_step_complete(core_job_state* st, u32 step_index);
int core_job_state_all_steps_complete(const core_job_def* def, const core_job_state* st);
int core_job_next_step_index(const core_job_def* def, const core_job_state* st, u32* out_step_index);

/*------------------------------------------------------------
 * TLV encoding (deterministic; canonical order).
 *------------------------------------------------------------*/
typedef dom_abi_result (*core_job_write_fn)(void* user, const void* data, u32 len);

typedef struct core_job_write_sink_t {
    void* user;
    core_job_write_fn write;
} core_job_write_sink;

dom_abi_result core_job_def_write_tlv(const core_job_def* def, const core_job_write_sink* sink);
dom_abi_result core_job_def_read_tlv(const unsigned char* data, u32 size, core_job_def* out_def);
dom_abi_result core_job_state_write_tlv(const core_job_state* st, const core_job_write_sink* sink);
dom_abi_result core_job_state_read_tlv(const unsigned char* data, u32 size, core_job_state* out_st);

u32 core_job_def_encoded_size(const core_job_def* def);
u32 core_job_state_encoded_size(const core_job_state* st);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_CORE_JOB_H */
