/*
FILE: source/dominium/common/core_installed_state.cpp
MODULE: Dominium
PURPOSE: Canonical installed_state.tlv parsing/writing (shared by setup + launcher).
*/

#include "dominium/core_installed_state.h"

#include <algorithm>

namespace dom {
namespace core_installed_state {

static err_t state_err_invalid_args(void) {
    return err_make((u16)ERRD_COMMON,
                    (u16)ERRC_COMMON_INVALID_ARGS,
                    (u32)ERRF_FATAL,
                    (u32)ERRMSG_COMMON_INVALID_ARGS);
}

static err_t state_err_parse(u16 subcode) {
    err_t err = err_make((u16)ERRD_TLV,
                         (u16)ERRC_TLV_PARSE_FAILED,
                         (u32)ERRF_INTEGRITY,
                         (u32)ERRMSG_TLV_PARSE_FAILED);
    if (subcode != 0u) {
        err_add_detail_u32(&err, (u32)ERR_DETAIL_KEY_SUBCODE, (u32)subcode);
    }
    return err;
}

static err_t state_err_missing_field(u32 field_tag) {
    err_t err = err_make((u16)ERRD_TLV,
                         (u16)ERRC_TLV_MISSING_FIELD,
                         (u32)ERRF_INTEGRITY,
                         (u32)ERRMSG_TLV_MISSING_FIELD);
    err_add_detail_u32(&err, (u32)ERR_DETAIL_KEY_SUBCODE, (u32)CORE_TLV_SUBCODE_MISSING_FIELD);
    if (field_tag != 0u) {
        err_add_detail_u32(&err, (u32)ERR_DETAIL_KEY_REQUIRED_FIELD, field_tag);
    }
    return err;
}

static err_t parse_string(const core_tlv_framed_record_t& rec, std::string* out) {
    if (!out) {
        return state_err_invalid_args();
    }
    out->assign(reinterpret_cast<const char*>(rec.payload), rec.length);
    return err_ok();
}

static err_t parse_u16(const core_tlv_framed_record_t& rec, u16* out) {
    if (!out) {
        return state_err_invalid_args();
    }
    if (rec.length != 2u) {
        return state_err_parse((u16)CORE_TLV_SUBCODE_INVALID_FIELD);
    }
    *out = (u16)rec.payload[0] | (u16)((u16)rec.payload[1] << 8);
    return err_ok();
}

static err_t parse_u32(const core_tlv_framed_record_t& rec, u32* out) {
    if (!out) {
        return state_err_invalid_args();
    }
    if (rec.length != 4u) {
        return state_err_parse((u16)CORE_TLV_SUBCODE_INVALID_FIELD);
    }
    *out = (u32)rec.payload[0]
         | ((u32)rec.payload[1] << 8)
         | ((u32)rec.payload[2] << 16)
         | ((u32)rec.payload[3] << 24);
    return err_ok();
}

static err_t parse_u64(const core_tlv_framed_record_t& rec, u64* out) {
    if (!out) {
        return state_err_invalid_args();
    }
    if (rec.length != 8u) {
        return state_err_parse((u16)CORE_TLV_SUBCODE_INVALID_FIELD);
    }
    *out = (u64)rec.payload[0]
         | ((u64)rec.payload[1] << 8)
         | ((u64)rec.payload[2] << 16)
         | ((u64)rec.payload[3] << 24)
         | ((u64)rec.payload[4] << 32)
         | ((u64)rec.payload[5] << 40)
         | ((u64)rec.payload[6] << 48)
         | ((u64)rec.payload[7] << 56);
    return err_ok();
}

void installed_state_clear(InstalledState* state) {
    if (!state) {
        return;
    }
    state->product_id.clear();
    state->installed_version.clear();
    state->selected_splat.clear();
    state->install_scope = 0u;
    state->install_root.clear();
    state->install_roots.clear();
    state->ownership = 0u;
    state->installed_components.clear();
    state->artifacts.clear();
    state->registrations.clear();
    state->manifest_digest64 = 0u;
    state->request_digest64 = 0u;
    state->previous_state_digest64 = 0u;
    state->import_source.clear();
    state->import_details.clear();
    state->state_version = 0u;
    state->migration_applied.clear();
}

static err_t parse_artifact(const core_tlv_framed_record_t& rec,
                            InstalledStateArtifact* out_artifact) {
    core_tlv_framed_stream_t stream;
    err_t st;
    u32 i;

    if (!out_artifact) {
        return state_err_invalid_args();
    }
    out_artifact->target_root_id = 0u;
    out_artifact->path.clear();
    out_artifact->digest64 = 0u;
    out_artifact->size = 0u;

    st = core_tlv_framed_parse_stream(rec.payload, rec.length, &stream);
    if (!err_is_ok(&st)) {
        return st;
    }
    for (i = 0u; i < stream.record_count; ++i) {
        const core_tlv_framed_record_t& field = stream.records[i];
        if (field.type == CORE_TLV_TAG_INSTALLED_STATE_ARTIFACT_ROOT_ID) {
            st = parse_u32(field, &out_artifact->target_root_id);
        } else if (field.type == CORE_TLV_TAG_INSTALLED_STATE_ARTIFACT_PATH) {
            st = parse_string(field, &out_artifact->path);
        } else if (field.type == CORE_TLV_TAG_INSTALLED_STATE_ARTIFACT_DIGEST64) {
            st = parse_u64(field, &out_artifact->digest64);
        } else if (field.type == CORE_TLV_TAG_INSTALLED_STATE_ARTIFACT_SIZE) {
            st = parse_u64(field, &out_artifact->size);
        } else {
            continue;
        }
        if (!err_is_ok(&st)) {
            core_tlv_framed_stream_destroy(&stream);
            return st;
        }
    }
    core_tlv_framed_stream_destroy(&stream);
    return err_ok();
}

static err_t parse_registration(const core_tlv_framed_record_t& rec,
                                InstalledStateRegistration* out_reg) {
    core_tlv_framed_stream_t stream;
    err_t st;
    u32 i;

    if (!out_reg) {
        return state_err_invalid_args();
    }
    out_reg->kind = 0u;
    out_reg->status = 0u;
    out_reg->value.clear();

    st = core_tlv_framed_parse_stream(rec.payload, rec.length, &stream);
    if (!err_is_ok(&st)) {
        return st;
    }
    for (i = 0u; i < stream.record_count; ++i) {
        const core_tlv_framed_record_t& field = stream.records[i];
        if (field.type == CORE_TLV_TAG_INSTALLED_STATE_REG_KIND) {
            st = parse_u16(field, &out_reg->kind);
        } else if (field.type == CORE_TLV_TAG_INSTALLED_STATE_REG_STATUS) {
            st = parse_u16(field, &out_reg->status);
        } else if (field.type == CORE_TLV_TAG_INSTALLED_STATE_REG_VALUE) {
            st = parse_string(field, &out_reg->value);
        } else {
            continue;
        }
        if (!err_is_ok(&st)) {
            core_tlv_framed_stream_destroy(&stream);
            return st;
        }
    }
    core_tlv_framed_stream_destroy(&stream);
    return err_ok();
}

err_t installed_state_parse(const unsigned char* data,
                            u32 size,
                            InstalledState* out_state) {
    core_tlv_framed_view_t view;
    err_t st;
    u32 i;
    bool has_product = false;
    bool has_version = false;
    bool has_splat = false;
    bool has_scope = false;
    bool has_root = false;
    bool has_manifest = false;
    bool has_request = false;
    bool has_state_version = false;

    if (!out_state) {
        return state_err_invalid_args();
    }
    installed_state_clear(out_state);

    st = core_tlv_framed_parse(data, size, &view);
    if (!err_is_ok(&st)) {
        return st;
    }

    for (i = 0u; i < view.record_count; ++i) {
        const core_tlv_framed_record_t& rec = view.records[i];
        if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_PRODUCT_ID) {
            st = parse_string(rec, &out_state->product_id);
            has_product = err_is_ok(&st) ? true : has_product;
        } else if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_INSTALLED_VERSION) {
            st = parse_string(rec, &out_state->installed_version);
            has_version = err_is_ok(&st) ? true : has_version;
        } else if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_SELECTED_SPLAT) {
            st = parse_string(rec, &out_state->selected_splat);
            has_splat = err_is_ok(&st) ? true : has_splat;
        } else if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_INSTALL_SCOPE) {
            st = parse_u16(rec, &out_state->install_scope);
            has_scope = err_is_ok(&st) ? true : has_scope;
        } else if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_INSTALL_ROOT) {
            st = parse_string(rec, &out_state->install_root);
            has_root = err_is_ok(&st) ? true : has_root;
        } else if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_MANIFEST_DIGEST64) {
            st = parse_u64(rec, &out_state->manifest_digest64);
            has_manifest = err_is_ok(&st) ? true : has_manifest;
        } else if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_REQUEST_DIGEST64) {
            st = parse_u64(rec, &out_state->request_digest64);
            has_request = err_is_ok(&st) ? true : has_request;
        } else if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_PREV_STATE_DIGEST64) {
            st = parse_u64(rec, &out_state->previous_state_digest64);
        } else if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_IMPORT_SOURCE) {
            st = parse_string(rec, &out_state->import_source);
        } else if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_IMPORT_DETAILS) {
            core_tlv_framed_stream_t list_stream;
            err_t lst;
            u32 j;
            lst = core_tlv_framed_parse_stream(rec.payload, rec.length, &list_stream);
            if (!err_is_ok(&lst)) {
                core_tlv_framed_view_destroy(&view);
                return lst;
            }
            for (j = 0u; j < list_stream.record_count; ++j) {
                const core_tlv_framed_record_t& entry = list_stream.records[j];
                if (entry.type != CORE_TLV_TAG_INSTALLED_STATE_IMPORT_DETAIL_ENTRY) {
                    continue;
                }
                std::string value;
                lst = parse_string(entry, &value);
                if (!err_is_ok(&lst)) {
                    core_tlv_framed_stream_destroy(&list_stream);
                    core_tlv_framed_view_destroy(&view);
                    return lst;
                }
                out_state->import_details.push_back(value);
            }
            core_tlv_framed_stream_destroy(&list_stream);
            st = err_ok();
        } else if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_VERSION) {
            st = parse_u32(rec, &out_state->state_version);
            has_state_version = err_is_ok(&st) ? true : has_state_version;
        } else if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_MIGRATIONS) {
            core_tlv_framed_stream_t list_stream;
            err_t lst;
            u32 j;
            lst = core_tlv_framed_parse_stream(rec.payload, rec.length, &list_stream);
            if (!err_is_ok(&lst)) {
                core_tlv_framed_view_destroy(&view);
                return lst;
            }
            for (j = 0u; j < list_stream.record_count; ++j) {
                const core_tlv_framed_record_t& entry = list_stream.records[j];
                if (entry.type != CORE_TLV_TAG_INSTALLED_STATE_MIGRATION_ENTRY) {
                    continue;
                }
                std::string value;
                lst = parse_string(entry, &value);
                if (!err_is_ok(&lst)) {
                    core_tlv_framed_stream_destroy(&list_stream);
                    core_tlv_framed_view_destroy(&view);
                    return lst;
                }
                out_state->migration_applied.push_back(value);
            }
            core_tlv_framed_stream_destroy(&list_stream);
            st = err_ok();
        } else if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_OWNERSHIP) {
            st = parse_u16(rec, &out_state->ownership);
        } else if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_COMPONENTS ||
                   rec.type == CORE_TLV_TAG_INSTALLED_STATE_INSTALL_ROOTS) {
            core_tlv_framed_stream_t list_stream;
            err_t lst;
            u32 j;
            lst = core_tlv_framed_parse_stream(rec.payload, rec.length, &list_stream);
            if (!err_is_ok(&lst)) {
                core_tlv_framed_view_destroy(&view);
                return lst;
            }
            {
                const u16 entry_tag = (rec.type == CORE_TLV_TAG_INSTALLED_STATE_COMPONENTS)
                                      ? (u16)CORE_TLV_TAG_INSTALLED_STATE_COMPONENT_ENTRY
                                      : (u16)CORE_TLV_TAG_INSTALLED_STATE_INSTALL_ROOT_ENTRY;
                for (j = 0u; j < list_stream.record_count; ++j) {
                    const core_tlv_framed_record_t& entry = list_stream.records[j];
                    if (entry.type != entry_tag) {
                        continue;
                    }
                    std::string value;
                    lst = parse_string(entry, &value);
                    if (!err_is_ok(&lst)) {
                        core_tlv_framed_stream_destroy(&list_stream);
                        core_tlv_framed_view_destroy(&view);
                        return lst;
                    }
                    if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_COMPONENTS) {
                        out_state->installed_components.push_back(value);
                    } else {
                        out_state->install_roots.push_back(value);
                    }
                }
            }
            core_tlv_framed_stream_destroy(&list_stream);
            st = err_ok();
        } else if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_ARTIFACTS) {
            core_tlv_framed_stream_t list_stream;
            err_t lst;
            u32 j;
            lst = core_tlv_framed_parse_stream(rec.payload, rec.length, &list_stream);
            if (!err_is_ok(&lst)) {
                core_tlv_framed_view_destroy(&view);
                return lst;
            }
            for (j = 0u; j < list_stream.record_count; ++j) {
                const core_tlv_framed_record_t& entry = list_stream.records[j];
                if (entry.type != CORE_TLV_TAG_INSTALLED_STATE_ARTIFACT_ENTRY) {
                    continue;
                }
                InstalledStateArtifact art;
                lst = parse_artifact(entry, &art);
                if (!err_is_ok(&lst)) {
                    core_tlv_framed_stream_destroy(&list_stream);
                    core_tlv_framed_view_destroy(&view);
                    return lst;
                }
                out_state->artifacts.push_back(art);
            }
            core_tlv_framed_stream_destroy(&list_stream);
            st = err_ok();
        } else if (rec.type == CORE_TLV_TAG_INSTALLED_STATE_REGISTRATIONS) {
            core_tlv_framed_stream_t list_stream;
            err_t lst;
            u32 j;
            lst = core_tlv_framed_parse_stream(rec.payload, rec.length, &list_stream);
            if (!err_is_ok(&lst)) {
                core_tlv_framed_view_destroy(&view);
                return lst;
            }
            for (j = 0u; j < list_stream.record_count; ++j) {
                const core_tlv_framed_record_t& entry = list_stream.records[j];
                if (entry.type != CORE_TLV_TAG_INSTALLED_STATE_REG_ENTRY) {
                    continue;
                }
                InstalledStateRegistration reg;
                lst = parse_registration(entry, &reg);
                if (!err_is_ok(&lst)) {
                    core_tlv_framed_stream_destroy(&list_stream);
                    core_tlv_framed_view_destroy(&view);
                    return lst;
                }
                out_state->registrations.push_back(reg);
            }
            core_tlv_framed_stream_destroy(&list_stream);
            st = err_ok();
        } else {
            continue;
        }

        if (!err_is_ok(&st)) {
            core_tlv_framed_view_destroy(&view);
            return st;
        }
    }

    core_tlv_framed_view_destroy(&view);

    if (!has_product || out_state->product_id.empty()) {
        return state_err_missing_field(CORE_TLV_TAG_INSTALLED_STATE_PRODUCT_ID);
    }
    if (!has_version || out_state->installed_version.empty()) {
        return state_err_missing_field(CORE_TLV_TAG_INSTALLED_STATE_INSTALLED_VERSION);
    }
    if (!has_splat || out_state->selected_splat.empty()) {
        return state_err_missing_field(CORE_TLV_TAG_INSTALLED_STATE_SELECTED_SPLAT);
    }
    if (!has_scope || out_state->install_scope == 0u) {
        return state_err_missing_field(CORE_TLV_TAG_INSTALLED_STATE_INSTALL_SCOPE);
    }
    if (!has_root || out_state->install_root.empty()) {
        return state_err_missing_field(CORE_TLV_TAG_INSTALLED_STATE_INSTALL_ROOT);
    }
    if (!has_manifest) {
        return state_err_missing_field(CORE_TLV_TAG_INSTALLED_STATE_MANIFEST_DIGEST64);
    }
    if (!has_request) {
        return state_err_missing_field(CORE_TLV_TAG_INSTALLED_STATE_REQUEST_DIGEST64);
    }
    if (!has_state_version) {
        out_state->state_version = CORE_INSTALLED_STATE_TLV_VERSION;
        out_state->migration_applied.push_back("backfill_state_version_v1");
    }

    return err_ok();
}

static bool string_less(const std::string& a, const std::string& b) {
    return a < b;
}

static bool artifact_less(const InstalledStateArtifact& a,
                          const InstalledStateArtifact& b) {
    if (a.target_root_id != b.target_root_id) {
        return a.target_root_id < b.target_root_id;
    }
    return a.path < b.path;
}

static bool registration_less(const InstalledStateRegistration& a,
                              const InstalledStateRegistration& b) {
    if (a.kind != b.kind) {
        return a.kind < b.kind;
    }
    if (a.value != b.value) {
        return a.value < b.value;
    }
    return a.status < b.status;
}

err_t installed_state_write(const InstalledState* state,
                            core_tlv_framed_buffer_t* out_buf) {
    core_tlv_framed_builder_t* builder;
    err_t st;
    std::vector<std::string> components;
    std::vector<std::string> roots;
    std::vector<InstalledStateArtifact> artifacts;
    std::vector<InstalledStateRegistration> registrations;
    u32 i;

    if (!state || !out_buf) {
        return state_err_invalid_args();
    }

    builder = core_tlv_framed_builder_create();
    if (!builder) {
        return err_make((u16)ERRD_COMMON,
                        (u16)ERRC_COMMON_INTERNAL,
                        (u32)ERRF_FATAL,
                        (u32)ERRMSG_COMMON_INTERNAL);
    }

    st = core_tlv_framed_builder_add_string(builder,
                                            CORE_TLV_TAG_INSTALLED_STATE_PRODUCT_ID,
                                            state->product_id.c_str());
    if (!err_is_ok(&st)) goto done;
    st = core_tlv_framed_builder_add_string(builder,
                                            CORE_TLV_TAG_INSTALLED_STATE_INSTALLED_VERSION,
                                            state->installed_version.c_str());
    if (!err_is_ok(&st)) goto done;
    st = core_tlv_framed_builder_add_string(builder,
                                            CORE_TLV_TAG_INSTALLED_STATE_SELECTED_SPLAT,
                                            state->selected_splat.c_str());
    if (!err_is_ok(&st)) goto done;
    st = core_tlv_framed_builder_add_u16(builder,
                                         CORE_TLV_TAG_INSTALLED_STATE_INSTALL_SCOPE,
                                         state->install_scope);
    if (!err_is_ok(&st)) goto done;
    st = core_tlv_framed_builder_add_string(builder,
                                            CORE_TLV_TAG_INSTALLED_STATE_INSTALL_ROOT,
                                            state->install_root.c_str());
    if (!err_is_ok(&st)) goto done;
    if (!state->install_roots.empty()) {
        roots = state->install_roots;
        std::sort(roots.begin(), roots.end(), string_less);
        core_tlv_framed_builder_t* list_builder = core_tlv_framed_builder_create();
        core_tlv_framed_buffer_t list_payload;
        for (i = 0u; i < roots.size(); ++i) {
            core_tlv_framed_builder_add_string(list_builder,
                                               CORE_TLV_TAG_INSTALLED_STATE_INSTALL_ROOT_ENTRY,
                                               roots[i].c_str());
        }
        st = core_tlv_framed_builder_finalize_payload(list_builder, &list_payload);
        core_tlv_framed_builder_destroy(list_builder);
        if (!err_is_ok(&st)) goto done;
        st = core_tlv_framed_builder_add_container(builder,
                                                   CORE_TLV_TAG_INSTALLED_STATE_INSTALL_ROOTS,
                                                   list_payload.data,
                                                   list_payload.size);
        core_tlv_framed_buffer_free(&list_payload);
        if (!err_is_ok(&st)) goto done;
    }
    st = core_tlv_framed_builder_add_u16(builder,
                                         CORE_TLV_TAG_INSTALLED_STATE_OWNERSHIP,
                                         state->ownership);
    if (!err_is_ok(&st)) goto done;
    st = core_tlv_framed_builder_add_u64(builder,
                                         CORE_TLV_TAG_INSTALLED_STATE_MANIFEST_DIGEST64,
                                         state->manifest_digest64);
    if (!err_is_ok(&st)) goto done;
    st = core_tlv_framed_builder_add_u64(builder,
                                         CORE_TLV_TAG_INSTALLED_STATE_REQUEST_DIGEST64,
                                         state->request_digest64);
    if (!err_is_ok(&st)) goto done;
    {
        u32 state_version = state->state_version ? state->state_version : (u32)CORE_INSTALLED_STATE_TLV_VERSION;
        st = core_tlv_framed_builder_add_u32(builder,
                                             CORE_TLV_TAG_INSTALLED_STATE_VERSION,
                                             state_version);
        if (!err_is_ok(&st)) goto done;
    }
    if (state->previous_state_digest64 != 0u) {
        st = core_tlv_framed_builder_add_u64(builder,
                                             CORE_TLV_TAG_INSTALLED_STATE_PREV_STATE_DIGEST64,
                                             state->previous_state_digest64);
        if (!err_is_ok(&st)) goto done;
    }
    if (!state->import_source.empty()) {
        st = core_tlv_framed_builder_add_string(builder,
                                                CORE_TLV_TAG_INSTALLED_STATE_IMPORT_SOURCE,
                                                state->import_source.c_str());
        if (!err_is_ok(&st)) goto done;
    }
    if (!state->import_details.empty()) {
        std::vector<std::string> details = state->import_details;
        std::sort(details.begin(), details.end(), string_less);
        core_tlv_framed_builder_t* list_builder = core_tlv_framed_builder_create();
        core_tlv_framed_buffer_t list_payload;
        for (i = 0u; i < details.size(); ++i) {
            core_tlv_framed_builder_add_string(list_builder,
                                               CORE_TLV_TAG_INSTALLED_STATE_IMPORT_DETAIL_ENTRY,
                                               details[i].c_str());
        }
        st = core_tlv_framed_builder_finalize_payload(list_builder, &list_payload);
        core_tlv_framed_builder_destroy(list_builder);
        if (!err_is_ok(&st)) goto done;
        st = core_tlv_framed_builder_add_container(builder,
                                                   CORE_TLV_TAG_INSTALLED_STATE_IMPORT_DETAILS,
                                                   list_payload.data,
                                                   list_payload.size);
        core_tlv_framed_buffer_free(&list_payload);
        if (!err_is_ok(&st)) goto done;
    }
    if (!state->migration_applied.empty()) {
        std::vector<std::string> details = state->migration_applied;
        std::sort(details.begin(), details.end(), string_less);
        core_tlv_framed_builder_t* list_builder = core_tlv_framed_builder_create();
        core_tlv_framed_buffer_t list_payload;
        for (i = 0u; i < details.size(); ++i) {
            core_tlv_framed_builder_add_string(list_builder,
                                               CORE_TLV_TAG_INSTALLED_STATE_MIGRATION_ENTRY,
                                               details[i].c_str());
        }
        st = core_tlv_framed_builder_finalize_payload(list_builder, &list_payload);
        core_tlv_framed_builder_destroy(list_builder);
        if (!err_is_ok(&st)) goto done;
        st = core_tlv_framed_builder_add_container(builder,
                                                   CORE_TLV_TAG_INSTALLED_STATE_MIGRATIONS,
                                                   list_payload.data,
                                                   list_payload.size);
        core_tlv_framed_buffer_free(&list_payload);
        if (!err_is_ok(&st)) goto done;
    }

    components = state->installed_components;
    std::sort(components.begin(), components.end(), string_less);
    if (!components.empty()) {
        core_tlv_framed_builder_t* list_builder = core_tlv_framed_builder_create();
        core_tlv_framed_buffer_t list_payload;
        for (i = 0u; i < components.size(); ++i) {
            core_tlv_framed_builder_add_string(list_builder,
                                               CORE_TLV_TAG_INSTALLED_STATE_COMPONENT_ENTRY,
                                               components[i].c_str());
        }
        st = core_tlv_framed_builder_finalize_payload(list_builder, &list_payload);
        core_tlv_framed_builder_destroy(list_builder);
        if (!err_is_ok(&st)) goto done;
        st = core_tlv_framed_builder_add_container(builder,
                                                   CORE_TLV_TAG_INSTALLED_STATE_COMPONENTS,
                                                   list_payload.data,
                                                   list_payload.size);
        core_tlv_framed_buffer_free(&list_payload);
        if (!err_is_ok(&st)) goto done;
    }

    artifacts = state->artifacts;
    std::sort(artifacts.begin(), artifacts.end(), artifact_less);
    if (!artifacts.empty()) {
        core_tlv_framed_builder_t* list_builder = core_tlv_framed_builder_create();
        core_tlv_framed_buffer_t list_payload;
        for (i = 0u; i < artifacts.size(); ++i) {
            const InstalledStateArtifact& art = artifacts[i];
            core_tlv_framed_builder_t* entry_builder = core_tlv_framed_builder_create();
            core_tlv_framed_buffer_t entry_payload;
            core_tlv_framed_builder_add_u32(entry_builder,
                                            CORE_TLV_TAG_INSTALLED_STATE_ARTIFACT_ROOT_ID,
                                            art.target_root_id);
            core_tlv_framed_builder_add_string(entry_builder,
                                               CORE_TLV_TAG_INSTALLED_STATE_ARTIFACT_PATH,
                                               art.path.c_str());
            core_tlv_framed_builder_add_u64(entry_builder,
                                            CORE_TLV_TAG_INSTALLED_STATE_ARTIFACT_DIGEST64,
                                            art.digest64);
            core_tlv_framed_builder_add_u64(entry_builder,
                                            CORE_TLV_TAG_INSTALLED_STATE_ARTIFACT_SIZE,
                                            art.size);
            st = core_tlv_framed_builder_finalize_payload(entry_builder, &entry_payload);
            core_tlv_framed_builder_destroy(entry_builder);
            if (!err_is_ok(&st)) {
                core_tlv_framed_builder_destroy(list_builder);
                goto done;
            }
            core_tlv_framed_builder_add_container(list_builder,
                                                  CORE_TLV_TAG_INSTALLED_STATE_ARTIFACT_ENTRY,
                                                  entry_payload.data,
                                                  entry_payload.size);
            core_tlv_framed_buffer_free(&entry_payload);
        }
        st = core_tlv_framed_builder_finalize_payload(list_builder, &list_payload);
        core_tlv_framed_builder_destroy(list_builder);
        if (!err_is_ok(&st)) goto done;
        st = core_tlv_framed_builder_add_container(builder,
                                                   CORE_TLV_TAG_INSTALLED_STATE_ARTIFACTS,
                                                   list_payload.data,
                                                   list_payload.size);
        core_tlv_framed_buffer_free(&list_payload);
        if (!err_is_ok(&st)) goto done;
    }

    registrations = state->registrations;
    std::sort(registrations.begin(), registrations.end(), registration_less);
    if (!registrations.empty()) {
        core_tlv_framed_builder_t* list_builder = core_tlv_framed_builder_create();
        core_tlv_framed_buffer_t list_payload;
        for (i = 0u; i < registrations.size(); ++i) {
            const InstalledStateRegistration& reg = registrations[i];
            core_tlv_framed_builder_t* entry_builder = core_tlv_framed_builder_create();
            core_tlv_framed_buffer_t entry_payload;
            core_tlv_framed_builder_add_u16(entry_builder,
                                            CORE_TLV_TAG_INSTALLED_STATE_REG_KIND,
                                            reg.kind);
            core_tlv_framed_builder_add_string(entry_builder,
                                               CORE_TLV_TAG_INSTALLED_STATE_REG_VALUE,
                                               reg.value.c_str());
            core_tlv_framed_builder_add_u16(entry_builder,
                                            CORE_TLV_TAG_INSTALLED_STATE_REG_STATUS,
                                            reg.status);
            st = core_tlv_framed_builder_finalize_payload(entry_builder, &entry_payload);
            core_tlv_framed_builder_destroy(entry_builder);
            if (!err_is_ok(&st)) {
                core_tlv_framed_builder_destroy(list_builder);
                goto done;
            }
            core_tlv_framed_builder_add_container(list_builder,
                                                  CORE_TLV_TAG_INSTALLED_STATE_REG_ENTRY,
                                                  entry_payload.data,
                                                  entry_payload.size);
            core_tlv_framed_buffer_free(&entry_payload);
        }
        st = core_tlv_framed_builder_finalize_payload(list_builder, &list_payload);
        core_tlv_framed_builder_destroy(list_builder);
        if (!err_is_ok(&st)) goto done;
        st = core_tlv_framed_builder_add_container(builder,
                                                   CORE_TLV_TAG_INSTALLED_STATE_REGISTRATIONS,
                                                   list_payload.data,
                                                   list_payload.size);
        core_tlv_framed_buffer_free(&list_payload);
        if (!err_is_ok(&st)) goto done;
    }

    st = core_tlv_framed_builder_finalize(builder, out_buf);

done:
    core_tlv_framed_builder_destroy(builder);
    return st;
}

} /* namespace core_installed_state */
} /* namespace dom */
