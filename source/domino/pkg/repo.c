/*
FILE: source/domino/pkg/repo.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / pkg/repo
RESPONSIBILITY: Implements `repo`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "domino/core/types.h"
#include "domino/pkg/repo.h"

/* Minimal manifest example for reference (posix-x86_64):
{
  "product_id": "dominium_game",
  "role": "game",
  "product_version": "0.0.1",
  "core_version": "0.0.1",
  "os_family": "posix",
  "arch": "x86_64",
  "exec_rel_path": "dominium_game",
  "compat": {
    "save_format_version": 1,
    "pack_format_version": 1,
    "net_protocol_version": 0,
    "replay_format_version": 0,
    "launcher_proto_version": 1,
    "tools_proto_version": 1
  }
}
*/

/* Internal helpers */
static dom_product_role dom_parse_role(const char* s) {
    if (!s) return DOM_PRODUCT_ROLE_UNKNOWN;
    if (strcmp(s, "game") == 0) return DOM_PRODUCT_ROLE_GAME;
    if (strcmp(s, "launcher") == 0) return DOM_PRODUCT_ROLE_LAUNCHER;
    if (strcmp(s, "setup") == 0) return DOM_PRODUCT_ROLE_SETUP;
    if (strcmp(s, "tool") == 0) return DOM_PRODUCT_ROLE_TOOL;
    return DOM_PRODUCT_ROLE_UNKNOWN;
}

static dom_os_family dom_parse_os_family(const char* s) {
    if (!s) return DOM_OS_UNKNOWN;
    if (strcmp(s, "winnt") == 0) return DOM_OS_WINNT;
    if (strcmp(s, "win9x") == 0) return DOM_OS_WIN9X;
    if (strcmp(s, "win3x") == 0) return DOM_OS_WIN3X;
    if (strcmp(s, "dos") == 0) return DOM_OS_DOS;
    if (strcmp(s, "mac_classic") == 0) return DOM_OS_MAC_CLASSIC;
    if (strcmp(s, "mac_carbon") == 0) return DOM_OS_MAC_CARBON;
    if (strcmp(s, "mac_cocoa") == 0) return DOM_OS_MAC_COCOA;
    if (strcmp(s, "posix") == 0) return DOM_OS_POSIX;
    if (strcmp(s, "sdl") == 0) return DOM_OS_SDL;
    if (strcmp(s, "web") == 0) return DOM_OS_WEB;
    if (strcmp(s, "cpm") == 0) return DOM_OS_CPM;
    return DOM_OS_UNKNOWN;
}

static dom_arch dom_parse_arch(const char* s) {
    if (!s) return DOM_ARCH_UNKNOWN;
    if (strcmp(s, "x86_16") == 0) return DOM_ARCH_X86_16;
    if (strcmp(s, "x86_32") == 0) return DOM_ARCH_X86_32;
    if (strcmp(s, "x86_64") == 0) return DOM_ARCH_X86_64;
    if (strcmp(s, "arm_32") == 0) return DOM_ARCH_ARM_32;
    if (strcmp(s, "arm_64") == 0) return DOM_ARCH_ARM_64;
    if (strcmp(s, "m68k_32") == 0) return DOM_ARCH_M68K_32;
    if (strcmp(s, "ppc_32") == 0) return DOM_ARCH_PPC_32;
    if (strcmp(s, "ppc_64") == 0) return DOM_ARCH_PPC_64;
    if (strcmp(s, "z80_8") == 0) return DOM_ARCH_Z80_8;
    if (strcmp(s, "wasm_32") == 0) return DOM_ARCH_WASM_32;
    if (strcmp(s, "wasm_64") == 0) return DOM_ARCH_WASM_64;
    return DOM_ARCH_UNKNOWN;
}

static d_bool dom_json_extract_string(const char* json, const char* key, char* out, u32 out_max) {
    char pattern[64];
    char* pos;
    char* start;
    char* end;
    size_t key_len;
    size_t len;

    if (!json || !key || !out || out_max == 0) return D_FALSE;

    key_len = strlen(key);
    if (key_len + 4 >= sizeof(pattern)) return D_FALSE;
    pattern[0] = '"';
    memcpy(pattern + 1, key, key_len);
    pattern[1 + key_len] = '"';
    pattern[2 + key_len] = '\0';

    pos = strstr(json, pattern);
    if (!pos) return D_FALSE;

    pos = strchr(pos + key_len + 2, ':');
    if (!pos) return D_FALSE;
    pos++;

    while (*pos == ' ' || *pos == '\t' || *pos == '\n' || *pos == '\r') pos++;
    if (*pos != '"') return D_FALSE;
    pos++;
    start = pos;

    end = strchr(start, '"');
    if (!end) return D_FALSE;

    len = (size_t)(end - start);
    if (len + 1 > out_max) return D_FALSE;

    memcpy(out, start, len);
    out[len] = '\0';
    return D_TRUE;
}

static d_bool dom_json_extract_u16(const char* json, const char* key, u16* out) {
    char pattern[64];
    char* pos;
    char* start;
    long val;
    size_t key_len;

    if (!json || !key || !out) return D_FALSE;

    key_len = strlen(key);
    if (key_len + 4 >= sizeof(pattern)) return D_FALSE;
    pattern[0] = '"';
    memcpy(pattern + 1, key, key_len);
    pattern[1 + key_len] = '"';
    pattern[2 + key_len] = '\0';

    pos = strstr(json, pattern);
    if (!pos) return D_FALSE;

    pos = strchr(pos + key_len + 2, ':');
    if (!pos) return D_FALSE;
    pos++;

    while (*pos == ' ' || *pos == '\t' || *pos == '\n' || *pos == '\r') pos++;
    start = pos;
    while (*pos >= '0' && *pos <= '9') pos++;
    if (pos == start) return D_FALSE;

    {
        char buf[16];
        size_t len = (size_t)(pos - start);
        if (len >= sizeof(buf)) len = sizeof(buf) - 1;
        memcpy(buf, start, len);
        buf[len] = '\0';
        val = strtol(buf, (char**)0, 10);
    }

    if (val < 0 || val > 65535) return D_FALSE;
    *out = (u16)val;
    return D_TRUE;
}

d_bool dom_repo_get_root(char* buffer, u32 max_len) {
    const char* env = getenv("DOMINIUM_HOME");
    const char* root = env ? env : ".";
    size_t len;

    if (!buffer || max_len == 0) return D_FALSE;
    len = strlen(root);
    if (len + 1 > max_len) return D_FALSE;
    memcpy(buffer, root, len + 1);
    return D_TRUE;
}

static d_bool dom_repo_read_file(const char* path, char* buffer, u32 max_len) {
    FILE* f;
    size_t rlen;
    if (!path || !buffer || max_len == 0) return D_FALSE;
    f = fopen(path, "rb");
    if (!f) return D_FALSE;
    rlen = fread(buffer, 1, max_len - 1, f);
    buffer[rlen] = '\0';
    fclose(f);
    return D_TRUE;
}

d_bool dom_repo_load_primary_game(dom_product_info* out_info) {
    /* Milestone 0: fixed platform dir; adjust as needed per dev host. */
    const char* platform_dir = "posix-x86_64";
    char root[512];
    char path[1024];
    char json[8192];
    char tmp[DOM_EXEC_PATH_MAX];

    if (!out_info) return D_FALSE;
    memset(out_info, 0, sizeof(dom_product_info));

    if (!dom_repo_get_root(root, sizeof(root))) {
        return D_FALSE;
    }

    /* DOMINIUM_HOME/repo/products/dominium_game/0.0.1/core-0.0.1/<platform>/product.json */
    {
        int n = snprintf(path, sizeof(path),
                         "%s/repo/products/dominium_game/0.0.1/core-0.0.1/%s/product.json",
                         root, platform_dir);
        if (n <= 0 || (size_t)n >= sizeof(path)) {
            return D_FALSE;
        }
    }

    if (!dom_repo_read_file(path, json, sizeof(json))) {
        return D_FALSE;
    }

    if (!dom_json_extract_string(json, "product_id", out_info->product_id, sizeof(out_info->product_id))) return D_FALSE;
    if (!dom_json_extract_string(json, "product_version", out_info->product_version, sizeof(out_info->product_version))) return D_FALSE;
    if (!dom_json_extract_string(json, "core_version", out_info->core_version, sizeof(out_info->core_version))) return D_FALSE;
    if (!dom_json_extract_string(json, "exec_rel_path", out_info->exec_rel_path, sizeof(out_info->exec_rel_path))) return D_FALSE;

    if (dom_json_extract_string(json, "role", tmp, sizeof(tmp))) {
        out_info->role = dom_parse_role(tmp);
    } else {
        out_info->role = DOM_PRODUCT_ROLE_UNKNOWN;
    }

    if (dom_json_extract_string(json, "os_family", tmp, sizeof(tmp))) {
        out_info->os_family = dom_parse_os_family(tmp);
    } else {
        out_info->os_family = DOM_OS_UNKNOWN;
    }

    if (dom_json_extract_string(json, "arch", tmp, sizeof(tmp))) {
        out_info->arch = dom_parse_arch(tmp);
    } else {
        out_info->arch = DOM_ARCH_UNKNOWN;
    }

    /* compat.* fields */
    if (!dom_json_extract_u16(json, "save_format_version", &out_info->compat.save_format_version)) return D_FALSE;
    if (!dom_json_extract_u16(json, "pack_format_version", &out_info->compat.pack_format_version)) return D_FALSE;
    if (!dom_json_extract_u16(json, "net_protocol_version", &out_info->compat.net_protocol_version)) return D_FALSE;
    if (!dom_json_extract_u16(json, "replay_format_version", &out_info->compat.replay_format_version)) return D_FALSE;
    if (!dom_json_extract_u16(json, "launcher_proto_version", &out_info->compat.launcher_proto_version)) return D_FALSE;
    if (!dom_json_extract_u16(json, "tools_proto_version", &out_info->compat.tools_proto_version)) return D_FALSE;

    return D_TRUE;
}
