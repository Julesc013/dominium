#ifndef DSK_JOBS_H
#define DSK_JOBS_H

#include "dsk_error.h"
#include "dsk_tlv.h"
#include "dsk_types.h"

#ifdef __cplusplus
#include <string>
#include <vector>

/* Job kinds for apply/resume/rollback. */
#define DSK_JOB_STAGE 1u
#define DSK_JOB_VERIFY 2u
#define DSK_JOB_COMMIT 3u
#define DSK_JOB_REGISTER 4u
#define DSK_JOB_WRITE_STATE 5u
#define DSK_JOB_WRITE_AUDIT 6u
#define DSK_JOB_CLEANUP_STAGE 7u

/* Job status values recorded in the journal. */
#define DSK_JOB_STATUS_PENDING 1u
#define DSK_JOB_STATUS_IN_PROGRESS 2u
#define DSK_JOB_STATUS_COMPLETE 3u
#define DSK_JOB_STATUS_FAILED 4u
#define DSK_JOB_STATUS_SKIPPED 5u

struct dsk_job_checkpoint_t {
    dsk_u32 job_id;
    dsk_u16 status;
    dsk_u32 last_completed_step;
};

struct dsk_job_journal_t {
    dsk_u64 run_id;
    dsk_u64 plan_digest64;
    std::string selected_splat_id;
    std::string stage_root;
    std::string rollback_ref;
    dsk_error_t last_error;
    std::vector<dsk_u8> plan_bytes;
    std::vector<dsk_job_checkpoint_t> checkpoints;
};

DSK_API void dsk_job_journal_clear(dsk_job_journal_t *journal);
DSK_API dsk_status_t dsk_job_journal_parse(const dsk_u8 *data,
                                           dsk_u32 size,
                                           dsk_job_journal_t *out_journal);
DSK_API dsk_status_t dsk_job_journal_write(const dsk_job_journal_t *journal,
                                           dsk_tlv_buffer_t *out_buf);
#endif

#endif /* DSK_JOBS_H */
