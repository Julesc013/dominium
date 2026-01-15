#include "dsk_jobs_internal.h"

#include "dsk/dsk_resume.h"
#include "dss/dss_txn.h"

#include <cstring>

static dsk_status_t dsk_jobs_error(dsk_u16 code, dsk_u16 subcode) {
    return dsk_error_make(DSK_DOMAIN_KERNEL, code, subcode, DSK_ERROR_FLAG_USER_ACTIONABLE);
}

static dsk_status_t dsk_jobs_from_dss(dss_error_t st) {
    return dss_error_is_ok(st) ? dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u)
                               : dss_to_dsk_error(st);
}

static void dsk_audit_add_event(dsk_audit_t *audit, dsk_u16 event_id, dsk_error_t err) {
    dsk_audit_event_t evt;
    if (!audit) {
        return;
    }
    evt.event_id = event_id;
    evt.error = err;
    audit->events.push_back(evt);
}

static std::string dsk_txn_path_from_journal(const char *journal_path) {
    if (!journal_path) {
        return std::string();
    }
    return std::string(journal_path) + ".txn.tlv";
}

static dsk_job_checkpoint_t *dsk_find_checkpoint(dsk_job_journal_t *journal, dsk_u32 job_id) {
    size_t i;
    if (!journal) {
        return 0;
    }
    for (i = 0u; i < journal->checkpoints.size(); ++i) {
        if (journal->checkpoints[i].job_id == job_id) {
            return &journal->checkpoints[i];
        }
    }
    return 0;
}

static dsk_status_t dsk_load_txn_journal(const dss_fs_api_t *fs,
                                         const std::string &path,
                                         dss_txn_journal_t *out_journal) {
    std::vector<dsk_u8> bytes;
    dss_error_t st;
    if (!fs || !fs->read_file_bytes || !out_journal) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    st = fs->read_file_bytes(fs->ctx, path.c_str(), &bytes);
    if (!dss_error_is_ok(st)) {
        return dsk_jobs_from_dss(st);
    }
    st = dss_txn_journal_parse(bytes.empty() ? 0 : &bytes[0],
                               (dss_u32)bytes.size(),
                               out_journal);
    return dsk_jobs_from_dss(st);
}

dsk_status_t dsk_rollback(const dsk_resume_request_t *req) {
    dsk_status_t st;
    dsk_plan_t plan;
    dsk_job_graph_t graph;
    dsk_job_journal_t journal;
    dsk_audit_t audit;
    dss_txn_journal_t txn;
    std::string txn_path;
    dsk_error_t ok = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    dsk_u32 commit_job_id = 0u;
    dsk_u32 last_step = 0u;
    size_t i;

    if (!req || !req->services || !req->journal_path || !req->out_audit_path) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }

    dsk_plan_clear(&plan);
    dsk_job_journal_clear(&journal);
    dsk_audit_clear(&audit);
    dss_txn_journal_clear(&txn);

    audit.result = ok;
    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_BEGIN, ok);
    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_ROLLBACK_BEGIN, ok);

    st = dsk_job_journal_load(&req->services->fs, req->journal_path, &journal);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_ROLLBACK_END, st);
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, st);
        dsk_write_audit_file(&req->services->fs, req->out_audit_path, &audit);
        return st;
    }
    if (journal.plan_bytes.empty()) {
        st = dsk_jobs_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_MISSING_FIELD);
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_ROLLBACK_END, st);
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, st);
        dsk_write_audit_file(&req->services->fs, req->out_audit_path, &audit);
        return st;
    }
    st = dsk_plan_parse(&journal.plan_bytes[0], (dsk_u32)journal.plan_bytes.size(), &plan);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_ROLLBACK_END, st);
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, st);
        dsk_write_audit_file(&req->services->fs, req->out_audit_path, &audit);
        return st;
    }
    st = dsk_plan_validate(&plan);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_ROLLBACK_END, st);
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, st);
        dsk_write_audit_file(&req->services->fs, req->out_audit_path, &audit);
        return st;
    }
    audit.manifest_digest64 = plan.manifest_digest64;
    audit.request_digest64 = plan.request_digest64;
    audit.splat_caps_digest64 = plan.selected_splat_caps_digest64;
    audit.resolved_set_digest64 = plan.resolved_set_digest64;
    audit.plan_digest64 = plan.plan_digest64;
    audit.selected_splat = plan.selected_splat_id;
    audit.operation = plan.operation;

    st = dsk_job_graph_build(plan, &graph);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_ROLLBACK_END, st);
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, st);
        dsk_write_audit_file(&req->services->fs, req->out_audit_path, &audit);
        return st;
    }
    for (i = 0u; i < graph.jobs.size(); ++i) {
        if (graph.jobs[i].kind == DSK_JOB_COMMIT) {
            commit_job_id = graph.jobs[i].job_id;
            break;
        }
    }
    if (commit_job_id != 0u) {
        dsk_job_checkpoint_t *cp = dsk_find_checkpoint(&journal, commit_job_id);
        if (cp) {
            last_step = cp->last_completed_step;
        }
    }

    audit.run_id = journal.run_id;
    audit.manifest_digest64 = plan.manifest_digest64;
    audit.request_digest64 = plan.request_digest64;
    audit.splat_caps_digest64 = plan.selected_splat_caps_digest64;
    audit.resolved_set_digest64 = plan.resolved_set_digest64;
    audit.plan_digest64 = plan.plan_digest64;
    audit.selected_splat = plan.selected_splat_id;
    audit.operation = plan.operation;

    txn_path = journal.rollback_ref.empty() ? dsk_txn_path_from_journal(req->journal_path)
                                            : journal.rollback_ref;
    st = dsk_load_txn_journal(&req->services->fs, txn_path, &txn);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_ROLLBACK_STEP_FAIL, st);
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_ROLLBACK_END, st);
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, st);
        dsk_write_audit_file(&req->services->fs, req->out_audit_path, &audit);
        return st;
    }

    {
        dss_error_t rb = dss_txn_rollback(&req->services->fs, &txn, last_step);
        if (!dss_error_is_ok(rb)) {
            st = dsk_jobs_from_dss(rb);
            audit.result = st;
            dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_ROLLBACK_STEP_FAIL, st);
        } else {
            dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_ROLLBACK_STEP_OK, ok);
        }
    }

    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_ROLLBACK_END, audit.result);
    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, audit.result);
    dsk_write_audit_file(&req->services->fs, req->out_audit_path, &audit);
    return audit.result;
}
