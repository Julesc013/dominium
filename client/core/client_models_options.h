#ifndef DOMINIUM_CLIENT_MODELS_OPTIONS_H
#define DOMINIUM_CLIENT_MODELS_OPTIONS_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct client_options_model_t {
    char renderer[32];
    char mode[16];
    u32 font_scale_percent;
    u32 high_contrast_enabled;
    u32 network_timeout_ms;
} client_options_model;

void client_options_model_init(client_options_model* model);
int client_options_model_set_renderer(client_options_model* model, const char* renderer);
int client_options_model_set_mode(client_options_model* model, const char* mode);
int client_options_model_set_font_scale(client_options_model* model, u32 font_scale_percent);
int client_options_model_set_network_timeout(client_options_model* model, u32 timeout_ms);
u64 client_options_model_digest(const client_options_model* model);

#ifdef __cplusplus
}
#endif

#endif
