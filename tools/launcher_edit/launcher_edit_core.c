/*
FILE: source/dominium/tools/launcher_edit/launcher_edit_core.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/launcher_edit/launcher_edit_core
RESPONSIBILITY: Implements `launcher_edit_core`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/architecture/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdio.h>
#include "dominium/launcher_edit_api.h"
#include "domino/sys.h"

#define DOM_LAUNCHER_MAX_TABS 64

typedef struct dom_launcher_tab_t {
    char view_id[64];
    char title[64];
    uint32_t index;
} dom_launcher_tab;

typedef struct dom_launcher_edit_ctx_t {
    char path[260];
    dom_launcher_tab tabs[DOM_LAUNCHER_MAX_TABS];
    int tab_count;
    int dirty;
} dom_launcher_edit_ctx;

static void dom_launcher_edit_parse_line(dom_launcher_edit_ctx *ctx, const char *line)
{
    const char *first_colon;
    const char *second_colon;
    dom_launcher_tab *t;
    if (!ctx || !line || ctx->tab_count >= DOM_LAUNCHER_MAX_TABS) return;
    first_colon = strchr(line, ':');
    if (!first_colon) return;
    second_colon = strchr(first_colon + 1, ':');
    if (!second_colon) return;

    t = &ctx->tabs[ctx->tab_count];
    memset(t, 0, sizeof(*t));
    t->index = (uint32_t)strtoul(line, NULL, 10);
    strncpy(t->view_id, first_colon + 1, (size_t)(second_colon - first_colon - 1) < sizeof(t->view_id) ? (size_t)(second_colon - first_colon - 1) : sizeof(t->view_id) - 1);
    strncpy(t->title, second_colon + 1, sizeof(t->title) - 1);
    ctx->tab_count++;
}

static void dom_launcher_edit_load(dom_launcher_edit_ctx *ctx)
{
    void *f;
    char buffer[512];
    size_t nread;
    size_t start = 0;
    size_t i;
    f = dsys_file_open(ctx->path, "rb");
    if (!f) return;

    while ((nread = dsys_file_read(f, buffer + start, sizeof(buffer) - start - 1)) > 0) {
        size_t total = start + nread;
        buffer[total] = '\0';
        start = 0;
        for (i = 0; i < total; ++i) {
            if (buffer[i] == '\n') {
                buffer[i] = '\0';
                dom_launcher_edit_parse_line(ctx, buffer + start);
                start = i + 1;
            }
        }
        if (start < total && start > 0) {
            memmove(buffer, buffer + start, total - start);
            start = total - start;
        }
    }
    if (start > 0) {
        buffer[start] = '\0';
        dom_launcher_edit_parse_line(ctx, buffer);
    }

    dsys_file_close(f);
}

dom_launcher_edit_ctx *dom_launcher_edit_open(const dom_launcher_edit_desc *desc)
{
    dom_launcher_edit_ctx *ctx;
    const char *path = "data/launcher/config.txt";
    if (desc && desc->config_path) {
        path = desc->config_path;
    }
    ctx = (dom_launcher_edit_ctx*)malloc(sizeof(dom_launcher_edit_ctx));
    if (!ctx) return NULL;
    memset(ctx, 0, sizeof(*ctx));
    strncpy(ctx->path, path, sizeof(ctx->path) - 1);
    ctx->path[sizeof(ctx->path) - 1] = '\0';
    dom_launcher_edit_load(ctx);
    return ctx;
}

void dom_launcher_edit_close(dom_launcher_edit_ctx *ctx)
{
    if (!ctx) return;
    free(ctx);
}

int dom_launcher_edit_list_tabs(dom_launcher_edit_ctx *ctx,
                                char *buf,
                                uint32_t buf_size)
{
    uint32_t written = 0;
    int i;
    if (!ctx || !buf || buf_size == 0) return -1;
    for (i = 0; i < ctx->tab_count; ++i) {
        dom_launcher_tab *t = &ctx->tabs[i];
        char line[256];
        size_t len;
        sprintf(line, "%u:%s:%s\n", (unsigned)t->index, t->view_id, t->title);
        len = strlen(line);
        if (written + len >= buf_size) break;
        memcpy(buf + written, line, len);
        written += (uint32_t)len;
    }
    if (written < buf_size) buf[written] = '\0';
    return (int)written;
}

int dom_launcher_edit_add_tab(dom_launcher_edit_ctx *ctx,
                              const char *view_id,
                              const char *title,
                              uint32_t index)
{
    dom_launcher_tab *t;
    if (!ctx || !view_id || !title) return -1;
    if (ctx->tab_count >= DOM_LAUNCHER_MAX_TABS) return -1;
    t = &ctx->tabs[ctx->tab_count++];
    memset(t, 0, sizeof(*t));
    strncpy(t->view_id, view_id, sizeof(t->view_id) - 1);
    strncpy(t->title, title, sizeof(t->title) - 1);
    t->index = index;
    ctx->dirty = 1;
    return 0;
}

int dom_launcher_edit_remove_tab(dom_launcher_edit_ctx *ctx,
                                 const char *view_id)
{
    int i;
    if (!ctx || !view_id) return -1;
    for (i = 0; i < ctx->tab_count; ++i) {
        if (strcmp(ctx->tabs[i].view_id, view_id) == 0) {
            memmove(&ctx->tabs[i], &ctx->tabs[i + 1], (size_t)(ctx->tab_count - i - 1) * sizeof(dom_launcher_tab));
            ctx->tab_count--;
            ctx->dirty = 1;
            return 0;
        }
    }
    return -1;
}

int dom_launcher_edit_save(dom_launcher_edit_ctx *ctx)
{
    void *f;
    int i;
    char line[256];
    if (!ctx) return -1;

    f = dsys_file_open(ctx->path, "wb");
    if (!f) return -1;
    for (i = 0; i < ctx->tab_count; ++i) {
        dom_launcher_tab *t = &ctx->tabs[i];
        sprintf(line, "%u:%s:%s\n", (unsigned)t->index, t->view_id, t->title);
        dsys_file_write(f, line, strlen(line));
    }
    dsys_file_close(f);
    ctx->dirty = 0;
    return 0;
}
