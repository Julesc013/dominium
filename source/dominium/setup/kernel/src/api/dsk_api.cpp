#include "dsk/dsk_api.h"
#include "dsk/dsk_audit.h"
#include "dsk/dsk_contracts.h"
#include "dsk/dsk_digest.h"
#include "dsk/dsk_plan.h"
#include "dsk/dsk_splat.h"
#include "dsk_resolve.h"
#include "dss/dss_services.h"

#include "dominium/core_err.h"
#include "dominium/core_log.h"

#include <algorithm>
#include <ctime>
#include <cstdlib>

static u32 dsk_error_flags_to_err_flags(dsk_error_t st) {
    u32 flags = 0u;
    if ((st.flags & DSK_ERROR_FLAG_RETRYABLE) != 0u) {
        flags |= (u32)ERRF_RETRYABLE;
    }
    if ((st.flags & DSK_ERROR_FLAG_USER_ACTIONABLE) != 0u) {
        flags |= (u32)ERRF_USER_ACTIONABLE;
    }
    if ((st.flags & DSK_ERROR_FLAG_FATAL) != 0u) {
        flags |= (u32)ERRF_FATAL;
    }
    if (st.code == DSK_CODE_INTEGRITY_ERROR) {
        flags |= (u32)ERRF_INTEGRITY;
    }
    if (st.code == DSK_CODE_UNSUPPORTED_VERSION || st.code == DSK_CODE_UNSUPPORTED_PLATFORM) {
        flags |= (u32)ERRF_NOT_SUPPORTED;
    }
    return flags;
}

static err_t dsk_error_to_err_t(dsk_error_t st, u32 op_id) {
    u16 domain = (u16)ERRD_SETUP;
    u16 code = (u16)ERRC_SETUP_PLAN_FAILED;
    u32 msg_id = (u32)ERRMSG_SETUP_PLAN_FAILED;
    u32 flags;

    if (dsk_error_is_ok(st)) {
        return err_ok();
    }

    if (st.code == DSK_CODE_INVALID_ARGS) {
        return err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
    }
    if (st.code == DSK_CODE_INTERNAL_ERROR) {
        return err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INTERNAL, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_INTERNAL);
    }
    if (st.code == DSK_CODE_UNSUPPORTED_PLATFORM) {
        return err_make((u16)ERRD_SETUP, (u16)ERRC_SETUP_UNSUPPORTED_PLATFORM, (u32)ERRF_NOT_SUPPORTED,
                        (u32)ERRMSG_SETUP_UNSUPPORTED_PLATFORM);
    }

    switch (op_id) {
    case CORE_LOG_OP_SETUP_PARSE_MANIFEST:
        code = (u16)ERRC_SETUP_INVALID_MANIFEST;
        msg_id = (u32)ERRMSG_SETUP_INVALID_MANIFEST;
        break;
    case CORE_LOG_OP_SETUP_PARSE_REQUEST:
        code = (u16)ERRC_SETUP_PLAN_FAILED;
        msg_id = (u32)ERRMSG_SETUP_PLAN_FAILED;
        break;
    case CORE_LOG_OP_SETUP_SPLAT_SELECT:
        code = (u16)ERRC_SETUP_RESOLVE_FAILED;
        msg_id = (u32)ERRMSG_SETUP_RESOLVE_FAILED;
        break;
    case CORE_LOG_OP_SETUP_WRITE_STATE:
        code = (u16)ERRC_SETUP_APPLY_FAILED;
        msg_id = (u32)ERRMSG_SETUP_APPLY_FAILED;
        break;
    default:
        code = (u16)ERRC_SETUP_PLAN_FAILED;
        msg_id = (u32)ERRMSG_SETUP_PLAN_FAILED;
        break;
    }

    flags = dsk_error_flags_to_err_flags(st);
    return err_make(domain, code, flags, msg_id);
}

static dom_abi_result dsk_log_sink_write(void *user, const void *data, u32 len) {
    const dsk_byte_sink_t *sink = (const dsk_byte_sink_t *)user;
    dsk_status_t st;
    if (!sink || !sink->write) {
        return (dom_abi_result)-1;
    }
    st = sink->write(sink->user, (const dsk_u8 *)data, len);
    return dsk_error_is_ok(st) ? 0 : (dom_abi_result)-1;
}

static void dsk_log_add_err_fields(core_log_event *ev, const err_t *err) {
    if (!ev || !err) {
        return;
    }
    (void)core_log_event_add_u32(ev, CORE_LOG_KEY_ERR_DOMAIN, (u32)err->domain);
    (void)core_log_event_add_u32(ev, CORE_LOG_KEY_ERR_CODE, (u32)err->code);
    (void)core_log_event_add_u32(ev, CORE_LOG_KEY_ERR_FLAGS, (u32)err->flags);
    (void)core_log_event_add_u32(ev, CORE_LOG_KEY_ERR_MSG_ID, (u32)err->msg_id);
}

static void dsk_emit_log_event(const dsk_kernel_request_ex_t *req,
                               u64 run_id,
                               u32 op_id,
                               u32 event_code,
                               dsk_error_t st) {
    core_log_event ev;
    core_log_write_sink sink;
    err_t err;

    if (!req || !req->out_log.write) {
        return;
    }

    err = dsk_error_to_err_t(st, op_id);

    core_log_event_clear(&ev);
    ev.domain = CORE_LOG_DOMAIN_SETUP;
    ev.code = (u16)event_code;
    ev.severity = (u8)((event_code == CORE_LOG_EVT_OP_FAIL) ? CORE_LOG_SEV_ERROR : CORE_LOG_SEV_INFO);
    ev.msg_id = err_is_ok(&err) ? 0u : err.msg_id;
    ev.t_mono = 0u;
    (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_OPERATION_ID, op_id);
    (void)core_log_event_add_u64(&ev, CORE_LOG_KEY_RUN_ID, run_id);
    if (!err_is_ok(&err)) {
        dsk_log_add_err_fields(&ev, &err);
        (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_STATUS_CODE, (u32)st.code);
    }

    sink.user = (void *)&req->out_log;
    sink.write = dsk_log_sink_write;
    (void)core_log_event_write_tlv(&ev, &sink);
}

static dsk_u64 dsk_generate_run_id(dsk_u8 deterministic_mode) {
    if (deterministic_mode) {
        return 0u;
    }
    static int seeded = 0;
    if (!seeded) {
        seeded = 1;
        std::srand((unsigned int)std::time(0));
    }
    {
        dsk_u64 a = (dsk_u64)(std::rand() & 0xFFFF);
        dsk_u64 b = (dsk_u64)(std::rand() & 0xFFFF);
        dsk_u64 c = (dsk_u64)(std::rand() & 0xFFFF);
        dsk_u64 d = (dsk_u64)(std::rand() & 0xFFFF);
        return (a << 48) | (b << 32) | (c << 16) | d;
    }
}

static void dsk_audit_add_event(dsk_audit_t *audit, dsk_u16 event_id, dsk_error_t err) {
    dsk_audit_event_t evt;
    evt.event_id = event_id;
    evt.error = err;
    audit->events.push_back(evt);
}

static void dsk_audit_capture_selection(dsk_audit_t *audit,
                                        const dsk_splat_selection_t &selection) {
    size_t i;
    if (!audit) {
        return;
    }
    audit->splat_caps_digest64 = 0u;
    audit->selection.candidates.clear();
    for (i = 0u; i < selection.candidates.size(); ++i) {
        dsk_audit_selection_candidate_t cand;
        cand.id = selection.candidates[i].id;
        cand.caps_digest64 = selection.candidates[i].caps_digest64;
        audit->selection.candidates.push_back(cand);
        if (selection.candidates[i].id == selection.selected_id) {
            audit->splat_caps_digest64 = selection.candidates[i].caps_digest64;
        }
    }
    audit->selection.rejections = selection.rejections;
    audit->selection.selected_id = selection.selected_id;
    audit->selection.selected_reason = selection.selected_reason;
    audit->selected_splat = selection.selected_id;
}

static void dsk_audit_capture_refusals(dsk_audit_t *audit,
                                       const std::vector<dsk_plan_refusal_t> &refusals) {
    size_t i;
    if (!audit) {
        return;
    }
    audit->refusals.clear();
    for (i = 0u; i < refusals.size(); ++i) {
        dsk_audit_refusal_t ref;
        ref.code = refusals[i].code;
        ref.detail = refusals[i].detail;
        audit->refusals.push_back(ref);
    }
}

static dsk_u16 dsk_select_ownership(const dsk_request_t &request,
                                    const dsk_splat_caps_t &caps) {
    if (request.ownership_preference != DSK_OWNERSHIP_ANY) {
        return request.ownership_preference;
    }
    if (caps.supports_pkg_ownership) {
        return DSK_OWNERSHIP_PKG;
    }
    if (caps.supports_portable_ownership) {
        return DSK_OWNERSHIP_PORTABLE;
    }
    return DSK_OWNERSHIP_ANY;
}

static dsk_status_t dsk_sink_write(const dsk_byte_sink_t *sink, const dsk_tlv_buffer_t *buf) {
    if (!sink || !sink->write || !buf) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    return sink->write(sink->user, buf->data, buf->size);
}

static dsk_status_t dsk_build_installed_state(const dsk_manifest_t &manifest,
                                              const dsk_plan_t &plan,
                                              const std::string &selected_splat,
                                              dsk_u16 ownership,
                                              dsk_u64 manifest_digest,
                                              dsk_u64 request_digest,
                                              const dsk_resolved_set_t &resolved,
                                              dsk_installed_state_t *out_state) {
    if (!out_state) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    dsk_installed_state_clear(out_state);
    out_state->product_id = manifest.product_id;
    out_state->installed_version = manifest.version;
    out_state->selected_splat = selected_splat;
    out_state->install_scope = plan.install_scope;
    out_state->install_root = plan.install_roots.empty() ? std::string() : plan.install_roots[0];
    out_state->install_roots = plan.install_roots;
    out_state->ownership = ownership;
    out_state->manifest_digest64 = manifest_digest;
    out_state->request_digest64 = request_digest;
    {
        size_t i;
        for (i = 0u; i < resolved.components.size(); ++i) {
            out_state->installed_components.push_back(resolved.components[i].component_id);
        }
    }
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

void dsk_kernel_request_init(dsk_kernel_request_t *req) {
    if (!req) {
        return;
    }
    req->services = 0;
    req->manifest_bytes = 0;
    req->manifest_size = 0u;
    req->request_bytes = 0;
    req->request_size = 0u;
    req->out_plan.user = 0;
    req->out_plan.write = 0;
    req->out_state.user = 0;
    req->out_state.write = 0;
    req->out_audit.user = 0;
    req->out_audit.write = 0;
    req->deterministic_mode = 1u;
}

void dsk_kernel_request_ex_init(dsk_kernel_request_ex_t *req) {
    if (!req) {
        return;
    }
    dsk_kernel_request_init(&req->base);
    req->out_log.user = 0;
    req->out_log.write = 0;
}

static dsk_status_t dsk_kernel_run(dsk_u16 expected_operation, const dsk_kernel_request_ex_t *req_ex) {
    dsk_status_t st;
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_installed_state_t state;
    dsk_plan_t plan;
    dsk_resolved_set_t resolved;
    std::vector<dsk_plan_refusal_t> refusals;
    dsk_splat_selection_t splat_sel;
    dsk_splat_caps_t selected_caps;
    dsk_audit_t audit;
    dsk_tlv_buffer_t plan_buf;
    dsk_tlv_buffer_t state_buf;
    dsk_tlv_buffer_t audit_buf;
    dsk_u64 manifest_digest;
    dsk_u64 request_digest;
    dsk_error_t ok = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    const dsk_kernel_request_t *req = req_ex ? &req_ex->base : 0;

    if (!req || !req->manifest_bytes || !req->request_bytes ||
        !req->out_audit.write || !req->out_state.write) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }

    dsk_manifest_clear(&manifest);
    dsk_request_clear(&request);
    dsk_installed_state_clear(&state);
    dsk_plan_clear(&plan);
    resolved.components.clear();
    resolved.digest64 = 0u;
    refusals.clear();
    dsk_audit_clear(&audit);
    dsk_splat_caps_clear(&selected_caps);

    manifest_digest = dsk_digest64_bytes(req->manifest_bytes, req->manifest_size);
    request_digest = dsk_digest64_bytes(req->request_bytes, req->request_size);

    audit.run_id = dsk_generate_run_id(req->deterministic_mode);
    audit.manifest_digest64 = manifest_digest;
    audit.request_digest64 = request_digest;
    audit.splat_caps_digest64 = 0u;
    audit.resolved_set_digest64 = 0u;
    audit.plan_digest64 = 0u;
    audit.operation = expected_operation;
    audit.result = ok;

    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_BEGIN, ok);

    st = dsk_manifest_parse(req->manifest_bytes, req->manifest_size, &manifest);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_PARSE_MANIFEST_FAIL, st);
        dsk_emit_log_event(req_ex, audit.run_id, CORE_LOG_OP_SETUP_PARSE_MANIFEST, CORE_LOG_EVT_OP_FAIL, st);
        goto emit_audit;
    }
    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_PARSE_MANIFEST_OK, ok);
    dsk_emit_log_event(req_ex, audit.run_id, CORE_LOG_OP_SETUP_PARSE_MANIFEST, CORE_LOG_EVT_OP_OK, ok);

    st = dsk_request_parse(req->request_bytes, req->request_size, &request);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_PARSE_REQUEST_FAIL, st);
        dsk_emit_log_event(req_ex, audit.run_id, CORE_LOG_OP_SETUP_PARSE_REQUEST, CORE_LOG_EVT_OP_FAIL, st);
        goto emit_audit;
    }

    if (req->services && req->services->platform.get_platform_triple) {
        std::string platform_override;
        dss_error_t pst = req->services->platform.get_platform_triple(
            req->services->platform.ctx,
            &platform_override);
        if (dss_error_is_ok(pst) && !platform_override.empty()) {
            request.target_platform_triple = platform_override;
        }
    }

    if (request.operation != expected_operation) {
        st = dsk_error_make(DSK_DOMAIN_KERNEL,
                            DSK_CODE_VALIDATION_ERROR,
                            DSK_SUBCODE_REQUEST_MISMATCH,
                            DSK_ERROR_FLAG_USER_ACTIONABLE);
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_PARSE_REQUEST_FAIL, st);
        dsk_emit_log_event(req_ex, audit.run_id, CORE_LOG_OP_SETUP_PARSE_REQUEST, CORE_LOG_EVT_OP_FAIL, st);
        goto emit_audit;
    }
    audit.operation = request.operation;
    audit.frontend_id = request.frontend_id;
    audit.platform_triple = request.target_platform_triple;
    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_PARSE_REQUEST_OK, ok);
    dsk_emit_log_event(req_ex, audit.run_id, CORE_LOG_OP_SETUP_PARSE_REQUEST, CORE_LOG_EVT_OP_OK, ok);

    st = dsk_splat_select(manifest, request, &splat_sel);
    dsk_audit_capture_selection(&audit, splat_sel);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_SPLAT_SELECT_FAIL, st);
        dsk_emit_log_event(req_ex, audit.run_id, CORE_LOG_OP_SETUP_SPLAT_SELECT, CORE_LOG_EVT_OP_FAIL, st);
        goto emit_audit;
    }

    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_SPLAT_SELECT_OK, ok);
    dsk_emit_log_event(req_ex, audit.run_id, CORE_LOG_OP_SETUP_SPLAT_SELECT, CORE_LOG_EVT_OP_OK, ok);

    {
        size_t i;
        for (i = 0u; i < splat_sel.candidates.size(); ++i) {
            if (splat_sel.candidates[i].id == splat_sel.selected_id) {
                selected_caps = splat_sel.candidates[i].caps;
                if (selected_caps.is_deprecated) {
                    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_SPLAT_DEPRECATED, ok);
                }
                break;
            }
        }

        st = dsk_resolve_components(manifest,
                                    request,
                                    request.target_platform_triple,
                                    &resolved,
                                    &refusals);
        if (!dsk_error_is_ok(st)) {
            audit.result = st;
            dsk_audit_capture_refusals(&audit, refusals);
            dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_PLAN_RESOLVE_FAIL, st);
            goto emit_audit;
        }
        audit.resolved_set_digest64 = resolved.digest64;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_PLAN_RESOLVE_OK, ok);

        st = dsk_plan_build(manifest,
                            request,
                            splat_sel.selected_id,
                            selected_caps,
                            audit.splat_caps_digest64,
                            resolved,
                            manifest_digest,
                            request_digest,
                            &plan);
        if (!dsk_error_is_ok(st)) {
            audit.result = st;
            dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_PLAN_BUILD_FAIL, st);
            goto emit_audit;
        }
        audit.plan_digest64 = plan.plan_digest64;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_PLAN_BUILD_OK, ok);
    }

    if (req->out_plan.write) {
        st = dsk_plan_write(&plan, &plan_buf);
        if (!dsk_error_is_ok(st)) {
            audit.result = st;
            dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_PLAN_BUILD_FAIL, st);
            goto emit_audit;
        }
        st = dsk_sink_write(&req->out_plan, &plan_buf);
        dsk_tlv_buffer_free(&plan_buf);
        if (!dsk_error_is_ok(st)) {
            audit.result = st;
            dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_PLAN_BUILD_FAIL, st);
            goto emit_audit;
        }
    }

    {
        dsk_u16 ownership = dsk_select_ownership(request, selected_caps);
        st = dsk_build_installed_state(manifest,
                                       plan,
                                       splat_sel.selected_id,
                                       ownership,
                                       manifest_digest,
                                       request_digest,
                                       resolved,
                                       &state);
    }
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_WRITE_STATE_FAIL, st);
        dsk_emit_log_event(req_ex, audit.run_id, CORE_LOG_OP_SETUP_WRITE_STATE, CORE_LOG_EVT_OP_FAIL, st);
        goto emit_audit;
    }

    st = dsk_installed_state_write(&state, &state_buf);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_WRITE_STATE_FAIL, st);
        dsk_emit_log_event(req_ex, audit.run_id, CORE_LOG_OP_SETUP_WRITE_STATE, CORE_LOG_EVT_OP_FAIL, st);
        goto emit_audit;
    }

    st = dsk_sink_write(&req->out_state, &state_buf);
    dsk_tlv_buffer_free(&state_buf);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_WRITE_STATE_FAIL, st);
        dsk_emit_log_event(req_ex, audit.run_id, CORE_LOG_OP_SETUP_WRITE_STATE, CORE_LOG_EVT_OP_FAIL, st);
        goto emit_audit;
    }
    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_WRITE_STATE_OK, ok);
    dsk_emit_log_event(req_ex, audit.run_id, CORE_LOG_OP_SETUP_WRITE_STATE, CORE_LOG_EVT_OP_OK, ok);

    audit.result = ok;

emit_audit:
    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_END, audit.result);
    st = dsk_audit_write(&audit, &audit_buf);
    if (dsk_error_is_ok(st)) {
        dsk_status_t wr = dsk_sink_write(&req->out_audit, &audit_buf);
        dsk_tlv_buffer_free(&audit_buf);
        if (!dsk_error_is_ok(wr)) {
            return wr;
        }
    } else {
        return st;
    }

    return audit.result;
}

dsk_status_t dsk_install(const dsk_kernel_request_t *req) {
    dsk_kernel_request_ex_t ex;
    if (!req) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    dsk_kernel_request_ex_init(&ex);
    ex.base = *req;
    return dsk_kernel_run(DSK_OPERATION_INSTALL, &ex);
}

dsk_status_t dsk_upgrade(const dsk_kernel_request_t *req) {
    dsk_kernel_request_ex_t ex;
    if (!req) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    dsk_kernel_request_ex_init(&ex);
    ex.base = *req;
    return dsk_kernel_run(DSK_OPERATION_UPGRADE, &ex);
}

dsk_status_t dsk_repair(const dsk_kernel_request_t *req) {
    dsk_kernel_request_ex_t ex;
    if (!req) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    dsk_kernel_request_ex_init(&ex);
    ex.base = *req;
    return dsk_kernel_run(DSK_OPERATION_REPAIR, &ex);
}

dsk_status_t dsk_uninstall(const dsk_kernel_request_t *req) {
    dsk_kernel_request_ex_t ex;
    if (!req) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    dsk_kernel_request_ex_init(&ex);
    ex.base = *req;
    return dsk_kernel_run(DSK_OPERATION_UNINSTALL, &ex);
}

dsk_status_t dsk_verify(const dsk_kernel_request_t *req) {
    dsk_kernel_request_ex_t ex;
    if (!req) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    dsk_kernel_request_ex_init(&ex);
    ex.base = *req;
    return dsk_kernel_run(DSK_OPERATION_VERIFY, &ex);
}

dsk_status_t dsk_status(const dsk_kernel_request_t *req) {
    dsk_kernel_request_ex_t ex;
    if (!req) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    dsk_kernel_request_ex_init(&ex);
    ex.base = *req;
    return dsk_kernel_run(DSK_OPERATION_STATUS, &ex);
}

dsk_status_t dsk_install_ex(const dsk_kernel_request_ex_t *req) {
    return dsk_kernel_run(DSK_OPERATION_INSTALL, req);
}

dsk_status_t dsk_upgrade_ex(const dsk_kernel_request_ex_t *req) {
    return dsk_kernel_run(DSK_OPERATION_UPGRADE, req);
}

dsk_status_t dsk_repair_ex(const dsk_kernel_request_ex_t *req) {
    return dsk_kernel_run(DSK_OPERATION_REPAIR, req);
}

dsk_status_t dsk_uninstall_ex(const dsk_kernel_request_ex_t *req) {
    return dsk_kernel_run(DSK_OPERATION_UNINSTALL, req);
}

dsk_status_t dsk_verify_ex(const dsk_kernel_request_ex_t *req) {
    return dsk_kernel_run(DSK_OPERATION_VERIFY, req);
}

dsk_status_t dsk_status_ex(const dsk_kernel_request_ex_t *req) {
    return dsk_kernel_run(DSK_OPERATION_STATUS, req);
}
