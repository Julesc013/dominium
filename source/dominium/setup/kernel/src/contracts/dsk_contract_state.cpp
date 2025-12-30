#include "dsk/dsk_contracts.h"

#include <algorithm>

static dsk_status_t dsk_state_error(dsk_u16 code, dsk_u16 subcode) {
    return dsk_error_make(DSK_DOMAIN_KERNEL, code, subcode, DSK_ERROR_FLAG_USER_ACTIONABLE);
}

static dsk_status_t dsk_state_parse_string(const dsk_tlv_record_t &rec, std::string *out) {
    if (!out) {
        return dsk_state_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    out->assign(reinterpret_cast<const char *>(rec.payload), rec.length);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_state_parse_u16(const dsk_tlv_record_t &rec, dsk_u16 *out) {
    if (!out) {
        return dsk_state_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length != 2u) {
        return dsk_state_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }
    *out = (dsk_u16)rec.payload[0] | (dsk_u16)((dsk_u16)rec.payload[1] << 8);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_state_parse_u32(const dsk_tlv_record_t &rec, dsk_u32 *out) {
    if (!out) {
        return dsk_state_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length != 4u) {
        return dsk_state_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }
    *out = (dsk_u32)rec.payload[0]
         | ((dsk_u32)rec.payload[1] << 8)
         | ((dsk_u32)rec.payload[2] << 16)
         | ((dsk_u32)rec.payload[3] << 24);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_state_parse_u64(const dsk_tlv_record_t &rec, dsk_u64 *out) {
    if (!out) {
        return dsk_state_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length != 8u) {
        return dsk_state_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }
    *out = (dsk_u64)rec.payload[0]
         | ((dsk_u64)rec.payload[1] << 8)
         | ((dsk_u64)rec.payload[2] << 16)
         | ((dsk_u64)rec.payload[3] << 24)
         | ((dsk_u64)rec.payload[4] << 32)
         | ((dsk_u64)rec.payload[5] << 40)
         | ((dsk_u64)rec.payload[6] << 48)
         | ((dsk_u64)rec.payload[7] << 56);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

void dsk_installed_state_clear(dsk_installed_state_t *state) {
    if (!state) {
        return;
    }
    state->product_id.clear();
    state->installed_version.clear();
    state->selected_splat.clear();
    state->install_scope = 0u;
    state->install_root.clear();
    state->install_roots.clear();
    state->ownership = DSK_OWNERSHIP_ANY;
    state->installed_components.clear();
    state->artifacts.clear();
    state->registrations.clear();
    state->manifest_digest64 = 0u;
    state->request_digest64 = 0u;
    state->previous_state_digest64 = 0u;
}

static dsk_status_t dsk_state_parse_artifact(const dsk_tlv_record_t &rec,
                                             dsk_state_artifact_t *out_artifact) {
    dsk_tlv_stream_t stream;
    dsk_status_t st;
    dsk_u32 i;

    if (!out_artifact) {
        return dsk_state_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    out_artifact->target_root_id = 0u;
    out_artifact->path.clear();
    out_artifact->digest64 = 0u;
    out_artifact->size = 0u;

    st = dsk_tlv_parse_stream(rec.payload, rec.length, &stream);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    for (i = 0u; i < stream.record_count; ++i) {
        const dsk_tlv_record_t &field = stream.records[i];
        if (field.type == DSK_TLV_TAG_STATE_ARTIFACT_ROOT_ID) {
            st = dsk_state_parse_u32(field, &out_artifact->target_root_id);
        } else if (field.type == DSK_TLV_TAG_STATE_ARTIFACT_PATH) {
            st = dsk_state_parse_string(field, &out_artifact->path);
        } else if (field.type == DSK_TLV_TAG_STATE_ARTIFACT_DIGEST64) {
            st = dsk_state_parse_u64(field, &out_artifact->digest64);
        } else if (field.type == DSK_TLV_TAG_STATE_ARTIFACT_SIZE) {
            st = dsk_state_parse_u64(field, &out_artifact->size);
        } else {
            continue;
        }
        if (!dsk_error_is_ok(st)) {
            dsk_tlv_stream_destroy(&stream);
            return st;
        }
    }
    dsk_tlv_stream_destroy(&stream);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_state_parse_registration(const dsk_tlv_record_t &rec,
                                                 dsk_state_registration_t *out_reg) {
    dsk_tlv_stream_t stream;
    dsk_status_t st;
    dsk_u32 i;

    if (!out_reg) {
        return dsk_state_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    out_reg->kind = 0u;
    out_reg->status = 0u;
    out_reg->value.clear();

    st = dsk_tlv_parse_stream(rec.payload, rec.length, &stream);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    for (i = 0u; i < stream.record_count; ++i) {
        const dsk_tlv_record_t &field = stream.records[i];
        if (field.type == DSK_TLV_TAG_STATE_REG_KIND) {
            st = dsk_state_parse_u16(field, &out_reg->kind);
        } else if (field.type == DSK_TLV_TAG_STATE_REG_STATUS) {
            st = dsk_state_parse_u16(field, &out_reg->status);
        } else if (field.type == DSK_TLV_TAG_STATE_REG_VALUE) {
            st = dsk_state_parse_string(field, &out_reg->value);
        } else {
            continue;
        }
        if (!dsk_error_is_ok(st)) {
            dsk_tlv_stream_destroy(&stream);
            return st;
        }
    }
    dsk_tlv_stream_destroy(&stream);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

dsk_status_t dsk_installed_state_parse(const dsk_u8 *data,
                                       dsk_u32 size,
                                       dsk_installed_state_t *out_state) {
    dsk_tlv_view_t view;
    dsk_status_t st;
    dsk_u32 i;
    dsk_bool has_product = DSK_FALSE;
    dsk_bool has_version = DSK_FALSE;
    dsk_bool has_splat = DSK_FALSE;
    dsk_bool has_scope = DSK_FALSE;
    dsk_bool has_root = DSK_FALSE;
    dsk_bool has_manifest = DSK_FALSE;
    dsk_bool has_request = DSK_FALSE;

    if (!out_state) {
        return dsk_state_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    dsk_installed_state_clear(out_state);

    st = dsk_tlv_parse(data, size, &view);
    if (!dsk_error_is_ok(st)) {
        return st;
    }

    for (i = 0u; i < view.record_count; ++i) {
        const dsk_tlv_record_t &rec = view.records[i];
        if (rec.type == DSK_TLV_TAG_STATE_PRODUCT_ID) {
            st = dsk_state_parse_string(rec, &out_state->product_id);
            has_product = dsk_error_is_ok(st) ? DSK_TRUE : has_product;
        } else if (rec.type == DSK_TLV_TAG_STATE_INSTALLED_VERSION) {
            st = dsk_state_parse_string(rec, &out_state->installed_version);
            has_version = dsk_error_is_ok(st) ? DSK_TRUE : has_version;
        } else if (rec.type == DSK_TLV_TAG_STATE_SELECTED_SPLAT) {
            st = dsk_state_parse_string(rec, &out_state->selected_splat);
            has_splat = dsk_error_is_ok(st) ? DSK_TRUE : has_splat;
        } else if (rec.type == DSK_TLV_TAG_STATE_INSTALL_SCOPE) {
            st = dsk_state_parse_u16(rec, &out_state->install_scope);
            has_scope = dsk_error_is_ok(st) ? DSK_TRUE : has_scope;
        } else if (rec.type == DSK_TLV_TAG_STATE_INSTALL_ROOT) {
            st = dsk_state_parse_string(rec, &out_state->install_root);
            has_root = dsk_error_is_ok(st) ? DSK_TRUE : has_root;
        } else if (rec.type == DSK_TLV_TAG_STATE_MANIFEST_DIGEST64) {
            st = dsk_state_parse_u64(rec, &out_state->manifest_digest64);
            has_manifest = dsk_error_is_ok(st) ? DSK_TRUE : has_manifest;
        } else if (rec.type == DSK_TLV_TAG_STATE_REQUEST_DIGEST64) {
            st = dsk_state_parse_u64(rec, &out_state->request_digest64);
            has_request = dsk_error_is_ok(st) ? DSK_TRUE : has_request;
        } else if (rec.type == DSK_TLV_TAG_STATE_PREV_STATE_DIGEST64) {
            st = dsk_state_parse_u64(rec, &out_state->previous_state_digest64);
        } else if (rec.type == DSK_TLV_TAG_STATE_OWNERSHIP) {
            st = dsk_state_parse_u16(rec, &out_state->ownership);
        } else if (rec.type == DSK_TLV_TAG_STATE_INSTALLED_COMPONENTS ||
                   rec.type == DSK_TLV_TAG_STATE_INSTALL_ROOTS) {
            dsk_tlv_stream_t list_stream;
            dsk_status_t lst;
            dsk_u32 j;
            lst = dsk_tlv_parse_stream(rec.payload, rec.length, &list_stream);
            if (!dsk_error_is_ok(lst)) {
                dsk_tlv_view_destroy(&view);
                return lst;
            }
            {
                const dsk_u16 entry_tag = (rec.type == DSK_TLV_TAG_STATE_INSTALLED_COMPONENTS)
                                          ? DSK_TLV_TAG_STATE_COMPONENT_ENTRY
                                          : DSK_TLV_TAG_STATE_INSTALL_ROOT_ENTRY;
                for (j = 0u; j < list_stream.record_count; ++j) {
                    const dsk_tlv_record_t &entry = list_stream.records[j];
                    if (entry.type != entry_tag) {
                        continue;
                    }
                    std::string value;
                    lst = dsk_state_parse_string(entry, &value);
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_view_destroy(&view);
                        return lst;
                    }
                    if (rec.type == DSK_TLV_TAG_STATE_INSTALLED_COMPONENTS) {
                        out_state->installed_components.push_back(value);
                    } else {
                        out_state->install_roots.push_back(value);
                    }
                }
            }
            dsk_tlv_stream_destroy(&list_stream);
            st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        } else if (rec.type == DSK_TLV_TAG_STATE_ARTIFACTS) {
            dsk_tlv_stream_t list_stream;
            dsk_status_t lst;
            dsk_u32 j;
            lst = dsk_tlv_parse_stream(rec.payload, rec.length, &list_stream);
            if (!dsk_error_is_ok(lst)) {
                dsk_tlv_view_destroy(&view);
                return lst;
            }
            for (j = 0u; j < list_stream.record_count; ++j) {
                const dsk_tlv_record_t &entry = list_stream.records[j];
                if (entry.type != DSK_TLV_TAG_STATE_ARTIFACT_ENTRY) {
                    continue;
                }
                dsk_state_artifact_t art;
                lst = dsk_state_parse_artifact(entry, &art);
                if (!dsk_error_is_ok(lst)) {
                    dsk_tlv_stream_destroy(&list_stream);
                    dsk_tlv_view_destroy(&view);
                    return lst;
                }
                out_state->artifacts.push_back(art);
            }
            dsk_tlv_stream_destroy(&list_stream);
            st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        } else if (rec.type == DSK_TLV_TAG_STATE_REGISTRATIONS) {
            dsk_tlv_stream_t list_stream;
            dsk_status_t lst;
            dsk_u32 j;
            lst = dsk_tlv_parse_stream(rec.payload, rec.length, &list_stream);
            if (!dsk_error_is_ok(lst)) {
                dsk_tlv_view_destroy(&view);
                return lst;
            }
            for (j = 0u; j < list_stream.record_count; ++j) {
                const dsk_tlv_record_t &entry = list_stream.records[j];
                if (entry.type != DSK_TLV_TAG_STATE_REG_ENTRY) {
                    continue;
                }
                dsk_state_registration_t reg;
                lst = dsk_state_parse_registration(entry, &reg);
                if (!dsk_error_is_ok(lst)) {
                    dsk_tlv_stream_destroy(&list_stream);
                    dsk_tlv_view_destroy(&view);
                    return lst;
                }
                out_state->registrations.push_back(reg);
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

    if (!has_product || !has_version || !has_splat || !has_scope || !has_root ||
        !has_manifest || !has_request ||
        out_state->product_id.empty() || out_state->installed_version.empty() ||
        out_state->selected_splat.empty() || out_state->install_scope == 0u) {
        return dsk_state_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_MISSING_FIELD);
    }

    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static bool dsk_string_less(const std::string &a, const std::string &b) {
    return a < b;
}

static bool dsk_artifact_less(const dsk_state_artifact_t &a,
                              const dsk_state_artifact_t &b) {
    if (a.target_root_id != b.target_root_id) {
        return a.target_root_id < b.target_root_id;
    }
    return a.path < b.path;
}

static bool dsk_registration_less(const dsk_state_registration_t &a,
                                  const dsk_state_registration_t &b) {
    if (a.kind != b.kind) {
        return a.kind < b.kind;
    }
    if (a.value != b.value) {
        return a.value < b.value;
    }
    return a.status < b.status;
}

dsk_status_t dsk_installed_state_write(const dsk_installed_state_t *state,
                                       dsk_tlv_buffer_t *out_buf) {
    dsk_tlv_builder_t *builder;
    dsk_status_t st;
    std::vector<std::string> components;
    std::vector<std::string> roots;
    std::vector<dsk_state_artifact_t> artifacts;
    std::vector<dsk_state_registration_t> registrations;
    dsk_u32 i;

    if (!state || !out_buf) {
        return dsk_state_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }

    builder = dsk_tlv_builder_create();
    if (!builder) {
        return dsk_state_error(DSK_CODE_INTERNAL_ERROR, DSK_SUBCODE_NONE);
    }

    st = dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_STATE_PRODUCT_ID, state->product_id.c_str());
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_STATE_INSTALLED_VERSION, state->installed_version.c_str());
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_STATE_SELECTED_SPLAT, state->selected_splat.c_str());
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_u16(builder, DSK_TLV_TAG_STATE_INSTALL_SCOPE, state->install_scope);
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_STATE_INSTALL_ROOT, state->install_root.c_str());
    if (!dsk_error_is_ok(st)) goto done;
    if (!state->install_roots.empty()) {
        roots = state->install_roots;
        std::sort(roots.begin(), roots.end(), dsk_string_less);
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;
        for (i = 0u; i < roots.size(); ++i) {
            dsk_tlv_builder_add_string(list_builder,
                                       DSK_TLV_TAG_STATE_INSTALL_ROOT_ENTRY,
                                       roots[i].c_str());
        }
        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) goto done;
        st = dsk_tlv_builder_add_container(builder,
                                           DSK_TLV_TAG_STATE_INSTALL_ROOTS,
                                           list_payload.data,
                                           list_payload.size);
        dsk_tlv_buffer_free(&list_payload);
        if (!dsk_error_is_ok(st)) goto done;
    }
    st = dsk_tlv_builder_add_u16(builder, DSK_TLV_TAG_STATE_OWNERSHIP, state->ownership);
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_u64(builder, DSK_TLV_TAG_STATE_MANIFEST_DIGEST64, state->manifest_digest64);
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_u64(builder, DSK_TLV_TAG_STATE_REQUEST_DIGEST64, state->request_digest64);
    if (!dsk_error_is_ok(st)) goto done;
    if (state->previous_state_digest64 != 0u) {
        st = dsk_tlv_builder_add_u64(builder,
                                     DSK_TLV_TAG_STATE_PREV_STATE_DIGEST64,
                                     state->previous_state_digest64);
        if (!dsk_error_is_ok(st)) goto done;
    }

    components = state->installed_components;
    std::sort(components.begin(), components.end(), dsk_string_less);
    if (!components.empty()) {
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;
        for (i = 0u; i < components.size(); ++i) {
            dsk_tlv_builder_add_string(list_builder, DSK_TLV_TAG_STATE_COMPONENT_ENTRY, components[i].c_str());
        }
        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) goto done;
        st = dsk_tlv_builder_add_container(builder,
                                           DSK_TLV_TAG_STATE_INSTALLED_COMPONENTS,
                                           list_payload.data,
                                           list_payload.size);
        dsk_tlv_buffer_free(&list_payload);
        if (!dsk_error_is_ok(st)) goto done;
    }

    artifacts = state->artifacts;
    std::sort(artifacts.begin(), artifacts.end(), dsk_artifact_less);
    if (!artifacts.empty()) {
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;
        for (i = 0u; i < artifacts.size(); ++i) {
            const dsk_state_artifact_t &art = artifacts[i];
            dsk_tlv_builder_t *entry_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t entry_payload;
            dsk_tlv_builder_add_u32(entry_builder,
                                    DSK_TLV_TAG_STATE_ARTIFACT_ROOT_ID,
                                    art.target_root_id);
            dsk_tlv_builder_add_string(entry_builder,
                                       DSK_TLV_TAG_STATE_ARTIFACT_PATH,
                                       art.path.c_str());
            dsk_tlv_builder_add_u64(entry_builder,
                                    DSK_TLV_TAG_STATE_ARTIFACT_DIGEST64,
                                    art.digest64);
            dsk_tlv_builder_add_u64(entry_builder,
                                    DSK_TLV_TAG_STATE_ARTIFACT_SIZE,
                                    art.size);
            st = dsk_tlv_builder_finalize_payload(entry_builder, &entry_payload);
            dsk_tlv_builder_destroy(entry_builder);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(list_builder);
                goto done;
            }
            dsk_tlv_builder_add_container(list_builder,
                                          DSK_TLV_TAG_STATE_ARTIFACT_ENTRY,
                                          entry_payload.data,
                                          entry_payload.size);
            dsk_tlv_buffer_free(&entry_payload);
        }
        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) goto done;
        st = dsk_tlv_builder_add_container(builder,
                                           DSK_TLV_TAG_STATE_ARTIFACTS,
                                           list_payload.data,
                                           list_payload.size);
        dsk_tlv_buffer_free(&list_payload);
        if (!dsk_error_is_ok(st)) goto done;
    }

    registrations = state->registrations;
    std::sort(registrations.begin(), registrations.end(), dsk_registration_less);
    if (!registrations.empty()) {
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;
        for (i = 0u; i < registrations.size(); ++i) {
            const dsk_state_registration_t &reg = registrations[i];
            dsk_tlv_builder_t *entry_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t entry_payload;
            dsk_tlv_builder_add_u16(entry_builder,
                                    DSK_TLV_TAG_STATE_REG_KIND,
                                    reg.kind);
            dsk_tlv_builder_add_string(entry_builder,
                                       DSK_TLV_TAG_STATE_REG_VALUE,
                                       reg.value.c_str());
            dsk_tlv_builder_add_u16(entry_builder,
                                    DSK_TLV_TAG_STATE_REG_STATUS,
                                    reg.status);
            st = dsk_tlv_builder_finalize_payload(entry_builder, &entry_payload);
            dsk_tlv_builder_destroy(entry_builder);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(list_builder);
                goto done;
            }
            dsk_tlv_builder_add_container(list_builder,
                                          DSK_TLV_TAG_STATE_REG_ENTRY,
                                          entry_payload.data,
                                          entry_payload.size);
            dsk_tlv_buffer_free(&entry_payload);
        }
        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) goto done;
        st = dsk_tlv_builder_add_container(builder,
                                           DSK_TLV_TAG_STATE_REGISTRATIONS,
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
