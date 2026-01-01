#include "dsk/dsk_api.h"
#include "dsk/dsk_audit.h"
#include "dsk/dsk_contracts.h"
#include "dsk/dsk_tlv.h"

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <cstring>
#include <string>
#include <vector>

namespace {

enum {
    DSU_TLV_STATE_ROOT = 0x0001u,
    DSU_TLV_STATE_ROOT_VERSION = 0x0002u,
    DSU_TLV_STATE_PRODUCT_ID = 0x0010u,
    DSU_TLV_STATE_PRODUCT_VERSION = 0x0011u,
    DSU_TLV_STATE_BUILD_CHANNEL = 0x0012u,
    DSU_TLV_STATE_PLATFORM = 0x0020u,
    DSU_TLV_STATE_SCOPE = 0x0021u,
    DSU_TLV_STATE_INSTALL_ROOT = 0x0022u,
    DSU_TLV_STATE_INSTALL_ROOT_ITEM = 0x0023u,
    DSU_TLV_STATE_INSTALL_ROOT_ROLE = 0x0025u,
    DSU_TLV_STATE_INSTALL_ROOT_PATH = 0x0026u,
    DSU_TLV_STATE_COMPONENT = 0x0040u,
    DSU_TLV_STATE_COMPONENT_VERSION = 0x0041u,
    DSU_TLV_STATE_COMPONENT_ID = 0x0042u,
    DSU_TLV_STATE_COMPONENT_VERSTR = 0x0043u,
    DSU_TLV_STATE_COMPONENT_KIND = 0x0044u
};

static const dsk_u8 kLegacyMagic[4] = { 'D', 'S', 'U', 'S' };
static const dsk_u16 kLegacyEndianLE = 0xFFFEu;
static const dsk_u32 kLegacyHeaderSize = 20u;

static dsk_status_t dsk_import_error(dsk_u16 code, dsk_u16 subcode) {
    return dsk_error_make(DSK_DOMAIN_KERNEL, code, subcode, DSK_ERROR_FLAG_USER_ACTIONABLE);
}

static dsk_u16 dsk_read_u16_le(const dsk_u8 *p) {
    return (dsk_u16)p[0] | (dsk_u16)((dsk_u16)p[1] << 8);
}

static dsk_u32 dsk_read_u32_le(const dsk_u8 *p) {
    return (dsk_u32)p[0]
         | ((dsk_u32)p[1] << 8)
         | ((dsk_u32)p[2] << 16)
         | ((dsk_u32)p[3] << 24);
}

static dsk_u32 dsk_header_checksum32_base(const dsk_u8 header_base[kLegacyHeaderSize]) {
    dsk_u32 sum = 0u;
    dsk_u32 i;
    if (!header_base) {
        return 0u;
    }
    for (i = 0u; i < (kLegacyHeaderSize - 4u); ++i) {
        sum += (dsk_u32)header_base[i];
    }
    return sum;
}

static dsk_status_t dsk_unwrap_legacy_payload(const dsk_u8 *data,
                                              dsk_u32 size,
                                              dsk_u16 *out_version,
                                              const dsk_u8 **out_payload,
                                              dsk_u32 *out_payload_len) {
    dsk_u16 version;
    dsk_u16 endian;
    dsk_u32 header_size;
    dsk_u32 payload_size;
    dsk_u32 checksum_stored;
    dsk_u32 checksum_calc;

    if (!data || !out_payload || !out_payload_len || !out_version) {
        return dsk_import_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (size < kLegacyHeaderSize) {
        return dsk_import_error(DSK_CODE_INTEGRITY_ERROR, DSK_SUBCODE_TLV_TRUNCATED);
    }
    if (std::memcmp(data, kLegacyMagic, 4u) != 0) {
        return dsk_import_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_TLV_BAD_MAGIC);
    }

    version = dsk_read_u16_le(data + 4u);
    endian = dsk_read_u16_le(data + 6u);
    header_size = dsk_read_u32_le(data + 8u);
    payload_size = dsk_read_u32_le(data + 12u);
    checksum_stored = dsk_read_u32_le(data + 16u);

    if (endian != kLegacyEndianLE) {
        return dsk_import_error(DSK_CODE_UNSUPPORTED_VERSION, DSK_SUBCODE_TLV_BAD_ENDIAN);
    }
    if (version == 0u || version > 2u) {
        return dsk_import_error(DSK_CODE_UNSUPPORTED_VERSION, DSK_SUBCODE_NONE);
    }
    if (header_size < kLegacyHeaderSize || header_size > size) {
        return dsk_import_error(DSK_CODE_INTEGRITY_ERROR, DSK_SUBCODE_TLV_BAD_HEADER_SIZE);
    }
    if (payload_size > (size - header_size)) {
        return dsk_import_error(DSK_CODE_INTEGRITY_ERROR, DSK_SUBCODE_TLV_BAD_PAYLOAD_SIZE);
    }

    checksum_calc = dsk_header_checksum32_base(data);
    if (checksum_calc != checksum_stored) {
        return dsk_import_error(DSK_CODE_INTEGRITY_ERROR, DSK_SUBCODE_TLV_BAD_CRC);
    }

    *out_version = version;
    *out_payload = data + header_size;
    *out_payload_len = payload_size;
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_parse_u8(const dsk_tlv_record_t &rec, dsk_u8 *out) {
    if (!out) {
        return dsk_import_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length != 1u) {
        return dsk_import_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }
    *out = rec.payload[0];
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static std::string dsk_parse_string(const dsk_tlv_record_t &rec) {
    if (!rec.payload || rec.length == 0u) {
        return std::string();
    }
    return std::string(reinterpret_cast<const char *>(rec.payload), rec.length);
}

static std::string dsk_scope_to_string(dsk_u16 scope) {
    switch (scope) {
    case DSK_INSTALL_SCOPE_USER: return "user";
    case DSK_INSTALL_SCOPE_SYSTEM: return "system";
    case DSK_INSTALL_SCOPE_PORTABLE: return "portable";
    default: return "unknown";
    }
}

static dsk_u16 dsk_map_scope(dsk_u8 legacy_scope) {
    switch (legacy_scope) {
    case 0u: return DSK_INSTALL_SCOPE_PORTABLE;
    case 1u: return DSK_INSTALL_SCOPE_USER;
    case 2u: return DSK_INSTALL_SCOPE_SYSTEM;
    default: return DSK_INSTALL_SCOPE_PORTABLE;
    }
}

static void dsk_sort_strings(std::vector<std::string> &values) {
    size_t i, j;
    for (i = 1u; i < values.size(); ++i) {
        std::string key = values[i];
        j = i;
        while (j > 0u) {
            const std::string &prev = values[j - 1u];
            if (!(prev > key)) {
                break;
            }
            values[j] = values[j - 1u];
            --j;
        }
        values[j] = key;
    }
}

static void dsk_normalize_lower_ascii(std::string &value) {
    size_t i;
    for (i = 0u; i < value.size(); ++i) {
        char c = value[i];
        if (c >= 'A' && c <= 'Z') {
            value[i] = (char)(c - 'A' + 'a');
        }
    }
}

static dsk_status_t dsk_parse_legacy_state_payload(const dsk_u8 *payload,
                                                   dsk_u32 payload_len,
                                                   dsk_u16 legacy_version,
                                                   dsk_installed_state_t *out_state,
                                                   std::string *out_platform,
                                                   std::vector<std::string> *out_details) {
    dsk_tlv_stream_t stream;
    dsk_tlv_stream_t root_stream;
    dsk_status_t st;
    const dsk_tlv_record_t *root;
    std::string product_id;
    std::string product_version;
    std::string build_channel;
    std::string platform;
    std::string install_root_fallback;
    std::vector<std::string> install_roots;
    std::string primary_root;
    std::vector<std::string> components;
    dsk_u8 legacy_scope = 0u;

    if (!out_state || !out_platform || !out_details) {
        return dsk_import_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }

    st = dsk_tlv_parse_stream(payload, payload_len, &stream);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    root = dsk_tlv_find_first(stream.records, stream.record_count, (dsk_u16)DSU_TLV_STATE_ROOT);
    if (!root) {
        dsk_tlv_stream_destroy(&stream);
        return dsk_import_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_MISSING_FIELD);
    }

    st = dsk_tlv_parse_stream(root->payload, root->length, &root_stream);
    if (!dsk_error_is_ok(st)) {
        dsk_tlv_stream_destroy(&stream);
        return st;
    }

    for (dsk_u32 i = 0u; i < root_stream.record_count; ++i) {
        const dsk_tlv_record_t &rec = root_stream.records[i];
        if (rec.type == DSU_TLV_STATE_PRODUCT_ID) {
            product_id = dsk_parse_string(rec);
        } else if (rec.type == DSU_TLV_STATE_PRODUCT_VERSION) {
            product_version = dsk_parse_string(rec);
        } else if (rec.type == DSU_TLV_STATE_BUILD_CHANNEL) {
            build_channel = dsk_parse_string(rec);
        } else if (rec.type == DSU_TLV_STATE_PLATFORM) {
            platform = dsk_parse_string(rec);
        } else if (rec.type == DSU_TLV_STATE_SCOPE) {
            (void)dsk_parse_u8(rec, &legacy_scope);
        } else if (rec.type == DSU_TLV_STATE_INSTALL_ROOT) {
            install_root_fallback = dsk_parse_string(rec);
        } else if (rec.type == DSU_TLV_STATE_INSTALL_ROOT_ITEM) {
            dsk_tlv_stream_t item_stream;
            std::string path;
            dsk_u8 role = 0u;
            if (dsk_error_is_ok(dsk_tlv_parse_stream(rec.payload, rec.length, &item_stream))) {
                for (dsk_u32 j = 0u; j < item_stream.record_count; ++j) {
                    const dsk_tlv_record_t &field = item_stream.records[j];
                    if (field.type == DSU_TLV_STATE_INSTALL_ROOT_ROLE) {
                        (void)dsk_parse_u8(field, &role);
                    } else if (field.type == DSU_TLV_STATE_INSTALL_ROOT_PATH) {
                        path = dsk_parse_string(field);
                    }
                }
                dsk_tlv_stream_destroy(&item_stream);
            }
            if (!path.empty()) {
                install_roots.push_back(path);
                if (role == 0u && primary_root.empty()) {
                    primary_root = path;
                }
            }
        } else if (rec.type == DSU_TLV_STATE_COMPONENT) {
            dsk_tlv_stream_t comp_stream;
            std::string id;
            if (dsk_error_is_ok(dsk_tlv_parse_stream(rec.payload, rec.length, &comp_stream))) {
                for (dsk_u32 j = 0u; j < comp_stream.record_count; ++j) {
                    const dsk_tlv_record_t &field = comp_stream.records[j];
                    if (field.type == DSU_TLV_STATE_COMPONENT_ID) {
                        id = dsk_parse_string(field);
                    }
                }
                dsk_tlv_stream_destroy(&comp_stream);
            }
            if (!id.empty()) {
                dsk_normalize_lower_ascii(id);
                components.push_back(id);
            }
        }
    }

    dsk_tlv_stream_destroy(&root_stream);
    dsk_tlv_stream_destroy(&stream);

    if (product_id.empty() || product_version.empty()) {
        return dsk_import_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_MISSING_FIELD);
    }

    if (primary_root.empty()) {
        if (!install_roots.empty()) {
            primary_root = install_roots[0];
        } else if (!install_root_fallback.empty()) {
            primary_root = install_root_fallback;
        }
    }
    if (install_roots.empty() && !primary_root.empty()) {
        install_roots.push_back(primary_root);
    }

    out_state->product_id = product_id;
    out_state->installed_version = product_version;
    out_state->selected_splat = "legacy-import";
    out_state->install_scope = dsk_map_scope(legacy_scope);
    out_state->install_root = primary_root;
    out_state->install_roots = install_roots;
    out_state->ownership = DSK_OWNERSHIP_PORTABLE;
    out_state->installed_components = components;
    out_state->manifest_digest64 = 0u;
    out_state->request_digest64 = 0u;
    out_state->previous_state_digest64 = 0u;

    dsk_sort_strings(out_state->installed_components);
    dsk_sort_strings(out_state->install_roots);

    *out_platform = platform;
    out_details->push_back(std::string("legacy_state_version=") + (legacy_version == 2u ? "2" : "1"));
    out_details->push_back(std::string("legacy_scope=") + dsk_scope_to_string(dsk_map_scope(legacy_scope)));
    out_details->push_back(std::string("mapped_scope=") + dsk_scope_to_string(out_state->install_scope));
    if (!platform.empty()) {
        out_details->push_back(std::string("legacy_platform=") + platform);
    }
    if (!build_channel.empty()) {
        out_details->push_back(std::string("legacy_build_channel=") + build_channel);
    }
    if (!primary_root.empty()) {
        out_details->push_back(std::string("primary_root=") + primary_root);
    }
    {
        char buf[64];
        std::snprintf(buf, sizeof(buf), "component_count=%u", (unsigned)components.size());
        out_details->push_back(buf);
    }
    dsk_sort_strings(*out_details);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
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

static dsk_status_t dsk_sink_write(const dsk_byte_sink_t *sink, const dsk_tlv_buffer_t *buf) {
    if (!sink || !sink->write || !buf) {
        return dsk_import_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    return sink->write(sink->user, buf->data, buf->size);
}

} // namespace

void dsk_import_request_init(dsk_import_request_t *req) {
    if (!req) {
        return;
    }
    req->services = 0;
    req->legacy_state_bytes = 0;
    req->legacy_state_size = 0u;
    req->out_state.user = 0;
    req->out_state.write = 0;
    req->out_audit.user = 0;
    req->out_audit.write = 0;
    req->deterministic_mode = 1u;
}

dsk_status_t dsk_import_legacy_state(const dsk_import_request_t *req) {
    dsk_audit_t audit;
    dsk_installed_state_t state;
    dsk_tlv_buffer_t state_buf;
    dsk_tlv_buffer_t audit_buf;
    dsk_status_t st;
    dsk_status_t ok = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    const dsk_u8 *payload = 0;
    dsk_u32 payload_len = 0u;
    dsk_u16 legacy_version = 0u;
    std::string platform;
    std::vector<std::string> details;

    if (!req || !req->legacy_state_bytes || req->legacy_state_size == 0u ||
        !req->out_state.write || !req->out_audit.write) {
        return dsk_import_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }

    dsk_audit_clear(&audit);
    dsk_installed_state_clear(&state);

    audit.run_id = dsk_generate_run_id(req->deterministic_mode);
    audit.operation = DSK_OPERATION_IMPORT_LEGACY;
    audit.result = ok;

    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_IMPORT_BEGIN, ok);

    st = dsk_unwrap_legacy_payload(req->legacy_state_bytes,
                                   req->legacy_state_size,
                                   &legacy_version,
                                   &payload,
                                   &payload_len);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_IMPORT_PARSE_FAIL, st);
        goto emit_audit;
    }

    st = dsk_parse_legacy_state_payload(payload,
                                        payload_len,
                                        legacy_version,
                                        &state,
                                        &platform,
                                        &details);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_IMPORT_PARSE_FAIL, st);
        goto emit_audit;
    }

    state.import_source = (legacy_version == 2u) ? "legacy_dsu_state_v2" : "legacy_dsu_state_v1";
    state.import_details = details;
    audit.import_source = state.import_source;
    audit.import_details = details;
    audit.platform_triple = platform;
    audit.selected_splat = state.selected_splat;
    audit.frontend_id = "import-legacy-state";

    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_IMPORT_PARSE_OK, ok);

    st = dsk_installed_state_write(&state, &state_buf);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_IMPORT_WRITE_STATE_FAIL, st);
        goto emit_audit;
    }
    st = dsk_sink_write(&req->out_state, &state_buf);
    dsk_tlv_buffer_free(&state_buf);
    if (!dsk_error_is_ok(st)) {
        audit.result = st;
        dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_IMPORT_WRITE_STATE_FAIL, st);
        goto emit_audit;
    }

    audit.result = ok;
    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_IMPORT_WRITE_STATE_OK, ok);

emit_audit:
    dsk_audit_add_event(&audit, DSK_AUDIT_EVENT_IMPORT_END, audit.result);
    st = dsk_audit_write(&audit, &audit_buf);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    {
        dsk_status_t wr = dsk_sink_write(&req->out_audit, &audit_buf);
        dsk_tlv_buffer_free(&audit_buf);
        if (!dsk_error_is_ok(wr)) {
            return wr;
        }
    }
    return audit.result;
}
