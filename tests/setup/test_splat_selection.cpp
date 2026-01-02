#include "dsk/dsk_api.h"
#include "dsk/dsk_audit.h"
#include "dsk/dsk_contracts.h"
#include "dsk/dsk_error.h"
#include "dsk/dsk_splat.h"
#include "dsk/dsk_tlv.h"
#include "dss/dss_services.h"

#include <cstdio>
#include <cstring>
#include <vector>

struct dsk_mem_sink_t {
    std::vector<dsk_u8> data;
};

static dsk_status_t dsk_mem_sink_write(void *user, const dsk_u8 *data, dsk_u32 len) {
    dsk_mem_sink_t *sink = reinterpret_cast<dsk_mem_sink_t *>(user);
    if (!sink) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    if (len && !data) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    sink->data.insert(sink->data.end(), data, data + len);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static dsk_u32 dsk_error_subcode(dsk_status_t st) {
    dsk_u32 i;
    for (i = 0u; i < st.detail_count; ++i) {
        if (st.details[i].key_id == (u32)ERR_DETAIL_KEY_SUBCODE &&
            st.details[i].type == (u32)ERR_DETAIL_TYPE_U32) {
            return st.details[i].v.u32_value;
        }
    }
    return 0u;
}

static void build_manifest_base(dsk_manifest_t *out_manifest) {
    dsk_manifest_clear(out_manifest);
    out_manifest->product_id = "dominium";
    out_manifest->version = "0.0.1";
    out_manifest->build_id = "dev";
    out_manifest->supported_targets.push_back("linux_deb");
    {
        dsk_manifest_component_t comp;
        comp.component_id = "core";
        comp.kind = "product";
        comp.default_selected = DSK_TRUE;
        out_manifest->components.push_back(comp);
    }
}

static void build_request_base(dsk_request_t *out_request, const char *target) {
    dsk_request_clear(out_request);
    out_request->operation = DSK_OPERATION_INSTALL;
    out_request->install_scope = DSK_INSTALL_SCOPE_SYSTEM;
    out_request->ui_mode = DSK_UI_MODE_CLI;
    out_request->frontend_id = "cli";
    out_request->policy_flags = DSK_POLICY_DETERMINISTIC;
    out_request->target_platform_triple = target ? target : "linux_deb";
}

static dsk_status_t write_manifest_bytes(const dsk_manifest_t &manifest,
                                         std::vector<dsk_u8> &out) {
    dsk_tlv_buffer_t buf;
    dsk_status_t st = dsk_manifest_write(&manifest, &buf);
    if (dsk_error_is_ok(st)) {
        out.assign(buf.data, buf.data + buf.size);
    }
    dsk_tlv_buffer_free(&buf);
    return st;
}

static dsk_status_t write_request_bytes(const dsk_request_t &request,
                                        std::vector<dsk_u8> &out) {
    dsk_tlv_buffer_t buf;
    dsk_status_t st = dsk_request_write(&request, &buf);
    if (dsk_error_is_ok(st)) {
        out.assign(buf.data, buf.data + buf.size);
    }
    dsk_tlv_buffer_free(&buf);
    return st;
}

static int selection_has_rejection(const dsk_splat_selection_t &selection,
                                   const char *id,
                                   dsk_u16 code) {
    size_t i;
    for (i = 0u; i < selection.rejections.size(); ++i) {
        if (selection.rejections[i].id == id && selection.rejections[i].code == code) {
            return 1;
        }
    }
    return 0;
}

static int audit_has_event(const dsk_audit_t &audit, dsk_u16 event_id) {
    size_t i;
    for (i = 0u; i < audit.events.size(); ++i) {
        if (audit.events[i].event_id == event_id) {
            return 1;
        }
    }
    return 0;
}

static int test_splat_registry_sorted(void) {
    std::vector<dsk_splat_candidate_t> list;
    size_t i;
    static const char *k_required[] = {
        "splat_win32_nt5",
        "splat_win32_9x",
        "splat_win16_win3x",
        "splat_dos",
        "splat_macos_pkg",
        "splat_macos_classic",
        "splat_linux_deb",
        "splat_linux_rpm",
        "splat_linux_portable",
        "splat_steam",
        "splat_portable"
    };

    dsk_splat_registry_list(list);
    if (list.empty()) {
        return fail("registry list empty");
    }
    for (i = 1u; i < list.size(); ++i) {
        if (list[i - 1u].id > list[i].id) {
            return fail("registry not sorted");
        }
    }
    for (i = 0u; i < sizeof(k_required) / sizeof(k_required[0]); ++i) {
        if (!dsk_splat_registry_contains(k_required[i])) {
            return fail("missing required splat id");
        }
    }
    return 0;
}

static int test_splat_select_requested_id_success(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_splat_selection_t selection;
    dsk_status_t st;

    build_manifest_base(&manifest);
    manifest.supported_targets.clear();
    manifest.supported_targets.push_back("macos_pkg");
    build_request_base(&request, "macos_pkg");
    request.requested_splat_id = "splat_macos_pkg";
    request.install_scope = DSK_INSTALL_SCOPE_SYSTEM;
    request.ui_mode = DSK_UI_MODE_GUI;

    st = dsk_splat_select(manifest, request, &selection);
    if (!dsk_error_is_ok(st)) {
        return fail("requested splat selection failed");
    }
    if (selection.selected_id != "splat_macos_pkg") {
        return fail("unexpected selected splat");
    }
    if (selection.selected_reason != DSK_SPLAT_SELECTED_REQUESTED) {
        return fail("unexpected selected reason");
    }
    if (!selection_has_rejection(selection, "splat_portable", DSK_SPLAT_REJECT_REQUESTED_ID_MISMATCH)) {
        return fail("missing requested-id rejection");
    }
    return 0;
}

static int test_splat_select_requested_id_not_found(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_splat_selection_t selection;
    dsk_status_t st;

    build_manifest_base(&manifest);
    build_request_base(&request, "linux_deb");
    request.requested_splat_id = "splat_missing";

    st = dsk_splat_select(manifest, request, &selection);
    if (dsk_error_is_ok(st)) {
        return fail("expected splat not found failure");
    }
    if (dsk_error_subcode(st) != DSK_SUBCODE_SPLAT_NOT_FOUND) {
        return fail("unexpected subcode for missing splat");
    }
    if (selection.rejections.empty()) {
        return fail("missing rejections for not found");
    }
    return 0;
}

static int test_splat_select_requested_id_removed(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_splat_selection_t selection;
    dsk_status_t st;

    build_manifest_base(&manifest);
    build_request_base(&request, "win32_9x");
    request.requested_splat_id = "splat_win32_nt4";

    st = dsk_splat_select(manifest, request, &selection);
    if (dsk_error_is_ok(st)) {
        return fail("expected removed splat failure");
    }
    if (dsk_error_subcode(st) != DSK_SUBCODE_SPLAT_REMOVED) {
        return fail("unexpected subcode for removed splat");
    }
    return 0;
}

static int test_splat_select_filters_by_platform(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_splat_selection_t selection;
    dsk_status_t st;

    build_manifest_base(&manifest);
    manifest.allowed_splats.clear();
    manifest.allowed_splats.push_back("splat_win32_nt5");
    build_request_base(&request, "linux_deb");
    request.install_scope = DSK_INSTALL_SCOPE_SYSTEM;
    request.ui_mode = DSK_UI_MODE_CLI;

    st = dsk_splat_select(manifest, request, &selection);
    if (dsk_error_is_ok(st)) {
        return fail("expected platform filter failure");
    }
    if (!selection_has_rejection(selection, "splat_win32_nt5", DSK_SPLAT_REJECT_PLATFORM_UNSUPPORTED)) {
        return fail("missing platform rejection");
    }
    return 0;
}

static int test_splat_select_filters_by_scope(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_splat_selection_t selection;
    dsk_status_t st;

    build_manifest_base(&manifest);
    manifest.allowed_splats.clear();
    manifest.allowed_splats.push_back("splat_linux_deb");
    build_request_base(&request, "linux_deb");
    request.install_scope = DSK_INSTALL_SCOPE_USER;
    request.ui_mode = DSK_UI_MODE_CLI;

    st = dsk_splat_select(manifest, request, &selection);
    if (dsk_error_is_ok(st)) {
        return fail("expected scope filter failure");
    }
    if (!selection_has_rejection(selection, "splat_linux_deb", DSK_SPLAT_REJECT_SCOPE_UNSUPPORTED)) {
        return fail("missing scope rejection");
    }
    return 0;
}

static int test_splat_select_filters_by_ui_mode(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_splat_selection_t selection;
    dsk_status_t st;

    build_manifest_base(&manifest);
    manifest.allowed_splats.clear();
    manifest.allowed_splats.push_back("splat_linux_deb");
    build_request_base(&request, "linux_deb");
    request.install_scope = DSK_INSTALL_SCOPE_SYSTEM;
    request.ui_mode = DSK_UI_MODE_GUI;

    st = dsk_splat_select(manifest, request, &selection);
    if (dsk_error_is_ok(st)) {
        return fail("expected ui mode filter failure");
    }
    if (!selection_has_rejection(selection, "splat_linux_deb", DSK_SPLAT_REJECT_UI_MODE_UNSUPPORTED)) {
        return fail("missing ui mode rejection");
    }
    return 0;
}

static int test_splat_select_no_compatible_emits_rejections_and_audit(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    std::vector<dsk_u8> manifest_bytes;
    std::vector<dsk_u8> request_bytes;
    dsk_kernel_request_t kernel_req;
    dsk_mem_sink_t audit_sink;
    dsk_mem_sink_t state_sink;
    dss_services_t services;
    dss_services_config_t cfg;
    dsk_status_t st;
    dsk_audit_t audit;

    build_manifest_base(&manifest);
    manifest.allowed_splats.clear();
    manifest.allowed_splats.push_back("splat_linux_deb");
    build_request_base(&request, "linux_deb");
    request.install_scope = DSK_INSTALL_SCOPE_USER;
    request.ui_mode = DSK_UI_MODE_CLI;

    st = write_manifest_bytes(manifest, manifest_bytes);
    if (!dsk_error_is_ok(st)) return fail("manifest write failed");
    st = write_request_bytes(request, request_bytes);
    if (!dsk_error_is_ok(st)) return fail("request write failed");

    dss_services_config_init(&cfg);
    cfg.platform_triple = "linux_deb";
    dss_services_init_fake(&cfg, &services);

    dsk_kernel_request_init(&kernel_req);
    kernel_req.services = &services;
    kernel_req.manifest_bytes = &manifest_bytes[0];
    kernel_req.manifest_size = (dsk_u32)manifest_bytes.size();
    kernel_req.request_bytes = &request_bytes[0];
    kernel_req.request_size = (dsk_u32)request_bytes.size();
    kernel_req.deterministic_mode = 1u;
    kernel_req.out_state.user = &state_sink;
    kernel_req.out_state.write = dsk_mem_sink_write;
    kernel_req.out_audit.user = &audit_sink;
    kernel_req.out_audit.write = dsk_mem_sink_write;

    st = dsk_install(&kernel_req);
    dss_services_shutdown(&services);
    if (dsk_error_is_ok(st)) {
        return fail("expected no compatible splat failure");
    }
    if (audit_sink.data.empty()) {
        return fail("missing audit payload");
    }
    st = dsk_audit_parse(&audit_sink.data[0],
                         (dsk_u32)audit_sink.data.size(),
                         &audit);
    if (!dsk_error_is_ok(st)) {
        return fail("audit parse failed");
    }
    if (audit.selection.candidates.empty()) {
        return fail("missing audit candidates");
    }
    if (audit.selection.rejections.empty()) {
        return fail("missing audit rejections");
    }
    if (dsk_error_subcode(audit.result) != DSK_SUBCODE_NO_COMPATIBLE_SPLAT) {
        return fail("unexpected audit subcode");
    }
    return 0;
}

static int test_splat_select_deterministic_choice_first_compatible(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_splat_selection_t selection;
    dsk_status_t st;

    build_manifest_base(&manifest);
    manifest.supported_targets.clear();
    manifest.supported_targets.push_back("linux_portable");
    build_request_base(&request, "linux_portable");
    request.install_scope = DSK_INSTALL_SCOPE_PORTABLE;
    request.ui_mode = DSK_UI_MODE_CLI;

    st = dsk_splat_select(manifest, request, &selection);
    if (!dsk_error_is_ok(st)) {
        return fail("expected selection success");
    }
    if (selection.selected_id != "splat_linux_portable") {
        return fail("unexpected first compatible selection");
    }
    if (selection.selected_reason != DSK_SPLAT_SELECTED_FIRST_COMPATIBLE) {
        return fail("unexpected selected reason");
    }
    return 0;
}

static int test_splat_select_deprecated_emits_warning(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    std::vector<dsk_u8> manifest_bytes;
    std::vector<dsk_u8> request_bytes;
    dsk_kernel_request_t kernel_req;
    dsk_mem_sink_t audit_sink;
    dsk_mem_sink_t state_sink;
    dss_services_t services;
    dss_services_config_t cfg;
    dsk_status_t st;
    dsk_audit_t audit;

    build_manifest_base(&manifest);
    manifest.supported_targets.clear();
    manifest.supported_targets.push_back("win32_9x");
    build_request_base(&request, "win32_9x");
    request.install_scope = DSK_INSTALL_SCOPE_SYSTEM;
    request.ui_mode = DSK_UI_MODE_CLI;

    st = write_manifest_bytes(manifest, manifest_bytes);
    if (!dsk_error_is_ok(st)) return fail("manifest write failed");
    st = write_request_bytes(request, request_bytes);
    if (!dsk_error_is_ok(st)) return fail("request write failed");

    dss_services_config_init(&cfg);
    cfg.platform_triple = "win32_9x";
    dss_services_init_fake(&cfg, &services);

    dsk_kernel_request_init(&kernel_req);
    kernel_req.services = &services;
    kernel_req.manifest_bytes = &manifest_bytes[0];
    kernel_req.manifest_size = (dsk_u32)manifest_bytes.size();
    kernel_req.request_bytes = &request_bytes[0];
    kernel_req.request_size = (dsk_u32)request_bytes.size();
    kernel_req.deterministic_mode = 1u;
    kernel_req.out_state.user = &state_sink;
    kernel_req.out_state.write = dsk_mem_sink_write;
    kernel_req.out_audit.user = &audit_sink;
    kernel_req.out_audit.write = dsk_mem_sink_write;

    st = dsk_install(&kernel_req);
    dss_services_shutdown(&services);
    if (!dsk_error_is_ok(st)) {
        return fail("expected deprecated splat selection success");
    }
    if (audit_sink.data.empty()) {
        return fail("missing audit payload");
    }
    st = dsk_audit_parse(&audit_sink.data[0],
                         (dsk_u32)audit_sink.data.size(),
                         &audit);
    if (!dsk_error_is_ok(st)) {
        return fail("audit parse failed");
    }
    if (!audit_has_event(audit, DSK_AUDIT_EVENT_SPLAT_DEPRECATED)) {
        return fail("missing deprecated splat audit event");
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        std::fprintf(stderr, "usage: setup_splat_tests <test>\n");
        return 1;
    }
    if (std::strcmp(argv[1], "splat_registry_sorted") == 0) {
        return test_splat_registry_sorted();
    }
    if (std::strcmp(argv[1], "splat_select_requested_id_success") == 0) {
        return test_splat_select_requested_id_success();
    }
    if (std::strcmp(argv[1], "splat_select_requested_id_not_found") == 0) {
        return test_splat_select_requested_id_not_found();
    }
    if (std::strcmp(argv[1], "splat_select_requested_id_removed") == 0) {
        return test_splat_select_requested_id_removed();
    }
    if (std::strcmp(argv[1], "splat_select_filters_by_platform") == 0) {
        return test_splat_select_filters_by_platform();
    }
    if (std::strcmp(argv[1], "splat_select_filters_by_scope") == 0) {
        return test_splat_select_filters_by_scope();
    }
    if (std::strcmp(argv[1], "splat_select_filters_by_ui_mode") == 0) {
        return test_splat_select_filters_by_ui_mode();
    }
    if (std::strcmp(argv[1], "splat_select_no_compatible_emits_rejections_and_audit") == 0) {
        return test_splat_select_no_compatible_emits_rejections_and_audit();
    }
    if (std::strcmp(argv[1], "splat_select_deterministic_choice_first_compatible") == 0) {
        return test_splat_select_deterministic_choice_first_compatible();
    }
    if (std::strcmp(argv[1], "splat_select_deprecated_emits_warning") == 0) {
        return test_splat_select_deprecated_emits_warning();
    }
    std::fprintf(stderr, "unknown test: %s\n", argv[1]);
    return 1;
}
