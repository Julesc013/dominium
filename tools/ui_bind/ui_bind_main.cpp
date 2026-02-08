/*
FILE: tools/ui_bind/ui_bind_main.cpp
MODULE: Dominium
PURPOSE: UI_BIND_PHASE tool - validate UI IR bindings and generate binding outputs.
NOTES: Deterministic; no side effects unless --write is used.
*/
#include "ui_bind_index.h"

#include <algorithm>
#include <cstdio>
#include <cstring>
#include <map>
#include <set>
#include <string>
#include <vector>

#include "ui_ir_diag.h"
#include "ui_ir_doc.h"
#include "ui_ir_tlv.h"
#include "ui_ir_props.h"
#include "command/command_registry.h"

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#else
#include <errno.h>
#include <sys/stat.h>
#endif
typedef struct bind_entry {
    std::string ui_element_id;
    std::string event_name;
    std::string action_key;
    unsigned int command_id;
} bind_entry;

typedef struct accessibility_entry {
    std::string ui_element_id;
    std::string name;
    std::string role;
    std::string description;
    std::string localization_key;
} accessibility_entry;

static void print_usage(void)
{
    std::fprintf(stderr,
                 "usage: tool_ui_bind --repo-root <path> --ui-index <path> --out-dir <path> (--check|--write)\n");
}

static bool is_abs_path(const std::string& path)
{
    if (path.size() >= 2u && path[1] == ':') {
        return true;
    }
    if (!path.empty() && (path[0] == '/' || path[0] == '\\')) {
        return true;
    }
    return false;
}

static std::string join_path(const std::string& root, const std::string& rel)
{
    if (rel.empty()) {
        return rel;
    }
    if (is_abs_path(rel)) {
        return rel;
    }
    if (root.empty()) {
        return rel;
    }
    if (root[root.size() - 1] == '/' || root[root.size() - 1] == '\\') {
        return root + rel;
    }
    return root + "/" + rel;
}

static bool is_interactive_type(domui_widget_type t)
{
    switch (t) {
    case DOMUI_WIDGET_BUTTON:
    case DOMUI_WIDGET_EDIT:
    case DOMUI_WIDGET_LISTBOX:
    case DOMUI_WIDGET_COMBOBOX:
    case DOMUI_WIDGET_CHECKBOX:
    case DOMUI_WIDGET_RADIO:
    case DOMUI_WIDGET_TAB:
    case DOMUI_WIDGET_TREEVIEW:
    case DOMUI_WIDGET_LISTVIEW:
    case DOMUI_WIDGET_SLIDER:
    case DOMUI_WIDGET_TABS:
    case DOMUI_WIDGET_TAB_PAGE:
        return true;
    default:
        break;
    }
    return false;
}

static bool get_prop_string(const domui_props& props, const char* key, std::string& out)
{
    domui_value value;
    out.clear();
    if (!props.get(key, &value)) {
        return false;
    }
    if (value.type != DOMUI_VALUE_STRING) {
        return false;
    }
    out = value.v_string.c_str();
    return !out.empty();
}

static bool prop_has_enabled_predicate(const domui_props& props, std::string& out_value)
{
    domui_value value;
    out_value.clear();
    if (!props.get("enabled_if", &value) && !props.get("ui.enabled_if", &value)) {
        return false;
    }
    if (value.type != DOMUI_VALUE_STRING) {
        return true;
    }
    out_value = value.v_string.c_str();
    return true;
}

static bool enabled_predicate_allowed(const std::string& predicate)
{
    if (predicate.empty()) {
        return false;
    }
    if (predicate == "instance.selected") {
        return true;
    }
    if (predicate == "profile.present") {
        return true;
    }
    if (predicate == "epistemic_permission") {
        return true;
    }
    if (predicate.size() > 11u && predicate.find("capability:") == 0u) {
        return predicate.size() > 11u;
    }
    if (predicate.size() > 21u && predicate.find("epistemic_permission:") == 0u) {
        return predicate.size() > 21u;
    }
    return false;
}

static bool command_epistemic_scope_known(const char* scope)
{
    if (!scope || !scope[0]) {
        return false;
    }
    if (strcmp(scope, DOM_EPISTEMIC_SCOPE_OBS_ONLY) == 0) return true;
    if (strcmp(scope, DOM_EPISTEMIC_SCOPE_MEMORY_ONLY) == 0) return true;
    if (strcmp(scope, DOM_EPISTEMIC_SCOPE_PARTIAL) == 0) return true;
    if (strcmp(scope, DOM_EPISTEMIC_SCOPE_FULL) == 0) return true;
    return false;
}

static bool write_file_text(const char* path, const std::string& content)
{
    FILE* f = std::fopen(path, "wb");
    if (!f) {
        return false;
    }
    if (!content.empty()) {
        size_t wrote = std::fwrite(content.data(), 1u, content.size(), f);
        if (wrote != content.size()) {
            std::fclose(f);
            return false;
        }
    }
    std::fflush(f);
    return std::fclose(f) == 0;
}

static bool read_file_text(const char* path, std::string& out)
{
    FILE* f = std::fopen(path, "rb");
    long size = 0;
    out.clear();
    if (!f) {
        return false;
    }
    if (std::fseek(f, 0L, SEEK_END) != 0) {
        std::fclose(f);
        return false;
    }
    size = std::ftell(f);
    if (size < 0) {
        std::fclose(f);
        return false;
    }
    if (std::fseek(f, 0L, SEEK_SET) != 0) {
        std::fclose(f);
        return false;
    }
    if (size == 0) {
        std::fclose(f);
        return true;
    }
    out.resize((size_t)size);
    if (std::fread(&out[0], 1u, (size_t)size, f) != (size_t)size) {
        std::fclose(f);
        return false;
    }
    std::fclose(f);
    return true;
}

static std::string c_escape(const std::string& value)
{
    std::string out;
    size_t i;
    out.reserve(value.size() + 8u);
    for (i = 0u; i < value.size(); ++i) {
        char c = value[i];
        switch (c) {
        case '\\': out += "\\\\"; break;
        case '\"': out += "\\\""; break;
        case '\n': out += "\\n"; break;
        case '\r': out += "\\r"; break;
        case '\t': out += "\\t"; break;
        default:
            out.push_back(c);
            break;
        }
    }
    return out;
}

static std::string json_escape(const std::string& value)
{
    std::string out;
    size_t i;
    out.reserve(value.size() + 8u);
    for (i = 0u; i < value.size(); ++i) {
        char c = value[i];
        switch (c) {
        case '\\': out += "\\\\"; break;
        case '\"': out += "\\\""; break;
        case '\n': out += "\\n"; break;
        case '\r': out += "\\r"; break;
        case '\t': out += "\\t"; break;
        default:
            out.push_back(c);
            break;
        }
    }
    return out;
}

static std::string make_ui_element_id(const std::string& doc_name, const std::string& widget_name)
{
    std::string out = doc_name;
    out += "#";
    out += widget_name;
    return out;
}

static void build_command_map(std::map<std::string, std::vector<const dom_app_command_desc*> >& out)
{
    u32 count = 0u;
    u32 i;
    const dom_app_command_desc* cmds = appcore_command_registry(&count);
    out.clear();
    for (i = 0u; i < count; ++i) {
        const char* name = cmds[i].name ? cmds[i].name : "";
        out[name].push_back(&cmds[i]);
    }
}

static bool command_schema_known(const char* schema)
{
    if (!schema || !schema[0]) {
        return false;
    }
    if (strcmp(schema, DOM_APP_ARG_SCHEMA_NONE) == 0) return true;
    if (strcmp(schema, DOM_APP_ARG_SCHEMA_ARGS) == 0) return true;
    if (strcmp(schema, DOM_APP_ARG_SCHEMA_PATH) == 0) return true;
    if (strcmp(schema, DOM_APP_ARG_SCHEMA_INSTANCE_ID) == 0) return true;
    if (strcmp(schema, DOM_APP_ARG_SCHEMA_SUBCOMMAND) == 0) return true;
    return false;
}

struct bind_entry_less {
    bool operator()(const bind_entry& a, const bind_entry& b) const
    {
        if (a.ui_element_id != b.ui_element_id) return a.ui_element_id < b.ui_element_id;
        if (a.event_name != b.event_name) return a.event_name < b.event_name;
        if (a.action_key != b.action_key) return a.action_key < b.action_key;
        return a.command_id < b.command_id;
    }
};

struct accessibility_entry_less {
    bool operator()(const accessibility_entry& a, const accessibility_entry& b) const
    {
        if (a.ui_element_id != b.ui_element_id) return a.ui_element_id < b.ui_element_id;
        return a.localization_key < b.localization_key;
    }
};

static void emit_binding_header(std::string& out)
{
    out.clear();
    out += "/*\n";
    out += "AUTO-GENERATED by tool_ui_bind. DO NOT EDIT.\n";
    out += "*/\n";
    out += "#ifndef DOMINIUM_APPCORE_UI_COMMAND_BINDING_TABLE_H\n";
    out += "#define DOMINIUM_APPCORE_UI_COMMAND_BINDING_TABLE_H\n\n";
    out += "#include \"command/command_registry.h\"\n\n";
    out += "#ifdef __cplusplus\nextern \"C\" {\n#endif\n\n";
    out += "typedef struct dom_ui_command_binding {\n";
    out += "    const char* ui_element_id;\n";
    out += "    const char* event_name;\n";
    out += "    const char* action_key;\n";
    out += "    u32 command_id;\n";
    out += "} dom_ui_command_binding;\n\n";
    out += "const dom_ui_command_binding* appcore_ui_command_bindings(u32* out_count);\n";
    out += "const dom_ui_command_binding* appcore_ui_command_find_action(const char* action_key);\n";
    out += "const dom_ui_command_binding* appcore_ui_command_find_element_event(const char* ui_element_id,\n";
    out += "                                                                    const char* event_name);\n";
    out += "const dom_app_command_desc* appcore_ui_command_desc_for_action(const char* action_key);\n\n";
    out += "#ifdef __cplusplus\n} /* extern \"C\" */\n#endif\n\n";
    out += "#endif /* DOMINIUM_APPCORE_UI_COMMAND_BINDING_TABLE_H */\n";
}

static void emit_binding_source(std::string& out, const std::vector<bind_entry>& entries)
{
    size_t i;
    out.clear();
    out += "/*\n";
    out += "AUTO-GENERATED by tool_ui_bind. DO NOT EDIT.\n";
    out += "*/\n";
    out += "#include \"ui_bind/ui_command_binding_table.h\"\n";
    out += "#include <string.h>\n\n";
    out += "static const dom_ui_command_binding k_ui_bindings[] = {\n";
    for (i = 0u; i < entries.size(); ++i) {
        const bind_entry& e = entries[i];
        out += "    { \"";
        out += c_escape(e.ui_element_id);
        out += "\", \"";
        out += c_escape(e.event_name);
        out += "\", \"";
        out += c_escape(e.action_key);
        out += "\", ";
        {
            char buf[32];
            std::sprintf(buf, "%u", e.command_id);
            out += buf;
        }
        out += " }";
        if (i + 1u < entries.size()) {
            out += ",";
        }
        out += "\n";
    }
    out += "};\n\n";
    out += "const dom_ui_command_binding* appcore_ui_command_bindings(u32* out_count)\n{\n";
    out += "    if (out_count) {\n";
    out += "        *out_count = (u32)(sizeof(k_ui_bindings) / sizeof(k_ui_bindings[0]));\n";
    out += "    }\n";
    out += "    return k_ui_bindings;\n";
    out += "}\n\n";
    out += "const dom_ui_command_binding* appcore_ui_command_find_action(const char* action_key)\n{\n";
    out += "    u32 count = 0u;\n";
    out += "    u32 i;\n";
    out += "    const dom_ui_command_binding* bindings = appcore_ui_command_bindings(&count);\n";
    out += "    if (!action_key) {\n";
    out += "        return 0;\n";
    out += "    }\n";
    out += "    for (i = 0u; i < count; ++i) {\n";
    out += "        if (bindings[i].action_key && strcmp(bindings[i].action_key, action_key) == 0) {\n";
    out += "            return &bindings[i];\n";
    out += "        }\n";
    out += "    }\n";
    out += "    return 0;\n";
    out += "}\n\n";
    out += "const dom_ui_command_binding* appcore_ui_command_find_element_event(const char* ui_element_id,\n";
    out += "                                                                    const char* event_name)\n{\n";
    out += "    u32 count = 0u;\n";
    out += "    u32 i;\n";
    out += "    const dom_ui_command_binding* bindings = appcore_ui_command_bindings(&count);\n";
    out += "    if (!ui_element_id || !event_name) {\n";
    out += "        return 0;\n";
    out += "    }\n";
    out += "    for (i = 0u; i < count; ++i) {\n";
    out += "        if (bindings[i].ui_element_id && bindings[i].event_name &&\n";
    out += "            strcmp(bindings[i].ui_element_id, ui_element_id) == 0 &&\n";
    out += "            strcmp(bindings[i].event_name, event_name) == 0) {\n";
    out += "            return &bindings[i];\n";
    out += "        }\n";
    out += "    }\n";
    out += "    return 0;\n";
    out += "}\n\n";
    out += "const dom_app_command_desc* appcore_ui_command_desc_for_action(const char* action_key)\n{\n";
    out += "    const dom_ui_command_binding* binding = appcore_ui_command_find_action(action_key);\n";
    out += "    if (!binding) {\n";
    out += "        return 0;\n";
    out += "    }\n";
    out += "    return appcore_command_find(binding->action_key);\n";
    out += "}\n";
}

static void emit_accessibility_header(std::string& out)
{
    out.clear();
    out += "/*\n";
    out += "AUTO-GENERATED by tool_ui_bind. DO NOT EDIT.\n";
    out += "*/\n";
    out += "#ifndef DOMINIUM_APPCORE_UI_ACCESSIBILITY_MAP_H\n";
    out += "#define DOMINIUM_APPCORE_UI_ACCESSIBILITY_MAP_H\n\n";
    out += "#include \"domino/core/types.h\"\n\n";
    out += "#ifdef __cplusplus\nextern \"C\" {\n#endif\n\n";
    out += "typedef struct dom_ui_accessibility_entry {\n";
    out += "    const char* ui_element_id;\n";
    out += "    const char* name;\n";
    out += "    const char* role;\n";
    out += "    const char* description;\n";
    out += "    const char* localization_key;\n";
    out += "} dom_ui_accessibility_entry;\n\n";
    out += "const dom_ui_accessibility_entry* appcore_ui_accessibility_entries(u32* out_count);\n";
    out += "const dom_ui_accessibility_entry* appcore_ui_accessibility_find(const char* ui_element_id);\n\n";
    out += "#ifdef __cplusplus\n} /* extern \"C\" */\n#endif\n\n";
    out += "#endif /* DOMINIUM_APPCORE_UI_ACCESSIBILITY_MAP_H */\n";
}

static void emit_accessibility_source(std::string& out, const std::vector<accessibility_entry>& entries)
{
    size_t i;
    out.clear();
    out += "/*\n";
    out += "AUTO-GENERATED by tool_ui_bind. DO NOT EDIT.\n";
    out += "*/\n";
    out += "#include \"ui_bind/ui_accessibility_map.h\"\n";
    out += "#include <string.h>\n\n";
    out += "static const dom_ui_accessibility_entry k_ui_accessibility[] = {\n";
    for (i = 0u; i < entries.size(); ++i) {
        const accessibility_entry& e = entries[i];
        out += "    { \"";
        out += c_escape(e.ui_element_id);
        out += "\", \"";
        out += c_escape(e.name);
        out += "\", \"";
        out += c_escape(e.role);
        out += "\", \"";
        out += c_escape(e.description);
        out += "\", \"";
        out += c_escape(e.localization_key);
        out += "\" }";
        if (i + 1u < entries.size()) {
            out += ",";
        }
        out += "\n";
    }
    out += "};\n\n";
    out += "const dom_ui_accessibility_entry* appcore_ui_accessibility_entries(u32* out_count)\n{\n";
    out += "    if (out_count) {\n";
    out += "        *out_count = (u32)(sizeof(k_ui_accessibility) / sizeof(k_ui_accessibility[0]));\n";
    out += "    }\n";
    out += "    return k_ui_accessibility;\n";
    out += "}\n\n";
    out += "const dom_ui_accessibility_entry* appcore_ui_accessibility_find(const char* ui_element_id)\n{\n";
    out += "    u32 count = 0u;\n";
    out += "    u32 i;\n";
    out += "    const dom_ui_accessibility_entry* entries = appcore_ui_accessibility_entries(&count);\n";
    out += "    if (!ui_element_id) {\n";
    out += "        return 0;\n";
    out += "    }\n";
    out += "    for (i = 0u; i < count; ++i) {\n";
    out += "        if (entries[i].ui_element_id && strcmp(entries[i].ui_element_id, ui_element_id) == 0) {\n";
    out += "            return &entries[i];\n";
    out += "        }\n";
    out += "    }\n";
    out += "    return 0;\n";
    out += "}\n";
}

static void emit_localization_report(std::string& out, const std::vector<accessibility_entry>& entries)
{
    size_t i;
    out.clear();
    out += "{\n";
    out += "  \"version\": 1,\n";
    out += "  \"entries\": [\n";
    for (i = 0u; i < entries.size(); ++i) {
        const accessibility_entry& e = entries[i];
        out += "    { \"ui_element_id\": \"";
        out += json_escape(e.ui_element_id);
        out += "\", \"localization_key\": \"";
        out += json_escape(e.localization_key);
        out += "\" }";
        if (i + 1u < entries.size()) {
            out += ",";
        }
        out += "\n";
    }
    out += "  ]\n";
    out += "}\n";
}

static bool ensure_dir(const std::string& path)
{
    if (path.empty()) {
        return false;
    }
#if defined(_WIN32)
    return CreateDirectoryA(path.c_str(), 0) != 0 || GetLastError() == ERROR_ALREADY_EXISTS;
#else
    return mkdir(path.c_str(), 0755) == 0 || errno == EEXIST;
#endif
}

static bool ensure_dir_recursive(const std::string& path)
{
    size_t i = 0u;
    if (path.empty()) {
        return false;
    }
    while (i < path.size()) {
        size_t sep = path.find_first_of("/\\", i);
        std::string part;
        if (sep == std::string::npos) {
            part = path;
            i = path.size();
        } else {
            part = path.substr(0, sep);
            i = sep + 1u;
        }
        if (part.empty()) {
            continue;
        }
#if defined(_WIN32)
        if (part.size() == 2u && part[1] == ':') {
            continue;
        }
#endif
        if (!ensure_dir(part)) {
            return false;
        }
    }
    return true;
}

static bool compare_or_write(const std::string& path,
                             const std::string& expected,
                             bool do_write,
                             std::vector<std::string>& errors)
{
    std::string existing;
    if (do_write) {
        size_t pos = path.find_last_of("/\\");
        if (pos != std::string::npos) {
            std::string parent = path.substr(0, pos);
            if (!parent.empty() && !ensure_dir_recursive(parent)) {
                errors.push_back(std::string("UI_BIND_ERROR|output|dir_create_failed|") + path);
                return false;
            }
        }
        if (!write_file_text(path.c_str(), expected)) {
            errors.push_back(std::string("UI_BIND_ERROR|output|write_failed|") + path);
            return false;
        }
        return true;
    }
    if (!read_file_text(path.c_str(), existing)) {
        errors.push_back(std::string("UI_BIND_ERROR|output|missing|") + path);
        return false;
    }
    if (existing != expected) {
        errors.push_back(std::string("UI_BIND_ERROR|output|stale|") + path);
        return false;
    }
    return true;
}

int main(int argc, char** argv)
{
    const char* repo_root = ".";
    const char* ui_index_path = 0;
    const char* out_dir = 0;
    std::string ui_index_storage;
    std::string out_dir_storage;
    bool do_check = false;
    bool do_write = false;
    int i;

    for (i = 1; i < argc; ++i) {
        const char* arg = argv[i];
        if (!arg) {
            continue;
        }
        if (strcmp(arg, "--repo-root") == 0 && i + 1 < argc) {
            repo_root = argv[++i];
        } else if (strcmp(arg, "--ui-index") == 0 && i + 1 < argc) {
            ui_index_path = argv[++i];
        } else if (strcmp(arg, "--out-dir") == 0 && i + 1 < argc) {
            out_dir = argv[++i];
        } else if (strcmp(arg, "--check") == 0) {
            do_check = true;
        } else if (strcmp(arg, "--write") == 0) {
            do_write = true;
        } else if (strcmp(arg, "--help") == 0 || strcmp(arg, "-h") == 0) {
            print_usage();
            return 0;
        } else {
            print_usage();
            return 2;
        }
    }

    if (do_check == do_write) {
        print_usage();
        return 2;
    }

    if (!ui_index_path) {
        ui_index_storage = std::string(repo_root) + "/tools/ui_index/ui_index.json";
        ui_index_path = ui_index_storage.c_str();
    }
    if (!out_dir) {
        out_dir_storage = std::string(repo_root) + "/libs/appcore/ui_bind";
        out_dir = out_dir_storage.c_str();
    }

    std::vector<ui_bind_index_entry> entries;
    std::string index_error;
    if (!ui_bind_load_index(ui_index_path, entries, &index_error)) {
        std::fprintf(stderr, "UI_BIND_ERROR|index|%s\n", index_error.c_str());
        return 1;
    }

    std::map<std::string, std::vector<const dom_app_command_desc*> > command_map;
    build_command_map(command_map);

    std::set<std::string> seen_ids;
    std::vector<bind_entry> bindings;
    std::vector<accessibility_entry> access_entries;
    std::vector<std::string> errors;

    for (i = 0; i < (int)entries.size(); ++i) {
        const ui_bind_index_entry& entry = entries[(size_t)i];
        if (entry.ui_type != "canonical") {
            continue;
        }
        domui_doc doc;
        domui_diag diag;
        std::string doc_path = join_path(repo_root, entry.path);
        if (!domui_doc_load_tlv(&doc, doc_path.c_str(), &diag)) {
            size_t e;
            for (e = 0u; e < diag.errors().size(); ++e) {
                errors.push_back(std::string("UI_BIND_ERROR|doc|load_failed|") + entry.path);
            }
            continue;
        }
        if (doc.meta.doc_name.empty()) {
            errors.push_back(std::string("UI_BIND_ERROR|doc|missing_name|") + entry.path);
            continue;
        }
        {
            std::vector<domui_widget_id> order;
            size_t widx;
            doc.canonical_widget_order(order);
            for (widx = 0u; widx < order.size(); ++widx) {
                domui_widget* w = doc.find_by_id(order[widx]);
                bool interactive;
                std::string widget_name;
                std::string ui_element_id;
                std::string acc_name;
                std::string acc_role;
                std::string acc_desc;
                std::string loc_key;
                std::string enabled_predicate;

                if (!w) {
                    continue;
                }
                widget_name = w->name.c_str();
                if (widget_name.empty()) {
                    errors.push_back(std::string("UI_BIND_ERROR|widget|missing_name|") + doc_path);
                    continue;
                }
                ui_element_id = make_ui_element_id(doc.meta.doc_name.c_str(), widget_name);
                if (seen_ids.find(ui_element_id) != seen_ids.end()) {
                    errors.push_back(std::string("UI_BIND_ERROR|widget|duplicate_id|") + ui_element_id);
                    continue;
                }
                seen_ids.insert(ui_element_id);

                interactive = (w->events.size() > 0u) || is_interactive_type(w->type);

                if (prop_has_enabled_predicate(w->props, enabled_predicate) &&
                    !enabled_predicate_allowed(enabled_predicate)) {
                    errors.push_back(std::string("UI_BIND_ERROR|widget|invalid_enabled_predicate|") +
                                     ui_element_id + "|" + enabled_predicate);
                }

                if (interactive) {
                    if (!get_prop_string(w->props, "accessibility.name", acc_name)) {
                        errors.push_back(std::string("UI_BIND_ERROR|widget|missing_accessibility_name|") +
                                         ui_element_id);
                    }
                    if (!get_prop_string(w->props, "accessibility.role", acc_role)) {
                        errors.push_back(std::string("UI_BIND_ERROR|widget|missing_accessibility_role|") +
                                         ui_element_id);
                    }
                    if (!get_prop_string(w->props, "accessibility.description", acc_desc)) {
                        errors.push_back(std::string("UI_BIND_ERROR|widget|missing_accessibility_desc|") +
                                         ui_element_id);
                    }
                    if (!get_prop_string(w->props, "localization.key", loc_key)) {
                        errors.push_back(std::string("UI_BIND_ERROR|widget|missing_localization_key|") +
                                         ui_element_id);
                    }
                    if (!acc_name.empty() && !acc_role.empty() && !acc_desc.empty() && !loc_key.empty()) {
                        accessibility_entry acc;
                        acc.ui_element_id = ui_element_id;
                        acc.name = acc_name;
                        acc.role = acc_role;
                        acc.description = acc_desc;
                        acc.localization_key = loc_key;
                        access_entries.push_back(acc);
                    }
                }

                if (w->events.size() == 0u) {
                    continue;
                }
                {
                    size_t eidx;
                    const domui_events::list_type& events = w->events.entries();
                    for (eidx = 0u; eidx < events.size(); ++eidx) {
                        const std::string action_key = events[eidx].action_key.c_str();
                        const std::string event_name = events[eidx].event_name.c_str();
                        std::map<std::string, std::vector<const dom_app_command_desc*> >::const_iterator it;
                        if (action_key.empty()) {
                            errors.push_back(std::string("UI_BIND_ERROR|event|missing_action|") + ui_element_id);
                            continue;
                        }
                        it = command_map.find(action_key);
                        if (it == command_map.end()) {
                            errors.push_back(std::string("UI_BIND_ERROR|event|unknown_command|") + action_key);
                            continue;
                        }
                        if (it->second.size() != 1u) {
                            errors.push_back(std::string("UI_BIND_ERROR|event|ambiguous_command|") + action_key);
                            continue;
                        }
                        {
                            const dom_app_command_desc* cmd = it->second[0];
                            if (!cmd->arg_schema || !cmd->arg_schema[0]) {
                                errors.push_back(std::string("UI_BIND_ERROR|event|missing_arg_schema|") + action_key);
                                continue;
                            }
                            if (!command_epistemic_scope_known(cmd->epistemic_scope)) {
                                errors.push_back(std::string("UI_BIND_ERROR|event|invalid_epistemic_scope|") +
                                                 action_key);
                                continue;
                            }
                            if (cmd->required_capability_count > 0u && !cmd->required_capabilities) {
                                errors.push_back(std::string("UI_BIND_ERROR|event|missing_required_capabilities|") +
                                                 action_key);
                                continue;
                            }
                            if (!command_schema_known(cmd->arg_schema)) {
                                errors.push_back(std::string("UI_BIND_ERROR|event|unknown_arg_schema|") +
                                                 action_key + "|" + cmd->arg_schema);
                                continue;
                            }
                            if (!cmd->failure_codes || cmd->failure_code_count == 0u) {
                                errors.push_back(std::string("UI_BIND_ERROR|event|missing_failure_codes|") +
                                                 action_key);
                                continue;
                            }
                            bind_entry be;
                            be.ui_element_id = ui_element_id;
                            be.event_name = event_name;
                            be.action_key = action_key;
                            be.command_id = cmd->command_id;
                            bindings.push_back(be);
                        }
                    }
                }
            }
        }
    }

    if (!errors.empty()) {
        size_t e;
        for (e = 0u; e < errors.size(); ++e) {
            std::fprintf(stderr, "%s\n", errors[e].c_str());
        }
        return 1;
    }

    std::sort(bindings.begin(), bindings.end(), bind_entry_less());

    std::sort(access_entries.begin(), access_entries.end(), accessibility_entry_less());

    {
        std::string header;
        std::string source;
        std::string access_header;
        std::string access_source;
        std::string localization_json;
        std::vector<std::string> out_errors;
        std::string out_dir_str = out_dir ? out_dir : "";
        std::string binding_h = out_dir_str + "/ui_command_binding_table.h";
        std::string binding_c = out_dir_str + "/ui_command_binding_table.c";
        std::string access_h = out_dir_str + "/ui_accessibility_map.h";
        std::string access_c = out_dir_str + "/ui_accessibility_map.c";
        std::string loc_json = out_dir_str + "/ui_localisation_usage_report.json";

        emit_binding_header(header);
        emit_binding_source(source, bindings);
        emit_accessibility_header(access_header);
        emit_accessibility_source(access_source, access_entries);
        emit_localization_report(localization_json, access_entries);

        (void)compare_or_write(binding_h, header, do_write, out_errors);
        (void)compare_or_write(binding_c, source, do_write, out_errors);
        (void)compare_or_write(access_h, access_header, do_write, out_errors);
        (void)compare_or_write(access_c, access_source, do_write, out_errors);
        (void)compare_or_write(loc_json, localization_json, do_write, out_errors);

        if (!out_errors.empty()) {
            size_t o;
            for (o = 0u; o < out_errors.size(); ++o) {
                std::fprintf(stderr, "%s\n", out_errors[o].c_str());
            }
            return 1;
        }
    }

    return 0;
}
