/*
FILE: source/dominium/tools/replay/tool_replay.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/replay/tool_replay
RESPONSIBILITY: Implements `tool_replay`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/architecture/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
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

static void usage(void)
{
    printf("Usage: replay --input <replay_file> [--summary] [--dump-timeline <out_file>]\n");
}

int dom_tool_replay_main(dom_tool_ctx* ctx, int argc, char** argv)
{
    const char* input = NULL;
    const char* dump_path = NULL;
    int summary = 0;
    int i;
    void* in;
    void* out = NULL;
    unsigned char buffer[1024];
    size_t nread;
    unsigned long bytes = 0;
    unsigned long events = 0;
    unsigned long tick = 0;
    unsigned long checksum = 0;

    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--input") == 0 && i + 1 < argc) {
            input = argv[++i];
        } else if (strcmp(argv[i], "--summary") == 0) {
            summary = 1;
        } else if (strcmp(argv[i], "--dump-timeline") == 0 && i + 1 < argc) {
            dump_path = argv[++i];
        } else {
            usage();
            return 1;
        }
    }

    if (!input) {
        usage();
        return 1;
    }

    if (dsys_init() != DSYS_OK) {
        tool_err(ctx, "Failed to initialize dsys\n");
        return 1;
    }

    in = dsys_file_open(input, "rb");
    if (!in) {
        tool_err(ctx, "Unable to open replay file\n");
        dsys_shutdown();
        return 1;
    }

    if (dump_path) {
        out = dsys_file_open(dump_path, "wb");
        if (!out) {
            tool_err(ctx, "Unable to open dump output file\n");
            dsys_file_close(in);
            dsys_shutdown();
            return 1;
        }
        dsys_file_write(out, "tick,event_count,checksum\n", 28);
    }

    while ((nread = dsys_file_read(in, buffer, sizeof(buffer))) > 0) {
        size_t idx = 0;
        bytes += (unsigned long)nread;
        for (idx = 0; idx < nread; ++idx) {
            checksum = (checksum * 16777619u) ^ buffer[idx];
        }
        events += (unsigned long)(nread / 16);
        if (dump_path) {
            char line[128];
            sprintf(line, "%lu,%lu,%lu\n", tick, events, checksum);
            dsys_file_write(out, line, strlen(line));
        }
        ++tick;
    }

    dsys_file_close(in);
    if (out) {
        dsys_file_close(out);
    }

    if (summary || !dump_path) {
        char msg[256];
        sprintf(msg, "Replay summary:\n  bytes=%lu\n  events=%lu\n  ticks=%lu\n  checksum=%lu\n",
                bytes, events, tick, checksum);
        tool_log(ctx, msg);
    }

    dsys_shutdown();
    return 0;
}
