#include "client_models_options.h"

#include <string.h>

static void copy_text(char* out, size_t cap, const char* value)
{
    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (!value || !value[0]) {
        return;
    }
    strncpy(out, value, cap - 1u);
    out[cap - 1u] = '\0';
}

void client_options_model_init(client_options_model* model)
{
    if (!model) {
        return;
    }
    memset(model, 0, sizeof(*model));
    copy_text(model->renderer, sizeof(model->renderer), "auto");
    copy_text(model->mode, sizeof(model->mode), "cli");
    model->font_scale_percent = 100u;
    model->high_contrast_enabled = 0u;
    model->network_timeout_ms = 5000u;
}

int client_options_model_set_renderer(client_options_model* model, const char* renderer)
{
    if (!model || !renderer || !renderer[0]) {
        return 0;
    }
    copy_text(model->renderer, sizeof(model->renderer), renderer);
    return 1;
}

int client_options_model_set_mode(client_options_model* model, const char* mode)
{
    if (!model || !mode || !mode[0]) {
        return 0;
    }
    if (strcmp(mode, "cli") != 0 &&
        strcmp(mode, "tui") != 0 &&
        strcmp(mode, "gui") != 0) {
        return 0;
    }
    copy_text(model->mode, sizeof(model->mode), mode);
    return 1;
}

int client_options_model_set_font_scale(client_options_model* model, u32 font_scale_percent)
{
    if (!model) {
        return 0;
    }
    if (font_scale_percent < 50u || font_scale_percent > 200u) {
        return 0;
    }
    model->font_scale_percent = font_scale_percent;
    return 1;
}

int client_options_model_set_network_timeout(client_options_model* model, u32 timeout_ms)
{
    if (!model) {
        return 0;
    }
    if (timeout_ms < 100u || timeout_ms > 120000u) {
        return 0;
    }
    model->network_timeout_ms = timeout_ms;
    return 1;
}

u64 client_options_model_digest(const client_options_model* model)
{
    const u64 fnv_offset = 1469598103934665603ull;
    const u64 fnv_prime = 1099511628211ull;
    u64 hash = fnv_offset;
    const unsigned char* p = 0;
    if (!model) {
        return 0ull;
    }
    p = (const unsigned char*)model->renderer;
    while (p && *p) {
        hash ^= (u64)(*p++);
        hash *= fnv_prime;
    }
    p = (const unsigned char*)model->mode;
    while (p && *p) {
        hash ^= (u64)(*p++);
        hash *= fnv_prime;
    }
    hash ^= (u64)model->font_scale_percent;
    hash *= fnv_prime;
    hash ^= (u64)model->high_contrast_enabled;
    hash *= fnv_prime;
    hash ^= (u64)model->network_timeout_ms;
    hash *= fnv_prime;
    return hash;
}
