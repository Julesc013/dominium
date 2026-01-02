#include "dsk/dsk_contracts.h"

#include <algorithm>
#include <string.h>

static bool dsk_string_less(const std::string &a, const std::string &b);

static dsk_status_t dsk_contract_error(dsk_u16 code, dsk_u16 subcode) {
    return dsk_error_make(DSK_DOMAIN_KERNEL, code, subcode, DSK_ERROR_FLAG_USER_ACTIONABLE);
}

static dsk_status_t dsk_parse_string(const dsk_tlv_record_t &rec, std::string *out) {
    if (!out) {
        return dsk_contract_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    out->assign(reinterpret_cast<const char *>(rec.payload), rec.length);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_parse_u64(const dsk_tlv_record_t &rec, dsk_u64 *out) {
    if (!out) {
        return dsk_contract_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length != 8u) {
        return dsk_contract_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
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

static dsk_status_t dsk_parse_bool(const dsk_tlv_record_t &rec, dsk_bool *out) {
    if (!out) {
        return dsk_contract_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length == 1u) {
        *out = rec.payload[0] ? DSK_TRUE : DSK_FALSE;
        return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    }
    if (rec.length == 2u) {
        dsk_u16 v = (dsk_u16)rec.payload[0] | (dsk_u16)((dsk_u16)rec.payload[1] << 8);
        *out = v ? DSK_TRUE : DSK_FALSE;
        return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    }
    return dsk_contract_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
}

void dsk_manifest_clear(dsk_manifest_t *manifest) {
    if (!manifest) {
        return;
    }
    manifest->product_id.clear();
    manifest->version.clear();
    manifest->build_id.clear();
    manifest->supported_targets.clear();
    manifest->allowed_splats.clear();
    manifest->layout_templates.clear();
    manifest->components.clear();
}

static dsk_status_t dsk_parse_artifact(const dsk_tlv_record_t &rec,
                                       dsk_artifact_t *out_artifact) {
    dsk_tlv_stream_t stream;
    dsk_status_t st;
    dsk_u32 i;

    if (!out_artifact) {
        return dsk_contract_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    out_artifact->artifact_id.clear();
    out_artifact->hash.clear();
    out_artifact->digest64 = 0u;
    out_artifact->source_path.clear();
    out_artifact->layout_template_id.clear();
    out_artifact->size = 0u;

    st = dsk_tlv_parse_stream(rec.payload, rec.length, &stream);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    for (i = 0u; i < stream.record_count; ++i) {
        const dsk_tlv_record_t &field = stream.records[i];
        if (field.type == DSK_TLV_TAG_ARTIFACT_ID) {
            st = dsk_parse_string(field, &out_artifact->artifact_id);
        } else if (field.type == DSK_TLV_TAG_ARTIFACT_HASH) {
            st = dsk_parse_string(field, &out_artifact->hash);
        } else if (field.type == DSK_TLV_TAG_ARTIFACT_DIGEST64) {
            st = dsk_parse_u64(field, &out_artifact->digest64);
        } else if (field.type == DSK_TLV_TAG_ARTIFACT_PATH ||
                   field.type == DSK_TLV_TAG_ARTIFACT_SOURCE_PATH) {
            st = dsk_parse_string(field, &out_artifact->source_path);
        } else if (field.type == DSK_TLV_TAG_ARTIFACT_SIZE) {
            st = dsk_parse_u64(field, &out_artifact->size);
        } else if (field.type == DSK_TLV_TAG_ARTIFACT_LAYOUT_TEMPLATE_ID) {
            st = dsk_parse_string(field, &out_artifact->layout_template_id);
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

static dsk_status_t dsk_parse_component(const dsk_tlv_record_t &rec,
                                        dsk_manifest_component_t *out_component) {
    dsk_tlv_stream_t stream;
    dsk_status_t st;
    dsk_u32 i;

    if (!out_component) {
        return dsk_contract_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    out_component->component_id.clear();
    out_component->component_version.clear();
    out_component->kind.clear();
    out_component->default_selected = DSK_FALSE;
    out_component->deps.clear();
    out_component->conflicts.clear();
    out_component->supported_targets.clear();
    out_component->artifacts.clear();

    st = dsk_tlv_parse_stream(rec.payload, rec.length, &stream);
    if (!dsk_error_is_ok(st)) {
        return st;
    }

    for (i = 0u; i < stream.record_count; ++i) {
        const dsk_tlv_record_t &field = stream.records[i];
        if (field.type == DSK_TLV_TAG_COMPONENT_ID) {
            st = dsk_parse_string(field, &out_component->component_id);
        } else if (field.type == DSK_TLV_TAG_COMPONENT_VERSION) {
            st = dsk_parse_string(field, &out_component->component_version);
        } else if (field.type == DSK_TLV_TAG_COMPONENT_KIND) {
            st = dsk_parse_string(field, &out_component->kind);
        } else if (field.type == DSK_TLV_TAG_COMPONENT_DEFAULT_SELECTED) {
            st = dsk_parse_bool(field, &out_component->default_selected);
        } else if (field.type == DSK_TLV_TAG_COMPONENT_DEPS ||
                   field.type == DSK_TLV_TAG_COMPONENT_CONFLICTS ||
                   field.type == DSK_TLV_TAG_COMPONENT_ARTIFACTS ||
                   field.type == DSK_TLV_TAG_COMPONENT_SUPPORTED_TARGETS) {
            dsk_tlv_stream_t list_stream;
            dsk_status_t lst;
            dsk_u32 j;

            lst = dsk_tlv_parse_stream(field.payload, field.length, &list_stream);
            if (!dsk_error_is_ok(lst)) {
                dsk_tlv_stream_destroy(&stream);
                return lst;
            }

            if (field.type == DSK_TLV_TAG_COMPONENT_ARTIFACTS) {
                for (j = 0u; j < list_stream.record_count; ++j) {
                    const dsk_tlv_record_t &entry = list_stream.records[j];
                    if (entry.type != DSK_TLV_TAG_ARTIFACT_ENTRY) {
                        continue;
                    }
                    dsk_artifact_t artifact;
                    lst = dsk_parse_artifact(entry, &artifact);
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_stream_destroy(&stream);
                        return lst;
                    }
                    out_component->artifacts.push_back(artifact);
                }
            } else if (field.type == DSK_TLV_TAG_COMPONENT_SUPPORTED_TARGETS) {
                for (j = 0u; j < list_stream.record_count; ++j) {
                    const dsk_tlv_record_t &entry = list_stream.records[j];
                    if (entry.type != DSK_TLV_TAG_COMPONENT_TARGET_ENTRY) {
                        continue;
                    }
                    std::string value;
                    lst = dsk_parse_string(entry, &value);
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_stream_destroy(&stream);
                        return lst;
                    }
                    out_component->supported_targets.push_back(value);
                }
            } else {
                const dsk_u16 entry_tag = (field.type == DSK_TLV_TAG_COMPONENT_DEPS)
                                          ? DSK_TLV_TAG_COMPONENT_DEP_ENTRY
                                          : DSK_TLV_TAG_COMPONENT_CONFLICT_ENTRY;
                for (j = 0u; j < list_stream.record_count; ++j) {
                    const dsk_tlv_record_t &entry = list_stream.records[j];
                    if (entry.type != entry_tag) {
                        continue;
                    }
                    std::string value;
                    lst = dsk_parse_string(entry, &value);
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_stream_destroy(&stream);
                        return lst;
                    }
                    if (field.type == DSK_TLV_TAG_COMPONENT_DEPS) {
                        out_component->deps.push_back(value);
                    } else {
                        out_component->conflicts.push_back(value);
                    }
                }
            }

            dsk_tlv_stream_destroy(&list_stream);
            st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
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

static dsk_status_t dsk_parse_layout_template(const dsk_tlv_record_t &rec,
                                              dsk_layout_template_t *out_template) {
    dsk_tlv_stream_t stream;
    dsk_status_t st;
    dsk_u32 i;

    if (!out_template) {
        return dsk_contract_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    out_template->template_id.clear();
    out_template->target_root.clear();
    out_template->path_prefix.clear();

    st = dsk_tlv_parse_stream(rec.payload, rec.length, &stream);
    if (!dsk_error_is_ok(st)) {
        return st;
    }

    for (i = 0u; i < stream.record_count; ++i) {
        const dsk_tlv_record_t &field = stream.records[i];
        if (field.type == DSK_TLV_TAG_LAYOUT_TEMPLATE_ID) {
            st = dsk_parse_string(field, &out_template->template_id);
        } else if (field.type == DSK_TLV_TAG_LAYOUT_TEMPLATE_TARGET_ROOT) {
            st = dsk_parse_string(field, &out_template->target_root);
        } else if (field.type == DSK_TLV_TAG_LAYOUT_TEMPLATE_PATH_PREFIX) {
            st = dsk_parse_string(field, &out_template->path_prefix);
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

static int dsk_manifest_has_component(const dsk_manifest_t &manifest,
                                      const std::string &id) {
    size_t i;
    for (i = 0u; i < manifest.components.size(); ++i) {
        if (manifest.components[i].component_id == id) {
            return 1;
        }
    }
    return 0;
}

static int dsk_manifest_has_layout_template(const dsk_manifest_t &manifest,
                                            const std::string &id) {
    size_t i;
    for (i = 0u; i < manifest.layout_templates.size(); ++i) {
        if (manifest.layout_templates[i].template_id == id) {
            return 1;
        }
    }
    return 0;
}

dsk_status_t dsk_manifest_parse(const dsk_u8 *data,
                                dsk_u32 size,
                                dsk_manifest_t *out_manifest) {
    dsk_tlv_view_t view;
    dsk_status_t st;
    dsk_u32 i;

    if (!out_manifest) {
        return dsk_contract_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    dsk_manifest_clear(out_manifest);
    if (!data || size == 0u) {
        return dsk_contract_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }

    st = dsk_tlv_parse(data, size, &view);
    if (!dsk_error_is_ok(st)) {
        return st;
    }

    for (i = 0u; i < view.record_count; ++i) {
        const dsk_tlv_record_t &rec = view.records[i];
        if (rec.type == DSK_TLV_TAG_MANIFEST_PRODUCT_ID) {
            st = dsk_parse_string(rec, &out_manifest->product_id);
        } else if (rec.type == DSK_TLV_TAG_MANIFEST_VERSION) {
            st = dsk_parse_string(rec, &out_manifest->version);
        } else if (rec.type == DSK_TLV_TAG_MANIFEST_BUILD_ID) {
            st = dsk_parse_string(rec, &out_manifest->build_id);
        } else if (rec.type == DSK_TLV_TAG_MANIFEST_SUPPORTED_TARGETS ||
                   rec.type == DSK_TLV_TAG_MANIFEST_ALLOWED_SPLATS ||
                   rec.type == DSK_TLV_TAG_MANIFEST_LAYOUT_TEMPLATES ||
                   rec.type == DSK_TLV_TAG_MANIFEST_COMPONENTS) {
            dsk_tlv_stream_t list_stream;
            dsk_status_t lst;
            dsk_u32 j;

            lst = dsk_tlv_parse_stream(rec.payload, rec.length, &list_stream);
            if (!dsk_error_is_ok(lst)) {
                dsk_tlv_view_destroy(&view);
                return lst;
            }

            if (rec.type == DSK_TLV_TAG_MANIFEST_SUPPORTED_TARGETS) {
                for (j = 0u; j < list_stream.record_count; ++j) {
                    const dsk_tlv_record_t &entry = list_stream.records[j];
                    if (entry.type != DSK_TLV_TAG_PLATFORM_ENTRY) {
                        continue;
                    }
                    std::string platform;
                    lst = dsk_parse_string(entry, &platform);
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_view_destroy(&view);
                        return lst;
                    }
                    out_manifest->supported_targets.push_back(platform);
                }
            } else if (rec.type == DSK_TLV_TAG_MANIFEST_ALLOWED_SPLATS) {
                for (j = 0u; j < list_stream.record_count; ++j) {
                    const dsk_tlv_record_t &entry = list_stream.records[j];
                    if (entry.type != DSK_TLV_TAG_ALLOWED_SPLAT_ENTRY) {
                        continue;
                    }
                    std::string splat;
                    lst = dsk_parse_string(entry, &splat);
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_view_destroy(&view);
                        return lst;
                    }
                    out_manifest->allowed_splats.push_back(splat);
                }
            } else if (rec.type == DSK_TLV_TAG_MANIFEST_LAYOUT_TEMPLATES) {
                for (j = 0u; j < list_stream.record_count; ++j) {
                    const dsk_tlv_record_t &entry = list_stream.records[j];
                    if (entry.type != DSK_TLV_TAG_LAYOUT_TEMPLATE_ENTRY) {
                        continue;
                    }
                    dsk_layout_template_t layout;
                    lst = dsk_parse_layout_template(entry, &layout);
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_view_destroy(&view);
                        return lst;
                    }
                    out_manifest->layout_templates.push_back(layout);
                }
            } else {
                for (j = 0u; j < list_stream.record_count; ++j) {
                    const dsk_tlv_record_t &entry = list_stream.records[j];
                    if (entry.type != DSK_TLV_TAG_COMPONENT_ENTRY) {
                        continue;
                    }
                    dsk_manifest_component_t comp;
                    lst = dsk_parse_component(entry, &comp);
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_view_destroy(&view);
                        return lst;
                    }
                    out_manifest->components.push_back(comp);
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

    if (out_manifest->product_id.empty() ||
        out_manifest->version.empty() ||
        out_manifest->build_id.empty() ||
        out_manifest->supported_targets.empty() ||
        out_manifest->components.empty()) {
        return dsk_contract_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_MISSING_FIELD);
    }

    {
        std::vector<std::string> component_ids;
        for (i = 0u; i < out_manifest->components.size(); ++i) {
            if (out_manifest->components[i].component_id.empty() ||
                out_manifest->components[i].kind.empty()) {
                return dsk_contract_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_MISSING_FIELD);
            }
            component_ids.push_back(out_manifest->components[i].component_id);
        }
        std::sort(component_ids.begin(), component_ids.end(), dsk_string_less);
        for (i = 1u; i < component_ids.size(); ++i) {
            if (component_ids[i] == component_ids[i - 1u]) {
                return dsk_contract_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_INVALID_FIELD);
            }
        }
    }

    if (!out_manifest->layout_templates.empty()) {
        std::vector<std::string> template_ids;
        for (i = 0u; i < out_manifest->layout_templates.size(); ++i) {
            if (out_manifest->layout_templates[i].template_id.empty()) {
                return dsk_contract_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_MISSING_FIELD);
            }
            template_ids.push_back(out_manifest->layout_templates[i].template_id);
        }
        std::sort(template_ids.begin(), template_ids.end(), dsk_string_less);
        for (i = 1u; i < template_ids.size(); ++i) {
            if (template_ids[i] == template_ids[i - 1u]) {
                return dsk_contract_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_INVALID_FIELD);
            }
        }
    }

    for (i = 0u; i < out_manifest->components.size(); ++i) {
        const dsk_manifest_component_t &comp = out_manifest->components[i];
        size_t j;
        if (!comp.artifacts.empty() && out_manifest->layout_templates.empty()) {
            return dsk_contract_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_MISSING_FIELD);
        }
        for (j = 0u; j < comp.deps.size(); ++j) {
            if (!dsk_manifest_has_component(*out_manifest, comp.deps[j])) {
                return dsk_contract_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_INVALID_FIELD);
            }
        }
        for (j = 0u; j < comp.conflicts.size(); ++j) {
            if (!dsk_manifest_has_component(*out_manifest, comp.conflicts[j])) {
                return dsk_contract_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_INVALID_FIELD);
            }
        }
        for (j = 0u; j < comp.artifacts.size(); ++j) {
            const dsk_artifact_t &art = comp.artifacts[j];
            if (art.artifact_id.empty() || art.source_path.empty() ||
                art.layout_template_id.empty()) {
                return dsk_contract_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_MISSING_FIELD);
            }
            if (art.digest64 == 0u) {
                return dsk_contract_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_MISSING_FIELD);
            }
            if (!out_manifest->layout_templates.empty() &&
                !dsk_manifest_has_layout_template(*out_manifest, art.layout_template_id)) {
                return dsk_contract_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_INVALID_FIELD);
            }
        }
    }

    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static bool dsk_string_less(const std::string &a, const std::string &b) {
    return a < b;
}

static bool dsk_artifact_less(const dsk_artifact_t &a, const dsk_artifact_t &b) {
    if (a.artifact_id != b.artifact_id) {
        return a.artifact_id < b.artifact_id;
    }
    if (a.source_path != b.source_path) {
        return a.source_path < b.source_path;
    }
    return a.layout_template_id < b.layout_template_id;
}

static bool dsk_component_less(const dsk_manifest_component_t &a,
                               const dsk_manifest_component_t &b) {
    return a.component_id < b.component_id;
}

static bool dsk_layout_template_less(const dsk_layout_template_t &a,
                                     const dsk_layout_template_t &b) {
    return a.template_id < b.template_id;
}

dsk_status_t dsk_manifest_write(const dsk_manifest_t *manifest,
                                dsk_tlv_buffer_t *out_buf) {
    dsk_tlv_builder_t *builder;
    dsk_status_t st;
    std::vector<std::string> platforms;
    std::vector<dsk_manifest_component_t> components;
    dsk_u32 i;

    if (!manifest || !out_buf) {
        return dsk_contract_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }

    builder = dsk_tlv_builder_create();
    if (!builder) {
        return dsk_contract_error(DSK_CODE_INTERNAL_ERROR, DSK_SUBCODE_NONE);
    }

    st = dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_MANIFEST_PRODUCT_ID, manifest->product_id.c_str());
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_MANIFEST_VERSION, manifest->version.c_str());
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_MANIFEST_BUILD_ID, manifest->build_id.c_str());
    if (!dsk_error_is_ok(st)) goto done;

    platforms = manifest->supported_targets;
    std::sort(platforms.begin(), platforms.end(), dsk_string_less);
    {
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;
        for (i = 0u; i < platforms.size(); ++i) {
            dsk_tlv_builder_add_string(list_builder, DSK_TLV_TAG_PLATFORM_ENTRY, platforms[i].c_str());
        }
        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) goto done;
        st = dsk_tlv_builder_add_container(builder,
                                           DSK_TLV_TAG_MANIFEST_SUPPORTED_TARGETS,
                                           list_payload.data,
                                           list_payload.size);
        dsk_tlv_buffer_free(&list_payload);
        if (!dsk_error_is_ok(st)) goto done;
    }

    if (!manifest->allowed_splats.empty()) {
        std::vector<std::string> allow = manifest->allowed_splats;
        std::sort(allow.begin(), allow.end(), dsk_string_less);
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;
        for (i = 0u; i < allow.size(); ++i) {
            dsk_tlv_builder_add_string(list_builder,
                                       DSK_TLV_TAG_ALLOWED_SPLAT_ENTRY,
                                       allow[i].c_str());
        }
        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) goto done;
        st = dsk_tlv_builder_add_container(builder,
                                           DSK_TLV_TAG_MANIFEST_ALLOWED_SPLATS,
                                           list_payload.data,
                                           list_payload.size);
        dsk_tlv_buffer_free(&list_payload);
        if (!dsk_error_is_ok(st)) goto done;
    }

    if (!manifest->layout_templates.empty()) {
        std::vector<dsk_layout_template_t> layouts = manifest->layout_templates;
        std::sort(layouts.begin(), layouts.end(), dsk_layout_template_less);
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;
        for (i = 0u; i < layouts.size(); ++i) {
            const dsk_layout_template_t &layout = layouts[i];
            dsk_tlv_builder_t *entry_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t entry_payload;
            dsk_tlv_builder_add_string(entry_builder,
                                       DSK_TLV_TAG_LAYOUT_TEMPLATE_ID,
                                       layout.template_id.c_str());
            if (!layout.target_root.empty()) {
                dsk_tlv_builder_add_string(entry_builder,
                                           DSK_TLV_TAG_LAYOUT_TEMPLATE_TARGET_ROOT,
                                           layout.target_root.c_str());
            }
            if (!layout.path_prefix.empty()) {
                dsk_tlv_builder_add_string(entry_builder,
                                           DSK_TLV_TAG_LAYOUT_TEMPLATE_PATH_PREFIX,
                                           layout.path_prefix.c_str());
            }
            st = dsk_tlv_builder_finalize_payload(entry_builder, &entry_payload);
            dsk_tlv_builder_destroy(entry_builder);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(list_builder);
                goto done;
            }
            dsk_tlv_builder_add_container(list_builder,
                                          DSK_TLV_TAG_LAYOUT_TEMPLATE_ENTRY,
                                          entry_payload.data,
                                          entry_payload.size);
            dsk_tlv_buffer_free(&entry_payload);
        }
        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) goto done;
        st = dsk_tlv_builder_add_container(builder,
                                           DSK_TLV_TAG_MANIFEST_LAYOUT_TEMPLATES,
                                           list_payload.data,
                                           list_payload.size);
        dsk_tlv_buffer_free(&list_payload);
        if (!dsk_error_is_ok(st)) goto done;
    }

    components = manifest->components;
    std::sort(components.begin(), components.end(), dsk_component_less);
    {
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;

        for (i = 0u; i < components.size(); ++i) {
            const dsk_manifest_component_t &comp = components[i];
            dsk_tlv_builder_t *comp_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t comp_payload;
            dsk_u8 def = comp.default_selected ? 1u : 0u;

            dsk_tlv_builder_add_string(comp_builder, DSK_TLV_TAG_COMPONENT_ID, comp.component_id.c_str());
            if (!comp.component_version.empty()) {
                dsk_tlv_builder_add_string(comp_builder,
                                           DSK_TLV_TAG_COMPONENT_VERSION,
                                           comp.component_version.c_str());
            }
            dsk_tlv_builder_add_string(comp_builder, DSK_TLV_TAG_COMPONENT_KIND, comp.kind.c_str());
            dsk_tlv_builder_add_bytes(comp_builder, DSK_TLV_TAG_COMPONENT_DEFAULT_SELECTED, &def, 1u);

            {
                std::vector<std::string> deps = comp.deps;
                std::sort(deps.begin(), deps.end(), dsk_string_less);
                dsk_tlv_builder_t *deps_builder = dsk_tlv_builder_create();
                dsk_tlv_buffer_t deps_payload;
                dsk_u32 j;
                for (j = 0u; j < deps.size(); ++j) {
                    dsk_tlv_builder_add_string(deps_builder, DSK_TLV_TAG_COMPONENT_DEP_ENTRY, deps[j].c_str());
                }
                st = dsk_tlv_builder_finalize_payload(deps_builder, &deps_payload);
                dsk_tlv_builder_destroy(deps_builder);
                if (!dsk_error_is_ok(st)) {
                    dsk_tlv_builder_destroy(comp_builder);
                    goto done;
                }
                dsk_tlv_builder_add_container(comp_builder,
                                              DSK_TLV_TAG_COMPONENT_DEPS,
                                              deps_payload.data,
                                              deps_payload.size);
                dsk_tlv_buffer_free(&deps_payload);
            }

            {
                std::vector<std::string> conflicts = comp.conflicts;
                std::sort(conflicts.begin(), conflicts.end(), dsk_string_less);
                dsk_tlv_builder_t *conf_builder = dsk_tlv_builder_create();
                dsk_tlv_buffer_t conf_payload;
                dsk_u32 j;
                for (j = 0u; j < conflicts.size(); ++j) {
                    dsk_tlv_builder_add_string(conf_builder, DSK_TLV_TAG_COMPONENT_CONFLICT_ENTRY, conflicts[j].c_str());
                }
                st = dsk_tlv_builder_finalize_payload(conf_builder, &conf_payload);
                dsk_tlv_builder_destroy(conf_builder);
                if (!dsk_error_is_ok(st)) {
                    dsk_tlv_builder_destroy(comp_builder);
                    goto done;
                }
                dsk_tlv_builder_add_container(comp_builder,
                                              DSK_TLV_TAG_COMPONENT_CONFLICTS,
                                              conf_payload.data,
                                              conf_payload.size);
                dsk_tlv_buffer_free(&conf_payload);
            }

            if (!comp.supported_targets.empty()) {
                std::vector<std::string> targets = comp.supported_targets;
                std::sort(targets.begin(), targets.end(), dsk_string_less);
                dsk_tlv_builder_t *target_builder = dsk_tlv_builder_create();
                dsk_tlv_buffer_t target_payload;
                dsk_u32 j;
                for (j = 0u; j < targets.size(); ++j) {
                    dsk_tlv_builder_add_string(target_builder,
                                               DSK_TLV_TAG_COMPONENT_TARGET_ENTRY,
                                               targets[j].c_str());
                }
                st = dsk_tlv_builder_finalize_payload(target_builder, &target_payload);
                dsk_tlv_builder_destroy(target_builder);
                if (!dsk_error_is_ok(st)) {
                    dsk_tlv_builder_destroy(comp_builder);
                    goto done;
                }
                dsk_tlv_builder_add_container(comp_builder,
                                              DSK_TLV_TAG_COMPONENT_SUPPORTED_TARGETS,
                                              target_payload.data,
                                              target_payload.size);
                dsk_tlv_buffer_free(&target_payload);
            }

            {
                std::vector<dsk_artifact_t> artifacts = comp.artifacts;
                std::sort(artifacts.begin(), artifacts.end(), dsk_artifact_less);
                dsk_tlv_builder_t *art_builder = dsk_tlv_builder_create();
                dsk_tlv_buffer_t art_payload;
                dsk_u32 j;
                for (j = 0u; j < artifacts.size(); ++j) {
                    dsk_tlv_builder_t *entry_builder = dsk_tlv_builder_create();
                    dsk_tlv_buffer_t entry_payload;
                    if (!artifacts[j].artifact_id.empty()) {
                        dsk_tlv_builder_add_string(entry_builder,
                                                   DSK_TLV_TAG_ARTIFACT_ID,
                                                   artifacts[j].artifact_id.c_str());
                    }
                    if (!artifacts[j].hash.empty()) {
                        dsk_tlv_builder_add_string(entry_builder,
                                                   DSK_TLV_TAG_ARTIFACT_HASH,
                                                   artifacts[j].hash.c_str());
                    }
                    if (artifacts[j].digest64 != 0u) {
                        dsk_tlv_builder_add_u64(entry_builder,
                                                DSK_TLV_TAG_ARTIFACT_DIGEST64,
                                                artifacts[j].digest64);
                    }
                    dsk_tlv_builder_add_u64(entry_builder, DSK_TLV_TAG_ARTIFACT_SIZE, artifacts[j].size);
                    if (!artifacts[j].source_path.empty()) {
                        dsk_tlv_builder_add_string(entry_builder,
                                                   DSK_TLV_TAG_ARTIFACT_SOURCE_PATH,
                                                   artifacts[j].source_path.c_str());
                    }
                    if (!artifacts[j].layout_template_id.empty()) {
                        dsk_tlv_builder_add_string(entry_builder,
                                                   DSK_TLV_TAG_ARTIFACT_LAYOUT_TEMPLATE_ID,
                                                   artifacts[j].layout_template_id.c_str());
                    }
                    st = dsk_tlv_builder_finalize_payload(entry_builder, &entry_payload);
                    dsk_tlv_builder_destroy(entry_builder);
                    if (!dsk_error_is_ok(st)) {
                        dsk_tlv_builder_destroy(art_builder);
                        dsk_tlv_builder_destroy(comp_builder);
                        goto done;
                    }
                    dsk_tlv_builder_add_container(art_builder,
                                                  DSK_TLV_TAG_ARTIFACT_ENTRY,
                                                  entry_payload.data,
                                                  entry_payload.size);
                    dsk_tlv_buffer_free(&entry_payload);
                }
                st = dsk_tlv_builder_finalize_payload(art_builder, &art_payload);
                dsk_tlv_builder_destroy(art_builder);
                if (!dsk_error_is_ok(st)) {
                    dsk_tlv_builder_destroy(comp_builder);
                    goto done;
                }
                dsk_tlv_builder_add_container(comp_builder,
                                              DSK_TLV_TAG_COMPONENT_ARTIFACTS,
                                              art_payload.data,
                                              art_payload.size);
                dsk_tlv_buffer_free(&art_payload);
            }

            st = dsk_tlv_builder_finalize_payload(comp_builder, &comp_payload);
            dsk_tlv_builder_destroy(comp_builder);
            if (!dsk_error_is_ok(st)) goto done;
            dsk_tlv_builder_add_container(list_builder,
                                          DSK_TLV_TAG_COMPONENT_ENTRY,
                                          comp_payload.data,
                                          comp_payload.size);
            dsk_tlv_buffer_free(&comp_payload);
        }

        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) goto done;
        st = dsk_tlv_builder_add_container(builder,
                                           DSK_TLV_TAG_MANIFEST_COMPONENTS,
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
