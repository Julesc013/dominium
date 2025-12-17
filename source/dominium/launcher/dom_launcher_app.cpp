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
#include <map>
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
#include "core/include/launcher_core_api.h"
#include "core/include/launcher_instance.h"
#include "core/include/launcher_instance_ops.h"
#include "core/include/launcher_instance_config.h"
#include "core/include/launcher_instance_launch_history.h"
#include "core/include/launcher_instance_tx.h"
#include "core/include/launcher_artifact_store.h"
#include "core/include/launcher_pack_resolver.h"
#include "core/include/launcher_pack_ops.h"
#include "core/include/launcher_instance_artifact_ops.h"
#include "core/include/launcher_tools_registry.h"
#include "core/include/launcher_audit.h"

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
    u32 play_offline; /* 0/1 */

    /* Instances tab inputs */
    std::string inst_import_path;
    std::string inst_export_path;

    /* Packs tab state */
    u32 packs_selected_item_id;
    std::string packs_selected_key;
    struct StagedPackChange {
        u32 has_enabled;
        u32 enabled; /* 0/1 */
        u32 has_update_policy;
        u32 update_policy; /* LauncherUpdatePolicy */
        StagedPackChange() : has_enabled(0u), enabled(0u), has_update_policy(0u), update_policy(0u) {}
    };
    std::map<std::string, StagedPackChange> packs_staged;

    /* Options tab edit buffers (text fields) */
    u32 opt_gfx_selected_item_id;
    u32 opt_winmode_selected_item_id;
    std::string opt_renderer_api_text;
    std::string opt_width_text;
    std::string opt_height_text;
    std::string opt_dpi_text;
    std::string opt_monitor_text;

    /* Logs/Diagnostics tab inputs */
    std::string logs_diag_out_path;
    u32 logs_selected_run_item_id;
    std::string logs_selected_run_id;
    std::vector<std::string> logs_selected_audit_lines;

    /* Local news lines (loaded once) */
    u32 news_loaded;
    std::vector<std::string> news_lines;

    u32 dialog_visible;
    std::string dialog_title;
    std::string dialog_text;
    std::vector<std::string> dialog_lines;

    std::string status_text;
    u32 status_progress; /* 0..1000 */

    enum UiTaskKind {
        TASK_NONE = 0,
        TASK_LAUNCH = 1,
        TASK_VERIFY_REPAIR = 2,
        TASK_INSTANCE_CREATE = 3,
        TASK_INSTANCE_CLONE = 4,
        TASK_INSTANCE_DELETE = 5,
        TASK_INSTANCE_IMPORT = 6,
        TASK_INSTANCE_EXPORT = 7,
        TASK_INSTANCE_MARK_KG = 8,
        TASK_PACKS_APPLY = 9,
        TASK_OPTIONS_RESET = 10,
        TASK_DIAG_BUNDLE = 11
    };

    struct UiTask {
        u32 kind;
        u32 step;
        u32 total_steps;

        std::string op;
        std::string instance_id;
        std::string aux_id;
        std::string path;
        u32 flag_u32;
        u32 safe_mode;

        LaunchRunResult launch_result;

        std::map<std::string, StagedPackChange> packs_changes;

        launcher_core::LauncherInstanceTx tx;
        launcher_core::LauncherInstanceManifest after_manifest;

        std::string error;
        std::vector<std::string> lines;

        UiTask()
            : kind(0u),
              step(0u),
              total_steps(0u),
              op(),
              instance_id(),
              aux_id(),
              path(),
              flag_u32(0u),
              safe_mode(0u),
              launch_result(),
              packs_changes(),
              tx(),
              after_manifest(),
              error(),
              lines() {}
    };

    UiTask task;
    u32 confirm_action_id;
    std::string confirm_instance_id;

    /* Selected instance cache (refreshed on selection + after ops). */
    std::string cache_instance_id;
    u32 cache_valid;
    std::string cache_error;
    launcher_core::LauncherInstanceManifest cache_manifest;
    u64 cache_manifest_hash64;
    launcher_core::LauncherInstanceConfig cache_config;
    launcher_core::LauncherInstanceLaunchHistory cache_history;
    std::vector<std::string> cache_run_ids;
    std::string cache_resolved_packs_summary;
    std::string cache_resolved_packs_error;
    std::vector<launcher_core::LauncherToolEntry> cache_tools;
    std::string cache_tools_error;

    DomLauncherUiState()
        : tab((u32)TAB_PLAY),
          instance_search(),
          play_target_item_id(0u),
          play_offline(0u),
          inst_import_path(),
          inst_export_path(),
          packs_selected_item_id(0u),
          packs_selected_key(),
          packs_staged(),
          opt_gfx_selected_item_id(0u),
          opt_winmode_selected_item_id(0u),
          opt_renderer_api_text(),
          opt_width_text(),
          opt_height_text(),
          opt_dpi_text(),
          opt_monitor_text(),
          logs_diag_out_path(),
          logs_selected_run_item_id(0u),
          logs_selected_run_id(),
          logs_selected_audit_lines(),
          news_loaded(0u),
          news_lines(),
          dialog_visible(0u),
          dialog_title(),
          dialog_text(),
          dialog_lines(),
          status_text("Ready."),
          status_progress(0u),
          task(),
          confirm_action_id(0u),
          confirm_instance_id(),
          cache_instance_id(),
          cache_valid(0u),
          cache_error(),
          cache_manifest(),
          cache_manifest_hash64(0ull),
          cache_config(),
          cache_history(),
          cache_run_ids(),
          cache_resolved_packs_summary(),
          cache_resolved_packs_error(),
          cache_tools(),
          cache_tools_error() {}
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
    W_PLAY_BTN = 1416,
    W_SAFE_PLAY_BTN = 1417,
    W_VERIFY_BTN = 1418,
    W_PLAY_LAST_RUN = 1419,
    W_NEWS_LIST = 1451,

    W_INST_CREATE_BTN = 1501,
    W_INST_CLONE_BTN = 1502,
    W_INST_DELETE_BTN = 1503,
    W_INST_IMPORT_PATH = 1505,
    W_INST_IMPORT_BTN = 1506,
    W_INST_EXPORT_PATH = 1508,
    W_INST_EXPORT_DEF_BTN = 1509,
    W_INST_EXPORT_BUNDLE_BTN = 1510,
    W_INST_MARK_KG_BTN = 1511,
    W_INST_PATHS_LIST = 1512,

    W_PACKS_LABEL = 1600,
    W_PACKS_LIST = 1601,
    W_PACKS_ENABLED = 1602,
    W_PACKS_POLICY_LIST = 1604,
    W_PACKS_APPLY_BTN = 1605,
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
    W_OPT_RESET_BTN = 1714,
    W_OPT_DETAILS_BTN = 1715,

    W_LOGS_LAST_RUN = 1801,
    W_LOGS_RUNS_LIST = 1803,
    W_LOGS_AUDIT_LIST = 1804,
    W_LOGS_DIAG_OUT = 1806,
    W_LOGS_DIAG_BTN = 1807,
    W_LOGS_LOCS_LIST = 1809,

    W_STATUS_TEXT = 1901,
    W_STATUS_PROGRESS = 1902,
    W_STATUS_SELECTION = 1903,

    W_DIALOG_COL = 2000,
    W_DIALOG_TITLE = 2001,
    W_DIALOG_TEXT = 2002,
    W_DIALOG_LIST = 2003,
    W_DIALOG_OK = 2005,
    W_DIALOG_CANCEL = 2006
};

/* UI schema action IDs (scripts/gen_launcher_ui_schema_v1.py). */
enum LauncherUiActionId {
    ACT_TAB_PLAY = 100,
    ACT_TAB_INST = 101,
    ACT_TAB_PACKS = 102,
    ACT_TAB_OPTIONS = 103,
    ACT_TAB_LOGS = 104,

    ACT_PLAY = 200,
    ACT_SAFE_PLAY = 201,
    ACT_VERIFY_REPAIR = 202,

    ACT_INST_CREATE = 300,
    ACT_INST_CLONE = 301,
    ACT_INST_DELETE = 302,
    ACT_INST_IMPORT = 303,
    ACT_INST_EXPORT_DEF = 304,
    ACT_INST_EXPORT_BUNDLE = 305,
    ACT_INST_MARK_KG = 306,

    ACT_PACKS_APPLY = 400,

    ACT_OPT_RESET = 500,
    ACT_OPT_DETAILS = 501,

    ACT_LOGS_DIAG = 600,

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

static void sort_strings_deterministic(std::vector<std::string>& v) {
    size_t i, j;
    for (i = 1u; i < v.size(); ++i) {
        std::string key = v[i];
        j = i;
        while (j > 0u) {
            const std::string& prev = v[j - 1u];
            if (!(prev > key)) {
                break;
            }
            v[j] = v[j - 1u];
            --j;
        }
        v[j] = key;
    }
}

static const char* content_type_to_short(u32 type) {
    switch (type) {
    case (u32)launcher_core::LAUNCHER_CONTENT_PACK: return "pack";
    case (u32)launcher_core::LAUNCHER_CONTENT_MOD: return "mod";
    case (u32)launcher_core::LAUNCHER_CONTENT_RUNTIME: return "runtime";
    case (u32)launcher_core::LAUNCHER_CONTENT_ENGINE: return "engine";
    case (u32)launcher_core::LAUNCHER_CONTENT_GAME: return "game";
    default: return "content";
    }
}

static std::string update_policy_to_string(u32 policy) {
    switch (policy) {
    case (u32)launcher_core::LAUNCHER_UPDATE_NEVER: return "never";
    case (u32)launcher_core::LAUNCHER_UPDATE_PROMPT: return "prompt";
    case (u32)launcher_core::LAUNCHER_UPDATE_AUTO: return "auto";
    default: return "unknown";
    }
}

static u32 update_policy_item_id(u32 policy) {
    return stable_item_id(update_policy_to_string(policy));
}

static u32 update_policy_from_item_id(u32 item_id, u32 fallback_policy) {
    if (item_id == stable_item_id("never")) return (u32)launcher_core::LAUNCHER_UPDATE_NEVER;
    if (item_id == stable_item_id("prompt")) return (u32)launcher_core::LAUNCHER_UPDATE_PROMPT;
    if (item_id == stable_item_id("auto")) return (u32)launcher_core::LAUNCHER_UPDATE_AUTO;
    return fallback_policy;
}

static u32 window_mode_item_id(u32 mode) {
    switch (mode) {
    case (u32)launcher_core::LAUNCHER_WINDOW_MODE_WINDOWED: return stable_item_id("windowed");
    case (u32)launcher_core::LAUNCHER_WINDOW_MODE_FULLSCREEN: return stable_item_id("fullscreen");
    case (u32)launcher_core::LAUNCHER_WINDOW_MODE_BORDERLESS: return stable_item_id("borderless");
    case (u32)launcher_core::LAUNCHER_WINDOW_MODE_AUTO:
    default:
        return stable_item_id("auto");
    }
}

static u32 window_mode_from_item_id(u32 item_id, u32 fallback_mode) {
    if (item_id == stable_item_id("auto")) return (u32)launcher_core::LAUNCHER_WINDOW_MODE_AUTO;
    if (item_id == stable_item_id("windowed")) return (u32)launcher_core::LAUNCHER_WINDOW_MODE_WINDOWED;
    if (item_id == stable_item_id("fullscreen")) return (u32)launcher_core::LAUNCHER_WINDOW_MODE_FULLSCREEN;
    if (item_id == stable_item_id("borderless")) return (u32)launcher_core::LAUNCHER_WINDOW_MODE_BORDERLESS;
    return fallback_mode;
}

static bool is_pack_like(u32 content_type) {
    return content_type == (u32)launcher_core::LAUNCHER_CONTENT_PACK ||
           content_type == (u32)launcher_core::LAUNCHER_CONTENT_MOD ||
           content_type == (u32)launcher_core::LAUNCHER_CONTENT_RUNTIME;
}

static std::string pack_key(u32 content_type, const std::string& id) {
    return std::string(content_type_to_short(content_type)) + ":" + id;
}

static const launcher_core::LauncherContentEntry* find_entry_by_pack_key(const launcher_core::LauncherInstanceManifest& m,
                                                                         const std::string& key) {
    size_t i;
    for (i = 0u; i < m.content_entries.size(); ++i) {
        const launcher_core::LauncherContentEntry& e = m.content_entries[i];
        if (!is_pack_like(e.type)) {
            continue;
        }
        if (pack_key(e.type, e.id) == key) {
            return &m.content_entries[i];
        }
    }
    return (const launcher_core::LauncherContentEntry*)0;
}

static void collect_dgfx_backend_names(std::vector<std::string>& out_names) {
    u32 i;
    u32 count;
    dom_backend_desc desc;

    out_names.clear();

    (void)dom_caps_register_builtin_backends();
    (void)dom_caps_finalize_registry();

    count = dom_caps_backend_count();
    for (i = 0u; i < count; ++i) {
        if (dom_caps_backend_get(i, &desc) != DOM_CAPS_OK) {
            continue;
        }
        if (desc.subsystem_id != DOM_SUBSYS_DGFX) {
            continue;
        }
        if (!desc.backend_name || !desc.backend_name[0]) {
            continue;
        }
        out_names.push_back(std::string(desc.backend_name));
    }
    sort_strings_deterministic(out_names);
    {
        size_t out = 0u;
        for (i = 0u; i < out_names.size(); ++i) {
            if (out == 0u || out_names[i] != out_names[out - 1u]) {
                out_names[out++] = out_names[i];
            }
        }
        out_names.resize(out);
    }
}

static std::string dgfx_backend_from_item_id(u32 item_id) {
    std::vector<std::string> names;
    size_t i;
    collect_dgfx_backend_names(names);
    for (i = 0u; i < names.size(); ++i) {
        if (stable_item_id(std::string("dgfx:") + names[i]) == item_id) {
            return names[i];
        }
    }
    return std::string();
}

#if defined(_WIN32) || defined(_WIN64)
static std::string add_exe_if_missing(const std::string& p) {
    if (ends_with_ci(p.c_str(), ".exe")) {
        return p;
    }
    return p + ".exe";
}
#else
static std::string add_exe_if_missing(const std::string& p) { return p; }
#endif

static bool parse_u32_decimal(const std::string& s, u32& out_v) {
    size_t i;
    out_v = 0u;
    if (s.empty()) {
        return true;
    }
    for (i = 0u; i < s.size(); ++i) {
        const char c = s[i];
        u32 digit;
        if (c < '0' || c > '9') {
            return false;
        }
        digit = (u32)(c - '0');
        if (out_v > (0xffffffffu - digit) / 10u) {
            return false;
        }
        out_v = out_v * 10u + digit;
    }
    return true;
}

static bool instance_id_exists(const std::vector<InstanceInfo>& instances, const std::string& id) {
    size_t i;
    for (i = 0u; i < instances.size(); ++i) {
        if (instances[i].id == id) {
            return true;
        }
    }
    return false;
}

static std::string make_unique_instance_id(const std::vector<InstanceInfo>& instances,
                                           const std::string& base,
                                           const std::string& suffix) {
    u32 n;
    std::string b = base.empty() ? std::string("instance") : base;
    std::string s = suffix.empty() ? std::string("new") : suffix;
    if (b.size() > 48u) {
        b.erase(48u);
    }
    if (s.size() > 16u) {
        s.erase(16u);
    }
    for (n = 1u; n < 10000u; ++n) {
        char buf[32];
        std::snprintf(buf, sizeof(buf), "%u", (unsigned)n);
        std::string cand = b + "_" + s + std::string(buf);
        if (!launcher_core::launcher_is_safe_id_component(cand)) {
            continue;
        }
        if (!instance_id_exists(instances, cand)) {
            return cand;
        }
    }
    return b + "_" + s + "x";
}

static bool resolve_tool_executable_path(const std::string& state_root,
                                        const std::string& argv0,
                                        const launcher_core::LauncherToolEntry& te,
                                        std::string& out_path) {
    std::string artifact_dir;
    std::string meta_path;
    std::string payload_path;

    out_path.clear();

    if (!te.executable_artifact_hash_bytes.empty() &&
        launcher_core::launcher_artifact_store_paths(state_root,
                                                     te.executable_artifact_hash_bytes,
                                                     artifact_dir,
                                                     meta_path,
                                                     payload_path) &&
        file_exists_stdio(payload_path)) {
        out_path = payload_path;
        return true;
    }

    {
        const std::string dir = dirname_of(argv0);
        if (!dir.empty()) {
            const std::string cand0 = path_join(dir, te.tool_id);
            const std::string cand1 = add_exe_if_missing(cand0);
            if (file_exists_stdio(cand0)) {
                out_path = cand0;
                return true;
            }
            if (file_exists_stdio(cand1)) {
                out_path = cand1;
                return true;
            }

            if (te.tool_id.compare(0u, 5u, "tool_") != 0) {
                const std::string pref = std::string("tool_") + te.tool_id;
                const std::string cand2 = path_join(dir, pref);
                const std::string cand3 = add_exe_if_missing(cand2);
                if (file_exists_stdio(cand2)) {
                    out_path = cand2;
                    return true;
                }
                if (file_exists_stdio(cand3)) {
                    out_path = cand3;
                    return true;
                }
            }
        }
    }

    out_path = add_exe_if_missing(te.tool_id);
    return true;
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

static std::string u64_hex16(u64 v) {
    static const char* hex = "0123456789abcdef";
    char buf[17];
    int i;
    for (i = 0; i < 16; ++i) {
        unsigned shift = (unsigned)((15 - i) * 4);
        unsigned nib = (unsigned)((v >> shift) & (u64)0xFu);
        buf[i] = hex[nib & 0xFu];
    }
    buf[16] = '\0';
    return std::string(buf);
}

static std::string u32_to_string(u32 v) {
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%u", (unsigned)v);
    return std::string(buf);
}

static std::string i32_to_string(i32 v) {
    char buf[32];
    std::snprintf(buf, sizeof(buf), "%d", (int)v);
    return std::string(buf);
}

static void split_lines_limit(const std::string& text, size_t max_lines, std::vector<std::string>& out_lines) {
    size_t pos = 0u;
    out_lines.clear();
    while (pos < text.size() && out_lines.size() < max_lines) {
        size_t eol = text.find('\n', pos);
        if (eol == std::string::npos) {
            eol = text.size();
        }
        std::string line = text.substr(pos, eol - pos);
        if (!line.empty() && line[line.size() - 1u] == '\r') {
            line.erase(line.size() - 1u);
        }
        out_lines.push_back(line);
        pos = (eol < text.size()) ? (eol + 1u) : text.size();
    }
}

static void ui_load_news_if_needed(DomLauncherUiState& ui, const std::string& argv0) {
    std::vector<unsigned char> bytes;
    std::string err;
    std::string cur;
    std::string text;
    size_t i;

    if (ui.news_loaded) {
        return;
    }
    ui.news_loaded = 1u;
    ui.news_lines.clear();

    /* Try CWD first. */
    if (file_exists_stdio("docs/launcher/news.txt") && read_file_all_bytes("docs/launcher/news.txt", bytes, err)) {
        text.assign(bytes.empty() ? "" : (const char*)&bytes[0], bytes.size());
        split_lines_limit(text, 200u, ui.news_lines);
        return;
    }

    /* Walk upwards from argv0 directory. */
    cur = dirname_of(argv0);
    for (i = 0u; i < 10u; ++i) {
        if (!cur.empty()) {
            const std::string cand = path_join(cur, "docs/launcher/news.txt");
            if (file_exists_stdio(cand) && read_file_all_bytes(cand, bytes, err)) {
                text.assign(bytes.empty() ? "" : (const char*)&bytes[0], bytes.size());
                split_lines_limit(text, 200u, ui.news_lines);
                return;
            }
        }
        cur = dirname_of(cur);
        if (cur.empty()) {
            break;
        }
    }

    ui.news_lines.push_back("No local news file found (docs/launcher/news.txt).");
}

static void ui_load_selected_run_audit(DomLauncherUiState& ui,
                                       const std::string& state_root,
                                       const std::string& instance_id) {
    std::vector<unsigned char> bytes;
    std::string err;
    launcher_core::LauncherAuditLog audit;

    ui.logs_selected_audit_lines.clear();
    if (state_root.empty() || instance_id.empty() || ui.logs_selected_run_id.empty()) {
        return;
    }

    {
        const std::string audit_path =
            path_join(path_join(path_join(path_join(path_join(state_root, "instances"), instance_id), "logs/runs"), ui.logs_selected_run_id),
                      "launcher_audit.tlv");
        if (!read_file_all_bytes(audit_path, bytes, err) || bytes.empty()) {
            ui.logs_selected_audit_lines.push_back(std::string("audit_read_failed;path=") + audit_path + ";err=" + err);
            return;
        }
        if (!launcher_core::launcher_audit_from_tlv_bytes(bytes.empty() ? (const unsigned char*)0 : &bytes[0], bytes.size(), audit)) {
            ui.logs_selected_audit_lines.push_back(std::string("audit_decode_failed;path=") + audit_path);
            return;
        }
    }

    {
        size_t i;
        ui.logs_selected_audit_lines.push_back(std::string("run_id=0x") + u64_hex16(audit.run_id));
        ui.logs_selected_audit_lines.push_back(std::string("exit_result=") + i32_to_string(audit.exit_result));
        for (i = 0u; i < audit.reasons.size(); ++i) {
            ui.logs_selected_audit_lines.push_back(audit.reasons[i]);
        }
    }
}

static void ui_refresh_instance_cache(DomLauncherUiState& ui,
                                      const std::string& state_root,
                                      const std::string& instance_id) {
    const launcher_services_api_v1* services = launcher_services_null_v1();
    launcher_core::LauncherInstancePaths paths;
    std::string run_err;
    launcher_core::LauncherToolsRegistry reg;
    std::string tools_loaded;
    std::string tools_err;
    std::vector<launcher_core::LauncherResolvedPack> resolved;
    std::string resolve_err;

    ui.cache_instance_id = instance_id;
    ui.cache_valid = 0u;
    ui.cache_error.clear();
    ui.cache_manifest = launcher_core::launcher_instance_manifest_make_null();
    ui.cache_manifest_hash64 = 0ull;
    ui.cache_config = launcher_core::launcher_instance_config_make_default(instance_id);
    ui.cache_history = launcher_core::launcher_instance_launch_history_make_default(instance_id, 64u);
    ui.cache_run_ids.clear();
    ui.cache_resolved_packs_summary.clear();
    ui.cache_resolved_packs_error.clear();
    ui.cache_tools.clear();
    ui.cache_tools_error.clear();

    ui.logs_selected_run_item_id = 0u;
    ui.logs_selected_run_id.clear();
    ui.logs_selected_audit_lines.clear();

    if (instance_id.empty() || state_root.empty()) {
        return;
    }

    if (!launcher_core::launcher_instance_load_manifest(services, instance_id, state_root, ui.cache_manifest)) {
        ui.cache_error = "load_manifest_failed";
        return;
    }
    ui.cache_manifest_hash64 = launcher_core::launcher_instance_manifest_hash64(ui.cache_manifest);

    paths = launcher_core::launcher_instance_paths_make(state_root, instance_id);
    if (!launcher_core::launcher_instance_config_load(services, paths, ui.cache_config)) {
        ui.cache_error = "load_config_failed";
    }
    if (!launcher_core::launcher_instance_launch_history_load(services, paths, ui.cache_history)) {
        if (ui.cache_error.empty()) ui.cache_error = "load_launch_history_failed";
    }

    (void)launcher_list_instance_runs(state_root, instance_id, ui.cache_run_ids, run_err);
    if (!ui.cache_run_ids.empty()) {
        ui.logs_selected_run_id = ui.cache_run_ids[ui.cache_run_ids.size() - 1u];
        ui.logs_selected_run_item_id = stable_item_id(ui.logs_selected_run_id);
        ui_load_selected_run_audit(ui, state_root, instance_id);
    }

    if (launcher_core::launcher_tools_registry_load(services, state_root, reg, &tools_loaded, &tools_err)) {
        launcher_core::launcher_tools_registry_enumerate_for_instance(reg, ui.cache_manifest, ui.cache_tools);
    } else {
        ui.cache_tools_error = tools_err;
    }

    if (launcher_core::launcher_pack_resolve_enabled(services, ui.cache_manifest, state_root, resolved, &resolve_err)) {
        ui.cache_resolved_packs_summary = launcher_core::launcher_pack_resolved_order_summary(resolved);
    } else {
        ui.cache_resolved_packs_error = resolve_err;
    }

    ui.play_offline = (ui.cache_config.allow_network == 0u) ? 1u : 0u;
    ui.opt_renderer_api_text = ui.cache_config.renderer_api;
    ui.opt_width_text = ui.cache_config.window_width ? u32_to_string(ui.cache_config.window_width) : std::string();
    ui.opt_height_text = ui.cache_config.window_height ? u32_to_string(ui.cache_config.window_height) : std::string();
    ui.opt_dpi_text = ui.cache_config.window_dpi ? u32_to_string(ui.cache_config.window_dpi) : std::string();
    ui.opt_monitor_text = ui.cache_config.window_monitor ? u32_to_string(ui.cache_config.window_monitor) : std::string();

    ui.cache_valid = 1u;
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
        set_selected_product(0);
    }
    if (m_selected_instance < 0 && !m_instances.empty()) {
        set_selected_instance(0);
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
    if (m_mode == LAUNCHER_MODE_CLI || !m_ui) {
        return;
    }
    {
        const std::string id = m_instances[(size_t)idx].id;
        if (m_ui->cache_instance_id != id) {
            m_ui->packs_staged.clear();
            m_ui->packs_selected_item_id = 0u;
            m_ui->packs_selected_key.clear();
            ui_refresh_instance_cache(*m_ui, m_paths.root, id);
            ui_load_news_if_needed(*m_ui, m_argv0);
            if (m_ui->play_target_item_id == 0u) {
                m_ui->play_target_item_id = stable_item_id(std::string("game"));
            }
        }
    }
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
        set_selected_instance(0);
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
        process_ui_task();

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
            } else if (act == (u32)ACT_PLAY || act == (u32)ACT_SAFE_PLAY) {
                if (m_ui->task.kind != (u32)DomLauncherUiState::TASK_NONE) {
                    m_ui->status_text = std::string("Busy: ") + (m_ui->task.op.empty() ? std::string("operation") : m_ui->task.op);
                } else {
                    const InstanceInfo* inst = selected_instance();
                    if (!inst) {
                        m_ui->status_text = "Refused: no instance selected.";
                    } else {
                        const u32 want = m_ui->play_target_item_id ? m_ui->play_target_item_id : stable_item_id(std::string("game"));
                        DomLauncherUiState::UiTask t;
                        t.kind = (u32)DomLauncherUiState::TASK_LAUNCH;
                        t.step = 0u;
                        t.total_steps = 2u;
                        t.op = (act == (u32)ACT_SAFE_PLAY) ? "Safe Mode Play" : "Play";
                        t.instance_id = inst->id;
                        t.safe_mode = (act == (u32)ACT_SAFE_PLAY) ? 1u : 0u;
                        if (want == stable_item_id(std::string("game"))) {
                            t.flag_u32 = 0u;
                        } else {
                            size_t i;
                            bool found = false;
                            for (i = 0u; i < m_ui->cache_tools.size(); ++i) {
                                const launcher_core::LauncherToolEntry& te = m_ui->cache_tools[i];
                                if (stable_item_id(std::string("tool:") + te.tool_id) == want) {
                                    t.flag_u32 = 1u;
                                    t.aux_id = te.tool_id;
                                    found = true;
                                    break;
                                }
                            }
                            if (!found) {
                                m_ui->status_text = "Refused: target not available for this instance.";
                                std::memset(&ev, 0, sizeof(ev));
                                continue;
                            }
                        }
                        m_ui->task = t;
                        m_ui->status_text = t.op + " started.";
                        m_ui->status_progress = 0u;
                    }
                }
            } else if (act == (u32)ACT_VERIFY_REPAIR) {
                if (m_ui->task.kind != (u32)DomLauncherUiState::TASK_NONE) {
                    m_ui->status_text = std::string("Busy: ") + (m_ui->task.op.empty() ? std::string("operation") : m_ui->task.op);
                } else {
                    const InstanceInfo* inst = selected_instance();
                    if (!inst) {
                        m_ui->status_text = "Refused: no instance selected.";
                    } else {
                        DomLauncherUiState::UiTask t;
                        t.kind = (u32)DomLauncherUiState::TASK_VERIFY_REPAIR;
                        t.step = 0u;
                        t.total_steps = 2u;
                        t.op = "Verify / Repair";
                        t.instance_id = inst->id;
                        m_ui->task = t;
                        m_ui->status_text = "Verify / Repair started.";
                        m_ui->status_progress = 0u;
                    }
                }
            } else if (act == (u32)ACT_INST_CREATE) {
                if (m_ui->task.kind != (u32)DomLauncherUiState::TASK_NONE) {
                    m_ui->status_text = std::string("Busy: ") + (m_ui->task.op.empty() ? std::string("operation") : m_ui->task.op);
                } else {
                    const InstanceInfo* inst = selected_instance();
                    const std::string base = inst ? inst->id : std::string("instance");
                    DomLauncherUiState::UiTask t;
                    t.kind = (u32)DomLauncherUiState::TASK_INSTANCE_CREATE;
                    t.step = 0u;
                    t.total_steps = 2u;
                    t.op = "Create Instance";
                    t.instance_id = inst ? inst->id : std::string();
                    t.aux_id = make_unique_instance_id(m_instances, base, "tmpl");
                    t.flag_u32 = inst ? 1u : 0u; /* 1=template, 0=empty */
                    m_ui->task = t;
                    m_ui->status_text = std::string("Create instance: ") + t.aux_id;
                    m_ui->status_progress = 0u;
                }
            } else if (act == (u32)ACT_INST_CLONE) {
                if (m_ui->task.kind != (u32)DomLauncherUiState::TASK_NONE) {
                    m_ui->status_text = std::string("Busy: ") + (m_ui->task.op.empty() ? std::string("operation") : m_ui->task.op);
                } else {
                    const InstanceInfo* inst = selected_instance();
                    if (!inst) {
                        m_ui->status_text = "Refused: no instance selected.";
                    } else {
                        DomLauncherUiState::UiTask t;
                        t.kind = (u32)DomLauncherUiState::TASK_INSTANCE_CLONE;
                        t.step = 0u;
                        t.total_steps = 2u;
                        t.op = "Clone Instance";
                        t.instance_id = inst->id;
                        t.aux_id = make_unique_instance_id(m_instances, inst->id, "clone");
                        m_ui->task = t;
                        m_ui->status_text = std::string("Clone instance: ") + t.aux_id;
                        m_ui->status_progress = 0u;
                    }
                }
            } else if (act == (u32)ACT_INST_DELETE) {
                if (m_ui->task.kind != (u32)DomLauncherUiState::TASK_NONE) {
                    m_ui->status_text = std::string("Busy: ") + (m_ui->task.op.empty() ? std::string("operation") : m_ui->task.op);
                } else {
                    const InstanceInfo* inst = selected_instance();
                    if (!inst) {
                        m_ui->status_text = "Refused: no instance selected.";
                    } else {
                        m_ui->confirm_action_id = (u32)ACT_INST_DELETE;
                        m_ui->confirm_instance_id = inst->id;
                        m_ui->dialog_visible = 1u;
                        m_ui->dialog_title = "Confirm delete";
                        m_ui->dialog_text = "Delete selected instance (soft delete)?";
                        m_ui->dialog_lines.clear();
                        m_ui->dialog_lines.push_back(std::string("instance_id=") + inst->id);
                    }
                }
            } else if (act == (u32)ACT_INST_IMPORT) {
                if (m_ui->task.kind != (u32)DomLauncherUiState::TASK_NONE) {
                    m_ui->status_text = std::string("Busy: ") + (m_ui->task.op.empty() ? std::string("operation") : m_ui->task.op);
                } else if (m_ui->inst_import_path.empty()) {
                    m_ui->status_text = "Refused: import path is empty.";
                } else {
                    DomLauncherUiState::UiTask t;
                    t.kind = (u32)DomLauncherUiState::TASK_INSTANCE_IMPORT;
                    t.step = 0u;
                    t.total_steps = 2u;
                    t.op = "Import Instance";
                    t.path = m_ui->inst_import_path;
                    t.instance_id = make_unique_instance_id(m_instances, "imported", "imp");
                    t.flag_u32 = (u32)launcher_core::LAUNCHER_INSTANCE_IMPORT_FULL_BUNDLE;
                    m_ui->task = t;
                    m_ui->status_text = std::string("Import instance: ") + t.instance_id;
                    m_ui->status_progress = 0u;
                }
            } else if (act == (u32)ACT_INST_EXPORT_DEF || act == (u32)ACT_INST_EXPORT_BUNDLE) {
                if (m_ui->task.kind != (u32)DomLauncherUiState::TASK_NONE) {
                    m_ui->status_text = std::string("Busy: ") + (m_ui->task.op.empty() ? std::string("operation") : m_ui->task.op);
                } else {
                    const InstanceInfo* inst = selected_instance();
                    if (!inst) {
                        m_ui->status_text = "Refused: no instance selected.";
                    } else if (m_ui->inst_export_path.empty()) {
                        m_ui->status_text = "Refused: export path is empty.";
                    } else {
                        DomLauncherUiState::UiTask t;
                        t.kind = (u32)DomLauncherUiState::TASK_INSTANCE_EXPORT;
                        t.step = 0u;
                        t.total_steps = 1u;
                        t.op = (act == (u32)ACT_INST_EXPORT_DEF) ? "Export Definition" : "Export Bundle";
                        t.instance_id = inst->id;
                        t.path = m_ui->inst_export_path;
                        t.flag_u32 = (act == (u32)ACT_INST_EXPORT_DEF)
                                         ? (u32)launcher_core::LAUNCHER_INSTANCE_EXPORT_DEFINITION_ONLY
                                         : (u32)launcher_core::LAUNCHER_INSTANCE_EXPORT_FULL_BUNDLE;
                        m_ui->task = t;
                        m_ui->status_text = std::string("Exporting to: ") + t.path;
                        m_ui->status_progress = 0u;
                    }
                }
            } else if (act == (u32)ACT_INST_MARK_KG) {
                if (m_ui->task.kind != (u32)DomLauncherUiState::TASK_NONE) {
                    m_ui->status_text = std::string("Busy: ") + (m_ui->task.op.empty() ? std::string("operation") : m_ui->task.op);
                } else {
                    const InstanceInfo* inst = selected_instance();
                    if (!inst) {
                        m_ui->status_text = "Refused: no instance selected.";
                    } else {
                        DomLauncherUiState::UiTask t;
                        t.kind = (u32)DomLauncherUiState::TASK_INSTANCE_MARK_KG;
                        t.step = 0u;
                        t.total_steps = 2u;
                        t.op = "Mark Known Good";
                        t.instance_id = inst->id;
                        m_ui->task = t;
                        m_ui->status_text = "Mark known-good started.";
                        m_ui->status_progress = 0u;
                    }
                }
            } else if (act == (u32)ACT_PACKS_APPLY) {
                if (m_ui->task.kind != (u32)DomLauncherUiState::TASK_NONE) {
                    m_ui->status_text = std::string("Busy: ") + (m_ui->task.op.empty() ? std::string("operation") : m_ui->task.op);
                } else {
                    const InstanceInfo* inst = selected_instance();
                    if (!inst) {
                        m_ui->status_text = "Refused: no instance selected.";
                    } else if (m_ui->packs_staged.empty()) {
                        m_ui->status_text = "Refused: no staged changes.";
                    } else {
                        DomLauncherUiState::UiTask t;
                        t.kind = (u32)DomLauncherUiState::TASK_PACKS_APPLY;
                        t.step = 0u;
                        t.total_steps = 5u;
                        t.op = "Apply Packs";
                        t.instance_id = inst->id;
                        t.packs_changes = m_ui->packs_staged;
                        m_ui->task = t;
                        m_ui->status_text = "Packs apply started.";
                        m_ui->status_progress = 0u;
                    }
                }
            } else if (act == (u32)ACT_DIALOG_OK) {
                const u32 pending = m_ui->confirm_action_id;
                const std::string pending_inst = m_ui->confirm_instance_id;
                m_ui->confirm_action_id = 0u;
                m_ui->confirm_instance_id.clear();
                m_ui->dialog_visible = 0u;
                m_ui->dialog_title.clear();
                m_ui->dialog_text.clear();
                m_ui->dialog_lines.clear();
                if (pending == (u32)ACT_INST_DELETE) {
                    if (m_ui->task.kind != (u32)DomLauncherUiState::TASK_NONE) {
                        m_ui->status_text = std::string("Busy: ") + (m_ui->task.op.empty() ? std::string("operation") : m_ui->task.op);
                    } else if (!pending_inst.empty()) {
                        DomLauncherUiState::UiTask t;
                        t.kind = (u32)DomLauncherUiState::TASK_INSTANCE_DELETE;
                        t.step = 0u;
                        t.total_steps = 2u;
                        t.op = "Delete Instance";
                        t.instance_id = pending_inst;
                        m_ui->task = t;
                        m_ui->status_text = std::string("Delete instance: ") + pending_inst;
                        m_ui->status_progress = 0u;
                    }
                }
            } else if (act == (u32)ACT_DIALOG_CANCEL) {
                m_ui->confirm_action_id = 0u;
                m_ui->confirm_instance_id.clear();
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
            } else if (wid == (u32)W_PLAY_OFFLINE && vt == (u32)DUI_VALUE_BOOL) {
                m_ui->play_offline = ev.u.value.v_u32 ? 1u : 0u;
                m_ui->cache_config.allow_network = m_ui->play_offline ? 0u : 1u;
            } else if (wid == (u32)W_INST_IMPORT_PATH && vt == (u32)DUI_VALUE_TEXT) {
                std::string next;
                u32 i;
                for (i = 0u; i < ev.u.value.text_len; ++i) {
                    next.push_back(ev.u.value.text[i]);
                }
                m_ui->inst_import_path = next;
            } else if (wid == (u32)W_INST_EXPORT_PATH && vt == (u32)DUI_VALUE_TEXT) {
                std::string next;
                u32 i;
                for (i = 0u; i < ev.u.value.text_len; ++i) {
                    next.push_back(ev.u.value.text[i]);
                }
                m_ui->inst_export_path = next;
            } else if (wid == (u32)W_PACKS_LIST && vt == (u32)DUI_VALUE_LIST) {
                const u32 item_id = ev.u.value.item_id;
                const launcher_core::LauncherInstanceManifest& m = m_ui->cache_manifest;
                size_t i;

                m_ui->packs_selected_item_id = item_id;
                m_ui->packs_selected_key.clear();
                for (i = 0u; i < m.content_entries.size(); ++i) {
                    const launcher_core::LauncherContentEntry& e = m.content_entries[i];
                    if (!is_pack_like(e.type)) {
                        continue;
                    }
                    const std::string key = pack_key(e.type, e.id);
                    if (stable_item_id(key) == item_id) {
                        m_ui->packs_selected_key = key;
                        break;
                    }
                }
            } else if (wid == (u32)W_PACKS_ENABLED && vt == (u32)DUI_VALUE_BOOL) {
                const launcher_core::LauncherContentEntry* e =
                    find_entry_by_pack_key(m_ui->cache_manifest, m_ui->packs_selected_key);
                if (e && !m_ui->packs_selected_key.empty()) {
                    const u32 cur_enabled = e->enabled ? 1u : 0u;
                    const u32 next_enabled = ev.u.value.v_u32 ? 1u : 0u;
                    DomLauncherUiState::StagedPackChange& sc = m_ui->packs_staged[m_ui->packs_selected_key];
                    sc.has_enabled = 1u;
                    sc.enabled = next_enabled;
                    if (sc.has_enabled && sc.enabled == cur_enabled) {
                        sc.has_enabled = 0u;
                    }
                    if (!sc.has_enabled && !sc.has_update_policy) {
                        m_ui->packs_staged.erase(m_ui->packs_selected_key);
                    }
                }
            } else if (wid == (u32)W_PACKS_POLICY_LIST && vt == (u32)DUI_VALUE_LIST) {
                const launcher_core::LauncherContentEntry* e =
                    find_entry_by_pack_key(m_ui->cache_manifest, m_ui->packs_selected_key);
                if (e && !m_ui->packs_selected_key.empty()) {
                    const u32 cur_policy = e->update_policy;
                    const u32 next_policy = update_policy_from_item_id(ev.u.value.item_id, cur_policy);
                    DomLauncherUiState::StagedPackChange& sc = m_ui->packs_staged[m_ui->packs_selected_key];
                    sc.has_update_policy = 1u;
                    sc.update_policy = next_policy;
                    if (sc.has_update_policy && sc.update_policy == cur_policy) {
                        sc.has_update_policy = 0u;
                    }
                    if (!sc.has_enabled && !sc.has_update_policy) {
                        m_ui->packs_staged.erase(m_ui->packs_selected_key);
                    }
                }
            } else if (wid == (u32)W_OPT_GFX_LIST && vt == (u32)DUI_VALUE_LIST) {
                const u32 item_id = ev.u.value.item_id;
                m_ui->opt_gfx_selected_item_id = item_id;
                if (item_id == stable_item_id("auto")) {
                    m_ui->cache_config.gfx_backend.clear();
                } else {
                    const std::string name = dgfx_backend_from_item_id(item_id);
                    if (!name.empty()) {
                        m_ui->cache_config.gfx_backend = name;
                    }
                }
            } else if (wid == (u32)W_OPT_API_FIELD && vt == (u32)DUI_VALUE_TEXT) {
                std::string next;
                u32 i;
                for (i = 0u; i < ev.u.value.text_len; ++i) {
                    next.push_back(ev.u.value.text[i]);
                }
                m_ui->opt_renderer_api_text = next;
                m_ui->cache_config.renderer_api = next;
            } else if (wid == (u32)W_OPT_WINMODE_LIST && vt == (u32)DUI_VALUE_LIST) {
                const u32 item_id = ev.u.value.item_id;
                m_ui->opt_winmode_selected_item_id = item_id;
                m_ui->cache_config.window_mode = window_mode_from_item_id(item_id, m_ui->cache_config.window_mode);
            } else if (wid == (u32)W_OPT_WIDTH_FIELD && vt == (u32)DUI_VALUE_TEXT) {
                std::string next;
                u32 i;
                for (i = 0u; i < ev.u.value.text_len; ++i) {
                    next.push_back(ev.u.value.text[i]);
                }
                m_ui->opt_width_text = next;
            } else if (wid == (u32)W_OPT_HEIGHT_FIELD && vt == (u32)DUI_VALUE_TEXT) {
                std::string next;
                u32 i;
                for (i = 0u; i < ev.u.value.text_len; ++i) {
                    next.push_back(ev.u.value.text[i]);
                }
                m_ui->opt_height_text = next;
            } else if (wid == (u32)W_OPT_DPI_FIELD && vt == (u32)DUI_VALUE_TEXT) {
                std::string next;
                u32 i;
                for (i = 0u; i < ev.u.value.text_len; ++i) {
                    next.push_back(ev.u.value.text[i]);
                }
                m_ui->opt_dpi_text = next;
            } else if (wid == (u32)W_OPT_MONITOR_FIELD && vt == (u32)DUI_VALUE_TEXT) {
                std::string next;
                u32 i;
                for (i = 0u; i < ev.u.value.text_len; ++i) {
                    next.push_back(ev.u.value.text[i]);
                }
                m_ui->opt_monitor_text = next;
            } else if (wid == (u32)W_LOGS_DIAG_OUT && vt == (u32)DUI_VALUE_TEXT) {
                std::string next;
                u32 i;
                for (i = 0u; i < ev.u.value.text_len; ++i) {
                    next.push_back(ev.u.value.text[i]);
                }
                m_ui->logs_diag_out_path = next;
            } else if (wid == (u32)W_LOGS_RUNS_LIST && vt == (u32)DUI_VALUE_LIST) {
                const u32 item_id = ev.u.value.item_id;
                size_t i;
                m_ui->logs_selected_run_item_id = item_id;
                m_ui->logs_selected_run_id.clear();
                for (i = 0u; i < m_ui->cache_run_ids.size(); ++i) {
                    if (stable_item_id(m_ui->cache_run_ids[i]) == item_id) {
                        m_ui->logs_selected_run_id = m_ui->cache_run_ids[i];
                        break;
                    }
                }
                if (!m_ui->logs_selected_run_id.empty() && selected_instance()) {
                    ui_load_selected_run_audit(*m_ui, m_paths.root, selected_instance()->id);
                }
            }
        }

        std::memset(&ev, 0, sizeof(ev));
    }
}

void DomLauncherApp::process_ui_task() {
    if (!m_ui) {
        return;
    }
    DomLauncherUiState::UiTask& t = m_ui->task;
    const launcher_services_api_v1* services = launcher_services_null_v1();

    if (t.kind == (u32)DomLauncherUiState::TASK_NONE) {
        return;
    }

    if (t.kind == (u32)DomLauncherUiState::TASK_LAUNCH) {
        if (t.step == 0u) {
            launcher_core::LauncherLaunchOverrides ov;
            std::vector<std::string> child_args;
            LaunchTarget target;
            std::string exe_path;
            LaunchRunResult lr;

            u32 width = 0u;
            u32 height = 0u;
            u32 dpi = 0u;
            u32 monitor = 0u;

            std::vector<std::string> errs;

            if (!parse_u32_decimal(m_ui->opt_width_text, width)) {
                errs.push_back(std::string("window_width_invalid='") + m_ui->opt_width_text + "'");
            }
            if (!parse_u32_decimal(m_ui->opt_height_text, height)) {
                errs.push_back(std::string("window_height_invalid='") + m_ui->opt_height_text + "'");
            }
            if (!parse_u32_decimal(m_ui->opt_dpi_text, dpi)) {
                errs.push_back(std::string("window_dpi_invalid='") + m_ui->opt_dpi_text + "'");
            }
            if (!parse_u32_decimal(m_ui->opt_monitor_text, monitor)) {
                errs.push_back(std::string("window_monitor_invalid='") + m_ui->opt_monitor_text + "'");
            }
            if (!errs.empty()) {
                m_ui->status_text = "Refused: invalid option value.";
                m_ui->status_progress = 1000u;
                m_ui->dialog_visible = 1u;
                m_ui->dialog_title = "Refused";
                m_ui->dialog_text = "Invalid option value.";
                m_ui->dialog_lines = errs;
                t.kind = (u32)DomLauncherUiState::TASK_NONE;
                return;
            }

            m_ui->status_text = t.op + " in progress...";
            m_ui->status_progress = 100u;

            target = LaunchTarget();
            target.is_tool = t.flag_u32 ? 1u : 0u;
            if (target.is_tool) {
                target.tool_id = t.aux_id;
            }

            if (!target.is_tool) {
                ProductEntry* entry = find_product_entry("game");
                if (!entry) {
                    m_ui->status_text = "Launch failed: game executable not found.";
                    m_ui->status_progress = 1000u;
                    t.kind = (u32)DomLauncherUiState::TASK_NONE;
                    return;
                }
                exe_path = entry->path;
            } else {
                size_t i;
                bool found = false;
                for (i = 0u; i < m_ui->cache_tools.size(); ++i) {
                    if (m_ui->cache_tools[i].tool_id == target.tool_id) {
                        found = true;
                        (void)resolve_tool_executable_path(m_paths.root, m_argv0, m_ui->cache_tools[i], exe_path);
                        break;
                    }
                }
                if (!found) {
                    m_ui->status_text = "Launch failed: tool not in registry.";
                    m_ui->status_progress = 1000u;
                    t.kind = (u32)DomLauncherUiState::TASK_NONE;
                    return;
                }
            }

            ov = launcher_core::LauncherLaunchOverrides();
            ov.request_safe_mode = t.safe_mode ? 1u : 0u;
            ov.safe_mode_allow_network = m_ui->play_offline ? 0u : 1u;

            ov.has_allow_network = 1u;
            ov.allow_network = m_ui->play_offline ? 0u : 1u;

            if (!m_ui->cache_config.gfx_backend.empty()) {
                ov.has_gfx_backend = 1u;
                ov.gfx_backend = m_ui->cache_config.gfx_backend;
            }
            if (!m_ui->cache_config.renderer_api.empty()) {
                ov.has_renderer_api = 1u;
                ov.renderer_api = m_ui->cache_config.renderer_api;
            }
            ov.has_window_mode = 1u;
            ov.window_mode = m_ui->cache_config.window_mode;

            if (width != 0u) {
                ov.has_window_width = 1u;
                ov.window_width = width;
            }
            if (height != 0u) {
                ov.has_window_height = 1u;
                ov.window_height = height;
            }
            if (dpi != 0u) {
                ov.has_window_dpi = 1u;
                ov.window_dpi = dpi;
            }
            if (monitor != 0u) {
                ov.has_window_monitor = 1u;
                ov.window_monitor = monitor;
            }

            child_args.push_back(std::string("--mode=") + (m_selected_mode.empty() ? std::string("gui") : m_selected_mode));
            child_args.push_back(std::string("--instance=") + t.instance_id);
            child_args.push_back(dom_u32_arg("--keep_last_runs=", 8u));

            if (!launcher_execute_launch_attempt(m_paths.root,
                                                 t.instance_id,
                                                 target,
                                                 m_profile_valid ? &m_profile : (const dom_profile*)0,
                                                 exe_path,
                                                 child_args,
                                                 0u,
                                                 8u,
                                                 ov,
                                                 lr)) {
                t.launch_result = lr;
                m_ui->status_progress = 600u;
                if (lr.refused) {
                    m_ui->status_text = std::string("Refused: ") + lr.refusal_detail;
                } else if (!lr.error.empty()) {
                    m_ui->status_text = std::string("Launch failed: ") + lr.error;
                } else {
                    m_ui->status_text = "Launch failed.";
                }
                m_ui->dialog_visible = 1u;
                m_ui->dialog_title = "Launch details";
                m_ui->dialog_text = m_ui->status_text;
                m_ui->dialog_lines.clear();
                if (!lr.run_dir.empty()) m_ui->dialog_lines.push_back(std::string("run_dir=") + lr.run_dir);
                if (!lr.handshake_path.empty()) m_ui->dialog_lines.push_back(std::string("handshake_path=") + lr.handshake_path);
                if (!lr.audit_path.empty()) m_ui->dialog_lines.push_back(std::string("audit_path=") + lr.audit_path);
                if (lr.refused) {
                    m_ui->dialog_lines.push_back(std::string("refusal_code=") + u32_to_string(lr.refusal_code));
                    m_ui->dialog_lines.push_back(std::string("refusal_detail=") + lr.refusal_detail);
                }
            } else {
                t.launch_result = lr;
                m_ui->status_text = std::string("Spawned run_id=0x") + u64_hex16(lr.run_id);
                m_ui->status_progress = 600u;
            }

            t.step = 1u;
            return;
        }

        if (t.step == 1u) {
            ui_refresh_instance_cache(*m_ui, m_paths.root, t.instance_id);
            m_ui->status_progress = 1000u;
            t = DomLauncherUiState::UiTask();
            return;
        }
    }

    if (t.kind == (u32)DomLauncherUiState::TASK_VERIFY_REPAIR) {
        if (t.step == 0u) {
            launcher_core::LauncherInstanceManifest updated;
            launcher_core::LauncherAuditLog audit;
            bool ok;
            size_t i;
            bool has_any = false;

            m_ui->status_text = "Verify / Repair in progress...";
            m_ui->status_progress = 100u;

            for (i = 0u; i < m_ui->cache_manifest.content_entries.size(); ++i) {
                const launcher_core::LauncherContentEntry& e = m_ui->cache_manifest.content_entries[i];
                if (e.enabled && !e.hash_bytes.empty()) {
                    has_any = true;
                    break;
                }
            }
            if (!has_any) {
                m_ui->status_text = "Verify / Repair: no artifacts; skipped.";
                m_ui->status_progress = 600u;
                t.step = 1u;
                return;
            }

            ok = launcher_core::launcher_instance_verify_or_repair(services,
                                                                   t.instance_id,
                                                                   m_paths.root,
                                                                   1u,
                                                                   updated,
                                                                   &audit);
            if (ok) {
                m_ui->status_text = "Verify / Repair: ok.";
            } else {
                m_ui->status_text = "Verify / Repair failed.";
                m_ui->dialog_visible = 1u;
                m_ui->dialog_title = "Verify / Repair failed";
                m_ui->dialog_text = "Operation failed.";
                m_ui->dialog_lines = audit.reasons;
            }
            m_ui->status_progress = 600u;
            t.step = 1u;
            return;
        }
        if (t.step == 1u) {
            ui_refresh_instance_cache(*m_ui, m_paths.root, t.instance_id);
            m_ui->status_progress = 1000u;
            t = DomLauncherUiState::UiTask();
            return;
        }
    }

    if (t.kind == (u32)DomLauncherUiState::TASK_INSTANCE_CREATE) {
        if (t.step == 0u) {
            launcher_core::LauncherAuditLog audit;
            launcher_core::LauncherInstanceManifest created;
            bool ok = false;

            m_ui->status_text = "Creating instance...";
            m_ui->status_progress = 100u;

            if (t.flag_u32 && !t.instance_id.empty()) {
                ok = launcher_core::launcher_instance_template_instance(services,
                                                                        t.instance_id,
                                                                        t.aux_id,
                                                                        m_paths.root,
                                                                        created,
                                                                        &audit);
            } else {
                launcher_core::LauncherInstanceManifest desired = launcher_core::launcher_instance_manifest_make_empty(t.aux_id);
                ok = launcher_core::launcher_instance_create_instance(services,
                                                                      desired,
                                                                      m_paths.root,
                                                                      created,
                                                                      &audit);
            }

            if (!ok) {
                m_ui->status_text = "Create instance failed.";
                m_ui->status_progress = 1000u;
                m_ui->dialog_visible = 1u;
                m_ui->dialog_title = "Create instance failed";
                m_ui->dialog_text = "Operation failed.";
                m_ui->dialog_lines = audit.reasons;
                t = DomLauncherUiState::UiTask();
                return;
            }

            m_ui->status_text = std::string("Created instance: ") + t.aux_id;
            m_ui->status_progress = 600u;
            t.step = 1u;
            return;
        }
        if (t.step == 1u) {
            size_t i;
            int idx = -1;
            (void)scan_instances();
            for (i = 0u; i < m_instances.size(); ++i) {
                if (m_instances[i].id == t.aux_id) {
                    idx = (int)i;
                    break;
                }
            }
            if (idx >= 0) {
                set_selected_instance(idx);
            }
            m_ui->status_progress = 1000u;
            t = DomLauncherUiState::UiTask();
            return;
        }
    }

    if (t.kind == (u32)DomLauncherUiState::TASK_INSTANCE_CLONE) {
        if (t.step == 0u) {
            launcher_core::LauncherAuditLog audit;
            launcher_core::LauncherInstanceManifest created;
            bool ok;

            m_ui->status_text = "Cloning instance...";
            m_ui->status_progress = 100u;

            ok = launcher_core::launcher_instance_clone_instance(services,
                                                                 t.instance_id,
                                                                 t.aux_id,
                                                                 m_paths.root,
                                                                 created,
                                                                 &audit);
            if (!ok) {
                m_ui->status_text = "Clone instance failed.";
                m_ui->status_progress = 1000u;
                m_ui->dialog_visible = 1u;
                m_ui->dialog_title = "Clone instance failed";
                m_ui->dialog_text = "Operation failed.";
                m_ui->dialog_lines = audit.reasons;
                t = DomLauncherUiState::UiTask();
                return;
            }

            m_ui->status_text = std::string("Cloned instance: ") + t.aux_id;
            m_ui->status_progress = 600u;
            t.step = 1u;
            return;
        }
        if (t.step == 1u) {
            size_t i;
            int idx = -1;
            (void)scan_instances();
            for (i = 0u; i < m_instances.size(); ++i) {
                if (m_instances[i].id == t.aux_id) {
                    idx = (int)i;
                    break;
                }
            }
            if (idx >= 0) {
                set_selected_instance(idx);
            }
            m_ui->status_progress = 1000u;
            t = DomLauncherUiState::UiTask();
            return;
        }
    }

    if (t.kind == (u32)DomLauncherUiState::TASK_INSTANCE_DELETE) {
        if (t.step == 0u) {
            launcher_core::LauncherAuditLog audit;
            bool ok;

            m_ui->status_text = "Deleting instance...";
            m_ui->status_progress = 100u;

            ok = launcher_core::launcher_instance_delete_instance(services, t.instance_id, m_paths.root, &audit);
            if (!ok) {
                m_ui->status_text = "Delete instance failed.";
                m_ui->status_progress = 1000u;
                m_ui->dialog_visible = 1u;
                m_ui->dialog_title = "Delete instance failed";
                m_ui->dialog_text = "Operation failed.";
                m_ui->dialog_lines = audit.reasons;
                t = DomLauncherUiState::UiTask();
                return;
            }
            m_ui->status_text = std::string("Deleted instance: ") + t.instance_id;
            m_ui->status_progress = 600u;
            t.step = 1u;
            return;
        }
        if (t.step == 1u) {
            (void)scan_instances();
            if (!m_instances.empty()) {
                set_selected_instance(0);
            } else {
                m_selected_instance = -1;
                ui_refresh_instance_cache(*m_ui, m_paths.root, std::string());
            }
            m_ui->status_progress = 1000u;
            t = DomLauncherUiState::UiTask();
            return;
        }
    }

    if (t.kind == (u32)DomLauncherUiState::TASK_INSTANCE_IMPORT) {
        if (t.step == 0u) {
            launcher_core::LauncherAuditLog audit;
            launcher_core::LauncherInstanceManifest created;
            bool ok;

            m_ui->status_text = "Importing instance...";
            m_ui->status_progress = 100u;

            ok = launcher_core::launcher_instance_import_instance(services,
                                                                  t.path,
                                                                  t.instance_id,
                                                                  m_paths.root,
                                                                  t.flag_u32,
                                                                  1u,
                                                                  created,
                                                                  &audit);
            if (!ok) {
                m_ui->status_text = "Import failed.";
                m_ui->status_progress = 1000u;
                m_ui->dialog_visible = 1u;
                m_ui->dialog_title = "Import failed";
                m_ui->dialog_text = "Operation failed.";
                m_ui->dialog_lines = audit.reasons;
                t = DomLauncherUiState::UiTask();
                return;
            }

            m_ui->status_text = std::string("Imported instance: ") + t.instance_id;
            m_ui->status_progress = 600u;
            t.step = 1u;
            return;
        }
        if (t.step == 1u) {
            size_t i;
            int idx = -1;
            (void)scan_instances();
            for (i = 0u; i < m_instances.size(); ++i) {
                if (m_instances[i].id == t.instance_id) {
                    idx = (int)i;
                    break;
                }
            }
            if (idx >= 0) {
                set_selected_instance(idx);
            }
            m_ui->status_progress = 1000u;
            t = DomLauncherUiState::UiTask();
            return;
        }
    }

    if (t.kind == (u32)DomLauncherUiState::TASK_INSTANCE_EXPORT) {
        launcher_core::LauncherAuditLog audit;
        bool ok;

        m_ui->status_text = "Exporting instance...";
        m_ui->status_progress = 100u;

        ok = launcher_core::launcher_instance_export_instance(services,
                                                              t.instance_id,
                                                              t.path,
                                                              m_paths.root,
                                                              t.flag_u32,
                                                              &audit);
        if (!ok) {
            m_ui->status_text = "Export failed.";
            m_ui->status_progress = 1000u;
            m_ui->dialog_visible = 1u;
            m_ui->dialog_title = "Export failed";
            m_ui->dialog_text = "Operation failed.";
            m_ui->dialog_lines = audit.reasons;
            t = DomLauncherUiState::UiTask();
            return;
        }

        m_ui->status_text = std::string("Exported to: ") + t.path;
        m_ui->status_progress = 1000u;
        m_ui->dialog_visible = 1u;
        m_ui->dialog_title = "Export complete";
        m_ui->dialog_text = "Instance export complete.";
        m_ui->dialog_lines.clear();
        m_ui->dialog_lines.push_back(std::string("out_root=") + t.path);
        t = DomLauncherUiState::UiTask();
        return;
    }

    if (t.kind == (u32)DomLauncherUiState::TASK_INSTANCE_MARK_KG) {
        if (t.step == 0u) {
            launcher_core::LauncherAuditLog audit;
            launcher_core::LauncherInstanceManifest updated;
            bool ok;

            m_ui->status_text = "Marking known-good...";
            m_ui->status_progress = 100u;

            ok = launcher_core::launcher_instance_mark_known_good(services, t.instance_id, m_paths.root, updated, &audit);
            if (!ok) {
                m_ui->status_text = "Mark known-good failed.";
                m_ui->status_progress = 1000u;
                m_ui->dialog_visible = 1u;
                m_ui->dialog_title = "Mark known-good failed";
                m_ui->dialog_text = "Operation failed.";
                m_ui->dialog_lines = audit.reasons;
                t = DomLauncherUiState::UiTask();
                return;
            }

            m_ui->status_text = "Mark known-good: ok.";
            m_ui->status_progress = 600u;
            t.step = 1u;
            return;
        }
        if (t.step == 1u) {
            ui_refresh_instance_cache(*m_ui, m_paths.root, t.instance_id);
            m_ui->status_progress = 1000u;
            t = DomLauncherUiState::UiTask();
            return;
        }
    }

    if (t.kind == (u32)DomLauncherUiState::TASK_PACKS_APPLY) {
        if (t.step == 0u) {
            launcher_core::LauncherAuditLog audit;
            std::vector<launcher_core::LauncherResolvedPack> resolved;
            std::string resolve_err;
            std::vector<std::string> errs;
            bool ok;

            m_ui->status_text = "Packs apply: prepare...";
            m_ui->status_progress = 100u;

            ok = launcher_core::launcher_instance_tx_prepare(services,
                                                             t.instance_id,
                                                             m_paths.root,
                                                             (u32)launcher_core::LAUNCHER_INSTANCE_TX_OP_UPDATE,
                                                             t.tx,
                                                             &audit);
            if (!ok) {
                m_ui->status_text = "Packs apply failed: prepare.";
                m_ui->status_progress = 1000u;
                m_ui->dialog_visible = 1u;
                m_ui->dialog_title = "Packs apply failed";
                m_ui->dialog_text = "Prepare failed.";
                m_ui->dialog_lines = audit.reasons;
                t = DomLauncherUiState::UiTask();
                return;
            }

            t.tx.after_manifest = t.tx.before_manifest;

            {
                std::map<std::string, DomLauncherUiState::StagedPackChange>::const_iterator it;
                for (it = t.packs_changes.begin(); it != t.packs_changes.end(); ++it) {
                    const std::string& key = it->first;
                    const DomLauncherUiState::StagedPackChange& sc = it->second;
                    size_t i;
                    bool found = false;
                    for (i = 0u; i < t.tx.after_manifest.content_entries.size(); ++i) {
                        launcher_core::LauncherContentEntry& e = t.tx.after_manifest.content_entries[i];
                        if (!is_pack_like(e.type)) {
                            continue;
                        }
                        if (pack_key(e.type, e.id) != key) {
                            continue;
                        }
                        found = true;
                        if (sc.has_enabled) {
                            e.enabled = sc.enabled ? 1u : 0u;
                        }
                        if (sc.has_update_policy) {
                            e.update_policy = sc.update_policy;
                        }
                        break;
                    }
                    if (!found) {
                        errs.push_back(std::string("staged_entry_missing;key=") + key);
                    }
                }
            }

            if (!errs.empty()) {
                (void)launcher_core::launcher_instance_tx_rollback(services, t.tx, &audit);
                m_ui->status_text = "Refused: staged pack entry missing.";
                m_ui->status_progress = 1000u;
                m_ui->dialog_visible = 1u;
                m_ui->dialog_title = "Refused";
                m_ui->dialog_text = "Staged entry does not exist in the instance.";
                m_ui->dialog_lines = errs;
                t = DomLauncherUiState::UiTask();
                return;
            }

            if (!launcher_core::launcher_pack_resolve_enabled(services, t.tx.after_manifest, m_paths.root, resolved, &resolve_err)) {
                (void)launcher_core::launcher_instance_tx_rollback(services, t.tx, &audit);
                m_ui->status_text = "Refused: pack resolution failed.";
                m_ui->status_progress = 1000u;
                m_ui->dialog_visible = 1u;
                m_ui->dialog_title = "Pack resolution failed";
                m_ui->dialog_text = "Dependency/conflict rules refused the staged change.";
                m_ui->dialog_lines.clear();
                m_ui->dialog_lines.push_back(resolve_err);
                t = DomLauncherUiState::UiTask();
                return;
            }

            t.lines.clear();
            t.lines.push_back(std::string("resolved=") + launcher_core::launcher_pack_resolved_order_summary(resolved));

            m_ui->status_text = "Packs apply: stage...";
            m_ui->status_progress = 250u;
            t.step = 1u;
            return;
        }
        if (t.step == 1u) {
            launcher_core::LauncherAuditLog audit;
            bool ok;

            m_ui->status_text = "Packs apply: stage...";
            m_ui->status_progress = 350u;

            ok = launcher_core::launcher_instance_tx_stage(services, t.tx, &audit);
            if (!ok) {
                (void)launcher_core::launcher_instance_tx_rollback(services, t.tx, &audit);
                m_ui->status_text = "Packs apply failed: stage.";
                m_ui->status_progress = 1000u;
                m_ui->dialog_visible = 1u;
                m_ui->dialog_title = "Packs apply failed";
                m_ui->dialog_text = "Stage failed.";
                m_ui->dialog_lines = audit.reasons;
                t = DomLauncherUiState::UiTask();
                return;
            }

            m_ui->status_text = "Packs apply: verify...";
            m_ui->status_progress = 500u;
            t.step = 2u;
            return;
        }
        if (t.step == 2u) {
            launcher_core::LauncherAuditLog audit;
            bool ok;

            m_ui->status_text = "Packs apply: verify...";
            m_ui->status_progress = 600u;

            ok = launcher_core::launcher_instance_tx_verify(services, t.tx, &audit);
            if (!ok) {
                (void)launcher_core::launcher_instance_tx_rollback(services, t.tx, &audit);
                m_ui->status_text = "Packs apply failed: verify.";
                m_ui->status_progress = 1000u;
                m_ui->dialog_visible = 1u;
                m_ui->dialog_title = "Packs apply failed";
                m_ui->dialog_text = "Verify failed.";
                m_ui->dialog_lines = audit.reasons;
                t = DomLauncherUiState::UiTask();
                return;
            }

            m_ui->status_text = "Packs apply: commit...";
            m_ui->status_progress = 750u;
            t.step = 3u;
            return;
        }
        if (t.step == 3u) {
            launcher_core::LauncherAuditLog audit;
            bool ok;

            m_ui->status_text = "Packs apply: commit...";
            m_ui->status_progress = 850u;

            ok = launcher_core::launcher_instance_tx_commit(services, t.tx, &audit);
            if (!ok) {
                (void)launcher_core::launcher_instance_tx_rollback(services, t.tx, &audit);
                m_ui->status_text = "Packs apply failed: commit.";
                m_ui->status_progress = 1000u;
                m_ui->dialog_visible = 1u;
                m_ui->dialog_title = "Packs apply failed";
                m_ui->dialog_text = "Commit failed.";
                m_ui->dialog_lines = audit.reasons;
                t = DomLauncherUiState::UiTask();
                return;
            }

            m_ui->status_text = "Packs applied.";
            m_ui->status_progress = 950u;
            t.step = 4u;
            return;
        }
        if (t.step == 4u) {
            m_ui->packs_staged.clear();
            ui_refresh_instance_cache(*m_ui, m_paths.root, t.instance_id);
            m_ui->status_progress = 1000u;
            t = DomLauncherUiState::UiTask();
            return;
        }
    }

    m_ui->status_text = "Operation refused: not implemented.";
    m_ui->status_progress = 1000u;
    t = DomLauncherUiState::UiTask();
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

    /* Play tab */
    {
        const InstanceInfo* inst = selected_instance();
        std::string selected = inst ? (std::string("Selected: ") + inst->id) : std::string("Selected: (none)");
        if (inst && m_ui->cache_valid && m_ui->cache_manifest.instance_id == inst->id) {
            selected += std::string(" known_good=") + (m_ui->cache_manifest.known_good ? "1" : "0");
        }
        dui_state_add_text(inner, (u32)W_PLAY_SELECTED, selected);

        {
            std::string profile_line = std::string("Profile: ") + (m_profile_valid ? "dom_profile" : "default");
            profile_line += std::string(" ui=") + m_ui_backend_selected;
            profile_line += std::string(" dgfx=") + (m_ui->cache_config.gfx_backend.empty() ? std::string("auto") : m_ui->cache_config.gfx_backend);
            profile_line += std::string(" api=") + (m_ui->cache_config.renderer_api.empty() ? std::string("auto") : m_ui->cache_config.renderer_api);
            dui_state_add_text(inner, (u32)W_PLAY_PROFILE, profile_line);
        }

        if (inst && m_ui->cache_valid && m_ui->cache_manifest.instance_id == inst->id) {
            std::string manifest_line = std::string("Manifest: hash=0x") + u64_hex16(m_ui->cache_manifest_hash64);
            if (m_ui->cache_manifest.known_good) {
                manifest_line += " [known_good]";
            }
            if (!m_ui->cache_manifest.pinned_engine_build_id.empty()) {
                manifest_line += std::string(" engine=") + m_ui->cache_manifest.pinned_engine_build_id;
            }
            if (!m_ui->cache_manifest.pinned_game_build_id.empty()) {
                manifest_line += std::string(" game=") + m_ui->cache_manifest.pinned_game_build_id;
            }
            if (!m_ui->cache_error.empty()) {
                manifest_line += std::string(" cache_err=") + m_ui->cache_error;
            }
            dui_state_add_text(inner, (u32)W_PLAY_MANIFEST, manifest_line);
        } else {
            dui_state_add_text(inner, (u32)W_PLAY_MANIFEST, std::string("Manifest: (unavailable)"));
        }

        if (inst && m_ui->cache_valid && !m_ui->cache_history.attempts.empty()) {
            const launcher_core::LauncherInstanceLaunchAttempt& a = m_ui->cache_history.attempts[m_ui->cache_history.attempts.size() - 1u];
            std::string last_line = std::string("Last run: outcome=") + u32_to_string(a.outcome);
            last_line += std::string(" safe_mode=") + (a.safe_mode ? "1" : "0");
            last_line += std::string(" exit=") + i32_to_string(a.exit_code);
            if (!a.detail.empty()) {
                last_line += std::string(" detail=") + a.detail;
            }
            dui_state_add_text(inner, (u32)W_PLAY_LAST_RUN, last_line);
        } else {
            dui_state_add_text(inner, (u32)W_PLAY_LAST_RUN, std::string("Last run: (none)"));
        }

        dui_state_add_u32(inner, (u32)W_PLAY_OFFLINE, (u32)DUI_VALUE_BOOL, m_ui->play_offline ? 1u : 0u);
        {
            std::vector<ListItem> targets;
            const u32 game_id = stable_item_id(std::string("game"));
            u32 selected_target = m_ui->play_target_item_id ? m_ui->play_target_item_id : game_id;

            targets.push_back(ListItem(game_id, "game"));
            for (i = 0u; i < m_ui->cache_tools.size(); ++i) {
                const launcher_core::LauncherToolEntry& te = m_ui->cache_tools[i];
                const std::string key = std::string("tool:") + te.tool_id;
                const u32 tid = stable_item_id(key);
                std::string label = key;
                if (!te.display_name.empty()) {
                    label += std::string(" (") + te.display_name + ")";
                }
                targets.push_back(ListItem(tid, label));
            }

            {
                size_t j;
                bool found = false;
                for (j = 0u; j < targets.size(); ++j) {
                    if (targets[j].id == selected_target) {
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    selected_target = game_id;
                }
            }
            dui_state_add_list(inner, (u32)W_PLAY_TARGET_LIST, selected_target, targets);
        }
        {
            std::vector<ListItem> news;
            if (m_ui->news_lines.empty()) {
                news.push_back(ListItem(1u, "No local news."));
            } else {
                for (i = 0u; i < m_ui->news_lines.size(); ++i) {
                    news.push_back(ListItem((u32)(i + 1u), m_ui->news_lines[i]));
                }
            }
            dui_state_add_list(inner, (u32)W_NEWS_LIST, 0u, news);
        }
    }

    /* Instances tab */
    {
        std::vector<ListItem> paths;
        const InstanceInfo* inst = selected_instance();
        if (inst) {
            launcher_core::LauncherInstancePaths p = launcher_core::launcher_instance_paths_make(m_paths.root, inst->id);
            paths.push_back(ListItem(1u, std::string("instance_id=") + inst->id));
            paths.push_back(ListItem(2u, std::string("state_root=") + p.state_root));
            paths.push_back(ListItem(3u, std::string("instance_root=") + p.instance_root));
            paths.push_back(ListItem(4u, std::string("manifest=") + p.manifest_path));
            paths.push_back(ListItem(5u, std::string("config=") + p.config_file_path));
            paths.push_back(ListItem(6u, std::string("logs_root=") + p.logs_root));
            paths.push_back(ListItem(7u, std::string("runs_root=") + path_join(p.logs_root, "runs")));
            paths.push_back(ListItem(8u, std::string("cache_root=") + p.cache_root));
            paths.push_back(ListItem(9u, std::string("content_root=") + p.content_root));
            paths.push_back(ListItem(10u, std::string("mods_root=") + p.mods_root));
            paths.push_back(ListItem(11u, std::string("saves_root=") + p.saves_root));
            if (m_ui->cache_valid && m_ui->cache_manifest.instance_id == inst->id) {
                paths.push_back(ListItem(12u, std::string("known_good=") + (m_ui->cache_manifest.known_good ? "1" : "0")));
            }
        }
        dui_state_add_list(inner, (u32)W_INST_PATHS_LIST, 0u, paths);
        dui_state_add_text(inner, (u32)W_INST_IMPORT_PATH, m_ui->inst_import_path);
        dui_state_add_text(inner, (u32)W_INST_EXPORT_PATH, m_ui->inst_export_path);
    }

    /* Packs tab */
    dui_state_add_text(inner,
                       (u32)W_PACKS_LABEL,
                       std::string("Packs / Mods (staged=") + u32_to_string((u32)m_ui->packs_staged.size()) + ")");
    {
        std::vector<ListItem> packs;
        u32 packs_selected_id = 0u;
        u32 selected_enabled = 0u;
        u32 selected_policy = (u32)launcher_core::LAUNCHER_UPDATE_PROMPT;

        if (selected_instance() && m_ui->cache_valid) {
            const launcher_core::LauncherInstanceManifest& m = m_ui->cache_manifest;
            for (i = 0u; i < m.content_entries.size(); ++i) {
                const launcher_core::LauncherContentEntry& e = m.content_entries[i];
                if (!is_pack_like(e.type)) {
                    continue;
                }
                const std::string key = pack_key(e.type, e.id);
                const u32 id = stable_item_id(key);
                u32 eff_enabled = e.enabled ? 1u : 0u;
                u32 eff_policy = e.update_policy;
                bool staged = false;

                std::map<std::string, DomLauncherUiState::StagedPackChange>::const_iterator it = m_ui->packs_staged.find(key);
                if (it != m_ui->packs_staged.end()) {
                    if (it->second.has_enabled) {
                        eff_enabled = it->second.enabled ? 1u : 0u;
                        staged = true;
                    }
                    if (it->second.has_update_policy) {
                        eff_policy = it->second.update_policy;
                        staged = true;
                    }
                }

                std::string line;
                if (staged) {
                    line += "* ";
                }
                line += std::string(content_type_to_short(e.type)) + ":" + e.id + " v" + e.version;
                line += std::string(" enabled=") + (eff_enabled ? "1" : "0");
                line += std::string(" policy=") + update_policy_to_string(eff_policy);
                packs.push_back(ListItem(id, line));

                if ((!m_ui->packs_selected_key.empty() && key == m_ui->packs_selected_key) ||
                    (m_ui->packs_selected_key.empty() && m_ui->packs_selected_item_id != 0u && id == m_ui->packs_selected_item_id)) {
                    packs_selected_id = id;
                    selected_enabled = eff_enabled;
                    selected_policy = eff_policy;
                }
            }
        }

        dui_state_add_list(inner, (u32)W_PACKS_LIST, packs_selected_id, packs);
        dui_state_add_u32(inner, (u32)W_PACKS_ENABLED, (u32)DUI_VALUE_BOOL, packs_selected_id ? (selected_enabled ? 1u : 0u) : 0u);

        {
            std::vector<ListItem> policies;
            policies.push_back(ListItem(stable_item_id("never"), "never"));
            policies.push_back(ListItem(stable_item_id("prompt"), "prompt"));
            policies.push_back(ListItem(stable_item_id("auto"), "auto"));
            dui_state_add_list(inner, (u32)W_PACKS_POLICY_LIST, update_policy_item_id(selected_policy), policies);
        }
    }

    dui_state_add_text(inner, (u32)W_PACKS_RESOLVED, m_ui->cache_resolved_packs_summary);
    dui_state_add_text(inner, (u32)W_PACKS_ERROR, m_ui->cache_resolved_packs_error);

    /* Options tab */
    {
        std::vector<ListItem> gfx;
        std::vector<std::string> names;
        u32 selected = stable_item_id("auto");

        gfx.push_back(ListItem(stable_item_id("auto"), "auto"));
        collect_dgfx_backend_names(names);
        for (i = 0u; i < names.size(); ++i) {
            gfx.push_back(ListItem(stable_item_id(std::string("dgfx:") + names[i]), names[i]));
        }
        if (!m_ui->cache_config.gfx_backend.empty()) {
            selected = stable_item_id(std::string("dgfx:") + m_ui->cache_config.gfx_backend);
        }
        dui_state_add_list(inner, (u32)W_OPT_GFX_LIST, selected, gfx);
    }
    dui_state_add_text(inner, (u32)W_OPT_API_FIELD, m_ui->opt_renderer_api_text);
    {
        std::vector<ListItem> wm;
        wm.push_back(ListItem(stable_item_id("auto"), "auto"));
        wm.push_back(ListItem(stable_item_id("windowed"), "windowed"));
        wm.push_back(ListItem(stable_item_id("fullscreen"), "fullscreen"));
        wm.push_back(ListItem(stable_item_id("borderless"), "borderless"));
        dui_state_add_list(inner, (u32)W_OPT_WINMODE_LIST, window_mode_item_id(m_ui->cache_config.window_mode), wm);
    }
    dui_state_add_text(inner, (u32)W_OPT_WIDTH_FIELD, m_ui->opt_width_text);
    dui_state_add_text(inner, (u32)W_OPT_HEIGHT_FIELD, m_ui->opt_height_text);
    dui_state_add_text(inner, (u32)W_OPT_DPI_FIELD, m_ui->opt_dpi_text);
    dui_state_add_text(inner, (u32)W_OPT_MONITOR_FIELD, m_ui->opt_monitor_text);
    dui_state_add_text(inner, (u32)W_OPT_AUDIO_LABEL, std::string("Audio device: not supported"));
    dui_state_add_text(inner, (u32)W_OPT_INPUT_LABEL, std::string("Input backend: not supported"));

    /* Logs tab */
    {
        if (selected_instance() && m_ui->cache_valid && !m_ui->cache_run_ids.empty()) {
            dui_state_add_text(inner,
                               (u32)W_LOGS_LAST_RUN,
                               std::string("Last run_id=") + m_ui->cache_run_ids[m_ui->cache_run_ids.size() - 1u]);
        } else {
            dui_state_add_text(inner, (u32)W_LOGS_LAST_RUN, std::string("Last run: (none)"));
        }

        {
            std::vector<ListItem> runs;
            for (i = 0u; i < m_ui->cache_run_ids.size(); ++i) {
                runs.push_back(ListItem(stable_item_id(m_ui->cache_run_ids[i]), m_ui->cache_run_ids[i]));
            }
            dui_state_add_list(inner, (u32)W_LOGS_RUNS_LIST, m_ui->logs_selected_run_item_id, runs);
        }

        {
            std::vector<ListItem> audit;
            for (i = 0u; i < m_ui->logs_selected_audit_lines.size(); ++i) {
                audit.push_back(ListItem((u32)(i + 1u), m_ui->logs_selected_audit_lines[i]));
            }
            dui_state_add_list(inner, (u32)W_LOGS_AUDIT_LIST, 0u, audit);
        }

        dui_state_add_text(inner, (u32)W_LOGS_DIAG_OUT, m_ui->logs_diag_out_path);

        {
            std::vector<ListItem> locs;
            const InstanceInfo* inst = selected_instance();
            if (inst) {
                launcher_core::LauncherInstancePaths p = launcher_core::launcher_instance_paths_make(m_paths.root, inst->id);
                locs.push_back(ListItem(1u, std::string("instance_root=") + p.instance_root));
                locs.push_back(ListItem(2u, std::string("logs_root=") + p.logs_root));
                locs.push_back(ListItem(3u, std::string("runs_root=") + path_join(p.logs_root, "runs")));
                locs.push_back(ListItem(4u, std::string("cache_root=") + p.cache_root));
                locs.push_back(ListItem(5u, std::string("content_root=") + p.content_root));
            }
            dui_state_add_list(inner, (u32)W_LOGS_LOCS_LIST, 0u, locs);
        }
    }

    /* Status bar */
    dui_state_add_text(inner, (u32)W_STATUS_TEXT, m_ui->status_text);
    dui_state_add_u32(inner, (u32)W_STATUS_PROGRESS, (u32)DUI_VALUE_U32, (m_ui->status_progress > 1000u) ? 1000u : m_ui->status_progress);
    {
        std::string summary = std::string("instance=") + (selected_instance() ? selected_instance()->id : std::string("(none)"));
        summary += std::string(" profile=") + (m_profile_valid ? "dom_profile" : "default");
        summary += std::string(" ui=") + m_ui_backend_selected;
        if (selected_instance() && m_ui->cache_valid) {
            summary += std::string(" manifest=") + u64_hex16(m_ui->cache_manifest_hash64).substr(0u, 8u);
        }
        dui_state_add_text(inner, (u32)W_STATUS_SELECTION, summary);
    }

    append_tlv_raw(out_state, DUI_TLV_STATE_V1, inner.empty() ? (const void*)0 : &inner[0], inner.size());
    return true;
}

} // namespace dom
