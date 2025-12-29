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

static void build_basic_manifest(dsk_manifest_t *out_manifest) {
    dsk_manifest_clear(out_manifest);
    out_manifest->product_id = "dominium";
    out_manifest->version = "0.0.1";
    out_manifest->build_id = "dev";
    out_manifest->supported_targets.push_back("win32_nt5");
    out_manifest->supported_targets.push_back("linux_deb");

    {
        dsk_manifest_component_t comp;
        comp.component_id = "core";
        comp.kind = "product";
        comp.default_selected = DSK_TRUE;
        comp.deps.push_back("base");
        comp.conflicts.push_back("legacy");
        {
            dsk_artifact_t art;
            art.hash = "deadbeef";
            art.size = 123u;
            art.path = "bin/core.dat";
            comp.artifacts.push_back(art);
        }
        out_manifest->components.push_back(comp);
    }
    {
        dsk_manifest_component_t comp;
        comp.component_id = "extras";
        comp.kind = "tool";
        comp.default_selected = DSK_FALSE;
        out_manifest->components.push_back(comp);
    }
}

static void build_basic_request(dsk_request_t *out_request,
                                dsk_u16 operation,
                                const char *platform) {
    dsk_request_clear(out_request);
    out_request->operation = operation;
    out_request->install_scope = DSK_INSTALL_SCOPE_SYSTEM;
    out_request->ui_mode = DSK_UI_MODE_CLI;
    out_request->policy_flags = DSK_POLICY_DETERMINISTIC;
    out_request->target_platform_triple = platform ? platform : "win32_nt5";
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

static dsk_u16 read_u16_le(const dsk_u8 *p) {
    return (dsk_u16)p[0] | (dsk_u16)((dsk_u16)p[1] << 8);
}

static dsk_u32 read_u32_le(const dsk_u8 *p) {
    return (dsk_u32)p[0]
         | ((dsk_u32)p[1] << 8)
         | ((dsk_u32)p[2] << 16)
         | ((dsk_u32)p[3] << 24);
}

static void write_u16_le(dsk_u8 *p, dsk_u16 v) {
    p[0] = (dsk_u8)(v & 0xFFu);
    p[1] = (dsk_u8)((v >> 8) & 0xFFu);
}

static void write_u32_le(dsk_u8 *p, dsk_u32 v) {
    p[0] = (dsk_u8)(v & 0xFFu);
    p[1] = (dsk_u8)((v >> 8) & 0xFFu);
    p[2] = (dsk_u8)((v >> 16) & 0xFFu);
    p[3] = (dsk_u8)((v >> 24) & 0xFFu);
}

static int append_unknown_record(std::vector<dsk_u8> &bytes) {
    if (bytes.size() < DSK_TLV_HEADER_SIZE) {
        return 0;
    }
    dsk_u32 payload_size = read_u32_le(&bytes[12]);
    dsk_u32 header_size = read_u32_le(&bytes[8]);
    if (header_size < DSK_TLV_HEADER_SIZE) {
        return 0;
    }
    dsk_u32 offset = header_size + payload_size;
    dsk_u16 type = 0xEEEFu;
    const char payload[] = "xyz";
    dsk_u32 len = (dsk_u32)sizeof(payload) - 1u;
    bytes.resize(bytes.size() + 6u + len);
    write_u16_le(&bytes[offset], type);
    write_u32_le(&bytes[offset + 2u], len);
    std::memcpy(&bytes[offset + 6u], payload, len);
    payload_size += 6u + len;
    write_u32_le(&bytes[12], payload_size);
    {
        dsk_u8 header[DSK_TLV_HEADER_SIZE];
        std::memcpy(header, &bytes[0], DSK_TLV_HEADER_SIZE);
        header[16] = 0u;
        header[17] = 0u;
        header[18] = 0u;
        header[19] = 0u;
        dsk_u32 crc = dsk_tlv_crc32(header, DSK_TLV_HEADER_SIZE);
        write_u32_le(&bytes[16], crc);
    }
    return 1;
}

static int test_tlv_roundtrip_known_fields(void) {
    dsk_manifest_t manifest;
    dsk_manifest_t parsed;
    std::vector<dsk_u8> first;
    std::vector<dsk_u8> second;
    dsk_status_t st;

    build_basic_manifest(&manifest);
    st = write_manifest_bytes(manifest, first);
    if (!dsk_error_is_ok(st)) {
        return fail("manifest write failed");
    }
    st = dsk_manifest_parse(&first[0], (dsk_u32)first.size(), &parsed);
    if (!dsk_error_is_ok(st)) {
        return fail("manifest parse failed");
    }
    st = write_manifest_bytes(parsed, second);
    if (!dsk_error_is_ok(st)) {
        return fail("manifest re-write failed");
    }
    if (first.size() != second.size() ||
        std::memcmp(&first[0], &second[0], first.size()) != 0) {
        return fail("manifest roundtrip mismatch");
    }
    return 0;
}

static int test_tlv_skip_unknown(void) {
    dsk_manifest_t manifest;
    std::vector<dsk_u8> bytes;
    dsk_status_t st;

    build_basic_manifest(&manifest);
    st = write_manifest_bytes(manifest, bytes);
    if (!dsk_error_is_ok(st)) {
        return fail("manifest write failed");
    }
    if (!append_unknown_record(bytes)) {
        return fail("append unknown record failed");
    }
    st = dsk_manifest_parse(&bytes[0], (dsk_u32)bytes.size(), &manifest);
    if (!dsk_error_is_ok(st)) {
        return fail("parse failed on unknown record");
    }
    return 0;
}

static int test_manifest_validate_missing_required(void) {
    dsk_manifest_t manifest;
    std::vector<dsk_u8> bytes;
    dsk_status_t st;

    build_basic_manifest(&manifest);
    manifest.product_id.clear();
    st = write_manifest_bytes(manifest, bytes);
    if (!dsk_error_is_ok(st)) {
        return fail("manifest write failed");
    }
    st = dsk_manifest_parse(&bytes[0], (dsk_u32)bytes.size(), &manifest);
    if (dsk_error_is_ok(st)) {
        return fail("expected manifest validation failure");
    }
    return 0;
}

static int test_request_validate_missing_required(void) {
    dsk_request_t request;
    std::vector<dsk_u8> bytes;
    dsk_status_t st;

    build_basic_request(&request, DSK_OPERATION_INSTALL, "");
    request.target_platform_triple.clear();
    st = write_request_bytes(request, bytes);
    if (!dsk_error_is_ok(st)) {
        return fail("request write failed");
    }
    st = dsk_request_parse(&bytes[0], (dsk_u32)bytes.size(), &request);
    if (dsk_error_is_ok(st)) {
        return fail("expected request validation failure");
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

static int test_kernel_emits_audit_on_failure(void) {
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

    build_basic_manifest(&manifest);
    manifest.product_id.clear();
    build_basic_request(&request, DSK_OPERATION_INSTALL, "win32_nt5");

    st = write_manifest_bytes(manifest, manifest_bytes);
    if (!dsk_error_is_ok(st)) return fail("manifest write failed");
    st = write_request_bytes(request, request_bytes);
    if (!dsk_error_is_ok(st)) return fail("request write failed");

    dss_services_config_init(&cfg);
    cfg.platform_triple = "win32_nt5";
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
        return fail("expected kernel failure");
    }
    if (audit_sink.data.empty()) {
        return fail("audit not emitted");
    }
    st = dsk_audit_parse(&audit_sink.data[0],
                         (dsk_u32)audit_sink.data.size(),
                         &audit);
    if (!dsk_error_is_ok(st)) {
        return fail("audit parse failed");
    }
    if (!audit_has_event(audit, DSK_AUDIT_EVENT_PARSE_MANIFEST_FAIL)) {
        return fail("missing audit failure event");
    }
    return 0;
}

static int test_splat_selection_deterministic(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    std::vector<dsk_u8> manifest_bytes;
    std::vector<dsk_u8> request_bytes;
    dsk_kernel_request_t kernel_req;
    dsk_mem_sink_t audit_sink_a;
    dsk_mem_sink_t audit_sink_b;
    dsk_mem_sink_t state_sink_a;
    dsk_mem_sink_t state_sink_b;
    dss_services_t services;
    dss_services_config_t cfg;
    dsk_status_t st;
    dsk_audit_t audit_a;
    dsk_audit_t audit_b;

    build_basic_manifest(&manifest);
    build_basic_request(&request, DSK_OPERATION_INSTALL, "win32_nt5");

    st = write_manifest_bytes(manifest, manifest_bytes);
    if (!dsk_error_is_ok(st)) return fail("manifest write failed");
    st = write_request_bytes(request, request_bytes);
    if (!dsk_error_is_ok(st)) return fail("request write failed");

    dss_services_config_init(&cfg);
    cfg.platform_triple = "win32_nt5";
    dss_services_init_fake(&cfg, &services);

    dsk_kernel_request_init(&kernel_req);
    kernel_req.services = &services;
    kernel_req.manifest_bytes = &manifest_bytes[0];
    kernel_req.manifest_size = (dsk_u32)manifest_bytes.size();
    kernel_req.request_bytes = &request_bytes[0];
    kernel_req.request_size = (dsk_u32)request_bytes.size();
    kernel_req.deterministic_mode = 1u;

    kernel_req.out_state.user = &state_sink_a;
    kernel_req.out_state.write = dsk_mem_sink_write;
    kernel_req.out_audit.user = &audit_sink_a;
    kernel_req.out_audit.write = dsk_mem_sink_write;
    st = dsk_install(&kernel_req);
    if (!dsk_error_is_ok(st)) return fail("first kernel run failed");

    kernel_req.out_state.user = &state_sink_b;
    kernel_req.out_state.write = dsk_mem_sink_write;
    kernel_req.out_audit.user = &audit_sink_b;
    kernel_req.out_audit.write = dsk_mem_sink_write;
    st = dsk_install(&kernel_req);
    dss_services_shutdown(&services);
    if (!dsk_error_is_ok(st)) return fail("second kernel run failed");

    st = dsk_audit_parse(&audit_sink_a.data[0],
                         (dsk_u32)audit_sink_a.data.size(),
                         &audit_a);
    if (!dsk_error_is_ok(st)) return fail("audit A parse failed");
    st = dsk_audit_parse(&audit_sink_b.data[0],
                         (dsk_u32)audit_sink_b.data.size(),
                         &audit_b);
    if (!dsk_error_is_ok(st)) return fail("audit B parse failed");

    if (audit_a.selected_splat != audit_b.selected_splat) {
        return fail("splat selection not deterministic");
    }
    if (audit_a.selected_splat != "splat_win32_nt5") {
        return fail("unexpected splat selection");
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        std::fprintf(stderr, "usage: setup2_kernel_tests <test>\n");
        return 1;
    }
    if (std::strcmp(argv[1], "tlv_roundtrip_known_fields") == 0) {
        return test_tlv_roundtrip_known_fields();
    }
    if (std::strcmp(argv[1], "tlv_skip_unknown") == 0) {
        return test_tlv_skip_unknown();
    }
    if (std::strcmp(argv[1], "manifest_validate_missing_required") == 0) {
        return test_manifest_validate_missing_required();
    }
    if (std::strcmp(argv[1], "request_validate_missing_required") == 0) {
        return test_request_validate_missing_required();
    }
    if (std::strcmp(argv[1], "kernel_emits_audit_on_failure") == 0) {
        return test_kernel_emits_audit_on_failure();
    }
    if (std::strcmp(argv[1], "splat_selection_deterministic") == 0) {
        return test_splat_selection_deterministic();
    }
    std::fprintf(stderr, "unknown test: %s\n", argv[1]);
    return 1;
}
