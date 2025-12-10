#include <stdlib.h>
#include <string.h>
#include "dominium/game_edit_api.h"
#include "domino/sys.h"

#define DOM_GAME_MAX_ENTRIES 128

typedef struct dom_game_entry_t {
    char kind[32];
    char id[64];
    char json[512];
} dom_game_entry;

typedef struct dom_game_edit_ctx_t {
    char root[260];
    dom_game_entry entries[DOM_GAME_MAX_ENTRIES];
    int entry_count;
    int dirty;
} dom_game_edit_ctx;

static void dom_game_edit_seed(dom_game_edit_ctx *ctx)
{
    if (!ctx) return;
    if (ctx->entry_count > 0) return;
    strncpy(ctx->entries[0].kind, "item", sizeof(ctx->entries[0].kind) - 1);
    strncpy(ctx->entries[0].id, "sample_item", sizeof(ctx->entries[0].id) - 1);
    strncpy(ctx->entries[0].json, "{ \"id\": \"sample_item\", \"name\": \"Sample Item\" }", sizeof(ctx->entries[0].json) - 1);
    strncpy(ctx->entries[1].kind, "recipe", sizeof(ctx->entries[1].kind) - 1);
    strncpy(ctx->entries[1].id, "sample_recipe", sizeof(ctx->entries[1].id) - 1);
    strncpy(ctx->entries[1].json, "{ \"id\": \"sample_recipe\", \"inputs\": [], \"outputs\": [] }", sizeof(ctx->entries[1].json) - 1);
    ctx->entry_count = 2;
}

dom_game_edit_ctx *dom_game_edit_open(const dom_game_edit_desc *desc)
{
    dom_game_edit_ctx *ctx;
    const char *root = "data/defs";
    if (desc && desc->def_root) {
        root = desc->def_root;
    }
    ctx = (dom_game_edit_ctx*)malloc(sizeof(dom_game_edit_ctx));
    if (!ctx) return NULL;
    memset(ctx, 0, sizeof(*ctx));
    strncpy(ctx->root, root, sizeof(ctx->root) - 1);
    ctx->root[sizeof(ctx->root) - 1] = '\0';
    dom_game_edit_seed(ctx);
    return ctx;
}

void dom_game_edit_close(dom_game_edit_ctx *ctx)
{
    if (!ctx) return;
    free(ctx);
}

int dom_game_edit_list_entities(dom_game_edit_ctx *ctx,
                                const char *kind,
                                char *buf,
                                uint32_t buf_size)
{
    uint32_t written = 0;
    int i;
    if (!ctx || !buf || buf_size == 0) return -1;
    for (i = 0; i < ctx->entry_count; ++i) {
        dom_game_entry *e = &ctx->entries[i];
        size_t len;
        if (kind && strcmp(kind, e->kind) != 0) continue;
        len = strlen(e->id);
        if (written + len + 1 >= buf_size) break;
        memcpy(buf + written, e->id, len);
        written += (uint32_t)len;
        buf[written++] = '\n';
    }
    if (written < buf_size) buf[written] = '\0';
    return (int)written;
}

int dom_game_edit_get_entity_json(dom_game_edit_ctx *ctx,
                                  const char *kind,
                                  const char *id,
                                  char *buf,
                                  uint32_t buf_size)
{
    int i;
    if (!ctx || !kind || !id || !buf || buf_size == 0) return -1;
    for (i = 0; i < ctx->entry_count; ++i) {
        dom_game_entry *e = &ctx->entries[i];
        if (strcmp(e->kind, kind) == 0 && strcmp(e->id, id) == 0) {
            strncpy(buf, e->json, buf_size - 1);
            buf[buf_size - 1] = '\0';
            return 0;
        }
    }
    return -1;
}

int dom_game_edit_set_entity_json(dom_game_edit_ctx *ctx,
                                  const char *kind,
                                  const char *id,
                                  const char *json)
{
    int i;
    if (!ctx || !kind || !id || !json) return -1;
    for (i = 0; i < ctx->entry_count; ++i) {
        dom_game_entry *e = &ctx->entries[i];
        if (strcmp(e->kind, kind) == 0 && strcmp(e->id, id) == 0) {
            strncpy(e->json, json, sizeof(e->json) - 1);
            e->json[sizeof(e->json) - 1] = '\0';
            ctx->dirty = 1;
            return 0;
        }
    }
    if (ctx->entry_count >= DOM_GAME_MAX_ENTRIES) return -1;
    i = ctx->entry_count++;
    memset(&ctx->entries[i], 0, sizeof(ctx->entries[i]));
    strncpy(ctx->entries[i].kind, kind, sizeof(ctx->entries[i].kind) - 1);
    strncpy(ctx->entries[i].id, id, sizeof(ctx->entries[i].id) - 1);
    strncpy(ctx->entries[i].json, json, sizeof(ctx->entries[i].json) - 1);
    ctx->dirty = 1;
    return 0;
}

int dom_game_edit_save(dom_game_edit_ctx *ctx)
{
    void *f;
    int i;
    char path[320];
    char line[640];
    if (!ctx) return -1;

    strncpy(path, ctx->root, sizeof(path) - 1);
    path[sizeof(path) - 1] = '\0';
    if (strlen(path) + 15 < sizeof(path)) {
        strcat(path, "/game_defs.txt");
    }

    f = dsys_file_open(path, "wb");
    if (!f) return -1;

    for (i = 0; i < ctx->entry_count; ++i) {
        dom_game_entry *e = &ctx->entries[i];
        sprintf(line, "%s:%s=%s\n", e->kind, e->id, e->json);
        dsys_file_write(f, line, strlen(line));
    }
    dsys_file_close(f);
    ctx->dirty = 0;
    return 0;
}
