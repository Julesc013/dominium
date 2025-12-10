#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "dominium/tool_api.h"
#include "domino/sys.h"

#define DOM_PATH_MAX 512

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
    if (!dst || cap == 0) {
        return;
    }
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
    if (root && (root[0] == '/' || root[0] == '\\' || (root[0] != '\0' && root[1] == ':'))) {
        join_path(out, cap, root, rel);
        return;
    }
    app_root[0] = '\0';
    combined[0] = '\0';
    dsys_get_path(DSYS_PATH_APP_ROOT, app_root, sizeof(app_root));
    join_path(combined, sizeof(combined), app_root, root ? root : "");
    join_path(out, cap, combined, rel);
}

static int copy_file(const char* src, const char* dst)
{
    void* in;
    void* out;
    unsigned char buffer[4096];
    size_t nread;

    in = dsys_file_open(src, "rb");
    if (!in) {
        return -1;
    }
    out = dsys_file_open(dst, "wb");
    if (!out) {
        dsys_file_close(in);
        return -1;
    }
    while ((nread = dsys_file_read(in, buffer, sizeof(buffer))) > 0) {
        size_t nwritten = dsys_file_write(out, buffer, nread);
        if (nwritten != nread) {
            dsys_file_close(in);
            dsys_file_close(out);
            return -1;
        }
    }
    dsys_file_close(in);
    dsys_file_close(out);
    return 0;
}

static void usage(void)
{
    printf("Usage: assetc --input <src_dir> --output <pack_dir> [--type graphics|sounds|music] [--name <pack_name>]\n");
}

int dom_tool_assetc_main(dom_tool_ctx* ctx, int argc, char** argv)
{
    const char* input_flag = NULL;
    const char* output_flag = NULL;
    const char* type_flag = "graphics";
    const char* name_flag = "default";
    int i;
    char input_root[DOM_PATH_MAX];
    char output_root[DOM_PATH_MAX];
    char src_dir[DOM_PATH_MAX];
    char dst_dir[DOM_PATH_MAX];
    char manifest_path[DOM_PATH_MAX];
    dsys_dir_iter* it;
    dsys_dir_entry entry;
    void* manifest;
    int wrote_any = 0;

    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--input") == 0 && i + 1 < argc) {
            input_flag = argv[++i];
        } else if (strcmp(argv[i], "--output") == 0 && i + 1 < argc) {
            output_flag = argv[++i];
        } else if (strcmp(argv[i], "--type") == 0 && i + 1 < argc) {
            type_flag = argv[++i];
        } else if (strcmp(argv[i], "--name") == 0 && i + 1 < argc) {
            name_flag = argv[++i];
        } else {
            usage();
            return 1;
        }
    }

    if (!input_flag) {
        input_flag = "data/authoring";
    }
    if (!output_flag) {
        output_flag = "data/packs";
    }
    if (strcmp(type_flag, "graphics") != 0 &&
        strcmp(type_flag, "sounds") != 0 &&
        strcmp(type_flag, "music") != 0) {
        tool_err(ctx, "Invalid --type (expected graphics|sounds|music)\n");
        return 1;
    }

    if (dsys_init() != DSYS_OK) {
        tool_err(ctx, "Failed to initialize dsys\n");
        return 1;
    }

    build_path(input_flag, type_flag, input_root, sizeof(input_root));
    build_path(output_flag, type_flag, output_root, sizeof(output_root));
    join_path(src_dir, sizeof(src_dir), input_root, "");
    join_path(dst_dir, sizeof(dst_dir), output_root, name_flag);
    join_path(manifest_path, sizeof(manifest_path), dst_dir, "manifest.txt");

    tool_log(ctx, "Dominium asset compiler\n");
    tool_log(ctx, "Scanning input directory...\n");

    it = dsys_dir_open(src_dir);
    if (!it) {
        tool_err(ctx, "Unable to open input directory\n");
        dsys_shutdown();
        return 1;
    }

    manifest = dsys_file_open(manifest_path, "wb");
    if (!manifest) {
        tool_err(ctx, "Unable to write manifest (ensure output path exists)\n");
        dsys_dir_close(it);
        dsys_shutdown();
        return 1;
    }

    while (dsys_dir_next(it, &entry)) {
        char src_file[DOM_PATH_MAX];
        char dst_file[DOM_PATH_MAX];
        if (entry.is_dir) {
            continue;
        }
        join_path(src_file, sizeof(src_file), src_dir, entry.name);
        join_path(dst_file, sizeof(dst_file), dst_dir, entry.name);
        if (copy_file(src_file, dst_file) == 0) {
            char line[DOM_PATH_MAX];
            wrote_any = 1;
            tool_log(ctx, "Packed: ");
            tool_log(ctx, entry.name);
            tool_log(ctx, "\n");
            sprintf(line, "file=%s\n", entry.name);
            dsys_file_write(manifest, line, strlen(line));
        } else {
            tool_err(ctx, "Failed to pack file\n");
        }
    }

    dsys_dir_close(it);
    dsys_file_close(manifest);

    if (!wrote_any) {
        tool_err(ctx, "No files packed (check input path/type)\n");
        dsys_shutdown();
        return 1;
    }

    tool_log(ctx, "Asset compilation complete\n");
    dsys_shutdown();
    return 0;
}
