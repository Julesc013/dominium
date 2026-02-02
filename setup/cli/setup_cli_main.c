/*
Stub setup CLI entrypoint.
*/
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"
#include "dom_build_identity/build_identity.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#if defined(_WIN32)
#include <direct.h>
#else
#include <sys/stat.h>
#include <unistd.h>
#endif

#include "dsk/dsk_setup.h"

#ifndef DOMINO_VERSION_STRING
#define DOMINO_VERSION_STRING "0.0.0"
#endif

#ifndef DOMINIUM_GAME_VERSION
#define DOMINIUM_GAME_VERSION "0.0.0"
#endif

#ifndef DOM_BUILD_SKU
#define DOM_BUILD_SKU "auto"
#endif

#ifndef DOM_BUILD_ID
#define DOM_BUILD_ID "unknown"
#endif

#ifndef DOM_GIT_HASH
#define DOM_GIT_HASH "unknown"
#endif

#ifndef DOM_TOOLCHAIN_ID
#define DOM_TOOLCHAIN_ID "unknown"
#endif

#ifndef DOM_TOOLCHAIN_FAMILY
#define DOM_TOOLCHAIN_FAMILY "unknown"
#endif

#ifndef DOM_TOOLCHAIN_VERSION
#define DOM_TOOLCHAIN_VERSION "unknown"
#endif

#ifndef DOM_TOOLCHAIN_STDLIB
#define DOM_TOOLCHAIN_STDLIB "unknown"
#endif

#ifndef DOM_TOOLCHAIN_RUNTIME
#define DOM_TOOLCHAIN_RUNTIME "unknown"
#endif

#ifndef DOM_TOOLCHAIN_LINK
#define DOM_TOOLCHAIN_LINK "unknown"
#endif

#ifndef DOM_TOOLCHAIN_TARGET
#define DOM_TOOLCHAIN_TARGET "unknown"
#endif

#ifndef DOM_TOOLCHAIN_OS
#define DOM_TOOLCHAIN_OS "unknown"
#endif

#ifndef DOM_TOOLCHAIN_ARCH
#define DOM_TOOLCHAIN_ARCH "unknown"
#endif

#ifndef DOM_TOOLCHAIN_OS_FLOOR
#define DOM_TOOLCHAIN_OS_FLOOR "unknown"
#endif

#ifndef DOM_TOOLCHAIN_CONFIG
#define DOM_TOOLCHAIN_CONFIG "unknown"
#endif

#ifndef DOM_BUILD_INFO_ABI_VERSION
#define DOM_BUILD_INFO_ABI_VERSION 0
#endif

#ifndef DOM_CAPS_ABI_VERSION
#define DOM_CAPS_ABI_VERSION 0
#endif

#ifndef DSYS_PROTOCOL_VERSION
#define DSYS_PROTOCOL_VERSION 0
#endif

#ifndef DSYS_EXTENSION_WINDOW_EX_VERSION
#define DSYS_EXTENSION_WINDOW_EX_VERSION 0
#endif

#ifndef DSYS_EXTENSION_ERROR_VERSION
#define DSYS_EXTENSION_ERROR_VERSION 0
#endif

#ifndef DSYS_EXTENSION_CLIPTEXT_VERSION
#define DSYS_EXTENSION_CLIPTEXT_VERSION 0
#endif

#ifndef DSYS_EXTENSION_CURSOR_VERSION
#define DSYS_EXTENSION_CURSOR_VERSION 0
#endif

#ifndef DSYS_EXTENSION_DRAGDROP_VERSION
#define DSYS_EXTENSION_DRAGDROP_VERSION 0
#endif

#ifndef DSYS_EXTENSION_GAMEPAD_VERSION
#define DSYS_EXTENSION_GAMEPAD_VERSION 0
#endif

#ifndef DSYS_EXTENSION_POWER_VERSION
#define DSYS_EXTENSION_POWER_VERSION 0
#endif

#ifndef DSYS_EXTENSION_TEXT_INPUT_VERSION
#define DSYS_EXTENSION_TEXT_INPUT_VERSION 0
#endif

#ifndef DSYS_EXTENSION_WINDOW_MODE_VERSION
#define DSYS_EXTENSION_WINDOW_MODE_VERSION 0
#endif

#ifndef DSYS_EXTENSION_DPI_VERSION
#define DSYS_EXTENSION_DPI_VERSION 0
#endif

#ifndef DGFX_PROTOCOL_VERSION
#define DGFX_PROTOCOL_VERSION 0
#endif

enum {
    D_APP_EXIT_OK = 0,
    D_APP_EXIT_FAILURE = 1,
    D_APP_EXIT_USAGE = 2,
    D_APP_EXIT_UNAVAILABLE = 3,
    D_APP_EXIT_SIGNAL = 130
};

#define DOM_APP_UI_ENV "DOM_UI"
#define DOM_APP_UI_ENV_FALLBACK "DOM_UI_MODE"

typedef enum dom_app_ui_mode {
    DOM_APP_UI_NONE = 0,
    DOM_APP_UI_TUI,
    DOM_APP_UI_GUI
} dom_app_ui_mode;

typedef struct dom_app_ui_request {
    dom_app_ui_mode mode;
    int mode_explicit;
} dom_app_ui_request;

static void dom_app_ui_request_init(dom_app_ui_request* req)
{
    if (!req) {
        return;
    }
    req->mode = DOM_APP_UI_NONE;
    req->mode_explicit = 0;
}

static const char* dom_app_ui_mode_name(dom_app_ui_mode mode)
{
    switch (mode) {
    case DOM_APP_UI_TUI:
        return "tui";
    case DOM_APP_UI_GUI:
        return "gui";
    case DOM_APP_UI_NONE:
    default:
        return "none";
    }
}

static dom_app_ui_mode dom_app_ui_parse_value(const char* value, int* ok)
{
    if (!value || !*value) {
        if (ok) {
            *ok = 0;
        }
        return DOM_APP_UI_NONE;
    }
    if (strcmp(value, "none") == 0) {
        if (ok) {
            *ok = 1;
        }
        return DOM_APP_UI_NONE;
    }
    if (strcmp(value, "tui") == 0) {
        if (ok) {
            *ok = 1;
        }
        return DOM_APP_UI_TUI;
    }
    if (strcmp(value, "gui") == 0) {
        if (ok) {
            *ok = 1;
        }
        return DOM_APP_UI_GUI;
    }
    if (ok) {
        *ok = 0;
    }
    return DOM_APP_UI_NONE;
}

static int dom_app_parse_ui_arg(dom_app_ui_request* req,
                                const char* arg,
                                const char* next,
                                int* consumed,
                                char* err,
                                size_t err_cap)
{
    const char* value = 0;
    int ok = 0;
    if (!consumed) {
        return -1;
    }
    *consumed = 0;
    if (!req || !arg) {
        return -1;
    }
    if (strncmp(arg, "--ui", 4) != 0) {
        return 0;
    }
    if (req->mode_explicit) {
        if (err && err_cap) {
            snprintf(err, err_cap, "ui mode already set to %s", dom_app_ui_mode_name(req->mode));
        }
        return -1;
    }
    if (arg[4] == '\0') {
        value = next;
        if (!value || !*value) {
            if (err && err_cap) {
                snprintf(err, err_cap, "missing ui mode (none|tui|gui)");
            }
            return -1;
        }
        *consumed = 2;
    } else if (arg[4] == '=') {
        value = arg + 5;
        if (!value || !*value) {
            if (err && err_cap) {
                snprintf(err, err_cap, "missing ui mode (none|tui|gui)");
            }
            return -1;
        }
        *consumed = 1;
    } else {
        return 0;
    }
    req->mode = dom_app_ui_parse_value(value, &ok);
    if (!ok) {
        if (err && err_cap) {
            snprintf(err, err_cap, "invalid ui mode '%s'", value);
        }
        return -1;
    }
    req->mode_explicit = 1;
    return 1;
}

static dom_app_ui_mode dom_app_ui_mode_from_env(void)
{
    int ok = 0;
    const char* value = getenv(DOM_APP_UI_ENV);
    if (!value || !*value) {
        value = getenv(DOM_APP_UI_ENV_FALLBACK);
    }
    if (!value || !*value) {
        return DOM_APP_UI_NONE;
    }
    return dom_app_ui_parse_value(value, &ok);
}

static dom_app_ui_mode dom_app_select_ui_mode(const dom_app_ui_request* req,
                                              dom_app_ui_mode default_mode)
{
    dom_app_ui_mode env_mode;
    if (req && req->mode_explicit) {
        return req->mode;
    }
    env_mode = dom_app_ui_mode_from_env();
    if (env_mode != DOM_APP_UI_NONE) {
        return env_mode;
    }
    return default_mode;
}

static void print_version(const char* product_version)
{
    printf("setup %s\\n", product_version);
}

static const char* setup_default_sku_for_product(const char* product_name)
{
    if (!product_name || !product_name[0]) {
        return "unspecified";
    }
    if (strcmp(product_name, "client") == 0) {
        return "modern_desktop";
    }
    if (strcmp(product_name, "server") == 0) {
        return "headless_server";
    }
    if (strcmp(product_name, "launcher") == 0) {
        return "modern_desktop";
    }
    if (strcmp(product_name, "setup") == 0) {
        return "modern_desktop";
    }
    if (strcmp(product_name, "tools") == 0) {
        return "devtools";
    }
    return "unspecified";
}

static const char* setup_build_sku_value(const char* product_name)
{
    const char* override = DOM_BUILD_SKU;
    if (override && override[0] && strcmp(override, "auto") != 0) {
        return override;
    }
    return setup_default_sku_for_product(product_name);
}

static void print_build_info(const char* product_name, const char* product_version)
{
    dom_build_identity identity = dom_build_identity_get();
    const char* git_commit = identity.git_commit ? identity.git_commit : DOM_GIT_HASH;
    printf("product=%s\n", product_name ? product_name : "");
    printf("product_version=%s\n", product_version ? product_version : "");
    printf("sku=%s\n", setup_build_sku_value(product_name));
    printf("engine_version=%s\n", DOMINO_VERSION_STRING);
    printf("game_version=%s\n", DOMINIUM_GAME_VERSION);
    printf("build_number=%u\n", (unsigned int)DOM_BUILD_NUMBER);
    printf("build_id=%s\n", DOM_BUILD_ID);
    printf("build_kind=%s\n", identity.build_kind ? identity.build_kind : "");
    printf("build_bii=%s\n", identity.bii ? identity.bii : "");
    printf("build_gbn=%s\n", identity.gbn ? identity.gbn : "");
    printf("build_timestamp=%s\n", identity.build_timestamp ? identity.build_timestamp : "");
    printf("git_hash=%s\n", git_commit ? git_commit : "");
    printf("git_commit=%s\n", git_commit ? git_commit : "");
    printf("toolchain_id=%s\n", DOM_TOOLCHAIN_ID);
    printf("toolchain_family=%s\n", DOM_TOOLCHAIN_FAMILY);
    printf("toolchain_version=%s\n", DOM_TOOLCHAIN_VERSION);
    printf("toolchain_stdlib=%s\n", DOM_TOOLCHAIN_STDLIB);
    printf("toolchain_runtime=%s\n", DOM_TOOLCHAIN_RUNTIME);
    printf("toolchain_link=%s\n", DOM_TOOLCHAIN_LINK);
    printf("toolchain_target=%s\n", DOM_TOOLCHAIN_TARGET);
    printf("toolchain_os=%s\n", DOM_TOOLCHAIN_OS);
    printf("toolchain_arch=%s\n", DOM_TOOLCHAIN_ARCH);
    printf("toolchain_os_floor=%s\n", DOM_TOOLCHAIN_OS_FLOOR);
    printf("toolchain_config=%s\n", DOM_TOOLCHAIN_CONFIG);
    printf("protocol_law_targets=LAW_TARGETS@1.4.0\n");
    printf("protocol_control_caps=CONTROL_CAPS@1.0.0\n");
    printf("protocol_authority_tokens=AUTHORITY_TOKEN@1.0.0\n");
    printf("abi_dom_build_info=%u\n", (unsigned int)DOM_BUILD_INFO_ABI_VERSION);
    printf("abi_dom_caps=%u\n", (unsigned int)DOM_CAPS_ABI_VERSION);
    printf("api_dsys=%u\n", (unsigned int)DSYS_PROTOCOL_VERSION);
    printf("platform_ext_window_ex_api=%u\n", (unsigned int)DSYS_EXTENSION_WINDOW_EX_VERSION);
    printf("platform_ext_error_api=%u\n", (unsigned int)DSYS_EXTENSION_ERROR_VERSION);
    printf("platform_ext_cliptext_api=%u\n", (unsigned int)DSYS_EXTENSION_CLIPTEXT_VERSION);
    printf("platform_ext_cursor_api=%u\n", (unsigned int)DSYS_EXTENSION_CURSOR_VERSION);
    printf("platform_ext_dragdrop_api=%u\n", (unsigned int)DSYS_EXTENSION_DRAGDROP_VERSION);
    printf("platform_ext_gamepad_api=%u\n", (unsigned int)DSYS_EXTENSION_GAMEPAD_VERSION);
    printf("platform_ext_power_api=%u\n", (unsigned int)DSYS_EXTENSION_POWER_VERSION);
    printf("platform_ext_text_input_api=%u\n", (unsigned int)DSYS_EXTENSION_TEXT_INPUT_VERSION);
    printf("platform_ext_window_mode_api=%u\n", (unsigned int)DSYS_EXTENSION_WINDOW_MODE_VERSION);
    printf("platform_ext_dpi_api=%u\n", (unsigned int)DSYS_EXTENSION_DPI_VERSION);
    printf("api_dgfx=%u\n", (unsigned int)DGFX_PROTOCOL_VERSION);
}

typedef struct setup_control_caps {
    char** keys;
    unsigned int count;
    unsigned int capacity;
    unsigned char* enabled;
    unsigned int enabled_count;
} setup_control_caps;

static int control_is_ascii_space(char c)
{
    return (c == ' ') || (c == '\t') || (c == '\r') || (c == '\n');
}

static char* control_trim(char* s)
{
    size_t len;
    char* end;
    if (!s) {
        return s;
    }
    while (*s && control_is_ascii_space(*s)) {
        ++s;
    }
    len = strlen(s);
    if (len == 0u) {
        return s;
    }
    end = s + len - 1u;
    while (end >= s && control_is_ascii_space(*end)) {
        *end = '\0';
        if (end == s) {
            break;
        }
        --end;
    }
    return s;
}

static int control_is_valid_key(const char* s)
{
    const unsigned char* p;
    if (!s || !*s) {
        return 0;
    }
    p = (const unsigned char*)s;
    while (*p) {
        if ((*p >= 'A' && *p <= 'Z') ||
            (*p >= '0' && *p <= '9') ||
            (*p == '_') || (*p == '.')) {
            ++p;
            continue;
        }
        return 0;
    }
    return 1;
}

static void control_sort_keys(char** keys, unsigned int count)
{
    unsigned int i;
    for (i = 1u; i < count; ++i) {
        char* key = keys[i];
        unsigned int j = i;
        while (j > 0u && strcmp(keys[j - 1u], key) > 0) {
            keys[j] = keys[j - 1u];
            --j;
        }
        keys[j] = key;
    }
}

static void control_free_caps(setup_control_caps* caps)
{
    unsigned int i;
    if (!caps) {
        return;
    }
    if (caps->keys) {
        for (i = 0u; i < caps->count; ++i) {
            free(caps->keys[i]);
        }
        free(caps->keys);
    }
    if (caps->enabled) {
        free(caps->enabled);
    }
    memset(caps, 0, sizeof(*caps));
}

static int control_caps_init(setup_control_caps* caps, const char* path)
{
    FILE* fp;
    char line_buf[512];
    unsigned int count = 0u;
    unsigned int capacity = 0u;
    if (!caps || !path) {
        return -1;
    }
    memset(caps, 0, sizeof(*caps));
    fp = fopen(path, "rb");
    if (!fp) {
        return -1;
    }
    while (fgets(line_buf, sizeof(line_buf), fp)) {
        char* line;
        char* dup;
        size_t len;
        unsigned int i;
        if (strchr(line_buf, '\n') == NULL && !feof(fp)) {
            fclose(fp);
            control_free_caps(caps);
            return -1;
        }
        line = control_trim(line_buf);
        if (*line == '\0' || *line == '#') {
            continue;
        }
        if (!control_is_valid_key(line)) {
            fclose(fp);
            control_free_caps(caps);
            return -1;
        }
        len = strlen(line);
        dup = (char*)malloc(len + 1u);
        if (!dup) {
            fclose(fp);
            control_free_caps(caps);
            return -1;
        }
        memcpy(dup, line, len + 1u);
        for (i = 0u; i < count; ++i) {
            if (strcmp(caps->keys[i], dup) == 0) {
                free(dup);
                fclose(fp);
                control_free_caps(caps);
                return -1;
            }
        }
        if (count >= capacity) {
            unsigned int new_cap = capacity ? (capacity * 2u) : 16u;
            char** next = (char**)realloc(caps->keys, sizeof(char*) * new_cap);
            if (!next) {
                free(dup);
                fclose(fp);
                control_free_caps(caps);
                return -1;
            }
            caps->keys = next;
            capacity = new_cap;
        }
        caps->keys[count++] = dup;
    }
    fclose(fp);
    if (count == 0u) {
        control_free_caps(caps);
        return -1;
    }
    caps->count = count;
    caps->capacity = count;
    control_sort_keys(caps->keys, caps->count);
    caps->enabled = (unsigned char*)calloc(caps->count, sizeof(unsigned char));
    if (!caps->enabled) {
        control_free_caps(caps);
        return -1;
    }
    caps->enabled_count = 0u;
    return 0;
}

static int control_caps_enable_key(setup_control_caps* caps, const char* key)
{
    unsigned int i;
    if (!caps || !key) {
        return -1;
    }
    for (i = 0u; i < caps->count; ++i) {
        if (strcmp(caps->keys[i], key) == 0) {
            if (!caps->enabled[i]) {
                caps->enabled[i] = 1u;
                caps->enabled_count += 1u;
            }
            return 0;
        }
    }
    return -1;
}

static int control_caps_is_enabled(const setup_control_caps* caps, unsigned int index)
{
    if (!caps || !caps->enabled || index >= caps->count) {
        return 0;
    }
    return caps->enabled[index] ? 1 : 0;
}

static void print_control_caps(const setup_control_caps* caps)
{
    unsigned int i;
    unsigned int enabled = caps ? caps->enabled_count : 0u;
    printf("control_hooks=external\n");
    printf("control_caps_enabled=%u\n", (unsigned int)enabled);
    if (!caps || !caps->keys) {
        return;
    }
    for (i = 0u; i < caps->count; ++i) {
        if (control_caps_is_enabled(caps, i)) {
            printf("control_cap=%s\n", caps->keys[i]);
        }
    }
}

static int enable_control_list(setup_control_caps* caps, const char* list)
{
    char buf[512];
    size_t len;
    char* token;
    if (!list || !caps) {
        return 0;
    }
    len = strlen(list);
    if (len >= sizeof(buf)) {
        return -1;
    }
    memcpy(buf, list, len + 1u);
    token = buf;
    while (token) {
        char* comma = strchr(token, ',');
        if (comma) {
            *comma = '\0';
        }
        if (*token) {
            if (control_caps_enable_key(caps, token) != 0) {
                return -1;
            }
        }
        token = comma ? (comma + 1u) : (char*)0;
    }
    return 0;
}

static void setup_print_help(void)
{
    printf("usage: setup [--help] [--version] [--build-info] [--status] [--smoke] [--selftest] <command>\\n");
    printf("options:\\n");
    printf("  --build-info                 Show build info + control capabilities\\n");
    printf("  --status                     Show active control layers\\n");
    printf("  --smoke                      Run deterministic CLI smoke\\n");
    printf("  --selftest                   Alias for --smoke\\n");
    printf("  --ui=none|tui|gui            Select UI shell (optional)\\n");
    printf("  --deterministic             Use fixed timestep (no wall-clock sleep)\\n");
    printf("  --interactive               Use variable timestep (wall-clock)\\n");
    printf("  --root <path>                Install root for prepare command\\n");
    printf("  --control-enable=K1,K2       Enable control capabilities (canonical keys)\\n");
    printf("  --control-registry <path>    Override control registry path\\n");
    printf("commands:\\n");
    printf("  version   Show setup version\\n");
    printf("  status    Show setup status\\n");
    printf("  prepare   Create empty install layout\\n");
    printf("  install   Perform install (offline-first)\\n");
    printf("  repair    Repair an existing install\\n");
    printf("  uninstall Uninstall binaries (preserve data by default)\\n");
    printf("  rollback  Roll back to previous install snapshot\\n");
    printf("  export-invocation  Emit invocation payload\\n");
    printf("  plan      Create a transactional plan\\n");
    printf("  apply     Apply a transactional plan\\n");
    printf("  detect    Detect install root status\\n");
    printf("  manifest  Manifest operations (validate)\\n");
    printf("  ops <args> Install/instance operations (delegates to ops_cli)\\n");
    printf("  share <args> Bundle export/import/inspect (delegates to share_cli)\\n");
}

static int setup_is_abs_path(const char* path)
{
    if (!path || !path[0]) {
        return 0;
    }
    if (path[0] == '/' || path[0] == '\\') {
        return 1;
    }
    if (isalpha((unsigned char)path[0]) && path[1] == ':' &&
        (path[2] == '/' || path[2] == '\\')) {
        return 1;
    }
    return 0;
}

static int setup_file_exists(const char* path)
{
    FILE* f = 0;
    if (!path || !path[0]) {
        return 0;
    }
    f = fopen(path, "rb");
    if (f) {
        fclose(f);
        return 1;
    }
    return 0;
}

static int setup_get_cwd(char* buf, size_t cap)
{
#if defined(_WIN32)
    return (_getcwd(buf, (int)cap) != NULL);
#else
    return (getcwd(buf, cap) != NULL);
#endif
}

static void setup_normalize_path(char* path)
{
    char* p;
    if (!path) {
        return;
    }
    for (p = path; *p; ++p) {
        if (*p == '\\') {
            *p = '/';
        }
    }
}

static int setup_pop_dir(char* path)
{
    size_t len;
    char* slash;
    if (!path || !path[0]) {
        return 0;
    }
    len = strlen(path);
    while (len > 0 && path[len - 1] == '/') {
        path[--len] = '\0';
    }
    if (len == 0) {
        return 0;
    }
    if (len == 1 && path[0] == '/') {
        return 0;
    }
    if (len == 3 && path[1] == ':' && path[2] == '/') {
        return 0;
    }
    slash = strrchr(path, '/');
    if (!slash) {
        return 0;
    }
    if (slash == path) {
        path[1] = '\0';
        return 1;
    }
    if (slash == path + 2 && path[1] == ':') {
        slash[1] = '\0';
        return 1;
    }
    *slash = '\0';
    return 1;
}

static int setup_join_search_path(char* out, size_t cap, const char* base, const char* rel)
{
    size_t blen;
    int written;
    if (!out || cap == 0u || !base || !rel) {
        return 0;
    }
    blen = strlen(base);
    if (blen > 0 && base[blen - 1] == '/') {
        written = snprintf(out, cap, "%s%s", base, rel);
    } else {
        written = snprintf(out, cap, "%s/%s", base, rel);
    }
    return written > 0 && (size_t)written < cap;
}

static int setup_find_upward(char* out, size_t cap, const char* rel)
{
    char cwd[512];
    char probe[512];
    if (!setup_get_cwd(cwd, sizeof(cwd))) {
        return 0;
    }
    setup_normalize_path(cwd);
    while (1) {
        if (!setup_join_search_path(probe, sizeof(probe), cwd, rel)) {
            return 0;
        }
        if (setup_file_exists(probe)) {
            strncpy(out, probe, cap - 1u);
            out[cap - 1u] = '\0';
            return 1;
        }
        if (!setup_pop_dir(cwd)) {
            break;
        }
    }
    return 0;
}

static void setup_resolve_control_registry(char* out, size_t cap, const char* requested)
{
    const char* fallback = "data/registries/control_capabilities.registry";
    const char* path = (requested && requested[0]) ? requested : fallback;
    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (setup_is_abs_path(path)) {
        strncpy(out, path, cap - 1u);
        out[cap - 1u] = '\0';
        return;
    }
    if (setup_file_exists(path)) {
        strncpy(out, path, cap - 1u);
        out[cap - 1u] = '\0';
        return;
    }
    if (setup_find_upward(out, cap, path)) {
        return;
    }
    strncpy(out, path, cap - 1u);
    out[cap - 1u] = '\0';
}

static int setup_append_quoted(char* buf, size_t cap, const char* arg)
{
    size_t len;
    size_t pos;
    size_t i;
    if (!buf || cap == 0u || !arg) {
        return 0;
    }
    len = strlen(buf);
    if (len + 3u >= cap) {
        return 0;
    }
    pos = len;
    buf[pos++] = ' ';
    buf[pos++] = '"';
    for (i = 0u; arg[i]; ++i) {
        char c = arg[i];
        if (c == '"') {
            if (pos + 2u >= cap) {
                return 0;
            }
            buf[pos++] = '\\';
            buf[pos++] = '"';
            continue;
        }
        if (pos + 1u >= cap) {
            return 0;
        }
        buf[pos++] = c;
    }
    if (pos + 2u >= cap) {
        return 0;
    }
    buf[pos++] = '"';
    buf[pos] = '\0';
    return 1;
}

static int setup_resolve_ops_script(char* out, size_t cap)
{
    const char* rel = "tools/ops/ops_cli.py";
    if (!out || cap == 0u) {
        return 0;
    }
    out[0] = '\0';
    if (setup_find_upward(out, cap, rel)) {
        return 1;
    }
    strncpy(out, rel, cap - 1u);
    out[cap - 1u] = '\0';
    return 1;
}

static int setup_run_ops(int argc, char** argv, int cmd_index)
{
    char script_path[512];
    char cmd[2048];
    int i;
    int rc;
    if (cmd_index < 0 || argc <= cmd_index) {
        return D_APP_EXIT_USAGE;
    }
    if (!setup_resolve_ops_script(script_path, sizeof(script_path))) {
        fprintf(stderr, "setup: unable to resolve ops cli path\n");
        return D_APP_EXIT_FAILURE;
    }
    if (snprintf(cmd, sizeof(cmd), "python") <= 0) {
        fprintf(stderr, "setup: failed to build ops command\n");
        return D_APP_EXIT_FAILURE;
    }
    if (!setup_append_quoted(cmd, sizeof(cmd), script_path)) {
        fprintf(stderr, "setup: ops command too long\n");
        return D_APP_EXIT_FAILURE;
    }
    for (i = cmd_index + 1; i < argc; ++i) {
        if (!setup_append_quoted(cmd, sizeof(cmd), argv[i])) {
            fprintf(stderr, "setup: ops command too long\n");
            return D_APP_EXIT_FAILURE;
        }
    }
    rc = system(cmd);
    if (rc == -1) {
        fprintf(stderr, "setup: failed to run ops cli\n");
        return D_APP_EXIT_FAILURE;
    }
    return rc;
}

static int setup_resolve_share_script(char* out, size_t cap)
{
    const char* rel = "tools/share/share_cli.py";
    if (!out || cap == 0u) {
        return 0;
    }
    out[0] = '\0';
    if (setup_find_upward(out, cap, rel)) {
        return 1;
    }
    strncpy(out, rel, cap - 1u);
    out[cap - 1u] = '\0';
    return 1;
}

static int setup_run_share(int argc, char** argv, int cmd_index)
{
    char script_path[512];
    char cmd[2048];
    int i;
    int rc;
    if (cmd_index < 0 || argc <= cmd_index) {
        return D_APP_EXIT_USAGE;
    }
    if (!setup_resolve_share_script(script_path, sizeof(script_path))) {
        fprintf(stderr, "setup: unable to resolve share cli path\\n");
        return D_APP_EXIT_FAILURE;
    }
    if (snprintf(cmd, sizeof(cmd), "python") <= 0) {
        fprintf(stderr, "setup: failed to build share command\\n");
        return D_APP_EXIT_FAILURE;
    }
    if (!setup_append_quoted(cmd, sizeof(cmd), script_path)) {
        fprintf(stderr, "setup: share command too long\\n");
        return D_APP_EXIT_FAILURE;
    }
    for (i = cmd_index + 1; i < argc; ++i) {
        if (!setup_append_quoted(cmd, sizeof(cmd), argv[i])) {
            fprintf(stderr, "setup: share command too long\\n");
            return D_APP_EXIT_FAILURE;
        }
    }
    rc = system(cmd);
    if (rc == -1) {
        fprintf(stderr, "setup: failed to run share cli\\n");
        return D_APP_EXIT_FAILURE;
    }
    return rc;
}

static int setup_args_has_prefix(int argc, char** argv, const char* prefix)
{
    size_t prefix_len;
    int i;
    if (!prefix || !prefix[0]) {
        return 0;
    }
    prefix_len = strlen(prefix);
    for (i = 1; i < argc; ++i) {
        if (strncmp(argv[i], prefix, prefix_len) == 0) {
            return 1;
        }
    }
    return 0;
}

static int setup_resolve_setup_script(char* out, size_t cap)
{
    const char* rel = "tools/setup/setup_cli.py";
    if (!out || cap == 0u) {
        return 0;
    }
    out[0] = '\0';
    if (setup_find_upward(out, cap, rel)) {
        return 1;
    }
    rel = "setup/setup_cli.py";
    if (setup_find_upward(out, cap, rel)) {
        return 1;
    }
    strncpy(out, "tools/setup/setup_cli.py", cap - 1u);
    out[cap - 1u] = '\0';
    return 1;
}

static int setup_run_setup_cli(int argc, char** argv, const char* ui_mode_override)
{
    char script_path[512];
    char cmd[4096];
    int i;
    int rc;
    int have_ui_mode = 0;

    if (!setup_resolve_setup_script(script_path, sizeof(script_path))) {
        fprintf(stderr, "setup: unable to resolve setup cli path\n");
        return D_APP_EXIT_FAILURE;
    }
    if (snprintf(cmd, sizeof(cmd), "python") <= 0) {
        fprintf(stderr, "setup: failed to build setup command\n");
        return D_APP_EXIT_FAILURE;
    }
    if (!setup_append_quoted(cmd, sizeof(cmd), script_path)) {
        fprintf(stderr, "setup: setup command too long\n");
        return D_APP_EXIT_FAILURE;
    }
    have_ui_mode = setup_args_has_prefix(argc, argv, "--ui-mode");
    for (i = 1; i < argc; ++i) {
        if (!setup_append_quoted(cmd, sizeof(cmd), argv[i])) {
            fprintf(stderr, "setup: setup command too long\n");
            return D_APP_EXIT_FAILURE;
        }
    }
    if (!have_ui_mode && ui_mode_override && ui_mode_override[0]) {
        if (!setup_append_quoted(cmd, sizeof(cmd), "--ui-mode")) {
            fprintf(stderr, "setup: setup command too long\n");
            return D_APP_EXIT_FAILURE;
        }
        if (!setup_append_quoted(cmd, sizeof(cmd), ui_mode_override)) {
            fprintf(stderr, "setup: setup command too long\n");
            return D_APP_EXIT_FAILURE;
        }
    }
    rc = system(cmd);
    if (rc == -1) {
        fprintf(stderr, "setup: failed to run setup cli\n");
        return D_APP_EXIT_FAILURE;
    }
    return rc;
}

static char setup_path_sep(void)
{
#if defined(_WIN32)
    return '\\\\';
#else
    return '/';
#endif
}

static int setup_mkdir(const char* path)
{
    int rc;
    if (!path || !path[0]) {
        return -1;
    }
#if defined(_WIN32)
    rc = _mkdir(path);
#else
    rc = mkdir(path, 0755);
#endif
    if (rc == 0) {
        return 0;
    }
    if (errno == EEXIST) {
        return 0;
    }
    return -1;
}

static int setup_join_path(char* out, size_t cap, const char* root, const char* leaf)
{
    size_t root_len;
    int written;
    char sep;
    if (!out || cap == 0u || !leaf) {
        return -1;
    }
    if (!root || !root[0]) {
        root = ".";
    }
    root_len = strlen(root);
    sep = setup_path_sep();
    if (root_len > 0u && root[root_len - 1u] != '/' && root[root_len - 1u] != '\\\\') {
        written = snprintf(out, cap, "%s%c%s", root, sep, leaf);
    } else {
        written = snprintf(out, cap, "%s%s", root, leaf);
    }
    if (written <= 0 || (size_t)written >= cap) {
        return -1;
    }
    return 0;
}

static int setup_prepare(const char* root)
{
    static const char* dirs[] = { "program", "data", "user", "state", "temp" };
    char path[512];
    size_t i;
    if (!root || !root[0]) {
        root = ".";
    }
    if (setup_mkdir(root) != 0) {
        fprintf(stderr, "setup: failed to create root '%s' (%s)\\n", root, strerror(errno));
        return D_APP_EXIT_FAILURE;
    }
    printf("setup_prepare_root=%s\\n", root);
    for (i = 0u; i < (sizeof(dirs) / sizeof(dirs[0])); ++i) {
        if (setup_join_path(path, sizeof(path), root, dirs[i]) != 0) {
            fprintf(stderr, "setup: path too long for '%s'\\n", dirs[i]);
            return D_APP_EXIT_FAILURE;
        }
        if (setup_mkdir(path) != 0) {
            fprintf(stderr, "setup: failed to create '%s' (%s)\\n", path, strerror(errno));
            return D_APP_EXIT_FAILURE;
        }
        printf("setup_prepare_dir=%s\\n", path);
    }
    printf("setup_prepare=ok\\n");
    return D_APP_EXIT_OK;
}

static int setup_run_tui(int argc, char** argv)
{
    return setup_run_setup_cli(argc, argv, "tui");
}

static int setup_run_gui(int argc, char** argv)
{
    return setup_run_setup_cli(argc, argv, "gui");
}

int setup_main(int argc, char** argv)
{
    const char* control_registry_path = "data/registries/control_capabilities.registry";
    char control_registry_buf[512];
    const char* control_enable = 0;
    const char* prepare_root = ".";
    int want_build_info = 0;
    int want_status = 0;
    int want_smoke = 0;
    int want_selftest = 0;
    int want_deterministic = 0;
    int want_interactive = 0;
    dom_app_ui_request ui_req;
    dom_app_ui_mode ui_mode = DOM_APP_UI_NONE;
    setup_control_caps caps;
    int control_loaded = 0;
    const char* cmd = 0;
    int cmd_index = -1;
    int i;

    dom_app_ui_request_init(&ui_req);

    for (i = 1; i < argc; ++i) {
        int ui_consumed = 0;
        char ui_err[96];
        int ui_res = dom_app_parse_ui_arg(&ui_req,
                                          argv[i],
                                          (i + 1 < argc) ? argv[i + 1] : 0,
                                          &ui_consumed,
                                          ui_err,
                                          sizeof(ui_err));
        if (ui_res < 0) {
            fprintf(stderr, "setup: %s\\n", ui_err);
            return D_APP_EXIT_USAGE;
        }
        if (ui_res > 0) {
            i += ui_consumed - 1;
            continue;
        }
        if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            cmd = argv[i];
            cmd_index = i;
            break;
        }
        if (strcmp(argv[i], "--version") == 0) {
            cmd = argv[i];
            cmd_index = i;
            break;
        }
        if (strcmp(argv[i], "--build-info") == 0) {
            want_build_info = 1;
            continue;
        }
        if (strcmp(argv[i], "--status") == 0) {
            want_status = 1;
            continue;
        }
        if (strcmp(argv[i], "--smoke") == 0) {
            want_smoke = 1;
            continue;
        }
        if (strcmp(argv[i], "--selftest") == 0) {
            want_selftest = 1;
            continue;
        }
        if (strcmp(argv[i], "--deterministic") == 0) {
            want_deterministic = 1;
            if (i + 1 < argc && (strcmp(argv[i + 1], "0") == 0 || strcmp(argv[i + 1], "1") == 0)) {
                want_deterministic = (strcmp(argv[i + 1], "1") == 0) ? 1 : 0;
                i += 1;
            }
            continue;
        }
        if (strncmp(argv[i], "--deterministic=", 16) == 0) {
            const char* value = argv[i] + 16;
            want_deterministic = (value && strcmp(value, "0") != 0) ? 1 : 0;
            continue;
        }
        if (strcmp(argv[i], "--interactive") == 0) {
            want_interactive = 1;
            if (i + 1 < argc && (strcmp(argv[i + 1], "0") == 0 || strcmp(argv[i + 1], "1") == 0)) {
                want_interactive = (strcmp(argv[i + 1], "1") == 0) ? 1 : 0;
                i += 1;
            }
            continue;
        }
        if (strncmp(argv[i], "--interactive=", 14) == 0) {
            const char* value = argv[i] + 14;
            want_interactive = (value && strcmp(value, "0") != 0) ? 1 : 0;
            continue;
        }
        if (strncmp(argv[i], "--root=", 7) == 0) {
            prepare_root = argv[i] + 7;
            continue;
        }
        if (strcmp(argv[i], "--root") == 0 && i + 1 < argc) {
            prepare_root = argv[i + 1];
            i += 1;
            continue;
        }
        if (strcmp(argv[i], "--control-registry") == 0 && i + 1 < argc) {
            control_registry_path = argv[i + 1];
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--control-enable=", 17) == 0) {
            control_enable = argv[i] + 17;
            continue;
        }
        if (strcmp(argv[i], "--control-enable") == 0 && i + 1 < argc) {
            control_enable = argv[i + 1];
            i += 1;
            continue;
        }
        if (argv[i][0] != '-') {
            cmd = argv[i];
            cmd_index = i;
            break;
        }
    }
    if (want_smoke || want_selftest) {
        if (!cmd) {
            cmd = "status";
        }
    }
    if (cmd && strcmp(cmd, "prepare") == 0 && cmd_index >= 0) {
        for (i = cmd_index + 1; i < argc; ++i) {
            if (strncmp(argv[i], "--root=", 7) == 0) {
                prepare_root = argv[i] + 7;
                continue;
            }
            if (strcmp(argv[i], "--root") == 0 && i + 1 < argc) {
                prepare_root = argv[i + 1];
                i += 1;
                continue;
            }
        }
    }
    if (want_deterministic && want_interactive) {
        fprintf(stderr, "setup: --deterministic and --interactive are mutually exclusive\\n");
        return D_APP_EXIT_USAGE;
    }
    if ((want_smoke || want_selftest) && want_interactive) {
        fprintf(stderr, "setup: --smoke requires deterministic mode\\n");
        return D_APP_EXIT_USAGE;
    }
    ui_mode = dom_app_select_ui_mode(&ui_req, DOM_APP_UI_NONE);
    if ((ui_mode == DOM_APP_UI_TUI || ui_mode == DOM_APP_UI_GUI) &&
        (want_build_info || want_status || want_smoke || want_selftest ||
         (cmd && strcmp(cmd, "--help") != 0 && strcmp(cmd, "-h") != 0 &&
          strcmp(cmd, "--version") != 0))) {
        fprintf(stderr, "setup: --ui=%s cannot combine with CLI commands\\n",
                dom_app_ui_mode_name(ui_mode));
        return D_APP_EXIT_USAGE;
    }
    if (!cmd && !want_build_info && !want_status && ui_mode == DOM_APP_UI_NONE) {
        setup_print_help();
        return D_APP_EXIT_USAGE;
    }

    if (cmd && (strcmp(cmd, "--help") == 0 || strcmp(cmd, "-h") == 0)) {
        setup_print_help();
        return D_APP_EXIT_OK;
    }
    if (ui_mode == DOM_APP_UI_TUI && !cmd && !want_build_info && !want_status) {
        return setup_run_tui(argc, argv);
    }
    if (ui_mode == DOM_APP_UI_GUI && !cmd && !want_build_info && !want_status) {
        fprintf(stderr, "setup: gui not implemented\n");
        return D_APP_EXIT_UNAVAILABLE;
    }

    setup_resolve_control_registry(control_registry_buf,
                                   sizeof(control_registry_buf),
                                   control_registry_path);
    control_registry_path = control_registry_buf;

    if (want_status || (cmd && strcmp(cmd, "status") == 0) || control_enable) {
        if (control_caps_init(&caps, control_registry_path) != 0) {
            fprintf(stderr, "setup: failed to load control registry: %s\\n", control_registry_path);
            return D_APP_EXIT_FAILURE;
        }
        control_loaded = 1;
        if (enable_control_list(&caps, control_enable) != 0) {
            fprintf(stderr, "setup: invalid control capability list\\n");
            control_free_caps(&caps);
            return D_APP_EXIT_USAGE;
        }
    }
    if (want_build_info) {
        if (!control_loaded && !control_enable) {
            if (control_caps_init(&caps, control_registry_path) == 0) {
                control_loaded = 1;
            }
        }
        print_build_info("setup", DOMINIUM_SETUP_VERSION);
        if (control_loaded) {
            print_control_caps(&caps);
            control_free_caps(&caps);
        }
        return D_APP_EXIT_OK;
    }
    if (cmd && strcmp(cmd, "status") == 0) {
        int status;
        if (!control_loaded) {
            if (control_caps_init(&caps, control_registry_path) != 0) {
                fprintf(stderr, "setup: failed to load control registry: %s\\n", control_registry_path);
                return D_APP_EXIT_FAILURE;
            }
            control_loaded = 1;
        }
        printf("setup status: ok (stub)\\n");
        status = dsk_setup_status();
        print_control_caps(&caps);
        control_free_caps(&caps);
        return status;
    }
    if (want_status) {
        if (!control_loaded) {
            if (control_caps_init(&caps, control_registry_path) != 0) {
                fprintf(stderr, "setup: failed to load control registry: %s\\n", control_registry_path);
                return D_APP_EXIT_FAILURE;
            }
            control_loaded = 1;
        }
        print_control_caps(&caps);
        control_free_caps(&caps);
        return D_APP_EXIT_OK;
    }
    if (!cmd) {
        setup_print_help();
        return D_APP_EXIT_USAGE;
    }
    if (strcmp(cmd, "--version") == 0 || strcmp(cmd, "version") == 0) {
        print_version(DOMINIUM_SETUP_VERSION);
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "prepare") == 0) {
        return setup_prepare(prepare_root);
    }
    if (strcmp(cmd, "ops") == 0) {
        return setup_run_ops(argc, argv, cmd_index);
    }
    if (strcmp(cmd, "share") == 0) {
        return setup_run_share(argc, argv, cmd_index);
    }
    if (strcmp(cmd, "install") == 0 ||
        strcmp(cmd, "repair") == 0 ||
        strcmp(cmd, "uninstall") == 0 ||
        strcmp(cmd, "rollback") == 0 ||
        strcmp(cmd, "export-invocation") == 0 ||
        strcmp(cmd, "plan") == 0 ||
        strcmp(cmd, "apply") == 0 ||
        strcmp(cmd, "detect") == 0 ||
        strcmp(cmd, "manifest") == 0) {
        return setup_run_setup_cli(argc, argv, "cli");
    }

    printf("setup: unknown command '%s'\\n", cmd);
    setup_print_help();
    return D_APP_EXIT_USAGE;
}

int main(int argc, char** argv)
{
    return setup_main(argc, argv);
}
