/*
FILE: source/domino/ui_ir/ui_ir_json.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir json
RESPONSIBILITY: Deterministic JSON mirror for UI IR documents.
*/
#include "ui_ir_json.h"

#include <stdio.h>
#include <string.h>

#include "ui_ir_fileio.h"

static const size_t DOMUI_JSON_MAX_PRETTY = 2u * 1024u * 1024u;

static const char* domui_widget_type_name(domui_widget_type t)
{
    switch (t) {
    case DOMUI_WIDGET_CONTAINER: return "CONTAINER";
    case DOMUI_WIDGET_STATIC_TEXT: return "STATIC_TEXT";
    case DOMUI_WIDGET_BUTTON: return "BUTTON";
    case DOMUI_WIDGET_EDIT: return "EDIT";
    case DOMUI_WIDGET_LISTBOX: return "LISTBOX";
    case DOMUI_WIDGET_COMBOBOX: return "COMBOBOX";
    case DOMUI_WIDGET_CHECKBOX: return "CHECKBOX";
    case DOMUI_WIDGET_RADIO: return "RADIO";
    case DOMUI_WIDGET_TAB: return "TAB";
    case DOMUI_WIDGET_TREEVIEW: return "TREEVIEW";
    case DOMUI_WIDGET_LISTVIEW: return "LISTVIEW";
    case DOMUI_WIDGET_PROGRESS: return "PROGRESS";
    case DOMUI_WIDGET_SLIDER: return "SLIDER";
    case DOMUI_WIDGET_GROUPBOX: return "GROUPBOX";
    case DOMUI_WIDGET_IMAGE: return "IMAGE";
    case DOMUI_WIDGET_SPLITTER: return "SPLITTER";
    case DOMUI_WIDGET_SCROLLPANEL: return "SCROLLPANEL";
    case DOMUI_WIDGET_TABS: return "TABS";
    case DOMUI_WIDGET_TAB_PAGE: return "TAB_PAGE";
    default:
        break;
    }
    return "UNKNOWN";
}

static const char* domui_layout_mode_name(domui_container_layout_mode m)
{
    switch (m) {
    case DOMUI_LAYOUT_ABSOLUTE: return "ABSOLUTE";
    case DOMUI_LAYOUT_STACK_ROW: return "STACK_ROW";
    case DOMUI_LAYOUT_STACK_COL: return "STACK_COL";
    case DOMUI_LAYOUT_GRID: return "GRID";
    default:
        break;
    }
    return "UNKNOWN";
}

static const char* domui_dock_name(domui_dock_mode d)
{
    switch (d) {
    case DOMUI_DOCK_NONE: return "NONE";
    case DOMUI_DOCK_LEFT: return "LEFT";
    case DOMUI_DOCK_RIGHT: return "RIGHT";
    case DOMUI_DOCK_TOP: return "TOP";
    case DOMUI_DOCK_BOTTOM: return "BOTTOM";
    case DOMUI_DOCK_FILL: return "FILL";
    default:
        break;
    }
    return "UNKNOWN";
}

static const char* domui_value_type_name(domui_value_type t)
{
    switch (t) {
    case DOMUI_VALUE_INT: return "INT";
    case DOMUI_VALUE_UINT: return "UINT";
    case DOMUI_VALUE_BOOL: return "BOOL";
    case DOMUI_VALUE_STRING: return "STRING";
    case DOMUI_VALUE_VEC2I: return "VEC2I";
    case DOMUI_VALUE_RECTI: return "RECTI";
    default:
        break;
    }
    return "UNKNOWN";
}

static void domui_json_escape(const domui_string& s, std::string& out)
{
    const std::string& v = s.str();
    size_t i;
    for (i = 0u; i < v.size(); ++i) {
        unsigned char c = (unsigned char)v[i];
        switch (c) {
        case '\"': out += "\\\""; break;
        case '\\': out += "\\\\"; break;
        case '\b': out += "\\b"; break;
        case '\f': out += "\\f"; break;
        case '\n': out += "\\n"; break;
        case '\r': out += "\\r"; break;
        case '\t': out += "\\t"; break;
        default:
            if (c < 0x20u) {
                char buf[7];
                snprintf(buf, sizeof(buf), "\\u%04x", (unsigned int)c);
                out += buf;
            } else {
                out.push_back((char)c);
            }
            break;
        }
    }
}

static void domui_json_indent(std::string& out, int level, bool pretty)
{
    int i;
    if (!pretty) {
        return;
    }
    out.push_back('\n');
    for (i = 0; i < level; ++i) {
        out += "  ";
    }
}

static void domui_json_key(std::string& out, const char* key, int level, bool pretty)
{
    domui_json_indent(out, level, pretty);
    out.push_back('\"');
    out += key;
    out += "\":";
    if (pretty) {
        out.push_back(' ');
    }
}

static void domui_json_string(std::string& out, const domui_string& s)
{
    out.push_back('\"');
    domui_json_escape(s, out);
    out.push_back('\"');
}

static void domui_json_string_c(std::string& out, const char* s)
{
    domui_string tmp(s ? s : "");
    domui_json_string(out, tmp);
}

static void domui_json_write_string_list(std::string& out, const domui_string_list& list, int level, bool pretty)
{
    size_t i;
    out.push_back('[');
    for (i = 0u; i < list.size(); ++i) {
        if (i != 0u) {
            out.push_back(',');
        }
        domui_json_indent(out, level + 1, pretty);
        domui_json_string(out, list[i]);
    }
    if (!list.empty()) {
        domui_json_indent(out, level, pretty);
    }
    out.push_back(']');
}

static void domui_json_write_props(std::string& out, const domui_props& props, int level, bool pretty)
{
    size_t i;
    const domui_props::list_type& entries = props.entries();
    out.push_back('[');
    for (i = 0u; i < entries.size(); ++i) {
        const domui_prop_entry& e = entries[i];
        if (i != 0u) {
            out.push_back(',');
        }
        domui_json_indent(out, level + 1, pretty);
        out.push_back('{');
        domui_json_key(out, "key", level + 2, pretty);
        domui_json_string(out, e.key);
        out.push_back(',');
        domui_json_key(out, "type", level + 2, pretty);
        domui_json_string_c(out, domui_value_type_name(e.value.type));
        out.push_back(',');
        domui_json_key(out, "value", level + 2, pretty);
        switch (e.value.type) {
        case DOMUI_VALUE_INT:
            {
                char buf[32];
                snprintf(buf, sizeof(buf), "%d", e.value.v_int);
                out += buf;
            }
            break;
        case DOMUI_VALUE_UINT:
            {
                char buf[32];
                snprintf(buf, sizeof(buf), "%u", (unsigned int)e.value.v_uint);
                out += buf;
            }
            break;
        case DOMUI_VALUE_BOOL:
            out += (e.value.v_bool ? "true" : "false");
            break;
        case DOMUI_VALUE_STRING:
            domui_json_string(out, e.value.v_string);
            break;
        case DOMUI_VALUE_VEC2I:
            out.push_back('{');
            domui_json_key(out, "x", level + 3, pretty);
            {
                char buf[32];
                snprintf(buf, sizeof(buf), "%d", e.value.v_vec2i.x);
                out += buf;
            }
            out.push_back(',');
            domui_json_key(out, "y", level + 3, pretty);
            {
                char buf[32];
                snprintf(buf, sizeof(buf), "%d", e.value.v_vec2i.y);
                out += buf;
            }
            domui_json_indent(out, level + 2, pretty);
            out.push_back('}');
            break;
        case DOMUI_VALUE_RECTI:
            out.push_back('{');
            domui_json_key(out, "x", level + 3, pretty);
            {
                char buf[32];
                snprintf(buf, sizeof(buf), "%d", e.value.v_recti.x);
                out += buf;
            }
            out.push_back(',');
            domui_json_key(out, "y", level + 3, pretty);
            {
                char buf[32];
                snprintf(buf, sizeof(buf), "%d", e.value.v_recti.y);
                out += buf;
            }
            out.push_back(',');
            domui_json_key(out, "w", level + 3, pretty);
            {
                char buf[32];
                snprintf(buf, sizeof(buf), "%d", e.value.v_recti.w);
                out += buf;
            }
            out.push_back(',');
            domui_json_key(out, "h", level + 3, pretty);
            {
                char buf[32];
                snprintf(buf, sizeof(buf), "%d", e.value.v_recti.h);
                out += buf;
            }
            domui_json_indent(out, level + 2, pretty);
            out.push_back('}');
            break;
        default:
            out += "null";
            break;
        }
        domui_json_indent(out, level + 1, pretty);
        out.push_back('}');
    }
    if (!entries.empty()) {
        domui_json_indent(out, level, pretty);
    }
    out.push_back(']');
}

static void domui_json_write_events(std::string& out, const domui_events& events, int level, bool pretty)
{
    size_t i;
    const domui_events::list_type& entries = events.entries();
    out.push_back('[');
    for (i = 0u; i < entries.size(); ++i) {
        if (i != 0u) {
            out.push_back(',');
        }
        domui_json_indent(out, level + 1, pretty);
        out.push_back('{');
        domui_json_key(out, "event", level + 2, pretty);
        domui_json_string(out, entries[i].event_name);
        out.push_back(',');
        domui_json_key(out, "action", level + 2, pretty);
        domui_json_string(out, entries[i].action_key);
        domui_json_indent(out, level + 1, pretty);
        out.push_back('}');
    }
    if (!entries.empty()) {
        domui_json_indent(out, level, pretty);
    }
    out.push_back(']');
}

static void domui_json_write_widget(std::string& out, const domui_widget& w, int level, bool pretty)
{
    char buf[32];
    out.push_back('{');
    domui_json_key(out, "id", level + 1, pretty);
    snprintf(buf, sizeof(buf), "%u", (unsigned int)w.id);
    out += buf;
    out.push_back(',');
    domui_json_key(out, "type", level + 1, pretty);
    domui_json_string_c(out, domui_widget_type_name(w.type));
    out.push_back(',');
    domui_json_key(out, "name", level + 1, pretty);
    domui_json_string(out, w.name);
    out.push_back(',');
    domui_json_key(out, "parent_id", level + 1, pretty);
    snprintf(buf, sizeof(buf), "%u", (unsigned int)w.parent_id);
    out += buf;
    out.push_back(',');
    domui_json_key(out, "z_order", level + 1, pretty);
    snprintf(buf, sizeof(buf), "%u", (unsigned int)w.z_order);
    out += buf;
    out.push_back(',');
    domui_json_key(out, "rect", level + 1, pretty);
    out.push_back('{');
    domui_json_key(out, "x", level + 2, pretty);
    snprintf(buf, sizeof(buf), "%d", w.x);
    out += buf;
    out.push_back(',');
    domui_json_key(out, "y", level + 2, pretty);
    snprintf(buf, sizeof(buf), "%d", w.y);
    out += buf;
    out.push_back(',');
    domui_json_key(out, "w", level + 2, pretty);
    snprintf(buf, sizeof(buf), "%d", w.w);
    out += buf;
    out.push_back(',');
    domui_json_key(out, "h", level + 2, pretty);
    snprintf(buf, sizeof(buf), "%d", w.h);
    out += buf;
    domui_json_indent(out, level + 1, pretty);
    out.push_back('}');

    out.push_back(',');
    domui_json_key(out, "layout", level + 1, pretty);
    out.push_back('{');
    domui_json_key(out, "mode", level + 2, pretty);
    domui_json_string_c(out, domui_layout_mode_name(w.layout_mode));
    out.push_back(',');
    domui_json_key(out, "dock", level + 2, pretty);
    domui_json_string_c(out, domui_dock_name(w.dock));
    out.push_back(',');
    domui_json_key(out, "anchors", level + 2, pretty);
    out.push_back('[');
    if (w.anchors & DOMUI_ANCHOR_L) { domui_json_string_c(out, "L"); }
    if (w.anchors & DOMUI_ANCHOR_R) { if (out[out.size() - 1] != '[') out.push_back(','); domui_json_string_c(out, "R"); }
    if (w.anchors & DOMUI_ANCHOR_T) { if (out[out.size() - 1] != '[') out.push_back(','); domui_json_string_c(out, "T"); }
    if (w.anchors & DOMUI_ANCHOR_B) { if (out[out.size() - 1] != '[') out.push_back(','); domui_json_string_c(out, "B"); }
    out.push_back(']');
    out.push_back(',');
    domui_json_key(out, "margin", level + 2, pretty);
    out.push_back('{');
    domui_json_key(out, "left", level + 3, pretty);
    snprintf(buf, sizeof(buf), "%d", w.margin.left);
    out += buf;
    out.push_back(',');
    domui_json_key(out, "right", level + 3, pretty);
    snprintf(buf, sizeof(buf), "%d", w.margin.right);
    out += buf;
    out.push_back(',');
    domui_json_key(out, "top", level + 3, pretty);
    snprintf(buf, sizeof(buf), "%d", w.margin.top);
    out += buf;
    out.push_back(',');
    domui_json_key(out, "bottom", level + 3, pretty);
    snprintf(buf, sizeof(buf), "%d", w.margin.bottom);
    out += buf;
    domui_json_indent(out, level + 2, pretty);
    out.push_back('}');
    out.push_back(',');
    domui_json_key(out, "padding", level + 2, pretty);
    out.push_back('{');
    domui_json_key(out, "left", level + 3, pretty);
    snprintf(buf, sizeof(buf), "%d", w.padding.left);
    out += buf;
    out.push_back(',');
    domui_json_key(out, "right", level + 3, pretty);
    snprintf(buf, sizeof(buf), "%d", w.padding.right);
    out += buf;
    out.push_back(',');
    domui_json_key(out, "top", level + 3, pretty);
    snprintf(buf, sizeof(buf), "%d", w.padding.top);
    out += buf;
    out.push_back(',');
    domui_json_key(out, "bottom", level + 3, pretty);
    snprintf(buf, sizeof(buf), "%d", w.padding.bottom);
    out += buf;
    domui_json_indent(out, level + 2, pretty);
    out.push_back('}');
    out.push_back(',');
    domui_json_key(out, "constraints", level + 2, pretty);
    out.push_back('{');
    domui_json_key(out, "min_w", level + 3, pretty);
    snprintf(buf, sizeof(buf), "%d", w.min_w);
    out += buf;
    out.push_back(',');
    domui_json_key(out, "min_h", level + 3, pretty);
    snprintf(buf, sizeof(buf), "%d", w.min_h);
    out += buf;
    out.push_back(',');
    domui_json_key(out, "max_w", level + 3, pretty);
    snprintf(buf, sizeof(buf), "%d", w.max_w);
    out += buf;
    out.push_back(',');
    domui_json_key(out, "max_h", level + 3, pretty);
    snprintf(buf, sizeof(buf), "%d", w.max_h);
    out += buf;
    domui_json_indent(out, level + 2, pretty);
    out.push_back('}');
    domui_json_indent(out, level + 1, pretty);
    out.push_back('}');

    out.push_back(',');
    domui_json_key(out, "props", level + 1, pretty);
    domui_json_write_props(out, w.props, level + 1, pretty);
    out.push_back(',');
    domui_json_key(out, "events", level + 1, pretty);
    domui_json_write_events(out, w.events, level + 1, pretty);
    domui_json_indent(out, level, pretty);
    out.push_back('}');
}

static std::string domui_build_json(const domui_doc& doc, bool pretty)
{
    std::string out;
    char buf[32];
    std::vector<domui_widget_id> order;
    size_t i;
    int level = 0;

    out.push_back('{');
    domui_json_key(out, "doc_version", level + 1, pretty);
    snprintf(buf, sizeof(buf), "%u", (unsigned int)doc.meta.doc_version);
    out += buf;
    out.push_back(',');
    domui_json_key(out, "doc_name", level + 1, pretty);
    domui_json_string(out, doc.meta.doc_name);
    out.push_back(',');
    domui_json_key(out, "doc_guid", level + 1, pretty);
    domui_json_string(out, doc.meta.doc_guid);
    out.push_back(',');
    domui_json_key(out, "target_backends", level + 1, pretty);
    domui_json_write_string_list(out, doc.meta.target_backends, level + 1, pretty);
    out.push_back(',');
    domui_json_key(out, "target_tiers", level + 1, pretty);
    domui_json_write_string_list(out, doc.meta.target_tiers, level + 1, pretty);
    out.push_back(',');
    domui_json_key(out, "widgets", level + 1, pretty);

    out.push_back('[');
    doc.canonical_widget_order(order);
    for (i = 0u; i < order.size(); ++i) {
        const domui_widget* w = doc.find_by_id(order[i]);
        if (!w) {
            continue;
        }
        if (i != 0u) {
            out.push_back(',');
        }
        domui_json_indent(out, level + 2, pretty);
        domui_json_write_widget(out, *w, level + 2, pretty);
    }
    if (!order.empty()) {
        domui_json_indent(out, level + 1, pretty);
    }
    out.push_back(']');

    domui_json_indent(out, level, pretty);
    out.push_back('}');
    if (pretty) {
        out.push_back('\n');
    }
    return out;
}

bool domui_doc_save_json_mirror(const domui_doc* doc, const char* json_path, domui_diag* diag)
{
    std::string json;
    std::string compact;
    if (!doc || !json_path) {
        if (diag) {
            diag->add_error("json mirror: invalid args", 0u, "");
        }
        return false;
    }

    json = domui_build_json(*doc, true);
    if (json.size() > DOMUI_JSON_MAX_PRETTY) {
        compact = domui_build_json(*doc, false);
        return domui_atomic_write_file(json_path, compact.c_str(), compact.size(), diag);
    }
    return domui_atomic_write_file(json_path, json.c_str(), json.size(), diag);
}
