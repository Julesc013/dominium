/*
Stub setup CLI entrypoint.
*/
#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/config_base.h"
#include "domino/gfx.h"
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#if defined(_WIN32)
#include <direct.h>
#else
#include <sys/stat.h>
#endif

#include "dsk/dsk_setup.h"

static void print_version(const char* product_version)
{
    printf("setup %s\\n", product_version);
}

static void print_build_info(const char* product_name, const char* product_version)
{
    printf("product=%s\n", product_name);
    printf("product_version=%s\n", product_version);
    printf("engine_version=%s\n", DOMINO_VERSION_STRING);
    printf("game_version=%s\n", DOMINIUM_GAME_VERSION);
    printf("build_number=%u\n", (unsigned int)DOM_BUILD_NUMBER);
    printf("build_id=%s\n", DOM_BUILD_ID);
    printf("git_hash=%s\n", DOM_GIT_HASH);
    printf("toolchain_id=%s\n", DOM_TOOLCHAIN_ID);
    printf("protocol_law_targets=LAW_TARGETS@1.4.0\n");
    printf("protocol_control_caps=CONTROL_CAPS@1.0.0\n");
    printf("protocol_authority_tokens=AUTHORITY_TOKEN@1.0.0\n");
    printf("abi_dom_build_info=%u\n", (unsigned int)DOM_BUILD_INFO_ABI_VERSION);
    printf("abi_dom_caps=%u\n", (unsigned int)DOM_CAPS_ABI_VERSION);
    printf("api_dsys=%u\n", 1u);
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
    printf("  --root <path>                Install root for prepare command\\n");
    printf("  --control-enable=K1,K2       Enable control capabilities (canonical keys)\\n");
    printf("  --control-registry <path>    Override control registry path\\n");
    printf("commands:\\n");
    printf("  version   Show setup version\\n");
    printf("  status    Show setup status\\n");
    printf("  prepare   Create empty install layout\\n");
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
    size_t leaf_len;
    size_t total;
    char sep;
    if (!out || cap == 0u || !leaf) {
        return -1;
    }
    if (!root || !root[0]) {
        root = ".";
    }
    root_len = strlen(root);
    leaf_len = strlen(leaf);
    sep = setup_path_sep();
    total = root_len + leaf_len + 2u;
    if (total > cap) {
        return -1;
    }
    memcpy(out, root, root_len);
    if (root_len > 0u && root[root_len - 1u] != '/' && root[root_len - 1u] != '\\\\') {
        out[root_len++] = sep;
    }
    memcpy(out + root_len, leaf, leaf_len);
    out[root_len + leaf_len] = '\\0';
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
        return 2;
    }
    printf("setup_prepare_root=%s\\n", root);
    for (i = 0u; i < (sizeof(dirs) / sizeof(dirs[0])); ++i) {
        if (setup_join_path(path, sizeof(path), root, dirs[i]) != 0) {
            fprintf(stderr, "setup: path too long for '%s'\\n", dirs[i]);
            return 2;
        }
        if (setup_mkdir(path) != 0) {
            fprintf(stderr, "setup: failed to create '%s' (%s)\\n", path, strerror(errno));
            return 2;
        }
        printf("setup_prepare_dir=%s\\n", path);
    }
    printf("setup_prepare=ok\\n");
    return 0;
}

int main(int argc, char** argv)
{
    const char* control_registry_path = "data/registries/control_capabilities.registry";
    const char* control_enable = 0;
    const char* prepare_root = ".";
    int want_build_info = 0;
    int want_status = 0;
    int want_smoke = 0;
    int want_selftest = 0;
    const char* cmd = 0;
    int i;

    if (argc <= 1) {
        setup_print_help();
        return 0;
    }

    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            cmd = argv[i];
            break;
        }
        if (strcmp(argv[i], "--version") == 0) {
            cmd = argv[i];
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
            break;
        }
    }
    if (want_smoke || want_selftest) {
        if (!cmd) {
            cmd = "status";
        }
    }
    if (!cmd && !want_build_info && !want_status) {
        setup_print_help();
        return 2;
    }

    if (strcmp(cmd, "--help") == 0 || strcmp(cmd, "-h") == 0) {
        setup_print_help();
        return 0;
    }
    if (want_build_info || want_status || (cmd && strcmp(cmd, "status") == 0)) {
        setup_control_caps caps;
        if (control_caps_init(&caps, control_registry_path) != 0) {
            fprintf(stderr, "setup: failed to load control registry: %s\\n", control_registry_path);
            return 2;
        }
        if (enable_control_list(&caps, control_enable) != 0) {
            fprintf(stderr, "setup: invalid control capability list\\n");
            control_free_caps(&caps);
            return 2;
        }
        if (want_build_info) {
            print_build_info("setup", DOMINIUM_SETUP_VERSION);
        }
        if (cmd && strcmp(cmd, "status") == 0) {
            int status;
            printf("setup status: ok (stub)\\n");
            status = dsk_setup_status();
            print_control_caps(&caps);
            control_free_caps(&caps);
            return status;
        }
        print_control_caps(&caps);
        control_free_caps(&caps);
        return 0;
    }
    if (!cmd) {
        setup_print_help();
        return 2;
    }
    if (strcmp(cmd, "--version") == 0 || strcmp(cmd, "version") == 0) {
        print_version(DOMINIUM_SETUP_VERSION);
        return 0;
    }
    if (strcmp(cmd, "prepare") == 0) {
        return setup_prepare(prepare_root);
    }

    printf("setup: unknown command '%s'\\n", cmd);
    setup_print_help();
    return 2;
}
