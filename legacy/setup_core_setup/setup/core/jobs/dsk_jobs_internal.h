#ifndef DSK_JOBS_INTERNAL_H
#define DSK_JOBS_INTERNAL_H

#include "dsk/dsk_audit.h"
#include "dsk/dsk_jobs.h"
#include "dsk/dsk_plan.h"
#include "dss/dss_services.h"

#include <string>
#include <vector>

struct dsk_job_node_t {
    dsk_u32 job_id;
    dsk_u16 kind;
    dsk_u32 file_op_index;
};

struct dsk_job_graph_t {
    std::vector<dsk_job_node_t> jobs;
};

dsk_status_t dsk_job_graph_build(const dsk_plan_t &plan, dsk_job_graph_t *out_graph);

dsk_status_t dsk_job_journal_load(const dss_fs_api_t *fs,
                                  const char *path,
                                  dsk_job_journal_t *out_journal);
dsk_status_t dsk_job_journal_store(const dss_fs_api_t *fs,
                                   const char *path,
                                   const dsk_job_journal_t *journal);

dsk_status_t dsk_write_audit_file(const dss_fs_api_t *fs,
                                  const char *path,
                                  const dsk_audit_t *audit);

dsk_status_t dsk_resolve_install_roots(const dsk_plan_t &plan,
                                       const dss_services_t *services,
                                       std::vector<std::string> *out_roots);
dsk_status_t dsk_stage_root_path(const dss_fs_api_t *fs,
                                 dsk_u64 plan_digest64,
                                 std::string *out_stage_root);
dsk_status_t dsk_stage_file_op(const dsk_plan_file_op_t &op,
                               const dsk_plan_t &plan,
                               const std::string &stage_root,
                               const dss_services_t *services);
dsk_status_t dsk_verify_file_op(const dsk_plan_file_op_t &op,
                                const std::string &stage_root,
                                const dss_services_t *services);

#endif /* DSK_JOBS_INTERNAL_H */
