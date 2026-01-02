#include "dsk_jobs_internal.h"

#include <algorithm>

static bool dsk_file_op_less(const dsk_plan_file_op_t &a,
                             const dsk_plan_file_op_t &b) {
    if (a.target_root_id != b.target_root_id) {
        return a.target_root_id < b.target_root_id;
    }
    if (a.to_path != b.to_path) {
        return a.to_path < b.to_path;
    }
    if (a.from_path != b.from_path) {
        return a.from_path < b.from_path;
    }
    return a.op_kind < b.op_kind;
}

dsk_status_t dsk_job_graph_build(const dsk_plan_t &plan, dsk_job_graph_t *out_graph) {
    std::vector<dsk_plan_file_op_t> ops = plan.file_ops;
    dsk_u32 job_id = 0u;
    size_t i;
    if (!out_graph) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    out_graph->jobs.clear();
    std::sort(ops.begin(), ops.end(), dsk_file_op_less);

    for (i = 0u; i < ops.size(); ++i) {
        dsk_job_node_t stage_job;
        stage_job.job_id = ++job_id;
        stage_job.kind = DSK_JOB_STAGE;
        stage_job.file_op_index = (dsk_u32)i;
        out_graph->jobs.push_back(stage_job);

        dsk_job_node_t verify_job;
        verify_job.job_id = ++job_id;
        verify_job.kind = DSK_JOB_VERIFY;
        verify_job.file_op_index = (dsk_u32)i;
        out_graph->jobs.push_back(verify_job);
    }

    {
        dsk_job_node_t job;
        job.job_id = ++job_id;
        job.kind = DSK_JOB_COMMIT;
        job.file_op_index = 0u;
        out_graph->jobs.push_back(job);
    }
    {
        dsk_job_node_t job;
        job.job_id = ++job_id;
        job.kind = DSK_JOB_REGISTER;
        job.file_op_index = 0u;
        out_graph->jobs.push_back(job);
    }
    {
        dsk_job_node_t job;
        job.job_id = ++job_id;
        job.kind = DSK_JOB_WRITE_STATE;
        job.file_op_index = 0u;
        out_graph->jobs.push_back(job);
    }
    {
        dsk_job_node_t job;
        job.job_id = ++job_id;
        job.kind = DSK_JOB_WRITE_AUDIT;
        job.file_op_index = 0u;
        out_graph->jobs.push_back(job);
    }
    {
        dsk_job_node_t job;
        job.job_id = ++job_id;
        job.kind = DSK_JOB_CLEANUP_STAGE;
        job.file_op_index = 0u;
        out_graph->jobs.push_back(job);
    }

    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}
