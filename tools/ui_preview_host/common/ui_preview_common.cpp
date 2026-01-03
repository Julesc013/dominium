/*
FILE: tools/ui_preview_host/common/ui_preview_common.cpp
MODULE: Dominium tools
RESPONSIBILITY: Shared helpers for UI preview hosts (doc loading, schema/state build, logging).
*/
#include "ui_preview_common.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cctype>

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <sys/stat.h>
#else
#include <sys/stat.h>
#endif

namespace {

static std::string ui_preview_trim(const std::string& s)
{
    size_t start = 0u;
    size_t end = s.size();
    while (start < end && std::isspace((unsigned char)s[start])) {
        ++start;
    }
    while (end > start && std::isspace((unsigned char)s[end - 1u])) {
        --end;
    }
    return s.substr(start, end - start);
}

static void ui_preview_split_simple(const std::string& s, char sep, std::vector<std::string>& out)
{
    size_t start = 0u;
    out.clear();
    while (start <= s.size()) {
        size_t pos = s.find(sep, start);
        if (pos == std::string::npos) {
            pos = s.size();
        }
        out.push_back(ui_preview_trim(s.substr(start, pos - start)));
        if (pos == s.size()) {
            break;
        }
        start = pos + 1u;
    }
}

static bool ui_preview_is_backend_token(const std::string& token_lc)
{
    return token_lc == "win32" ||
           token_lc == "dgfx" ||
           token_lc == "null" ||
           token_lc == "gtk" ||
           token_lc == "macos";
}

static bool ui_preview_read_file_all(const std::string& path, std::string& out, std::string& err)
{
    FILE* f = std::fopen(path.c_str(), "rb");
    long size;
    out.clear();
    err.clear();
    if (!f) {
        err = "open_failed";
        return false;
    }
    if (std::fseek(f, 0, SEEK_END) != 0) {
        std::fclose(f);
        err = "seek_end_failed";
        return false;
    }
    size = std::ftell(f);
    if (size < 0) {
        std::fclose(f);
        err = "tell_failed";
        return false;
    }
    if (std::fseek(f, 0, SEEK_SET) != 0) {
        std::fclose(f);
        err = "seek_set_failed";
        return false;
    }
    out.resize((size_t)size);
    if (size > 0) {
        size_t got = std::fread(&out[0], 1u, (size_t)size, f);
        if (got != (size_t)size) {
            std::fclose(f);
            out.clear();
            err = "read_failed";
            return false;
        }
    }
    std::fclose(f);
    return true;
}

static void ui_preview_skip_ws(const std::string& s, size_t& pos)
{
    while (pos < s.size() && std::isspace((unsigned char)s[pos])) {
        ++pos;
    }
}

static bool ui_preview_parse_json_string(const std::string& s, size_t& pos, std::string& out, std::string& err)
{
    ui_preview_skip_ws(s, pos);
    out.clear();
    if (pos >= s.size() || s[pos] != '"') {
        err = "expected_string";
        return false;
    }
    ++pos;
    while (pos < s.size()) {
        char c = s[pos++];
        if (c == '"') {
            return true;
        }
        if (c == '\\') {
            if (pos >= s.size()) {
                err = "bad_escape";
                return false;
            }
            char esc = s[pos++];
            switch (esc) {
            case '"': out.push_back('"'); break;
            case '\\': out.push_back('\\'); break;
            case '/': out.push_back('/'); break;
            case 'n': out.push_back('\n'); break;
            case 'r': out.push_back('\r'); break;
            case 't': out.push_back('\t'); break;
            case 'b': out.push_back('\b'); break;
            case 'f': out.push_back('\f'); break;
            default:
                out.push_back(esc);
                break;
            }
        } else {
            out.push_back(c);
        }
    }
    err = "unterminated_string";
    return false;
}

static bool ui_preview_parse_u32(const std::string& s, size_t& pos, domui_action_id* out, std::string& err)
{
    ui_preview_skip_ws(s, pos);
    if (pos >= s.size() || !std::isdigit((unsigned char)s[pos])) {
        err = "expected_number";
        return false;
    }
    unsigned long v = 0u;
    while (pos < s.size() && std::isdigit((unsigned char)s[pos])) {
        v = v * 10u + (unsigned long)(s[pos] - '0');
        ++pos;
    }
    if (out) {
        *out = (domui_action_id)v;
    }
    return true;
}

static domui_action_id ui_preview_fnv1a32(const void* data, size_t len)
{
    const unsigned char* p = (const unsigned char*)data;
    domui_action_id h = 2166136261u;
    size_t i;
    for (i = 0u; i < len; ++i) {
        h ^= (domui_action_id)p[i];
        h *= 16777619u;
    }
    return h;
}

static domui_action_id ui_preview_fallback_action_id(const std::string& key)
{
    domui_action_id h = ui_preview_fnv1a32(key.data(), key.size());
    h &= 0x7FFFFFFFu;
    if (h == 0u) {
        h = 1u;
    }
    h |= 0x80000000u;
    return h;
}

static domui_action_id ui_preview_stable_item_id(const std::string& s)
{
    domui_action_id h = ui_preview_fnv1a32(s.data(), s.size());
    if (h == 0u) {
        h = 1u;
    }
    return h;
}

static int ui_preview_prop_get_int_default(const domui_props& props, const char* key, int def_v)
{
    domui_value v;
    if (!props.get(key, &v)) {
        return def_v;
    }
    if (v.type == DOMUI_VALUE_INT) {
        return v.v_int;
    }
    if (v.type == DOMUI_VALUE_UINT) {
        return (int)v.v_uint;
    }
    if (v.type == DOMUI_VALUE_BOOL) {
        return v.v_bool ? 1 : 0;
    }
    return def_v;
}

static int ui_preview_prop_get_u32(const domui_props& props, const char* key, domui_u32* out)
{
    domui_value v;
    if (!props.get(key, &v)) {
        return 0;
    }
    if (v.type == DOMUI_VALUE_INT) {
        if (out) *out = (domui_u32)v.v_int;
        return 1;
    }
    if (v.type == DOMUI_VALUE_UINT) {
        if (out) *out = v.v_uint;
        return 1;
    }
    if (v.type == DOMUI_VALUE_BOOL) {
        if (out) *out = v.v_bool ? 1u : 0u;
        return 1;
    }
    return 0;
}

static int ui_preview_prop_get_string(const domui_props& props, const char* key, std::string& out)
{
    domui_value v;
    if (!props.get(key, &v)) {
        return 0;
    }
    if (v.type != DOMUI_VALUE_STRING) {
        return 0;
    }
    out = v.v_string.str();
    return 1;
}

static std::string ui_preview_widget_text(const domui_widget* w)
{
    std::string text;
    if (!w) {
        return text;
    }
    if (ui_preview_prop_get_string(w->props, "text", text)) {
        return text;
    }
    if (w->type == DOMUI_WIDGET_TAB_PAGE &&
        ui_preview_prop_get_string(w->props, "tab.title", text)) {
        return text;
    }
    return w->name.str();
}

static int ui_preview_pick_action_key(const domui_widget* w, domui_string& out_key)
{
    if (!w) {
        return 0;
    }
    if (w->events.get("on_tab_change", &out_key)) {
        return 1;
    }
    if (w->events.get("on_click", &out_key)) {
        return 1;
    }
    if (w->events.get("on_change", &out_key)) {
        return 1;
    }
    if (w->events.get("on_submit", &out_key)) {
        return 1;
    }
    return 0;
}

static u32 ui_preview_dui_kind_for_widget(domui_widget_type type)
{
    switch (type) {
    case DOMUI_WIDGET_CONTAINER: return (u32)DUI_NODE_STACK;
    case DOMUI_WIDGET_STATIC_TEXT: return (u32)DUI_NODE_LABEL;
    case DOMUI_WIDGET_BUTTON: return (u32)DUI_NODE_BUTTON;
    case DOMUI_WIDGET_EDIT: return (u32)DUI_NODE_TEXT_FIELD;
    case DOMUI_WIDGET_LISTBOX: return (u32)DUI_NODE_LIST;
    case DOMUI_WIDGET_COMBOBOX: return (u32)DUI_NODE_LIST;
    case DOMUI_WIDGET_CHECKBOX: return (u32)DUI_NODE_CHECKBOX;
    case DOMUI_WIDGET_RADIO: return (u32)DUI_NODE_CHECKBOX;
    case DOMUI_WIDGET_TAB: return (u32)DUI_NODE_TABS;
    case DOMUI_WIDGET_TREEVIEW: return (u32)DUI_NODE_LIST;
    case DOMUI_WIDGET_LISTVIEW: return (u32)DUI_NODE_LIST;
    case DOMUI_WIDGET_PROGRESS: return (u32)DUI_NODE_PROGRESS;
    case DOMUI_WIDGET_SLIDER: return (u32)DUI_NODE_PROGRESS;
    case DOMUI_WIDGET_GROUPBOX: return (u32)DUI_NODE_STACK;
    case DOMUI_WIDGET_IMAGE: return (u32)DUI_NODE_LABEL;
    case DOMUI_WIDGET_SPLITTER: return (u32)DUI_NODE_SPLITTER;
    case DOMUI_WIDGET_SCROLLPANEL: return (u32)DUI_NODE_SCROLL_PANEL;
    case DOMUI_WIDGET_TABS: return (u32)DUI_NODE_TABS;
    case DOMUI_WIDGET_TAB_PAGE: return (u32)DUI_NODE_TAB_PAGE;
    default:
        break;
    }
    return (u32)DUI_NODE_STACK;
}

static int ui_preview_widget_has_binding(domui_widget_type type)
{
    switch (type) {
    case DOMUI_WIDGET_EDIT:
    case DOMUI_WIDGET_LISTBOX:
    case DOMUI_WIDGET_COMBOBOX:
    case DOMUI_WIDGET_CHECKBOX:
    case DOMUI_WIDGET_RADIO:
    case DOMUI_WIDGET_LISTVIEW:
    case DOMUI_WIDGET_TREEVIEW:
    case DOMUI_WIDGET_PROGRESS:
    case DOMUI_WIDGET_SLIDER:
        return 1;
    default:
        break;
    }
    return 0;
}

static void ui_preview_tlv_write_u32(std::vector<unsigned char>& out, u32 v)
{
    out.push_back((unsigned char)(v & 0xFFu));
    out.push_back((unsigned char)((v >> 8u) & 0xFFu));
    out.push_back((unsigned char)((v >> 16u) & 0xFFu));
    out.push_back((unsigned char)((v >> 24u) & 0xFFu));
}

static void ui_preview_tlv_write_tlv(std::vector<unsigned char>& out, u32 tag, const void* payload, size_t len)
{
    ui_preview_tlv_write_u32(out, tag);
    ui_preview_tlv_write_u32(out, (u32)len);
    if (payload && len > 0u) {
        const unsigned char* p = (const unsigned char*)payload;
        out.insert(out.end(), p, p + len);
    }
}

static void ui_preview_tlv_write_u32_value(std::vector<unsigned char>& out, u32 tag, u32 v)
{
    unsigned char tmp[4];
    tmp[0] = (unsigned char)(v & 0xFFu);
    tmp[1] = (unsigned char)((v >> 8u) & 0xFFu);
    tmp[2] = (unsigned char)((v >> 16u) & 0xFFu);
    tmp[3] = (unsigned char)((v >> 24u) & 0xFFu);
    ui_preview_tlv_write_tlv(out, tag, tmp, sizeof(tmp));
}

static void ui_preview_tlv_write_rect(std::vector<unsigned char>& out, u32 tag, int x, int y, int w, int h)
{
    unsigned char tmp[16];
    u32 ux = (u32)x;
    u32 uy = (u32)y;
    u32 uw = (u32)w;
    u32 uh = (u32)h;
    tmp[0] = (unsigned char)(ux & 0xFFu);
    tmp[1] = (unsigned char)((ux >> 8u) & 0xFFu);
    tmp[2] = (unsigned char)((ux >> 16u) & 0xFFu);
    tmp[3] = (unsigned char)((ux >> 24u) & 0xFFu);
    tmp[4] = (unsigned char)(uy & 0xFFu);
    tmp[5] = (unsigned char)((uy >> 8u) & 0xFFu);
    tmp[6] = (unsigned char)((uy >> 16u) & 0xFFu);
    tmp[7] = (unsigned char)((uy >> 24u) & 0xFFu);
    tmp[8] = (unsigned char)(uw & 0xFFu);
    tmp[9] = (unsigned char)((uw >> 8u) & 0xFFu);
    tmp[10] = (unsigned char)((uw >> 16u) & 0xFFu);
    tmp[11] = (unsigned char)((uw >> 24u) & 0xFFu);
    tmp[12] = (unsigned char)(uh & 0xFFu);
    tmp[13] = (unsigned char)((uh >> 8u) & 0xFFu);
    tmp[14] = (unsigned char)((uh >> 16u) & 0xFFu);
    tmp[15] = (unsigned char)((uh >> 24u) & 0xFFu);
    ui_preview_tlv_write_tlv(out, tag, tmp, sizeof(tmp));
}

static void ui_preview_tlv_write_string(std::vector<unsigned char>& out, u32 tag, const std::string& s)
{
    ui_preview_tlv_write_tlv(out, tag, s.empty() ? 0 : s.c_str(), s.size());
}

static void ui_preview_build_dui_node(const domui_doc& doc,
                                      domui_widget_id id,
                                      const std::map<domui_widget_id, domui_layout_rect>& layout,
                                      UiPreviewActionRegistry& actions,
                                      std::vector<unsigned char>& out_payload)
{
    const domui_widget* w = doc.find_by_id(id);
    std::vector<unsigned char> node_payload;
    std::vector<unsigned char> children_payload;
    std::vector<domui_widget_id> children;
    domui_action_id action_id = 0u;
    domui_string action_key;
    domui_layout_rect rect;
    u32 flags = DUI_NODE_FLAG_ABSOLUTE;
    std::string text;

    if (!w) {
        return;
    }

    ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_ID_U32, (u32)w->id);
    ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_KIND_U32, ui_preview_dui_kind_for_widget(w->type));

    text = ui_preview_widget_text(w);
    if (!text.empty() &&
        (w->type == DOMUI_WIDGET_STATIC_TEXT ||
         w->type == DOMUI_WIDGET_BUTTON ||
         w->type == DOMUI_WIDGET_CHECKBOX ||
         w->type == DOMUI_WIDGET_RADIO ||
         w->type == DOMUI_WIDGET_EDIT ||
         w->type == DOMUI_WIDGET_GROUPBOX ||
         w->type == DOMUI_WIDGET_TAB_PAGE)) {
        ui_preview_tlv_write_string(node_payload, DUI_TLV_TEXT_UTF8, text);
    }

    if (ui_preview_pick_action_key(w, action_key) && !action_key.empty()) {
        action_id = actions.lookup_or_fallback(action_key.str());
    }
    if (action_id != 0u) {
        ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_ACTION_U32, (u32)action_id);
    }

    if (ui_preview_widget_has_binding(w->type)) {
        ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_BIND_U32, (u32)w->id);
    }

    ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_FLAGS_U32, flags);

    rect.x = w->x;
    rect.y = w->y;
    rect.w = w->w;
    rect.h = w->h;
    {
        std::map<domui_widget_id, domui_layout_rect>::const_iterator it = layout.find(id);
        if (it != layout.end()) {
            rect = it->second;
        }
    }
    ui_preview_tlv_write_rect(node_payload, DUI_TLV_RECT_I32, rect.x, rect.y, rect.w, rect.h);

    if (w->type == DOMUI_WIDGET_SPLITTER) {
        std::string orient;
        int is_horizontal = 0;
        if (ui_preview_prop_get_string(w->props, "splitter.orientation", orient)) {
            const char* s = orient.c_str();
            if (s && (s[0] == 'h' || s[0] == 'H')) {
                is_horizontal = 1;
            }
        }
        ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_SPLITTER_ORIENT_U32,
                                       (u32)(is_horizontal ? DUI_SPLIT_HORIZONTAL : DUI_SPLIT_VERTICAL));
        ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_SPLITTER_POS_U32,
                                       (u32)ui_preview_prop_get_int_default(w->props, "splitter.pos", -1));
        ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_SPLITTER_THICK_U32,
                                       (u32)ui_preview_prop_get_int_default(w->props, "splitter.thickness", 4));
        ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_SPLITTER_MIN_A_U32,
                                       (u32)ui_preview_prop_get_int_default(w->props, "splitter.min_a", 0));
        ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_SPLITTER_MIN_B_U32,
                                       (u32)ui_preview_prop_get_int_default(w->props, "splitter.min_b", 0));
    } else if (w->type == DOMUI_WIDGET_TABS || w->type == DOMUI_WIDGET_TAB) {
        std::string placement;
        int placement_id = DUI_TABS_TOP;
        if (ui_preview_prop_get_string(w->props, "tabs.placement", placement) ||
            ui_preview_prop_get_string(w->props, "tab.placement", placement)) {
            const char* s = placement.c_str();
            if (s) {
                if (s[0] == 'b' || s[0] == 'B') placement_id = DUI_TABS_BOTTOM;
                else if (s[0] == 'l' || s[0] == 'L') placement_id = DUI_TABS_LEFT;
                else if (s[0] == 'r' || s[0] == 'R') placement_id = DUI_TABS_RIGHT;
            }
        }
        ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_TABS_SELECTED_U32,
                                       (u32)ui_preview_prop_get_int_default(w->props, "tabs.selected_index", 0));
        ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_TABS_PLACEMENT_U32, (u32)placement_id);
    } else if (w->type == DOMUI_WIDGET_TAB_PAGE) {
        ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_TAB_ENABLED_U32,
                                       (u32)ui_preview_prop_get_int_default(w->props, "tab.enabled", 1));
    } else if (w->type == DOMUI_WIDGET_SCROLLPANEL) {
        ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_SCROLL_H_ENABLED_U32,
                                       (u32)ui_preview_prop_get_int_default(w->props, "scroll.h_enabled", 1));
        ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_SCROLL_V_ENABLED_U32,
                                       (u32)ui_preview_prop_get_int_default(w->props, "scroll.v_enabled", 1));
        ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_SCROLL_X_U32,
                                       (u32)ui_preview_prop_get_int_default(w->props, "scroll.x", 0));
        ui_preview_tlv_write_u32_value(node_payload, DUI_TLV_SCROLL_Y_U32,
                                       (u32)ui_preview_prop_get_int_default(w->props, "scroll.y", 0));
    }

    doc.enumerate_children(id, children);
    for (size_t i = 0u; i < children.size(); ++i) {
        ui_preview_build_dui_node(doc, children[i], layout, actions, children_payload);
    }
    if (!children_payload.empty()) {
        ui_preview_tlv_write_tlv(node_payload, DUI_TLV_CHILDREN_V1,
                                 &children_payload[0], children_payload.size());
    }

    ui_preview_tlv_write_tlv(out_payload, DUI_TLV_NODE_V1,
                             node_payload.empty() ? 0 : &node_payload[0], node_payload.size());
}

struct UiPreviewListItem {
    domui_u32 id;
    std::string text;
    UiPreviewListItem(domui_u32 i, const std::string& t) : id(i), text(t) {}
};

static void ui_preview_append_tlv_raw(std::vector<unsigned char>& out, u32 tag, const void* payload, size_t payload_len)
{
    ui_preview_tlv_write_u32(out, tag);
    ui_preview_tlv_write_u32(out, (u32)payload_len);
    if (payload && payload_len > 0u) {
        const unsigned char* p = (const unsigned char*)payload;
        out.insert(out.end(), p, p + payload_len);
    }
}

static void ui_preview_append_tlv_u32(std::vector<unsigned char>& out, u32 tag, u32 v)
{
    ui_preview_tlv_write_u32_value(out, tag, v);
}

static void ui_preview_append_tlv_text(std::vector<unsigned char>& out, u32 tag, const std::string& s)
{
    ui_preview_tlv_write_string(out, tag, s);
}

static void ui_preview_state_add_text(std::vector<unsigned char>& inner, u32 bind_id, const std::string& text)
{
    std::vector<unsigned char> value;
    ui_preview_append_tlv_u32(value, DUI_TLV_BIND_U32, bind_id);
    ui_preview_append_tlv_u32(value, DUI_TLV_VALUE_TYPE_U32, (u32)DUI_VALUE_TEXT);
    ui_preview_append_tlv_text(value, DUI_TLV_VALUE_UTF8, text);
    ui_preview_append_tlv_raw(inner, DUI_TLV_VALUE_V1, value.empty() ? (const void*)0 : &value[0], value.size());
}

static void ui_preview_state_add_u32(std::vector<unsigned char>& inner, u32 bind_id, u32 value_type, u32 v)
{
    std::vector<unsigned char> value;
    ui_preview_append_tlv_u32(value, DUI_TLV_BIND_U32, bind_id);
    ui_preview_append_tlv_u32(value, DUI_TLV_VALUE_TYPE_U32, value_type);
    ui_preview_append_tlv_u32(value, DUI_TLV_VALUE_U32, v);
    ui_preview_append_tlv_raw(inner, DUI_TLV_VALUE_V1, value.empty() ? (const void*)0 : &value[0], value.size());
}

static void ui_preview_state_add_list(std::vector<unsigned char>& inner,
                                      u32 bind_id,
                                      u32 selected_item_id,
                                      const std::vector<UiPreviewListItem>& items)
{
    std::vector<unsigned char> list_payload;
    std::vector<unsigned char> value;
    ui_preview_append_tlv_u32(list_payload, DUI_TLV_LIST_SELECTED_U32, selected_item_id);
    for (size_t i = 0u; i < items.size(); ++i) {
        std::vector<unsigned char> item_payload;
        ui_preview_append_tlv_u32(item_payload, DUI_TLV_ITEM_ID_U32, items[i].id);
        ui_preview_append_tlv_text(item_payload, DUI_TLV_ITEM_TEXT_UTF8, items[i].text);
        ui_preview_append_tlv_raw(list_payload,
                                  DUI_TLV_LIST_ITEM_V1,
                                  item_payload.empty() ? (const void*)0 : &item_payload[0],
                                  item_payload.size());
    }
    ui_preview_append_tlv_u32(value, DUI_TLV_BIND_U32, bind_id);
    ui_preview_append_tlv_u32(value, DUI_TLV_VALUE_TYPE_U32, (u32)DUI_VALUE_LIST);
    ui_preview_append_tlv_raw(value,
                              DUI_TLV_LIST_V1,
                              list_payload.empty() ? (const void*)0 : &list_payload[0],
                              list_payload.size());
    ui_preview_append_tlv_raw(inner, DUI_TLV_VALUE_V1, value.empty() ? (const void*)0 : &value[0], value.size());
}

static void ui_preview_split_items(const std::string& s, std::vector<std::string>& out)
{
    out.clear();
    if (s.find('\n') != std::string::npos) {
        ui_preview_split_simple(s, '\n', out);
        return;
    }
    if (s.find('|') != std::string::npos) {
        ui_preview_split_simple(s, '|', out);
        return;
    }
    if (s.find(',') != std::string::npos) {
        ui_preview_split_simple(s, ',', out);
        return;
    }
    if (!s.empty()) {
        out.push_back(ui_preview_trim(s));
    }
}

static void ui_preview_default_list_items(std::vector<UiPreviewListItem>& out)
{
    out.push_back(UiPreviewListItem(1u, "Item 1"));
    out.push_back(UiPreviewListItem(2u, "Item 2"));
    out.push_back(UiPreviewListItem(3u, "Item 3"));
}

static void ui_preview_build_list_items(const domui_widget* w, std::vector<UiPreviewListItem>& out)
{
    std::string raw;
    std::vector<std::string> items;
    out.clear();
    if (ui_preview_prop_get_string(w->props, "items", raw) ||
        ui_preview_prop_get_string(w->props, "list.items", raw)) {
        ui_preview_split_items(raw, items);
        for (size_t i = 0u; i < items.size(); ++i) {
            if (!items[i].empty()) {
                out.push_back(UiPreviewListItem(ui_preview_stable_item_id(items[i]), items[i]));
            }
        }
    }
    if (out.empty()) {
        ui_preview_default_list_items(out);
    }
}

static std::string ui_preview_value_to_string(const domui_value& v)
{
    char buf[64];
    switch (v.type) {
    case DOMUI_VALUE_I32:
        std::sprintf(buf, "%d", v.u.v_i32);
        return std::string(buf);
    case DOMUI_VALUE_U32:
        std::sprintf(buf, "%u", (unsigned int)v.u.v_u32);
        return std::string(buf);
    case DOMUI_VALUE_BOOL:
        return v.u.v_bool ? "true" : "false";
    case DOMUI_VALUE_STR:
        if (v.u.v_str.ptr && v.u.v_str.len) {
            return std::string(v.u.v_str.ptr, v.u.v_str.len);
        }
        return std::string();
    case DOMUI_VALUE_VEC2I:
        std::sprintf(buf, "%d,%d", v.u.v_vec2i.x, v.u.v_vec2i.y);
        return std::string(buf);
    case DOMUI_VALUE_RECTI:
        std::sprintf(buf, "%d,%d,%d,%d", v.u.v_recti.x, v.u.v_recti.y, v.u.v_recti.w, v.u.v_recti.h);
        return std::string(buf);
    default:
        break;
    }
    return std::string();
}

static const char* ui_preview_event_type_name(domui_event_type t)
{
    switch (t) {
    case DOMUI_EVENT_CLICK: return "click";
    case DOMUI_EVENT_CHANGE: return "change";
    case DOMUI_EVENT_SUBMIT: return "submit";
    case DOMUI_EVENT_TAB_CHANGE: return "tab_change";
    case DOMUI_EVENT_KEYDOWN: return "keydown";
    case DOMUI_EVENT_KEYUP: return "keyup";
    case DOMUI_EVENT_TEXT_INPUT: return "text_input";
    case DOMUI_EVENT_MOUSE_DOWN: return "mouse_down";
    case DOMUI_EVENT_MOUSE_UP: return "mouse_up";
    case DOMUI_EVENT_MOUSE_MOVE: return "mouse_move";
    case DOMUI_EVENT_SCROLL: return "scroll";
    case DOMUI_EVENT_FOCUS_GAIN: return "focus_gain";
    case DOMUI_EVENT_FOCUS_LOST: return "focus_lost";
    case DOMUI_EVENT_CUSTOM: return "custom";
    default:
        break;
    }
    return "unknown";
}

} // namespace

UiPreviewLog::UiPreviewLog()
    : file(0)
{
}

UiPreviewLog::~UiPreviewLog()
{
    close_file();
}

bool UiPreviewLog::open_file(const std::string& path)
{
    close_file();
    if (path.empty()) {
        return false;
    }
    file = std::fopen(path.c_str(), "ab");
    return file != 0;
}

void UiPreviewLog::close_file()
{
    if (file) {
        std::fclose(file);
        file = 0;
    }
}

void UiPreviewLog::line(const std::string& text)
{
    if (!text.empty()) {
        std::fputs(text.c_str(), stdout);
    }
    std::fputc('\n', stdout);
    std::fflush(stdout);
#if defined(_WIN32)
    {
        std::string dbg = text;
        dbg.push_back('\n');
        OutputDebugStringA(dbg.c_str());
    }
#endif
    if (file) {
        if (!text.empty()) {
            std::fputs(text.c_str(), file);
        }
        std::fputc('\n', file);
        std::fflush(file);
    }
}

UiPreviewActionRegistry::UiPreviewActionRegistry()
    : key_to_id(),
      id_to_key(),
      loaded(0)
{
}

void UiPreviewActionRegistry::clear()
{
    key_to_id.clear();
    id_to_key.clear();
    loaded = 0;
}

domui_action_id UiPreviewActionRegistry::lookup_or_fallback(const std::string& key)
{
    std::map<std::string, domui_action_id>::const_iterator it = key_to_id.find(key);
    if (it != key_to_id.end()) {
        return it->second;
    }
    if (key.empty()) {
        return 0u;
    }
    domui_action_id id = ui_preview_fallback_action_id(key);
    key_to_id[key] = id;
    id_to_key[id] = key;
    return id;
}

const char* UiPreviewActionRegistry::key_from_id(domui_action_id id) const
{
    std::map<domui_action_id, std::string>::const_iterator it = id_to_key.find(id);
    if (it != id_to_key.end()) {
        return it->second.c_str();
    }
    return 0;
}

bool ui_preview_parse_targets(const char* list, UiPreviewTargets& out_targets, std::string& out_err)
{
    std::vector<std::string> tokens;
    out_err.clear();
    out_targets.targets.backends.clear();
    out_targets.targets.tiers.clear();
    out_targets.tokens.clear();
    if (!list || !list[0]) {
        return true;
    }
    ui_preview_split_simple(list, ',', tokens);
    for (size_t i = 0u; i < tokens.size(); ++i) {
        std::string token = ui_preview_trim(tokens[i]);
        if (token.empty()) {
            continue;
        }
        out_targets.tokens.push_back(token);
        std::string token_lc = ui_preview_to_lower(token);
        if (ui_preview_is_backend_token(token_lc)) {
            out_targets.targets.backends.push_back(domui_string(token.c_str()));
        } else {
            out_targets.targets.tiers.push_back(domui_string(token.c_str()));
        }
    }
    return true;
}

bool ui_preview_load_action_registry(const std::string& path, UiPreviewActionRegistry& out_registry, std::string& out_err)
{
    std::string text;
    size_t pos;
    out_err.clear();
    out_registry.clear();
    if (path.empty()) {
        out_err = "no_registry_path";
        return false;
    }
    if (!ui_preview_read_file_all(path, text, out_err)) {
        return false;
    }
    pos = text.find("\"actions\"");
    if (pos == std::string::npos) {
        out_err = "actions_not_found";
        return false;
    }
    pos = text.find('{', pos);
    if (pos == std::string::npos) {
        out_err = "actions_object_missing";
        return false;
    }
    ++pos;
    while (pos < text.size()) {
        std::string key;
        domui_action_id id = 0u;
        ui_preview_skip_ws(text, pos);
        if (pos < text.size() && text[pos] == '}') {
            ++pos;
            break;
        }
        if (!ui_preview_parse_json_string(text, pos, key, out_err)) {
            return false;
        }
        ui_preview_skip_ws(text, pos);
        if (pos >= text.size() || text[pos] != ':') {
            out_err = "expected_colon";
            return false;
        }
        ++pos;
        if (!ui_preview_parse_u32(text, pos, &id, out_err)) {
            return false;
        }
        if (!key.empty() && id != 0u) {
            out_registry.key_to_id[key] = id;
            out_registry.id_to_key[id] = key;
        }
        ui_preview_skip_ws(text, pos);
        if (pos < text.size() && text[pos] == ',') {
            ++pos;
            continue;
        }
        if (pos < text.size() && text[pos] == '}') {
            ++pos;
            break;
        }
    }
    out_registry.loaded = 1;
    return true;
}

std::string ui_preview_guess_registry_path(const std::string& ui_doc_path)
{
    std::string doc_dir = ui_preview_dirname(ui_doc_path);
    std::string doc_base = ui_preview_basename_no_ext(ui_doc_path);
    std::string ui_root = doc_dir;
    std::string reg_dir;
    std::vector<std::string> candidates;

    if (ui_preview_to_lower(ui_preview_basename(doc_dir)) == "doc") {
        ui_root = ui_preview_dirname(doc_dir);
    }
    if (ui_root.empty()) {
        return std::string();
    }
    reg_dir = ui_preview_join(ui_root, "registry");

    if (!doc_base.empty()) {
        std::string base = doc_base;
        size_t pos = base.rfind("_ui_doc");
        if (pos != std::string::npos) {
            base = base.substr(0u, pos);
        }
        if (!base.empty()) {
            candidates.push_back(base + "_actions_registry.json");
        }
    }
    candidates.push_back("ui_actions_registry.json");

    for (size_t i = 0u; i < candidates.size(); ++i) {
        std::string path = ui_preview_join(reg_dir, candidates[i]);
        if (ui_preview_file_exists(path)) {
            return path;
        }
    }
    return std::string();
}

void ui_preview_collect_watch_dirs(const std::string& ui_doc_path,
                                   const std::string& registry_path,
                                   std::vector<std::string>& out_dirs)
{
    std::string doc_dir = ui_preview_dirname(ui_doc_path);
    std::string ui_root = doc_dir;
    out_dirs.clear();
    if (!doc_dir.empty()) {
        out_dirs.push_back(doc_dir);
    }
    if (ui_preview_to_lower(ui_preview_basename(doc_dir)) == "doc") {
        ui_root = ui_preview_dirname(doc_dir);
    }
    if (!ui_root.empty()) {
        std::string gen_dir = ui_preview_join(ui_root, "gen");
        std::string user_dir = ui_preview_join(ui_root, "user");
        std::string registry_dir = ui_preview_join(ui_root, "registry");
        if (ui_preview_is_dir(gen_dir)) {
            out_dirs.push_back(gen_dir);
        }
        if (ui_preview_is_dir(user_dir)) {
            out_dirs.push_back(user_dir);
        }
        if (ui_preview_is_dir(registry_dir)) {
            out_dirs.push_back(registry_dir);
        }
    }
    if (!registry_path.empty()) {
        std::string reg_dir = ui_preview_dirname(registry_path);
        if (!reg_dir.empty()) {
            out_dirs.push_back(reg_dir);
        }
    }
}

bool ui_preview_file_exists(const std::string& path)
{
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) {
        return false;
    }
    std::fclose(f);
    return true;
}

bool ui_preview_is_dir(const std::string& path)
{
#if defined(_WIN32)
    struct _stat info;
    if (_stat(path.c_str(), &info) != 0) {
        return false;
    }
    return (info.st_mode & _S_IFDIR) != 0;
#else
    struct stat info;
    if (stat(path.c_str(), &info) != 0) {
        return false;
    }
    return S_ISDIR(info.st_mode) != 0;
#endif
}

std::string ui_preview_dirname(const std::string& path)
{
    size_t pos = path.find_last_of("/\\");
    if (pos == std::string::npos) {
        return std::string();
    }
    return path.substr(0u, pos);
}

std::string ui_preview_basename(const std::string& path)
{
    size_t pos = path.find_last_of("/\\");
    if (pos == std::string::npos) {
        return path;
    }
    return path.substr(pos + 1u);
}

std::string ui_preview_basename_no_ext(const std::string& path)
{
    std::string base = ui_preview_basename(path);
    size_t dot = base.find_last_of('.');
    if (dot == std::string::npos) {
        return base;
    }
    return base.substr(0u, dot);
}

std::string ui_preview_join(const std::string& a, const std::string& b)
{
    if (a.empty()) {
        return b;
    }
    if (b.empty()) {
        return a;
    }
    if (a[a.size() - 1u] == '/' || a[a.size() - 1u] == '\\') {
        return a + b;
    }
    return a + "/" + b;
}

std::string ui_preview_to_lower(const std::string& in)
{
    std::string out = in;
    for (size_t i = 0u; i < out.size(); ++i) {
        out[i] = (char)std::tolower((unsigned char)out[i]);
    }
    return out;
}

bool ui_preview_load_doc(const char* path, UiPreviewDoc& out_doc, UiPreviewLog& log, domui_diag* out_diag)
{
    std::vector<domui_widget_id> roots;
    out_doc.doc.clear();
    out_doc.root_id = 0u;
    out_doc.layout.clear();
    out_doc.layout_results.clear();
    out_doc.schema.clear();
    out_doc.state.clear();
    if (out_diag) {
        out_diag->clear();
    }
    if (!path || !path[0]) {
        if (out_diag) {
            out_diag->add_error("preview: missing ui_doc path", 0u, "");
        }
        return false;
    }
    if (!domui_doc_load_tlv(&out_doc.doc, path, out_diag)) {
        ui_preview_log_diag(log, out_diag ? *out_diag : domui_diag());
        return false;
    }
    out_doc.doc.enumerate_children(0u, roots);
    if (roots.empty()) {
        if (out_diag) {
            out_diag->add_error("preview: ui_doc has no root widget", 0u, "");
        }
        return false;
    }
    out_doc.root_id = roots[0];
    return true;
}

bool ui_preview_build_layout(UiPreviewDoc& doc, int width, int height, domui_diag* out_diag)
{
    int count;
    if (width <= 0) width = 800;
    if (height <= 0) height = 600;
    doc.layout_results.clear();
    doc.layout.clear();
    if (out_diag) {
        out_diag->clear();
    }
    doc.layout_results.resize(doc.doc.widget_count() + 1u);
    count = (int)doc.layout_results.size();
    if (!domui_compute_layout(&doc.doc, doc.root_id, 0, 0, width, height, &doc.layout_results[0], &count, out_diag)) {
        return false;
    }
    doc.layout_results.resize((size_t)count);
    for (size_t i = 0u; i < doc.layout_results.size(); ++i) {
        doc.layout[doc.layout_results[i].widget_id] = doc.layout_results[i].rect;
    }
    return true;
}

bool ui_preview_build_schema(UiPreviewDoc& doc, UiPreviewActionRegistry& actions)
{
    std::vector<unsigned char> form_payload;
    std::vector<unsigned char> schema_payload;
    doc.schema.clear();
    if (doc.root_id == 0u) {
        return false;
    }
    ui_preview_build_dui_node(doc.doc, doc.root_id, doc.layout, actions, form_payload);
    if (form_payload.empty()) {
        return false;
    }
    ui_preview_tlv_write_tlv(schema_payload, DUI_TLV_FORM_V1,
                             &form_payload[0], form_payload.size());
    ui_preview_tlv_write_tlv(doc.schema, DUI_TLV_SCHEMA_V1,
                             &schema_payload[0], schema_payload.size());
    return true;
}

bool ui_preview_build_state(UiPreviewDoc& doc)
{
    std::vector<unsigned char> inner;
    std::vector<domui_widget_id> order;
    doc.state.clear();
    doc.doc.canonical_widget_order(order);
    for (size_t i = 0u; i < order.size(); ++i) {
        const domui_widget* w = doc.doc.find_by_id(order[i]);
        if (!w) {
            continue;
        }
        if (!ui_preview_widget_has_binding(w->type)) {
            continue;
        }
        if (w->type == DOMUI_WIDGET_LISTBOX ||
            w->type == DOMUI_WIDGET_COMBOBOX ||
            w->type == DOMUI_WIDGET_LISTVIEW ||
            w->type == DOMUI_WIDGET_TREEVIEW) {
            std::vector<UiPreviewListItem> items;
            domui_u32 selected_index = 0u;
            domui_u32 selected_id = 0u;
            ui_preview_build_list_items(w, items);
            if (ui_preview_prop_get_u32(w->props, "selected_index", &selected_index) ||
                ui_preview_prop_get_u32(w->props, "list.selected_index", &selected_index)) {
                if (selected_index < items.size()) {
                    selected_id = items[selected_index].id;
                }
            } else if (ui_preview_prop_get_u32(w->props, "selected_id", &selected_id)) {
                /* use provided selected id */
            }
            ui_preview_state_add_list(inner, (u32)w->id, selected_id, items);
        } else if (w->type == DOMUI_WIDGET_CHECKBOX || w->type == DOMUI_WIDGET_RADIO) {
            domui_u32 checked = 0u;
            if (ui_preview_prop_get_u32(w->props, "checked", &checked) ||
                ui_preview_prop_get_u32(w->props, "value", &checked)) {
                ui_preview_state_add_u32(inner, (u32)w->id, (u32)DUI_VALUE_BOOL, checked ? 1u : 0u);
            }
        } else if (w->type == DOMUI_WIDGET_EDIT) {
            std::string val;
            if (ui_preview_prop_get_string(w->props, "value", val) ||
                ui_preview_prop_get_string(w->props, "text", val)) {
                ui_preview_state_add_text(inner, (u32)w->id, val);
            }
        } else if (w->type == DOMUI_WIDGET_PROGRESS || w->type == DOMUI_WIDGET_SLIDER) {
            domui_u32 v = 0u;
            if (ui_preview_prop_get_u32(w->props, "value", &v)) {
                ui_preview_state_add_u32(inner, (u32)w->id, (u32)DUI_VALUE_U32, v);
            }
        }
    }
    if (inner.empty()) {
        return true;
    }
    ui_preview_append_tlv_raw(doc.state, DUI_TLV_STATE_V1, &inner[0], inner.size());
    return true;
}

bool ui_preview_validate_doc(const UiPreviewDoc& doc, const UiPreviewTargets& targets, domui_diag* out_diag)
{
    const domui_target_set* ptr = 0;
    if (out_diag) {
        out_diag->clear();
    }
    if (!targets.targets.backends.empty() || !targets.targets.tiers.empty()) {
        ptr = &targets.targets;
    }
    return domui_validate_doc(&doc.doc, ptr, out_diag);
}

void ui_preview_log_diag(UiPreviewLog& log, const domui_diag& diag)
{
    size_t i;
    for (i = 0u; i < diag.errors().size(); ++i) {
        std::string line = "error: ";
        line.append(diag.errors()[i].message.c_str());
        log.line(line);
    }
    for (i = 0u; i < diag.warnings().size(); ++i) {
        std::string line = "warn: ";
        line.append(diag.warnings()[i].message.c_str());
        log.line(line);
    }
}

void ui_preview_action_dispatch(void* user_ctx, const domui_event* e)
{
    UiPreviewActionContext* ctx = (UiPreviewActionContext*)user_ctx;
    const char* key = 0;
    if (!ctx || !ctx->log || !e) {
        return;
    }
    if (ctx->registry) {
        key = ctx->registry->key_from_id(e->action_id);
    }
    {
        char buf[256];
        std::string line = "action: ";
        std::sprintf(buf, "id=%u widget=%u type=%s", (unsigned int)e->action_id,
                     (unsigned int)e->widget_id, ui_preview_event_type_name(e->type));
        line.append(buf);
        if (key) {
            line.append(" key=");
            line.append(key);
        }
        if (e->a.type != DOMUI_VALUE_NONE) {
            line.append(" a=");
            line.append(ui_preview_value_to_string(e->a));
        }
        if (e->b.type != DOMUI_VALUE_NONE) {
            line.append(" b=");
            line.append(ui_preview_value_to_string(e->b));
        }
        ctx->log->line(line);
    }
}
