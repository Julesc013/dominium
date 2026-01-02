#include "dsk/dsk_api.h"
#include "dsk/dsk_audit.h"
#include "dsk/dsk_contracts.h"
#include "dsk/dsk_error.h"
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

static void build_manifest(dsk_manifest_t *out_manifest) {
    dsk_manifest_clear(out_manifest);
    out_manifest->product_id = "dominium";
    out_manifest->version = "0.0.1";
    out_manifest->build_id = "dev";
    out_manifest->supported_targets.push_back("win32_nt5");
    out_manifest->supported_targets.push_back("linux_deb");
    {
        dsk_layout_template_t layout;
        layout.template_id = "root_base";
        layout.target_root = "primary";
        layout.path_prefix = "app";
        out_manifest->layout_templates.push_back(layout);
    }
    {
        dsk_manifest_component_t comp;
        comp.component_id = "core";
        comp.kind = "product";
        comp.default_selected = DSK_TRUE;
        {
            dsk_artifact_t art;
            art.artifact_id = "core_bin";
            art.hash = "deadbeef";
            art.digest64 = 0x1111111111111111ULL;
            art.size = 123u;
            art.source_path = "bin/core.dat";
            art.layout_template_id = "root_base";
            comp.artifacts.push_back(art);
        }
        out_manifest->components.push_back(comp);
    }
}

static void build_request(dsk_request_t *out_request) {
    dsk_request_clear(out_request);
    out_request->operation = DSK_OPERATION_INSTALL;
    out_request->install_scope = DSK_INSTALL_SCOPE_SYSTEM;
    out_request->ui_mode = DSK_UI_MODE_CLI;
    out_request->frontend_id = "cli";
    out_request->policy_flags = DSK_POLICY_DETERMINISTIC;
    out_request->target_platform_triple = "win32_nt5";
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

static int test_kernel_uses_services_platform(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    std::vector<dsk_u8> manifest_bytes;
    std::vector<dsk_u8> request_bytes;
    dsk_kernel_request_t kernel_req;
    dsk_mem_sink_t state_sink;
    dsk_mem_sink_t audit_sink;
    dss_services_t services;
    dss_services_config_t cfg;
    dsk_status_t st;
    dsk_audit_t audit;

    build_manifest(&manifest);
    build_request(&request);

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
    if (!dsk_error_is_ok(st)) {
        return fail("kernel run failed");
    }
    st = dsk_audit_parse(&audit_sink.data[0],
                         (dsk_u32)audit_sink.data.size(),
                         &audit);
    if (!dsk_error_is_ok(st)) {
        return fail("audit parse failed");
    }
    if (audit.selected_splat != "splat_linux_deb") {
        return fail("expected linux splat selection");
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        std::fprintf(stderr, "usage: test_kernel_uses_services_platform <test>\n");
        return 1;
    }
    if (std::strcmp(argv[1], "kernel_uses_services_platform") == 0) {
        return test_kernel_uses_services_platform();
    }
    std::fprintf(stderr, "unknown test: %s\n", argv[1]);
    return 1;
}
