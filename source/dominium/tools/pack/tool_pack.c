/*
FILE: source/dominium/tools/pack/tool_pack.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/pack/tool_pack
RESPONSIBILITY: Implements `tool_pack`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "dominium/tool_api.h"
#include "domino/sys.h"

#define DOM_PATH_MAX 512
#define MAX_PACKS    16

static void tool_log(dom_tool_ctx* ctx, const char* msg)
{
    if (ctx && ctx->env.write_stdout) {
        ctx->env.write_stdout(msg, ctx->env.io_user);
    } else {
        printf("%s", msg);
    }
}

static void tool_err(dom_tool_ctx* ctx, const char* msg)
{
    if (ctx && ctx->env.write_stderr) {
        ctx->env.write_stderr(msg, ctx->env.io_user);
    } else {
        fprintf(stderr, "%s", msg);
    }
}

static void join_path(char* dst, size_t cap, const char* a, const char* b)
{
    size_t i = 0;
    size_t j = 0;
    if (!dst || cap == 0) return;
    dst[0] = '\0';
    if (a) {
        while (a[i] != '\0' && i + 1 < cap) {
            dst[i] = a[i];
            ++i;
        }
    }
    if (i > 0 && dst[i - 1] != '/' && dst[i - 1] != '\\' && b && b[0] != '\0') {
        if (i + 1 < cap) {
            dst[i++] = '/';
        }
    }
    if (b) {
        while (b[j] != '\0' && i + 1 < cap) {
            dst[i++] = b[j++];
        }
    }
    dst[i] = '\0';
}

static void build_path(const char* root, const char* rel, char* out, size_t cap)
{
    char app_root[DOM_PATH_MAX];
    char combined[DOM_PATH_MAX];
    app_root[0] = '\0';
    combined[0] = '\0';
    dsys_get_path(DSYS_PATH_APP_ROOT, app_root, sizeof(app_root));

    if (root && (root[0] == '/' || root[0] == '\\' || (root[0] != '\0' && root[1] == ':'))) {
        join_path(out, cap, root, rel);
    } else {
        join_path(combined, sizeof(combined), app_root, root ? root : "");
        join_path(out, cap, combined, rel);
    }
}

static int write_manifest(const char* path, const char* version, const char packs[][64], int pack_count)
{
    void* f;
    int i;
    char line[DOM_PATH_MAX];

    f = dsys_file_open(path, "wb");
    if (!f) {
        return -1;
    }

    sprintf(line, "version=%s\n", version);
    dsys_file_write(f, line, strlen(line));
    for (i = 0; i < pack_count; ++i) {
        sprintf(line, "pack=%s,checksum=0,compat=any\n", packs[i]);
        dsys_file_write(f, line, strlen(line));
    }
    dsys_file_close(f);
    return 0;
}

static void usage(void)
{
    printf("Usage: pack --version <ver> --output <versions_dir> [--include base,space,war]\n");
}

int dom_tool_pack_main(dom_tool_ctx* ctx, int argc, char** argv)
{
    const char* version = NULL;
    const char* output_flag = "data/versions";
    const char* include_flag = NULL;
    char packs[MAX_PACKS][64];
    int pack_count = 0;
    int i;
    char output_root[DOM_PATH_MAX];
    char version_dir[DOM_PATH_MAX];
    char manifest_path[DOM_PATH_MAX];

    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--version") == 0 && i + 1 < argc) {
            version = argv[++i];
        } else if (strcmp(argv[i], "--output") == 0 && i + 1 < argc) {
            output_flag = argv[++i];
        } else if (strcmp(argv[i], "--include") == 0 && i + 1 < argc) {
            include_flag = argv[++i];
        } else {
            usage();
            return 1;
        }
    }

    if (!version) {
        usage();
        return 1;
    }

    if (include_flag) {
        const char* p = include_flag;
        int len = 0;
        char tmp[64];
        while (*p != '\0' && pack_count < MAX_PACKS) {
            if (*p == ',') {
                tmp[len] = '\0';
                strncpy(packs[pack_count], tmp, sizeof(packs[pack_count]) - 1);
                packs[pack_count][sizeof(packs[pack_count]) - 1] = '\0';
                ++pack_count;
                len = 0;
                ++p;
                continue;
            }
            if (len + 1 < (int)sizeof(tmp)) {
                tmp[len++] = *p;
            }
            ++p;
        }
        if (len > 0 && pack_count < MAX_PACKS) {
            tmp[len] = '\0';
            strncpy(packs[pack_count], tmp, sizeof(packs[pack_count]) - 1);
            packs[pack_count][sizeof(packs[pack_count]) - 1] = '\0';
            ++pack_count;
        }
    } else {
        strncpy(packs[0], "base", sizeof(packs[0]) - 1);
        packs[0][sizeof(packs[0]) - 1] = '\0';
        pack_count = 1;
    }

    if (dsys_init() != DSYS_OK) {
        tool_err(ctx, "Failed to initialize dsys\n");
        return 1;
    }

    build_path(output_flag, version, output_root, sizeof(output_root));
    join_path(version_dir, sizeof(version_dir), output_root, "");
    join_path(manifest_path, sizeof(manifest_path), version_dir, "manifest.txt");

    tool_log(ctx, "Dominium pack builder\n");
    tool_log(ctx, "Writing manifest...\n");

    if (write_manifest(manifest_path, version, packs, pack_count) != 0) {
        tool_err(ctx, "Failed to write manifest (ensure output path exists)\n");
        dsys_shutdown();
        return 1;
    }

    tool_log(ctx, "Pack manifest generated\n");
    dsys_shutdown();
    return 0;
}
