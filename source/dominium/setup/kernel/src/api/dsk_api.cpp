#include "dsk/dsk_api.h"
#include "dsk/dsk_audit.h"
#include "dsk/dsk_contracts.h"
#include "dsk/dsk_digest.h"
#include "dsk/dsk_splat.h"

#include <algorithm>
#include <ctime>
#include <cstdlib>

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

static dsk_status_t dsk_sink_write(const dsk_byte_sink_t *sink, const dsk_tlv_buffer_t *buf) {
    if (!sink || !sink->write || !buf) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    return sink->write(sink->user, buf->data, buf->size);
}

static int dsk_manifest_has_component(const dsk_manifest_t &manifest, const std::string &id) {
    size_t i;
    for (i = 0u; i < manifest.components.size(); ++i) {
        if (manifest.components[i].component_id == id) {
            return 1;
        }
    }
    return 0;
}

static void dsk_select_default_components(const dsk_manifest_t &manifest,
                                          std::vector<std::string> &out_selected) {
    size_t i;
    for (i = 0u; i < manifest.components.size(); ++i) {
        if (manifest.components[i].default_selected) {
            out_selected.push_back(manifest.components[i].component_id);
        }
    }
}

static void dsk_select_component_unique(std::vector<std::string> &selected,
                                        const std::string &id) {
    if (std::find(selected.begin(), selected.end(), id) == selected.end()) {
        selected.push_back(id);
    }
}

static void dsk_remove_component(std::vector<std::string> &selected,
                                 const std::string &id) {
    std::vector<std::string>::iterator it = std::find(selected.begin(), selected.end(), id);
    if (it != selected.end()) {
        selected.erase(it);
    }
}

static dsk_status_t dsk_build_installed_state(const dsk_manifest_t &manifest,
                                              const dsk_request_t &request,
                                              const std::string &selected_splat,
                                              dsk_u64 manifest_digest,
                                              dsk_u64 request_digest,
                                              dsk_installed_state_t *out_state) {
    size_t i;
    std::vector<std::string> selected;

    if (!out_state) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    dsk_installed_state_clear(out_state);
    out_state->product_id = manifest.product_id;
    out_state->installed_version = manifest.version;
    out_state->selected_splat = selected_splat;
    out_state->install_scope = request.install_scope;
    out_state->install_root = request.preferred_install_root;
    out_state->manifest_digest64 = manifest_digest;
    out_state->request_digest64 = request_digest;

    dsk_select_default_components(manifest, selected);

    for (i = 0u; i < request.requested_components.size(); ++i) {
        const std::string &id = request.requested_components[i];
        if (!dsk_manifest_has_component(manifest, id)) {
            return dsk_error_make(DSK_DOMAIN_KERNEL,
                                  DSK_CODE_VALIDATION_ERROR,
                                  DSK_SUBCODE_INVALID_FIELD,
                                  DSK_ERROR_FLAG_USER_ACTIONABLE);
        }
        dsk_select_component_unique(selected, id);
    }

    for (i = 0u; i < request.excluded_components.size(); ++i) {
        const std::string &id = request.excluded_components[i];
        if (!dsk_manifest_has_component(manifest, id)) {
            return dsk_error_make(DSK_DOMAIN_KERNEL,
                                  DSK_CODE_VALIDATION_ERROR,
                                  DSK_SUBCODE_INVALID_FIELD,
                                  DSK_ERROR_FLAG_USER_ACTIONABLE);
        }
        dsk_remove_component(selected, id);
    }

    out_state->installed_components = selected;
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

void dsk_kernel_request_init(dsk_kernel_request_t *req) {
    if (!req) {
        return;
    }
    req->manifest_bytes = 0;
    req->manifest_size = 0u;
    req->request_bytes = 0;
    req->request_size = 0u;
    req->out_state.user = 0;
    req->out_state.write = 0;
    req->out_audit.user = 0;
    req->out_audit.write = 0;
    req->deterministic_mode = 1u;
}

static dsk_status_t dsk_kernel_run(dsk_u16 expected_operation, const dsk_kernel_request_t *req) {
    dsk_status_t st;
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_installed_state_t state;
    dsk_splat_selection_t splat_sel;
    dsk_audit_t audit;
    dsk_tlv_buffer_t state_buf;
    dsk_tlv_buffer_t audit_buf;
    dsk_u64 manifest_digest;
    dsk_u64 request_digest;
    dsk_error_t ok = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);

    if (!req || !req->manifest_bytes || !req->request_bytes ||
        !req->out_audit.write || !req->out_state.write) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }

    dsk_manifest_clear(&manifest);
    dsk_request_clear(&request);
    dsk_installed_state_clear(&state);
    dsk_audit_clear(&audit);

    manifest_digest = dsk_digest64_bytes(req->manifest_bytes, req->manifest_size);
    request_digest = dsk_digest64_bytes(req->request_bytes, req->request_size);

    audit.run_id = dsk_generate_run_id(req->deterministic_mode);
    audit.manifest_digest64 = manifest_digest;
    audit.request_digest64 = request_digest;
    audit.operation = expected_operation;
    audit.result = ok;

    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_BEGIN, ok);

    st = dsk_manifest_parse(req->manifest_bytes, req->manifest_size, &manifest);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_PARSE_MANIFEST_FAIL, st);
        goto emit_audit;
    }
    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_PARSE_MANIFEST_OK, ok);

    st = dsk_request_parse(req->request_bytes, req->request_size, &request);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_PARSE_REQUEST_FAIL, st);
        goto emit_audit;
    }

    if (request.operation != expected_operation) {
        st = dsk_error_make(DSK_DOMAIN_KERNEL,
                            DSK_CODE_VALIDATION_ERROR,
                            DSK_SUBCODE_REQUEST_MISMATCH,
                            DSK_ERROR_FLAG_USER_ACTIONABLE);
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_PARSE_REQUEST_FAIL, st);
        goto emit_audit;
    }
    audit.operation = request.operation;
    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_PARSE_REQUEST_OK, ok);

    st = dsk_splat_select(manifest, request, &splat_sel);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_SPLAT_SELECT_FAIL, st);
        goto emit_audit;
    }

    audit.selected_splat = splat_sel.chosen;
    audit.selection_reason.candidates = splat_sel.candidates;
    audit.selection_reason.rejections = splat_sel.rejections;
    audit.selection_reason.chosen = splat_sel.chosen;
    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_SPLAT_SELECT_OK, ok);

    st = dsk_build_installed_state(manifest,
                                   request,
                                   splat_sel.chosen,
                                   manifest_digest,
                                   request_digest,
                                   &state);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_WRITE_STATE_FAIL, st);
        goto emit_audit;
    }

    st = dsk_installed_state_write(&state, &state_buf);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_WRITE_STATE_FAIL, st);
        goto emit_audit;
    }

    st = dsk_sink_write(&req->out_state, &state_buf);
    dsk_tlv_buffer_free(&state_buf);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_WRITE_STATE_FAIL, st);
        goto emit_audit;
    }
    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_WRITE_STATE_OK, ok);

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
    return dsk_kernel_run(DSK_OPERATION_INSTALL, req);
}

dsk_status_t dsk_repair(const dsk_kernel_request_t *req) {
    return dsk_kernel_run(DSK_OPERATION_REPAIR, req);
}

dsk_status_t dsk_uninstall(const dsk_kernel_request_t *req) {
    return dsk_kernel_run(DSK_OPERATION_UNINSTALL, req);
}

dsk_status_t dsk_verify(const dsk_kernel_request_t *req) {
    return dsk_kernel_run(DSK_OPERATION_VERIFY, req);
}

dsk_status_t dsk_status(const dsk_kernel_request_t *req) {
    return dsk_kernel_run(DSK_OPERATION_STATUS, req);
}
