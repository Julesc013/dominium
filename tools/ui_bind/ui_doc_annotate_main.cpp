/*
FILE: tools/ui_bind/ui_doc_annotate_main.cpp
MODULE: Dominium
PURPOSE: Auto-annotate UI IR documents with accessibility + localization props.
NOTES: Deterministic; no side effects unless --write is used.
*/
#include "ui_bind_index.h"

#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "ui_ir_diag.h"
#include "ui_ir_doc.h"
#include "ui_ir_json.h"
#include "ui_ir_props.h"
#include "ui_ir_tlv.h"

static void print_usage(void)
{
    std::fprintf(stderr,
                 "usage: tool_ui_doc_annotate --repo-root <path> --ui-index <path> (--check|--write)\n");
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

static void set_prop_string(domui_props& props, const char* key, const std::string& value)
{
    if (value.empty()) {
        return;
    }
    props.set(key, domui_value_string(domui_string(value)));
}

static std::string pick_label(const domui_widget& w)
{
    std::string label;
    if (get_prop_string(w.props, "text", label)) {
        return label;
    }
    if (get_prop_string(w.props, "tab.title", label)) {
        return label;
    }
    return w.name.c_str();
}

static const char* role_for_widget(domui_widget_type t, bool has_events)
{
    switch (t) {
    case DOMUI_WIDGET_BUTTON: return "button";
    case DOMUI_WIDGET_EDIT: return "textbox";
    case DOMUI_WIDGET_LISTBOX: return "listbox";
    case DOMUI_WIDGET_COMBOBOX: return "combobox";
    case DOMUI_WIDGET_CHECKBOX: return "checkbox";
    case DOMUI_WIDGET_RADIO: return "radio";
    case DOMUI_WIDGET_TAB: return "tab";
    case DOMUI_WIDGET_TABS: return "tablist";
    case DOMUI_WIDGET_TAB_PAGE: return "tabpanel";
    case DOMUI_WIDGET_TREEVIEW: return "tree";
    case DOMUI_WIDGET_LISTVIEW: return "list";
    case DOMUI_WIDGET_SLIDER: return "slider";
    default:
        break;
    }
    return has_events ? "control" : "";
}

static std::string join_path(const std::string& root, const std::string& rel)
{
    if (rel.empty()) {
        return rel;
    }
    if (rel.size() >= 2u && rel[1] == ':') {
        return rel;
    }
    if (!rel.empty() && (rel[0] == '/' || rel[0] == '\\')) {
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

static std::string json_path_from_tlv(const std::string& tlv_path)
{
    size_t dot = tlv_path.find_last_of('.');
    if (dot == std::string::npos) {
        return tlv_path + ".json";
    }
    return tlv_path.substr(0, dot) + ".json";
}

static void print_diag(const domui_diag& diag)
{
    size_t i;
    for (i = 0u; i < diag.errors().size(); ++i) {
        const domui_diag_item& item = diag.errors()[i];
        std::fprintf(stderr, "ERROR|%u|%s|%s\n",
                     (unsigned int)item.widget_id,
                     item.context.c_str(),
                     item.message.c_str());
    }
    for (i = 0u; i < diag.warnings().size(); ++i) {
        const domui_diag_item& item = diag.warnings()[i];
        std::fprintf(stderr, "WARN|%u|%s|%s\n",
                     (unsigned int)item.widget_id,
                     item.context.c_str(),
                     item.message.c_str());
    }
}

int main(int argc, char** argv)
{
    const char* repo_root = ".";
    const char* ui_index_path = 0;
    bool do_check = false;
    bool do_write = false;
    int i;

    for (i = 1; i < argc; ++i) {
        const char* arg = argv[i];
        if (!arg) {
            continue;
        }
        if (std::strcmp(arg, "--repo-root") == 0 && i + 1 < argc) {
            repo_root = argv[++i];
        } else if (std::strcmp(arg, "--ui-index") == 0 && i + 1 < argc) {
            ui_index_path = argv[++i];
        } else if (std::strcmp(arg, "--check") == 0) {
            do_check = true;
        } else if (std::strcmp(arg, "--write") == 0) {
            do_write = true;
        } else if (std::strcmp(arg, "--help") == 0 || std::strcmp(arg, "-h") == 0) {
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

    {
        std::string default_index = std::string(repo_root) + "/tools/ui_index/ui_index.json";
        if (!ui_index_path) {
            ui_index_path = default_index.c_str();
        }
    }

    std::vector<ui_bind_index_entry> entries;
    std::string index_error;
    if (!ui_bind_load_index(ui_index_path, entries, &index_error)) {
        std::fprintf(stderr, "UI_DOC_ANNOTATE_ERROR|index|%s\n", index_error.c_str());
        return 1;
    }

    size_t missing_total = 0u;
    size_t changed_total = 0u;

    for (i = 0; i < (int)entries.size(); ++i) {
        const ui_bind_index_entry& entry = entries[(size_t)i];
        if (entry.ui_type != "canonical") {
            continue;
        }

        domui_doc doc;
        domui_diag diag;
        std::string doc_path = join_path(repo_root, entry.path);
        if (!domui_doc_load_tlv(&doc, doc_path.c_str(), &diag)) {
            std::fprintf(stderr, "UI_DOC_ANNOTATE_ERROR|doc|load_failed|%s\n", entry.path.c_str());
            print_diag(diag);
            return 1;
        }
        if (doc.meta.doc_name.empty()) {
            std::fprintf(stderr, "UI_DOC_ANNOTATE_ERROR|doc|missing_name|%s\n", entry.path.c_str());
            return 1;
        }

        bool changed = false;
        std::vector<domui_widget_id> order;
        size_t widx;
        doc.canonical_widget_order(order);
        for (widx = 0u; widx < order.size(); ++widx) {
            domui_widget* w = doc.find_by_id(order[widx]);
            if (!w) {
                continue;
            }
            if (w->name.empty()) {
                continue;
            }
            if (!(w->events.size() > 0u || is_interactive_type(w->type))) {
                continue;
            }

            std::string acc_name;
            std::string acc_role;
            std::string acc_desc;
            std::string loc_key;
            std::string label = pick_label(*w);
            const char* role = role_for_widget(w->type, w->events.size() > 0u);

            if (!get_prop_string(w->props, "accessibility.name", acc_name)) {
                if (!label.empty()) {
                    set_prop_string(w->props, "accessibility.name", label);
                    changed = true;
                } else {
                    ++missing_total;
                }
            }

            if (!get_prop_string(w->props, "accessibility.role", acc_role)) {
                if (role && role[0]) {
                    set_prop_string(w->props, "accessibility.role", role);
                    changed = true;
                } else {
                    ++missing_total;
                }
            }

            if (!get_prop_string(w->props, "accessibility.description", acc_desc)) {
                std::string desc = label;
                if (desc.empty() && !w->events.entries().empty()) {
                    desc = w->events.entries()[0].action_key.c_str();
                }
                if (desc.empty()) {
                    desc = w->name.c_str();
                }
                if (!desc.empty()) {
                    set_prop_string(w->props, "accessibility.description", desc);
                    changed = true;
                } else {
                    ++missing_total;
                }
            }

            if (!get_prop_string(w->props, "localization.key", loc_key)) {
                std::string key = std::string("ui.") + doc.meta.doc_name.c_str() + "." + w->name.c_str();
                set_prop_string(w->props, "localization.key", key);
                changed = true;
            }
        }

        if (changed && do_write) {
            if (!domui_doc_save_tlv(&doc, doc_path.c_str(), &diag)) {
                std::fprintf(stderr, "UI_DOC_ANNOTATE_ERROR|doc|save_failed|%s\n", entry.path.c_str());
                print_diag(diag);
                return 1;
            }
            if (!domui_doc_save_json_mirror(&doc, json_path_from_tlv(doc_path).c_str(), &diag)) {
                std::fprintf(stderr, "UI_DOC_ANNOTATE_ERROR|doc|json_save_failed|%s\n", entry.path.c_str());
                print_diag(diag);
                return 1;
            }
            ++changed_total;
        }
    }

    if (do_check && missing_total > 0u) {
        std::fprintf(stderr, "UI_DOC_ANNOTATE_ERROR|missing_annotations|%u\n",
                     (unsigned int)missing_total);
        return 1;
    }

    if (do_write) {
        std::printf("UI_DOC_ANNOTATE_OK|updated_docs=%u\n", (unsigned int)changed_total);
    } else {
        std::printf("UI_DOC_ANNOTATE_OK|checked\n");
    }
    return 0;
}
