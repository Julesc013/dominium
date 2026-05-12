#ifndef DOMINIUM_CLIENT_MODELS_SERVER_H
#define DOMINIUM_CLIENT_MODELS_SERVER_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define CLIENT_SERVER_MODEL_MAX_RECORDS 256u

typedef struct client_server_record_t {
    char provider[32];
    char server_id[96];
    char address[128];
    char protocol_version[32];
    char capability_hash[80];
    char refusal_reason[64];
} client_server_record;

typedef struct client_server_model_t {
    client_server_record records[CLIENT_SERVER_MODEL_MAX_RECORDS];
    u32 count;
} client_server_model;

void client_server_model_init(client_server_model* model);
int client_server_model_merge(client_server_model* model, const client_server_record* incoming, u32 incoming_count);
const client_server_record* client_server_model_at(const client_server_model* model, u32 index);
u32 client_server_model_count(const client_server_model* model);
u64 client_server_model_digest(const client_server_model* model);

#ifdef __cplusplus
}
#endif

#endif
