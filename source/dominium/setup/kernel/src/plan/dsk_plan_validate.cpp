#include "dsk/dsk_plan.h"
#include "dsk/dsk_digest.h"

#include <algorithm>
#include <string.h>

static dsk_status_t dsk_plan_error(dsk_u16 code, dsk_u16 subcode) {
    return dsk_error_make(DSK_DOMAIN_KERNEL, code, subcode, DSK_ERROR_FLAG_USER_ACTIONABLE);
}

static dsk_status_t dsk_parse_u16(const dsk_tlv_record_t &rec, dsk_u16 *out) {
    if (!out) {
        return dsk_plan_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length != 2u) {
        return dsk_plan_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }
    *out = (dsk_u16)rec.payload[0] | (dsk_u16)((dsk_u16)rec.payload[1] << 8);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_parse_u32(const dsk_tlv_record_t &rec, dsk_u32 *out) {
    if (!out) {
        return dsk_plan_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length != 4u) {
        return dsk_plan_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }
    *out = (dsk_u32)rec.payload[0]
         | ((dsk_u32)rec.payload[1] << 8)
         | ((dsk_u32)rec.payload[2] << 16)
         | ((dsk_u32)rec.payload[3] << 24);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_parse_u64(const dsk_tlv_record_t &rec, dsk_u64 *out) {
    if (!out) {
        return dsk_plan_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length != 8u) {
        return dsk_plan_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
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

static dsk_status_t dsk_parse_string(const dsk_tlv_record_t &rec, std::string *out) {
    if (!out) {
        return dsk_plan_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    out->assign(reinterpret_cast<const char *>(rec.payload), rec.length);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

void dsk_plan_clear(dsk_plan_t *plan) {
    if (!plan) {
        return;
    }
    plan->product_id.clear();
    plan->product_version.clear();
    plan->selected_splat_id.clear();
    plan->selected_splat_caps_digest64 = 0u;
    plan->operation = 0u;
    plan->install_scope = 0u;
    plan->install_roots.clear();
    plan->payload_root.clear();
    plan->frontend_id.clear();
    plan->target_platform_triple.clear();
    plan->manifest_digest64 = 0u;
    plan->request_digest64 = 0u;
    plan->resolved_set_digest64 = 0u;
    plan->plan_digest64 = 0u;
    plan->resolved_components.clear();
    plan->ordered_steps.clear();
    plan->file_ops.clear();
    plan->registrations.shortcuts.clear();
    plan->registrations.file_associations.clear();
    plan->registrations.url_handlers.clear();
}

dsk_status_t dsk_plan_parse(const dsk_u8 *data, dsk_u32 size, dsk_plan_t *out_plan) {
    dsk_tlv_view_t view;
    dsk_status_t st;
    dsk_u32 i;

    if (!out_plan) {
        return dsk_plan_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    dsk_plan_clear(out_plan);

    st = dsk_tlv_parse(data, size, &view);
    if (!dsk_error_is_ok(st)) {
        return st;
    }

    for (i = 0u; i < view.record_count; ++i) {
        const dsk_tlv_record_t &rec = view.records[i];
        if (rec.type == DSK_TLV_TAG_PLAN_PRODUCT_ID) {
            st = dsk_parse_string(rec, &out_plan->product_id);
        } else if (rec.type == DSK_TLV_TAG_PLAN_PRODUCT_VERSION) {
            st = dsk_parse_string(rec, &out_plan->product_version);
        } else if (rec.type == DSK_TLV_TAG_PLAN_SELECTED_SPLAT_ID) {
            st = dsk_parse_string(rec, &out_plan->selected_splat_id);
        } else if (rec.type == DSK_TLV_TAG_PLAN_SELECTED_SPLAT_CAPS_DIGEST64) {
            st = dsk_parse_u64(rec, &out_plan->selected_splat_caps_digest64);
        } else if (rec.type == DSK_TLV_TAG_PLAN_OPERATION) {
            st = dsk_parse_u16(rec, &out_plan->operation);
        } else if (rec.type == DSK_TLV_TAG_PLAN_INSTALL_SCOPE) {
            st = dsk_parse_u16(rec, &out_plan->install_scope);
        } else if (rec.type == DSK_TLV_TAG_PLAN_MANIFEST_DIGEST64) {
            st = dsk_parse_u64(rec, &out_plan->manifest_digest64);
        } else if (rec.type == DSK_TLV_TAG_PLAN_REQUEST_DIGEST64) {
            st = dsk_parse_u64(rec, &out_plan->request_digest64);
        } else if (rec.type == DSK_TLV_TAG_PLAN_RESOLVED_SET_DIGEST64) {
            st = dsk_parse_u64(rec, &out_plan->resolved_set_digest64);
        } else if (rec.type == DSK_TLV_TAG_PLAN_DIGEST64) {
            st = dsk_parse_u64(rec, &out_plan->plan_digest64);
        } else if (rec.type == DSK_TLV_TAG_PLAN_PAYLOAD_ROOT) {
            st = dsk_parse_string(rec, &out_plan->payload_root);
        } else if (rec.type == DSK_TLV_TAG_PLAN_FRONTEND_ID) {
            st = dsk_parse_string(rec, &out_plan->frontend_id);
        } else if (rec.type == DSK_TLV_TAG_PLAN_TARGET_PLATFORM_TRIPLE) {
            st = dsk_parse_string(rec, &out_plan->target_platform_triple);
        } else if (rec.type == DSK_TLV_TAG_PLAN_INSTALL_ROOTS) {
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
                if (entry.type != DSK_TLV_TAG_PLAN_INSTALL_ROOT_ENTRY) {
                    continue;
                }
                std::string root;
                lst = dsk_parse_string(entry, &root);
                if (!dsk_error_is_ok(lst)) {
                    dsk_tlv_stream_destroy(&list_stream);
                    dsk_tlv_view_destroy(&view);
                    return lst;
                }
                out_plan->install_roots.push_back(root);
            }
            dsk_tlv_stream_destroy(&list_stream);
            st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        } else if (rec.type == DSK_TLV_TAG_PLAN_RESOLVED_COMPONENTS) {
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
                if (entry.type != DSK_TLV_TAG_PLAN_COMPONENT_ENTRY) {
                    continue;
                }
                dsk_tlv_stream_t comp_stream;
                dsk_resolved_component_t comp;
                dsk_u32 k;
                comp.source = 0u;
                lst = dsk_tlv_parse_stream(entry.payload, entry.length, &comp_stream);
                if (!dsk_error_is_ok(lst)) {
                    dsk_tlv_stream_destroy(&list_stream);
                    dsk_tlv_view_destroy(&view);
                    return lst;
                }
                for (k = 0u; k < comp_stream.record_count; ++k) {
                    const dsk_tlv_record_t &field = comp_stream.records[k];
                    if (field.type == DSK_TLV_TAG_PLAN_COMPONENT_ID) {
                        lst = dsk_parse_string(field, &comp.component_id);
                    } else if (field.type == DSK_TLV_TAG_PLAN_COMPONENT_VERSION) {
                        lst = dsk_parse_string(field, &comp.component_version);
                    } else if (field.type == DSK_TLV_TAG_PLAN_COMPONENT_KIND) {
                        lst = dsk_parse_string(field, &comp.kind);
                    } else if (field.type == DSK_TLV_TAG_PLAN_COMPONENT_SOURCE) {
                        dsk_u16 src;
                        lst = dsk_parse_u16(field, &src);
                        if (dsk_error_is_ok(lst)) {
                            comp.source = src;
                        }
                    } else {
                        continue;
                    }
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&comp_stream);
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_view_destroy(&view);
                        return lst;
                    }
                }
                dsk_tlv_stream_destroy(&comp_stream);
                out_plan->resolved_components.push_back(comp);
            }
            dsk_tlv_stream_destroy(&list_stream);
            st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        } else if (rec.type == DSK_TLV_TAG_PLAN_JOB_GRAPH) {
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
                if (entry.type != DSK_TLV_TAG_PLAN_STEP_ENTRY) {
                    continue;
                }
                dsk_tlv_stream_t step_stream;
                dsk_plan_step_t step;
                dsk_u32 k;
                step.step_id = 0u;
                step.step_kind = 0u;
                step.target_root_id = 0u;
                lst = dsk_tlv_parse_stream(entry.payload, entry.length, &step_stream);
                if (!dsk_error_is_ok(lst)) {
                    dsk_tlv_stream_destroy(&list_stream);
                    dsk_tlv_view_destroy(&view);
                    return lst;
                }
                for (k = 0u; k < step_stream.record_count; ++k) {
                    const dsk_tlv_record_t &field = step_stream.records[k];
                    if (field.type == DSK_TLV_TAG_PLAN_STEP_ID) {
                        lst = dsk_parse_u32(field, &step.step_id);
                    } else if (field.type == DSK_TLV_TAG_PLAN_STEP_KIND) {
                        dsk_u16 kind;
                        lst = dsk_parse_u16(field, &kind);
                        if (dsk_error_is_ok(lst)) {
                            step.step_kind = kind;
                        }
                    } else if (field.type == DSK_TLV_TAG_PLAN_STEP_COMPONENT_ID) {
                        lst = dsk_parse_string(field, &step.component_id);
                    } else if (field.type == DSK_TLV_TAG_PLAN_STEP_ARTIFACT_ID) {
                        lst = dsk_parse_string(field, &step.artifact_id);
                    } else if (field.type == DSK_TLV_TAG_PLAN_STEP_TARGET_ROOT_ID) {
                        lst = dsk_parse_u32(field, &step.target_root_id);
                    } else if (field.type == DSK_TLV_TAG_PLAN_STEP_INTENT) {
                        if (field.length != 0u) {
                            step.intent_tlv.assign(field.payload, field.payload + field.length);
                        }
                        lst = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
                    } else {
                        continue;
                    }
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&step_stream);
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_view_destroy(&view);
                        return lst;
                    }
                }
                dsk_tlv_stream_destroy(&step_stream);
                out_plan->ordered_steps.push_back(step);
            }
            dsk_tlv_stream_destroy(&list_stream);
            st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        } else if (rec.type == DSK_TLV_TAG_PLAN_FILE_OPS) {
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
                if (entry.type != DSK_TLV_TAG_PLAN_FILE_OP_ENTRY) {
                    continue;
                }
                dsk_tlv_stream_t op_stream;
                dsk_plan_file_op_t op;
                dsk_u32 k;
                op.op_kind = 0u;
                op.ownership = 0u;
                op.digest64 = 0u;
                op.size = 0u;
                op.target_root_id = 0u;
                lst = dsk_tlv_parse_stream(entry.payload, entry.length, &op_stream);
                if (!dsk_error_is_ok(lst)) {
                    dsk_tlv_stream_destroy(&list_stream);
                    dsk_tlv_view_destroy(&view);
                    return lst;
                }
                for (k = 0u; k < op_stream.record_count; ++k) {
                    const dsk_tlv_record_t &field = op_stream.records[k];
                    if (field.type == DSK_TLV_TAG_PLAN_FILE_OP_KIND) {
                        dsk_u16 kind;
                        lst = dsk_parse_u16(field, &kind);
                        if (dsk_error_is_ok(lst)) {
                            op.op_kind = kind;
                        }
                    } else if (field.type == DSK_TLV_TAG_PLAN_FILE_OP_FROM) {
                        lst = dsk_parse_string(field, &op.from_path);
                    } else if (field.type == DSK_TLV_TAG_PLAN_FILE_OP_TO) {
                        lst = dsk_parse_string(field, &op.to_path);
                    } else if (field.type == DSK_TLV_TAG_PLAN_FILE_OP_OWNERSHIP) {
                        dsk_u16 own;
                        lst = dsk_parse_u16(field, &own);
                        if (dsk_error_is_ok(lst)) {
                            op.ownership = own;
                        }
                    } else if (field.type == DSK_TLV_TAG_PLAN_FILE_OP_DIGEST64) {
                        lst = dsk_parse_u64(field, &op.digest64);
                    } else if (field.type == DSK_TLV_TAG_PLAN_FILE_OP_SIZE) {
                        lst = dsk_parse_u64(field, &op.size);
                    } else if (field.type == DSK_TLV_TAG_PLAN_FILE_OP_TARGET_ROOT_ID) {
                        lst = dsk_parse_u32(field, &op.target_root_id);
                    } else {
                        continue;
                    }
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&op_stream);
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_view_destroy(&view);
                        return lst;
                    }
                }
                dsk_tlv_stream_destroy(&op_stream);
                out_plan->file_ops.push_back(op);
            }
            dsk_tlv_stream_destroy(&list_stream);
            st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        } else if (rec.type == DSK_TLV_TAG_PLAN_REGISTRATIONS) {
            dsk_tlv_stream_t reg_stream;
            dsk_status_t lst;
            dsk_u32 j;
            lst = dsk_tlv_parse_stream(rec.payload, rec.length, &reg_stream);
            if (!dsk_error_is_ok(lst)) {
                dsk_tlv_view_destroy(&view);
                return lst;
            }
            for (j = 0u; j < reg_stream.record_count; ++j) {
                const dsk_tlv_record_t &field = reg_stream.records[j];
                dsk_tlv_stream_t list_stream;
                dsk_u32 k;
                if (field.type != DSK_TLV_TAG_PLAN_REG_SHORTCUTS &&
                    field.type != DSK_TLV_TAG_PLAN_REG_FILE_ASSOCS &&
                    field.type != DSK_TLV_TAG_PLAN_REG_URL_HANDLERS) {
                    continue;
                }
                lst = dsk_tlv_parse_stream(field.payload, field.length, &list_stream);
                if (!dsk_error_is_ok(lst)) {
                    dsk_tlv_stream_destroy(&reg_stream);
                    dsk_tlv_view_destroy(&view);
                    return lst;
                }
                for (k = 0u; k < list_stream.record_count; ++k) {
                    const dsk_tlv_record_t &entry = list_stream.records[k];
                    std::string value;
                    if (field.type == DSK_TLV_TAG_PLAN_REG_SHORTCUTS &&
                        entry.type == DSK_TLV_TAG_PLAN_REG_SHORTCUT_ENTRY) {
                        lst = dsk_parse_string(entry, &value);
                        if (dsk_error_is_ok(lst)) {
                            out_plan->registrations.shortcuts.push_back(value);
                        }
                    } else if (field.type == DSK_TLV_TAG_PLAN_REG_FILE_ASSOCS &&
                               entry.type == DSK_TLV_TAG_PLAN_REG_FILE_ASSOC_ENTRY) {
                        lst = dsk_parse_string(entry, &value);
                        if (dsk_error_is_ok(lst)) {
                            out_plan->registrations.file_associations.push_back(value);
                        }
                    } else if (field.type == DSK_TLV_TAG_PLAN_REG_URL_HANDLERS &&
                               entry.type == DSK_TLV_TAG_PLAN_REG_URL_HANDLER_ENTRY) {
                        lst = dsk_parse_string(entry, &value);
                        if (dsk_error_is_ok(lst)) {
                            out_plan->registrations.url_handlers.push_back(value);
                        }
                    } else {
                        continue;
                    }
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_stream_destroy(&reg_stream);
                        dsk_tlv_view_destroy(&view);
                        return lst;
                    }
                }
                dsk_tlv_stream_destroy(&list_stream);
            }
            dsk_tlv_stream_destroy(&reg_stream);
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
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static bool dsk_string_less(const std::string &a, const std::string &b) {
    return a < b;
}

static bool dsk_component_less(const dsk_resolved_component_t &a,
                               const dsk_resolved_component_t &b) {
    if (a.component_id != b.component_id) {
        return a.component_id < b.component_id;
    }
    return a.component_version < b.component_version;
}

static bool dsk_step_id_less(const dsk_plan_step_t &a,
                             const dsk_plan_step_t &b) {
    return a.step_id < b.step_id;
}

static bool dsk_file_op_less(const dsk_plan_file_op_t &a,
                             const dsk_plan_file_op_t &b) {
    if (a.target_root_id != b.target_root_id) {
        return a.target_root_id < b.target_root_id;
    }
    if (a.to_path != b.to_path) {
        return a.to_path < b.to_path;
    }
    if (a.from_path != b.from_path) {
        return a.from_path < b.from_path;
    }
    return a.op_kind < b.op_kind;
}

static dsk_u64 dsk_plan_resolved_digest(const dsk_plan_t *plan) {
    dsk_u64 hash = dsk_digest64_init();
    size_t i;
    const dsk_u8 zero = 0u;
    for (i = 0u; i < plan->resolved_components.size(); ++i) {
        const dsk_resolved_component_t &comp = plan->resolved_components[i];
        hash = dsk_digest64_update(hash,
                                   (const dsk_u8 *)comp.component_id.c_str(),
                                   (dsk_u32)comp.component_id.size());
        hash = dsk_digest64_update(hash, &zero, 1u);
        hash = dsk_digest64_update(hash,
                                   (const dsk_u8 *)comp.component_version.c_str(),
                                   (dsk_u32)comp.component_version.size());
        hash = dsk_digest64_update(hash, &zero, 1u);
    }
    return hash;
}

dsk_status_t dsk_plan_validate(const dsk_plan_t *plan) {
    size_t i;
    dsk_u64 digest;
    dsk_u64 resolved_digest;

    if (!plan) {
        return dsk_plan_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (plan->product_id.empty() ||
        plan->product_version.empty() ||
        plan->selected_splat_id.empty() ||
        plan->operation == 0u ||
        plan->install_scope == 0u ||
        plan->frontend_id.empty() ||
        plan->target_platform_triple.empty() ||
        plan->manifest_digest64 == 0u ||
        plan->request_digest64 == 0u ||
        plan->resolved_set_digest64 == 0u ||
        plan->plan_digest64 == 0u) {
        return dsk_plan_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_MISSING_FIELD);
    }
    if (!plan->file_ops.empty() && plan->payload_root.empty()) {
        return dsk_plan_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_MISSING_FIELD);
    }

    for (i = 1u; i < plan->install_roots.size(); ++i) {
        if (plan->install_roots[i] < plan->install_roots[i - 1u]) {
            return dsk_plan_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_INVALID_FIELD);
        }
    }

    for (i = 1u; i < plan->resolved_components.size(); ++i) {
        if (dsk_component_less(plan->resolved_components[i], plan->resolved_components[i - 1u])) {
            return dsk_plan_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_INVALID_FIELD);
        }
    }

    for (i = 1u; i < plan->ordered_steps.size(); ++i) {
        if (dsk_step_id_less(plan->ordered_steps[i], plan->ordered_steps[i - 1u])) {
            return dsk_plan_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_INVALID_FIELD);
        }
    }

    for (i = 1u; i < plan->file_ops.size(); ++i) {
        if (dsk_file_op_less(plan->file_ops[i], plan->file_ops[i - 1u])) {
            return dsk_plan_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_INVALID_FIELD);
        }
    }
    for (i = 0u; i < plan->file_ops.size(); ++i) {
        if (plan->file_ops[i].target_root_id >= plan->install_roots.size()) {
            return dsk_plan_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_INVALID_FIELD);
        }
    }

    resolved_digest = dsk_plan_resolved_digest(plan);
    if (resolved_digest != plan->resolved_set_digest64) {
        return dsk_plan_error(DSK_CODE_INTEGRITY_ERROR, DSK_SUBCODE_PLAN_RESOLVED_DIGEST_MISMATCH);
    }

    digest = dsk_plan_payload_digest(plan);
    if (digest != plan->plan_digest64) {
        return dsk_plan_error(DSK_CODE_INTEGRITY_ERROR, DSK_SUBCODE_PLAN_DIGEST_MISMATCH);
    }

    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

dsk_status_t dsk_plan_write(const dsk_plan_t *plan, dsk_tlv_buffer_t *out_buf) {
    dsk_tlv_builder_t *builder;
    dsk_status_t st;
    dsk_u32 i;
    dsk_plan_t working;
    std::vector<std::string> roots;
    std::vector<dsk_resolved_component_t> components;
    std::vector<dsk_plan_step_t> steps;
    std::vector<dsk_plan_file_op_t> file_ops;

    if (!plan || !out_buf) {
        return dsk_plan_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }

    working = *plan;

    builder = dsk_tlv_builder_create();
    if (!builder) {
        return dsk_plan_error(DSK_CODE_INTERNAL_ERROR, DSK_SUBCODE_NONE);
    }

    st = dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_PLAN_PRODUCT_ID, working.product_id.c_str());
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_PLAN_PRODUCT_VERSION, working.product_version.c_str());
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_PLAN_SELECTED_SPLAT_ID, working.selected_splat_id.c_str());
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_u64(builder,
                                 DSK_TLV_TAG_PLAN_SELECTED_SPLAT_CAPS_DIGEST64,
                                 working.selected_splat_caps_digest64);
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_u16(builder, DSK_TLV_TAG_PLAN_OPERATION, working.operation);
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_u16(builder, DSK_TLV_TAG_PLAN_INSTALL_SCOPE, working.install_scope);
    if (!dsk_error_is_ok(st)) goto done;
    if (!working.payload_root.empty()) {
        st = dsk_tlv_builder_add_string(builder,
                                        DSK_TLV_TAG_PLAN_PAYLOAD_ROOT,
                                        working.payload_root.c_str());
        if (!dsk_error_is_ok(st)) goto done;
    }
    st = dsk_tlv_builder_add_string(builder,
                                    DSK_TLV_TAG_PLAN_FRONTEND_ID,
                                    working.frontend_id.c_str());
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_string(builder,
                                    DSK_TLV_TAG_PLAN_TARGET_PLATFORM_TRIPLE,
                                    working.target_platform_triple.c_str());
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_u64(builder, DSK_TLV_TAG_PLAN_MANIFEST_DIGEST64, working.manifest_digest64);
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_u64(builder, DSK_TLV_TAG_PLAN_REQUEST_DIGEST64, working.request_digest64);
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_u64(builder,
                                 DSK_TLV_TAG_PLAN_RESOLVED_SET_DIGEST64,
                                 working.resolved_set_digest64);
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_u64(builder, DSK_TLV_TAG_PLAN_DIGEST64, working.plan_digest64);
    if (!dsk_error_is_ok(st)) goto done;

    roots = working.install_roots;
    std::sort(roots.begin(), roots.end(), dsk_string_less);
    {
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;
        for (i = 0u; i < roots.size(); ++i) {
            dsk_tlv_builder_add_string(list_builder,
                                       DSK_TLV_TAG_PLAN_INSTALL_ROOT_ENTRY,
                                       roots[i].c_str());
        }
        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) goto done;
        st = dsk_tlv_builder_add_container(builder,
                                           DSK_TLV_TAG_PLAN_INSTALL_ROOTS,
                                           list_payload.data,
                                           list_payload.size);
        dsk_tlv_buffer_free(&list_payload);
        if (!dsk_error_is_ok(st)) goto done;
    }

    components = working.resolved_components;
    std::sort(components.begin(), components.end(), dsk_component_less);
    {
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;
        for (i = 0u; i < components.size(); ++i) {
            const dsk_resolved_component_t &comp = components[i];
            dsk_tlv_builder_t *entry_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t entry_payload;
            dsk_tlv_builder_add_string(entry_builder,
                                       DSK_TLV_TAG_PLAN_COMPONENT_ID,
                                       comp.component_id.c_str());
            dsk_tlv_builder_add_string(entry_builder,
                                       DSK_TLV_TAG_PLAN_COMPONENT_VERSION,
                                       comp.component_version.c_str());
            dsk_tlv_builder_add_string(entry_builder,
                                       DSK_TLV_TAG_PLAN_COMPONENT_KIND,
                                       comp.kind.c_str());
            dsk_tlv_builder_add_u16(entry_builder,
                                    DSK_TLV_TAG_PLAN_COMPONENT_SOURCE,
                                    comp.source);
            st = dsk_tlv_builder_finalize_payload(entry_builder, &entry_payload);
            dsk_tlv_builder_destroy(entry_builder);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(list_builder);
                goto done;
            }
            dsk_tlv_builder_add_container(list_builder,
                                          DSK_TLV_TAG_PLAN_COMPONENT_ENTRY,
                                          entry_payload.data,
                                          entry_payload.size);
            dsk_tlv_buffer_free(&entry_payload);
        }
        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) goto done;
        st = dsk_tlv_builder_add_container(builder,
                                           DSK_TLV_TAG_PLAN_RESOLVED_COMPONENTS,
                                           list_payload.data,
                                           list_payload.size);
        dsk_tlv_buffer_free(&list_payload);
        if (!dsk_error_is_ok(st)) goto done;
    }

    steps = working.ordered_steps;
    std::sort(steps.begin(), steps.end(), dsk_step_id_less);
    {
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;
        for (i = 0u; i < steps.size(); ++i) {
            const dsk_plan_step_t &step = steps[i];
            dsk_tlv_builder_t *entry_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t entry_payload;
            dsk_tlv_builder_add_u32(entry_builder, DSK_TLV_TAG_PLAN_STEP_ID, step.step_id);
            dsk_tlv_builder_add_u16(entry_builder, DSK_TLV_TAG_PLAN_STEP_KIND, step.step_kind);
            if (!step.component_id.empty()) {
                dsk_tlv_builder_add_string(entry_builder,
                                           DSK_TLV_TAG_PLAN_STEP_COMPONENT_ID,
                                           step.component_id.c_str());
            }
            if (!step.artifact_id.empty()) {
                dsk_tlv_builder_add_string(entry_builder,
                                           DSK_TLV_TAG_PLAN_STEP_ARTIFACT_ID,
                                           step.artifact_id.c_str());
            }
            dsk_tlv_builder_add_u32(entry_builder,
                                    DSK_TLV_TAG_PLAN_STEP_TARGET_ROOT_ID,
                                    step.target_root_id);
            if (!step.intent_tlv.empty()) {
                dsk_tlv_builder_add_bytes(entry_builder,
                                          DSK_TLV_TAG_PLAN_STEP_INTENT,
                                          &step.intent_tlv[0],
                                          (dsk_u32)step.intent_tlv.size());
            }
            st = dsk_tlv_builder_finalize_payload(entry_builder, &entry_payload);
            dsk_tlv_builder_destroy(entry_builder);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(list_builder);
                goto done;
            }
            dsk_tlv_builder_add_container(list_builder,
                                          DSK_TLV_TAG_PLAN_STEP_ENTRY,
                                          entry_payload.data,
                                          entry_payload.size);
            dsk_tlv_buffer_free(&entry_payload);
        }
        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) goto done;
        st = dsk_tlv_builder_add_container(builder,
                                           DSK_TLV_TAG_PLAN_JOB_GRAPH,
                                           list_payload.data,
                                           list_payload.size);
        dsk_tlv_buffer_free(&list_payload);
        if (!dsk_error_is_ok(st)) goto done;
    }

    file_ops = working.file_ops;
    std::sort(file_ops.begin(), file_ops.end(), dsk_file_op_less);
    {
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;
        for (i = 0u; i < file_ops.size(); ++i) {
            const dsk_plan_file_op_t &op = file_ops[i];
            dsk_tlv_builder_t *entry_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t entry_payload;
            dsk_tlv_builder_add_u16(entry_builder, DSK_TLV_TAG_PLAN_FILE_OP_KIND, op.op_kind);
            if (!op.from_path.empty()) {
                dsk_tlv_builder_add_string(entry_builder,
                                           DSK_TLV_TAG_PLAN_FILE_OP_FROM,
                                           op.from_path.c_str());
            }
            if (!op.to_path.empty()) {
                dsk_tlv_builder_add_string(entry_builder,
                                           DSK_TLV_TAG_PLAN_FILE_OP_TO,
                                           op.to_path.c_str());
            }
            dsk_tlv_builder_add_u16(entry_builder,
                                    DSK_TLV_TAG_PLAN_FILE_OP_OWNERSHIP,
                                    op.ownership);
            dsk_tlv_builder_add_u64(entry_builder,
                                    DSK_TLV_TAG_PLAN_FILE_OP_DIGEST64,
                                    op.digest64);
            dsk_tlv_builder_add_u64(entry_builder,
                                    DSK_TLV_TAG_PLAN_FILE_OP_SIZE,
                                    op.size);
            dsk_tlv_builder_add_u32(entry_builder,
                                    DSK_TLV_TAG_PLAN_FILE_OP_TARGET_ROOT_ID,
                                    op.target_root_id);
            st = dsk_tlv_builder_finalize_payload(entry_builder, &entry_payload);
            dsk_tlv_builder_destroy(entry_builder);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(list_builder);
                goto done;
            }
            dsk_tlv_builder_add_container(list_builder,
                                          DSK_TLV_TAG_PLAN_FILE_OP_ENTRY,
                                          entry_payload.data,
                                          entry_payload.size);
            dsk_tlv_buffer_free(&entry_payload);
        }
        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) goto done;
        st = dsk_tlv_builder_add_container(builder,
                                           DSK_TLV_TAG_PLAN_FILE_OPS,
                                           list_payload.data,
                                           list_payload.size);
        dsk_tlv_buffer_free(&list_payload);
        if (!dsk_error_is_ok(st)) goto done;
    }

    {
        dsk_tlv_builder_t *reg_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t reg_payload;
        if (!working.registrations.shortcuts.empty()) {
            dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t list_payload;
            for (i = 0u; i < working.registrations.shortcuts.size(); ++i) {
                dsk_tlv_builder_add_string(list_builder,
                                           DSK_TLV_TAG_PLAN_REG_SHORTCUT_ENTRY,
                                           working.registrations.shortcuts[i].c_str());
            }
            st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
            dsk_tlv_builder_destroy(list_builder);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(reg_builder);
                goto done;
            }
            dsk_tlv_builder_add_container(reg_builder,
                                          DSK_TLV_TAG_PLAN_REG_SHORTCUTS,
                                          list_payload.data,
                                          list_payload.size);
            dsk_tlv_buffer_free(&list_payload);
        }
        if (!working.registrations.file_associations.empty()) {
            dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t list_payload;
            for (i = 0u; i < working.registrations.file_associations.size(); ++i) {
                dsk_tlv_builder_add_string(list_builder,
                                           DSK_TLV_TAG_PLAN_REG_FILE_ASSOC_ENTRY,
                                           working.registrations.file_associations[i].c_str());
            }
            st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
            dsk_tlv_builder_destroy(list_builder);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(reg_builder);
                goto done;
            }
            dsk_tlv_builder_add_container(reg_builder,
                                          DSK_TLV_TAG_PLAN_REG_FILE_ASSOCS,
                                          list_payload.data,
                                          list_payload.size);
            dsk_tlv_buffer_free(&list_payload);
        }
        if (!working.registrations.url_handlers.empty()) {
            dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t list_payload;
            for (i = 0u; i < working.registrations.url_handlers.size(); ++i) {
                dsk_tlv_builder_add_string(list_builder,
                                           DSK_TLV_TAG_PLAN_REG_URL_HANDLER_ENTRY,
                                           working.registrations.url_handlers[i].c_str());
            }
            st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
            dsk_tlv_builder_destroy(list_builder);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(reg_builder);
                goto done;
            }
            dsk_tlv_builder_add_container(reg_builder,
                                          DSK_TLV_TAG_PLAN_REG_URL_HANDLERS,
                                          list_payload.data,
                                          list_payload.size);
            dsk_tlv_buffer_free(&list_payload);
        }
        st = dsk_tlv_builder_finalize_payload(reg_builder, &reg_payload);
        dsk_tlv_builder_destroy(reg_builder);
        if (!dsk_error_is_ok(st)) goto done;
        st = dsk_tlv_builder_add_container(builder,
                                           DSK_TLV_TAG_PLAN_REGISTRATIONS,
                                           reg_payload.data,
                                           reg_payload.size);
        dsk_tlv_buffer_free(&reg_payload);
        if (!dsk_error_is_ok(st)) goto done;
    }

    st = dsk_tlv_builder_finalize(builder, out_buf);

done:
    dsk_tlv_builder_destroy(builder);
    return st;
}
