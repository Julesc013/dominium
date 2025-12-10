#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "dominium/save_edit_api.h"
#include "domino/sys.h"

#define DOM_SAVE_MAX_ENTRIES 128

typedef struct dom_save_entry_t {
    char section[64];
    char key[64];
    char value[256];
} dom_save_entry;

typedef struct dom_save_edit_ctx_t {
    char path[260];
    dom_save_entry entries[DOM_SAVE_MAX_ENTRIES];
    int entry_count;
    int dirty;
} dom_save_edit_ctx;

static void dom_save_edit_parse_line(dom_save_edit_ctx *ctx, const char *line)
{
    const char *eq;
    const char *dot;
    size_t len;
    dom_save_entry *e;
    if (!line || !ctx) return;
    len = strlen(line);
    if (len == 0 || ctx->entry_count >= DOM_SAVE_MAX_ENTRIES) return;
    eq = strchr(line, '=');
    if (!eq) return;
    dot = strchr(line, '.');

    e = &ctx->entries[ctx->entry_count];
    memset(e, 0, sizeof(*e));
    if (dot && dot < eq) {
        size_t sec_len = (size_t)(dot - line);
        size_t key_len = (size_t)(eq - dot - 1);
        if (sec_len >= sizeof(e->section)) sec_len = sizeof(e->section) - 1;
        if (key_len >= sizeof(e->key)) key_len = sizeof(e->key) - 1;
        strncpy(e->section, line, sec_len);
        strncpy(e->key, dot + 1, key_len);
    } else {
        strncpy(e->section, "default", sizeof(e->section) - 1);
        len = (size_t)(eq - line);
        if (len >= sizeof(e->key)) len = sizeof(e->key) - 1;
        strncpy(e->key, line, len);
    }
    strncpy(e->value, eq + 1, sizeof(e->value) - 1);
    /* trim newline */
    len = strlen(e->value);
    if (len > 0 && (e->value[len - 1] == '\n' || e->value[len - 1] == '\r')) {
        e->value[len - 1] = '\0';
    }
    ctx->entry_count++;
}

static void dom_save_edit_load(dom_save_edit_ctx *ctx)
{
    void *f;
    char buffer[512];
    size_t nread;
    size_t start = 0;
    size_t i;

    f = dsys_file_open(ctx->path, "rb");
    if (!f) {
        return;
    }

    while ((nread = dsys_file_read(f, buffer + start, sizeof(buffer) - start - 1)) > 0) {
        size_t total = start + nread;
        buffer[total] = '\0';
        start = 0;
        for (i = 0; i < total; ++i) {
            if (buffer[i] == '\n') {
                buffer[i] = '\0';
                dom_save_edit_parse_line(ctx, buffer + start);
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
        dom_save_edit_parse_line(ctx, buffer);
    }

    dsys_file_close(f);
}

dom_save_edit_ctx *dom_save_edit_open(const dom_save_edit_desc *desc)
{
    dom_save_edit_ctx *ctx;
    const char *path = "state/save_default.dat";
    if (desc && desc->save_path) {
        path = desc->save_path;
    }
    ctx = (dom_save_edit_ctx*)malloc(sizeof(dom_save_edit_ctx));
    if (!ctx) return NULL;
    memset(ctx, 0, sizeof(*ctx));
    strncpy(ctx->path, path, sizeof(ctx->path) - 1);
    ctx->path[sizeof(ctx->path) - 1] = '\0';
    dom_save_edit_load(ctx);
    return ctx;
}

void dom_save_edit_close(dom_save_edit_ctx *ctx)
{
    if (!ctx) return;
    free(ctx);
}

int dom_save_edit_list_keys(dom_save_edit_ctx *ctx,
                            const char *section,
                            char *buf,
                            uint32_t buf_size)
{
    uint32_t written = 0;
    int i;
    if (!ctx || !buf || buf_size == 0) return -1;
    for (i = 0; i < ctx->entry_count; ++i) {
        const dom_save_entry *e = &ctx->entries[i];
        size_t len;
        if (section && strcmp(section, e->section) != 0) continue;
        len = strlen(e->key);
        if (written + len + 1 >= buf_size) break;
        memcpy(buf + written, e->key, len);
        written += (uint32_t)len;
        buf[written++] = '\n';
    }
    if (written < buf_size) buf[written] = '\0';
    return (int)written;
}

int dom_save_edit_get_value(dom_save_edit_ctx *ctx,
                            const char *section,
                            const char *key,
                            char *buf,
                            uint32_t buf_size)
{
    int i;
    if (!ctx || !section || !key || !buf || buf_size == 0) return -1;
    for (i = 0; i < ctx->entry_count; ++i) {
        dom_save_entry *e = &ctx->entries[i];
        if (strcmp(e->section, section) == 0 && strcmp(e->key, key) == 0) {
            strncpy(buf, e->value, buf_size - 1);
            buf[buf_size - 1] = '\0';
            return 0;
        }
    }
    return -1;
}

int dom_save_edit_set_value(dom_save_edit_ctx *ctx,
                            const char *section,
                            const char *key,
                            const char *value)
{
    int i;
    if (!ctx || !section || !key || !value) return -1;
    for (i = 0; i < ctx->entry_count; ++i) {
        dom_save_entry *e = &ctx->entries[i];
        if (strcmp(e->section, section) == 0 && strcmp(e->key, key) == 0) {
            strncpy(e->value, value, sizeof(e->value) - 1);
            e->value[sizeof(e->value) - 1] = '\0';
            ctx->dirty = 1;
            return 0;
        }
    }
    if (ctx->entry_count >= DOM_SAVE_MAX_ENTRIES) return -1;
    i = ctx->entry_count++;
    memset(&ctx->entries[i], 0, sizeof(ctx->entries[i]));
    strncpy(ctx->entries[i].section, section, sizeof(ctx->entries[i].section) - 1);
    strncpy(ctx->entries[i].key, key, sizeof(ctx->entries[i].key) - 1);
    strncpy(ctx->entries[i].value, value, sizeof(ctx->entries[i].value) - 1);
    ctx->dirty = 1;
    return 0;
}

int dom_save_edit_save(dom_save_edit_ctx *ctx)
{
    void *f;
    int i;
    char line[512];
    if (!ctx) return -1;

    f = dsys_file_open(ctx->path, "wb");
    if (!f) return -1;

    for (i = 0; i < ctx->entry_count; ++i) {
        dom_save_entry *e = &ctx->entries[i];
        sprintf(line, "%s.%s=%s\n", e->section, e->key, e->value);
        dsys_file_write(f, line, strlen(line));
    }
    dsys_file_close(f);
    ctx->dirty = 0;
    return 0;
}
