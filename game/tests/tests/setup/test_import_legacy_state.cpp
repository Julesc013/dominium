#include "dsk/dsk_api.h"
#include "dsk/dsk_audit.h"
#include "dsk/dsk_contracts.h"
#include "dsk/dsk_error.h"

#include <cstdio>
#include <fstream>
#include <string>
#include <vector>

#ifndef SETUP_TESTS_SOURCE_DIR
#define SETUP_TESTS_SOURCE_DIR "."
#endif

struct mem_sink_t {
    std::vector<dsk_u8> data;
};

static dsk_status_t mem_sink_write(void *user, const dsk_u8 *data, dsk_u32 len) {
    mem_sink_t *sink = reinterpret_cast<mem_sink_t *>(user);
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

static int read_file(const std::string &path, std::vector<dsk_u8> &out) {
    std::ifstream in(path.c_str(), std::ios::binary);
    if (!in) {
        return 0;
    }
    in.seekg(0, std::ios::end);
    std::streamoff size = in.tellg();
    if (size < 0) {
        return 0;
    }
    in.seekg(0, std::ios::beg);
    out.resize((size_t)size);
    if (size > 0) {
        in.read(reinterpret_cast<char *>(&out[0]), size);
    }
    return in.good() || in.eof();
}

static dsk_bool has_detail(const std::vector<std::string> &details, const char *value) {
    size_t i;
    for (i = 0u; i < details.size(); ++i) {
        if (details[i] == value) {
            return DSK_TRUE;
        }
    }
    return DSK_FALSE;
}

static dsk_bool has_event(const std::vector<dsk_audit_event_t> &events, dsk_u16 event_id) {
    size_t i;
    for (i = 0u; i < events.size(); ++i) {
        if (events[i].event_id == event_id) {
            return DSK_TRUE;
        }
    }
    return DSK_FALSE;
}

int main(void) {
    std::string path = std::string(SETUP_TESTS_SOURCE_DIR) + "/fixtures/legacy_state_min.tlv";
    std::vector<dsk_u8> legacy_bytes;
    mem_sink_t state_sink;
    mem_sink_t audit_sink;
    dsk_import_request_t req;
    dsk_installed_state_t state;
    dsk_audit_t audit;
    dsk_status_t st;

    if (!read_file(path, legacy_bytes)) {
        return fail("failed to read legacy state fixture");
    }

    dsk_import_request_init(&req);
    req.legacy_state_bytes = legacy_bytes.empty() ? 0 : &legacy_bytes[0];
    req.legacy_state_size = (dsk_u32)legacy_bytes.size();
    req.out_state.user = &state_sink;
    req.out_state.write = mem_sink_write;
    req.out_audit.user = &audit_sink;
    req.out_audit.write = mem_sink_write;
    req.deterministic_mode = 1u;

    st = dsk_import_legacy_state(&req);
    if (!dsk_error_is_ok(st)) {
        return fail("import legacy state failed");
    }
    if (state_sink.data.empty() || audit_sink.data.empty()) {
        return fail("import outputs missing");
    }

    st = dsk_installed_state_parse(&state_sink.data[0],
                                   (dsk_u32)state_sink.data.size(),
                                   &state);
    if (!dsk_error_is_ok(st)) {
        return fail("imported state parse failed");
    }
    if (state.product_id != "dominium") {
        return fail("product_id mismatch");
    }
    if (state.installed_version != "1.0.0") {
        return fail("installed_version mismatch");
    }
    if (state.selected_splat != "legacy-import") {
        return fail("selected_splat mismatch");
    }
    if (state.install_scope != DSK_INSTALL_SCOPE_PORTABLE) {
        return fail("install_scope mismatch");
    }
    if (state.install_root != "C:/Dominium") {
        return fail("install_root mismatch");
    }
    if (state.installed_components.size() != 1u || state.installed_components[0] != "base") {
        return fail("installed_components mismatch");
    }
    if (state.import_source != "legacy_dsu_state_v2") {
        return fail("import_source mismatch");
    }
    if (!has_detail(state.import_details, "legacy_state_version=2")) {
        return fail("missing import detail legacy_state_version");
    }

    st = dsk_audit_parse(&audit_sink.data[0],
                         (dsk_u32)audit_sink.data.size(),
                         &audit);
    if (!dsk_error_is_ok(st)) {
        return fail("audit parse failed");
    }
    if (audit.operation != DSK_OPERATION_IMPORT_LEGACY) {
        return fail("audit operation mismatch");
    }
    if (audit.import_source != "legacy_dsu_state_v2") {
        return fail("audit import_source mismatch");
    }
    if (!has_event(audit.events, DSK_AUDIT_EVENT_IMPORT_BEGIN) ||
        !has_event(audit.events, DSK_AUDIT_EVENT_IMPORT_END)) {
        return fail("audit import events missing");
    }

    return 0;
}
