#include "domino/mod.h"
#include <stdlib.h>

dm_mod_context* dm_mod_create(void)
{
    dm_mod_context* ctx = (dm_mod_context*)malloc(sizeof(dm_mod_context));
    if (!ctx) return NULL;
    ctx->placeholder = 0;
    return ctx;
}

void dm_mod_destroy(dm_mod_context* ctx)
{
    if (ctx) free(ctx);
}
