#include "dsk_jobs_internal.h"

#include "dsk/dsk_resume.h"
#include "dsk/dsk_splat.h"
#include "dsk/dsk_contracts.h"
#include "dss/dss_txn.h"

#include <algorithm>
#include <cstdlib>
#include <cstring>

static bool dsk_file_op_less(const dsk_plan_file_op_t &a,
                             const dsk_plan_file_op_t &b) {
    if (a.target_root_id != b.target_root_id) return a.target_root_id < b.target_root_id;
    if (a.to_path != b.to_path) return a.to_path < b.to_path;
    if (a.from_path != b.from_path) return a.from_path < b.from_path;
    return a.op_kind < b.op_kind;
}

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

static void dsk_audit_capture_jobs(dsk_audit_t *audit,
                                   const dsk_job_graph_t &graph,
                                   const dsk_job_journal_t &journal) {
    size_t i;
    if (!audit) {
        return;
    }
    audit->jobs.clear();
    for (i = 0u; i < journal.checkpoints.size(); ++i) {
        dsk_audit_job_t job;
        size_t j;
        job.job_id = journal.checkpoints[i].job_id;
        job.job_status = journal.checkpoints[i].status;
        job.job_kind = 0u;
        for (j = 0u; j < graph.jobs.size(); ++j) {
            if (graph.jobs[j].job_id == job.job_id) {
                job.job_kind = graph.jobs[j].kind;
                break;
            }
        }
        audit->jobs.push_back(job);
    }
}

static bool dsk_failpoint_hit(const char *name) {
    const char *env = std::getenv("DSK_FAILPOINT");
    if (!env || !name) {
        return false;
    }
    return std::strcmp(env, name) == 0;
}

static bool dsk_failpoint_after_commit_step(dsk_u32 step_id) {
    const char *env = std::getenv("DSK_FAILPOINT");
    const char *prefix = "mid_commit_step_";
    size_t i = 0u;
    if (!env || !env[0]) {
        return false;
    }
    while (prefix[i]) {
        if (env[i] != prefix[i]) {
            return false;
        }
        ++i;
    }
    {
        const char *num = env + i;
        if (!num[0]) {
            return false;
        }
        dsk_u32 val = 0u;
        while (*num) {
            char c = *num++;
            if (c < '0' || c > '9') {
                return false;
            }
            val = (val * 10u) + (dsk_u32)(c - '0');
        }
        return (val == step_id) ? true : false;
    }
}

static std::string dsk_txn_path_from_journal(const char *journal_path) {
    if (!journal_path) {
        return std::string();
    }
    return std::string(journal_path) + ".txn.tlv";
}

static dsk_status_t dsk_build_installed_state_from_plan(const dsk_plan_t &plan,
                                                        const std::vector<std::string> &install_roots,
                                                        dsk_installed_state_t *out_state) {
    size_t i;
    if (!out_state) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    dsk_installed_state_clear(out_state);
    out_state->product_id = plan.product_id;
    out_state->installed_version = plan.product_version;
    out_state->selected_splat = plan.selected_splat_id;
    out_state->install_scope = plan.install_scope;
    if (!install_roots.empty()) {
        out_state->install_root = install_roots[0];
        out_state->install_roots = install_roots;
    }
    out_state->ownership = DSK_OWNERSHIP_ANY;
    for (i = 0u; i < plan.file_ops.size(); ++i) {
        if (plan.file_ops[i].ownership != 0u) {
            out_state->ownership = plan.file_ops[i].ownership;
            break;
        }
    }
    out_state->manifest_digest64 = plan.manifest_digest64;
    out_state->request_digest64 = plan.request_digest64;
    out_state->previous_state_digest64 = 0u;

    if (plan.operation == DSK_OPERATION_UNINSTALL) {
        return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    }
    for (i = 0u; i < plan.resolved_components.size(); ++i) {
        out_state->installed_components.push_back(plan.resolved_components[i].component_id);
    }
    for (i = 0u; i < plan.file_ops.size(); ++i) {
        const dsk_plan_file_op_t &op = plan.file_ops[i];
        if (op.op_kind != DSK_PLAN_FILE_OP_COPY) {
            continue;
        }
        dsk_state_artifact_t art;
        art.target_root_id = op.target_root_id;
        art.path = op.to_path;
        art.digest64 = op.digest64;
        art.size = op.size;
        out_state->artifacts.push_back(art);
    }
    for (i = 0u; i < plan.registrations.shortcuts.size(); ++i) {
        dsk_state_registration_t reg;
        reg.kind = DSK_REG_KIND_SHORTCUT;
        reg.status = DSK_REG_STATUS_SKIPPED;
        reg.value = plan.registrations.shortcuts[i];
        out_state->registrations.push_back(reg);
    }
    for (i = 0u; i < plan.registrations.file_associations.size(); ++i) {
        dsk_state_registration_t reg;
        reg.kind = DSK_REG_KIND_FILE_ASSOC;
        reg.status = DSK_REG_STATUS_SKIPPED;
        reg.value = plan.registrations.file_associations[i];
        out_state->registrations.push_back(reg);
    }
    for (i = 0u; i < plan.registrations.url_handlers.size(); ++i) {
        dsk_state_registration_t reg;
        reg.kind = DSK_REG_KIND_URL_HANDLER;
        reg.status = DSK_REG_STATUS_SKIPPED;
        reg.value = plan.registrations.url_handlers[i];
        out_state->registrations.push_back(reg);
    }
    out_state->manifest_digest64 = plan.manifest_digest64;
    out_state->request_digest64 = plan.request_digest64;
    out_state->previous_state_digest64 = 0u;
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
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

void dsk_apply_request_init(dsk_apply_request_t *req) {
    if (!req) {
        return;
    }
    req->services = 0;
    req->plan_bytes = 0;
    req->plan_size = 0u;
    req->out_state_path = 0;
    req->out_audit_path = 0;
    req->out_journal_path = 0;
    req->dry_run = 0u;
}

dsk_status_t dsk_apply_plan(const dsk_apply_request_t *req) {
    dsk_status_t st;
    dsk_plan_t plan;
    dsk_job_graph_t graph;
    dsk_job_journal_t journal;
    dsk_audit_t audit;
    std::vector<std::string> install_roots;
    std::vector<dsk_plan_file_op_t> ops;
    dsk_splat_candidate_t candidate;
    std::string stage_root;
    dsk_error_t ok = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    size_t i;

    if (!req || !req->services || !req->plan_bytes || !req->out_audit_path || !req->out_journal_path) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (!req->dry_run && !req->out_state_path) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }

    dsk_plan_clear(&plan);
    dsk_job_journal_clear(&journal);
    dsk_audit_clear(&audit);

    audit.result = ok;
    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_BEGIN, ok);
    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_APPLY_BEGIN, ok);

    st = dsk_plan_parse(req->plan_bytes, req->plan_size, &plan);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, st);
        dsk_write_audit_file(&req->services->fs, req->out_audit_path, &audit);
        return st;
    }
    st = dsk_plan_validate(&plan);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
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

    if (!dsk_splat_registry_find(plan.selected_splat_id, &candidate)) {
        st = dsk_jobs_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_SPLAT_NOT_FOUND);
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, st);
        dsk_write_audit_file(&req->services->fs, req->out_audit_path, &audit);
        return st;
    }
    if (candidate.caps_digest64 != plan.selected_splat_caps_digest64) {
        st = dsk_jobs_error(DSK_CODE_INTEGRITY_ERROR, DSK_SUBCODE_INVALID_FIELD);
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, st);
        dsk_write_audit_file(&req->services->fs, req->out_audit_path, &audit);
        return st;
    }

    st = dsk_resolve_install_roots(plan, req->services, &install_roots);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, st);
        dsk_write_audit_file(&req->services->fs, req->out_audit_path, &audit);
        return st;
    }
    st = dsk_stage_root_path(&req->services->fs, plan.plan_digest64, &stage_root);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, st);
        dsk_write_audit_file(&req->services->fs, req->out_audit_path, &audit);
        return st;
    }

    ops = plan.file_ops;
    std::sort(ops.begin(), ops.end(), dsk_file_op_less);

    st = dsk_job_graph_build(plan, &graph);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, st);
        dsk_write_audit_file(&req->services->fs, req->out_audit_path, &audit);
        return st;
    }

    journal.run_id = 0u;
    journal.plan_digest64 = plan.plan_digest64;
    journal.selected_splat_id = plan.selected_splat_id;
    journal.stage_root = stage_root;
    journal.rollback_ref = dsk_txn_path_from_journal(req->out_journal_path);
    journal.last_error = ok;
    journal.plan_bytes.assign(req->plan_bytes, req->plan_bytes + req->plan_size);
    for (i = 0u; i < graph.jobs.size(); ++i) {
        dsk_job_checkpoint_t cp;
        cp.job_id = graph.jobs[i].job_id;
        cp.status = req->dry_run ? DSK_JOB_STATUS_SKIPPED : DSK_JOB_STATUS_PENDING;
        cp.last_completed_step = 0u;
        journal.checkpoints.push_back(cp);
    }

    st = dsk_job_journal_store(&req->services->fs, req->out_journal_path, &journal);
    if (!dsk_error_is_ok(st)) {
        return st;
    }

    audit.run_id = journal.run_id;
    audit.manifest_digest64 = plan.manifest_digest64;
    audit.request_digest64 = plan.request_digest64;
    audit.splat_caps_digest64 = plan.selected_splat_caps_digest64;
    audit.resolved_set_digest64 = plan.resolved_set_digest64;
    audit.plan_digest64 = plan.plan_digest64;
    audit.selected_splat = plan.selected_splat_id;
    audit.operation = plan.operation;
    if (req->dry_run) {
        dss_txn_journal_t txn;
        dss_txn_journal_clear(&txn);
        dss_error_t txst = dss_txn_build(&plan,
                                         install_roots,
                                         stage_root,
                                         candidate.caps.supports_atomic_swap,
                                         &txn);
        if (!dss_error_is_ok(txst)) {
            audit.result = dss_to_dsk_error(txst);
            dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_COMMIT_FAIL, audit.result);
            dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, audit.result);
            dsk_write_audit_file(&req->services->fs, req->out_audit_path, &audit);
            return audit.result;
        }
        {
            dsk_tlv_buffer_t buf;
            dss_error_t wr;
            dss_txn_journal_write(&txn, &buf);
            wr = req->services->fs.write_file_bytes_atomic(req->services->fs.ctx,
                                                           journal.rollback_ref.c_str(),
                                                           buf.data,
                                                           buf.size);
            dsk_tlv_buffer_free(&buf);
            if (!dss_error_is_ok(wr)) {
                audit.result = dss_to_dsk_error(wr);
            }
        }
        dsk_audit_capture_jobs(&audit, graph, journal);
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, audit.result);
        dsk_write_audit_file(&req->services->fs, req->out_audit_path, &audit);
        return audit.result;
    }

    for (i = 0u; i < graph.jobs.size(); ++i) {
        const dsk_job_node_t &job = graph.jobs[i];
        dsk_job_checkpoint_t *cp = dsk_find_checkpoint(&journal, job.job_id);
        if (!cp) {
            journal.checkpoints.push_back(dsk_job_checkpoint_t());
            cp = &journal.checkpoints.back();
            cp->job_id = job.job_id;
            cp->status = DSK_JOB_STATUS_PENDING;
            cp->last_completed_step = 0u;
        }
        if (cp->status == DSK_JOB_STATUS_COMPLETE || cp->status == DSK_JOB_STATUS_SKIPPED) {
            continue;
        }
        cp->status = DSK_JOB_STATUS_IN_PROGRESS;
        st = dsk_job_journal_store(&req->services->fs, req->out_journal_path, &journal);
        if (!dsk_error_is_ok(st)) {
            return st;
        }

        if (job.kind == DSK_JOB_STAGE) {
            st = dsk_stage_file_op(ops[job.file_op_index], plan, stage_root, req->services);
            if (!dsk_error_is_ok(st)) {
                journal.last_error = st;
                cp->status = DSK_JOB_STATUS_FAILED;
                dsk_job_journal_store(&req->services->fs, req->out_journal_path, &journal);
                audit.result = st;
                dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_STAGE_FAIL, st);
                break;
            }
            if (dsk_failpoint_hit("after_stage_extract")) {
                st = dsk_jobs_error(DSK_CODE_INTERNAL_ERROR, DSK_SUBCODE_NONE);
                journal.last_error = st;
                cp->status = DSK_JOB_STATUS_FAILED;
                dsk_job_journal_store(&req->services->fs, req->out_journal_path, &journal);
                audit.result = st;
                dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_STAGE_FAIL, st);
                break;
            }
            cp->status = DSK_JOB_STATUS_COMPLETE;
            cp->last_completed_step = 1u;
            dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_STAGE_OK, ok);
        } else if (job.kind == DSK_JOB_VERIFY) {
            st = dsk_verify_file_op(ops[job.file_op_index], stage_root, req->services);
            if (!dsk_error_is_ok(st)) {
                journal.last_error = st;
                cp->status = DSK_JOB_STATUS_FAILED;
                dsk_job_journal_store(&req->services->fs, req->out_journal_path, &journal);
                audit.result = st;
                dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_VERIFY_FAIL, st);
                break;
            }
            if (dsk_failpoint_hit("after_verify")) {
                st = dsk_jobs_error(DSK_CODE_INTERNAL_ERROR, DSK_SUBCODE_NONE);
                journal.last_error = st;
                cp->status = DSK_JOB_STATUS_FAILED;
                dsk_job_journal_store(&req->services->fs, req->out_journal_path, &journal);
                audit.result = st;
                dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_VERIFY_FAIL, st);
                break;
            }
            cp->status = DSK_JOB_STATUS_COMPLETE;
            cp->last_completed_step = 1u;
            dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_VERIFY_OK, ok);
        } else if (job.kind == DSK_JOB_COMMIT) {
            dss_txn_journal_t txn;
            dss_txn_journal_clear(&txn);
            dss_error_t txst = dss_txn_build(&plan,
                                             install_roots,
                                             stage_root,
                                             candidate.caps.supports_atomic_swap,
                                             &txn);
            if (!dss_error_is_ok(txst)) {
                st = dsk_jobs_from_dss(txst);
                journal.last_error = st;
                cp->status = DSK_JOB_STATUS_FAILED;
                dsk_job_journal_store(&req->services->fs, req->out_journal_path, &journal);
                audit.result = st;
                dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_COMMIT_FAIL, st);
                break;
            }
            {
                dsk_tlv_buffer_t buf;
                dss_error_t wr;
                dss_txn_journal_write(&txn, &buf);
                wr = req->services->fs.write_file_bytes_atomic(req->services->fs.ctx,
                                                               journal.rollback_ref.c_str(),
                                                               buf.data,
                                                               buf.size);
                dsk_tlv_buffer_free(&buf);
                if (!dss_error_is_ok(wr)) {
                    st = dsk_jobs_from_dss(wr);
                    journal.last_error = st;
                    cp->status = DSK_JOB_STATUS_FAILED;
                    dsk_job_journal_store(&req->services->fs, req->out_journal_path, &journal);
                    audit.result = st;
                    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_COMMIT_FAIL, st);
                    break;
                }
            }

            cp->last_completed_step = 0u;
            for (size_t step_index = 0u; step_index < txn.steps.size(); ++step_index) {
                const dss_txn_step_t &step = txn.steps[step_index];
                dss_error_t run = dss_txn_execute_step(&req->services->fs, &req->services->archive, &step);
                if (!dss_error_is_ok(run)) {
                    st = dsk_jobs_from_dss(run);
                    journal.last_error = st;
                    cp->status = DSK_JOB_STATUS_FAILED;
                    if (dsk_failpoint_after_commit_step(step.step_id)) {
                        cp->last_completed_step = step.step_id;
                    } else {
                        cp->last_completed_step = step.step_id - 1u;
                    }
                    dsk_job_journal_store(&req->services->fs, req->out_journal_path, &journal);
                    audit.result = st;
                    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_COMMIT_FAIL, st);
                    break;
                }
                cp->last_completed_step = step.step_id;
                dsk_job_journal_store(&req->services->fs, req->out_journal_path, &journal);
            }
            if (cp->status == DSK_JOB_STATUS_FAILED) {
                break;
            }
            cp->status = DSK_JOB_STATUS_COMPLETE;
            dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_COMMIT_OK, ok);
        } else if (job.kind == DSK_JOB_REGISTER) {
            cp->status = DSK_JOB_STATUS_COMPLETE;
            dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_REGISTER_OK, ok);
        } else if (job.kind == DSK_JOB_WRITE_STATE) {
            if (dsk_failpoint_hit("before_write_state")) {
                st = dsk_jobs_error(DSK_CODE_INTERNAL_ERROR, DSK_SUBCODE_NONE);
                journal.last_error = st;
                cp->status = DSK_JOB_STATUS_FAILED;
                dsk_job_journal_store(&req->services->fs, req->out_journal_path, &journal);
                audit.result = st;
                dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_WRITE_STATE_FAIL, st);
                break;
            }
            dsk_installed_state_t state;
            dsk_tlv_buffer_t buf;
            dsk_build_installed_state_from_plan(plan, install_roots, &state);
            st = dsk_installed_state_write(&state, &buf);
            if (!dsk_error_is_ok(st)) {
                journal.last_error = st;
                cp->status = DSK_JOB_STATUS_FAILED;
                dsk_job_journal_store(&req->services->fs, req->out_journal_path, &journal);
                audit.result = st;
                dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_WRITE_STATE_FAIL, st);
                break;
            }
            {
                dss_error_t wr = req->services->fs.write_file_bytes_atomic(req->services->fs.ctx,
                                                                           req->out_state_path,
                                                                           buf.data,
                                                                           buf.size);
                dsk_tlv_buffer_free(&buf);
                if (!dss_error_is_ok(wr)) {
                    st = dsk_jobs_from_dss(wr);
                    journal.last_error = st;
                    cp->status = DSK_JOB_STATUS_FAILED;
                    dsk_job_journal_store(&req->services->fs, req->out_journal_path, &journal);
                    audit.result = st;
                    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_WRITE_STATE_FAIL, st);
                    break;
                }
            }
            cp->status = DSK_JOB_STATUS_COMPLETE;
            dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_WRITE_STATE_OK, ok);
        } else if (job.kind == DSK_JOB_WRITE_AUDIT) {
            cp->status = DSK_JOB_STATUS_COMPLETE;
            dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_WRITE_AUDIT_OK, ok);
        } else if (job.kind == DSK_JOB_CLEANUP_STAGE) {
            if (req->services->fs.remove_dir_if_empty) {
                req->services->fs.remove_dir_if_empty(req->services->fs.ctx, stage_root.c_str());
            }
            cp->status = DSK_JOB_STATUS_COMPLETE;
        }

        dsk_job_journal_store(&req->services->fs, req->out_journal_path, &journal);
    }

    dsk_audit_capture_jobs(&audit, graph, journal);
    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, audit.result);
    dsk_write_audit_file(&req->services->fs, req->out_audit_path, &audit);
    return audit.result;
}
