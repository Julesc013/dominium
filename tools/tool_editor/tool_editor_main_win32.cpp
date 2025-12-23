/*
FILE: tools/tool_editor/tool_editor_main_win32.cpp
MODULE: Dominium tools
RESPONSIBILITY: Minimal Tool Editor host that loads a DUI UI doc and edits ui_doc.tlv files.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <map>
#include <string>
#include <algorithm>

#include "domino/core/types.h"

#include "ui_ir_doc.h"
#include "ui_ir_tlv.h"
#include "ui_ir_diag.h"
#include "ui_ir_props.h"
#include "ui_layout.h"
#include "ui_validate.h"

#include "tool_editor_actions.h"

struct domui_event;
typedef void (*domui_action_fn)(void* user_ctx, const domui_event* e);
#define DOMUI_EVENT_H_INCLUDED

#include "dui/dui_api_v1.h"
#include "dui/dui_schema_tlv.h"

#include "ui_tool_editor_actions_gen.h"

#if !defined(_WIN32)

int main(void)
{
    printf("dominium-tool-editor: not supported on this platform\n");
    return 0;
}

#else

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <commdlg.h>
#include <commctrl.h>

extern "C" const void* dom_dui_win32_get_api(u32 requested_abi);

static const char* kToolEditorUiDoc = "tools/tool_editor/ui/doc/tool_editor_ui_doc.tlv";
static const char* kToolEditorTemplateDoc = "tools/tool_editor/ui/doc/ui_doc_template_basic.tlv";
static const int kMaxDocs = 4;
enum ToolEditorAddMenuId {
    TOOL_EDITOR_MENU_ADD_CONTAINER = 1001,
    TOOL_EDITOR_MENU_ADD_LABEL,
    TOOL_EDITOR_MENU_ADD_BUTTON,
    TOOL_EDITOR_MENU_ADD_EDIT,
    TOOL_EDITOR_MENU_ADD_LISTBOX,
    TOOL_EDITOR_MENU_ADD_CHECKBOX,
    TOOL_EDITOR_MENU_ADD_TABS,
    TOOL_EDITOR_MENU_ADD_TAB_PAGE,
    TOOL_EDITOR_MENU_ADD_SPLITTER,
    TOOL_EDITOR_MENU_ADD_SCROLLPANEL
};

static LRESULT CALLBACK ToolEditor_WndProc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam);

static std::string ui_path_basename(const std::string& path)
{
    size_t pos = path.find_last_of("/\\");
    std::string name = (pos == std::string::npos) ? path : path.substr(pos + 1u);
    size_t dot = name.find_last_of('.');
    if (dot != std::string::npos) {
        name = name.substr(0u, dot);
    }
    return name;
}

static std::string ui_to_lower(const std::string& in)
{
    std::string out = in;
    for (size_t i = 0u; i < out.size(); ++i) {
        out[i] = (char)std::tolower((unsigned char)out[i]);
    }
    return out;
}

static int ui_parse_int(const std::string& s, int* out)
{
    char* end = 0;
    long v = std::strtol(s.c_str(), &end, 10);
    if (!end || end == s.c_str()) {
        return 0;
    }
    while (*end && std::isspace((unsigned char)*end)) {
        end++;
    }
    if (*end != '\0') {
        return 0;
    }
    if (out) {
        *out = (int)v;
    }
    return 1;
}

static HWND ui_find_child_by_id(HWND parent, int id)
{
    HWND child = GetWindow(parent, GW_CHILD);
    while (child) {
        if (GetDlgCtrlID(child) == id) {
            return child;
        }
        {
            HWND found = ui_find_child_by_id(child, id);
            if (found) {
                return found;
            }
        }
        child = GetWindow(child, GW_HWNDNEXT);
    }
    return NULL;
}

static const char* ui_widget_type_name(domui_widget_type t)
{
    switch (t) {
    case DOMUI_WIDGET_CONTAINER: return "CONTAINER";
    case DOMUI_WIDGET_STATIC_TEXT: return "STATIC_TEXT";
    case DOMUI_WIDGET_BUTTON: return "BUTTON";
    case DOMUI_WIDGET_EDIT: return "EDIT";
    case DOMUI_WIDGET_LISTBOX: return "LISTBOX";
    case DOMUI_WIDGET_CHECKBOX: return "CHECKBOX";
    case DOMUI_WIDGET_TABS: return "TABS";
    case DOMUI_WIDGET_TAB_PAGE: return "TAB_PAGE";
    case DOMUI_WIDGET_SPLITTER: return "SPLITTER";
    case DOMUI_WIDGET_SCROLLPANEL: return "SCROLLPANEL";
    default:
        break;
    }
    return "WIDGET";
}

static u32 ui_map_widget_kind(domui_widget_type t)
{
    switch (t) {
    case DOMUI_WIDGET_STATIC_TEXT: return (u32)DUI_NODE_LABEL;
    case DOMUI_WIDGET_BUTTON: return (u32)DUI_NODE_BUTTON;
    case DOMUI_WIDGET_EDIT: return (u32)DUI_NODE_TEXT_FIELD;
    case DOMUI_WIDGET_LISTBOX: return (u32)DUI_NODE_LIST;
    case DOMUI_WIDGET_CHECKBOX: return (u32)DUI_NODE_CHECKBOX;
    case DOMUI_WIDGET_PROGRESS: return (u32)DUI_NODE_PROGRESS;
    case DOMUI_WIDGET_SPLITTER: return (u32)DUI_NODE_SPLITTER;
    case DOMUI_WIDGET_TABS: return (u32)DUI_NODE_TABS;
    case DOMUI_WIDGET_TAB_PAGE: return (u32)DUI_NODE_TAB_PAGE;
    case DOMUI_WIDGET_SCROLLPANEL: return (u32)DUI_NODE_SCROLL_PANEL;
    default:
        break;
    }
    return (u32)DUI_NODE_STACK;
}

static int ui_prop_get_int_default(const domui_props& props, const char* key, int def_v)
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

static int ui_prop_get_string(const domui_props& props, const char* key, domui_string& out)
{
    domui_value v;
    if (!props.get(key, &v)) {
        return 0;
    }
    if (v.type != DOMUI_VALUE_STRING) {
        return 0;
    }
    out = v.v_string;
    return 1;
}

static std::string ui_widget_text(const domui_widget* w)
{
    domui_string s;
    if (!w) {
        return std::string();
    }
    if (ui_prop_get_string(w->props, "text", s)) {
        return s.str();
    }
    if (w->type == DOMUI_WIDGET_TAB_PAGE && ui_prop_get_string(w->props, "tab.title", s)) {
        return s.str();
    }
    return w->name.str();
}

static int ui_pick_action_key(const domui_widget* w, domui_string& out_key)
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

static void ui_tlv_write_u32(std::vector<unsigned char>& out, u32 v)
{
    out.push_back((unsigned char)(v & 0xFFu));
    out.push_back((unsigned char)((v >> 8u) & 0xFFu));
    out.push_back((unsigned char)((v >> 16u) & 0xFFu));
    out.push_back((unsigned char)((v >> 24u) & 0xFFu));
}

static void ui_tlv_write_tlv(std::vector<unsigned char>& out, u32 tag, const void* payload, size_t len)
{
    ui_tlv_write_u32(out, tag);
    ui_tlv_write_u32(out, (u32)len);
    if (payload && len > 0u) {
        const unsigned char* p = (const unsigned char*)payload;
        out.insert(out.end(), p, p + len);
    }
}

static void ui_tlv_write_u32_value(std::vector<unsigned char>& out, u32 tag, u32 v)
{
    unsigned char tmp[4];
    tmp[0] = (unsigned char)(v & 0xFFu);
    tmp[1] = (unsigned char)((v >> 8u) & 0xFFu);
    tmp[2] = (unsigned char)((v >> 16u) & 0xFFu);
    tmp[3] = (unsigned char)((v >> 24u) & 0xFFu);
    ui_tlv_write_tlv(out, tag, tmp, sizeof(tmp));
}

static void ui_tlv_write_i32_value(std::vector<unsigned char>& out, u32 tag, int v)
{
    ui_tlv_write_u32_value(out, tag, (u32)v);
}

static void ui_tlv_write_rect(std::vector<unsigned char>& out, u32 tag, int x, int y, int w, int h)
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
    ui_tlv_write_tlv(out, tag, tmp, sizeof(tmp));
}

static void ui_tlv_write_string(std::vector<unsigned char>& out, u32 tag, const std::string& s)
{
    ui_tlv_write_tlv(out, tag, s.empty() ? 0 : s.c_str(), s.size());
}

static bool ui_build_layout_map(const domui_doc& doc,
                                int width,
                                int height,
                                std::map<domui_widget_id, domui_layout_rect>& out_map,
                                std::vector<domui_layout_result>& out_results)
{
    domui_diag diag;
    int count;
    out_results.clear();
    out_map.clear();

    out_results.resize(doc.widget_count() + 1u);
    count = (int)out_results.size();
    if (!domui_compute_layout(&doc, 0u, 0, 0, width, height, &out_results[0], &count, &diag)) {
        return false;
    }
    out_results.resize(count);
    for (size_t i = 0u; i < out_results.size(); ++i) {
        out_map[out_results[i].widget_id] = out_results[i].rect;
    }
    return true;
}

static void ui_build_dui_node(const domui_doc& doc,
                              domui_widget_id id,
                              const std::map<domui_widget_id, domui_layout_rect>& layout,
                              bool include_actions,
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

    ui_tlv_write_u32_value(node_payload, DUI_TLV_ID_U32, (u32)w->id);
    ui_tlv_write_u32_value(node_payload, DUI_TLV_KIND_U32, ui_map_widget_kind(w->type));

    text = ui_widget_text(w);
    if (!text.empty() &&
        (w->type == DOMUI_WIDGET_STATIC_TEXT ||
         w->type == DOMUI_WIDGET_BUTTON ||
         w->type == DOMUI_WIDGET_CHECKBOX ||
         w->type == DOMUI_WIDGET_EDIT ||
         w->type == DOMUI_WIDGET_TAB_PAGE)) {
        ui_tlv_write_string(node_payload, DUI_TLV_TEXT_UTF8, text);
    }

    if (include_actions && ui_pick_action_key(w, action_key) && !action_key.empty()) {
        const std::string& key = action_key.str();
        action_id = ui_tool_editor_action_id_from_key(key.c_str(), (domui_u32)key.size());
    }
    if (action_id != 0u) {
        ui_tlv_write_u32_value(node_payload, DUI_TLV_ACTION_U32, (u32)action_id);
    }

    ui_tlv_write_u32_value(node_payload, DUI_TLV_FLAGS_U32, flags);

    rect.x = 0;
    rect.y = 0;
    rect.w = 0;
    rect.h = 0;
    {
        std::map<domui_widget_id, domui_layout_rect>::const_iterator it = layout.find(id);
        if (it != layout.end()) {
            rect = it->second;
        }
    }
    ui_tlv_write_rect(node_payload, DUI_TLV_RECT_I32, rect.x, rect.y, rect.w, rect.h);

    if (w->type == DOMUI_WIDGET_SPLITTER) {
        domui_string orient;
        int is_horizontal = 0;
        if (ui_prop_get_string(w->props, "splitter.orientation", orient)) {
            const char* s = orient.c_str();
            if (s && (s[0] == 'h' || s[0] == 'H')) {
                is_horizontal = 1;
            }
        }
        ui_tlv_write_u32_value(node_payload, DUI_TLV_SPLITTER_ORIENT_U32,
                               (u32)(is_horizontal ? DUI_SPLIT_HORIZONTAL : DUI_SPLIT_VERTICAL));
        ui_tlv_write_u32_value(node_payload, DUI_TLV_SPLITTER_POS_U32,
                               (u32)ui_prop_get_int_default(w->props, "splitter.pos", -1));
        ui_tlv_write_u32_value(node_payload, DUI_TLV_SPLITTER_THICK_U32,
                               (u32)ui_prop_get_int_default(w->props, "splitter.thickness", 4));
        ui_tlv_write_u32_value(node_payload, DUI_TLV_SPLITTER_MIN_A_U32,
                               (u32)ui_prop_get_int_default(w->props, "splitter.min_a", 0));
        ui_tlv_write_u32_value(node_payload, DUI_TLV_SPLITTER_MIN_B_U32,
                               (u32)ui_prop_get_int_default(w->props, "splitter.min_b", 0));
    } else if (w->type == DOMUI_WIDGET_TABS) {
        domui_string placement;
        int placement_id = DUI_TABS_TOP;
        if (ui_prop_get_string(w->props, "tabs.placement", placement)) {
            const char* s = placement.c_str();
            if (s) {
                if (s[0] == 'b' || s[0] == 'B') placement_id = DUI_TABS_BOTTOM;
                else if (s[0] == 'l' || s[0] == 'L') placement_id = DUI_TABS_LEFT;
                else if (s[0] == 'r' || s[0] == 'R') placement_id = DUI_TABS_RIGHT;
            }
        }
        ui_tlv_write_u32_value(node_payload, DUI_TLV_TABS_SELECTED_U32,
                               (u32)ui_prop_get_int_default(w->props, "tabs.selected_index", 0));
        ui_tlv_write_u32_value(node_payload, DUI_TLV_TABS_PLACEMENT_U32, (u32)placement_id);
    } else if (w->type == DOMUI_WIDGET_TAB_PAGE) {
        ui_tlv_write_u32_value(node_payload, DUI_TLV_TAB_ENABLED_U32,
                               (u32)ui_prop_get_int_default(w->props, "tab.enabled", 1));
    } else if (w->type == DOMUI_WIDGET_SCROLLPANEL) {
        ui_tlv_write_u32_value(node_payload, DUI_TLV_SCROLL_H_ENABLED_U32,
                               (u32)ui_prop_get_int_default(w->props, "scroll.h_enabled", 1));
        ui_tlv_write_u32_value(node_payload, DUI_TLV_SCROLL_V_ENABLED_U32,
                               (u32)ui_prop_get_int_default(w->props, "scroll.v_enabled", 1));
        ui_tlv_write_u32_value(node_payload, DUI_TLV_SCROLL_X_U32,
                               (u32)ui_prop_get_int_default(w->props, "scroll.x", 0));
        ui_tlv_write_u32_value(node_payload, DUI_TLV_SCROLL_Y_U32,
                               (u32)ui_prop_get_int_default(w->props, "scroll.y", 0));
    }

    doc.enumerate_children(id, children);
    for (size_t i = 0u; i < children.size(); ++i) {
        ui_build_dui_node(doc, children[i], layout, include_actions, children_payload);
    }
    if (!children_payload.empty()) {
        ui_tlv_write_tlv(node_payload, DUI_TLV_CHILDREN_V1,
                         &children_payload[0], children_payload.size());
    }

    ui_tlv_write_tlv(out_payload, DUI_TLV_NODE_V1,
                     node_payload.empty() ? 0 : &node_payload[0], node_payload.size());
}

static bool ui_build_dui_schema(const domui_doc& doc,
                                domui_widget_id root_id,
                                const std::map<domui_widget_id, domui_layout_rect>& layout,
                                bool include_actions,
                                std::vector<unsigned char>& out_bytes)
{
    std::vector<unsigned char> form_payload;
    std::vector<unsigned char> schema_payload;

    out_bytes.clear();
    if (root_id == 0u) {
        return false;
    }
    ui_build_dui_node(doc, root_id, layout, include_actions, form_payload);
    if (form_payload.empty()) {
        return false;
    }
    ui_tlv_write_tlv(schema_payload, DUI_TLV_FORM_V1,
                     &form_payload[0], form_payload.size());
    ui_tlv_write_tlv(out_bytes, DUI_TLV_SCHEMA_V1,
                     &schema_payload[0], schema_payload.size());
    return true;
}

struct OpenDoc {
    domui_doc doc;
    std::string path;
    int dirty;
    domui_widget_id selected_id;

    OpenDoc()
        : doc(),
          path(),
          dirty(0),
          selected_id(0u)
    {
    }
};

class ToolEditorApp {
public:
    ToolEditorApp();
    bool init(HINSTANCE inst);
    void shutdown();
    LRESULT handle_message(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam);
    void on_action(ToolEditorAction action, const ToolEditorEvent* e);

private:
    bool init_dui();
    bool load_ui_doc(const char* path);
    void resolve_ui_ids();
    void rebuild_ui_schema();
    void resolve_ui_handles();
    void move_preview_window();
    void refresh_preview();
    void update_tabs();
    void update_hierarchy_list();
    void update_inspector();
    void update_title();
    void log_clear();
    void log_line(const char* text);
    void log_diag(const domui_diag& diag);

    void new_doc_from_template();
    void open_doc_dialog();
    void save_doc(int save_as);
    void validate_doc();

    void add_widget(domui_widget_type type);
    void show_add_menu(int x, int y);
    void delete_widget();
    domui_u32 next_z_for_parent(domui_widget_id parent_id) const;
    domui_widget_id find_doc_root(const domui_doc& doc) const;
    static LRESULT CALLBACK HierarchySubclassProc(HWND hwnd,
                                                  UINT msg,
                                                  WPARAM wparam,
                                                  LPARAM lparam,
                                                  UINT_PTR id,
                                                  DWORD_PTR ref);

    OpenDoc* active_doc();
    const OpenDoc* active_doc() const;
    void set_active_doc(int index);

    HINSTANCE m_instance;
    HWND m_hwnd;
    HFONT m_font;

    const dui_api_v1* m_dui_api;
    dui_action_api_v1* m_dui_action_api;
    dui_native_api_v1* m_dui_native_api;
    dui_context* m_dui_ctx;
    dui_window* m_ui_win;
    dui_window* m_preview_win;
    HWND m_ui_hwnd;
    HWND m_preview_hwnd;

    domui_doc m_ui_doc;
    domui_widget_id m_ui_root_id;
    domui_widget_id m_ui_tabs_id;
    domui_widget_id m_ui_hierarchy_id;
    domui_widget_id m_ui_prop_name_id;
    domui_widget_id m_ui_prop_x_id;
    domui_widget_id m_ui_prop_y_id;
    domui_widget_id m_ui_prop_w_id;
    domui_widget_id m_ui_prop_h_id;
    domui_widget_id m_ui_log_id;
    domui_widget_id m_ui_preview_host_id;

    std::map<domui_widget_id, domui_layout_rect> m_ui_layout;
    std::vector<domui_layout_result> m_ui_layout_results;

    HWND m_hierarchy_hwnd;
    HWND m_prop_name_hwnd;
    HWND m_prop_x_hwnd;
    HWND m_prop_y_hwnd;
    HWND m_prop_w_hwnd;
    HWND m_prop_h_hwnd;
    HWND m_log_hwnd;
    HWND m_tabs_hwnd;

    std::vector<OpenDoc> m_docs;
    int m_active_doc;
    int m_ignore_events;
};

static ToolEditorApp* g_app = 0;

ToolEditorApp::ToolEditorApp()
    : m_instance(0),
      m_hwnd(0),
      m_font(0),
      m_dui_api(0),
      m_dui_action_api(0),
      m_dui_native_api(0),
      m_dui_ctx(0),
      m_ui_win(0),
      m_preview_win(0),
      m_ui_hwnd(0),
      m_preview_hwnd(0),
      m_ui_doc(),
      m_ui_root_id(0u),
      m_ui_tabs_id(0u),
      m_ui_hierarchy_id(0u),
      m_ui_prop_name_id(0u),
      m_ui_prop_x_id(0u),
      m_ui_prop_y_id(0u),
      m_ui_prop_w_id(0u),
      m_ui_prop_h_id(0u),
      m_ui_log_id(0u),
      m_ui_preview_host_id(0u),
      m_ui_layout(),
      m_ui_layout_results(),
      m_hierarchy_hwnd(0),
      m_prop_name_hwnd(0),
      m_prop_x_hwnd(0),
      m_prop_y_hwnd(0),
      m_prop_w_hwnd(0),
      m_prop_h_hwnd(0),
      m_log_hwnd(0),
      m_tabs_hwnd(0),
      m_docs(),
      m_active_doc(-1),
      m_ignore_events(0)
{
}

OpenDoc* ToolEditorApp::active_doc()
{
    if (m_active_doc < 0 || m_active_doc >= (int)m_docs.size()) {
        return 0;
    }
    return &m_docs[(size_t)m_active_doc];
}

const OpenDoc* ToolEditorApp::active_doc() const
{
    if (m_active_doc < 0 || m_active_doc >= (int)m_docs.size()) {
        return 0;
    }
    return &m_docs[(size_t)m_active_doc];
}

domui_widget_id ToolEditorApp::find_doc_root(const domui_doc& doc) const
{
    std::vector<domui_widget_id> roots;
    doc.enumerate_children(0u, roots);
    if (!roots.empty()) {
        return roots[0];
    }
    return 0u;
}

domui_u32 ToolEditorApp::next_z_for_parent(domui_widget_id parent_id) const
{
    const OpenDoc* doc = active_doc();
    domui_u32 z = 0u;
    if (!doc) {
        return 0u;
    }
    std::vector<domui_widget_id> children;
    doc->doc.enumerate_children(parent_id, children);
    for (size_t i = 0u; i < children.size(); ++i) {
        const domui_widget* w = doc->doc.find_by_id(children[i]);
        if (w && w->z_order >= z) {
            z = w->z_order + 1u;
        }
    }
    return z;
}

bool ToolEditorApp::init_dui()
{
    const void* api = dom_dui_win32_get_api(DUI_API_ABI_VERSION);
    if (!api) {
        return false;
    }
    m_dui_api = (const dui_api_v1*)api;
    if (m_dui_api->create_context(&m_dui_ctx) != DUI_OK) {
        return false;
    }
    if (m_dui_api->query_interface) {
        m_dui_api->query_interface(DUI_IID_ACTION_API_V1, (void**)&m_dui_action_api);
        m_dui_api->query_interface(DUI_IID_NATIVE_API_V1, (void**)&m_dui_native_api);
    }
    if (m_dui_action_api) {
        m_dui_action_api->set_action_dispatch(m_dui_ctx, ui_tool_editor_dispatch, this);
    }
    return true;
}

bool ToolEditorApp::load_ui_doc(const char* path)
{
    domui_diag diag;
    if (!domui_doc_load_tlv(&m_ui_doc, path, &diag)) {
        log_diag(diag);
        return false;
    }
    resolve_ui_ids();
    return true;
}

void ToolEditorApp::resolve_ui_ids()
{
    domui_widget* w = 0;
    w = m_ui_doc.find_by_name(domui_string("root"));
    m_ui_root_id = w ? w->id : find_doc_root(m_ui_doc);

    w = m_ui_doc.find_by_name(domui_string("doc_tabs"));
    m_ui_tabs_id = w ? w->id : 0u;
    w = m_ui_doc.find_by_name(domui_string("list_hierarchy"));
    m_ui_hierarchy_id = w ? w->id : 0u;
    w = m_ui_doc.find_by_name(domui_string("edit_name"));
    m_ui_prop_name_id = w ? w->id : 0u;
    w = m_ui_doc.find_by_name(domui_string("edit_x"));
    m_ui_prop_x_id = w ? w->id : 0u;
    w = m_ui_doc.find_by_name(domui_string("edit_y"));
    m_ui_prop_y_id = w ? w->id : 0u;
    w = m_ui_doc.find_by_name(domui_string("edit_w"));
    m_ui_prop_w_id = w ? w->id : 0u;
    w = m_ui_doc.find_by_name(domui_string("edit_h"));
    m_ui_prop_h_id = w ? w->id : 0u;
    w = m_ui_doc.find_by_name(domui_string("log_list"));
    m_ui_log_id = w ? w->id : 0u;
    w = m_ui_doc.find_by_name(domui_string("preview_host"));
    m_ui_preview_host_id = w ? w->id : 0u;
}

void ToolEditorApp::resolve_ui_handles()
{
    if (!m_ui_hwnd) {
        return;
    }
    m_hierarchy_hwnd = (m_ui_hierarchy_id != 0u) ? ui_find_child_by_id(m_ui_hwnd, (int)m_ui_hierarchy_id) : 0;
    m_prop_name_hwnd = (m_ui_prop_name_id != 0u) ? ui_find_child_by_id(m_ui_hwnd, (int)m_ui_prop_name_id) : 0;
    m_prop_x_hwnd = (m_ui_prop_x_id != 0u) ? ui_find_child_by_id(m_ui_hwnd, (int)m_ui_prop_x_id) : 0;
    m_prop_y_hwnd = (m_ui_prop_y_id != 0u) ? ui_find_child_by_id(m_ui_hwnd, (int)m_ui_prop_y_id) : 0;
    m_prop_w_hwnd = (m_ui_prop_w_id != 0u) ? ui_find_child_by_id(m_ui_hwnd, (int)m_ui_prop_w_id) : 0;
    m_prop_h_hwnd = (m_ui_prop_h_id != 0u) ? ui_find_child_by_id(m_ui_hwnd, (int)m_ui_prop_h_id) : 0;
    m_log_hwnd = (m_ui_log_id != 0u) ? ui_find_child_by_id(m_ui_hwnd, (int)m_ui_log_id) : 0;
    m_tabs_hwnd = (m_ui_tabs_id != 0u) ? ui_find_child_by_id(m_ui_hwnd, (int)m_ui_tabs_id) : 0;
    if (m_hierarchy_hwnd) {
        SetWindowSubclass(m_hierarchy_hwnd, ToolEditorApp::HierarchySubclassProc, 1, (DWORD_PTR)this);
    }
}

void ToolEditorApp::rebuild_ui_schema()
{
    RECT rc;
    std::vector<unsigned char> schema;
    domui_widget_id root_id;

    if (!m_ui_win || !m_ui_root_id) {
        return;
    }
    GetClientRect(m_hwnd, &rc);
    if (m_ui_hwnd) {
        MoveWindow(m_ui_hwnd, 0, 0, rc.right - rc.left, rc.bottom - rc.top, TRUE);
    }
    if (!ui_build_layout_map(m_ui_doc, rc.right - rc.left, rc.bottom - rc.top, m_ui_layout, m_ui_layout_results)) {
        return;
    }
    root_id = m_ui_root_id;
    if (!ui_build_dui_schema(m_ui_doc, root_id, m_ui_layout, true, schema)) {
        return;
    }
    m_dui_api->set_schema_tlv(m_ui_win, schema.empty() ? 0 : &schema[0], (u32)schema.size());
    resolve_ui_handles();
    update_hierarchy_list();
    update_inspector();
    move_preview_window();
    refresh_preview();
}

void ToolEditorApp::move_preview_window()
{
    std::map<domui_widget_id, domui_layout_rect>::const_iterator it;
    if (!m_preview_hwnd) {
        return;
    }
    it = m_ui_layout.find(m_ui_preview_host_id);
    if (it == m_ui_layout.end()) {
        ShowWindow(m_preview_hwnd, SW_HIDE);
        return;
    }
    {
        const domui_layout_rect& r = it->second;
        MoveWindow(m_preview_hwnd, r.x, r.y, r.w, r.h, TRUE);
        ShowWindow(m_preview_hwnd, SW_SHOW);
    }
}

void ToolEditorApp::refresh_preview()
{
    std::vector<unsigned char> schema;
    OpenDoc* doc = active_doc();
    std::map<domui_widget_id, domui_layout_rect> layout;
    std::vector<domui_layout_result> results;
    domui_widget_id root_id;
    domui_layout_rect preview_rect;
    std::map<domui_widget_id, domui_layout_rect>::const_iterator it;

    if (!m_preview_win || !doc) {
        return;
    }
    it = m_ui_layout.find(m_ui_preview_host_id);
    if (it == m_ui_layout.end()) {
        return;
    }
    preview_rect = it->second;
    if (preview_rect.w <= 0 || preview_rect.h <= 0) {
        return;
    }
    if (!ui_build_layout_map(doc->doc, preview_rect.w, preview_rect.h, layout, results)) {
        return;
    }
    root_id = find_doc_root(doc->doc);
    if (!ui_build_dui_schema(doc->doc, root_id, layout, false, schema)) {
        return;
    }
    m_dui_api->set_schema_tlv(m_preview_win, schema.empty() ? 0 : &schema[0], (u32)schema.size());
}

void ToolEditorApp::update_tabs()
{
    domui_widget* tabs = m_ui_doc.find_by_id(m_ui_tabs_id);
    std::vector<domui_widget_id> children;
    size_t doc_count = m_docs.size();
    size_t tab_index = 0u;
    if (!tabs) {
        return;
    }
    tabs->props.set("tabs.selected_index", domui_value_int(m_active_doc >= 0 ? m_active_doc : 0));
    m_ui_doc.enumerate_children(m_ui_tabs_id, children);
    for (size_t i = 0u; i < children.size(); ++i) {
        domui_widget* w = m_ui_doc.find_by_id(children[i]);
        if (!w || w->type != DOMUI_WIDGET_TAB_PAGE) {
            continue;
        }
        if (tab_index < doc_count) {
            const OpenDoc& d = m_docs[tab_index];
            std::string name = d.path.empty() ? "Untitled" : ui_path_basename(d.path);
            w->props.set("tab.title", domui_value_string(domui_string(name.c_str())));
            w->props.set("tab.enabled", domui_value_bool(1));
        } else {
            w->props.set("tab.title", domui_value_string(domui_string("")));
            w->props.set("tab.enabled", domui_value_bool(0));
        }
        tab_index += 1u;
    }
}

void ToolEditorApp::update_hierarchy_list()
{
    OpenDoc* doc = active_doc();
    if (!doc || !m_hierarchy_hwnd) {
        return;
    }
    m_ignore_events = 1;
    SendMessageA(m_hierarchy_hwnd, LB_RESETCONTENT, 0, 0);
    {
        std::vector<domui_widget_id> order;
        int select_index = -1;
        doc->doc.canonical_widget_order(order);
        for (size_t i = 0u; i < order.size(); ++i) {
            const domui_widget* w = doc->doc.find_by_id(order[i]);
            domui_widget_id cur = order[i];
            int depth = 0;
            while (cur != 0u) {
                const domui_widget* p = doc->doc.find_by_id(cur);
                if (!p) {
                    break;
                }
                cur = p->parent_id;
                if (cur != 0u) {
                    depth += 1;
                }
            }
            if (w) {
                std::string line;
                for (int d = 0; d < depth; ++d) {
                    line.append("  ");
                }
                line.append(w->name.str());
                line.append(" (");
                line.append(ui_widget_type_name(w->type));
                line.append(") [");
                {
                    char buf[32];
                    std::sprintf(buf, "%u", (unsigned int)w->id);
                    line.append(buf);
                }
                line.append("]");
                {
                    int idx = (int)SendMessageA(m_hierarchy_hwnd, LB_ADDSTRING, 0, (LPARAM)line.c_str());
                    SendMessageA(m_hierarchy_hwnd, LB_SETITEMDATA, (WPARAM)idx, (LPARAM)w->id);
                    if (doc->selected_id == w->id) {
                        select_index = idx;
                    }
                }
            }
        }
        if (select_index >= 0) {
            SendMessageA(m_hierarchy_hwnd, LB_SETCURSEL, (WPARAM)select_index, 0);
        } else if (!order.empty()) {
            SendMessageA(m_hierarchy_hwnd, LB_SETCURSEL, 0, 0);
            {
                LRESULT item_id = SendMessageA(m_hierarchy_hwnd, LB_GETITEMDATA, 0, 0);
                doc->selected_id = (domui_widget_id)item_id;
            }
        }
    }
    m_ignore_events = 0;
}

void ToolEditorApp::update_inspector()
{
    OpenDoc* doc = active_doc();
    domui_widget* w = 0;
    if (!doc) {
        return;
    }
    if (doc->selected_id != 0u) {
        w = doc->doc.find_by_id(doc->selected_id);
    }
    m_ignore_events = 1;
    if (!w) {
        if (m_prop_name_hwnd) SetWindowTextA(m_prop_name_hwnd, "");
        if (m_prop_x_hwnd) SetWindowTextA(m_prop_x_hwnd, "");
        if (m_prop_y_hwnd) SetWindowTextA(m_prop_y_hwnd, "");
        if (m_prop_w_hwnd) SetWindowTextA(m_prop_w_hwnd, "");
        if (m_prop_h_hwnd) SetWindowTextA(m_prop_h_hwnd, "");
        m_ignore_events = 0;
        return;
    }
    {
        char buf[64];
        if (m_prop_name_hwnd) {
            SetWindowTextA(m_prop_name_hwnd, w->name.c_str());
        }
        if (m_prop_x_hwnd) {
            std::sprintf(buf, "%d", w->x);
            SetWindowTextA(m_prop_x_hwnd, buf);
        }
        if (m_prop_y_hwnd) {
            std::sprintf(buf, "%d", w->y);
            SetWindowTextA(m_prop_y_hwnd, buf);
        }
        if (m_prop_w_hwnd) {
            std::sprintf(buf, "%d", w->w);
            SetWindowTextA(m_prop_w_hwnd, buf);
        }
        if (m_prop_h_hwnd) {
            std::sprintf(buf, "%d", w->h);
            SetWindowTextA(m_prop_h_hwnd, buf);
        }
    }
    m_ignore_events = 0;
}

void ToolEditorApp::update_title()
{
    std::string title = "Dominium Tool Editor";
    const OpenDoc* doc = active_doc();
    if (doc) {
        title.append(" - ");
        title.append(doc->path.empty() ? "Untitled" : ui_path_basename(doc->path));
        if (doc->dirty) {
            title.append(" *");
        }
    }
    SetWindowTextA(m_hwnd, title.c_str());
}

void ToolEditorApp::log_clear()
{
    if (m_log_hwnd) {
        SendMessageA(m_log_hwnd, LB_RESETCONTENT, 0, 0);
    }
}

void ToolEditorApp::log_line(const char* text)
{
    if (!m_log_hwnd || !text) {
        return;
    }
    SendMessageA(m_log_hwnd, LB_ADDSTRING, 0, (LPARAM)text);
}

void ToolEditorApp::log_diag(const domui_diag& diag)
{
    size_t i;
    for (i = 0u; i < diag.errors().size(); ++i) {
        std::string line = "error: ";
        line.append(diag.errors()[i].message.c_str());
        log_line(line.c_str());
    }
    for (i = 0u; i < diag.warnings().size(); ++i) {
        std::string line = "warn: ";
        line.append(diag.warnings()[i].message.c_str());
        log_line(line.c_str());
    }
}

void ToolEditorApp::new_doc_from_template()
{
    domui_diag diag;
    OpenDoc doc;
    if ((int)m_docs.size() >= kMaxDocs) {
        log_line("open: tab limit reached");
        return;
    }
    if (!domui_doc_load_tlv(&doc.doc, kToolEditorTemplateDoc, &diag)) {
        log_diag(diag);
        return;
    }
    doc.path.clear();
    doc.dirty = 0;
    doc.selected_id = find_doc_root(doc.doc);
    m_docs.push_back(doc);
    set_active_doc((int)m_docs.size() - 1);
    update_tabs();
    rebuild_ui_schema();
}

void ToolEditorApp::open_doc_dialog()
{
    char buf[MAX_PATH];
    OPENFILENAMEA ofn;
    memset(&ofn, 0, sizeof(ofn));
    memset(buf, 0, sizeof(buf));
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = m_hwnd;
    ofn.lpstrFile = buf;
    ofn.nMaxFile = (DWORD)sizeof(buf);
    ofn.lpstrFilter = "UI Docs (*.tlv)\0*.tlv\0All Files\0*.*\0";
    ofn.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST;
    if (!GetOpenFileNameA(&ofn)) {
        return;
    }
    {
        std::string path = buf;
        for (size_t i = 0u; i < m_docs.size(); ++i) {
            if (m_docs[i].path == path) {
                set_active_doc((int)i);
                return;
            }
        }
        if ((int)m_docs.size() >= kMaxDocs) {
            log_line("open: tab limit reached");
            return;
        }
        {
            domui_diag diag;
            OpenDoc doc;
            if (!domui_doc_load_tlv(&doc.doc, path.c_str(), &diag)) {
                log_diag(diag);
                return;
            }
            doc.path = path;
            doc.dirty = 0;
            doc.selected_id = find_doc_root(doc.doc);
            m_docs.push_back(doc);
            set_active_doc((int)m_docs.size() - 1);
            update_tabs();
            rebuild_ui_schema();
        }
    }
}

void ToolEditorApp::save_doc(int save_as)
{
    OpenDoc* doc = active_doc();
    domui_diag diag;
    if (!doc) {
        return;
    }
    if (save_as || doc->path.empty()) {
        char buf[MAX_PATH];
        OPENFILENAMEA ofn;
        memset(&ofn, 0, sizeof(ofn));
        memset(buf, 0, sizeof(buf));
        ofn.lStructSize = sizeof(ofn);
        ofn.hwndOwner = m_hwnd;
        ofn.lpstrFile = buf;
        ofn.nMaxFile = (DWORD)sizeof(buf);
        ofn.lpstrFilter = "UI Docs (*.tlv)\0*.tlv\0All Files\0*.*\0";
        ofn.Flags = OFN_OVERWRITEPROMPT | OFN_PATHMUSTEXIST;
        if (!GetSaveFileNameA(&ofn)) {
            return;
        }
        doc->path = buf;
    }
    if (!domui_doc_save_tlv(&doc->doc, doc->path.c_str(), &diag)) {
        log_diag(diag);
        return;
    }
    doc->dirty = 0;
    update_title();
}

void ToolEditorApp::validate_doc()
{
    OpenDoc* doc = active_doc();
    domui_diag diag;
    if (!doc) {
        return;
    }
    log_clear();
    (void)domui_validate_doc(&doc->doc, 0, &diag);
    log_diag(diag);
}

void ToolEditorApp::add_widget(domui_widget_type type)
{
    OpenDoc* doc = active_doc();
    domui_widget_id parent_id;
    domui_widget_id id;
    domui_widget* w;
    if (!doc) {
        return;
    }
    parent_id = doc->selected_id;
    if (parent_id != 0u && !doc->doc.find_by_id(parent_id)) {
        parent_id = 0u;
    }
    id = doc->doc.create_widget(type, parent_id);
    w = doc->doc.find_by_id(id);
    if (!w) {
        return;
    }
    w->z_order = next_z_for_parent(parent_id);
    {
        char name[64];
        std::sprintf(name, "%s_%u", ui_widget_type_name(type), (unsigned int)id);
        w->name.set(name);
    }
    switch (type) {
    case DOMUI_WIDGET_BUTTON:
        w->w = 90;
        w->h = 24;
        w->props.set("text", domui_value_string(domui_string("Button")));
        break;
    case DOMUI_WIDGET_STATIC_TEXT:
        w->w = 120;
        w->h = 20;
        w->props.set("text", domui_value_string(domui_string("Label")));
        break;
    case DOMUI_WIDGET_EDIT:
        w->w = 140;
        w->h = 22;
        break;
    case DOMUI_WIDGET_LISTBOX:
        w->w = 160;
        w->h = 120;
        break;
    case DOMUI_WIDGET_CHECKBOX:
        w->w = 120;
        w->h = 20;
        w->props.set("text", domui_value_string(domui_string("Checkbox")));
        break;
    case DOMUI_WIDGET_TABS:
        w->w = 260;
        w->h = 200;
        w->props.set("tabs.selected_index", domui_value_int(0));
        w->props.set("tabs.placement", domui_value_string(domui_string("top")));
        break;
    case DOMUI_WIDGET_TAB_PAGE:
        w->w = 240;
        w->h = 180;
        w->props.set("tab.title", domui_value_string(domui_string("Tab")));
        w->props.set("tab.enabled", domui_value_bool(1));
        break;
    case DOMUI_WIDGET_SPLITTER:
        w->w = 300;
        w->h = 200;
        w->props.set("splitter.orientation", domui_value_string(domui_string("v")));
        w->props.set("splitter.pos", domui_value_int(120));
        w->props.set("splitter.thickness", domui_value_int(4));
        w->props.set("splitter.min_a", domui_value_int(40));
        w->props.set("splitter.min_b", domui_value_int(40));
        break;
    case DOMUI_WIDGET_SCROLLPANEL:
        w->w = 260;
        w->h = 200;
        w->props.set("scroll.h_enabled", domui_value_bool(1));
        w->props.set("scroll.v_enabled", domui_value_bool(1));
        w->props.set("scroll.x", domui_value_int(0));
        w->props.set("scroll.y", domui_value_int(0));
        break;
    default:
        w->w = 200;
        w->h = 120;
        break;
    }
    doc->selected_id = id;
    doc->dirty = 1;
    update_title();
    update_hierarchy_list();
    update_inspector();
    refresh_preview();
}

void ToolEditorApp::show_add_menu(int x, int y)
{
    HMENU menu = CreatePopupMenu();
    int cmd = 0;
    if (!menu) {
        return;
    }
    AppendMenuA(menu, MF_STRING, TOOL_EDITOR_MENU_ADD_CONTAINER, "Container");
    AppendMenuA(menu, MF_STRING, TOOL_EDITOR_MENU_ADD_LABEL, "Label");
    AppendMenuA(menu, MF_STRING, TOOL_EDITOR_MENU_ADD_BUTTON, "Button");
    AppendMenuA(menu, MF_STRING, TOOL_EDITOR_MENU_ADD_EDIT, "Edit");
    AppendMenuA(menu, MF_STRING, TOOL_EDITOR_MENU_ADD_LISTBOX, "Listbox");
    AppendMenuA(menu, MF_STRING, TOOL_EDITOR_MENU_ADD_CHECKBOX, "Checkbox");
    AppendMenuA(menu, MF_STRING, TOOL_EDITOR_MENU_ADD_TABS, "Tabs");
    AppendMenuA(menu, MF_STRING, TOOL_EDITOR_MENU_ADD_TAB_PAGE, "Tab Page");
    AppendMenuA(menu, MF_STRING, TOOL_EDITOR_MENU_ADD_SPLITTER, "Splitter");
    AppendMenuA(menu, MF_STRING, TOOL_EDITOR_MENU_ADD_SCROLLPANEL, "Scroll Panel");

    if (x == -1 && y == -1) {
        POINT pt;
        if (GetCursorPos(&pt)) {
            x = pt.x;
            y = pt.y;
        }
    }
    SetForegroundWindow(m_hwnd);
    cmd = TrackPopupMenu(menu, TPM_RETURNCMD | TPM_RIGHTBUTTON, x, y, 0, m_hwnd, NULL);
    DestroyMenu(menu);
    switch (cmd) {
    case TOOL_EDITOR_MENU_ADD_CONTAINER: add_widget(DOMUI_WIDGET_CONTAINER); break;
    case TOOL_EDITOR_MENU_ADD_LABEL: add_widget(DOMUI_WIDGET_STATIC_TEXT); break;
    case TOOL_EDITOR_MENU_ADD_BUTTON: add_widget(DOMUI_WIDGET_BUTTON); break;
    case TOOL_EDITOR_MENU_ADD_EDIT: add_widget(DOMUI_WIDGET_EDIT); break;
    case TOOL_EDITOR_MENU_ADD_LISTBOX: add_widget(DOMUI_WIDGET_LISTBOX); break;
    case TOOL_EDITOR_MENU_ADD_CHECKBOX: add_widget(DOMUI_WIDGET_CHECKBOX); break;
    case TOOL_EDITOR_MENU_ADD_TABS: add_widget(DOMUI_WIDGET_TABS); break;
    case TOOL_EDITOR_MENU_ADD_TAB_PAGE: add_widget(DOMUI_WIDGET_TAB_PAGE); break;
    case TOOL_EDITOR_MENU_ADD_SPLITTER: add_widget(DOMUI_WIDGET_SPLITTER); break;
    case TOOL_EDITOR_MENU_ADD_SCROLLPANEL: add_widget(DOMUI_WIDGET_SCROLLPANEL); break;
    default:
        break;
    }
}

void ToolEditorApp::delete_widget()
{
    OpenDoc* doc = active_doc();
    domui_widget_id root_id;
    if (!doc || doc->selected_id == 0u) {
        return;
    }
    root_id = find_doc_root(doc->doc);
    if (doc->selected_id == root_id) {
        log_line("delete: cannot delete root");
        return;
    }
    if (!doc->doc.delete_widget(doc->selected_id)) {
        return;
    }
    doc->selected_id = root_id;
    doc->dirty = 1;
    update_title();
    update_hierarchy_list();
    update_inspector();
    refresh_preview();
}

void ToolEditorApp::set_active_doc(int index)
{
    if (index < 0 || index >= (int)m_docs.size()) {
        return;
    }
    m_active_doc = index;
    update_title();
    update_hierarchy_list();
    update_inspector();
    update_tabs();
    rebuild_ui_schema();
}

bool ToolEditorApp::init(HINSTANCE inst)
{
    WNDCLASSA wc;
    RECT rc;
    dui_window_desc_v1 desc;
    dui_window_desc_v1 preview_desc;

    m_instance = inst;

    memset(&wc, 0, sizeof(wc));
    wc.lpfnWndProc = ToolEditor_WndProc;
    wc.hInstance = inst;
    wc.lpszClassName = "DominiumToolEditor";
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    if (!RegisterClassA(&wc)) {
        return false;
    }

    m_hwnd = CreateWindowA(
        wc.lpszClassName,
        "Dominium Tool Editor",
        WS_OVERLAPPEDWINDOW | WS_CLIPCHILDREN | WS_CLIPSIBLINGS,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        1200,
        800,
        NULL,
        NULL,
        inst,
        this);
    if (!m_hwnd) {
        return false;
    }

    SetWindowLongPtr(m_hwnd, GWLP_USERDATA, (LONG_PTR)this);
    ShowWindow(m_hwnd, SW_SHOW);
    UpdateWindow(m_hwnd);

    if (!init_dui()) {
        return false;
    }

    if (!load_ui_doc(kToolEditorUiDoc)) {
        return false;
    }

    GetClientRect(m_hwnd, &rc);
    memset(&desc, 0, sizeof(desc));
    desc.abi_version = DUI_API_ABI_VERSION;
    desc.struct_size = (u32)sizeof(desc);
    desc.title = "Tool Editor UI";
    desc.width = rc.right - rc.left;
    desc.height = rc.bottom - rc.top;
    desc.flags = DUI_WINDOW_FLAG_CHILD;
    desc.parent_hwnd = (void*)m_hwnd;
    if (m_dui_api->create_window(m_dui_ctx, &desc, &m_ui_win) != DUI_OK) {
        return false;
    }
    if (m_dui_native_api) {
        m_ui_hwnd = (HWND)m_dui_native_api->get_native_window_handle(m_ui_win);
    }

    rebuild_ui_schema();

    memset(&preview_desc, 0, sizeof(preview_desc));
    preview_desc.abi_version = DUI_API_ABI_VERSION;
    preview_desc.struct_size = (u32)sizeof(preview_desc);
    preview_desc.title = "Tool Editor Preview";
    preview_desc.width = 640;
    preview_desc.height = 480;
    preview_desc.flags = DUI_WINDOW_FLAG_CHILD;
    preview_desc.parent_hwnd = (void*)m_ui_hwnd;
    if (m_dui_api->create_window(m_dui_ctx, &preview_desc, &m_preview_win) != DUI_OK) {
        return false;
    }
    if (m_dui_native_api) {
        m_preview_hwnd = (HWND)m_dui_native_api->get_native_window_handle(m_preview_win);
    }

    move_preview_window();

    new_doc_from_template();
    return true;
}

void ToolEditorApp::shutdown()
{
    if (m_dui_api) {
        if (m_preview_win) {
            m_dui_api->destroy_window(m_preview_win);
        }
        if (m_ui_win) {
            m_dui_api->destroy_window(m_ui_win);
        }
        if (m_dui_ctx) {
            m_dui_api->destroy_context(m_dui_ctx);
        }
    }
}

void ToolEditorApp::on_action(ToolEditorAction action, const ToolEditorEvent* e)
{
    if (m_ignore_events) {
        return;
    }
    switch (action) {
    case TOOL_EDITOR_ACTION_QUIT:
        PostMessageA(m_hwnd, WM_CLOSE, 0, 0);
        break;
    case TOOL_EDITOR_ACTION_NEW:
        new_doc_from_template();
        break;
    case TOOL_EDITOR_ACTION_OPEN:
        open_doc_dialog();
        break;
    case TOOL_EDITOR_ACTION_SAVE:
        save_doc(0);
        break;
    case TOOL_EDITOR_ACTION_SAVE_AS:
        save_doc(1);
        break;
    case TOOL_EDITOR_ACTION_VALIDATE:
        validate_doc();
        break;
    case TOOL_EDITOR_ACTION_TAB_CHANGE:
        if (e) {
            set_active_doc((int)e->value_u32);
        }
        break;
    case TOOL_EDITOR_ACTION_HIER_SELECT:
        if (e) {
            OpenDoc* doc = active_doc();
            domui_widget_id wid = (domui_widget_id)e->value_u32_b;
            if (doc && wid != 0u && doc->doc.find_by_id(wid)) {
                doc->selected_id = wid;
                update_inspector();
            }
        }
        break;
    case TOOL_EDITOR_ACTION_PROP_NAME:
        if (e && e->has_text) {
            OpenDoc* doc = active_doc();
            domui_widget* w = doc ? doc->doc.find_by_id(doc->selected_id) : 0;
            if (w) {
                std::string s(e->text, e->text_len);
                w->name.set(s.c_str());
                doc->dirty = 1;
                update_title();
                update_hierarchy_list();
                refresh_preview();
            }
        }
        break;
    case TOOL_EDITOR_ACTION_PROP_X:
    case TOOL_EDITOR_ACTION_PROP_Y:
    case TOOL_EDITOR_ACTION_PROP_W:
    case TOOL_EDITOR_ACTION_PROP_H:
        if (e && e->has_text) {
            OpenDoc* doc = active_doc();
            domui_widget* w = doc ? doc->doc.find_by_id(doc->selected_id) : 0;
            if (w) {
                std::string s(e->text, e->text_len);
                int v = 0;
                if (ui_parse_int(s, &v)) {
                    if (action == TOOL_EDITOR_ACTION_PROP_X) w->x = v;
                    else if (action == TOOL_EDITOR_ACTION_PROP_Y) w->y = v;
                    else if (action == TOOL_EDITOR_ACTION_PROP_W) w->w = v;
                    else if (action == TOOL_EDITOR_ACTION_PROP_H) w->h = v;
                    doc->dirty = 1;
                    update_title();
                    refresh_preview();
                } else {
                    log_line("invalid number");
                }
            }
        }
        break;
    case TOOL_EDITOR_ACTION_ADD_WIDGET:
        {
            POINT pt;
            if (GetCursorPos(&pt)) {
                show_add_menu(pt.x, pt.y);
            } else {
                show_add_menu(-1, -1);
            }
        }
        break;
    case TOOL_EDITOR_ACTION_DELETE_WIDGET:
        delete_widget();
        break;
    default:
        break;
    }
}

LRESULT ToolEditorApp::handle_message(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    if (msg == WM_SIZE) {
        rebuild_ui_schema();
        return 0;
    }
    if (msg == WM_CLOSE) {
        DestroyWindow(hwnd);
        return 0;
    }
    if (msg == WM_DESTROY) {
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProcA(hwnd, msg, wparam, lparam);
}

void tool_editor_handle_action(void* user_ctx, ToolEditorAction action, const ToolEditorEvent* e)
{
    ToolEditorApp* app = (ToolEditorApp*)user_ctx;
    if (!app) {
        return;
    }
    app->on_action(action, e);
}

LRESULT CALLBACK ToolEditorApp::HierarchySubclassProc(HWND hwnd,
                                                      UINT msg,
                                                      WPARAM wparam,
                                                      LPARAM lparam,
                                                      UINT_PTR id,
                                                      DWORD_PTR ref)
{
    ToolEditorApp* app = (ToolEditorApp*)ref;
    (void)id;
    if (!app) {
        return DefSubclassProc(hwnd, msg, wparam, lparam);
    }
    if (msg == WM_CONTEXTMENU) {
        int x = (int)(short)LOWORD(lparam);
        int y = (int)(short)HIWORD(lparam);
        app->show_add_menu(x, y);
        return 0;
    }
    return DefSubclassProc(hwnd, msg, wparam, lparam);
}

static LRESULT CALLBACK ToolEditor_WndProc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    ToolEditorApp* app = (ToolEditorApp*)GetWindowLongPtr(hwnd, GWLP_USERDATA);
    if (msg == WM_NCCREATE) {
        CREATESTRUCTA* cs = (CREATESTRUCTA*)lparam;
        if (cs && cs->lpCreateParams) {
            app = (ToolEditorApp*)cs->lpCreateParams;
            SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)app);
        }
    }
    if (app) {
        return app->handle_message(hwnd, msg, wparam, lparam);
    }
    return DefWindowProcA(hwnd, msg, wparam, lparam);
}

int APIENTRY WinMain(HINSTANCE inst, HINSTANCE prev, LPSTR cmd, int show_cmd)
{
    ToolEditorApp app;
    MSG msg;
    (void)prev;
    (void)cmd;
    (void)show_cmd;

    g_app = &app;
    if (!app.init(inst)) {
        return 1;
    }

    while (GetMessageA(&msg, NULL, 0, 0) > 0) {
        TranslateMessage(&msg);
        DispatchMessageA(&msg);
    }
    app.shutdown();
    return (int)msg.wParam;
}

#endif
