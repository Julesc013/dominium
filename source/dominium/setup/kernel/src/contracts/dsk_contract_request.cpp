#include "dsk/dsk_contracts.h"

#include <algorithm>
#include <string.h>

static dsk_status_t dsk_request_error(dsk_u16 code, dsk_u16 subcode) {
    return dsk_error_make(DSK_DOMAIN_KERNEL, code, subcode, DSK_ERROR_FLAG_USER_ACTIONABLE);
}

static dsk_status_t dsk_parse_string(const dsk_tlv_record_t &rec, std::string *out) {
    if (!out) {
        return dsk_request_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    out->assign(reinterpret_cast<const char *>(rec.payload), rec.length);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_parse_u16(const dsk_tlv_record_t &rec, dsk_u16 *out) {
    if (!out) {
        return dsk_request_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length != 2u) {
        return dsk_request_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }
    *out = (dsk_u16)rec.payload[0] | (dsk_u16)((dsk_u16)rec.payload[1] << 8);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_parse_u32(const dsk_tlv_record_t &rec, dsk_u32 *out) {
    if (!out) {
        return dsk_request_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length != 4u) {
        return dsk_request_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }
    *out = (dsk_u32)rec.payload[0]
         | ((dsk_u32)rec.payload[1] << 8)
         | ((dsk_u32)rec.payload[2] << 16)
         | ((dsk_u32)rec.payload[3] << 24);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

void dsk_request_clear(dsk_request_t *request) {
    if (!request) {
        return;
    }
    request->operation = 0u;
    request->requested_components.clear();
    request->excluded_components.clear();
    request->install_scope = 0u;
    request->preferred_install_root.clear();
    request->payload_root.clear();
    request->ui_mode = 0u;
    request->frontend_id.clear();
    request->requested_splat_id.clear();
    request->policy_flags = 0u;
    request->required_caps = 0u;
    request->prohibited_caps = 0u;
    request->ownership_preference = DSK_OWNERSHIP_ANY;
    request->target_platform_triple.clear();
}

dsk_status_t dsk_request_parse(const dsk_u8 *data,
                               dsk_u32 size,
                               dsk_request_t *out_request) {
    dsk_tlv_view_t view;
    dsk_status_t st;
    dsk_u32 i;
    dsk_bool has_operation = DSK_FALSE;
    dsk_bool has_scope = DSK_FALSE;
    dsk_bool has_ui = DSK_FALSE;
    dsk_bool has_policy = DSK_FALSE;
    dsk_bool has_platform = DSK_FALSE;
    dsk_bool has_frontend = DSK_FALSE;

    if (!out_request) {
        return dsk_request_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    dsk_request_clear(out_request);

    st = dsk_tlv_parse(data, size, &view);
    if (!dsk_error_is_ok(st)) {
        return st;
    }

    for (i = 0u; i < view.record_count; ++i) {
        const dsk_tlv_record_t &rec = view.records[i];
        if (rec.type == DSK_TLV_TAG_REQUEST_OPERATION) {
            st = dsk_parse_u16(rec, &out_request->operation);
            has_operation = dsk_error_is_ok(st) ? DSK_TRUE : has_operation;
        } else if (rec.type == DSK_TLV_TAG_REQUEST_INSTALL_SCOPE) {
            st = dsk_parse_u16(rec, &out_request->install_scope);
            has_scope = dsk_error_is_ok(st) ? DSK_TRUE : has_scope;
        } else if (rec.type == DSK_TLV_TAG_REQUEST_UI_MODE) {
            st = dsk_parse_u16(rec, &out_request->ui_mode);
            has_ui = dsk_error_is_ok(st) ? DSK_TRUE : has_ui;
        } else if (rec.type == DSK_TLV_TAG_REQUEST_POLICY_FLAGS) {
            st = dsk_parse_u32(rec, &out_request->policy_flags);
            has_policy = dsk_error_is_ok(st) ? DSK_TRUE : has_policy;
        } else if (rec.type == DSK_TLV_TAG_REQUEST_TARGET_PLATFORM_TRIPLE) {
            st = dsk_parse_string(rec, &out_request->target_platform_triple);
            has_platform = dsk_error_is_ok(st) ? DSK_TRUE : has_platform;
        } else if (rec.type == DSK_TLV_TAG_REQUEST_FRONTEND_ID) {
            st = dsk_parse_string(rec, &out_request->frontend_id);
            has_frontend = dsk_error_is_ok(st) ? DSK_TRUE : has_frontend;
        } else if (rec.type == DSK_TLV_TAG_REQUEST_PREFERRED_INSTALL_ROOT) {
            st = dsk_parse_string(rec, &out_request->preferred_install_root);
        } else if (rec.type == DSK_TLV_TAG_REQUEST_PAYLOAD_ROOT) {
            st = dsk_parse_string(rec, &out_request->payload_root);
        } else if (rec.type == DSK_TLV_TAG_REQUEST_REQUESTED_SPLAT_ID) {
            st = dsk_parse_string(rec, &out_request->requested_splat_id);
        } else if (rec.type == DSK_TLV_TAG_REQUEST_REQUIRED_CAPS) {
            st = dsk_parse_u32(rec, &out_request->required_caps);
        } else if (rec.type == DSK_TLV_TAG_REQUEST_PROHIBITED_CAPS) {
            st = dsk_parse_u32(rec, &out_request->prohibited_caps);
        } else if (rec.type == DSK_TLV_TAG_REQUEST_OWNERSHIP_PREFERENCE) {
            st = dsk_parse_u16(rec, &out_request->ownership_preference);
        } else if (rec.type == DSK_TLV_TAG_REQUEST_REQUESTED_COMPONENTS ||
                   rec.type == DSK_TLV_TAG_REQUEST_EXCLUDED_COMPONENTS) {
            dsk_tlv_stream_t list_stream;
            dsk_status_t lst;
            dsk_u32 j;

            lst = dsk_tlv_parse_stream(rec.payload, rec.length, &list_stream);
            if (!dsk_error_is_ok(lst)) {
                dsk_tlv_view_destroy(&view);
                return lst;
            }

            {
                const dsk_u16 entry_tag = (rec.type == DSK_TLV_TAG_REQUEST_REQUESTED_COMPONENTS)
                                          ? DSK_TLV_TAG_REQUESTED_COMPONENT_ENTRY
                                          : DSK_TLV_TAG_EXCLUDED_COMPONENT_ENTRY;
                for (j = 0u; j < list_stream.record_count; ++j) {
                    const dsk_tlv_record_t &entry = list_stream.records[j];
                    if (entry.type != entry_tag) {
                        continue;
                    }
                    std::string value;
                    lst = dsk_parse_string(entry, &value);
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_view_destroy(&view);
                        return lst;
                    }
                    if (rec.type == DSK_TLV_TAG_REQUEST_REQUESTED_COMPONENTS) {
                        out_request->requested_components.push_back(value);
                    } else {
                        out_request->excluded_components.push_back(value);
                    }
                }
            }

            dsk_tlv_stream_destroy(&list_stream);
            st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        } else {
            continue;
        }

        if (!dsk_error_is_ok(st)) {
            dsk_tlv_view_destroy(&view);
            return st;
        }
    }

    dsk_tlv_view_destroy(&view);

    if (!has_operation || !has_scope || !has_ui || !has_policy || !has_platform || !has_frontend ||
        out_request->operation == 0u ||
        out_request->install_scope == 0u ||
        out_request->ui_mode == 0u ||
        out_request->target_platform_triple.empty() ||
        out_request->frontend_id.empty()) {
        return dsk_request_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_MISSING_FIELD);
    }

    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static bool dsk_string_less(const std::string &a, const std::string &b) {
    return a < b;
}

dsk_status_t dsk_request_write(const dsk_request_t *request,
                               dsk_tlv_buffer_t *out_buf) {
    dsk_tlv_builder_t *builder;
    dsk_status_t st;
    std::vector<std::string> requested;
    std::vector<std::string> excluded;
    dsk_u32 i;

    if (!request || !out_buf) {
        return dsk_request_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }

    builder = dsk_tlv_builder_create();
    if (!builder) {
        return dsk_request_error(DSK_CODE_INTERNAL_ERROR, DSK_SUBCODE_NONE);
    }

    st = dsk_tlv_builder_add_u16(builder, DSK_TLV_TAG_REQUEST_OPERATION, request->operation);
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_u16(builder, DSK_TLV_TAG_REQUEST_INSTALL_SCOPE, request->install_scope);
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_u16(builder, DSK_TLV_TAG_REQUEST_UI_MODE, request->ui_mode);
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_u32(builder, DSK_TLV_TAG_REQUEST_POLICY_FLAGS, request->policy_flags);
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_string(builder,
                                    DSK_TLV_TAG_REQUEST_TARGET_PLATFORM_TRIPLE,
                                    request->target_platform_triple.c_str());
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_string(builder,
                                    DSK_TLV_TAG_REQUEST_FRONTEND_ID,
                                    request->frontend_id.c_str());
    if (!dsk_error_is_ok(st)) goto done;

    if (!request->preferred_install_root.empty()) {
        st = dsk_tlv_builder_add_string(builder,
                                        DSK_TLV_TAG_REQUEST_PREFERRED_INSTALL_ROOT,
                                        request->preferred_install_root.c_str());
        if (!dsk_error_is_ok(st)) goto done;
    }
    if (!request->payload_root.empty()) {
        st = dsk_tlv_builder_add_string(builder,
                                        DSK_TLV_TAG_REQUEST_PAYLOAD_ROOT,
                                        request->payload_root.c_str());
        if (!dsk_error_is_ok(st)) goto done;
    }
    if (!request->requested_splat_id.empty()) {
        st = dsk_tlv_builder_add_string(builder,
                                        DSK_TLV_TAG_REQUEST_REQUESTED_SPLAT_ID,
                                        request->requested_splat_id.c_str());
        if (!dsk_error_is_ok(st)) goto done;
    }
    if (request->required_caps != 0u) {
        st = dsk_tlv_builder_add_u32(builder,
                                     DSK_TLV_TAG_REQUEST_REQUIRED_CAPS,
                                     request->required_caps);
        if (!dsk_error_is_ok(st)) goto done;
    }
    if (request->prohibited_caps != 0u) {
        st = dsk_tlv_builder_add_u32(builder,
                                     DSK_TLV_TAG_REQUEST_PROHIBITED_CAPS,
                                     request->prohibited_caps);
        if (!dsk_error_is_ok(st)) goto done;
    }
    if (request->ownership_preference != DSK_OWNERSHIP_ANY) {
        st = dsk_tlv_builder_add_u16(builder,
                                     DSK_TLV_TAG_REQUEST_OWNERSHIP_PREFERENCE,
                                     request->ownership_preference);
        if (!dsk_error_is_ok(st)) goto done;
    }

    requested = request->requested_components;
    excluded = request->excluded_components;
    std::sort(requested.begin(), requested.end(), dsk_string_less);
    std::sort(excluded.begin(), excluded.end(), dsk_string_less);

    if (!requested.empty()) {
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;
        for (i = 0u; i < requested.size(); ++i) {
            dsk_tlv_builder_add_string(list_builder,
                                       DSK_TLV_TAG_REQUESTED_COMPONENT_ENTRY,
                                       requested[i].c_str());
        }
        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) goto done;
        st = dsk_tlv_builder_add_container(builder,
                                           DSK_TLV_TAG_REQUEST_REQUESTED_COMPONENTS,
                                           list_payload.data,
                                           list_payload.size);
        dsk_tlv_buffer_free(&list_payload);
        if (!dsk_error_is_ok(st)) goto done;
    }

    if (!excluded.empty()) {
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;
        for (i = 0u; i < excluded.size(); ++i) {
            dsk_tlv_builder_add_string(list_builder,
                                       DSK_TLV_TAG_EXCLUDED_COMPONENT_ENTRY,
                                       excluded[i].c_str());
        }
        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) goto done;
        st = dsk_tlv_builder_add_container(builder,
                                           DSK_TLV_TAG_REQUEST_EXCLUDED_COMPONENTS,
                                           list_payload.data,
                                           list_payload.size);
        dsk_tlv_buffer_free(&list_payload);
        if (!dsk_error_is_ok(st)) goto done;
    }

    st = dsk_tlv_builder_finalize(builder, out_buf);

done:
    dsk_tlv_builder_destroy(builder);
    return st;
}
