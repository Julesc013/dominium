/*
FILE: tools/ui_editor/ui_editor_main_win32.cpp
MODULE: Repository
LAYER / SUBSYSTEM: tools/ui_editor
RESPONSIBILITY: Windows-only entrypoint for the UI editor tool; does NOT provide cross-platform implementations.
ALLOWED DEPENDENCIES: Project-local headers; C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: Single-threaded tool entry; no internal synchronization unless noted.
ERROR MODEL: Process exit codes and console diagnostics; no exceptions.
DETERMINISM: N/A (tooling/UI layer).
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via UI editor modules and schema tooling; see `docs/ui_editor/README.md`.
*/
// UI Editor implementation scaffold.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <map>
#include <string>
#include <algorithm>
#include <cctype>

#include "domino/core/types.h"
#include "domino/version.h"

#include "ui_ir_doc.h"
#include "ui_ir_tlv.h"
#include "ui_ir_json.h"
#include "ui_ir_diag.h"
#include "ui_ir_fileio.h"
#include "ui_ir_legacy_import.h"
#include "ui_ops.h"
#include "ui_layout.h"
#include "ui_validate.h"
#include "ui_codegen.h"

struct domui_event;
typedef void (*domui_action_fn)(void* user_ctx, const domui_event* e);
#define DOMUI_EVENT_H_INCLUDED
#include "dui/dui_api_v1.h"
#include "dui/dui_schema_tlv.h"

#if !defined(_WIN32)

int main(int argc, char** argv)
{
    (void)argc;
    (void)argv;
    printf("dominium-ui-editor is Windows-only.\n");
    return 0;
}

#else

#define WIN32_LEAN_AND_MEAN
#ifndef _WIN32_IE
#define _WIN32_IE 0x0501
#endif
#include <windows.h>
#include <commctrl.h>
#include <commdlg.h>

extern "C" const void* dom_dui_win32_get_api(u32 requested_abi);

static const char* kMainClass = "DomUiEditorMain";
static const char* kOverlayClass = "DomUiEditorOverlay";
static const char* kSplitterClass = "DomUiEditorSplitter";
static const char* kOpenToolDialogClass = "DomUiEditorOpenToolDialog";

static const int kSplitterSize = 4;
static const int kMinPanelSize = 120;
static const int kMinPreviewSize = 200;
static const int kInspectorEditHeight = 22;
static const int kInfoPanelHeight = 64;
static const int kTreeSearchHeight = 22;
static const int kHandleSize = 6;
static const int kUndoLimit = 50;
static const COLORREF kOverlayClearColor = RGB(255, 0, 255);

enum {
    ID_TREE_SEARCH = 1000,
    ID_TREE = 1001,
    ID_PREVIEW_HOST = 1002,
    ID_INSPECTOR = 1003,
    ID_INSPECTOR_EDIT = 1004,
    ID_LOG = 1005,
    ID_PREVIEW_TIMER = 1200,
    ID_INFO_PANEL = 1006,
    ID_SPLIT_LEFT = 1101,
    ID_SPLIT_RIGHT = 1102,
    ID_SPLIT_BOTTOM = 1103
};

enum {
    ID_FILE_NEW = 40001,
    ID_FILE_OPEN,
    ID_FILE_SAVE,
    ID_FILE_SAVE_AS,
    ID_FILE_VALIDATE,
    ID_FILE_EXIT,
    ID_EDIT_UNDO,
    ID_EDIT_REDO,
    ID_EDIT_DELETE
};

enum {
    ID_FILE_REFRESH_INDEX = 40100,
    ID_FILE_OPEN_TOOL = 40101,
    ID_FILE_IMPORT_LEGACY = 40102,
    ID_FILE_EXPORT_TOOL = 40103
};

enum {
    ID_ADD_WIDGET_BASE = 42000,
    ID_CONTEXT_DELETE = 42100
};

enum {
    ID_OPEN_TOOL_LIST = 5001,
    ID_OPEN_TOOL_CANON = 5002,
    ID_OPEN_TOOL_LEGACY = 5003,
    ID_OPEN_TOOL_OPEN = 5004,
    ID_OPEN_TOOL_CANCEL = 5005
};

enum InspectorRowType {
    ROW_CATEGORY = 0,
    ROW_FIELD,
    ROW_PROP,
    ROW_EVENT
};

enum InspectorField {
    FIELD_NONE = 0,
    FIELD_ID,
    FIELD_NAME,
    FIELD_TYPE,
    FIELD_X,
    FIELD_Y,
    FIELD_W,
    FIELD_H,
    FIELD_LAYOUT_MODE,
    FIELD_DOCK,
    FIELD_ANCHORS,
    FIELD_MARGIN_LEFT,
    FIELD_MARGIN_RIGHT,
    FIELD_MARGIN_TOP,
    FIELD_MARGIN_BOTTOM,
    FIELD_PADDING_LEFT,
    FIELD_PADDING_RIGHT,
    FIELD_PADDING_TOP,
    FIELD_PADDING_BOTTOM,
    FIELD_MIN_W,
    FIELD_MIN_H,
    FIELD_MAX_W,
    FIELD_MAX_H
};

enum DragMode {
    DRAG_NONE = 0,
    DRAG_MOVE,
    DRAG_N,
    DRAG_S,
    DRAG_E,
    DRAG_W,
    DRAG_NE,
    DRAG_NW,
    DRAG_SE,
    DRAG_SW
};

enum DocOrigin {
    DOC_ORIGIN_CANONICAL = 0,
    DOC_ORIGIN_IMPORTED,
    DOC_ORIGIN_LEGACY
};

class UiEditorApp;

struct InspectorRow {
    InspectorRowType type;
    InspectorField field;
    std::string key;
    domui_value_type prop_type;
    domui_widget_id widget_id;
    int editable;

    InspectorRow()
        : type(ROW_CATEGORY),
          field(FIELD_NONE),
          key(),
          prop_type(DOMUI_VALUE_INT),
          widget_id(0u),
          editable(0)
    {
    }
};

struct EditorCommand {
    domui_doc before;
    domui_doc after;
    std::string label;
};

struct UiDiscoveryEntry {
    int is_canonical;
    std::string abs_path;
    std::string rel_path;
    std::string tool;
    domui_u32 format_version;
    u64 last_write;

    UiDiscoveryEntry()
        : is_canonical(0),
          abs_path(),
          rel_path(),
          tool(),
          format_version(0u),
          last_write(0u)
    {
    }
};

struct UiOpenToolDialogState {
    UiEditorApp* app;
    HWND hwnd;
    HWND list;
    HWND check_canonical;
    HWND check_legacy;
    HWND btn_open;
    HWND btn_cancel;
    int result;
    int selected_index;
    std::vector<UiDiscoveryEntry> entries;

    UiOpenToolDialogState()
        : app(0),
          hwnd(0),
          list(0),
          check_canonical(0),
          check_legacy(0),
          btn_open(0),
          btn_cancel(0),
          result(0),
          selected_index(-1),
          entries()
    {
    }
};

static RECT ui_make_rect(int l, int t, int r, int b)
{
    RECT rc;
    rc.left = l;
    rc.top = t;
    rc.right = r;
    rc.bottom = b;
    return rc;
}

static int ui_listview_insert_item(HWND list, const char* text, LPARAM lparam)
{
    LVITEMA item;
    memset(&item, 0, sizeof(item));
    item.mask = LVIF_TEXT | LVIF_PARAM;
    item.iItem = ListView_GetItemCount(list);
    item.pszText = (LPSTR)text;
    item.lParam = lparam;
    return (int)SendMessageA(list, LVM_INSERTITEMA, 0, (LPARAM)&item);
}

static void ui_listview_set_item_text(HWND list, int row, int col, const char* text)
{
    LVITEMA item;
    memset(&item, 0, sizeof(item));
    item.iSubItem = col;
    item.pszText = (LPSTR)text;
    (void)SendMessageA(list, LVM_SETITEMTEXTA, (WPARAM)row, (LPARAM)&item);
}

static std::string ui_to_lower(const std::string& in)
{
    std::string out = in;
    for (size_t i = 0u; i < out.size(); ++i) {
        out[i] = (char)std::tolower((unsigned char)out[i]);
    }
    return out;
}

static std::string ui_int_to_string(int v)
{
    char buf[32];
    sprintf(buf, "%d", v);
    return std::string(buf);
}

static std::string ui_u32_to_string(domui_u32 v)
{
    char buf[32];
    sprintf(buf, "%u", (unsigned int)v);
    return std::string(buf);
}

static std::string ui_bool_to_string(int v)
{
    return v ? "true" : "false";
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

static int ui_parse_u32(const std::string& s, domui_u32* out)
{
    char* end = 0;
    unsigned long v = std::strtoul(s.c_str(), &end, 10);
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
        *out = (domui_u32)v;
    }
    return 1;
}

static int ui_parse_bool(const std::string& s, int* out)
{
    std::string v = ui_to_lower(s);
    if (v == "1" || v == "true" || v == "yes" || v == "on") {
        if (out) *out = 1;
        return 1;
    }
    if (v == "0" || v == "false" || v == "no" || v == "off") {
        if (out) *out = 0;
        return 1;
    }
    return 0;
}

static int ui_parse_int_list(const std::string& s, int* out_vals, int max_vals)
{
    const char* p = s.c_str();
    int count = 0;
    while (*p && count < max_vals) {
        while (*p && (std::isspace((unsigned char)*p) || *p == ',')) {
            p++;
        }
        if (!*p) {
            break;
        }
        {
            char* end = 0;
            long v = std::strtol(p, &end, 10);
            if (end == p) {
                break;
            }
            if (out_vals) {
                out_vals[count] = (int)v;
            }
            count += 1;
            p = end;
        }
    }
    return count;
}

static int ui_parse_vec2i(const std::string& s, domui_vec2i* out)
{
    int vals[2];
    if (ui_parse_int_list(s, vals, 2) != 2) {
        return 0;
    }
    if (out) {
        out->x = vals[0];
        out->y = vals[1];
    }
    return 1;
}

static int ui_parse_recti(const std::string& s, domui_recti* out)
{
    int vals[4];
    if (ui_parse_int_list(s, vals, 4) != 4) {
        return 0;
    }
    if (out) {
        out->x = vals[0];
        out->y = vals[1];
        out->w = vals[2];
        out->h = vals[3];
    }
    return 1;
}

static domui_u32 ui_parse_anchor_mask(const std::string& s, int* out_ok)
{
    domui_u32 mask = 0u;
    domui_u32 numeric = 0u;
    if (ui_parse_u32(s, &numeric)) {
        if (out_ok) *out_ok = 1;
        return numeric;
    }
    for (size_t i = 0u; i < s.size(); ++i) {
        char c = (char)std::tolower((unsigned char)s[i]);
        if (c == 'l') mask |= DOMUI_ANCHOR_L;
        else if (c == 'r') mask |= DOMUI_ANCHOR_R;
        else if (c == 't') mask |= DOMUI_ANCHOR_T;
        else if (c == 'b') mask |= DOMUI_ANCHOR_B;
    }
    if (out_ok) {
        *out_ok = (mask != 0u) ? 1 : 0;
    }
    return mask;
}

static std::string ui_anchor_mask_to_string(domui_u32 mask)
{
    std::string out;
    if (mask == 0u) {
        return "0";
    }
    if (mask & DOMUI_ANCHOR_L) out.push_back('L');
    if (mask & DOMUI_ANCHOR_R) out.push_back('R');
    if (mask & DOMUI_ANCHOR_T) out.push_back('T');
    if (mask & DOMUI_ANCHOR_B) out.push_back('B');
    return out;
}

static const char* ui_dock_mode_name(domui_dock_mode dock)
{
    switch (dock) {
    case DOMUI_DOCK_LEFT: return "left";
    case DOMUI_DOCK_RIGHT: return "right";
    case DOMUI_DOCK_TOP: return "top";
    case DOMUI_DOCK_BOTTOM: return "bottom";
    case DOMUI_DOCK_FILL: return "fill";
    default:
        break;
    }
    return "none";
}

static domui_dock_mode ui_parse_dock_mode(const std::string& s, int* out_ok)
{
    domui_u32 numeric = 0u;
    if (ui_parse_u32(s, &numeric)) {
        if (out_ok) *out_ok = 1;
        return (domui_dock_mode)numeric;
    }
    {
        std::string v = ui_to_lower(s);
        if (v == "left") { if (out_ok) *out_ok = 1; return DOMUI_DOCK_LEFT; }
        if (v == "right") { if (out_ok) *out_ok = 1; return DOMUI_DOCK_RIGHT; }
        if (v == "top") { if (out_ok) *out_ok = 1; return DOMUI_DOCK_TOP; }
        if (v == "bottom") { if (out_ok) *out_ok = 1; return DOMUI_DOCK_BOTTOM; }
        if (v == "fill") { if (out_ok) *out_ok = 1; return DOMUI_DOCK_FILL; }
        if (v == "none") { if (out_ok) *out_ok = 1; return DOMUI_DOCK_NONE; }
    }
    if (out_ok) *out_ok = 0;
    return DOMUI_DOCK_NONE;
}

static const char* ui_layout_mode_name(domui_container_layout_mode mode)
{
    switch (mode) {
    case DOMUI_LAYOUT_STACK_ROW: return "stack_row";
    case DOMUI_LAYOUT_STACK_COL: return "stack_col";
    case DOMUI_LAYOUT_GRID: return "grid";
    default:
        break;
    }
    return "absolute";
}

static const char* ui_doc_origin_name(DocOrigin origin)
{
    switch (origin) {
    case DOC_ORIGIN_CANONICAL: return "canonical";
    case DOC_ORIGIN_IMPORTED: return "imported";
    case DOC_ORIGIN_LEGACY: return "legacy";
    default:
        break;
    }
    return "canonical";
}

static domui_container_layout_mode ui_parse_layout_mode(const std::string& s, int* out_ok)
{
    domui_u32 numeric = 0u;
    if (ui_parse_u32(s, &numeric)) {
        if (out_ok) *out_ok = 1;
        return (domui_container_layout_mode)numeric;
    }
    {
        std::string v = ui_to_lower(s);
        if (v == "stack_row") { if (out_ok) *out_ok = 1; return DOMUI_LAYOUT_STACK_ROW; }
        if (v == "stack_col") { if (out_ok) *out_ok = 1; return DOMUI_LAYOUT_STACK_COL; }
        if (v == "grid") { if (out_ok) *out_ok = 1; return DOMUI_LAYOUT_GRID; }
        if (v == "absolute") { if (out_ok) *out_ok = 1; return DOMUI_LAYOUT_ABSOLUTE; }
    }
    if (out_ok) *out_ok = 0;
    return DOMUI_LAYOUT_ABSOLUTE;
}

static const char* ui_widget_type_name(domui_widget_type t)
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

static domui_widget_type ui_widget_type_from_menu(int id)
{
    int v = id - ID_ADD_WIDGET_BASE;
    if (v < 0) {
        return DOMUI_WIDGET_CONTAINER;
    }
    return (domui_widget_type)v;
}

static std::string ui_path_dir(const std::string& path)
{
    size_t pos = path.find_last_of("/\\");
    if (pos == std::string::npos) {
        return "";
    }
    return path.substr(0u, pos);
}

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

static std::string ui_path_filename(const std::string& path)
{
    size_t pos = path.find_last_of("/\\");
    if (pos == std::string::npos) {
        return path;
    }
    return path.substr(pos + 1u);
}

static std::string ui_replace_extension(const std::string& path, const char* ext)
{
    size_t slash = path.find_last_of("/\\");
    size_t dot = path.find_last_of('.');
    if (dot == std::string::npos || (slash != std::string::npos && dot < slash)) {
        return path + (ext ? ext : "");
    }
    if (!ext) {
        return path.substr(0u, dot);
    }
    return path.substr(0u, dot) + ext;
}

static std::string ui_join_path(const std::string& a, const std::string& b)
{
    if (a.empty()) {
        return b;
    }
    if (b.empty()) {
        return a;
    }
    if (a[a.size() - 1u] == '\\' || a[a.size() - 1u] == '/') {
        return a + b;
    }
    return a + "\\" + b;
}

static std::string ui_normalize_slashes(const std::string& path)
{
    std::string out = path;
    for (size_t i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') {
            out[i] = '/';
        }
    }
    return out;
}

static int ui_path_basename_equals(const std::string& path, const char* name)
{
    std::string base = ui_to_lower(ui_path_basename(path));
    std::string target = ui_to_lower(name ? name : "");
    return base == target;
}

static int ui_path_is_dir(const std::string& path)
{
    DWORD attrs = GetFileAttributesA(path.c_str());
    if (attrs == INVALID_FILE_ATTRIBUTES) {
        return 0;
    }
    return (attrs & FILE_ATTRIBUTE_DIRECTORY) ? 1 : 0;
}

static int ui_path_is_file(const std::string& path)
{
    DWORD attrs = GetFileAttributesA(path.c_str());
    if (attrs == INVALID_FILE_ATTRIBUTES) {
        return 0;
    }
    return (attrs & FILE_ATTRIBUTE_DIRECTORY) ? 0 : 1;
}

static int ui_ensure_dir(const std::string& path)
{
    if (path.empty()) {
        return 0;
    }
    if (CreateDirectoryA(path.c_str(), NULL)) {
        return 1;
    }
    DWORD err = GetLastError();
    return (err == ERROR_ALREADY_EXISTS) ? 1 : 0;
}

static int ui_ensure_dir_recursive(const std::string& path)
{
    std::vector<std::string> stack;
    std::string cur = path;
    while (!cur.empty() && !ui_path_is_dir(cur)) {
        stack.push_back(cur);
        std::string parent = ui_path_dir(cur);
        if (parent.empty() || parent == cur) {
            break;
        }
        cur = parent;
    }
    for (size_t i = stack.size(); i > 0u; --i) {
        if (!ui_ensure_dir(stack[i - 1u])) {
            return 0;
        }
    }
    return 1;
}

static void ui_resolve_doc_paths(const std::string& tlv_path,
                                 std::string* out_doc_root,
                                 std::string* out_doc_dir,
                                 std::string* out_tlv_path)
{
    std::string dir = ui_path_dir(tlv_path);
    std::string file = ui_path_filename(tlv_path);
    std::string doc_dir = dir;
    std::string doc_root = dir;
    if (!dir.empty()) {
        if (ui_path_basename_equals(dir, "doc")) {
            doc_root = ui_path_dir(dir);
        } else {
            doc_dir = ui_join_path(dir, "doc");
        }
    }
    std::string final_tlv = tlv_path;
    if (!dir.empty() && !ui_path_basename_equals(dir, "doc")) {
        if (!file.empty()) {
            final_tlv = ui_join_path(doc_dir, file);
        }
    }
    if (out_doc_root) {
        *out_doc_root = doc_root;
    }
    if (out_doc_dir) {
        *out_doc_dir = doc_dir;
    }
    if (out_tlv_path) {
        *out_tlv_path = final_tlv;
    }
}

static std::string ui_make_relative_path(const std::string& root, const std::string& abs_path)
{
    std::string root_norm = ui_normalize_slashes(root);
    std::string abs_norm = ui_normalize_slashes(abs_path);
    std::string root_lower = ui_to_lower(root_norm);
    std::string abs_lower = ui_to_lower(abs_norm);
    if (!root_lower.empty() && root_lower[root_lower.size() - 1u] != '/') {
        root_lower += "/";
        root_norm += "/";
    }
    if (!root_lower.empty() && abs_lower.find(root_lower) == 0u) {
        return abs_norm.substr(root_norm.size());
    }
    return abs_norm;
}

static int ui_path_is_canonical_doc(const std::string& rel_path)
{
    std::string p = ui_to_lower(ui_normalize_slashes(rel_path));
    return (p.find("/ui/doc/") != std::string::npos) ? 1 : 0;
}

static int ui_is_legacy_name(const std::string& filename)
{
    std::string name = ui_to_lower(filename);
    if (name.size() < 4u) {
        return 0;
    }
    if (name == "launcher_ui_v1.tlv") {
        return 1;
    }
    if (name.rfind(".tlv") != name.size() - 4u) {
        return 0;
    }
    if (name.find("_ui_v") != std::string::npos) {
        return 1;
    }
    return 0;
}

static std::string ui_guess_tool_from_path(const std::string& rel_path)
{
    std::string p = ui_to_lower(ui_normalize_slashes(rel_path));
    size_t pos = p.find("tools/");
    if (pos != std::string::npos) {
        size_t start = pos + 6u;
        size_t end = p.find('/', start);
        if (end != std::string::npos && end > start) {
            return p.substr(start, end - start);
        }
    }
    if (p.find("/launcher/") != std::string::npos) {
        return "launcher";
    }
    return "unknown";
}

static std::string ui_get_cwd()
{
    char buf[MAX_PATH];
    DWORD len = GetCurrentDirectoryA((DWORD)sizeof(buf), buf);
    if (len == 0u || len >= sizeof(buf)) {
        return "";
    }
    return std::string(buf);
}

static int ui_is_repo_root(const std::string& path)
{
    if (path.empty()) {
        return 0;
    }
    if (!ui_path_is_file(ui_join_path(path, "CMakeLists.txt"))) {
        return 0;
    }
    if (!ui_path_is_dir(ui_join_path(path, "tools"))) {
        return 0;
    }
    if (!ui_path_is_dir(ui_join_path(path, "source"))) {
        return 0;
    }
    return 1;
}

static std::string ui_find_repo_root(const std::string& start)
{
    std::string cur = start.empty() ? ui_get_cwd() : start;
    while (!cur.empty()) {
        if (ui_is_repo_root(cur)) {
            return cur;
        }
        std::string parent = ui_path_dir(cur);
        if (parent.empty() || parent == cur) {
            break;
        }
        cur = parent;
    }
    return "";
}

static std::string ui_sanitize_key(const std::string& s)
{
    std::string out;
    out.reserve(s.size());
    for (size_t i = 0u; i < s.size(); ++i) {
        unsigned char c = (unsigned char)s[i];
        if (std::isalnum(c) || c == '_' || c == '.') {
            out.push_back((char)c);
        } else {
            out.push_back('_');
        }
    }
    if (out.empty()) {
        out = "action";
    }
    return out;
}

static std::string ui_trim(const std::string& s)
{
    size_t start = 0u;
    size_t end = s.size();
    while (start < end && std::isspace((unsigned char)s[start])) {
        start++;
    }
    while (end > start && std::isspace((unsigned char)s[end - 1u])) {
        end--;
    }
    return s.substr(start, end - start);
}

static void ui_split_csv(const std::string& s, std::vector<std::string>& out)
{
    out.clear();
    size_t pos = 0u;
    while (pos <= s.size()) {
        size_t comma = s.find(',', pos);
        if (comma == std::string::npos) {
            comma = s.size();
        }
        {
            std::string token = ui_trim(s.substr(pos, comma - pos));
            if (!token.empty()) {
                out.push_back(token);
            }
        }
        if (comma >= s.size()) {
            break;
        }
        pos = comma + 1u;
    }
}

static int ui_is_absolute_path(const std::string& path)
{
    if (path.size() >= 2u) {
        unsigned char c = (unsigned char)path[0];
        if (std::isalpha(c) && path[1] == ':') {
            return 1;
        }
        if ((path[0] == '\\' && path[1] == '\\') || (path[0] == '/' && path[1] == '/')) {
            return 1;
        }
    }
    if (!path.empty() && (path[0] == '\\' || path[0] == '/')) {
        return 1;
    }
    return 0;
}

static std::string ui_report_path(const std::string& path,
                                  const std::string& repo_root,
                                  const std::string& cwd)
{
    if (path.empty()) {
        return "";
    }
    std::string normalized = ui_normalize_slashes(path);
    if (!ui_is_absolute_path(normalized)) {
        return normalized;
    }
    if (!repo_root.empty()) {
        std::string rel = ui_make_relative_path(repo_root, normalized);
        if (!ui_is_absolute_path(rel)) {
            return rel;
        }
    }
    if (!cwd.empty()) {
        std::string rel = ui_make_relative_path(cwd, normalized);
        if (!ui_is_absolute_path(rel)) {
            return rel;
        }
    }
    return ui_path_filename(normalized);
}

static std::string ui_sanitize_doc_name(const std::string& in)
{
    std::string out;
    out.reserve(in.size() + 8u);
    for (size_t i = 0u; i < in.size(); ++i) {
        unsigned char c = (unsigned char)in[i];
        if (std::isalnum(c)) {
            out.push_back((char)std::tolower(c));
        } else {
            out.push_back('_');
        }
    }
    if (out.empty()) {
        out = "doc";
    }
    if (out[0] >= '0' && out[0] <= '9') {
        out.insert(0u, "ui_");
    }
    return out;
}

static std::string ui_doc_symbol_from_name(const std::string& name)
{
    return "ui_" + ui_sanitize_doc_name(name);
}

struct UiDocOutputPaths {
    std::string doc_root;
    std::string doc_dir;
    std::string tlv_path;
    std::string json_path;
    std::string gen_dir;
    std::string user_dir;
    std::string reg_dir;
    std::string reg_path;

    UiDocOutputPaths()
        : doc_root(),
          doc_dir(),
          tlv_path(),
          json_path(),
          gen_dir(),
          user_dir(),
          reg_dir(),
          reg_path()
    {
    }
};

static void ui_compute_doc_paths(const std::string& path,
                                 int normalize_to_doc,
                                 UiDocOutputPaths& out_paths)
{
    out_paths = UiDocOutputPaths();
    if (normalize_to_doc) {
        ui_resolve_doc_paths(path, &out_paths.doc_root, &out_paths.doc_dir, &out_paths.tlv_path);
    } else {
        out_paths.doc_root = ui_path_dir(path);
        out_paths.doc_dir = ui_path_dir(path);
        out_paths.tlv_path = path;
    }
    out_paths.json_path = ui_replace_extension(out_paths.tlv_path, ".json");
    out_paths.gen_dir = ui_join_path(out_paths.doc_root, "gen");
    out_paths.user_dir = ui_join_path(out_paths.doc_root, "user");
    out_paths.reg_dir = ui_join_path(out_paths.doc_root, "registry");
    out_paths.reg_path = ui_join_path(out_paths.reg_dir, "ui_actions_registry.json");
}

static void ui_auto_fill_action_keys(domui_doc& doc)
{
    std::vector<domui_widget_id> order;
    std::string doc_name = doc.meta.doc_name.str();
    if (doc_name.empty()) {
        doc_name = "doc";
    }
    doc_name = ui_sanitize_key(doc_name);
    doc.canonical_widget_order(order);
    for (size_t i = 0u; i < order.size(); ++i) {
        domui_widget* w = doc.find_by_id(order[i]);
        if (!w) {
            continue;
        }
        const domui_events::list_type& entries = w->events.entries();
        for (size_t e = 0u; e < entries.size(); ++e) {
            if (!entries[e].action_key.empty()) {
                continue;
            }
            std::string base = w->name.str();
            if (base.empty()) {
                base = ui_u32_to_string(w->id);
            }
            base = ui_sanitize_key(base);
            std::string ev = ui_sanitize_key(entries[e].event_name.str());
            std::string key = doc_name + "." + base + "." + ev;
            w->events.set(entries[e].event_name, domui_string(key.c_str()));
        }
    }
}

static int ui_save_doc_tlv_json(domui_doc* doc,
                                const UiDocOutputPaths& paths,
                                const char* doc_name_override,
                                int auto_fill_actions,
                                int write_json,
                                domui_diag* out_save_diag,
                                domui_diag* out_json_diag,
                                int* out_json_ok)
{
    if (out_json_ok) {
        *out_json_ok = 1;
    }
    if (!doc || paths.tlv_path.empty()) {
        if (out_save_diag) {
            out_save_diag->add_error("save: invalid doc or path", 0u, "");
        }
        return 0;
    }
    if (doc_name_override && doc_name_override[0]) {
        doc->meta.doc_name.set(doc_name_override);
    }
    if (doc->meta.doc_name.empty()) {
        std::string base = ui_path_basename(paths.tlv_path);
        doc->meta.doc_name.set(base.c_str());
    }
    if (auto_fill_actions) {
        ui_auto_fill_action_keys(*doc);
    }
    if (!domui_doc_save_tlv(doc, paths.tlv_path.c_str(), out_save_diag)) {
        return 0;
    }
    if (write_json) {
        if (!domui_doc_save_json_mirror(doc, paths.json_path.c_str(), out_json_diag)) {
            if (out_json_ok) {
                *out_json_ok = 0;
            }
        }
    }
    return 1;
}

static bool ui_run_codegen_with_paths(const char* tlv_path,
                                      const char* registry_path,
                                      const char* out_gen_dir,
                                      const char* out_user_dir,
                                      const char* doc_name_override,
                                      domui_diag* out_diag)
{
#if defined(DOMUI_ENABLE_CODEGEN) && (DOMUI_ENABLE_CODEGEN == 0)
    if (out_diag) {
        out_diag->add_warning("codegen disabled (DOMUI_ENABLE_CODEGEN=OFF)", 0u, "codegen");
    }
    return true;
#endif
    domui_codegen_params params;
    domui_diag local;
    domui_diag* diag = out_diag ? out_diag : &local;
    params.input_tlv_path = tlv_path;
    params.registry_path = registry_path;
    params.out_gen_dir = out_gen_dir;
    params.out_user_dir = out_user_dir;
    params.doc_name_override = doc_name_override;
    if (!domui_codegen_run(&params, diag)) {
        return false;
    }
    return true;
}

static const char* ui_discovery_type_name(const UiDiscoveryEntry& entry)
{
    return entry.is_canonical ? "canonical" : "legacy";
}

static bool ui_discovery_entry_less(const UiDiscoveryEntry& a, const UiDiscoveryEntry& b)
{
    std::string al = ui_to_lower(a.rel_path);
    std::string bl = ui_to_lower(b.rel_path);
    if (al != bl) {
        return al < bl;
    }
    if (a.is_canonical != b.is_canonical) {
        return a.is_canonical > b.is_canonical;
    }
    return ui_to_lower(a.tool) < ui_to_lower(b.tool);
}

static std::string ui_json_escape(const std::string& in)
{
    std::string out;
    out.reserve(in.size() + 8u);
    for (size_t i = 0u; i < in.size(); ++i) {
        unsigned char c = (unsigned char)in[i];
        switch (c) {
        case '\\': out += "\\\\"; break;
        case '"': out += "\\\""; break;
        case '\b': out += "\\b"; break;
        case '\f': out += "\\f"; break;
        case '\n': out += "\\n"; break;
        case '\r': out += "\\r"; break;
        case '\t': out += "\\t"; break;
        default:
            if (c < 0x20u) {
                char buf[8];
                sprintf(buf, "\\u%04x", (unsigned int)c);
                out += buf;
            } else {
                out.push_back((char)c);
            }
            break;
        }
    }
    return out;
}

static std::string ui_pretty_path(const std::string& repo_root, const std::string& abs_path)
{
    if (!repo_root.empty()) {
        return ui_make_relative_path(repo_root, abs_path);
    }
    return ui_path_filename(abs_path);
}

static std::string ui_format_diag_item(const domui_diag_item& item)
{
    std::string text = item.message.str();
    if (item.widget_id != 0u) {
        text += " [widget ";
        text += ui_u32_to_string(item.widget_id);
        text += "]";
    }
    if (!item.context.empty()) {
        text += " [";
        text += item.context.str();
        text += "]";
    }
    return text;
}

static void ui_collect_import_id_map(const domui_doc& doc,
                                     const domui_diag& diag,
                                     std::map<domui_u32, domui_u32>& out_map)
{
    out_map.clear();
    const std::vector<domui_diag_item>& warns = diag.warnings();
    for (size_t i = 0u; i < warns.size(); ++i) {
        const domui_diag_item& item = warns[i];
        if (item.widget_id == 0u) {
            continue;
        }
        if (item.message.str().find("legacy id remapped") == std::string::npos) {
            continue;
        }
        std::string name = "legacy.";
        name += ui_u32_to_string(item.widget_id);
        domui_string key(name.c_str());
        const domui_widget* w = doc.find_by_name(key);
        if (w && w->id != item.widget_id) {
            out_map[item.widget_id] = w->id;
        }
    }
}

static size_t ui_count_action_keys(const domui_doc& doc)
{
    std::map<std::string, int> keys;
    std::vector<domui_widget_id> order;
    doc.canonical_widget_order(order);
    for (size_t i = 0u; i < order.size(); ++i) {
        const domui_widget* w = doc.find_by_id(order[i]);
        if (!w) {
            continue;
        }
        const domui_events::list_type& entries = w->events.entries();
        for (size_t j = 0u; j < entries.size(); ++j) {
            const std::string& key = entries[j].action_key.str();
            if (!key.empty()) {
                keys[key] = 1;
            }
        }
    }
    return keys.size();
}

static std::string ui_build_import_report_json(const std::string& source,
                                               const std::string& destination,
                                               const domui_diag& diag,
                                               const std::map<domui_u32, domui_u32>& id_map)
{
    std::string json;
    const std::vector<domui_diag_item>& warns = diag.warnings();
    const std::vector<domui_diag_item>& errs = diag.errors();

    json += "{\n";
    json += "  \"source\": \"";
    json += ui_json_escape(source);
    json += "\",\n";
    json += "  \"destination\": \"";
    json += ui_json_escape(destination);
    json += "\",\n";
    json += "  \"warnings\": [\n";
    for (size_t i = 0u; i < warns.size(); ++i) {
        std::string text = ui_format_diag_item(warns[i]);
        json += "    \"";
        json += ui_json_escape(text);
        json += "\"";
        if (i + 1u < warns.size()) {
            json += ",";
        }
        json += "\n";
    }
    json += "  ],\n";
    json += "  \"errors\": [\n";
    for (size_t i = 0u; i < errs.size(); ++i) {
        std::string text = ui_format_diag_item(errs[i]);
        json += "    \"";
        json += ui_json_escape(text);
        json += "\"";
        if (i + 1u < errs.size()) {
            json += ",";
        }
        json += "\n";
    }
    json += "  ],\n";
    json += "  \"id_map\": {";
    if (!id_map.empty()) {
        json += "\n";
        std::map<domui_u32, domui_u32>::const_iterator it = id_map.begin();
        while (it != id_map.end()) {
            json += "    \"";
            json += ui_u32_to_string(it->first);
            json += "\": ";
            json += ui_u32_to_string(it->second);
            ++it;
            if (it != id_map.end()) {
                json += ",";
            }
            json += "\n";
        }
        json += "  ";
    }
    json += "}\n";
    json += "}\n";
    return json;
}

static void ui_scan_dir_recursive(const std::string& repo_root,
                                  const std::string& abs_dir,
                                  std::vector<UiDiscoveryEntry>& out_entries,
                                  domui_diag* diag)
{
    WIN32_FIND_DATAA data;
    HANDLE handle = INVALID_HANDLE_VALUE;
    std::string pattern = ui_join_path(abs_dir, "*");

    handle = FindFirstFileA(pattern.c_str(), &data);
    if (handle == INVALID_HANDLE_VALUE) {
        return;
    }
    do {
        const char* name = data.cFileName;
        if (!name || !name[0]) {
            continue;
        }
        if (strcmp(name, ".") == 0 || strcmp(name, "..") == 0) {
            continue;
        }
        std::string abs_path = ui_join_path(abs_dir, name);
        if (data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
            ui_scan_dir_recursive(repo_root, abs_path, out_entries, diag);
        } else {
            std::string filename = ui_path_filename(abs_path);
            std::string lower = ui_to_lower(filename);
            if (lower.find(".bak") != std::string::npos) {
                continue;
            }
            if (lower.size() < 4u || lower.rfind(".tlv") != lower.size() - 4u) {
                continue;
            }
            std::string rel_path = ui_make_relative_path(repo_root, abs_path);
            int is_canonical = ui_path_is_canonical_doc(rel_path);
            int is_legacy = ui_is_legacy_name(filename);
            if (!is_canonical && !is_legacy) {
                continue;
            }
            UiDiscoveryEntry entry;
            ULARGE_INTEGER stamp;
            stamp.LowPart = data.ftLastWriteTime.dwLowDateTime;
            stamp.HighPart = data.ftLastWriteTime.dwHighDateTime;
            entry.last_write = (u64)stamp.QuadPart;
            entry.is_canonical = is_canonical ? 1 : 0;
            entry.abs_path = abs_path;
            entry.rel_path = ui_normalize_slashes(rel_path);
            entry.tool = ui_guess_tool_from_path(entry.rel_path);
            entry.format_version = 0u;
            if (entry.is_canonical) {
                domui_doc doc;
                domui_diag local;
                if (domui_doc_load_tlv(&doc, entry.abs_path.c_str(), &local)) {
                    entry.format_version = doc.meta.doc_version;
                } else if (diag) {
                    diag->add_warning("ui scan: failed to read canonical doc", 0u, entry.abs_path.c_str());
                }
            }
            out_entries.push_back(entry);
        }
    } while (FindNextFileA(handle, &data) != 0);
    FindClose(handle);
}

static bool ui_scan_repo_ui(const std::string& repo_root,
                            std::vector<UiDiscoveryEntry>& out_entries,
                            domui_diag* diag)
{
    out_entries.clear();
    if (repo_root.empty()) {
        if (diag) {
            diag->add_error("ui scan: repo root not found", 0u, "");
        }
        return false;
    }
    ui_scan_dir_recursive(repo_root, repo_root, out_entries, diag);
    std::sort(out_entries.begin(), out_entries.end(), ui_discovery_entry_less);
    return true;
}

static std::string ui_default_index_path(const std::string& repo_root)
{
    std::string tools_dir = ui_join_path(repo_root, "tools");
    std::string index_dir = ui_join_path(tools_dir, "ui_index");
    return ui_join_path(index_dir, "ui_index.json");
}

static bool ui_write_ui_index_json(const std::string& out_path,
                                   const std::vector<UiDiscoveryEntry>& entries,
                                   domui_diag* diag)
{
    std::string json;
    std::string dir = ui_path_dir(out_path);
    if (!dir.empty()) {
        ui_ensure_dir_recursive(dir);
    }
    json += "{\n";
    json += "  \"version\": 1,\n";
    json += "  \"generated_by\": \"dominium-ui-editor\",\n";
    json += "  \"entries\": [\n";
    for (size_t i = 0u; i < entries.size(); ++i) {
        const UiDiscoveryEntry& entry = entries[i];
        json += "    {\n";
        json += "      \"ui_type\": \"";
        json += ui_discovery_type_name(entry);
        json += "\",\n";
        json += "      \"path\": \"";
        json += ui_json_escape(entry.rel_path);
        json += "\",\n";
        json += "      \"tool\": \"";
        json += ui_json_escape(entry.tool);
        json += "\",\n";
        json += "      \"format_version\": ";
        json += ui_u32_to_string(entry.format_version);
        json += "\n";
        json += "    }";
        if (i + 1u < entries.size()) {
            json += ",";
        }
        json += "\n";
    }
    json += "  ]\n";
    json += "}\n";
    return domui_atomic_write_file(out_path.c_str(),
                                   json.c_str(),
                                   json.size(),
                                   diag);
}

static void ui_split_args(const char* cmd, std::vector<std::string>& out_args)
{
    out_args.clear();
    if (!cmd) {
        return;
    }
    const char* p = cmd;
    while (*p) {
        while (*p && std::isspace((unsigned char)*p)) {
            ++p;
        }
        if (!*p) {
            break;
        }
        if (*p == '"') {
            const char* start = ++p;
            while (*p && *p != '"') {
                ++p;
            }
            out_args.push_back(std::string(start, p - start));
            if (*p == '"') {
                ++p;
            }
        } else {
            const char* start = p;
            while (*p && !std::isspace((unsigned char)*p)) {
                ++p;
            }
            out_args.push_back(std::string(start, p - start));
        }
    }
}

static int ui_has_arg(const std::vector<std::string>& args, const char* flag)
{
    if (!flag) {
        return 0;
    }
    for (size_t i = 0u; i < args.size(); ++i) {
        if (args[i] == flag) {
            return 1;
        }
    }
    return 0;
}

static int ui_has_arg_prefix(const std::vector<std::string>& args, const char* prefix)
{
    if (!prefix) {
        return 0;
    }
    size_t len = strlen(prefix);
    for (size_t i = 0u; i < args.size(); ++i) {
        if (args[i].compare(0u, len, prefix) == 0) {
            return 1;
        }
    }
    return 0;
}

static int ui_get_arg_value(const std::vector<std::string>& args, const char* key, std::string& out_value)
{
    if (!key) {
        return 0;
    }
    for (size_t i = 0u; i + 1u < args.size(); ++i) {
        if (args[i] == key) {
            out_value = args[i + 1u];
            return 1;
        }
    }
    return 0;
}

static int ui_run_scan_cli(const std::vector<std::string>& args)
{
    domui_diag diag;
    std::vector<UiDiscoveryEntry> entries;
    std::string repo_root = ui_find_repo_root("");
    std::string out_path;
    if (repo_root.empty()) {
        fprintf(stderr, "ui scan: repo root not found\n");
        return 1;
    }
    if (!ui_scan_repo_ui(repo_root, entries, &diag)) {
        fprintf(stderr, "ui scan: failed\n");
        return 1;
    }
    if (!ui_get_arg_value(args, "--out", out_path)) {
        out_path = ui_default_index_path(repo_root);
    }
    if (!ui_write_ui_index_json(out_path, entries, &diag)) {
        fprintf(stderr, "ui scan: failed to write index\n");
        return 1;
    }
    return 0;
}

static void ui_print_diag_to_stderr(const domui_diag& diag)
{
    size_t i;
    for (i = 0u; i < diag.error_count(); ++i) {
        std::string text = ui_format_diag_item(diag.errors()[i]);
        fprintf(stderr, "error: %s\n", text.c_str());
    }
    for (i = 0u; i < diag.warning_count(); ++i) {
        std::string text = ui_format_diag_item(diag.warnings()[i]);
        fprintf(stderr, "warning: %s\n", text.c_str());
    }
}

static void ui_sort_unique_strings(std::vector<std::string>& items)
{
    std::sort(items.begin(), items.end());
    items.erase(std::unique(items.begin(), items.end()), items.end());
}

static int ui_collect_targets(const std::vector<std::string>& args,
                              domui_target_set& out_targets,
                              std::vector<std::string>& out_tokens)
{
    std::string csv;
    out_targets.backends.clear();
    out_targets.tiers.clear();
    out_tokens.clear();
    if (!ui_get_arg_value(args, "--targets", csv)) {
        return 0;
    }
    std::vector<std::string> tokens;
    ui_split_csv(csv, tokens);
    ui_sort_unique_strings(tokens);
    if (tokens.empty()) {
        return 0;
    }
    domui_register_default_backend_caps();
    for (size_t i = 0u; i < tokens.size(); ++i) {
        const char* token = tokens[i].c_str();
        if (domui_get_backend_caps_cstr(token)) {
            out_targets.backends.push_back(domui_string(token));
        } else {
            out_targets.tiers.push_back(domui_string(token));
        }
    }
    out_tokens = tokens;
    return 1;
}

static std::string ui_strip_tlv_extension(const std::string& name)
{
    std::string lower = ui_to_lower(name);
    if (lower.size() >= 4u && lower.rfind(".tlv") == lower.size() - 4u) {
        return name.substr(0u, name.size() - 4u);
    }
    return name;
}

static void ui_sort_strings(std::vector<std::string>& items)
{
    std::sort(items.begin(), items.end());
}

static void ui_append_diag_strings(const domui_diag& diag,
                                   std::vector<std::string>& errors,
                                   std::vector<std::string>& warnings)
{
    size_t i;
    for (i = 0u; i < diag.error_count(); ++i) {
        errors.push_back(ui_format_diag_item(diag.errors()[i]));
    }
    for (i = 0u; i < diag.warning_count(); ++i) {
        warnings.push_back(ui_format_diag_item(diag.warnings()[i]));
    }
}

static void ui_append_diag_items(domui_diag* dst, const domui_diag& src)
{
    size_t i;
    if (!dst) {
        return;
    }
    for (i = 0u; i < src.error_count(); ++i) {
        const domui_diag_item& item = src.errors()[i];
        dst->add_error(item.message, item.widget_id, item.context);
    }
    for (i = 0u; i < src.warning_count(); ++i) {
        const domui_diag_item& item = src.warnings()[i];
        dst->add_warning(item.message, item.widget_id, item.context);
    }
}

static void ui_collect_targets_for_report(const domui_doc* doc,
                                          const std::vector<std::string>& cli_targets,
                                          std::vector<std::string>& out_targets)
{
    out_targets.clear();
    if (!cli_targets.empty()) {
        out_targets = cli_targets;
        ui_sort_unique_strings(out_targets);
        return;
    }
    if (doc) {
        size_t i;
        for (i = 0u; i < doc->meta.target_backends.size(); ++i) {
            out_targets.push_back(doc->meta.target_backends[i].str());
        }
        for (i = 0u; i < doc->meta.target_tiers.size(); ++i) {
            out_targets.push_back(doc->meta.target_tiers[i].str());
        }
    }
    if (out_targets.empty()) {
        out_targets.push_back("win32");
    }
    ui_sort_unique_strings(out_targets);
}

static void ui_append_json_string_array(std::string& json,
                                        const char* key,
                                        const std::vector<std::string>& items)
{
    json += "  \"";
    json += key ? key : "";
    json += "\": [\n";
    for (size_t i = 0u; i < items.size(); ++i) {
        json += "    \"";
        json += ui_json_escape(items[i]);
        json += "\"";
        if (i + 1u < items.size()) {
            json += ",";
        }
        json += "\n";
    }
    json += "  ]";
}

static void ui_append_json_u32_map(std::string& json,
                                   const char* key,
                                   const std::map<std::string, domui_u32>& items)
{
    std::map<std::string, domui_u32>::const_iterator it;
    json += "  \"";
    json += key ? key : "";
    json += "\": {";
    if (!items.empty()) {
        json += "\n";
        for (it = items.begin(); it != items.end(); ++it) {
            std::map<std::string, domui_u32>::const_iterator next = it;
            ++next;
            json += "    \"";
            json += ui_json_escape(it->first);
            json += "\": ";
            json += ui_u32_to_string(it->second);
            if (next != items.end()) {
                json += ",";
            }
            json += "\n";
        }
        json += "  ";
    }
    json += "}";
}

static std::string ui_build_cli_report_json(const char* command,
                                            const std::string& input,
                                            const std::vector<std::string>& output_files,
                                            const std::vector<std::string>& errors,
                                            const std::vector<std::string>& warnings,
                                            const std::map<std::string, domui_u32>* created_ids,
                                            int exit_code,
                                            const char* status,
                                            const std::vector<std::string>* targets)
{
    std::string json;
    std::map<std::string, domui_u32> empty_ids;
    const std::map<std::string, domui_u32>& ids = created_ids ? *created_ids : empty_ids;
    json += "{\n";
    json += "  \"command\": \"";
    json += ui_json_escape(command ? command : "");
    json += "\",\n";
    json += "  \"input\": \"";
    json += ui_json_escape(input);
    json += "\",\n";
    ui_append_json_string_array(json, "output_files", output_files);
    json += ",\n";
    ui_append_json_string_array(json, "errors", errors);
    json += ",\n";
    ui_append_json_string_array(json, "warnings", warnings);
    json += ",\n";
    ui_append_json_u32_map(json, "created_ids", ids);
    json += ",\n";
    json += "  \"exit_code\": ";
    json += ui_int_to_string(exit_code);
    if (status) {
        json += ",\n  \"status\": \"";
        json += ui_json_escape(status);
        json += "\"";
    }
    if (targets) {
        json += ",\n";
        ui_append_json_string_array(json, "targets", *targets);
    }
    json += "\n";
    json += "}\n";
    return json;
}

static int ui_write_cli_report(const std::string& report_path,
                               const char* command,
                               const std::string& input_path,
                               const std::vector<std::string>& output_files,
                               const std::vector<std::string>& errors,
                               const std::vector<std::string>& warnings,
                               const std::map<std::string, domui_u32>* created_ids,
                               int exit_code,
                               const char* status,
                               const std::vector<std::string>* targets,
                               const std::string& repo_root,
                               const std::string& cwd)
{
    std::vector<std::string> report_outputs;
    std::vector<std::string> report_errors = errors;
    std::vector<std::string> report_warnings = warnings;
    std::vector<std::string> report_targets;
    std::string report_input = ui_report_path(input_path, repo_root, cwd);
    for (size_t i = 0u; i < output_files.size(); ++i) {
        std::string entry = ui_report_path(output_files[i], repo_root, cwd);
        if (!entry.empty()) {
            report_outputs.push_back(entry);
        }
    }
    ui_sort_unique_strings(report_outputs);
    ui_sort_strings(report_errors);
    ui_sort_strings(report_warnings);
    if (targets) {
        report_targets = *targets;
        ui_sort_unique_strings(report_targets);
    }
    std::string json = ui_build_cli_report_json(command,
                                                report_input,
                                                report_outputs,
                                                report_errors,
                                                report_warnings,
                                                created_ids,
                                                exit_code,
                                                status,
                                                targets ? &report_targets : 0);
    {
        std::string dir = ui_path_dir(report_path);
        if (!dir.empty()) {
            ui_ensure_dir_recursive(dir);
        }
    }
    domui_diag diag;
    if (!domui_atomic_write_file(report_path.c_str(),
                                 json.c_str(),
                                 json.size(),
                                 &diag)) {
        ui_print_diag_to_stderr(diag);
        return 0;
    }
    return 1;
}

static void ui_print_help()
{
    printf("dominium-ui-editor %s\n", DOMINO_VERSION_STRING);
    printf("Commands:\n");
    printf("  --help\n");
    printf("    Show this help text.\n");
    printf("  --scan-ui [--out <path>]\n");
    printf("    Scan repo for UI docs and write ui_index.json.\n");
    printf("  --headless-validate <ui_doc.tlv> [--targets <list>] [--report <path.json>]\n");
    printf("    Validate UI doc without GUI.\n");
    printf("  --headless-format <ui_doc.tlv> [--out <ui_doc_out.tlv>] [--report <path.json>]\n");
    printf("    Canonicalize UI doc and write JSON mirror.\n");
    printf("  --headless-codegen --in <ui_doc.tlv> --out <gen_dir> --registry <registry.json> --docname <name>\n");
    printf("    [--report <path.json>]\n");
    printf("    Run action codegen and update registry.\n");
    printf("  --headless-build-ui --in <ui_doc.tlv> --docname <name> --out-root <tool/ui/>\n");
    printf("    [--report <path.json>]\n");
    printf("    Validate, format, and codegen into tool UI root.\n");
    printf("  --headless-apply <ui_doc.tlv> --script <ops.json>\n");
    printf("    [--out <ui_doc_out.tlv>] [--report <path.json>] [--in-new]\n");
    printf("    Apply ops.json deterministically without GUI.\n");
}

static int ui_run_headless_validate(const std::vector<std::string>& args)
{
    std::string input_path;
    std::string report_path;
    std::string repo_root = ui_find_repo_root("");
    std::string cwd = ui_get_cwd();
    domui_doc doc;
    domui_diag load_diag;
    domui_diag vdiag;
    domui_target_set targets;
    std::vector<std::string> target_tokens;
    std::vector<std::string> report_targets;
    std::vector<std::string> errors;
    std::vector<std::string> warnings;
    std::vector<std::string> output_files;
    domui_target_set* target_ptr = 0;
    int exit_code = 0;
    const char* status = "ok";
    int doc_loaded = 0;
    (void)ui_get_arg_value(args, "--report", report_path);
    if (!ui_get_arg_value(args, "--headless-validate", input_path) || input_path.empty()) {
        errors.push_back("headless-validate: missing input path");
        fprintf(stderr, "headless-validate: missing input path\n");
        exit_code = 1;
    } else {
        if (ui_collect_targets(args, targets, target_tokens)) {
            target_ptr = &targets;
        }
        if (!domui_doc_load_tlv(&doc, input_path.c_str(), &load_diag)) {
            ui_append_diag_strings(load_diag, errors, warnings);
            ui_print_diag_to_stderr(load_diag);
            exit_code = 1;
        } else {
            doc_loaded = 1;
            ui_append_diag_strings(load_diag, errors, warnings);
            if (!domui_validate_doc(&doc, target_ptr, &vdiag)) {
                ui_append_diag_strings(vdiag, errors, warnings);
                ui_print_diag_to_stderr(vdiag);
                exit_code = 2;
            } else {
                ui_append_diag_strings(vdiag, errors, warnings);
            }
        }
    }
    if (exit_code != 0) {
        status = "error";
    }
    ui_collect_targets_for_report(doc_loaded ? &doc : 0, target_tokens, report_targets);
    if (!report_path.empty()) {
        if (!ui_write_cli_report(report_path,
                                 "headless-validate",
                                 input_path,
                                 output_files,
                                 errors,
                                 warnings,
                                 0,
                                 exit_code,
                                 status,
                                 &report_targets,
                                 repo_root,
                                 cwd)) {
            if (exit_code == 0) {
                exit_code = 1;
                status = "error";
            }
        }
    }
    return exit_code;
}

static int ui_run_headless_format(const std::vector<std::string>& args)
{
    std::string input_path;
    std::string out_path;
    std::string report_path;
    std::string repo_root = ui_find_repo_root("");
    std::string cwd = ui_get_cwd();
    domui_doc doc;
    domui_diag load_diag;
    domui_diag vdiag;
    domui_diag save_diag;
    domui_diag json_diag;
    UiDocOutputPaths paths;
    std::vector<std::string> errors;
    std::vector<std::string> warnings;
    std::vector<std::string> output_files;
    int json_ok = 1;
    int exit_code = 0;
    const char* status = "ok";
    int tlv_ok = 0;
    (void)ui_get_arg_value(args, "--report", report_path);
    if (!ui_get_arg_value(args, "--headless-format", input_path) || input_path.empty()) {
        errors.push_back("headless-format: missing input path");
        fprintf(stderr, "headless-format: missing input path\n");
        exit_code = 1;
    } else {
        if (!ui_get_arg_value(args, "--out", out_path)) {
            out_path = input_path;
        }
        if (out_path.empty()) {
            errors.push_back("headless-format: missing output path");
            fprintf(stderr, "headless-format: missing output path\n");
            exit_code = 1;
        } else if (!domui_doc_load_tlv(&doc, input_path.c_str(), &load_diag)) {
            ui_append_diag_strings(load_diag, errors, warnings);
            ui_print_diag_to_stderr(load_diag);
            exit_code = 1;
        } else {
            ui_append_diag_strings(load_diag, errors, warnings);
            if (!domui_validate_doc(&doc, 0, &vdiag)) {
                ui_append_diag_strings(vdiag, errors, warnings);
                ui_print_diag_to_stderr(vdiag);
                exit_code = 2;
            } else {
                ui_append_diag_strings(vdiag, errors, warnings);
            }
            if (exit_code == 0) {
                ui_compute_doc_paths(out_path, 0, paths);
                {
                    std::string out_dir = ui_path_dir(paths.tlv_path);
                    if (!out_dir.empty()) {
                        ui_ensure_dir_recursive(out_dir);
                    }
                }
                tlv_ok = ui_save_doc_tlv_json(&doc,
                                              paths,
                                              NULL,
                                              1,
                                              1,
                                              &save_diag,
                                              &json_diag,
                                              &json_ok);
                ui_append_diag_strings(save_diag, errors, warnings);
                ui_append_diag_strings(json_diag, errors, warnings);
                if (!tlv_ok) {
                    ui_print_diag_to_stderr(save_diag);
                    exit_code = 1;
                } else {
                    output_files.push_back(paths.tlv_path);
                    if (!json_ok) {
                        ui_print_diag_to_stderr(json_diag);
                        exit_code = 1;
                    } else {
                        output_files.push_back(paths.json_path);
                    }
                }
            }
        }
    }
    if (exit_code != 0) {
        status = "error";
    }
    if (!report_path.empty()) {
        if (!ui_write_cli_report(report_path,
                                 "headless-format",
                                 input_path,
                                 output_files,
                                 errors,
                                 warnings,
                                 0,
                                 exit_code,
                                 status,
                                 0,
                                 repo_root,
                                 cwd)) {
            if (exit_code == 0) {
                exit_code = 1;
                status = "error";
            }
        }
    }
    return exit_code;
}

static int ui_run_headless_codegen(const std::vector<std::string>& args)
{
    std::string input_path;
    std::string out_gen_dir;
    std::string registry_path;
    std::string doc_name;
    std::string report_path;
    std::string repo_root = ui_find_repo_root("");
    std::string cwd = ui_get_cwd();
    std::string doc_base;
    domui_doc doc;
    domui_diag load_diag;
    domui_diag vdiag;
    domui_diag cdiag;
    std::vector<std::string> errors;
    std::vector<std::string> warnings;
    std::vector<std::string> output_files;
    std::string out_user_dir;
    int exit_code = 0;
    const char* status = "ok";
    int codegen_ok = 0;
    (void)ui_get_arg_value(args, "--report", report_path);
    if (!ui_get_arg_value(args, "--in", input_path) || input_path.empty()) {
        errors.push_back("headless-codegen: missing --in");
        fprintf(stderr, "headless-codegen: missing --in\n");
        exit_code = 1;
    } else if (!ui_get_arg_value(args, "--out", out_gen_dir) || out_gen_dir.empty()) {
        errors.push_back("headless-codegen: missing --out");
        fprintf(stderr, "headless-codegen: missing --out\n");
        exit_code = 1;
    } else if (!ui_get_arg_value(args, "--registry", registry_path) || registry_path.empty()) {
        errors.push_back("headless-codegen: missing --registry");
        fprintf(stderr, "headless-codegen: missing --registry\n");
        exit_code = 1;
    } else if (!ui_get_arg_value(args, "--docname", doc_name) || doc_name.empty()) {
        errors.push_back("headless-codegen: missing --docname");
        fprintf(stderr, "headless-codegen: missing --docname\n");
        exit_code = 1;
    } else {
        doc_base = ui_strip_tlv_extension(doc_name);
        if (doc_base.empty()) {
            errors.push_back("headless-codegen: invalid --docname");
            fprintf(stderr, "headless-codegen: invalid --docname\n");
            exit_code = 1;
        } else if (!domui_doc_load_tlv(&doc, input_path.c_str(), &load_diag)) {
            ui_append_diag_strings(load_diag, errors, warnings);
            ui_print_diag_to_stderr(load_diag);
            exit_code = 1;
        } else {
            ui_append_diag_strings(load_diag, errors, warnings);
            if (!domui_validate_doc(&doc, 0, &vdiag)) {
                ui_append_diag_strings(vdiag, errors, warnings);
                ui_print_diag_to_stderr(vdiag);
                exit_code = 2;
            } else {
                ui_append_diag_strings(vdiag, errors, warnings);
            }
        }
        if (exit_code == 0) {
            std::string out_parent = ui_path_dir(out_gen_dir);
            out_user_dir = out_parent.empty() ? std::string("user") : ui_join_path(out_parent, "user");
            {
                std::string reg_dir = ui_path_dir(registry_path);
                if (!out_gen_dir.empty()) {
                    ui_ensure_dir_recursive(out_gen_dir);
                }
                if (!out_user_dir.empty()) {
                    ui_ensure_dir_recursive(out_user_dir);
                }
                if (!reg_dir.empty()) {
                    ui_ensure_dir_recursive(reg_dir);
                }
            }
            if (!ui_run_codegen_with_paths(input_path.c_str(),
                                           registry_path.c_str(),
                                           out_gen_dir.c_str(),
                                           out_user_dir.c_str(),
                                           doc_base.c_str(),
                                           &cdiag)) {
                ui_append_diag_strings(cdiag, errors, warnings);
                ui_print_diag_to_stderr(cdiag);
                exit_code = 1;
            } else {
                ui_append_diag_strings(cdiag, errors, warnings);
                codegen_ok = 1;
            }
        }
    }
    if (exit_code != 0) {
        status = "error";
    }
    if (codegen_ok) {
        std::string doc_sym = ui_doc_symbol_from_name(doc_base);
        output_files.push_back(ui_join_path(out_gen_dir, doc_sym + "_actions_gen.h"));
        output_files.push_back(ui_join_path(out_gen_dir, doc_sym + "_actions_gen.cpp"));
        output_files.push_back(ui_join_path(out_user_dir, doc_sym + "_actions_user.h"));
        output_files.push_back(ui_join_path(out_user_dir, doc_sym + "_actions_user.cpp"));
        output_files.push_back(registry_path);
    }
    if (!report_path.empty()) {
        if (!ui_write_cli_report(report_path,
                                 "headless-codegen",
                                 input_path,
                                 output_files,
                                 errors,
                                 warnings,
                                 0,
                                 exit_code,
                                 status,
                                 0,
                                 repo_root,
                                 cwd)) {
            if (exit_code == 0) {
                exit_code = 1;
                status = "error";
            }
        }
    }
    return exit_code;
}

static int ui_run_headless_build_ui(const std::vector<std::string>& args)
{
    std::string input_path;
    std::string out_root;
    std::string doc_name;
    std::string report_path;
    std::string repo_root = ui_find_repo_root("");
    std::string cwd = ui_get_cwd();
    std::string doc_base;
    domui_doc doc;
    domui_diag load_diag;
    domui_diag vdiag;
    domui_diag save_diag;
    domui_diag json_diag;
    domui_diag cdiag;
    UiDocOutputPaths paths;
    std::vector<std::string> errors;
    std::vector<std::string> warnings;
    std::vector<std::string> output_files;
    int json_ok = 1;
    int exit_code = 0;
    const char* status = "ok";
    int tlv_ok = 0;
    int codegen_ok = 0;
    (void)ui_get_arg_value(args, "--report", report_path);
    if (!ui_get_arg_value(args, "--in", input_path) || input_path.empty()) {
        errors.push_back("headless-build-ui: missing --in");
        fprintf(stderr, "headless-build-ui: missing --in\n");
        exit_code = 1;
    } else if (!ui_get_arg_value(args, "--docname", doc_name) || doc_name.empty()) {
        errors.push_back("headless-build-ui: missing --docname");
        fprintf(stderr, "headless-build-ui: missing --docname\n");
        exit_code = 1;
    } else if (!ui_get_arg_value(args, "--out-root", out_root) || out_root.empty()) {
        errors.push_back("headless-build-ui: missing --out-root");
        fprintf(stderr, "headless-build-ui: missing --out-root\n");
        exit_code = 1;
    } else {
        doc_base = ui_strip_tlv_extension(doc_name);
        if (doc_base.empty()) {
            errors.push_back("headless-build-ui: invalid --docname");
            fprintf(stderr, "headless-build-ui: invalid --docname\n");
            exit_code = 1;
        } else if (!domui_doc_load_tlv(&doc, input_path.c_str(), &load_diag)) {
            ui_append_diag_strings(load_diag, errors, warnings);
            ui_print_diag_to_stderr(load_diag);
            exit_code = 1;
        } else {
            ui_append_diag_strings(load_diag, errors, warnings);
            if (!domui_validate_doc(&doc, 0, &vdiag)) {
                ui_append_diag_strings(vdiag, errors, warnings);
                ui_print_diag_to_stderr(vdiag);
                exit_code = 2;
            } else {
                ui_append_diag_strings(vdiag, errors, warnings);
            }
        }
    }
    if (exit_code == 0) {
        std::string tlv_name = doc_base + ".tlv";
        std::string base_path = ui_join_path(out_root, tlv_name);
        ui_compute_doc_paths(base_path, 1, paths);
        if (!paths.doc_root.empty()) {
            ui_ensure_dir_recursive(paths.doc_root);
        }
        if (!paths.doc_dir.empty()) {
            ui_ensure_dir_recursive(paths.doc_dir);
        }
        if (!paths.gen_dir.empty()) {
            ui_ensure_dir_recursive(paths.gen_dir);
        }
        if (!paths.user_dir.empty()) {
            ui_ensure_dir_recursive(paths.user_dir);
        }
        if (!paths.reg_dir.empty()) {
            ui_ensure_dir_recursive(paths.reg_dir);
        }
        tlv_ok = ui_save_doc_tlv_json(&doc,
                                      paths,
                                      doc_base.c_str(),
                                      1,
                                      1,
                                      &save_diag,
                                      &json_diag,
                                      &json_ok);
        ui_append_diag_strings(save_diag, errors, warnings);
        ui_append_diag_strings(json_diag, errors, warnings);
        if (!tlv_ok) {
            ui_print_diag_to_stderr(save_diag);
            exit_code = 1;
        } else {
            output_files.push_back(paths.tlv_path);
            if (!json_ok) {
                ui_print_diag_to_stderr(json_diag);
                exit_code = 1;
            } else {
                output_files.push_back(paths.json_path);
            }
        }
    }
    if (exit_code == 0) {
        if (!ui_run_codegen_with_paths(paths.tlv_path.c_str(),
                                       paths.reg_path.c_str(),
                                       paths.gen_dir.c_str(),
                                       paths.user_dir.c_str(),
                                       doc_base.c_str(),
                                       &cdiag)) {
            ui_append_diag_strings(cdiag, errors, warnings);
            ui_print_diag_to_stderr(cdiag);
            exit_code = 1;
        } else {
            ui_append_diag_strings(cdiag, errors, warnings);
            codegen_ok = 1;
        }
    }
    if (codegen_ok) {
        std::string doc_sym = ui_doc_symbol_from_name(doc_base);
        output_files.push_back(ui_join_path(paths.gen_dir, doc_sym + "_actions_gen.h"));
        output_files.push_back(ui_join_path(paths.gen_dir, doc_sym + "_actions_gen.cpp"));
        output_files.push_back(ui_join_path(paths.user_dir, doc_sym + "_actions_user.h"));
        output_files.push_back(ui_join_path(paths.user_dir, doc_sym + "_actions_user.cpp"));
        output_files.push_back(paths.reg_path);
    }
    if (exit_code != 0) {
        status = "error";
    }
    if (!report_path.empty()) {
        if (!ui_write_cli_report(report_path,
                                 "headless-build-ui",
                                 input_path,
                                 output_files,
                                 errors,
                                 warnings,
                                 0,
                                 exit_code,
                                 status,
                                 0,
                                 repo_root,
                                 cwd)) {
            if (exit_code == 0) {
                exit_code = 1;
                status = "error";
            }
        }
    }
    return exit_code;
}

struct UiOpsSaveContext {
    UiDocOutputPaths paths;

    UiOpsSaveContext()
        : paths()
    {
    }
};

static bool ui_ops_save_callback(void* user, const domui_doc* doc, domui_diag* diag)
{
    UiOpsSaveContext* ctx = (UiOpsSaveContext*)user;
    domui_diag save_diag;
    domui_diag json_diag;
    int json_ok = 1;
    int tlv_ok = 0;
    if (!ctx || !doc) {
        if (diag) {
            diag->add_error("ops: save invalid context", 0u, "save");
        }
        return false;
    }
    {
        std::string out_dir = ui_path_dir(ctx->paths.tlv_path);
        if (!out_dir.empty()) {
            ui_ensure_dir_recursive(out_dir);
        }
    }
    {
        domui_doc* mutable_doc = const_cast<domui_doc*>(doc);
        tlv_ok = ui_save_doc_tlv_json(mutable_doc,
                                      ctx->paths,
                                      NULL,
                                      1,
                                      1,
                                      &save_diag,
                                      &json_diag,
                                      &json_ok);
    }
    ui_append_diag_items(diag, save_diag);
    ui_append_diag_items(diag, json_diag);
    if (!tlv_ok || !json_ok) {
        if (diag && save_diag.error_count() == 0u && json_diag.error_count() == 0u) {
            diag->add_error("ops: save failed", 0u, "save");
        }
        return false;
    }
    return true;
}

static int ui_run_headless_apply(const std::vector<std::string>& args)
{
    std::string input_path;
    std::string out_path;
    std::string report_path;
    std::string script_path;
    std::string repo_root = ui_find_repo_root("");
    std::string cwd = ui_get_cwd();
    domui_doc doc;
    domui_diag load_diag;
    domui_diag script_diag;
    domui_diag ops_diag;
    domui_diag vdiag;
    domui_diag save_diag;
    domui_diag json_diag;
    UiDocOutputPaths paths;
    UiOpsSaveContext save_ctx;
    domui_ops_apply_params params;
    domui_ops_result ops_result;
    std::vector<unsigned char> script_bytes;
    std::vector<std::string> errors;
    std::vector<std::string> warnings;
    std::vector<std::string> output_files;
    int exit_code = 0;
    const char* status = "ok";
    int json_ok = 1;
    int tlv_ok = 0;
    int apply_ok = 0;
    int in_new = ui_has_arg(args, "--in-new");

    (void)ui_get_arg_value(args, "--report", report_path);
    if (!ui_get_arg_value(args, "--headless-apply", input_path) || input_path.empty()) {
        errors.push_back("headless-apply: missing input path");
        fprintf(stderr, "headless-apply: missing input path\n");
        exit_code = 1;
    } else if (!ui_get_arg_value(args, "--script", script_path) || script_path.empty()) {
        errors.push_back("headless-apply: missing --script");
        fprintf(stderr, "headless-apply: missing --script\n");
        exit_code = 1;
    } else {
        if (!ui_get_arg_value(args, "--out", out_path)) {
            out_path = input_path;
        }
        if (out_path.empty()) {
            errors.push_back("headless-apply: missing output path");
            fprintf(stderr, "headless-apply: missing output path\n");
            exit_code = 1;
        }
    }

    if (exit_code == 0) {
        if (!in_new) {
            if (!domui_doc_load_tlv(&doc, input_path.c_str(), &load_diag)) {
                ui_append_diag_strings(load_diag, errors, warnings);
                ui_print_diag_to_stderr(load_diag);
                exit_code = 1;
            } else {
                ui_append_diag_strings(load_diag, errors, warnings);
            }
        } else {
            doc.clear();
        }
    }

    if (exit_code == 0) {
        if (!domui_read_file_bytes(script_path.c_str(), script_bytes, &script_diag)) {
            ui_append_diag_strings(script_diag, errors, warnings);
            ui_print_diag_to_stderr(script_diag);
            exit_code = 1;
        } else {
            ui_append_diag_strings(script_diag, errors, warnings);
        }
    }

    if (exit_code == 0) {
        ui_compute_doc_paths(out_path, 0, paths);
        save_ctx.paths = paths;
        params.save_fn = ui_ops_save_callback;
        params.save_user = &save_ctx;
        apply_ok = domui_ops_apply_json(&doc,
                                        script_bytes.empty() ? "" : (const char*)&script_bytes[0],
                                        script_bytes.size(),
                                        &params,
                                        &ops_result,
                                        &ops_diag) ? 1 : 0;
        ui_append_diag_strings(ops_diag, errors, warnings);
        if (!apply_ok) {
            ui_print_diag_to_stderr(ops_diag);
            exit_code = 3;
        } else if (ops_result.save_failed) {
            ui_print_diag_to_stderr(ops_diag);
            exit_code = 1;
        } else if (ops_result.validation_failed) {
            ui_print_diag_to_stderr(ops_diag);
            exit_code = 2;
        }
    }

    if (exit_code == 0 && ops_result.final_validate) {
        if (!domui_validate_doc(&doc, 0, &vdiag)) {
            ui_append_diag_strings(vdiag, errors, warnings);
            ui_print_diag_to_stderr(vdiag);
            exit_code = 2;
        } else {
            ui_append_diag_strings(vdiag, errors, warnings);
        }
    }

    if (exit_code == 0) {
        std::string out_dir = ui_path_dir(paths.tlv_path);
        if (!out_dir.empty()) {
            ui_ensure_dir_recursive(out_dir);
        }
        tlv_ok = ui_save_doc_tlv_json(&doc,
                                      paths,
                                      NULL,
                                      1,
                                      1,
                                      &save_diag,
                                      &json_diag,
                                      &json_ok);
        ui_append_diag_strings(save_diag, errors, warnings);
        ui_append_diag_strings(json_diag, errors, warnings);
        if (!tlv_ok) {
            ui_print_diag_to_stderr(save_diag);
            exit_code = 1;
        } else {
            output_files.push_back(paths.tlv_path);
            if (!json_ok) {
                ui_print_diag_to_stderr(json_diag);
                exit_code = 1;
            } else {
                output_files.push_back(paths.json_path);
            }
        }
    }

    if (exit_code != 0) {
        status = "error";
    }

    if (!report_path.empty()) {
        const std::map<std::string, domui_u32>* created_ids = apply_ok ? &ops_result.created_ids : 0;
        if (!ui_write_cli_report(report_path,
                                 "headless-apply",
                                 input_path,
                                 output_files,
                                 errors,
                                 warnings,
                                 created_ids,
                                 exit_code,
                                 status,
                                 0,
                                 repo_root,
                                 cwd)) {
            if (exit_code == 0) {
                exit_code = 1;
                status = "error";
            }
        }
    }
    return exit_code;
}

static int ui_run_cli(const std::vector<std::string>& args)
{
    int cmd_count = 0;
    int cmd_scan = ui_has_arg(args, "--scan-ui");
    int cmd_validate = ui_has_arg(args, "--headless-validate");
    int cmd_format = ui_has_arg(args, "--headless-format");
    int cmd_codegen = ui_has_arg(args, "--headless-codegen");
    int cmd_build = ui_has_arg(args, "--headless-build-ui");
    int cmd_apply = ui_has_arg(args, "--headless-apply");
    if (ui_has_arg(args, "--help") || ui_has_arg(args, "-h")) {
        ui_print_help();
        return 0;
    }
    cmd_count += cmd_scan ? 1 : 0;
    cmd_count += cmd_validate ? 1 : 0;
    cmd_count += cmd_format ? 1 : 0;
    cmd_count += cmd_codegen ? 1 : 0;
    cmd_count += cmd_build ? 1 : 0;
    cmd_count += cmd_apply ? 1 : 0;
    if (cmd_count == 0) {
        if (ui_has_arg_prefix(args, "--headless-")) {
            fprintf(stderr, "cli: unknown headless command\n");
        } else {
            fprintf(stderr, "cli: no command specified\n");
        }
        ui_print_help();
        return 1;
    }
    if (cmd_count > 1) {
        fprintf(stderr, "cli: multiple commands specified\n");
        return 1;
    }
    if (cmd_scan) {
        return ui_run_scan_cli(args);
    }
    if (cmd_validate) {
        return ui_run_headless_validate(args);
    }
    if (cmd_format) {
        return ui_run_headless_format(args);
    }
    if (cmd_codegen) {
        return ui_run_headless_codegen(args);
    }
    if (cmd_build) {
        return ui_run_headless_build_ui(args);
    }
    if (cmd_apply) {
        return ui_run_headless_apply(args);
    }
    return 1;
}

static int ui_should_run_cli(const std::vector<std::string>& args)
{
    if (ui_has_arg(args, "--help") || ui_has_arg(args, "-h")) {
        return 1;
    }
    if (ui_has_arg(args, "--scan-ui")) {
        return 1;
    }
    if (ui_has_arg_prefix(args, "--headless-")) {
        return 1;
    }
    return 0;
}

static int ui_open_tool_dialog_show(const UiOpenToolDialogState* state, int want_canonical)
{
    if (!state) {
        return 0;
    }
    if (want_canonical) {
        return (SendMessageA(state->check_canonical, BM_GETCHECK, 0, 0) == BST_CHECKED) ? 1 : 0;
    }
    return (SendMessageA(state->check_legacy, BM_GETCHECK, 0, 0) == BST_CHECKED) ? 1 : 0;
}

static void ui_open_tool_dialog_populate(UiOpenToolDialogState* state)
{
    if (!state || !state->list) {
        return;
    }
    int show_canonical = ui_open_tool_dialog_show(state, 1);
    int show_legacy = ui_open_tool_dialog_show(state, 0);
    if (!show_canonical && !show_legacy) {
        show_canonical = 1;
        show_legacy = 1;
    }
    ListView_DeleteAllItems(state->list);
    for (size_t i = 0u; i < state->entries.size(); ++i) {
        const UiDiscoveryEntry& entry = state->entries[i];
        if (entry.is_canonical && !show_canonical) {
            continue;
        }
        if (!entry.is_canonical && !show_legacy) {
            continue;
        }
        std::string type_text = entry.is_canonical ? "Canonical" : "Legacy";
        std::string version_text = entry.is_canonical ? ui_u32_to_string(entry.format_version) : "-";
        int row = ui_listview_insert_item(state->list, entry.tool.c_str(), (LPARAM)i);
        ui_listview_set_item_text(state->list, row, 1, type_text.c_str());
        ui_listview_set_item_text(state->list, row, 2, entry.rel_path.c_str());
        ui_listview_set_item_text(state->list, row, 3, version_text.c_str());
    }
}

static void ui_open_tool_dialog_accept(UiOpenToolDialogState* state)
{
    if (!state || !state->list) {
        return;
    }
    int sel = ListView_GetNextItem(state->list, -1, LVNI_SELECTED);
    if (sel < 0) {
        return;
    }
    LVITEMA item;
    memset(&item, 0, sizeof(item));
    item.mask = LVIF_PARAM;
    item.iItem = sel;
    if (ListView_GetItem(state->list, &item)) {
        state->selected_index = (int)item.lParam;
        state->result = 1;
        if (state->hwnd) {
            DestroyWindow(state->hwnd);
        }
    }
}

static void ui_open_tool_dialog_layout(UiOpenToolDialogState* state, int width, int height)
{
    const int pad = 10;
    const int check_h = 20;
    const int btn_w = 90;
    const int btn_h = 24;
    int list_top = pad + check_h + 6;
    int list_h = height - list_top - btn_h - pad * 2;
    int list_w = width - pad * 2;
    if (list_h < 20) {
        list_h = 20;
    }
    MoveWindow(state->check_canonical, pad, pad, 140, check_h, TRUE);
    MoveWindow(state->check_legacy, pad + 150, pad, 140, check_h, TRUE);
    MoveWindow(state->list, pad, list_top, list_w, list_h, TRUE);
    MoveWindow(state->btn_cancel, width - pad - btn_w, height - pad - btn_h, btn_w, btn_h, TRUE);
    MoveWindow(state->btn_open, width - pad * 2 - btn_w * 2, height - pad - btn_h, btn_w, btn_h, TRUE);
}

static LRESULT CALLBACK UiEditor_OpenToolDialogWndProc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    UiOpenToolDialogState* state = (UiOpenToolDialogState*)GetWindowLongPtr(hwnd, GWLP_USERDATA);
    switch (msg) {
    case WM_CREATE:
        {
            CREATESTRUCTA* cs = (CREATESTRUCTA*)lparam;
            state = cs ? (UiOpenToolDialogState*)cs->lpCreateParams : 0;
            SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)state);
            if (!state) {
                return 0;
            }
            state->hwnd = hwnd;
            state->check_canonical = CreateWindowExA(0,
                                                     "BUTTON",
                                                     "Canonical only",
                                                     WS_CHILD | WS_VISIBLE | BS_AUTOCHECKBOX,
                                                     0, 0, 10, 10,
                                                     hwnd,
                                                     (HMENU)ID_OPEN_TOOL_CANON,
                                                     NULL,
                                                     NULL);
            state->check_legacy = CreateWindowExA(0,
                                                  "BUTTON",
                                                  "Legacy only",
                                                  WS_CHILD | WS_VISIBLE | BS_AUTOCHECKBOX,
                                                  0, 0, 10, 10,
                                                  hwnd,
                                                  (HMENU)ID_OPEN_TOOL_LEGACY,
                                                  NULL,
                                                  NULL);
            state->list = CreateWindowExA(WS_EX_CLIENTEDGE,
                                          WC_LISTVIEWA,
                                          "",
                                          WS_CHILD | WS_VISIBLE | LVS_REPORT | LVS_SINGLESEL |
                                              LVS_SHOWSELALWAYS,
                                          0, 0, 10, 10,
                                          hwnd,
                                          (HMENU)ID_OPEN_TOOL_LIST,
                                          NULL,
                                          NULL);
            state->btn_open = CreateWindowExA(0,
                                              "BUTTON",
                                              "Open",
                                              WS_CHILD | WS_VISIBLE | BS_DEFPUSHBUTTON,
                                              0, 0, 10, 10,
                                              hwnd,
                                              (HMENU)ID_OPEN_TOOL_OPEN,
                                              NULL,
                                              NULL);
            state->btn_cancel = CreateWindowExA(0,
                                                "BUTTON",
                                                "Cancel",
                                                WS_CHILD | WS_VISIBLE,
                                                0, 0, 10, 10,
                                                hwnd,
                                                (HMENU)ID_OPEN_TOOL_CANCEL,
                                                NULL,
                                                NULL);
            {
                HFONT font = (HFONT)GetStockObject(DEFAULT_GUI_FONT);
                SendMessageA(state->check_canonical, WM_SETFONT, (WPARAM)font, TRUE);
                SendMessageA(state->check_legacy, WM_SETFONT, (WPARAM)font, TRUE);
                SendMessageA(state->list, WM_SETFONT, (WPARAM)font, TRUE);
                SendMessageA(state->btn_open, WM_SETFONT, (WPARAM)font, TRUE);
                SendMessageA(state->btn_cancel, WM_SETFONT, (WPARAM)font, TRUE);
            }
            {
                LVCOLUMNA col;
                memset(&col, 0, sizeof(col));
                col.mask = LVCF_TEXT | LVCF_WIDTH | LVCF_SUBITEM;
                col.pszText = (LPSTR)"Tool";
                col.cx = 120;
                ListView_InsertColumn(state->list, 0, &col);
                col.pszText = (LPSTR)"UI Type";
                col.cx = 90;
                col.iSubItem = 1;
                ListView_InsertColumn(state->list, 1, &col);
                col.pszText = (LPSTR)"Path";
                col.cx = 420;
                col.iSubItem = 2;
                ListView_InsertColumn(state->list, 2, &col);
                col.pszText = (LPSTR)"Version";
                col.cx = 70;
                col.iSubItem = 3;
                ListView_InsertColumn(state->list, 3, &col);
                ListView_SetExtendedListViewStyle(state->list, LVS_EX_FULLROWSELECT | LVS_EX_GRIDLINES);
            }
            ui_open_tool_dialog_populate(state);
            {
                RECT rc;
                GetClientRect(hwnd, &rc);
                ui_open_tool_dialog_layout(state, rc.right - rc.left, rc.bottom - rc.top);
            }
        }
        return 0;
    case WM_SIZE:
        if (state) {
            ui_open_tool_dialog_layout(state, LOWORD(lparam), HIWORD(lparam));
        }
        return 0;
    case WM_COMMAND:
        if (!state) {
            return 0;
        }
        switch (LOWORD(wparam)) {
        case ID_OPEN_TOOL_OPEN:
            ui_open_tool_dialog_accept(state);
            return 0;
        case ID_OPEN_TOOL_CANCEL:
            state->result = 0;
            DestroyWindow(hwnd);
            return 0;
        case ID_OPEN_TOOL_CANON:
        case ID_OPEN_TOOL_LEGACY:
            ui_open_tool_dialog_populate(state);
            return 0;
        default:
            break;
        }
        break;
    case WM_NOTIFY:
        if (state) {
            NMHDR* hdr = (NMHDR*)lparam;
            if (hdr && hdr->idFrom == ID_OPEN_TOOL_LIST) {
                if (hdr->code == NM_DBLCLK || hdr->code == LVN_ITEMACTIVATE) {
                    ui_open_tool_dialog_accept(state);
                    return 0;
                }
            }
        }
        break;
    case WM_CLOSE:
        if (state) {
            state->result = 0;
        }
        DestroyWindow(hwnd);
        return 0;
    default:
        break;
    }
    return DefWindowProcA(hwnd, msg, wparam, lparam);
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

class UiEditorApp {
public:
    UiEditorApp();
    bool init(HINSTANCE inst);
    void shutdown();

    LRESULT handle_message(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam);
    LRESULT handle_overlay_message(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam);
    LRESULT handle_splitter_message(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam);

private:
    void on_create(HWND hwnd);
    void on_destroy();
    void on_size(int w, int h);
    void layout_children();
    void update_preview_size();
    void update_title();
    void mark_dirty(int dirty);
    bool scan_ui_index(const char* out_path);
    void update_info_panel();
    bool open_tool_ui_dialog();
    bool import_legacy_ui_dialog();
    bool import_legacy_ui_path(const char* legacy_path);
    bool export_tool_ui();

    void new_document();
    bool open_document();
    bool load_document(const char* path);
    bool save_document();
    bool save_document_as();
    bool save_document_to(const char* path);
    bool run_codegen(const char* tlv_path, domui_diag* out_diag);
    void auto_fill_action_keys();
    bool confirm_discard();

    void rebuild_tree();
    void rebuild_tree_item(domui_widget_id id, HTREEITEM parent);
    void rebuild_inspector();
    void refresh_inspector_edit();
    void select_widget(domui_widget_id id, int from_tree);
    void search_tree(const char* text);

    void log_clear();
    void log_add(const char* text, domui_widget_id widget_id);
    void log_info(const char* text);
    void log_from_diag(const domui_diag& diag);
    void log_append_diag(const domui_diag& diag);

    void refresh_layout(int rebuild_schema);
    void compute_layout(domui_diag* diag);
    bool build_dui_schema(std::vector<unsigned char>& out_bytes);
    void build_dui_node(domui_widget_id id, std::vector<unsigned char>& out_payload);

    void ensure_default_props(domui_widget* w);
    domui_widget_id add_widget(domui_widget_type type, domui_widget_id parent_id);
    void delete_widget(domui_widget_id id);
    domui_u32 next_z_for_parent(domui_widget_id parent_id);

    void push_command(const char* label, const domui_doc& before);
    void undo();
    void redo();

    domui_widget_id find_search_match(const std::string& needle) const;
    domui_layout_rect get_layout_rect(domui_widget_id id) const;
    domui_layout_rect get_parent_content_rect(domui_widget_id id) const;
    int apply_rect_to_widget(domui_widget* w, const domui_layout_rect& rect);

    void overlay_paint(HDC hdc);
    int overlay_hit_test(const POINT& pt, domui_layout_rect* out_rect, DragMode* out_handle);
    int overlay_should_capture(const POINT& pt) const;
    void overlay_start_drag(const POINT& pt);
    void overlay_update_drag(const POINT& pt);
    void overlay_end_drag();
    void nudge_selected(int dx, int dy);
    static LRESULT CALLBACK DuiSubclassProc(HWND hwnd,
                                            UINT msg,
                                            WPARAM wparam,
                                            LPARAM lparam,
                                            UINT_PTR id,
                                            DWORD_PTR ref);
    HINSTANCE m_instance;
    HWND m_hwnd;
    HWND m_tree_search;
    HWND m_tree;
    HWND m_preview_host;
    HWND m_overlay;
    int m_overlay_layered;
    HWND m_info_panel;
    HWND m_inspector;
    HWND m_inspector_edit;
    HWND m_log;
    HWND m_split_left;
    HWND m_split_right;
    HWND m_split_bottom;
    HFONT m_font;

    int m_left_width;
    int m_right_width;
    int m_bottom_height;
    int m_split_drag_type;
    int m_split_dragging;
    int m_tree_dragging;
    HTREEITEM m_tree_drag_item;
    domui_widget_id m_tree_drag_id;
    HTREEITEM m_tree_drop_target;

    domui_doc m_doc;
    std::string m_current_path;
    std::string m_repo_root;
    std::vector<UiDiscoveryEntry> m_discovery;
    DocOrigin m_doc_origin;
    std::string m_owning_tool;
    std::string m_import_report_path;
    int m_dirty;
    domui_widget_id m_selected_id;
    domui_layout_rect m_root_rect;

    std::vector<domui_layout_result> m_layout_results;
    std::vector<domui_widget_id> m_layout_order;
    std::map<domui_widget_id, domui_layout_rect> m_layout_map;
    std::map<domui_widget_id, HTREEITEM> m_tree_items;
    std::vector<InspectorRow> m_inspector_rows;
    int m_inspector_edit_row;
    std::vector<EditorCommand> m_undo;
    std::vector<EditorCommand> m_redo;
    domui_doc m_drag_before_doc;

    DragMode m_drag_mode;
    domui_widget_id m_drag_widget_id;
    POINT m_drag_start_pt;
    domui_layout_rect m_drag_start_rect;

    const dui_api_v1* m_dui_api;
    dui_context* m_dui_ctx;
    dui_window* m_dui_win;
    dui_native_api_v1* m_dui_native;
    HWND m_dui_hwnd;
};

static LRESULT CALLBACK UiEditor_MainWndProc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam);
static LRESULT CALLBACK UiEditor_OverlayWndProc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam);
static LRESULT CALLBACK UiEditor_SplitterWndProc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam);
static LRESULT CALLBACK UiEditor_OpenToolDialogWndProc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam);

UiEditorApp::UiEditorApp()
    : m_instance(0),
      m_hwnd(0),
      m_tree_search(0),
      m_tree(0),
      m_preview_host(0),
      m_overlay(0),
      m_overlay_layered(0),
      m_info_panel(0),
      m_inspector(0),
      m_inspector_edit(0),
      m_log(0),
      m_split_left(0),
      m_split_right(0),
      m_split_bottom(0),
      m_font(0),
      m_left_width(240),
      m_right_width(280),
      m_bottom_height(180),
      m_split_drag_type(0),
      m_split_dragging(0),
      m_tree_dragging(0),
      m_tree_drag_item(0),
      m_tree_drag_id(0u),
      m_tree_drop_target(0),
      m_doc(),
      m_current_path(),
      m_repo_root(),
      m_discovery(),
      m_doc_origin(DOC_ORIGIN_CANONICAL),
      m_owning_tool(),
      m_import_report_path(),
      m_dirty(0),
      m_selected_id(0u),
      m_root_rect(),
      m_layout_results(),
      m_layout_order(),
      m_layout_map(),
      m_tree_items(),
      m_inspector_rows(),
      m_inspector_edit_row(-1),
      m_undo(),
      m_redo(),
      m_drag_before_doc(),
      m_drag_mode(DRAG_NONE),
      m_drag_widget_id(0u),
      m_dui_api(0),
      m_dui_ctx(0),
      m_dui_win(0),
      m_dui_native(0),
      m_dui_hwnd(0)
{
    m_root_rect.x = 0;
    m_root_rect.y = 0;
    m_root_rect.w = 0;
    m_root_rect.h = 0;
    m_drag_start_pt.x = 0;
    m_drag_start_pt.y = 0;
    m_drag_start_rect.x = 0;
    m_drag_start_rect.y = 0;
    m_drag_start_rect.w = 0;
    m_drag_start_rect.h = 0;
}

bool UiEditorApp::init(HINSTANCE inst)
{
    WNDCLASSA wc;
    INITCOMMONCONTROLSEX icc;

    m_instance = inst;

    memset(&icc, 0, sizeof(icc));
    icc.dwSize = sizeof(icc);
    icc.dwICC = ICC_TREEVIEW_CLASSES | ICC_LISTVIEW_CLASSES | ICC_TAB_CLASSES;
    InitCommonControlsEx(&icc);

    memset(&wc, 0, sizeof(wc));
    wc.lpfnWndProc = UiEditor_MainWndProc;
    wc.hInstance = inst;
    wc.lpszClassName = kMainClass;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    if (!RegisterClassA(&wc)) {
        return false;
    }

    memset(&wc, 0, sizeof(wc));
    wc.lpfnWndProc = UiEditor_OverlayWndProc;
    wc.hInstance = inst;
    wc.lpszClassName = kOverlayClass;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)GetStockObject(NULL_BRUSH);
    if (!RegisterClassA(&wc)) {
        return false;
    }

    memset(&wc, 0, sizeof(wc));
    wc.lpfnWndProc = UiEditor_SplitterWndProc;
    wc.hInstance = inst;
    wc.lpszClassName = kSplitterClass;
    wc.hCursor = LoadCursor(NULL, IDC_SIZEWE);
    wc.hbrBackground = (HBRUSH)(COLOR_3DFACE + 1);
    if (!RegisterClassA(&wc)) {
        return false;
    }

    memset(&wc, 0, sizeof(wc));
    wc.lpfnWndProc = UiEditor_OpenToolDialogWndProc;
    wc.hInstance = inst;
    wc.lpszClassName = kOpenToolDialogClass;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    if (!RegisterClassA(&wc)) {
        return false;
    }

    m_hwnd = CreateWindowExA(0,
                             kMainClass,
                             "Dominium UI Editor",
                             WS_OVERLAPPEDWINDOW | WS_CLIPCHILDREN,
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
    ShowWindow(m_hwnd, SW_SHOW);
    UpdateWindow(m_hwnd);
    return true;
}

void UiEditorApp::shutdown()
{
    if (m_dui_api && m_dui_win) {
        m_dui_api->destroy_window(m_dui_win);
        m_dui_win = 0;
    }
    if (m_dui_api && m_dui_ctx) {
        m_dui_api->destroy_context(m_dui_ctx);
        m_dui_ctx = 0;
    }
}

void UiEditorApp::on_create(HWND hwnd)
{
    HMENU menu;
    HMENU file_menu;
    HMENU edit_menu;

    m_font = (HFONT)GetStockObject(DEFAULT_GUI_FONT);

    menu = CreateMenu();
    file_menu = CreatePopupMenu();
    edit_menu = CreatePopupMenu();

    AppendMenuA(file_menu, MF_STRING, ID_FILE_NEW, "&New");
    AppendMenuA(file_menu, MF_STRING, ID_FILE_OPEN, "&Open...");
    AppendMenuA(file_menu, MF_STRING, ID_FILE_OPEN_TOOL, "Open Tool UI...");
    AppendMenuA(file_menu, MF_STRING, ID_FILE_IMPORT_LEGACY, "Import Legacy UI...");
    AppendMenuA(file_menu, MF_STRING, ID_FILE_EXPORT_TOOL, "Export Tool UI...");
    AppendMenuA(file_menu, MF_STRING, ID_FILE_REFRESH_INDEX, "Refresh UI &Index");
    AppendMenuA(file_menu, MF_SEPARATOR, 0, 0);
    AppendMenuA(file_menu, MF_STRING, ID_FILE_SAVE, "&Save");
    AppendMenuA(file_menu, MF_STRING, ID_FILE_SAVE_AS, "Save &As...");
    AppendMenuA(file_menu, MF_SEPARATOR, 0, 0);
    AppendMenuA(file_menu, MF_STRING, ID_FILE_VALIDATE, "&Validate");
    AppendMenuA(file_menu, MF_SEPARATOR, 0, 0);
    AppendMenuA(file_menu, MF_STRING, ID_FILE_EXIT, "E&xit");

    AppendMenuA(edit_menu, MF_STRING, ID_EDIT_UNDO, "&Undo");
    AppendMenuA(edit_menu, MF_STRING, ID_EDIT_REDO, "&Redo");
    AppendMenuA(edit_menu, MF_SEPARATOR, 0, 0);
    AppendMenuA(edit_menu, MF_STRING, ID_EDIT_DELETE, "&Delete Widget");

    AppendMenuA(menu, MF_POPUP, (UINT_PTR)file_menu, "&File");
    AppendMenuA(menu, MF_POPUP, (UINT_PTR)edit_menu, "&Edit");
    SetMenu(hwnd, menu);

    m_tree_search = CreateWindowExA(WS_EX_CLIENTEDGE,
                                    "EDIT",
                                    "",
                                    WS_CHILD | WS_VISIBLE | ES_AUTOHSCROLL,
                                    0, 0, 10, 10,
                                    hwnd,
                                    (HMENU)ID_TREE_SEARCH,
                                    m_instance,
                                    NULL);

    m_tree = CreateWindowExA(WS_EX_CLIENTEDGE,
                             WC_TREEVIEWA,
                             "",
                             WS_CHILD | WS_VISIBLE | TVS_HASLINES | TVS_HASBUTTONS |
                                 TVS_LINESATROOT | TVS_SHOWSELALWAYS,
                             0, 0, 10, 10,
                             hwnd,
                             (HMENU)ID_TREE,
                             m_instance,
                             NULL);

    m_preview_host = CreateWindowExA(WS_EX_CLIENTEDGE,
                                     "STATIC",
                                     "",
                                     WS_CHILD | WS_VISIBLE | WS_CLIPCHILDREN | WS_CLIPSIBLINGS,
                                     0, 0, 10, 10,
                                     hwnd,
                                     (HMENU)ID_PREVIEW_HOST,
                                     m_instance,
                                     NULL);

    m_overlay = CreateWindowExA(WS_EX_LAYERED,
                                kOverlayClass,
                                "",
                                WS_CHILD | WS_VISIBLE,
                                0, 0, 10, 10,
                                m_preview_host,
                                NULL,
                                m_instance,
                                this);
    if (m_overlay) {
        if (SetLayeredWindowAttributes(m_overlay, kOverlayClearColor, 0, LWA_COLORKEY)) {
            m_overlay_layered = 1;
        }
    }
    if (m_overlay && !m_overlay_layered) {
        SetTimer(m_hwnd, ID_PREVIEW_TIMER, 100, NULL);
    }

    m_info_panel = CreateWindowExA(WS_EX_CLIENTEDGE,
                                   "STATIC",
                                   "",
                                   WS_CHILD | WS_VISIBLE | SS_LEFT | SS_NOPREFIX,
                                   0, 0, 10, 10,
                                   hwnd,
                                   (HMENU)ID_INFO_PANEL,
                                   m_instance,
                                   NULL);

    m_inspector = CreateWindowExA(WS_EX_CLIENTEDGE,
                                  WC_LISTVIEWA,
                                  "",
                                  WS_CHILD | WS_VISIBLE | LVS_REPORT | LVS_SINGLESEL |
                                      LVS_SHOWSELALWAYS,
                                  0, 0, 10, 10,
                                  hwnd,
                                  (HMENU)ID_INSPECTOR,
                                  m_instance,
                                  NULL);

    m_inspector_edit = CreateWindowExA(WS_EX_CLIENTEDGE,
                                       "EDIT",
                                       "",
                                       WS_CHILD | WS_VISIBLE | ES_AUTOHSCROLL,
                                       0, 0, 10, 10,
                                       hwnd,
                                       (HMENU)ID_INSPECTOR_EDIT,
                                       m_instance,
                                       NULL);

    m_log = CreateWindowExA(WS_EX_CLIENTEDGE,
                            "LISTBOX",
                            "",
                            WS_CHILD | WS_VISIBLE | LBS_NOTIFY | WS_VSCROLL,
                            0, 0, 10, 10,
                            hwnd,
                            (HMENU)ID_LOG,
                            m_instance,
                            NULL);

    m_split_left = CreateWindowExA(0,
                                   kSplitterClass,
                                   "",
                                   WS_CHILD | WS_VISIBLE,
                                   0, 0, 10, 10,
                                   hwnd,
                                   (HMENU)ID_SPLIT_LEFT,
                                   m_instance,
                                   this);

    m_split_right = CreateWindowExA(0,
                                    kSplitterClass,
                                    "",
                                    WS_CHILD | WS_VISIBLE,
                                    0, 0, 10, 10,
                                    hwnd,
                                    (HMENU)ID_SPLIT_RIGHT,
                                    m_instance,
                                    this);

    m_split_bottom = CreateWindowExA(0,
                                     kSplitterClass,
                                     "",
                                     WS_CHILD | WS_VISIBLE,
                                     0, 0, 10, 10,
                                     hwnd,
                                     (HMENU)ID_SPLIT_BOTTOM,
                                     m_instance,
                                     this);

    if (m_font) {
        SendMessageA(m_tree_search, WM_SETFONT, (WPARAM)m_font, TRUE);
        SendMessageA(m_tree, WM_SETFONT, (WPARAM)m_font, TRUE);
        SendMessageA(m_info_panel, WM_SETFONT, (WPARAM)m_font, TRUE);
        SendMessageA(m_inspector, WM_SETFONT, (WPARAM)m_font, TRUE);
        SendMessageA(m_inspector_edit, WM_SETFONT, (WPARAM)m_font, TRUE);
        SendMessageA(m_log, WM_SETFONT, (WPARAM)m_font, TRUE);
    }
    SendMessageA(m_tree_search, EM_LIMITTEXT, 128, 0);

    {
        LVCOLUMNA col;
        memset(&col, 0, sizeof(col));
        col.mask = LVCF_WIDTH | LVCF_TEXT | LVCF_SUBITEM;
        col.cx = 140;
        col.pszText = (LPSTR)"Property";
        ListView_InsertColumn(m_inspector, 0, &col);
        col.cx = 180;
        col.pszText = (LPSTR)"Value";
        ListView_InsertColumn(m_inspector, 1, &col);
        ListView_SetExtendedListViewStyle(m_inspector, LVS_EX_FULLROWSELECT | LVS_EX_GRIDLINES);
    }

    new_document();
    scan_ui_index(NULL);
    layout_children();

    m_dui_api = (const dui_api_v1*)dom_dui_win32_get_api(DUI_API_ABI_VERSION);
    if (m_dui_api && m_dui_api->create_context) {
        if (m_dui_api->create_context(&m_dui_ctx) == DUI_OK) {
            dui_window_desc_v1 desc;
            RECT rc;
            GetClientRect(m_preview_host, &rc);
            memset(&desc, 0, sizeof(desc));
            desc.abi_version = DUI_API_ABI_VERSION;
            desc.struct_size = (u32)sizeof(desc);
            desc.title = "Preview";
            desc.width = rc.right - rc.left;
            desc.height = rc.bottom - rc.top;
            desc.flags = DUI_WINDOW_FLAG_CHILD;
            desc.parent_hwnd = (void*)m_preview_host;
            if (m_dui_api->create_window(m_dui_ctx, &desc, &m_dui_win) == DUI_OK) {
                dom_abi_result q = m_dui_api->query_interface(DUI_IID_NATIVE_API_V1, (void**)&m_dui_native);
                if (q == 0 && m_dui_native && m_dui_win) {
                    m_dui_hwnd = (HWND)m_dui_native->get_native_window_handle(m_dui_win);
                    if (m_dui_hwnd) {
                        SetWindowSubclass(m_dui_hwnd, UiEditorApp::DuiSubclassProc, 1, (DWORD_PTR)this);
                        ShowWindow(m_dui_hwnd, SW_SHOW);
                        UpdateWindow(m_dui_hwnd);
                    }
                }
            }
        }
    }

    refresh_layout(1);
}

void UiEditorApp::on_destroy()
{
    KillTimer(m_hwnd, ID_PREVIEW_TIMER);
    shutdown();
}

void UiEditorApp::on_size(int w, int h)
{
    (void)w;
    (void)h;
    layout_children();
}

void UiEditorApp::layout_children()
{
    RECT rc;
    int width;
    int height;
    int top_h;
    int left_w;
    int right_w;
    int log_h;

    if (!m_hwnd) {
        return;
    }
    GetClientRect(m_hwnd, &rc);
    width = rc.right - rc.left;
    height = rc.bottom - rc.top;

    left_w = m_left_width;
    right_w = m_right_width;
    log_h = m_bottom_height;

    if (left_w < kMinPanelSize) left_w = kMinPanelSize;
    if (right_w < kMinPanelSize) right_w = kMinPanelSize;
    if (log_h < kMinPanelSize) log_h = kMinPanelSize;

    if (width < (left_w + right_w + kMinPreviewSize + kSplitterSize * 2)) {
        int avail = width - kMinPreviewSize - kSplitterSize * 2;
        if (avail < (kMinPanelSize * 2)) {
            left_w = kMinPanelSize;
            right_w = kMinPanelSize;
        } else {
            left_w = avail / 2;
            right_w = avail - left_w;
        }
    }

    if (height < (log_h + kMinPanelSize + kSplitterSize)) {
        log_h = kMinPanelSize;
    }

    top_h = height - log_h - kSplitterSize;
    if (top_h < kMinPanelSize) {
        top_h = kMinPanelSize;
        log_h = height - top_h - kSplitterSize;
        if (log_h < kMinPanelSize) {
            log_h = kMinPanelSize;
        }
    }

    MoveWindow(m_tree_search, 0, 0, left_w, kTreeSearchHeight, TRUE);
    MoveWindow(m_tree, 0, kTreeSearchHeight, left_w, top_h - kTreeSearchHeight, TRUE);
    MoveWindow(m_split_left, left_w, 0, kSplitterSize, top_h, TRUE);
    MoveWindow(m_preview_host, left_w + kSplitterSize, 0,
               width - left_w - right_w - kSplitterSize * 2, top_h, TRUE);
    MoveWindow(m_split_right, width - right_w - kSplitterSize, 0, kSplitterSize, top_h, TRUE);
    MoveWindow(m_info_panel, width - right_w, 0, right_w, kInfoPanelHeight, TRUE);
    MoveWindow(m_inspector, width - right_w, kInfoPanelHeight,
               right_w, top_h - kInspectorEditHeight - kInfoPanelHeight, TRUE);
    MoveWindow(m_inspector_edit, width - right_w, top_h - kInspectorEditHeight,
               right_w, kInspectorEditHeight, TRUE);
    MoveWindow(m_split_bottom, 0, top_h, width, kSplitterSize, TRUE);
    MoveWindow(m_log, 0, top_h + kSplitterSize, width, log_h, TRUE);

    update_preview_size();
    refresh_layout(1);
}

void UiEditorApp::update_preview_size()
{
    if (!m_preview_host) {
        return;
    }
    RECT rc;
    GetClientRect(m_preview_host, &rc);
    if (m_overlay) {
        MoveWindow(m_overlay, 0, 0, rc.right - rc.left, rc.bottom - rc.top, TRUE);
    }
    if (m_dui_hwnd) {
        MoveWindow(m_dui_hwnd, 0, 0, rc.right - rc.left, rc.bottom - rc.top, TRUE);
        ShowWindow(m_dui_hwnd, SW_SHOW);
    }
    if (m_overlay) {
        SetWindowPos(m_overlay, HWND_TOP, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE);
    }
}

void UiEditorApp::update_title()
{
    std::string title = "Dominium UI Editor";
    if (!m_current_path.empty()) {
        title += " - ";
        title += m_current_path;
    }
    if (m_dirty) {
        title += " *";
    }
    SetWindowTextA(m_hwnd, title.c_str());
}

void UiEditorApp::mark_dirty(int dirty)
{
    m_dirty = dirty ? 1 : 0;
    update_title();
}

bool UiEditorApp::scan_ui_index(const char* out_path)
{
    domui_diag diag;
    std::string repo_root = m_repo_root;
    std::vector<UiDiscoveryEntry> entries;
    std::string final_out = out_path ? out_path : "";

    if (repo_root.empty()) {
        repo_root = ui_find_repo_root("");
    }
    if (!ui_scan_repo_ui(repo_root, entries, &diag)) {
        log_append_diag(diag);
        log_info("ui scan: failed");
        return false;
    }
    if (final_out.empty()) {
        final_out = ui_default_index_path(repo_root);
    }
    if (!ui_write_ui_index_json(final_out, entries, &diag)) {
        log_append_diag(diag);
        log_info("ui scan: failed to write index");
        return false;
    }
    m_repo_root = repo_root;
    m_discovery = entries;
    log_append_diag(diag);
    log_info("ui scan: index updated");
    return true;
}

void UiEditorApp::update_info_panel()
{
    if (!m_info_panel) {
        return;
    }
    std::string tool = m_owning_tool.empty() ? "unknown" : m_owning_tool;
    std::string report = m_import_report_path.empty() ? "-" : m_import_report_path;
    std::string text = "Origin: ";
    text += ui_doc_origin_name(m_doc_origin);
    text += "\r\nTool: ";
    text += tool;
    text += "\r\nImport report: ";
    text += report;
    SetWindowTextA(m_info_panel, text.c_str());
}

void UiEditorApp::new_document()
{
    m_doc.clear();
    m_doc.meta.doc_name.set("ui_doc");
    domui_widget_id root = m_doc.create_widget(DOMUI_WIDGET_CONTAINER, 0u);
    if (root != 0u) {
        domui_widget* w = m_doc.find_by_id(root);
        if (w) {
            w->name.set("root");
            w->layout_mode = DOMUI_LAYOUT_ABSOLUTE;
            w->w = 400;
            w->h = 300;
        }
        m_selected_id = root;
    } else {
        m_selected_id = 0u;
    }
    m_current_path.clear();
    m_doc_origin = DOC_ORIGIN_CANONICAL;
    m_owning_tool.clear();
    m_import_report_path.clear();
    m_undo.clear();
    m_redo.clear();
    mark_dirty(0);
    rebuild_tree();
    rebuild_inspector();
    update_info_panel();
    refresh_layout(1);
}

bool UiEditorApp::confirm_discard()
{
    if (!m_dirty) {
        return true;
    }
    {
        int res = MessageBoxA(m_hwnd,
                              "Save changes before closing?",
                              "Dominium UI Editor",
                              MB_YESNOCANCEL | MB_ICONQUESTION);
        if (res == IDCANCEL) {
            return false;
        }
        if (res == IDYES) {
            if (!save_document()) {
                return false;
            }
        }
    }
    return true;
}

bool UiEditorApp::open_document()
{
    char path[MAX_PATH];
    OPENFILENAMEA ofn;
    if (!confirm_discard()) {
        return false;
    }
    memset(&ofn, 0, sizeof(ofn));
    memset(path, 0, sizeof(path));
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = m_hwnd;
    ofn.lpstrFile = path;
    ofn.nMaxFile = MAX_PATH;
    ofn.lpstrFilter = "UI Doc (*.tlv)\0*.tlv\0All Files\0*.*\0";
    ofn.Flags = OFN_PATHMUSTEXIST | OFN_FILEMUSTEXIST;
    if (!GetOpenFileNameA(&ofn)) {
        return false;
    }
    return load_document(path);
}

bool UiEditorApp::open_tool_ui_dialog()
{
    UiOpenToolDialogState state;
    std::string title = "Open Tool UI";
    HWND dlg = 0;
    RECT rc;

    if (!confirm_discard()) {
        return false;
    }

    if (m_discovery.empty()) {
        scan_ui_index(NULL);
    }
    if (m_discovery.empty()) {
        MessageBoxA(m_hwnd,
                    "No UI docs found. Refresh the UI index and try again.",
                    "UI Editor",
                    MB_OK | MB_ICONINFORMATION);
        return false;
    }

    state.app = this;
    state.entries = m_discovery;

    GetWindowRect(m_hwnd, &rc);
    dlg = CreateWindowExA(WS_EX_DLGMODALFRAME,
                          kOpenToolDialogClass,
                          title.c_str(),
                          WS_CAPTION | WS_SYSMENU | WS_POPUP | WS_VISIBLE,
                          rc.left + 80,
                          rc.top + 60,
                          820,
                          460,
                          m_hwnd,
                          NULL,
                          m_instance,
                          &state);
    if (!dlg) {
        return false;
    }
    EnableWindow(m_hwnd, FALSE);
    {
        MSG msg;
        while (IsWindow(dlg) && GetMessageA(&msg, NULL, 0, 0) > 0) {
            if (!IsDialogMessageA(dlg, &msg)) {
                TranslateMessage(&msg);
                DispatchMessageA(&msg);
            }
        }
    }
    EnableWindow(m_hwnd, TRUE);
    SetActiveWindow(m_hwnd);

    if (state.result && state.selected_index >= 0 &&
        state.selected_index < (int)state.entries.size()) {
        const UiDiscoveryEntry& entry = state.entries[state.selected_index];
        if (entry.is_canonical) {
            return load_document(entry.abs_path.c_str());
        }
        if (MessageBoxA(m_hwnd,
                        "Legacy UI selected. Import to canonical doc now?",
                        "UI Editor",
                        MB_YESNO | MB_ICONQUESTION) == IDYES) {
            return import_legacy_ui_path(entry.abs_path.c_str());
        }
    }
    return false;
}

bool UiEditorApp::import_legacy_ui_dialog()
{
    char path[MAX_PATH];
    OPENFILENAMEA ofn;
    memset(&ofn, 0, sizeof(ofn));
    if (!confirm_discard()) {
        return false;
    }
    path[0] = '\0';
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = m_hwnd;
    ofn.lpstrFile = path;
    ofn.nMaxFile = sizeof(path);
    ofn.lpstrFilter = "Legacy UI (*.tlv)\0*.tlv\0All Files\0*.*\0";
    ofn.Flags = OFN_PATHMUSTEXIST | OFN_FILEMUSTEXIST;
    if (!GetOpenFileNameA(&ofn)) {
        return false;
    }
    return import_legacy_ui_path(path);
}

bool UiEditorApp::import_legacy_ui_path(const char* legacy_path)
{
    domui_doc imported;
    domui_diag diag;
    domui_diag vdiag;
    domui_diag jdiag;
    std::map<domui_u32, domui_u32> id_map;
    std::string repo_root = m_repo_root;
    std::string rel_source;
    std::string tool;
    std::string default_dest;
    std::string dest_path;
    std::string dest_dir;
    std::string report_path;
    std::string report_json;

    if (!legacy_path || !legacy_path[0]) {
        return false;
    }
    if (!domui_doc_import_legacy_launcher_tlv(&imported, legacy_path, &diag)) {
        log_from_diag(diag);
        MessageBoxA(m_hwnd, "Legacy import failed. See log for details.", "UI Editor", MB_OK | MB_ICONERROR);
        return false;
    }

    if (repo_root.empty()) {
        repo_root = ui_find_repo_root("");
    }
    rel_source = ui_pretty_path(repo_root, legacy_path);
    tool = ui_guess_tool_from_path(rel_source);
    if (tool.empty()) {
        tool = "unknown";
    }

    if (!repo_root.empty()) {
        std::string tools_dir = ui_join_path(repo_root, "tools");
        std::string tool_dir = ui_join_path(tools_dir, tool);
        std::string ui_dir = ui_join_path(tool_dir, "ui");
        std::string doc_dir = ui_join_path(ui_dir, "doc");
        std::string file_name = tool + "_ui_doc.tlv";
        default_dest = ui_join_path(doc_dir, file_name);
    } else {
        std::string base = ui_path_basename(legacy_path);
        default_dest = base + "_ui_doc.tlv";
    }

    {
        char path_buf[MAX_PATH];
        OPENFILENAMEA ofn;
        memset(&ofn, 0, sizeof(ofn));
        memset(path_buf, 0, sizeof(path_buf));
        strncpy(path_buf, default_dest.c_str(), sizeof(path_buf) - 1u);
        ofn.lStructSize = sizeof(ofn);
        ofn.hwndOwner = m_hwnd;
        ofn.lpstrFile = path_buf;
        ofn.nMaxFile = sizeof(path_buf);
        ofn.lpstrFilter = "UI Doc (*.tlv)\0*.tlv\0All Files\0*.*\0";
        ofn.Flags = OFN_OVERWRITEPROMPT;
        if (!GetSaveFileNameA(&ofn)) {
            return false;
        }
        dest_path = path_buf;
    }

    dest_dir = ui_path_dir(dest_path);
    if (!dest_dir.empty()) {
        ui_ensure_dir_recursive(dest_dir);
    }

    if (imported.meta.doc_name.empty()) {
        std::string base = ui_path_basename(dest_path);
        imported.meta.doc_name.set(base.c_str());
    }

    if (!domui_doc_save_tlv(&imported, dest_path.c_str(), &diag)) {
        log_from_diag(diag);
        MessageBoxA(m_hwnd, "Failed to save imported UI doc.", "UI Editor", MB_OK | MB_ICONERROR);
        return false;
    }
    {
        std::string json_path = ui_replace_extension(dest_path, ".json");
        (void)domui_doc_save_json_mirror(&imported, json_path.c_str(), &jdiag);
    }

    ui_collect_import_id_map(imported, diag, id_map);
    report_path = ui_join_path(dest_dir, "import_report.json");
    report_json = ui_build_import_report_json(rel_source,
                                              ui_pretty_path(repo_root, dest_path),
                                              diag,
                                              id_map);
    (void)domui_atomic_write_file(report_path.c_str(),
                                  report_json.c_str(),
                                  report_json.size(),
                                  &diag);

    m_doc = imported;
    m_current_path = dest_path;
    m_repo_root = repo_root;
    m_doc_origin = DOC_ORIGIN_IMPORTED;
    m_owning_tool = tool;
    m_import_report_path = ui_pretty_path(repo_root, report_path);
    m_undo.clear();
    m_redo.clear();
    mark_dirty(0);
    rebuild_tree();
    rebuild_inspector();
    refresh_layout(1);
    domui_validate_doc(&m_doc, 0, &vdiag);
    log_clear();
    log_append_diag(diag);
    log_append_diag(jdiag);
    log_append_diag(vdiag);
    update_info_panel();

    MessageBoxA(m_hwnd, "Legacy UI import completed.", "UI Editor", MB_OK | MB_ICONINFORMATION);
    return true;
}

bool UiEditorApp::export_tool_ui()
{
    domui_diag vdiag;
    domui_diag sdiag;
    domui_diag jdiag;
    domui_diag cdiag;
    std::string doc_root;
    std::string doc_dir;
    std::string tlv_path;
    std::string export_path;
    std::string export_dir;
    std::string rel_export;
    int save_ok = 0;
    int json_ok = 0;
    int codegen_ok = 0;

    if (m_doc_origin == DOC_ORIGIN_LEGACY) {
        MessageBoxA(m_hwnd,
                    "Cannot export legacy UI docs. Import to canonical first.",
                    "UI Editor",
                    MB_OK | MB_ICONWARNING);
        return false;
    }
    if (m_current_path.empty()) {
        MessageBoxA(m_hwnd,
                    "Save the canonical UI doc before export.",
                    "UI Editor",
                    MB_OK | MB_ICONWARNING);
        return false;
    }

    domui_validate_doc(&m_doc, 0, &vdiag);
    if (vdiag.has_errors()) {
        log_from_diag(vdiag);
        MessageBoxA(m_hwnd,
                    "Export blocked: UI doc has validation errors.",
                    "UI Editor",
                    MB_OK | MB_ICONERROR);
        return false;
    }

    ui_resolve_doc_paths(m_current_path, &doc_root, &doc_dir, &tlv_path);
    if (doc_root.empty()) {
        MessageBoxA(m_hwnd,
                    "Export failed: unable to resolve UI doc root.",
                    "UI Editor",
                    MB_OK | MB_ICONERROR);
        return false;
    }
    export_path = ui_join_path(doc_root, "ui_doc.tlv");

    {
        char path_buf[MAX_PATH];
        OPENFILENAMEA ofn;
        memset(&ofn, 0, sizeof(ofn));
        memset(path_buf, 0, sizeof(path_buf));
        strncpy(path_buf, export_path.c_str(), sizeof(path_buf) - 1u);
        ofn.lStructSize = sizeof(ofn);
        ofn.hwndOwner = m_hwnd;
        ofn.lpstrFile = path_buf;
        ofn.nMaxFile = sizeof(path_buf);
        ofn.lpstrFilter = "UI Doc (*.tlv)\0*.tlv\0All Files\0*.*\0";
        ofn.Flags = OFN_OVERWRITEPROMPT;
        if (!GetSaveFileNameA(&ofn)) {
            return false;
        }
        export_path = path_buf;
    }

    rel_export = ui_pretty_path(m_repo_root, export_path);
    if (ui_path_is_canonical_doc(rel_export) && ui_path_is_file(export_path)) {
        if (MessageBoxA(m_hwnd,
                        "Export target is a canonical doc. Overwrite anyway?",
                        "UI Editor",
                        MB_YESNO | MB_ICONWARNING) != IDYES) {
            return false;
        }
    }

    export_dir = ui_path_dir(export_path);
    if (!export_dir.empty()) {
        ui_ensure_dir_recursive(export_dir);
    }

    save_ok = domui_doc_save_tlv(&m_doc, export_path.c_str(), &sdiag) ? 1 : 0;
    if (!save_ok) {
        log_from_diag(sdiag);
        MessageBoxA(m_hwnd, "Export failed while writing TLV.", "UI Editor", MB_OK | MB_ICONERROR);
        return false;
    }
    {
        std::string json_path = ui_replace_extension(export_path, ".json");
        json_ok = domui_doc_save_json_mirror(&m_doc, json_path.c_str(), &jdiag) ? 1 : 0;
    }
    codegen_ok = run_codegen(export_path.c_str(), &cdiag) ? 1 : 0;

    {
        size_t action_count = ui_count_action_keys(m_doc);
        int warn_count = (int)vdiag.warning_count() + (int)sdiag.warning_count() +
                         (int)jdiag.warning_count() + (int)cdiag.warning_count();
        std::string summary = "Export complete:\r\n";
        summary += "TLV written: ";
        summary += save_ok ? "OK" : "FAILED";
        summary += "\r\nJSON mirror: ";
        summary += json_ok ? "OK" : "FAILED";
        summary += "\r\nCodegen: ";
        if (codegen_ok) {
            summary += "OK (";
            summary += ui_u32_to_string((domui_u32)action_count);
            summary += " actions)";
        } else {
            summary += "FAILED";
        }
        if (warn_count > 0) {
            summary += "\r\nWarnings: ";
            summary += ui_int_to_string(warn_count);
        }
        MessageBoxA(m_hwnd,
                    summary.c_str(),
                    "UI Editor",
                    codegen_ok ? MB_OK | MB_ICONINFORMATION : MB_OK | MB_ICONWARNING);
    }

    log_clear();
    log_append_diag(vdiag);
    log_append_diag(sdiag);
    log_append_diag(jdiag);
    log_append_diag(cdiag);
    return codegen_ok ? true : false;
}

bool UiEditorApp::load_document(const char* path)
{
    domui_diag diag;
    domui_diag vdiag;
    if (!path || !path[0]) {
        return false;
    }
    if (!domui_doc_load_tlv(&m_doc, path, &diag)) {
        log_from_diag(diag);
        MessageBoxA(m_hwnd, "Failed to load UI doc.", "UI Editor", MB_OK | MB_ICONERROR);
        return false;
    }
    m_current_path = path;
    {
        std::string rel_path = m_current_path;
        if (m_repo_root.empty()) {
            m_repo_root = ui_find_repo_root("");
        }
        if (!m_repo_root.empty()) {
            rel_path = ui_make_relative_path(m_repo_root, m_current_path);
        }
        if (ui_is_legacy_name(ui_path_filename(m_current_path))) {
            m_doc_origin = DOC_ORIGIN_LEGACY;
        } else {
            m_doc_origin = DOC_ORIGIN_CANONICAL;
        }
        m_owning_tool = ui_guess_tool_from_path(rel_path);
        m_import_report_path.clear();
    }
    if (m_doc.meta.doc_name.empty()) {
        std::string base = ui_path_basename(m_current_path);
        m_doc.meta.doc_name.set(base.c_str());
    }
    m_undo.clear();
    m_redo.clear();
    mark_dirty(0);
    rebuild_tree();
    {
        std::vector<domui_widget_id> roots;
        m_doc.enumerate_children(0u, roots);
        if (!roots.empty()) {
            select_widget(roots[0], 0);
        } else {
            select_widget(0u, 0);
        }
    }
    rebuild_inspector();
    refresh_layout(1);
    domui_validate_doc(&m_doc, 0, &vdiag);
    log_clear();
    log_append_diag(diag);
    log_append_diag(vdiag);
    update_info_panel();
    if (m_doc_origin == DOC_ORIGIN_LEGACY) {
        MessageBoxA(m_hwnd,
                    "Legacy UI docs are read-only. Use Import Legacy UI to create a canonical doc.",
                    "UI Editor",
                    MB_OK | MB_ICONINFORMATION);
    }
    return true;
}

bool UiEditorApp::save_document()
{
    if (m_doc_origin == DOC_ORIGIN_LEGACY) {
        MessageBoxA(m_hwnd,
                    "Cannot save legacy UI docs. Use Import Legacy UI to create a canonical doc.",
                    "UI Editor",
                    MB_OK | MB_ICONWARNING);
        return false;
    }
    if (m_current_path.empty()) {
        return save_document_as();
    }
    return save_document_to(m_current_path.c_str());
}

bool UiEditorApp::save_document_as()
{
    if (m_doc_origin == DOC_ORIGIN_LEGACY) {
        MessageBoxA(m_hwnd,
                    "Cannot save legacy UI docs. Use Import Legacy UI to create a canonical doc.",
                    "UI Editor",
                    MB_OK | MB_ICONWARNING);
        return false;
    }
    char path[MAX_PATH];
    OPENFILENAMEA ofn;
    memset(&ofn, 0, sizeof(ofn));
    memset(path, 0, sizeof(path));
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = m_hwnd;
    ofn.lpstrFile = path;
    ofn.nMaxFile = MAX_PATH;
    ofn.lpstrFilter = "UI Doc (*.tlv)\0*.tlv\0All Files\0*.*\0";
    ofn.Flags = OFN_PATHMUSTEXIST | OFN_OVERWRITEPROMPT;
    if (!GetSaveFileNameA(&ofn)) {
        return false;
    }
    return save_document_to(path);
}

bool UiEditorApp::save_document_to(const char* path)
{
    domui_diag diag;
    domui_diag cdiag;
    int json_ok = 1;
    int write_json = 0;
    domui_diag* json_diag = NULL;
#if !defined(DOMUI_ENABLE_JSON_MIRROR) || DOMUI_ENABLE_JSON_MIRROR
    domui_diag jdiag;
    write_json = 1;
    json_diag = &jdiag;
#endif
    UiDocOutputPaths paths;
    if (!path || !path[0]) {
        return false;
    }
    ui_compute_doc_paths(path, 1, paths);
    if (!paths.doc_root.empty()) {
        ui_ensure_dir(paths.doc_root);
    }
    if (!paths.doc_dir.empty()) {
        ui_ensure_dir(paths.doc_dir);
    }
    {
        ui_ensure_dir(paths.gen_dir);
        ui_ensure_dir(paths.user_dir);
        ui_ensure_dir(paths.reg_dir);
    }
    if (!ui_save_doc_tlv_json(&m_doc,
                              paths,
                              NULL,
                              1,
                              write_json,
                              &diag,
                              json_diag,
                              &json_ok)) {
        log_from_diag(diag);
        MessageBoxA(m_hwnd, "Failed to save UI doc.", "UI Editor", MB_OK | MB_ICONERROR);
        return false;
    }
    m_current_path = paths.tlv_path;
    if (write_json && !json_ok) {
        log_clear();
        log_append_diag(diag);
#if !defined(DOMUI_ENABLE_JSON_MIRROR) || DOMUI_ENABLE_JSON_MIRROR
        log_append_diag(jdiag);
#endif
        MessageBoxA(m_hwnd, "Failed to save JSON mirror.", "UI Editor", MB_OK | MB_ICONWARNING);
        mark_dirty(1);
        return false;
    }
    mark_dirty(0);
    log_clear();
    log_append_diag(diag);
#if !defined(DOMUI_ENABLE_JSON_MIRROR) || DOMUI_ENABLE_JSON_MIRROR
    log_append_diag(jdiag);
#endif
    if (paths.tlv_path != path) {
        std::string msg = "save: " + paths.tlv_path;
        log_info(msg.c_str());
    }
    if (!run_codegen(paths.tlv_path.c_str(), &cdiag)) {
        log_append_diag(cdiag);
        MessageBoxA(m_hwnd, "Codegen failed. See log for details.", "UI Editor", MB_OK | MB_ICONWARNING);
        return true;
    }
    log_append_diag(cdiag);
    log_info("codegen: ok");
    return true;
}

bool UiEditorApp::run_codegen(const char* tlv_path, domui_diag* out_diag)
{
    domui_diag local;
    domui_diag* diag = out_diag ? out_diag : &local;
    std::string doc_root;
    ui_resolve_doc_paths(tlv_path ? tlv_path : "", &doc_root, NULL, NULL);
    std::string gen_dir = ui_join_path(doc_root, "gen");
    std::string user_dir = ui_join_path(doc_root, "user");
    std::string reg_dir = ui_join_path(doc_root, "registry");
    std::string reg_path = ui_join_path(reg_dir, "ui_actions_registry.json");
    return ui_run_codegen_with_paths(tlv_path,
                                     reg_path.c_str(),
                                     gen_dir.c_str(),
                                     user_dir.c_str(),
                                     m_doc.meta.doc_name.c_str(),
                                     diag);
}

void UiEditorApp::auto_fill_action_keys()
{
    ui_auto_fill_action_keys(m_doc);
}

void UiEditorApp::log_clear()
{
    SendMessageA(m_log, LB_RESETCONTENT, 0, 0);
}

void UiEditorApp::log_add(const char* text, domui_widget_id widget_id)
{
    int idx = (int)SendMessageA(m_log, LB_ADDSTRING, 0, (LPARAM)(text ? text : ""));
    SendMessageA(m_log, LB_SETITEMDATA, (WPARAM)idx, (LPARAM)widget_id);
}

void UiEditorApp::log_info(const char* text)
{
    log_add(text, 0u);
}

void UiEditorApp::log_from_diag(const domui_diag& diag)
{
    log_clear();
    log_append_diag(diag);
}

void UiEditorApp::log_append_diag(const domui_diag& diag)
{
    size_t i;
    for (i = 0u; i < diag.error_count(); ++i) {
        const domui_diag_item& item = diag.errors()[i];
        std::string msg = "error: ";
        msg += item.message.str();
        if (item.widget_id != 0u) {
            msg += " (widget ";
            msg += ui_u32_to_string(item.widget_id);
            msg += ")";
        }
        if (!item.context.empty()) {
            msg += " ";
            msg += item.context.str();
        }
        log_add(msg.c_str(), item.widget_id);
    }
    for (i = 0u; i < diag.warning_count(); ++i) {
        const domui_diag_item& item = diag.warnings()[i];
        std::string msg = "warn: ";
        msg += item.message.str();
        if (item.widget_id != 0u) {
            msg += " (widget ";
            msg += ui_u32_to_string(item.widget_id);
            msg += ")";
        }
        if (!item.context.empty()) {
            msg += " ";
            msg += item.context.str();
        }
        log_add(msg.c_str(), item.widget_id);
    }
}

void UiEditorApp::rebuild_tree()
{
    std::vector<domui_widget_id> roots;
    TreeView_DeleteAllItems(m_tree);
    m_tree_items.clear();
    m_doc.enumerate_children(0u, roots);
    for (size_t i = 0u; i < roots.size(); ++i) {
        rebuild_tree_item(roots[i], TVI_ROOT);
    }
    if (m_selected_id != 0u) {
        std::map<domui_widget_id, HTREEITEM>::iterator it = m_tree_items.find(m_selected_id);
        if (it != m_tree_items.end()) {
            TreeView_SelectItem(m_tree, it->second);
        }
    }
}

void UiEditorApp::rebuild_tree_item(domui_widget_id id, HTREEITEM parent)
{
    domui_widget* w = m_doc.find_by_id(id);
    if (!w) {
        return;
    }
    std::string label = w->name.str();
    if (label.empty()) {
        label = ui_widget_type_name(w->type);
    }
    label += " (";
    label += ui_widget_type_name(w->type);
    label += ") [";
    label += ui_u32_to_string(w->id);
    label += "]";
    TVINSERTSTRUCTA ins;
    memset(&ins, 0, sizeof(ins));
    ins.hParent = parent;
    ins.hInsertAfter = TVI_LAST;
    ins.item.mask = TVIF_TEXT | TVIF_PARAM;
    ins.item.pszText = (LPSTR)label.c_str();
    ins.item.lParam = (LPARAM)w->id;
    HTREEITEM item = TreeView_InsertItem(m_tree, &ins);
    m_tree_items[w->id] = item;

    std::vector<domui_widget_id> children;
    m_doc.enumerate_children(w->id, children);
    for (size_t i = 0u; i < children.size(); ++i) {
        rebuild_tree_item(children[i], item);
    }
    TreeView_Expand(m_tree, item, TVE_EXPAND);
}

void UiEditorApp::select_widget(domui_widget_id id, int from_tree)
{
    if (id == m_selected_id) {
        return;
    }
    if (id != 0u && !m_doc.find_by_id(id)) {
        return;
    }
    m_selected_id = id;
    if (!from_tree && id != 0u) {
        std::map<domui_widget_id, HTREEITEM>::iterator it = m_tree_items.find(id);
        if (it != m_tree_items.end()) {
            TreeView_SelectItem(m_tree, it->second);
            TreeView_EnsureVisible(m_tree, it->second);
        }
    }
    rebuild_inspector();
    InvalidateRect(m_overlay, NULL, TRUE);
}

void UiEditorApp::search_tree(const char* text)
{
    if (!text || !text[0]) {
        return;
    }
    domui_widget_id match = find_search_match(text);
    if (match != 0u) {
        select_widget(match, 0);
    }
}

domui_widget_id UiEditorApp::find_search_match(const std::string& needle) const
{
    if (needle.empty()) {
        return 0u;
    }
    domui_u32 id_val = 0u;
    if (ui_parse_u32(needle, &id_val)) {
        if (m_doc.find_by_id(id_val)) {
            return id_val;
        }
    }
    std::string q = ui_to_lower(needle);
    std::vector<domui_widget_id> order;
    m_doc.canonical_widget_order(order);
    for (size_t i = 0u; i < order.size(); ++i) {
        const domui_widget* w = m_doc.find_by_id(order[i]);
        if (!w) {
            continue;
        }
        std::string name = ui_to_lower(w->name.str());
        std::string type = ui_to_lower(ui_widget_type_name(w->type));
        std::string id = ui_u32_to_string(w->id);
        if (name.find(q) != std::string::npos ||
            type.find(q) != std::string::npos ||
            id.find(q) != std::string::npos) {
            return w->id;
        }
    }
    return 0u;
}

void UiEditorApp::rebuild_inspector()
{
    ListView_DeleteAllItems(m_inspector);
    m_inspector_rows.clear();
    m_inspector_edit_row = -1;
    if (m_selected_id == 0u) {
        EnableWindow(m_inspector_edit, FALSE);
        SetWindowTextA(m_inspector_edit, "");
        return;
    }
    domui_widget* w = m_doc.find_by_id(m_selected_id);
    if (!w) {
        return;
    }

    {
        InspectorRow row;
        row.type = ROW_CATEGORY;
        row.key = "Identity";
        row.editable = 0;
        m_inspector_rows.push_back(row);
    }

    {
        InspectorRow row;
        row.type = ROW_FIELD;
        row.field = FIELD_ID;
        row.widget_id = w->id;
        row.editable = 0;
        m_inspector_rows.push_back(row);
    }
    {
        InspectorRow row;
        row.type = ROW_FIELD;
        row.field = FIELD_NAME;
        row.widget_id = w->id;
        row.editable = 1;
        m_inspector_rows.push_back(row);
    }
    {
        InspectorRow row;
        row.type = ROW_FIELD;
        row.field = FIELD_TYPE;
        row.widget_id = w->id;
        row.editable = 0;
        m_inspector_rows.push_back(row);
    }

    {
        InspectorRow row;
        row.type = ROW_CATEGORY;
        row.key = "Layout";
        row.editable = 0;
        m_inspector_rows.push_back(row);
    }
    {
        InspectorRow row;
        row.type = ROW_FIELD;
        row.field = FIELD_X;
        row.widget_id = w->id;
        row.editable = 1;
        m_inspector_rows.push_back(row);
        row.field = FIELD_Y;
        m_inspector_rows.push_back(row);
        row.field = FIELD_W;
        m_inspector_rows.push_back(row);
        row.field = FIELD_H;
        m_inspector_rows.push_back(row);
    }
    {
        InspectorRow row;
        row.type = ROW_FIELD;
        row.field = FIELD_LAYOUT_MODE;
        row.widget_id = w->id;
        row.editable = 1;
        m_inspector_rows.push_back(row);
        row.field = FIELD_DOCK;
        m_inspector_rows.push_back(row);
        row.field = FIELD_ANCHORS;
        m_inspector_rows.push_back(row);
    }
    {
        InspectorRow row;
        row.type = ROW_FIELD;
        row.field = FIELD_MARGIN_LEFT;
        row.widget_id = w->id;
        row.editable = 1;
        m_inspector_rows.push_back(row);
        row.field = FIELD_MARGIN_RIGHT;
        m_inspector_rows.push_back(row);
        row.field = FIELD_MARGIN_TOP;
        m_inspector_rows.push_back(row);
        row.field = FIELD_MARGIN_BOTTOM;
        m_inspector_rows.push_back(row);
    }
    {
        InspectorRow row;
        row.type = ROW_FIELD;
        row.field = FIELD_PADDING_LEFT;
        row.widget_id = w->id;
        row.editable = 1;
        m_inspector_rows.push_back(row);
        row.field = FIELD_PADDING_RIGHT;
        m_inspector_rows.push_back(row);
        row.field = FIELD_PADDING_TOP;
        m_inspector_rows.push_back(row);
        row.field = FIELD_PADDING_BOTTOM;
        m_inspector_rows.push_back(row);
    }
    {
        InspectorRow row;
        row.type = ROW_FIELD;
        row.field = FIELD_MIN_W;
        row.widget_id = w->id;
        row.editable = 1;
        m_inspector_rows.push_back(row);
        row.field = FIELD_MIN_H;
        m_inspector_rows.push_back(row);
        row.field = FIELD_MAX_W;
        m_inspector_rows.push_back(row);
        row.field = FIELD_MAX_H;
        m_inspector_rows.push_back(row);
    }

    {
        InspectorRow row;
        row.type = ROW_CATEGORY;
        row.key = "Props";
        row.editable = 0;
        m_inspector_rows.push_back(row);
    }
    {
        const domui_props::list_type& props = w->props.entries();
        for (size_t i = 0u; i < props.size(); ++i) {
            InspectorRow row;
            row.type = ROW_PROP;
            row.key = props[i].key.str();
            row.prop_type = props[i].value.type;
            row.widget_id = w->id;
            row.editable = 1;
            m_inspector_rows.push_back(row);
        }
    }

    {
        InspectorRow row;
        row.type = ROW_CATEGORY;
        row.key = "Events";
        row.editable = 0;
        m_inspector_rows.push_back(row);
    }
    {
        std::vector<std::string> events;
        const domui_events::list_type& ev = w->events.entries();
        for (size_t i = 0u; i < ev.size(); ++i) {
            events.push_back(ev[i].event_name.str());
        }
        if (w->type == DOMUI_WIDGET_BUTTON || w->type == DOMUI_WIDGET_CHECKBOX) {
            events.push_back("on_click");
        } else if (w->type == DOMUI_WIDGET_EDIT) {
            events.push_back("on_change");
            events.push_back("on_submit");
        } else if (w->type == DOMUI_WIDGET_LISTBOX) {
            events.push_back("on_change");
            events.push_back("on_submit");
        } else if (w->type == DOMUI_WIDGET_SCROLLPANEL) {
            events.push_back("on_scroll");
        } else if (w->type == DOMUI_WIDGET_TABS) {
            events.push_back("on_tab_change");
        }
        std::sort(events.begin(), events.end());
        events.erase(std::unique(events.begin(), events.end()), events.end());
        for (size_t i = 0u; i < events.size(); ++i) {
            InspectorRow row;
            row.type = ROW_EVENT;
            row.key = events[i];
            row.widget_id = w->id;
            row.editable = 1;
            m_inspector_rows.push_back(row);
        }
    }

    for (size_t i = 0u; i < m_inspector_rows.size(); ++i) {
        const InspectorRow& row = m_inspector_rows[i];
        std::string label;
        std::string value;
        if (row.type == ROW_CATEGORY) {
            label = "[" + row.key + "]";
        } else if (row.type == ROW_FIELD) {
            switch (row.field) {
            case FIELD_ID: label = "id"; value = ui_u32_to_string(w->id); break;
            case FIELD_NAME: label = "name"; value = w->name.str(); break;
            case FIELD_TYPE: label = "type"; value = ui_widget_type_name(w->type); break;
            case FIELD_X: label = "x"; value = ui_int_to_string(w->x); break;
            case FIELD_Y: label = "y"; value = ui_int_to_string(w->y); break;
            case FIELD_W: label = "w"; value = ui_int_to_string(w->w); break;
            case FIELD_H: label = "h"; value = ui_int_to_string(w->h); break;
            case FIELD_LAYOUT_MODE: label = "layout_mode"; value = ui_layout_mode_name(w->layout_mode); break;
            case FIELD_DOCK: label = "dock"; value = ui_dock_mode_name(w->dock); break;
            case FIELD_ANCHORS: label = "anchors"; value = ui_anchor_mask_to_string(w->anchors); break;
            case FIELD_MARGIN_LEFT: label = "margin.left"; value = ui_int_to_string(w->margin.left); break;
            case FIELD_MARGIN_RIGHT: label = "margin.right"; value = ui_int_to_string(w->margin.right); break;
            case FIELD_MARGIN_TOP: label = "margin.top"; value = ui_int_to_string(w->margin.top); break;
            case FIELD_MARGIN_BOTTOM: label = "margin.bottom"; value = ui_int_to_string(w->margin.bottom); break;
            case FIELD_PADDING_LEFT: label = "padding.left"; value = ui_int_to_string(w->padding.left); break;
            case FIELD_PADDING_RIGHT: label = "padding.right"; value = ui_int_to_string(w->padding.right); break;
            case FIELD_PADDING_TOP: label = "padding.top"; value = ui_int_to_string(w->padding.top); break;
            case FIELD_PADDING_BOTTOM: label = "padding.bottom"; value = ui_int_to_string(w->padding.bottom); break;
            case FIELD_MIN_W: label = "min_w"; value = ui_int_to_string(w->min_w); break;
            case FIELD_MIN_H: label = "min_h"; value = ui_int_to_string(w->min_h); break;
            case FIELD_MAX_W: label = "max_w"; value = ui_int_to_string(w->max_w); break;
            case FIELD_MAX_H: label = "max_h"; value = ui_int_to_string(w->max_h); break;
            default: break;
            }
        } else if (row.type == ROW_PROP) {
            domui_value v;
            label = row.key;
            if (w->props.get(row.key.c_str(), &v)) {
                switch (v.type) {
                case DOMUI_VALUE_INT: value = ui_int_to_string(v.v_int); break;
                case DOMUI_VALUE_UINT: value = ui_u32_to_string(v.v_uint); break;
                case DOMUI_VALUE_BOOL: value = ui_bool_to_string(v.v_bool); break;
                case DOMUI_VALUE_STRING: value = v.v_string.str(); break;
                case DOMUI_VALUE_VEC2I:
                    value = ui_int_to_string(v.v_vec2i.x) + "," + ui_int_to_string(v.v_vec2i.y);
                    break;
                case DOMUI_VALUE_RECTI:
                    value = ui_int_to_string(v.v_recti.x) + "," +
                            ui_int_to_string(v.v_recti.y) + "," +
                            ui_int_to_string(v.v_recti.w) + "," +
                            ui_int_to_string(v.v_recti.h);
                    break;
                default:
                    break;
                }
            }
        } else if (row.type == ROW_EVENT) {
            domui_string action;
            label = row.key;
            if (w->events.get(row.key.c_str(), &action)) {
                value = action.str();
            } else {
                value = "";
            }
        }

        LVITEMA item;
        memset(&item, 0, sizeof(item));
        item.mask = LVIF_TEXT | LVIF_PARAM;
        item.iItem = (int)i;
        item.pszText = (LPSTR)label.c_str();
        item.lParam = (LPARAM)i;
        ListView_InsertItem(m_inspector, &item);
        ListView_SetItemText(m_inspector, (int)i, 1, (LPSTR)value.c_str());
    }

    if (!m_inspector_rows.empty()) {
        ListView_SetItemState(m_inspector, 0, LVIS_SELECTED | LVIS_FOCUSED, LVIS_SELECTED | LVIS_FOCUSED);
        m_inspector_edit_row = 0;
        refresh_inspector_edit();
    }
}

void UiEditorApp::refresh_inspector_edit()
{
    if (m_inspector_edit_row < 0 || m_inspector_edit_row >= (int)m_inspector_rows.size()) {
        EnableWindow(m_inspector_edit, FALSE);
        SetWindowTextA(m_inspector_edit, "");
        return;
    }
    const InspectorRow& row = m_inspector_rows[m_inspector_edit_row];
    EnableWindow(m_inspector_edit, row.editable ? TRUE : FALSE);
    if (!row.editable) {
        SetWindowTextA(m_inspector_edit, "");
        return;
    }
    {
        char buf[512];
        buf[0] = '\0';
        ListView_GetItemText(m_inspector, m_inspector_edit_row, 1, buf, sizeof(buf));
        SetWindowTextA(m_inspector_edit, buf);
        SendMessageA(m_inspector_edit, EM_SETSEL, 0, -1);
    }
}

void UiEditorApp::push_command(const char* label, const domui_doc& before)
{
    EditorCommand cmd;
    cmd.before = before;
    cmd.after = m_doc;
    cmd.label = label ? label : "";
    m_undo.push_back(cmd);
    if ((int)m_undo.size() > kUndoLimit) {
        m_undo.erase(m_undo.begin());
    }
    m_redo.clear();
    mark_dirty(1);
}

void UiEditorApp::undo()
{
    if (m_undo.empty()) {
        return;
    }
    EditorCommand cmd = m_undo.back();
    m_undo.pop_back();
    m_redo.push_back(cmd);
    m_doc = cmd.before;
    rebuild_tree();
    if (!m_doc.find_by_id(m_selected_id)) {
        std::vector<domui_widget_id> roots;
        m_doc.enumerate_children(0u, roots);
        m_selected_id = roots.empty() ? 0u : roots[0];
    }
    rebuild_inspector();
    refresh_layout(1);
    mark_dirty(1);
}

void UiEditorApp::redo()
{
    if (m_redo.empty()) {
        return;
    }
    EditorCommand cmd = m_redo.back();
    m_redo.pop_back();
    m_undo.push_back(cmd);
    m_doc = cmd.after;
    rebuild_tree();
    if (!m_doc.find_by_id(m_selected_id)) {
        std::vector<domui_widget_id> roots;
        m_doc.enumerate_children(0u, roots);
        m_selected_id = roots.empty() ? 0u : roots[0];
    }
    rebuild_inspector();
    refresh_layout(1);
    mark_dirty(1);
}

void UiEditorApp::ensure_default_props(domui_widget* w)
{
    if (!w) {
        return;
    }
    if (w->type == DOMUI_WIDGET_SPLITTER) {
        if (!w->props.has("splitter.orientation")) {
            w->props.set("splitter.orientation", domui_value_string(domui_string("v")));
        }
        if (!w->props.has("splitter.pos")) {
            w->props.set("splitter.pos", domui_value_int(-1));
        }
        if (!w->props.has("splitter.thickness")) {
            w->props.set("splitter.thickness", domui_value_int(4));
        }
        if (!w->props.has("splitter.min_a")) {
            w->props.set("splitter.min_a", domui_value_int(0));
        }
        if (!w->props.has("splitter.min_b")) {
            w->props.set("splitter.min_b", domui_value_int(0));
        }
    } else if (w->type == DOMUI_WIDGET_TABS) {
        if (!w->props.has("tabs.selected_index")) {
            w->props.set("tabs.selected_index", domui_value_int(0));
        }
        if (!w->props.has("tabs.placement")) {
            w->props.set("tabs.placement", domui_value_string(domui_string("top")));
        }
    } else if (w->type == DOMUI_WIDGET_TAB_PAGE) {
        if (!w->props.has("tab.title")) {
            w->props.set("tab.title", domui_value_string(domui_string("")));
        }
        if (!w->props.has("tab.enabled")) {
            w->props.set("tab.enabled", domui_value_bool(1));
        }
    } else if (w->type == DOMUI_WIDGET_SCROLLPANEL) {
        if (!w->props.has("scroll.h_enabled")) {
            w->props.set("scroll.h_enabled", domui_value_bool(1));
        }
        if (!w->props.has("scroll.v_enabled")) {
            w->props.set("scroll.v_enabled", domui_value_bool(1));
        }
        if (!w->props.has("scroll.x")) {
            w->props.set("scroll.x", domui_value_int(0));
        }
        if (!w->props.has("scroll.y")) {
            w->props.set("scroll.y", domui_value_int(0));
        }
    }
}

domui_widget_id UiEditorApp::add_widget(domui_widget_type type, domui_widget_id parent_id)
{
    domui_widget_id id = m_doc.create_widget(type, parent_id);
    domui_widget* w = m_doc.find_by_id(id);
    if (!w) {
        return 0u;
    }
    {
        std::string base = ui_to_lower(ui_widget_type_name(type));
        base += "_";
        base += ui_u32_to_string(id);
        w->name.set(base.c_str());
    }
    w->layout_mode = DOMUI_LAYOUT_ABSOLUTE;
    w->dock = DOMUI_DOCK_NONE;
    w->anchors = 0u;
    w->x = 8;
    w->y = 8;
    w->w = 160;
    w->h = 24;
    if (type == DOMUI_WIDGET_CONTAINER) {
        w->w = 240;
        w->h = 180;
    } else if (type == DOMUI_WIDGET_LISTBOX) {
        w->w = 200;
        w->h = 120;
    } else if (type == DOMUI_WIDGET_EDIT) {
        w->w = 200;
        w->h = 24;
    } else if (type == DOMUI_WIDGET_BUTTON) {
        w->w = 120;
        w->h = 26;
    } else if (type == DOMUI_WIDGET_TABS) {
        w->w = 260;
        w->h = 200;
    } else if (type == DOMUI_WIDGET_TAB_PAGE) {
        w->w = 240;
        w->h = 160;
    } else if (type == DOMUI_WIDGET_SPLITTER) {
        w->w = 260;
        w->h = 200;
    } else if (type == DOMUI_WIDGET_SCROLLPANEL) {
        w->w = 260;
        w->h = 200;
    }
    ensure_default_props(w);

    if (type == DOMUI_WIDGET_TABS) {
        domui_widget_id page = m_doc.create_widget(DOMUI_WIDGET_TAB_PAGE, id);
        domui_widget* pw = m_doc.find_by_id(page);
        if (pw) {
            pw->name.set("tab_page");
            pw->w = 220;
            pw->h = 160;
            ensure_default_props(pw);
            pw->props.set("tab.title", domui_value_string(domui_string("Tab 1")));
        }
    } else if (type == DOMUI_WIDGET_SPLITTER) {
        domui_widget_id a = m_doc.create_widget(DOMUI_WIDGET_CONTAINER, id);
        domui_widget_id b = m_doc.create_widget(DOMUI_WIDGET_CONTAINER, id);
        domui_widget* wa = m_doc.find_by_id(a);
        domui_widget* wb = m_doc.find_by_id(b);
        if (wa) {
            wa->name.set("pane_a");
            wa->w = 120;
            wa->h = 120;
        }
        if (wb) {
            wb->name.set("pane_b");
            wb->w = 120;
            wb->h = 120;
        }
    } else if (type == DOMUI_WIDGET_SCROLLPANEL) {
        domui_widget_id c = m_doc.create_widget(DOMUI_WIDGET_CONTAINER, id);
        domui_widget* wc = m_doc.find_by_id(c);
        if (wc) {
            wc->name.set("content");
            wc->w = 300;
            wc->h = 200;
        }
    }
    return id;
}

void UiEditorApp::delete_widget(domui_widget_id id)
{
    if (id == 0u) {
        return;
    }
    domui_widget* w = m_doc.find_by_id(id);
    domui_widget_id parent = w ? w->parent_id : 0u;
    m_doc.delete_widget(id);
    if (parent != 0u) {
        select_widget(parent, 0);
    } else {
        m_selected_id = 0u;
    }
    rebuild_tree();
    rebuild_inspector();
    refresh_layout(1);
}

domui_u32 UiEditorApp::next_z_for_parent(domui_widget_id parent_id)
{
    std::vector<domui_widget_id> children;
    domui_u32 next_z = 0u;
    m_doc.enumerate_children(parent_id, children);
    for (size_t i = 0u; i < children.size(); ++i) {
        domui_widget* w = m_doc.find_by_id(children[i]);
        if (w && (w->z_order >= next_z)) {
            next_z = w->z_order + 1u;
        }
    }
    return next_z;
}

domui_layout_rect UiEditorApp::get_layout_rect(domui_widget_id id) const
{
    std::map<domui_widget_id, domui_layout_rect>::const_iterator it = m_layout_map.find(id);
    if (it != m_layout_map.end()) {
        return it->second;
    }
    domui_layout_rect r;
    r.x = 0;
    r.y = 0;
    r.w = 0;
    r.h = 0;
    return r;
}

domui_layout_rect UiEditorApp::get_parent_content_rect(domui_widget_id id) const
{
    domui_layout_rect parent = m_root_rect;
    const domui_widget* w = m_doc.find_by_id(id);
    if (!w) {
        return parent;
    }
    if (w->parent_id != 0u) {
        parent = get_layout_rect(w->parent_id);
        const domui_widget* pw = m_doc.find_by_id(w->parent_id);
        if (pw) {
            parent.x += pw->padding.left;
            parent.y += pw->padding.top;
            parent.w -= (pw->padding.left + pw->padding.right);
            parent.h -= (pw->padding.top + pw->padding.bottom);
        }
    }
    return parent;
}

int UiEditorApp::apply_rect_to_widget(domui_widget* w, const domui_layout_rect& rect)
{
    if (!w) {
        return 0;
    }
    {
        domui_layout_rect parent = get_parent_content_rect(w->id);
        if (w->dock != DOMUI_DOCK_NONE) {
            if (w->dock == DOMUI_DOCK_LEFT || w->dock == DOMUI_DOCK_RIGHT) {
                w->w = rect.w;
                return 1;
            }
            if (w->dock == DOMUI_DOCK_TOP || w->dock == DOMUI_DOCK_BOTTOM) {
                w->h = rect.h;
                return 1;
            }
            if (w->dock == DOMUI_DOCK_FILL) {
                w->w = rect.w;
                w->h = rect.h;
                return 1;
            }
        }

        if (w->anchors != 0u) {
            int anchor_l = (w->anchors & DOMUI_ANCHOR_L) != 0u;
            int anchor_r = (w->anchors & DOMUI_ANCHOR_R) != 0u;
            int anchor_t = (w->anchors & DOMUI_ANCHOR_T) != 0u;
            int anchor_b = (w->anchors & DOMUI_ANCHOR_B) != 0u;

            if (anchor_l && anchor_r) {
                int left = rect.x - parent.x;
                int right = (parent.x + parent.w) - (rect.x + rect.w);
                w->x = left - w->margin.left;
                w->w = right - w->margin.right;
            } else if (anchor_l) {
                w->x = rect.x - parent.x - w->margin.left;
                w->w = rect.w;
            } else if (anchor_r) {
                int right = (parent.x + parent.w) - (rect.x + rect.w);
                w->x = right - w->margin.right;
                w->w = rect.w;
            } else {
                w->x = rect.x - parent.x - w->margin.left;
                w->w = rect.w;
            }

            if (anchor_t && anchor_b) {
                int top = rect.y - parent.y;
                int bottom = (parent.y + parent.h) - (rect.y + rect.h);
                w->y = top - w->margin.top;
                w->h = bottom - w->margin.bottom;
            } else if (anchor_t) {
                w->y = rect.y - parent.y - w->margin.top;
                w->h = rect.h;
            } else if (anchor_b) {
                int bottom = (parent.y + parent.h) - (rect.y + rect.h);
                w->y = bottom - w->margin.bottom;
                w->h = rect.h;
            } else {
                w->y = rect.y - parent.y - w->margin.top;
                w->h = rect.h;
            }
            return 1;
        }

        w->x = rect.x - parent.x - w->margin.left;
        w->y = rect.y - parent.y - w->margin.top;
        w->w = rect.w;
        w->h = rect.h;
    }
    return 1;
}

void UiEditorApp::overlay_paint(HDC hdc)
{
    RECT client;
    GetClientRect(m_overlay, &client);
    if (m_overlay_layered) {
        HBRUSH clear_brush = CreateSolidBrush(kOverlayClearColor);
        FillRect(hdc, &client, clear_brush);
        DeleteObject(clear_brush);
    } else {
        int client_w = client.right - client.left;
        int client_h = client.bottom - client.top;
        if (client_w > 0 && client_h > 0) {
            if (m_dui_hwnd) {
                SendMessageA(m_dui_hwnd,
                             WM_PRINT,
                             (WPARAM)hdc,
                             (LPARAM)(PRF_CLIENT | PRF_CHILDREN | PRF_ERASEBKGND));
            } else {
                FillRect(hdc, &client, (HBRUSH)(COLOR_WINDOW + 1));
            }
        }
    }
    if (m_selected_id == 0u) {
        return;
    }
    domui_layout_rect r = get_layout_rect(m_selected_id);
    if (r.w <= 0 || r.h <= 0) {
        return;
    }
    HPEN pen = CreatePen(PS_SOLID, 1, RGB(0, 120, 215));
    HBRUSH brush = (HBRUSH)GetStockObject(NULL_BRUSH);
    HBRUSH handle_brush = CreateSolidBrush(RGB(0, 120, 215));
    RECT rc = ui_make_rect(r.x, r.y, r.x + r.w, r.y + r.h);
    SelectObject(hdc, pen);
    SelectObject(hdc, brush);
    Rectangle(hdc, rc.left, rc.top, rc.right, rc.bottom);

    {
        int hs = kHandleSize;
        RECT handles[8];
        handles[0] = ui_make_rect(rc.left - hs, rc.top - hs, rc.left + hs, rc.top + hs);
        handles[1] = ui_make_rect(rc.right - hs, rc.top - hs, rc.right + hs, rc.top + hs);
        handles[2] = ui_make_rect(rc.left - hs, rc.bottom - hs, rc.left + hs, rc.bottom + hs);
        handles[3] = ui_make_rect(rc.right - hs, rc.bottom - hs, rc.right + hs, rc.bottom + hs);
        handles[4] = ui_make_rect((rc.left + rc.right) / 2 - hs, rc.top - hs, (rc.left + rc.right) / 2 + hs, rc.top + hs);
        handles[5] = ui_make_rect((rc.left + rc.right) / 2 - hs, rc.bottom - hs, (rc.left + rc.right) / 2 + hs, rc.bottom + hs);
        handles[6] = ui_make_rect(rc.left - hs, (rc.top + rc.bottom) / 2 - hs, rc.left + hs, (rc.top + rc.bottom) / 2 + hs);
        handles[7] = ui_make_rect(rc.right - hs, (rc.top + rc.bottom) / 2 - hs, rc.right + hs, (rc.top + rc.bottom) / 2 + hs);
        for (int i = 0; i < 8; ++i) {
            FillRect(hdc, &handles[i], handle_brush);
        }
    }
    DeleteObject(handle_brush);
    DeleteObject(pen);
}

int UiEditorApp::overlay_should_capture(const POINT& pt) const
{
    if (m_selected_id == 0u) {
        return 0;
    }
    domui_layout_rect r = get_layout_rect(m_selected_id);
    if (r.w <= 0 || r.h <= 0) {
        return 0;
    }
    RECT rc = ui_make_rect(r.x, r.y, r.x + r.w, r.y + r.h);
    int hs = kHandleSize;
    RECT handles[8];
    handles[0] = ui_make_rect(rc.left - hs, rc.top - hs, rc.left + hs, rc.top + hs);
    handles[1] = ui_make_rect(rc.right - hs, rc.top - hs, rc.right + hs, rc.top + hs);
    handles[2] = ui_make_rect(rc.left - hs, rc.bottom - hs, rc.left + hs, rc.bottom + hs);
    handles[3] = ui_make_rect(rc.right - hs, rc.bottom - hs, rc.right + hs, rc.bottom + hs);
    handles[4] = ui_make_rect((rc.left + rc.right) / 2 - hs, rc.top - hs, (rc.left + rc.right) / 2 + hs, rc.top + hs);
    handles[5] = ui_make_rect((rc.left + rc.right) / 2 - hs, rc.bottom - hs, (rc.left + rc.right) / 2 + hs, rc.bottom + hs);
    handles[6] = ui_make_rect(rc.left - hs, (rc.top + rc.bottom) / 2 - hs, rc.left + hs, (rc.top + rc.bottom) / 2 + hs);
    handles[7] = ui_make_rect(rc.right - hs, (rc.top + rc.bottom) / 2 - hs, rc.right + hs, (rc.top + rc.bottom) / 2 + hs);
    for (int i = 0; i < 8; ++i) {
        if (PtInRect(&handles[i], pt)) {
            return 1;
        }
    }
    {
        const int border = 2;
        if (pt.x >= rc.left - border && pt.x <= rc.right + border &&
            pt.y >= rc.top - border && pt.y <= rc.bottom + border) {
            if (pt.x <= rc.left + border || pt.x >= rc.right - border ||
                pt.y <= rc.top + border || pt.y >= rc.bottom - border) {
                return 1;
            }
        }
    }
    return 0;
}

int UiEditorApp::overlay_hit_test(const POINT& pt, domui_layout_rect* out_rect, DragMode* out_handle)
{
    domui_widget_id hit = 0u;
    domui_layout_rect hit_rect;
    if (m_dui_hwnd) {
        POINT local = pt;
        HWND child = ChildWindowFromPointEx(m_dui_hwnd,
                                            local,
                                            CWP_SKIPINVISIBLE | CWP_SKIPDISABLED | CWP_SKIPTRANSPARENT);
        if (child && child != m_dui_hwnd) {
            int ctrl_id = GetDlgCtrlID(child);
            if (ctrl_id > 0) {
                hit = (domui_widget_id)ctrl_id;
                hit_rect = get_layout_rect(hit);
            }
        }
    }
    if (hit == 0u) {
    for (size_t i = 0u; i < m_layout_order.size(); ++i) {
        domui_layout_rect r = get_layout_rect(m_layout_order[i]);
        if (r.w <= 0 || r.h <= 0) {
            continue;
        }
        if (pt.x >= r.x && pt.x <= (r.x + r.w) &&
            pt.y >= r.y && pt.y <= (r.y + r.h)) {
            hit = m_layout_order[i];
            hit_rect = r;
        }
    }
    }
    if (hit == 0u) {
        return 0;
    }
    if (out_rect) {
        *out_rect = hit_rect;
    }
    if (out_handle) {
        DragMode handle = DRAG_MOVE;
        int hs = kHandleSize;
        RECT rc = ui_make_rect(hit_rect.x, hit_rect.y, hit_rect.x + hit_rect.w, hit_rect.y + hit_rect.h);
        RECT h;
        h = ui_make_rect(rc.left - hs, rc.top - hs, rc.left + hs, rc.top + hs);
        if (PtInRect(&h, pt)) handle = DRAG_NW;
        h = ui_make_rect(rc.right - hs, rc.top - hs, rc.right + hs, rc.top + hs);
        if (PtInRect(&h, pt)) handle = DRAG_NE;
        h = ui_make_rect(rc.left - hs, rc.bottom - hs, rc.left + hs, rc.bottom + hs);
        if (PtInRect(&h, pt)) handle = DRAG_SW;
        h = ui_make_rect(rc.right - hs, rc.bottom - hs, rc.right + hs, rc.bottom + hs);
        if (PtInRect(&h, pt)) handle = DRAG_SE;
        h = ui_make_rect((rc.left + rc.right) / 2 - hs, rc.top - hs, (rc.left + rc.right) / 2 + hs, rc.top + hs);
        if (PtInRect(&h, pt)) handle = DRAG_N;
        h = ui_make_rect((rc.left + rc.right) / 2 - hs, rc.bottom - hs, (rc.left + rc.right) / 2 + hs, rc.bottom + hs);
        if (PtInRect(&h, pt)) handle = DRAG_S;
        h = ui_make_rect(rc.left - hs, (rc.top + rc.bottom) / 2 - hs, rc.left + hs, (rc.top + rc.bottom) / 2 + hs);
        if (PtInRect(&h, pt)) handle = DRAG_W;
        h = ui_make_rect(rc.right - hs, (rc.top + rc.bottom) / 2 - hs, rc.right + hs, (rc.top + rc.bottom) / 2 + hs);
        if (PtInRect(&h, pt)) handle = DRAG_E;
        *out_handle = handle;
    }
    return (int)hit;
}

void UiEditorApp::overlay_start_drag(const POINT& pt)
{
    domui_layout_rect r;
    DragMode handle = DRAG_NONE;
    int hit = overlay_hit_test(pt, &r, &handle);
    if (hit == 0) {
        select_widget(0u, 0);
        return;
    }
    select_widget((domui_widget_id)hit, 0);
    {
        domui_widget* w = m_doc.find_by_id((domui_widget_id)hit);
        if (w && w->dock != DOMUI_DOCK_NONE) {
            log_info("dock: drag disabled; use properties");
            return;
        }
    }
    m_drag_mode = handle;
    m_drag_widget_id = (domui_widget_id)hit;
    m_drag_start_pt = pt;
    m_drag_start_rect = r;
    m_drag_before_doc = m_doc;
    SetCapture(m_overlay);
}

void UiEditorApp::overlay_update_drag(const POINT& pt)
{
    if (m_drag_mode == DRAG_NONE || m_drag_widget_id == 0u) {
        return;
    }
    domui_widget* w = m_doc.find_by_id(m_drag_widget_id);
    if (!w) {
        return;
    }
    domui_layout_rect r = m_drag_start_rect;
    int dx = pt.x - m_drag_start_pt.x;
    int dy = pt.y - m_drag_start_pt.y;

    if (m_drag_mode == DRAG_MOVE) {
        r.x += dx;
        r.y += dy;
    } else {
        if (m_drag_mode == DRAG_N || m_drag_mode == DRAG_NE || m_drag_mode == DRAG_NW) {
            r.y += dy;
            r.h -= dy;
        }
        if (m_drag_mode == DRAG_S || m_drag_mode == DRAG_SE || m_drag_mode == DRAG_SW) {
            r.h += dy;
        }
        if (m_drag_mode == DRAG_W || m_drag_mode == DRAG_NW || m_drag_mode == DRAG_SW) {
            r.x += dx;
            r.w -= dx;
        }
        if (m_drag_mode == DRAG_E || m_drag_mode == DRAG_NE || m_drag_mode == DRAG_SE) {
            r.w += dx;
        }
    }

    if (r.w < 1) r.w = 1;
    if (r.h < 1) r.h = 1;
    apply_rect_to_widget(w, r);
    refresh_layout(1);
}

void UiEditorApp::overlay_end_drag()
{
    if (m_drag_mode != DRAG_NONE) {
        push_command("drag", m_drag_before_doc);
    }
    m_drag_mode = DRAG_NONE;
    m_drag_widget_id = 0u;
    ReleaseCapture();
}

LRESULT CALLBACK UiEditorApp::DuiSubclassProc(HWND hwnd,
                                              UINT msg,
                                              WPARAM wparam,
                                              LPARAM lparam,
                                              UINT_PTR id,
                                              DWORD_PTR ref)
{
    UiEditorApp* app = (UiEditorApp*)ref;
    LRESULT res = DefSubclassProc(hwnd, msg, wparam, lparam);
    if (app && msg == WM_PAINT && app->m_overlay && !app->m_overlay_layered) {
        InvalidateRect(app->m_overlay, NULL, TRUE);
    }
    if (msg == WM_NCDESTROY) {
        RemoveWindowSubclass(hwnd, UiEditorApp::DuiSubclassProc, id);
    }
    return res;
}

void UiEditorApp::nudge_selected(int dx, int dy)
{
    if (m_selected_id == 0u) {
        return;
    }
    domui_widget* w = m_doc.find_by_id(m_selected_id);
    if (!w) {
        return;
    }
    domui_doc before = m_doc;
    domui_layout_rect r = get_layout_rect(m_selected_id);
    r.x += dx;
    r.y += dy;
    apply_rect_to_widget(w, r);
    refresh_layout(1);
    push_command("nudge", before);
}

void UiEditorApp::refresh_layout(int rebuild_schema)
{
    RECT rc;
    if (!m_preview_host) {
        return;
    }
    GetClientRect(m_preview_host, &rc);
    m_root_rect.x = 0;
    m_root_rect.y = 0;
    m_root_rect.w = rc.right - rc.left;
    m_root_rect.h = rc.bottom - rc.top;

    compute_layout(NULL);

    if (rebuild_schema && m_dui_api && m_dui_win) {
        std::vector<unsigned char> schema;
        if (build_dui_schema(schema)) {
            if (m_dui_api->set_schema_tlv(m_dui_win,
                                          schema.empty() ? 0 : &schema[0],
                                          (u32)schema.size()) != DUI_OK) {
                log_info("preview: set_schema_tlv failed");
            }
        } else {
            log_info("preview: schema build failed");
        }
    }
    InvalidateRect(m_overlay, NULL, TRUE);
}

void UiEditorApp::compute_layout(domui_diag* diag)
{
    int count = (int)m_doc.widget_count();
    if (count < 1) {
        count = 1;
    }
    m_layout_results.resize((size_t)count);
    int cap = count;
    if (!domui_compute_layout(&m_doc,
                              0u,
                              m_root_rect.x,
                              m_root_rect.y,
                              m_root_rect.w,
                              m_root_rect.h,
                              &m_layout_results[0],
                              &cap,
                              diag)) {
        if (cap > count) {
            m_layout_results.resize((size_t)cap);
            int cap2 = cap;
            domui_compute_layout(&m_doc,
                                 0u,
                                 m_root_rect.x,
                                 m_root_rect.y,
                                 m_root_rect.w,
                                 m_root_rect.h,
                                 &m_layout_results[0],
                                 &cap2,
                                 diag);
            cap = cap2;
        }
    }
    m_layout_results.resize((size_t)cap);
    m_layout_map.clear();
    m_layout_order.clear();
    for (size_t i = 0u; i < m_layout_results.size(); ++i) {
        m_layout_map[m_layout_results[i].widget_id] = m_layout_results[i].rect;
        m_layout_order.push_back(m_layout_results[i].widget_id);
    }
}

static u32 ui_dui_kind_for_widget(domui_widget_type type)
{
    switch (type) {
    case DOMUI_WIDGET_CONTAINER: return (u32)DUI_NODE_STACK;
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
    case DOMUI_WIDGET_LISTVIEW: return (u32)DUI_NODE_LIST;
    default:
        break;
    }
    return (u32)DUI_NODE_LABEL;
}

void UiEditorApp::build_dui_node(domui_widget_id id, std::vector<unsigned char>& out_payload)
{
    domui_widget* w = m_doc.find_by_id(id);
    if (!w) {
        return;
    }
    domui_layout_rect r = get_layout_rect(id);
    ui_tlv_write_u32_value(out_payload, DUI_TLV_ID_U32, w->id);
    ui_tlv_write_u32_value(out_payload, DUI_TLV_KIND_U32, ui_dui_kind_for_widget(w->type));
    ui_tlv_write_u32_value(out_payload, DUI_TLV_FLAGS_U32, (u32)DUI_NODE_FLAG_ABSOLUTE);
    ui_tlv_write_rect(out_payload, DUI_TLV_RECT_I32, r.x, r.y, r.w, r.h);

    {
        std::string text;
        if (w->type == DOMUI_WIDGET_TAB_PAGE) {
            domui_string title;
            if (ui_prop_get_string(w->props, "tab.title", title) && !title.empty()) {
                text = title.str();
            } else {
                text = w->name.str();
            }
        } else if (w->type == DOMUI_WIDGET_STATIC_TEXT ||
                   w->type == DOMUI_WIDGET_BUTTON ||
                   w->type == DOMUI_WIDGET_CHECKBOX ||
                   w->type == DOMUI_WIDGET_EDIT) {
            text = w->name.str();
        }
        if (!text.empty()) {
            ui_tlv_write_string(out_payload, DUI_TLV_TEXT_UTF8, text);
        }
    }

    if (w->type == DOMUI_WIDGET_SPLITTER) {
        domui_string orient;
        int pos = ui_prop_get_int_default(w->props, "splitter.pos", -1);
        int thickness = ui_prop_get_int_default(w->props, "splitter.thickness", 4);
        int min_a = ui_prop_get_int_default(w->props, "splitter.min_a", 0);
        int min_b = ui_prop_get_int_default(w->props, "splitter.min_b", 0);
        u32 orient_val = (u32)DUI_SPLIT_VERTICAL;
        if (ui_prop_get_string(w->props, "splitter.orientation", orient)) {
            const char* s = orient.c_str();
            if (s && (s[0] == 'h' || s[0] == 'H')) {
                orient_val = (u32)DUI_SPLIT_HORIZONTAL;
            }
        }
        ui_tlv_write_u32_value(out_payload, DUI_TLV_SPLITTER_ORIENT_U32, orient_val);
        if (pos >= 0) {
            ui_tlv_write_u32_value(out_payload, DUI_TLV_SPLITTER_POS_U32, (u32)pos);
        }
        ui_tlv_write_u32_value(out_payload, DUI_TLV_SPLITTER_THICK_U32, (u32)thickness);
        ui_tlv_write_u32_value(out_payload, DUI_TLV_SPLITTER_MIN_A_U32, (u32)min_a);
        ui_tlv_write_u32_value(out_payload, DUI_TLV_SPLITTER_MIN_B_U32, (u32)min_b);
    } else if (w->type == DOMUI_WIDGET_TABS) {
        domui_string placement;
        int sel = ui_prop_get_int_default(w->props, "tabs.selected_index", 0);
        u32 place = (u32)DUI_TABS_TOP;
        if (ui_prop_get_string(w->props, "tabs.placement", placement)) {
            const char* s = placement.c_str();
            if (s && (s[0] == 'b' || s[0] == 'B')) place = (u32)DUI_TABS_BOTTOM;
            else if (s && (s[0] == 'l' || s[0] == 'L')) place = (u32)DUI_TABS_LEFT;
            else if (s && (s[0] == 'r' || s[0] == 'R')) place = (u32)DUI_TABS_RIGHT;
        }
        ui_tlv_write_u32_value(out_payload, DUI_TLV_TABS_SELECTED_U32, (u32)sel);
        ui_tlv_write_u32_value(out_payload, DUI_TLV_TABS_PLACEMENT_U32, place);
    } else if (w->type == DOMUI_WIDGET_TAB_PAGE) {
        int enabled = ui_prop_get_int_default(w->props, "tab.enabled", 1);
        ui_tlv_write_u32_value(out_payload, DUI_TLV_TAB_ENABLED_U32, (u32)(enabled ? 1u : 0u));
    } else if (w->type == DOMUI_WIDGET_SCROLLPANEL) {
        int h_en = ui_prop_get_int_default(w->props, "scroll.h_enabled", 1);
        int v_en = ui_prop_get_int_default(w->props, "scroll.v_enabled", 1);
        int sx = ui_prop_get_int_default(w->props, "scroll.x", 0);
        int sy = ui_prop_get_int_default(w->props, "scroll.y", 0);
        ui_tlv_write_u32_value(out_payload, DUI_TLV_SCROLL_H_ENABLED_U32, (u32)(h_en ? 1u : 0u));
        ui_tlv_write_u32_value(out_payload, DUI_TLV_SCROLL_V_ENABLED_U32, (u32)(v_en ? 1u : 0u));
        ui_tlv_write_u32_value(out_payload, DUI_TLV_SCROLL_X_U32, (u32)sx);
        ui_tlv_write_u32_value(out_payload, DUI_TLV_SCROLL_Y_U32, (u32)sy);
    }

    {
        std::vector<unsigned char> children_payload;
        std::vector<domui_widget_id> child_ids;
        m_doc.enumerate_children(w->id, child_ids);
        for (size_t i = 0u; i < child_ids.size(); ++i) {
            std::vector<unsigned char> child_payload;
            build_dui_node(child_ids[i], child_payload);
            if (!child_payload.empty()) {
                ui_tlv_write_tlv(children_payload, DUI_TLV_NODE_V1,
                                 &child_payload[0], child_payload.size());
            }
        }
        if (!children_payload.empty()) {
            ui_tlv_write_tlv(out_payload, DUI_TLV_CHILDREN_V1,
                             &children_payload[0], children_payload.size());
        }
    }
}

bool UiEditorApp::build_dui_schema(std::vector<unsigned char>& out_bytes)
{
    std::vector<domui_widget_id> roots;
    m_doc.enumerate_children(0u, roots);
    if (roots.empty()) {
        out_bytes.clear();
        return false;
    }

    std::vector<unsigned char> root_payload;
    build_dui_node(roots[0], root_payload);
    if (root_payload.empty()) {
        out_bytes.clear();
        return false;
    }

    {
        std::vector<unsigned char> form_payload;
        std::vector<unsigned char> schema_payload;
        ui_tlv_write_tlv(form_payload, DUI_TLV_NODE_V1,
                         &root_payload[0],
                         root_payload.size());
        ui_tlv_write_tlv(schema_payload, DUI_TLV_FORM_V1,
                         &form_payload[0],
                         form_payload.size());
        out_bytes.clear();
        ui_tlv_write_tlv(out_bytes, DUI_TLV_SCHEMA_V1,
                         &schema_payload[0],
                         schema_payload.size());
    }

    return !out_bytes.empty();
}

LRESULT UiEditorApp::handle_message(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    switch (msg) {
    case WM_CREATE:
        on_create(hwnd);
        return 0;
    case WM_DESTROY:
        on_destroy();
        PostQuitMessage(0);
        return 0;
    case WM_SIZE:
        on_size(LOWORD(lparam), HIWORD(lparam));
        return 0;
    case WM_TIMER:
        if (wparam == ID_PREVIEW_TIMER) {
            if (m_overlay && !m_overlay_layered) {
                InvalidateRect(m_overlay, NULL, TRUE);
            }
            return 0;
        }
        break;
    case WM_COMMAND:
        {
            int id = LOWORD(wparam);
            int code = HIWORD(wparam);
            if (id == ID_FILE_NEW) {
                if (confirm_discard()) {
                    new_document();
                }
                return 0;
            }
            if (id == ID_FILE_OPEN) {
                open_document();
                return 0;
            }
            if (id == ID_FILE_OPEN_TOOL) {
                open_tool_ui_dialog();
                return 0;
            }
            if (id == ID_FILE_IMPORT_LEGACY) {
                import_legacy_ui_dialog();
                return 0;
            }
            if (id == ID_FILE_EXPORT_TOOL) {
                export_tool_ui();
                return 0;
            }
            if (id == ID_FILE_REFRESH_INDEX) {
                scan_ui_index(NULL);
                return 0;
            }
            if (id == ID_FILE_SAVE) {
                save_document();
                return 0;
            }
            if (id == ID_FILE_SAVE_AS) {
                save_document_as();
                return 0;
            }
            if (id == ID_FILE_VALIDATE) {
                domui_diag diag;
                domui_validate_doc(&m_doc, 0, &diag);
                log_from_diag(diag);
                return 0;
            }
            if (id == ID_FILE_EXIT) {
                if (confirm_discard()) {
                    DestroyWindow(hwnd);
                }
                return 0;
            }
            if (id == ID_EDIT_UNDO) {
                undo();
                return 0;
            }
            if (id == ID_EDIT_REDO) {
                redo();
                return 0;
            }
            if (id == ID_EDIT_DELETE) {
                if (m_selected_id != 0u) {
                    domui_doc before = m_doc;
                    delete_widget(m_selected_id);
                    push_command("delete", before);
                }
                return 0;
            }
            if (id == ID_TREE_SEARCH && code == EN_CHANGE) {
                char buf[256];
                GetWindowTextA(m_tree_search, buf, sizeof(buf));
                search_tree(buf);
                return 0;
            }
            if (id >= ID_ADD_WIDGET_BASE && id < (ID_ADD_WIDGET_BASE + 128)) {
                domui_widget_type type = ui_widget_type_from_menu(id);
                domui_doc before = m_doc;
                domui_widget_id new_id = add_widget(type, m_selected_id);
                if (new_id != 0u) {
                    push_command("add", before);
                    rebuild_tree();
                    select_widget(new_id, 0);
                    refresh_layout(1);
                }
                return 0;
            }
            if (id == ID_CONTEXT_DELETE) {
                if (m_selected_id != 0u) {
                    domui_doc before = m_doc;
                    delete_widget(m_selected_id);
                    push_command("delete", before);
                }
                return 0;
            }
            if (id == ID_LOG && code == LBN_SELCHANGE) {
                int sel = (int)SendMessageA(m_log, LB_GETCURSEL, 0, 0);
                if (sel >= 0) {
                    domui_widget_id wid = (domui_widget_id)SendMessageA(m_log, LB_GETITEMDATA, sel, 0);
                    if (wid != 0u) {
                        select_widget(wid, 0);
                    }
                }
                return 0;
            }
            if (id == ID_LOG && code == LBN_DBLCLK) {
                int sel = (int)SendMessageA(m_log, LB_GETCURSEL, 0, 0);
                if (sel >= 0) {
                    domui_widget_id wid = (domui_widget_id)SendMessageA(m_log, LB_GETITEMDATA, sel, 0);
                    if (wid != 0u) {
                        select_widget(wid, 0);
                    }
                }
                return 0;
            }
            if (id == ID_INSPECTOR_EDIT && code == EN_KILLFOCUS) {
                if (m_inspector_edit_row >= 0 && m_inspector_edit_row < (int)m_inspector_rows.size()) {
                    char buf[512];
                    GetWindowTextA(m_inspector_edit, buf, sizeof(buf));
                    {
                        domui_doc before = m_doc;
                        InspectorRow& row = m_inspector_rows[m_inspector_edit_row];
                        if (row.editable && row.widget_id != 0u) {
                            domui_widget* w = m_doc.find_by_id(row.widget_id);
                            if (w) {
                                std::string val = buf;
                                int ok = 1;
                                domui_u32 uv = 0u;
                                if (row.type == ROW_FIELD) {
                                    int iv = 0;
                                    switch (row.field) {
                                    case FIELD_NAME:
                                        w->name.set(val.c_str());
                                        break;
                                    case FIELD_X:
                                        ok = ui_parse_int(val, &iv);
                                        if (ok) w->x = iv;
                                        break;
                                    case FIELD_Y:
                                        ok = ui_parse_int(val, &iv);
                                        if (ok) w->y = iv;
                                        break;
                                    case FIELD_W:
                                        ok = ui_parse_int(val, &iv);
                                        if (ok) w->w = iv;
                                        break;
                                    case FIELD_H:
                                        ok = ui_parse_int(val, &iv);
                                        if (ok) w->h = iv;
                                        break;
                                    case FIELD_LAYOUT_MODE:
                                        w->layout_mode = ui_parse_layout_mode(val, &ok);
                                        break;
                                    case FIELD_DOCK:
                                        w->dock = ui_parse_dock_mode(val, &ok);
                                        break;
                                    case FIELD_ANCHORS:
                                        w->anchors = ui_parse_anchor_mask(val, &ok);
                                        break;
                                    case FIELD_MARGIN_LEFT:
                                        ok = ui_parse_int(val, &iv);
                                        if (ok) w->margin.left = iv;
                                        break;
                                    case FIELD_MARGIN_RIGHT:
                                        ok = ui_parse_int(val, &iv);
                                        if (ok) w->margin.right = iv;
                                        break;
                                    case FIELD_MARGIN_TOP:
                                        ok = ui_parse_int(val, &iv);
                                        if (ok) w->margin.top = iv;
                                        break;
                                    case FIELD_MARGIN_BOTTOM:
                                        ok = ui_parse_int(val, &iv);
                                        if (ok) w->margin.bottom = iv;
                                        break;
                                    case FIELD_PADDING_LEFT:
                                        ok = ui_parse_int(val, &iv);
                                        if (ok) w->padding.left = iv;
                                        break;
                                    case FIELD_PADDING_RIGHT:
                                        ok = ui_parse_int(val, &iv);
                                        if (ok) w->padding.right = iv;
                                        break;
                                    case FIELD_PADDING_TOP:
                                        ok = ui_parse_int(val, &iv);
                                        if (ok) w->padding.top = iv;
                                        break;
                                    case FIELD_PADDING_BOTTOM:
                                        ok = ui_parse_int(val, &iv);
                                        if (ok) w->padding.bottom = iv;
                                        break;
                                    case FIELD_MIN_W:
                                        ok = ui_parse_int(val, &iv);
                                        if (ok) w->min_w = iv;
                                        break;
                                    case FIELD_MIN_H:
                                        ok = ui_parse_int(val, &iv);
                                        if (ok) w->min_h = iv;
                                        break;
                                    case FIELD_MAX_W:
                                        ok = ui_parse_int(val, &iv);
                                        if (ok) w->max_w = iv;
                                        break;
                                    case FIELD_MAX_H:
                                        ok = ui_parse_int(val, &iv);
                                        if (ok) w->max_h = iv;
                                        break;
                                    default:
                                        break;
                                    }
                                } else if (row.type == ROW_PROP) {
                                    domui_value v;
                                    v.type = row.prop_type;
                                    if (row.prop_type == DOMUI_VALUE_INT) {
                                        ok = ui_parse_int(val, &v.v_int);
                                    } else if (row.prop_type == DOMUI_VALUE_UINT) {
                                        ok = ui_parse_u32(val, &uv);
                                        v.v_uint = uv;
                                    } else if (row.prop_type == DOMUI_VALUE_BOOL) {
                                        ok = ui_parse_bool(val, &v.v_bool);
                                    } else if (row.prop_type == DOMUI_VALUE_STRING) {
                                        v.v_string.set(val.c_str());
                                    } else if (row.prop_type == DOMUI_VALUE_VEC2I) {
                                        ok = ui_parse_vec2i(val, &v.v_vec2i);
                                    } else if (row.prop_type == DOMUI_VALUE_RECTI) {
                                        ok = ui_parse_recti(val, &v.v_recti);
                                    }
                                    if (ok) {
                                        w->props.set(row.key.c_str(), v);
                                    }
                                } else if (row.type == ROW_EVENT) {
                                    if (val.empty()) {
                                        w->events.erase(row.key.c_str());
                                    } else {
                                        w->events.set(row.key.c_str(), val.c_str());
                                    }
                                }
                                if (ok) {
                                    push_command("edit", before);
                                    rebuild_inspector();
                                    refresh_layout(1);
                                } else {
                                    log_info("invalid value");
                                }
                            }
                        }
                    }
                }
                return 0;
            }
        }
        break;
    case WM_NOTIFY:
        {
            NMHDR* hdr = (NMHDR*)lparam;
            if (!hdr) {
                break;
            }
            if (hdr->idFrom == ID_TREE) {
                if (hdr->code == TVN_SELCHANGEDA) {
                    NMTREEVIEWA* tv = (NMTREEVIEWA*)lparam;
                    domui_widget_id wid = (domui_widget_id)tv->itemNew.lParam;
                    select_widget(wid, 1);
                } else if (hdr->code == TVN_BEGINDRAGA) {
                    NMTREEVIEWA* tv = (NMTREEVIEWA*)lparam;
                    m_tree_dragging = 1;
                    m_tree_drag_item = tv->itemNew.hItem;
                    m_tree_drag_id = (domui_widget_id)tv->itemNew.lParam;
                    m_tree_drop_target = 0;
                    SetCapture(m_hwnd);
                }
            }
            if (hdr->idFrom == ID_INSPECTOR) {
                if (hdr->code == LVN_ITEMCHANGED) {
                    NMLISTVIEW* lv = (NMLISTVIEW*)lparam;
                    if ((lv->uNewState & LVIS_SELECTED) != 0) {
                        m_inspector_edit_row = lv->iItem;
                        refresh_inspector_edit();
                    }
                }
            }
        }
        break;
    case WM_MOUSEMOVE:
        if (m_tree_dragging) {
            POINT pt;
            TVHITTESTINFO ht;
            GetCursorPos(&pt);
            ScreenToClient(m_tree, &pt);
            memset(&ht, 0, sizeof(ht));
            ht.pt = pt;
            TreeView_HitTest(m_tree, &ht);
            if (ht.hItem != m_tree_drop_target) {
                TreeView_SelectDropTarget(m_tree, ht.hItem);
                m_tree_drop_target = ht.hItem;
            }
            return 0;
        }
        break;
    case WM_LBUTTONUP:
        if (m_tree_dragging) {
            domui_widget_id new_parent = 0u;
            HTREEITEM target = m_tree_drop_target;
            ReleaseCapture();
            TreeView_SelectDropTarget(m_tree, NULL);
            m_tree_dragging = 0;
            if (target) {
                TVITEMA item;
                memset(&item, 0, sizeof(item));
                item.mask = TVIF_PARAM;
                item.hItem = target;
                if (TreeView_GetItem(m_tree, &item)) {
                    new_parent = (domui_widget_id)item.lParam;
                }
            }
            if (m_tree_drag_id != 0u) {
                domui_doc before = m_doc;
                domui_u32 z = next_z_for_parent(new_parent);
                if (m_doc.reparent_widget(m_tree_drag_id, new_parent, z)) {
                    push_command("reparent", before);
                    rebuild_tree();
                    select_widget(m_tree_drag_id, 0);
                    refresh_layout(1);
                } else {
                    log_info("reparent: invalid target");
                }
            }
            m_tree_drop_target = 0;
            m_tree_drag_id = 0u;
            return 0;
        }
        break;
    case WM_KEYDOWN:
        if (wparam == VK_DELETE && m_selected_id != 0u) {
            domui_doc before = m_doc;
            delete_widget(m_selected_id);
            push_command("delete", before);
            return 0;
        }
        {
            int step = (GetKeyState(VK_SHIFT) & 0x8000) ? 10 : 1;
            if (wparam == VK_LEFT) {
                nudge_selected(-step, 0);
                return 0;
            }
            if (wparam == VK_RIGHT) {
                nudge_selected(step, 0);
                return 0;
            }
            if (wparam == VK_UP) {
                nudge_selected(0, -step);
                return 0;
            }
            if (wparam == VK_DOWN) {
                nudge_selected(0, step);
                return 0;
            }
        }
        break;
    case WM_CONTEXTMENU:
        if ((HWND)wparam == m_tree) {
            HMENU menu = CreatePopupMenu();
            AppendMenuA(menu, MF_STRING, ID_ADD_WIDGET_BASE + DOMUI_WIDGET_CONTAINER, "Add Container");
            AppendMenuA(menu, MF_STRING, ID_ADD_WIDGET_BASE + DOMUI_WIDGET_STATIC_TEXT, "Add Static Text");
            AppendMenuA(menu, MF_STRING, ID_ADD_WIDGET_BASE + DOMUI_WIDGET_BUTTON, "Add Button");
            AppendMenuA(menu, MF_STRING, ID_ADD_WIDGET_BASE + DOMUI_WIDGET_EDIT, "Add Edit");
            AppendMenuA(menu, MF_STRING, ID_ADD_WIDGET_BASE + DOMUI_WIDGET_LISTBOX, "Add Listbox");
            AppendMenuA(menu, MF_STRING, ID_ADD_WIDGET_BASE + DOMUI_WIDGET_CHECKBOX, "Add Checkbox");
            AppendMenuA(menu, MF_STRING, ID_ADD_WIDGET_BASE + DOMUI_WIDGET_TABS, "Add Tabs");
            AppendMenuA(menu, MF_STRING, ID_ADD_WIDGET_BASE + DOMUI_WIDGET_TAB_PAGE, "Add Tab Page");
            AppendMenuA(menu, MF_STRING, ID_ADD_WIDGET_BASE + DOMUI_WIDGET_SPLITTER, "Add Splitter");
            AppendMenuA(menu, MF_STRING, ID_ADD_WIDGET_BASE + DOMUI_WIDGET_SCROLLPANEL, "Add ScrollPanel");
            AppendMenuA(menu, MF_SEPARATOR, 0, 0);
            AppendMenuA(menu, MF_STRING, ID_CONTEXT_DELETE, "Delete");
            TrackPopupMenu(menu, TPM_RIGHTBUTTON, LOWORD(lparam), HIWORD(lparam), 0, m_hwnd, NULL);
            DestroyMenu(menu);
            return 0;
        }
        break;
    default:
        break;
    }
    return DefWindowProcA(hwnd, msg, wparam, lparam);
}

LRESULT UiEditorApp::handle_overlay_message(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    switch (msg) {
    case WM_NCHITTEST:
        {
            POINT pt;
            pt.x = (int)(short)LOWORD(lparam);
            pt.y = (int)(short)HIWORD(lparam);
            ScreenToClient(hwnd, &pt);
            if (overlay_should_capture(pt)) {
                return HTCLIENT;
            }
            return HTTRANSPARENT;
        }
    case WM_LBUTTONDOWN:
        {
            POINT pt;
            pt.x = LOWORD(lparam);
            pt.y = HIWORD(lparam);
            overlay_start_drag(pt);
        }
        return 0;
    case WM_MOUSEMOVE:
        if (m_drag_mode != DRAG_NONE) {
            POINT pt;
            pt.x = LOWORD(lparam);
            pt.y = HIWORD(lparam);
            overlay_update_drag(pt);
        }
        return 0;
    case WM_LBUTTONUP:
        overlay_end_drag();
        return 0;
    case WM_ERASEBKGND:
        return 1;
    case WM_PAINT:
        {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hwnd, &ps);
            overlay_paint(hdc);
            EndPaint(hwnd, &ps);
        }
        return 0;
    case WM_SETCURSOR:
        if (LOWORD(lparam) == HTCLIENT) {
            POINT pt;
            GetCursorPos(&pt);
            ScreenToClient(hwnd, &pt);
            domui_layout_rect r;
            DragMode handle = DRAG_NONE;
            overlay_hit_test(pt, &r, &handle);
            if (handle == DRAG_MOVE) {
                SetCursor(LoadCursor(NULL, IDC_SIZEALL));
                return TRUE;
            }
            if (handle == DRAG_N || handle == DRAG_S) {
                SetCursor(LoadCursor(NULL, IDC_SIZENS));
                return TRUE;
            }
            if (handle == DRAG_E || handle == DRAG_W) {
                SetCursor(LoadCursor(NULL, IDC_SIZEWE));
                return TRUE;
            }
            if (handle == DRAG_NE || handle == DRAG_SW) {
                SetCursor(LoadCursor(NULL, IDC_SIZENESW));
                return TRUE;
            }
            if (handle == DRAG_NW || handle == DRAG_SE) {
                SetCursor(LoadCursor(NULL, IDC_SIZENWSE));
                return TRUE;
            }
        }
        break;
    default:
        break;
    }
    return DefWindowProcA(hwnd, msg, wparam, lparam);
}

LRESULT UiEditorApp::handle_splitter_message(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    switch (msg) {
    case WM_LBUTTONDOWN:
        m_split_dragging = 1;
        SetCapture(hwnd);
        if ((HWND)hwnd == m_split_left) m_split_drag_type = ID_SPLIT_LEFT;
        else if ((HWND)hwnd == m_split_right) m_split_drag_type = ID_SPLIT_RIGHT;
        else if ((HWND)hwnd == m_split_bottom) m_split_drag_type = ID_SPLIT_BOTTOM;
        return 0;
    case WM_LBUTTONUP:
        m_split_dragging = 0;
        m_split_drag_type = 0;
        ReleaseCapture();
        return 0;
    case WM_MOUSEMOVE:
        if (m_split_dragging && m_hwnd) {
            POINT pt;
            RECT rc;
            GetCursorPos(&pt);
            ScreenToClient(m_hwnd, &pt);
            GetClientRect(m_hwnd, &rc);
            if (m_split_drag_type == ID_SPLIT_LEFT) {
                int new_left = pt.x;
                if (new_left < kMinPanelSize) new_left = kMinPanelSize;
                if (new_left > rc.right - kMinPanelSize - kMinPreviewSize) {
                    new_left = rc.right - kMinPanelSize - kMinPreviewSize;
                }
                m_left_width = new_left;
                layout_children();
            } else if (m_split_drag_type == ID_SPLIT_RIGHT) {
                int new_right = rc.right - pt.x - kSplitterSize;
                if (new_right < kMinPanelSize) new_right = kMinPanelSize;
                if (new_right > rc.right - kMinPanelSize - kMinPreviewSize) {
                    new_right = rc.right - kMinPanelSize - kMinPreviewSize;
                }
                m_right_width = new_right;
                layout_children();
            } else if (m_split_drag_type == ID_SPLIT_BOTTOM) {
                int new_bottom = rc.bottom - pt.y - kSplitterSize;
                if (new_bottom < kMinPanelSize) new_bottom = kMinPanelSize;
                if (new_bottom > rc.bottom - kMinPanelSize) {
                    new_bottom = rc.bottom - kMinPanelSize;
                }
                m_bottom_height = new_bottom;
                layout_children();
            }
        }
        return 0;
    case WM_SETCURSOR:
        if ((HWND)hwnd == m_split_bottom) {
            SetCursor(LoadCursor(NULL, IDC_SIZENS));
        } else {
            SetCursor(LoadCursor(NULL, IDC_SIZEWE));
        }
        return TRUE;
    default:
        break;
    }
    return DefWindowProcA(hwnd, msg, wparam, lparam);
}

static LRESULT CALLBACK UiEditor_MainWndProc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    UiEditorApp* app = (UiEditorApp*)GetWindowLongPtr(hwnd, GWLP_USERDATA);
    if (msg == WM_CREATE) {
        CREATESTRUCTA* cs = (CREATESTRUCTA*)lparam;
        app = (UiEditorApp*)cs->lpCreateParams;
        SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)app);
    }
    if (!app) {
        return DefWindowProcA(hwnd, msg, wparam, lparam);
    }
    return app->handle_message(hwnd, msg, wparam, lparam);
}

static LRESULT CALLBACK UiEditor_OverlayWndProc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    UiEditorApp* app = (UiEditorApp*)GetWindowLongPtr(hwnd, GWLP_USERDATA);
    if (msg == WM_CREATE) {
        CREATESTRUCTA* cs = (CREATESTRUCTA*)lparam;
        app = (UiEditorApp*)cs->lpCreateParams;
        SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)app);
    }
    if (!app) {
        return DefWindowProcA(hwnd, msg, wparam, lparam);
    }
    return app->handle_overlay_message(hwnd, msg, wparam, lparam);
}

static LRESULT CALLBACK UiEditor_SplitterWndProc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    UiEditorApp* app = (UiEditorApp*)GetWindowLongPtr(hwnd, GWLP_USERDATA);
    if (msg == WM_CREATE) {
        CREATESTRUCTA* cs = (CREATESTRUCTA*)lparam;
        app = (UiEditorApp*)cs->lpCreateParams;
        SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)app);
    }
    if (!app) {
        return DefWindowProcA(hwnd, msg, wparam, lparam);
    }
    return app->handle_splitter_message(hwnd, msg, wparam, lparam);
}

int WINAPI WinMain(HINSTANCE inst, HINSTANCE prev, LPSTR cmd, int show)
{
    UiEditorApp app;
    (void)prev;
    (void)show;

    {
        std::vector<std::string> args;
        ui_split_args(cmd, args);
        if (ui_should_run_cli(args)) {
            return ui_run_cli(args);
        }
    }

    if (!app.init(inst)) {
        return 1;
    }

    {
        MSG msg;
        while (GetMessageA(&msg, NULL, 0, 0) > 0) {
            TranslateMessage(&msg);
            DispatchMessageA(&msg);
        }
    }
    return 0;
}

#endif
