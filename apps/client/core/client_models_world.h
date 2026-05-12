#ifndef DOMINIUM_CLIENT_MODELS_WORLD_H
#define DOMINIUM_CLIENT_MODELS_WORLD_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define CLIENT_WORLD_MODEL_MAX_RECORDS 128u

typedef struct client_world_record_t {
    char world_id[64];
    char metadata_path[192];
    char pack_set_hash[80];
    char schema_versions[128];
    char last_build_identity[64];
} client_world_record;

typedef struct client_world_model_t {
    client_world_record records[CLIENT_WORLD_MODEL_MAX_RECORDS];
    u32 count;
} client_world_model;

void client_world_model_init(client_world_model* model);
int client_world_model_add_or_replace(client_world_model* model, const client_world_record* record);
int client_world_model_remove(client_world_model* model, const char* world_id);
const client_world_record* client_world_model_at(const client_world_model* model, u32 index);
u32 client_world_model_count(const client_world_model* model);
u64 client_world_model_digest(const client_world_model* model);

#ifdef __cplusplus
}
#endif

#endif
