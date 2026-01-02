#include "dsk/dsk_plan.h"

#include <algorithm>
#include <cstdio>

static void append_json_escape(std::string &out, const std::string &value) {
    size_t i;
    for (i = 0u; i < value.size(); ++i) {
        char c = value[i];
        switch (c) {
        case '\\':
        case '"':
            out.push_back('\\');
            out.push_back(c);
            break;
        case '\n':
            out.append("\\n");
            break;
        case '\r':
            out.append("\\r");
            break;
        case '\t':
            out.append("\\t");
            break;
        default:
            out.push_back(c);
            break;
        }
    }
}

static void append_json_string(std::string &out, const std::string &value) {
    out.push_back('"');
    append_json_escape(out, value);
    out.push_back('"');
}

static void append_json_u64_hex(std::string &out, dsk_u64 value) {
    char buf[17];
    std::snprintf(buf, sizeof(buf), "%016llx", (unsigned long long)value);
    out.append("\"0x");
    out.append(buf);
    out.push_back('"');
}

static void append_json_u32(std::string &out, dsk_u32 value) {
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%u", (unsigned)value);
    out.append(buf);
}

static void append_json_u64_dec(std::string &out, dsk_u64 value) {
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%llu", (unsigned long long)value);
    out.append(buf);
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

static bool dsk_step_less(const dsk_plan_step_t &a, const dsk_plan_step_t &b) {
    return a.step_id < b.step_id;
}

static bool dsk_file_op_less(const dsk_plan_file_op_t &a, const dsk_plan_file_op_t &b) {
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

dsk_status_t dsk_plan_dump_json(const dsk_plan_t *plan, std::string *out_json) {
    std::vector<std::string> roots;
    std::vector<dsk_resolved_component_t> components;
    std::vector<dsk_plan_step_t> steps;
    std::vector<dsk_plan_file_op_t> file_ops;
    std::vector<std::string> shortcuts;
    std::vector<std::string> file_assocs;
    std::vector<std::string> url_handlers;
    size_t i;

    if (!plan || !out_json) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }

    roots = plan->install_roots;
    components = plan->resolved_components;
    steps = plan->ordered_steps;
    file_ops = plan->file_ops;
    shortcuts = plan->registrations.shortcuts;
    file_assocs = plan->registrations.file_associations;
    url_handlers = plan->registrations.url_handlers;

    std::sort(roots.begin(), roots.end(), dsk_string_less);
    std::sort(components.begin(), components.end(), dsk_component_less);
    std::sort(steps.begin(), steps.end(), dsk_step_less);
    std::sort(file_ops.begin(), file_ops.end(), dsk_file_op_less);
    std::sort(shortcuts.begin(), shortcuts.end(), dsk_string_less);
    std::sort(file_assocs.begin(), file_assocs.end(), dsk_string_less);
    std::sort(url_handlers.begin(), url_handlers.end(), dsk_string_less);

    out_json->clear();
    out_json->append("{\"product_id\":");
    append_json_string(*out_json, plan->product_id);
    out_json->append(",\"product_version\":");
    append_json_string(*out_json, plan->product_version);
    out_json->append(",\"selected_splat_id\":");
    append_json_string(*out_json, plan->selected_splat_id);
    out_json->append(",\"selected_splat_caps_digest64\":");
    append_json_u64_hex(*out_json, plan->selected_splat_caps_digest64);
    out_json->append(",\"operation\":");
    append_json_u32(*out_json, plan->operation);
    out_json->append(",\"install_scope\":");
    append_json_u32(*out_json, plan->install_scope);
    out_json->append(",\"payload_root\":");
    append_json_string(*out_json, plan->payload_root);
    out_json->append(",\"frontend_id\":");
    append_json_string(*out_json, plan->frontend_id);
    out_json->append(",\"target_platform_triple\":");
    append_json_string(*out_json, plan->target_platform_triple);

    out_json->append(",\"install_roots\":[");
    for (i = 0u; i < roots.size(); ++i) {
        if (i != 0u) out_json->push_back(',');
        append_json_string(*out_json, roots[i]);
    }
    out_json->append("]");

    out_json->append(",\"manifest_digest64\":");
    append_json_u64_hex(*out_json, plan->manifest_digest64);
    out_json->append(",\"request_digest64\":");
    append_json_u64_hex(*out_json, plan->request_digest64);
    out_json->append(",\"resolved_set_digest64\":");
    append_json_u64_hex(*out_json, plan->resolved_set_digest64);
    out_json->append(",\"plan_digest64\":");
    append_json_u64_hex(*out_json, plan->plan_digest64);

    out_json->append(",\"resolved_components\":[");
    for (i = 0u; i < components.size(); ++i) {
        if (i != 0u) out_json->push_back(',');
        out_json->append("{\"component_id\":");
        append_json_string(*out_json, components[i].component_id);
        out_json->append(",\"component_version\":");
        append_json_string(*out_json, components[i].component_version);
        out_json->append(",\"kind\":");
        append_json_string(*out_json, components[i].kind);
        out_json->append(",\"source\":");
        append_json_u32(*out_json, components[i].source);
        out_json->append("}");
    }
    out_json->append("]");

    out_json->append(",\"ordered_steps\":[");
    for (i = 0u; i < steps.size(); ++i) {
        if (i != 0u) out_json->push_back(',');
        out_json->append("{\"step_id\":");
        append_json_u32(*out_json, steps[i].step_id);
        out_json->append(",\"step_kind\":");
        append_json_u32(*out_json, steps[i].step_kind);
        out_json->append(",\"component_id\":");
        append_json_string(*out_json, steps[i].component_id);
        out_json->append(",\"artifact_id\":");
        append_json_string(*out_json, steps[i].artifact_id);
        out_json->append(",\"target_root_id\":");
        append_json_u32(*out_json, steps[i].target_root_id);
        out_json->append("}");
    }
    out_json->append("]");

    out_json->append(",\"file_operations\":[");
    for (i = 0u; i < file_ops.size(); ++i) {
        if (i != 0u) out_json->push_back(',');
        out_json->append("{\"op_kind\":");
        append_json_u32(*out_json, file_ops[i].op_kind);
        out_json->append(",\"from\":");
        append_json_string(*out_json, file_ops[i].from_path);
        out_json->append(",\"to\":");
        append_json_string(*out_json, file_ops[i].to_path);
        out_json->append(",\"ownership\":");
        append_json_u32(*out_json, file_ops[i].ownership);
        out_json->append(",\"digest64\":");
        append_json_u64_hex(*out_json, file_ops[i].digest64);
        out_json->append(",\"size\":");
        append_json_u64_dec(*out_json, file_ops[i].size);
        out_json->append(",\"target_root_id\":");
        append_json_u32(*out_json, file_ops[i].target_root_id);
        out_json->append("}");
    }
    out_json->append("]");

    out_json->append(",\"registrations\":{");
    out_json->append("\"shortcuts\":[");
    for (i = 0u; i < shortcuts.size(); ++i) {
        if (i != 0u) out_json->push_back(',');
        append_json_string(*out_json, shortcuts[i]);
    }
    out_json->append("],\"file_associations\":[");
    for (i = 0u; i < file_assocs.size(); ++i) {
        if (i != 0u) out_json->push_back(',');
        append_json_string(*out_json, file_assocs[i]);
    }
    out_json->append("],\"url_handlers\":[");
    for (i = 0u; i < url_handlers.size(); ++i) {
        if (i != 0u) out_json->push_back(',');
        append_json_string(*out_json, url_handlers[i]);
    }
    out_json->append("]}");

    out_json->append("}");
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}
