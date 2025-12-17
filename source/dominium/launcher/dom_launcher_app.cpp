/*
FILE: source/dominium/launcher/dom_launcher_app.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/dom_launcher_app
RESPONSIBILITY: Implements `dom_launcher_app`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_launcher_app.h"

#include <algorithm>
#include <cstdio>
#include <cstring>
#include <cctype>

#include "dom_launcher_actions.h"
#include "dom_launcher_catalog.h"

#include "launcher_launch_plumbing.h"

extern "C" {
#include "domino/caps.h"
#include "domino/system/dsys.h"
}

#include "core/include/launcher_safety.h"

namespace dom {

struct DomLauncherUiState {
    enum LauncherTab {
        TAB_PLAY = 0,
        TAB_INSTANCES = 1,
        TAB_PACKS = 2,
        TAB_OPTIONS = 3,
        TAB_LOGS = 4
    };

    u32 tab;
    std::string instance_search;
    u32 play_target_item_id;

    u32 dialog_visible;
    std::string dialog_title;
    std::string dialog_text;
    std::vector<std::string> dialog_lines;

    std::string status_text;
    u32 status_progress; /* 0..1000 */

    DomLauncherUiState()
        : tab((u32)TAB_PLAY),
          instance_search(),
          play_target_item_id(0u),
          dialog_visible(0u),
          dialog_title(),
          dialog_text(),
          dialog_lines(),
          status_text("Ready."),
          status_progress(0u) {}
};

namespace {

/* UI schema widget IDs (scripts/gen_launcher_ui_schema_v1.py). */
enum LauncherUiWidgetId {
    W_HEADER_INFO = 1112,

    W_INST_SEARCH = 1201,
    W_INST_LIST = 1202,
    W_INST_HINT = 1203,

    W_TAB_PLAY_BTN = 1301,
    W_TAB_INST_BTN = 1302,
    W_TAB_PACKS_BTN = 1303,
    W_TAB_OPTIONS_BTN = 1304,
    W_TAB_LOGS_BTN = 1305,

    W_TAB_PLAY_PANEL = 1311,
    W_TAB_INST_PANEL = 1312,
    W_TAB_PACKS_PANEL = 1313,
    W_TAB_OPTIONS_PANEL = 1314,
    W_TAB_LOGS_PANEL = 1315,

    W_PLAY_SELECTED = 1410,
    W_PLAY_PROFILE = 1411,
    W_PLAY_MANIFEST = 1412,
    W_PLAY_TARGET_LIST = 1414,
    W_PLAY_OFFLINE = 1415,
    W_PLAY_LAST_RUN = 1419,
    W_NEWS_LIST = 1451,

    W_INST_IMPORT_PATH = 1505,
    W_INST_EXPORT_PATH = 1508,
    W_INST_PATHS_LIST = 1512,

    W_PACKS_LABEL = 1600,
    W_PACKS_LIST = 1601,
    W_PACKS_ENABLED = 1602,
    W_PACKS_POLICY_LIST = 1604,
    W_PACKS_RESOLVED = 1607,
    W_PACKS_ERROR = 1608,

    W_OPT_GFX_LIST = 1702,
    W_OPT_API_FIELD = 1704,
    W_OPT_WINMODE_LIST = 1706,
    W_OPT_WIDTH_FIELD = 1708,
    W_OPT_HEIGHT_FIELD = 1709,
    W_OPT_DPI_FIELD = 1710,
    W_OPT_MONITOR_FIELD = 1711,
    W_OPT_AUDIO_LABEL = 1712,
    W_OPT_INPUT_LABEL = 1713,

    W_LOGS_LAST_RUN = 1801,
    W_LOGS_RUNS_LIST = 1803,
    W_LOGS_AUDIT_LIST = 1804,
    W_LOGS_DIAG_OUT = 1806,
    W_LOGS_LOCS_LIST = 1809,

    W_STATUS_TEXT = 1901,
    W_STATUS_PROGRESS = 1902,
    W_STATUS_SELECTION = 1903,

    W_DIALOG_COL = 2000,
    W_DIALOG_TITLE = 2001,
    W_DIALOG_TEXT = 2002,
    W_DIALOG_LIST = 2003
};

/* UI schema action IDs (scripts/gen_launcher_ui_schema_v1.py). */
enum LauncherUiActionId {
    ACT_TAB_PLAY = 100,
    ACT_TAB_INST = 101,
    ACT_TAB_PACKS = 102,
    ACT_TAB_OPTIONS = 103,
    ACT_TAB_LOGS = 104,

    ACT_DIALOG_OK = 900,
    ACT_DIALOG_CANCEL = 901
};

static int ascii_tolower(int c) {
    if (c >= 'A' && c <= 'Z') {
        return c - 'A' + 'a';
    }
    return c;
}

static bool str_ieq(const char* a, const char* b) {
    if (!a || !b) {
        return false;
    }
    while (*a && *b) {
        if (ascii_tolower((unsigned char)*a) != ascii_tolower((unsigned char)*b)) {
            return false;
        }
        ++a;
        ++b;
    }
    return *a == '\0' && *b == '\0';
}

static bool ends_with_ci(const char* s, const char* suffix) {
    size_t ls, lx, i;
    if (!s || !suffix) {
        return false;
    }
    ls = std::strlen(s);
    lx = std::strlen(suffix);
    if (lx == 0u || ls < lx) {
        return false;
    }
    s += (ls - lx);
    for (i = 0u; i < lx; ++i) {
        int a = (unsigned char)s[i];
        int b = (unsigned char)suffix[i];
        a = std::tolower(a);
        b = std::tolower(b);
        if (a != b) {
            return false;
        }
    }
    return true;
}

static bool is_product_entry_file(const char* filename) {
    if (!filename || !filename[0]) {
        return false;
    }
#if defined(_WIN32) || defined(_WIN64)
    return ends_with_ci(filename, ".exe");
#else
    if (filename[0] == '.') {
        return false;
    }
    if (ends_with_ci(filename, ".so") || std::strstr(filename, ".so.") != 0) {
        return false;
    }
    if (ends_with_ci(filename, ".dylib")) {
        return false;
    }
    if (ends_with_ci(filename, ".a")) {
        return false;
    }
    if (ends_with_ci(filename, ".txt") || ends_with_ci(filename, ".md")) {
        return false;
    }
    return true;
#endif
}

static void sort_products_deterministic(std::vector<ProductEntry>& products) {
    size_t i, j;
    for (i = 1u; i < products.size(); ++i) {
        ProductEntry key = products[i];
        j = i;
        while (j > 0u) {
            const ProductEntry& prev = products[j - 1u];
            bool move = false;
            if (prev.product > key.product) move = true;
            else if (prev.product == key.product && prev.version > key.version) move = true;
            else if (prev.product == key.product && prev.version == key.version && prev.path > key.path) move = true;
            if (!move) break;
            products[j] = products[j - 1u];
            --j;
        }
        products[j] = key;
    }
}

static bool str_contains_ci(const std::string& hay, const std::string& needle) {
    size_t i;
    size_t j;
    if (needle.empty()) {
        return true;
    }
    if (hay.size() < needle.size()) {
        return false;
    }
    for (i = 0u; i + needle.size() <= hay.size(); ++i) {
        bool ok = true;
        for (j = 0u; j < needle.size(); ++j) {
            const int a = ascii_tolower((unsigned char)hay[i + j]);
            const int b = ascii_tolower((unsigned char)needle[j]);
            if (a != b) {
                ok = false;
                break;
            }
        }
        if (ok) {
            return true;
        }
    }
    return false;
}

static bool is_sep(char c) { return c == '/' || c == '\\'; }

static std::string normalize_seps(const std::string& in) {
    std::string out = in;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') out[i] = '/';
    }
    return out;
}

static std::string dirname_of(const std::string& path) {
    size_t i;
    for (i = path.size(); i > 0u; --i) {
        if (is_sep(path[i - 1u])) {
            return path.substr(0u, i - 1u);
        }
    }
    return std::string();
}

static std::string path_join(const std::string& a, const std::string& b) {
    std::string aa = normalize_seps(a);
    std::string bb = normalize_seps(b);
    if (aa.empty()) return bb;
    if (bb.empty()) return aa;
    if (is_sep(aa[aa.size() - 1u])) return aa + bb;
    return aa + "/" + bb;
}

static bool file_exists_stdio(const std::string& path) {
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    std::fclose(f);
    return true;
}

static bool read_file_all_bytes(const std::string& path,
                                std::vector<unsigned char>& out_bytes,
                                std::string& out_error) {
    FILE* f;
    long sz;
    size_t got;
    out_bytes.clear();
    out_error.clear();

    f = std::fopen(path.c_str(), "rb");
    if (!f) {
        out_error = "open_failed";
        return false;
    }
    if (std::fseek(f, 0, SEEK_END) != 0) {
        std::fclose(f);
        out_error = "seek_end_failed";
        return false;
    }
    sz = std::ftell(f);
    if (sz < 0) {
        std::fclose(f);
        out_error = "tell_failed";
        return false;
    }
    if (std::fseek(f, 0, SEEK_SET) != 0) {
        std::fclose(f);
        out_error = "seek_set_failed";
        return false;
    }
    out_bytes.resize((size_t)sz);
    got = 0u;
    if (sz > 0) {
        got = std::fread(&out_bytes[0], 1u, (size_t)sz, f);
    }
    std::fclose(f);
    if (got != (size_t)sz) {
        out_bytes.clear();
        out_error = "read_failed";
        return false;
    }
    return true;
}

static u32 fnv1a32_bytes(const void* data, size_t len) {
    const unsigned char* p = (const unsigned char*)data;
    u32 h = 2166136261u;
    size_t i;
    for (i = 0u; i < len; ++i) {
        h ^= (u32)p[i];
        h *= 16777619u;
    }
    return h;
}

static u32 stable_item_id(const std::string& s) {
    u32 id = fnv1a32_bytes(s.data(), s.size());
    return (id == 0u) ? 1u : id;
}

static void append_u32_le(std::vector<unsigned char>& out, u32 v) {
    out.push_back((unsigned char)((v >> 0u) & 0xffu));
    out.push_back((unsigned char)((v >> 8u) & 0xffu));
    out.push_back((unsigned char)((v >> 16u) & 0xffu));
    out.push_back((unsigned char)((v >> 24u) & 0xffu));
}

static void append_u64_le(std::vector<unsigned char>& out, u64 v) {
    append_u32_le(out, (u32)(v & 0xffffffffu));
    append_u32_le(out, (u32)((v >> 32u) & 0xffffffffu));
}

static void append_tlv_raw(std::vector<unsigned char>& out, u32 tag, const void* payload, size_t payload_len) {
    append_u32_le(out, tag);
    append_u32_le(out, (u32)payload_len);
    if (payload_len != 0u) {
        const unsigned char* p = (const unsigned char*)payload;
        out.insert(out.end(), p, p + payload_len);
    }
}

static void append_tlv_u32(std::vector<unsigned char>& out, u32 tag, u32 v) {
    unsigned char le[4];
    le[0] = (unsigned char)((v >> 0u) & 0xffu);
    le[1] = (unsigned char)((v >> 8u) & 0xffu);
    le[2] = (unsigned char)((v >> 16u) & 0xffu);
    le[3] = (unsigned char)((v >> 24u) & 0xffu);
    append_tlv_raw(out, tag, le, 4u);
}

static void append_tlv_u64(std::vector<unsigned char>& out, u32 tag, u64 v) {
    std::vector<unsigned char> le;
    le.reserve(8u);
    append_u64_le(le, v);
    append_tlv_raw(out, tag, le.empty() ? (const void*)0 : &le[0], le.size());
}

static void append_tlv_text(std::vector<unsigned char>& out, u32 tag, const std::string& s) {
    append_tlv_raw(out, tag, s.empty() ? (const void*)0 : s.data(), s.size());
}

struct ListItem {
    u32 id;
    std::string text;
    ListItem() : id(0u), text() {}
    ListItem(u32 i, const std::string& t) : id(i), text(t) {}
};

static void dui_state_add_text(std::vector<unsigned char>& inner, u32 bind_id, const std::string& text) {
    std::vector<unsigned char> value;
    append_tlv_u32(value, DUI_TLV_BIND_U32, bind_id);
    append_tlv_u32(value, DUI_TLV_VALUE_TYPE_U32, (u32)DUI_VALUE_TEXT);
    append_tlv_text(value, DUI_TLV_VALUE_UTF8, text);
    append_tlv_raw(inner, DUI_TLV_VALUE_V1, value.empty() ? (const void*)0 : &value[0], value.size());
}

static void dui_state_add_u32(std::vector<unsigned char>& inner, u32 bind_id, u32 value_type, u32 v) {
    std::vector<unsigned char> value;
    append_tlv_u32(value, DUI_TLV_BIND_U32, bind_id);
    append_tlv_u32(value, DUI_TLV_VALUE_TYPE_U32, value_type);
    append_tlv_u32(value, DUI_TLV_VALUE_U32, v);
    append_tlv_raw(inner, DUI_TLV_VALUE_V1, value.empty() ? (const void*)0 : &value[0], value.size());
}

static void dui_state_add_list(std::vector<unsigned char>& inner,
                               u32 bind_id,
                               u32 selected_item_id,
                               const std::vector<ListItem>& items) {
    std::vector<unsigned char> list_payload;
    size_t i;
    append_tlv_u32(list_payload, DUI_TLV_LIST_SELECTED_U32, selected_item_id);
    for (i = 0u; i < items.size(); ++i) {
        std::vector<unsigned char> item_payload;
        append_tlv_u32(item_payload, DUI_TLV_ITEM_ID_U32, items[i].id);
        append_tlv_text(item_payload, DUI_TLV_ITEM_TEXT_UTF8, items[i].text);
        append_tlv_raw(list_payload,
                       DUI_TLV_LIST_ITEM_V1,
                       item_payload.empty() ? (const void*)0 : &item_payload[0],
                       item_payload.size());
    }

    std::vector<unsigned char> value;
    append_tlv_u32(value, DUI_TLV_BIND_U32, bind_id);
    append_tlv_u32(value, DUI_TLV_VALUE_TYPE_U32, (u32)DUI_VALUE_LIST);
    append_tlv_raw(value,
                   DUI_TLV_LIST_V1,
                   list_payload.empty() ? (const void*)0 : &list_payload[0],
                   list_payload.size());
    append_tlv_raw(inner, DUI_TLV_VALUE_V1, value.empty() ? (const void*)0 : &value[0], value.size());
}

static std::string tab_button_text(const char* base, bool selected) {
    if (!base) {
        return selected ? std::string("[*]") : std::string("[ ]");
    }
    return selected ? (std::string("[") + base + "]") : std::string(base);
}

static const dui_api_v1* lookup_dui_api_by_backend_name(const char* want_name, std::string& out_err) {
    u32 i;
    u32 count;
    dom_backend_desc desc;

    if (!want_name || !want_name[0]) {
        out_err = "ui backend name is empty";
        return 0;
    }

    count = dom_caps_backend_count();
    for (i = 0u; i < count; ++i) {
        if (dom_caps_backend_get(i, &desc) != DOM_CAPS_OK) {
            continue;
        }
        if (desc.subsystem_id != DOM_SUBSYS_DUI) {
            continue;
        }
        if (!desc.backend_name || !desc.backend_name[0]) {
            continue;
        }
        if (!str_ieq(desc.backend_name, want_name)) {
            continue;
        }
        if (!desc.get_api) {
            out_err = "ui backend missing get_api";
            return 0;
        }

        {
            const dui_api_v1* api = (const dui_api_v1*)desc.get_api(DUI_API_ABI_VERSION);
            if (!api) {
                out_err = std::string("ui get_api returned null for backend '") + want_name + "'";
                return 0;
            }
            if (api->abi_version != DUI_API_ABI_VERSION || api->struct_size != (u32)sizeof(dui_api_v1)) {
                out_err = std::string("ui api abi mismatch for backend '") + want_name + "'";
                return 0;
            }
            if (!api->create_context || !api->destroy_context ||
                !api->create_window || !api->destroy_window ||
                !api->set_schema_tlv || !api->set_state_tlv ||
                !api->pump || !api->poll_event || !api->request_quit || !api->render) {
                out_err = std::string("ui api missing required functions for backend '") + want_name + "'";
                return 0;
            }
            return api;
        }
    }

    out_err = std::string("ui backend not found in registry: '") + want_name + "'";
    return 0;
}

} // namespace

DomLauncherApp::DomLauncherApp()
    : m_paths(),
      m_mode(LAUNCHER_MODE_CLI),
      m_argv0(""),
      m_products(),
      m_instances(),
      m_profile(),
      m_profile_valid(false),
      m_dui_api(0),
      m_dui_ctx(0),
      m_dui_win(0),
      m_running(false),
      m_selected_product(-1),
      m_selected_instance(-1),
      m_selected_mode("gui"),
      m_ui_backend_selected(""),
      m_ui_caps_selected(0u),
      m_ui_fallback_note(""),
      m_ui(new DomLauncherUiState()) {
    std::memset(&m_profile, 0, sizeof(m_profile));
    m_profile.abi_version = DOM_PROFILE_ABI_VERSION;
    m_profile.struct_size = (u32)sizeof(dom_profile);
}

DomLauncherApp::~DomLauncherApp() {
    shutdown();
    delete m_ui;
    m_ui = 0;
}

bool DomLauncherApp::init_from_cli(const LauncherConfig &cfg, const dom_profile* profile) {
    std::string home = cfg.home;

    m_argv0 = cfg.argv0;

    m_profile_valid = false;
    std::memset(&m_profile, 0, sizeof(m_profile));
    m_profile.abi_version = DOM_PROFILE_ABI_VERSION;
    m_profile.struct_size = (u32)sizeof(dom_profile);
    if (profile &&
        profile->abi_version == DOM_PROFILE_ABI_VERSION &&
        profile->struct_size == (u32)sizeof(dom_profile)) {
        m_profile = *profile;
        m_profile_valid = true;
    }

    if (home.empty()) {
        home = ".";
    }

    if (!resolve_paths(m_paths, home)) {
        std::printf("Launcher: failed to resolve DOMINIUM_HOME from '%s'.\n", home.c_str());
        return false;
    }

    m_mode = cfg.mode;
    m_selected_mode = cfg.product_mode.empty() ? "gui" : cfg.product_mode;

    if (!scan_repo()) {
        return false;
    }
    (void)scan_products();
    (void)scan_instances();

    if (m_selected_product < 0 && !m_products.empty()) {
        m_selected_product = 0;
    }
    if (m_selected_instance < 0 && !m_instances.empty()) {
        m_selected_instance = 0;
    }

    if (m_mode == LAUNCHER_MODE_CLI) {
        return perform_cli_action(cfg);
    }

    if (!init_gui(cfg)) {
        std::printf("Launcher: failed to initialize GUI/TUI front-end.\n");
        return false;
    }
    return true;
}

void DomLauncherApp::run() {
    if (m_mode == LAUNCHER_MODE_CLI) {
        return;
    }
    if (m_running) {
        gui_loop();
    }
}

void DomLauncherApp::shutdown() {
    if (m_dui_api && m_dui_win) {
        m_dui_api->destroy_window(m_dui_win);
        m_dui_win = 0;
    }
    if (m_dui_api && m_dui_ctx) {
        m_dui_api->destroy_context(m_dui_ctx);
        m_dui_ctx = 0;
    }
    m_dui_api = 0;
    m_running = false;
}

void DomLauncherApp::set_selected_product(int idx) {
    if (idx < 0 || idx >= (int)m_products.size()) {
        return;
    }
    m_selected_product = idx;
}

void DomLauncherApp::set_selected_instance(int idx) {
    if (idx < 0 || idx >= (int)m_instances.size()) {
        return;
    }
    m_selected_instance = idx;
}

void DomLauncherApp::set_selected_mode(const std::string &mode) {
    if (!mode.empty()) {
        m_selected_mode = mode;
    }
}

void DomLauncherApp::select_prev_instance() {
    if (m_instances.empty()) {
        m_selected_instance = -1;
        return;
    }
    if (m_selected_instance < 0) {
        m_selected_instance = (int)m_instances.size() - 1;
        return;
    }
    m_selected_instance -= 1;
    if (m_selected_instance < 0) {
        m_selected_instance = (int)m_instances.size() - 1;
    }
}

void DomLauncherApp::select_next_instance() {
    if (m_instances.empty()) {
        m_selected_instance = -1;
        return;
    }
    if (m_selected_instance < 0) {
        m_selected_instance = 0;
        return;
    }
    m_selected_instance += 1;
    if (m_selected_instance >= (int)m_instances.size()) {
        m_selected_instance = 0;
    }
}

void DomLauncherApp::cycle_selected_mode() {
    if (m_selected_mode == "gui") {
        m_selected_mode = "tui";
    } else if (m_selected_mode == "tui") {
        m_selected_mode = "headless";
    } else {
        m_selected_mode = "gui";
    }
}

std::string DomLauncherApp::home_join(const std::string &rel) const {
    return join(m_paths.root, rel);
}

ProductEntry* DomLauncherApp::find_product_entry(const std::string &product) {
    size_t i;
    for (i = 0u; i < m_products.size(); ++i) {
        if (m_products[i].product == product) {
            return &m_products[i];
        }
    }
    return (ProductEntry *)0;
}

const InstanceInfo* DomLauncherApp::selected_instance() const {
    if (m_selected_instance < 0 || m_selected_instance >= (int)m_instances.size()) {
        return (const InstanceInfo *)0;
    }
    return &m_instances[(size_t)m_selected_instance];
}

bool DomLauncherApp::scan_repo() {
    if (!dir_exists(m_paths.root)) {
        std::printf("Launcher: DOMINIUM_HOME '%s' does not exist.\n", m_paths.root.c_str());
        return false;
    }
    if (!dir_exists(m_paths.products)) {
        std::printf("Launcher: '%s' missing, continuing with empty product catalog.\n",
                    m_paths.products.c_str());
    }
    if (!dir_exists(m_paths.instances)) {
        std::printf("Launcher: '%s' missing, no instances available.\n",
                    m_paths.instances.c_str());
    }
    if (!dir_exists(m_paths.mods)) {
        std::printf("Launcher: '%s' missing, no mods available.\n",
                    m_paths.mods.c_str());
    }
    if (!dir_exists(m_paths.packs)) {
        std::printf("Launcher: '%s' missing, no packs available.\n",
                    m_paths.packs.c_str());
    }
    return true;
}

bool DomLauncherApp::scan_products() {
    dsys_dir_iter *prod_it;
    dsys_dir_entry entry;

    m_products.clear();

    prod_it = dsys_dir_open(m_paths.products.c_str());
    if (!prod_it) {
        return true; /* No products directory is not fatal. */
    }

    while (dsys_dir_next(prod_it, &entry)) {
        if (!entry.is_dir) {
            continue;
        }
        std::string product_id = entry.name;
        std::string product_root = join(m_paths.products, product_id);
        dsys_dir_iter *ver_it = dsys_dir_open(product_root.c_str());
        dsys_dir_entry ver_entry;
        while (ver_it && dsys_dir_next(ver_it, &ver_entry)) {
            if (!ver_entry.is_dir) {
                continue;
            }
            std::string version = ver_entry.name;
            std::string bin_dir = join(join(product_root, version), "bin");
            dsys_dir_iter *bin_it = dsys_dir_open(bin_dir.c_str());
            dsys_dir_entry bin_entry;
            while (bin_it && dsys_dir_next(bin_it, &bin_entry)) {
                if (bin_entry.is_dir) {
                    continue;
                }
                if (!is_product_entry_file(bin_entry.name)) {
                    continue;
                }
                ProductEntry p;
                p.product = product_id;
                p.version = version;
                p.path = join(bin_dir, bin_entry.name);
                m_products.push_back(p);
            }
            if (bin_it) {
                dsys_dir_close(bin_it);
            }
        }
        if (ver_it) {
            dsys_dir_close(ver_it);
        }
    }

    dsys_dir_close(prod_it);

    /* Dev fallback: use in-tree build outputs when product catalog is absent. */
    if (!find_product_entry("game")) {
        std::string dbg = join(m_paths.root, "build/source/dominium/game/Debug/dominium_game.exe");
        std::string rel = join(m_paths.root, "build/source/dominium/game/Release/dominium_game.exe");
        ProductEntry p;
        if (file_exists(dbg)) {
            p.product = "game";
            p.version = "dev-debug";
            p.path = dbg;
            m_products.push_back(p);
        } else if (file_exists(rel)) {
            p.product = "game";
            p.version = "dev-release";
            p.path = rel;
            m_products.push_back(p);
        }
    }
    if (!m_products.empty()) {
        sort_products_deterministic(m_products);
    }
    return true;
}

bool DomLauncherApp::scan_instances() {
    dsys_dir_iter *inst_it;
    dsys_dir_entry entry;

    m_instances.clear();
    inst_it = dsys_dir_open(m_paths.instances.c_str());
    if (!inst_it) {
        return true;
    }

    while (dsys_dir_next(inst_it, &entry)) {
        if (!entry.is_dir) {
            continue;
        }
        InstanceInfo inst;
        inst.id = entry.name;
        if (!dom::launcher_core::launcher_is_safe_id_component(inst.id)) {
            continue;
        }
        {
            const std::string manifest_path = join(join(m_paths.instances, inst.id), "manifest.tlv");
            if (!file_exists(manifest_path)) {
                continue;
            }
        }
        m_instances.push_back(inst);
    }

    dsys_dir_close(inst_it);
    if (m_selected_instance < 0 && !m_instances.empty()) {
        m_selected_instance = 0;
    }
    return true;
}

bool DomLauncherApp::perform_cli_action(const LauncherConfig &cfg) {
    if (cfg.action == "list-instances") {
        return launcher_action_list_instances(m_instances);
    }
    if (cfg.action == "list-products") {
        return launcher_action_list_products(m_products);
    }
    if (cfg.action == "launch") {
        return launcher_action_launch(*this, cfg);
    }
    if (!cfg.action.empty()) {
        std::printf("Launcher: unknown action '%s'.\n", cfg.action.c_str());
        return false;
    }
    /* No action: nothing to do in CLI mode. */
    return true;
}

const dui_api_v1* DomLauncherApp::select_dui_api(std::string& out_backend_name, std::string& out_err) {
    dom_hw_caps hw;
    dom_selection sel;
    dom_caps_result sel_rc;
    u32 i;
    const char* chosen = (const char*)0;

    out_backend_name.clear();
    out_err.clear();

    (void)dom_caps_register_builtin_backends();
    (void)dom_caps_finalize_registry();

    std::memset(&hw, 0, sizeof(hw));
    hw.abi_version = DOM_CAPS_ABI_VERSION;
    hw.struct_size = (u32)sizeof(hw);
    (void)dom_hw_caps_probe_host(&hw);

    std::memset(&sel, 0, sizeof(sel));
    sel.abi_version = DOM_CAPS_ABI_VERSION;
    sel.struct_size = (u32)sizeof(sel);

    sel_rc = dom_caps_select(m_profile_valid ? &m_profile : (const dom_profile*)0, &hw, &sel);
    if (sel_rc != DOM_CAPS_OK) {
        out_err = "caps selection failed";
        return (const dui_api_v1*)0;
    }

    for (i = 0u; i < sel.entry_count; ++i) {
        const dom_selection_entry* e = &sel.entries[i];
        if (e->subsystem_id == DOM_SUBSYS_DUI) {
            chosen = e->backend_name;
            break;
        }
    }
    if (!chosen || !chosen[0]) {
        out_err = "caps selection produced empty ui backend";
        return (const dui_api_v1*)0;
    }

    out_backend_name = chosen;
    return lookup_dui_api_by_backend_name(chosen, out_err);
}

bool DomLauncherApp::load_dui_schema(std::vector<unsigned char>& out_schema,
                                    std::string& out_loaded_path,
                                    std::string& out_error) const {
    std::string err;
    std::vector<std::string> candidates;
    std::string cur;
    int i;

    out_schema.clear();
    out_loaded_path.clear();
    out_error.clear();

    candidates.push_back("source/dominium/launcher/ui_schema/launcher_ui_v1.tlv");
    candidates.push_back("source\\dominium\\launcher\\ui_schema\\launcher_ui_v1.tlv");
    candidates.push_back("ui_schema/launcher_ui_v1.tlv");
    candidates.push_back("ui_schema\\launcher_ui_v1.tlv");
    candidates.push_back("launcher_ui_v1.tlv");

    for (i = 0; i < (int)candidates.size(); ++i) {
        if (file_exists_stdio(candidates[(size_t)i])) {
            if (!read_file_all_bytes(candidates[(size_t)i], out_schema, err)) {
                out_error = std::string("schema_read_failed;path=") + candidates[(size_t)i] + ";err=" + err;
                return false;
            }
            out_loaded_path = candidates[(size_t)i];
            return true;
        }
    }

    cur = dirname_of(m_argv0.empty() ? std::string() : m_argv0);
    for (i = 0; i < 10; ++i) {
        if (!cur.empty()) {
            const std::string c0 = path_join(cur, "source/dominium/launcher/ui_schema/launcher_ui_v1.tlv");
            const std::string c1 = path_join(cur, "ui_schema/launcher_ui_v1.tlv");
            const std::string c2 = path_join(cur, "launcher_ui_v1.tlv");
            if (file_exists_stdio(c0) && read_file_all_bytes(c0, out_schema, err)) {
                out_loaded_path = c0;
                return true;
            }
            if (file_exists_stdio(c1) && read_file_all_bytes(c1, out_schema, err)) {
                out_loaded_path = c1;
                return true;
            }
            if (file_exists_stdio(c2) && read_file_all_bytes(c2, out_schema, err)) {
                out_loaded_path = c2;
                return true;
            }
        }
        cur = dirname_of(cur);
        if (cur.empty()) {
            break;
        }
    }

    out_error = "schema_not_found";
    return false;
}

static std::string dom_u32_arg(const char *prefix, unsigned v) {
    char buf[64];
    std::snprintf(buf, sizeof(buf), "%s%u", prefix ? prefix : "", (unsigned)v);
    return std::string(buf);
}

bool DomLauncherApp::spawn_product_args(const std::string &product,
                                       const std::vector<std::string> &args,
                                       bool wait_for_exit) {
    ProductEntry *entry = find_product_entry(product);
    size_t i;
    std::string instance_id;
    dom::LaunchTarget target;
    dom::launcher_core::LauncherLaunchOverrides ov;
    dom::LaunchRunResult lr;

    if (!entry) {
        if (m_ui) m_ui->status_text = "Launch failed: product not found.";
        return false;
    }

    for (i = 0u; i < args.size(); ++i) {
        if (args[i].compare(0u, 11u, "--instance=") == 0) {
            instance_id = args[i].substr(11u);
            break;
        }
    }

    if (instance_id.empty()) {
        if (m_ui) m_ui->status_text = "Launch failed: missing --instance.";
        return false;
    }
    if (product == "game") {
        target.is_tool = 0u;
    } else {
        if (!dom::launcher_core::launcher_is_safe_id_component(product)) {
            if (m_ui) m_ui->status_text = "Launch failed: unsafe tool id.";
            return false;
        }
        target.is_tool = 1u;
        target.tool_id = product;
    }

    std::printf("Launcher: spawning %s (%s)\n",
                entry->path.c_str(), product.c_str());

    ov = dom::launcher_core::LauncherLaunchOverrides();

    if (!dom::launcher_execute_launch_attempt(m_paths.root,
                                              instance_id,
                                              target,
                                              m_profile_valid ? &m_profile : (const dom_profile*)0,
                                              entry->path,
                                              args,
                                              wait_for_exit ? 1u : 0u,
                                              8u,
                                              ov,
                                              lr)) {
        if (m_ui) {
            if (lr.refused) {
                m_ui->status_text = std::string("Refused: ") + lr.refusal_detail;
            } else if (!lr.error.empty()) {
                m_ui->status_text = std::string("Launch failed: ") + lr.error;
            } else {
                m_ui->status_text = "Launch failed.";
            }
        }
        return false;
    }

    if (!wait_for_exit) {
        if (m_ui) m_ui->status_text = "Spawned.";
        return true;
    }

    {
        char buf[64];
        std::snprintf(buf, sizeof(buf), "Process exited (%d).", (int)lr.child_exit_code);
        if (m_ui) m_ui->status_text = buf;
    }
    return lr.ok != 0u;
}

bool DomLauncherApp::launch_product(const std::string &product,
                                    const std::string &instance_id,
                                    const std::string &mode) {
    std::vector<std::string> args;
    args.push_back(std::string("--mode=") + (mode.empty() ? "gui" : mode));
    if (!instance_id.empty()) {
        args.push_back(std::string("--instance=") + instance_id);
    }
    args.push_back(dom_u32_arg("--keep_last_runs=", 8u));
    return spawn_product_args(product, args, true);
}

bool DomLauncherApp::init_gui(const LauncherConfig &cfg) {
    std::string backend;
    std::string err;
    std::vector<unsigned char> schema;
    std::vector<unsigned char> state;
    std::string schema_path;

    (void)cfg;

    shutdown();

    m_ui_backend_selected.clear();
    m_ui_caps_selected = 0u;
    m_ui_fallback_note.clear();

    if (m_ui) {
        m_ui->status_text = "Initializing UI...";
        m_ui->status_progress = 0u;
    }

    m_dui_api = select_dui_api(backend, err);
    if (!m_dui_api) {
        std::printf("Launcher: DUI selection failed: %s\n", err.empty() ? "unknown" : err.c_str());
        return false;
    }

    {
        const char* initial_name;
        const char* candidates[3];
        u32 cand_count = 0u;
        u32 cand_i;

        initial_name = (m_dui_api->backend_name && m_dui_api->backend_name()) ? m_dui_api->backend_name() : backend.c_str();

        candidates[cand_count++] = initial_name;
        if (!str_ieq(initial_name, "null") && !str_ieq(initial_name, "dgfx")) {
            candidates[cand_count++] = "dgfx";
        }
        if (!str_ieq(initial_name, "null")) {
            candidates[cand_count++] = "null";
        }

        for (cand_i = 0u; cand_i < cand_count; ++cand_i) {
            const char* want = candidates[cand_i];
            const dui_api_v1* api = m_dui_api;
            std::string lookup_err;
            dui_result rc;
            dui_window_desc_v1 wdesc;

            if (cand_i != 0u) {
                api = lookup_dui_api_by_backend_name(want, lookup_err);
                if (!api) {
                    continue;
                }
            }

            if (api->create_context(&m_dui_ctx) != DUI_OK || !m_dui_ctx) {
                continue;
            }

            std::memset(&wdesc, 0, sizeof(wdesc));
            wdesc.abi_version = DUI_API_ABI_VERSION;
            wdesc.struct_size = (u32)sizeof(wdesc);
            wdesc.title = "Dominium Dev Launcher";
            wdesc.width = 960;
            wdesc.height = 640;
            wdesc.flags = 0u;

            rc = api->create_window(m_dui_ctx, &wdesc, &m_dui_win);
            if (rc != DUI_OK || !m_dui_win) {
                api->destroy_context(m_dui_ctx);
                m_dui_ctx = 0;
                m_dui_win = 0;
                continue;
            }

            m_dui_api = api;
            m_ui_backend_selected = (m_dui_api->backend_name && m_dui_api->backend_name()) ? m_dui_api->backend_name() : want;
            m_ui_caps_selected = m_dui_api->get_caps ? m_dui_api->get_caps() : 0u;

            if (cand_i != 0u) {
                m_ui_fallback_note = std::string("ui_fallback=") + initial_name + "->" + m_ui_backend_selected;
            }
            break;
        }
    }

    if (!m_dui_api || !m_dui_ctx || !m_dui_win) {
        std::printf("Launcher: DUI init failed.\n");
        shutdown();
        return false;
    }

    if (!load_dui_schema(schema, schema_path, err)) {
        std::printf("Launcher: failed to load DUI schema: %s\n", err.empty() ? "unknown" : err.c_str());
        shutdown();
        return false;
    }

    if (m_dui_api->set_schema_tlv(m_dui_win, schema.empty() ? (const void*)0 : &schema[0], (u32)schema.size()) != DUI_OK) {
        std::printf("Launcher: DUI set_schema_tlv failed.\n");
        shutdown();
        return false;
    }

    if (!build_dui_state(state)) {
        std::printf("Launcher: failed to build DUI state.\n");
        shutdown();
        return false;
    }
    (void)m_dui_api->set_state_tlv(m_dui_win, state.empty() ? (const void*)0 : &state[0], (u32)state.size());
    (void)m_dui_api->render(m_dui_win);

    if (m_ui) {
        m_ui->status_text = std::string("Ready. Schema=") + schema_path;
        m_ui->status_progress = 0u;
    }

    m_running = true;
    return true;
}

void DomLauncherApp::gui_loop() {
    while (m_running) {
        std::vector<unsigned char> state;
        if (!m_dui_api || !m_dui_ctx) {
            m_running = false;
            break;
        }

        (void)m_dui_api->pump(m_dui_ctx);
        process_dui_events();
        if (!m_running) {
            break;
        }

        if (build_dui_state(state)) {
            (void)m_dui_api->set_state_tlv(m_dui_win, state.empty() ? (const void*)0 : &state[0], (u32)state.size());
        }
        (void)m_dui_api->render(m_dui_win);
        dsys_sleep_ms(16);
    }
}

void DomLauncherApp::process_dui_events() {
    dui_event_v1 ev;
    if (!m_dui_api || !m_dui_ctx || !m_ui) {
        return;
    }
    std::memset(&ev, 0, sizeof(ev));
    while (m_dui_api->poll_event(m_dui_ctx, &ev) > 0) {
        if (ev.type == (u32)DUI_EVENT_QUIT) {
            m_running = false;
            return;
        }
        if (ev.type == (u32)DUI_EVENT_ACTION) {
            const u32 act = ev.u.action.action_id;
            if (act == (u32)ACT_TAB_PLAY) {
                m_ui->tab = (u32)DomLauncherUiState::TAB_PLAY;
            } else if (act == (u32)ACT_TAB_INST) {
                m_ui->tab = (u32)DomLauncherUiState::TAB_INSTANCES;
            } else if (act == (u32)ACT_TAB_PACKS) {
                m_ui->tab = (u32)DomLauncherUiState::TAB_PACKS;
            } else if (act == (u32)ACT_TAB_OPTIONS) {
                m_ui->tab = (u32)DomLauncherUiState::TAB_OPTIONS;
            } else if (act == (u32)ACT_TAB_LOGS) {
                m_ui->tab = (u32)DomLauncherUiState::TAB_LOGS;
            } else if (act == (u32)ACT_DIALOG_OK || act == (u32)ACT_DIALOG_CANCEL) {
                m_ui->dialog_visible = 0u;
                m_ui->dialog_title.clear();
                m_ui->dialog_text.clear();
                m_ui->dialog_lines.clear();
            }
        } else if (ev.type == (u32)DUI_EVENT_VALUE_CHANGED) {
            const u32 wid = ev.u.value.widget_id;
            const u32 vt = ev.u.value.value_type;

            if (wid == (u32)W_INST_SEARCH && vt == (u32)DUI_VALUE_TEXT) {
                std::string next;
                u32 i;
                for (i = 0u; i < ev.u.value.text_len; ++i) {
                    next.push_back(ev.u.value.text[i]);
                }
                m_ui->instance_search = next;
            } else if (wid == (u32)W_INST_LIST && vt == (u32)DUI_VALUE_LIST) {
                const u32 item_id = ev.u.value.item_id;
                int idx = -1;
                size_t i;
                for (i = 0u; i < m_instances.size(); ++i) {
                    if (stable_item_id(m_instances[i].id) == item_id) {
                        idx = (int)i;
                        break;
                    }
                }
                if (idx >= 0) {
                    set_selected_instance(idx);
                }
            } else if (wid == (u32)W_PLAY_TARGET_LIST && vt == (u32)DUI_VALUE_LIST) {
                m_ui->play_target_item_id = ev.u.value.item_id;
            }
        }

        std::memset(&ev, 0, sizeof(ev));
    }
}

bool DomLauncherApp::build_dui_state(std::vector<unsigned char>& out_state) const {
    std::vector<unsigned char> inner;
    std::vector<ListItem> inst_items;
    u32 inst_selected_id = 0u;
    size_t i;

    if (!m_ui) {
        return false;
    }

    out_state.clear();

    /* Header */
    dui_state_add_text(inner,
                       (u32)W_HEADER_INFO,
                       std::string("ui=") + m_ui_backend_selected +
                           (m_ui_fallback_note.empty() ? std::string() : (std::string(" ") + m_ui_fallback_note)));

    /* Tabs */
    dui_state_add_text(inner, (u32)W_TAB_PLAY_BTN, tab_button_text("Play", m_ui->tab == (u32)DomLauncherUiState::TAB_PLAY));
    dui_state_add_text(inner, (u32)W_TAB_INST_BTN, tab_button_text("Instances", m_ui->tab == (u32)DomLauncherUiState::TAB_INSTANCES));
    dui_state_add_text(inner, (u32)W_TAB_PACKS_BTN, tab_button_text("Packs", m_ui->tab == (u32)DomLauncherUiState::TAB_PACKS));
    dui_state_add_text(inner, (u32)W_TAB_OPTIONS_BTN, tab_button_text("Options", m_ui->tab == (u32)DomLauncherUiState::TAB_OPTIONS));
    dui_state_add_text(inner, (u32)W_TAB_LOGS_BTN, tab_button_text("Logs", m_ui->tab == (u32)DomLauncherUiState::TAB_LOGS));

    /* Tab visibility gates */
    dui_state_add_u32(inner, (u32)W_TAB_PLAY_PANEL, (u32)DUI_VALUE_BOOL, (m_ui->tab == (u32)DomLauncherUiState::TAB_PLAY) ? 1u : 0u);
    dui_state_add_u32(inner, (u32)W_TAB_INST_PANEL, (u32)DUI_VALUE_BOOL, (m_ui->tab == (u32)DomLauncherUiState::TAB_INSTANCES) ? 1u : 0u);
    dui_state_add_u32(inner, (u32)W_TAB_PACKS_PANEL, (u32)DUI_VALUE_BOOL, (m_ui->tab == (u32)DomLauncherUiState::TAB_PACKS) ? 1u : 0u);
    dui_state_add_u32(inner, (u32)W_TAB_OPTIONS_PANEL, (u32)DUI_VALUE_BOOL, (m_ui->tab == (u32)DomLauncherUiState::TAB_OPTIONS) ? 1u : 0u);
    dui_state_add_u32(inner, (u32)W_TAB_LOGS_PANEL, (u32)DUI_VALUE_BOOL, (m_ui->tab == (u32)DomLauncherUiState::TAB_LOGS) ? 1u : 0u);

    /* Dialog */
    dui_state_add_u32(inner, (u32)W_DIALOG_COL, (u32)DUI_VALUE_BOOL, m_ui->dialog_visible ? 1u : 0u);
    dui_state_add_text(inner, (u32)W_DIALOG_TITLE, m_ui->dialog_title);
    dui_state_add_text(inner, (u32)W_DIALOG_TEXT, m_ui->dialog_text);
    {
        std::vector<ListItem> dlg;
        for (i = 0u; i < m_ui->dialog_lines.size(); ++i) {
            dlg.push_back(ListItem((u32)(i + 1u), m_ui->dialog_lines[i]));
        }
        dui_state_add_list(inner, (u32)W_DIALOG_LIST, 0u, dlg);
    }

    /* Instances list + search */
    dui_state_add_text(inner, (u32)W_INST_SEARCH, m_ui->instance_search);
    inst_items.clear();
    inst_items.reserve(m_instances.size());
    for (i = 0u; i < m_instances.size(); ++i) {
        if (!m_ui->instance_search.empty() && !str_contains_ci(m_instances[i].id, m_ui->instance_search)) {
            continue;
        }
        inst_items.push_back(ListItem(stable_item_id(m_instances[i].id), m_instances[i].id));
    }
    if (m_selected_instance >= 0 && m_selected_instance < (int)m_instances.size()) {
        inst_selected_id = stable_item_id(m_instances[(size_t)m_selected_instance].id);
    }
    dui_state_add_list(inner, (u32)W_INST_LIST, inst_selected_id, inst_items);
    {
        char buf[128];
        std::snprintf(buf, sizeof(buf), "Total instances: %u", (unsigned)m_instances.size());
        dui_state_add_text(inner, (u32)W_INST_HINT, buf);
    }

    /* Play tab placeholders */
    {
        const InstanceInfo* inst = selected_instance();
        dui_state_add_text(inner, (u32)W_PLAY_SELECTED, inst ? (std::string("Selected: ") + inst->id) : std::string("Selected: (none)"));
        dui_state_add_text(inner, (u32)W_PLAY_PROFILE, std::string("Profile: ") + (m_profile_valid ? "dom_profile" : "default"));
        dui_state_add_text(inner, (u32)W_PLAY_MANIFEST, std::string("Manifest: (not loaded)"));
        dui_state_add_text(inner, (u32)W_PLAY_LAST_RUN, std::string("Last run: (not loaded)"));
        dui_state_add_u32(inner, (u32)W_PLAY_OFFLINE, (u32)DUI_VALUE_BOOL, 0u);
        {
            std::vector<ListItem> targets;
            targets.push_back(ListItem(1u, "game"));
            dui_state_add_list(inner, (u32)W_PLAY_TARGET_LIST, (m_ui->play_target_item_id ? m_ui->play_target_item_id : 1u), targets);
        }
        {
            std::vector<ListItem> news;
            news.push_back(ListItem(1u, "Local news: add docs/launcher/news.txt"));
            dui_state_add_list(inner, (u32)W_NEWS_LIST, 0u, news);
        }
    }

    /* Instances tab placeholders */
    {
        std::vector<ListItem> paths;
        const InstanceInfo* inst = selected_instance();
        if (inst) {
            paths.push_back(ListItem(1u, std::string("instance_root=") + path_join(path_join(m_paths.root, "instances"), inst->id)));
        }
        dui_state_add_list(inner, (u32)W_INST_PATHS_LIST, 0u, paths);
        dui_state_add_text(inner, (u32)W_INST_IMPORT_PATH, std::string());
        dui_state_add_text(inner, (u32)W_INST_EXPORT_PATH, std::string());
    }

    /* Packs tab placeholders */
    dui_state_add_text(inner, (u32)W_PACKS_LABEL, std::string("Packs / Mods"));
    dui_state_add_list(inner, (u32)W_PACKS_LIST, 0u, std::vector<ListItem>());
    dui_state_add_u32(inner, (u32)W_PACKS_ENABLED, (u32)DUI_VALUE_BOOL, 0u);
    {
        std::vector<ListItem> policies;
        policies.push_back(ListItem(1u, "never"));
        policies.push_back(ListItem(2u, "prompt"));
        policies.push_back(ListItem(3u, "auto"));
        dui_state_add_list(inner, (u32)W_PACKS_POLICY_LIST, 2u, policies);
    }
    dui_state_add_text(inner, (u32)W_PACKS_RESOLVED, std::string());
    dui_state_add_text(inner, (u32)W_PACKS_ERROR, std::string());

    /* Options tab placeholders */
    dui_state_add_list(inner, (u32)W_OPT_GFX_LIST, 0u, std::vector<ListItem>());
    dui_state_add_text(inner, (u32)W_OPT_API_FIELD, std::string());
    {
        std::vector<ListItem> wm;
        wm.push_back(ListItem(1u, "auto"));
        wm.push_back(ListItem(2u, "windowed"));
        wm.push_back(ListItem(3u, "fullscreen"));
        wm.push_back(ListItem(4u, "borderless"));
        dui_state_add_list(inner, (u32)W_OPT_WINMODE_LIST, 1u, wm);
    }
    dui_state_add_text(inner, (u32)W_OPT_WIDTH_FIELD, std::string());
    dui_state_add_text(inner, (u32)W_OPT_HEIGHT_FIELD, std::string());
    dui_state_add_text(inner, (u32)W_OPT_DPI_FIELD, std::string());
    dui_state_add_text(inner, (u32)W_OPT_MONITOR_FIELD, std::string());
    dui_state_add_text(inner, (u32)W_OPT_AUDIO_LABEL, std::string("Audio device: not supported"));
    dui_state_add_text(inner, (u32)W_OPT_INPUT_LABEL, std::string("Input backend: not supported"));

    /* Logs tab placeholders */
    dui_state_add_text(inner, (u32)W_LOGS_LAST_RUN, std::string("Last run: (not loaded)"));
    dui_state_add_list(inner, (u32)W_LOGS_RUNS_LIST, 0u, std::vector<ListItem>());
    dui_state_add_list(inner, (u32)W_LOGS_AUDIT_LIST, 0u, std::vector<ListItem>());
    dui_state_add_text(inner, (u32)W_LOGS_DIAG_OUT, std::string());
    dui_state_add_list(inner, (u32)W_LOGS_LOCS_LIST, 0u, std::vector<ListItem>());

    /* Status bar */
    dui_state_add_text(inner, (u32)W_STATUS_TEXT, m_ui->status_text);
    dui_state_add_u32(inner, (u32)W_STATUS_PROGRESS, (u32)DUI_VALUE_U32, (m_ui->status_progress > 1000u) ? 1000u : m_ui->status_progress);
    {
        std::string summary = std::string("instance=") + (selected_instance() ? selected_instance()->id : std::string("(none)"));
        summary += std::string(" ui=") + m_ui_backend_selected;
        dui_state_add_text(inner, (u32)W_STATUS_SELECTION, summary);
    }

    append_tlv_raw(out_state, DUI_TLV_STATE_V1, inner.empty() ? (const void*)0 : &inner[0], inner.size());
    return true;
}

} // namespace dom
