#ifndef DOMINIUM_CLIENT_SESSION_PIPELINE_H
#define DOMINIUM_CLIENT_SESSION_PIPELINE_H

#include "session_stage_registry.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct client_session_pipeline_t {
    client_session_stage_id stage_id;
    char last_refusal[96];
    u32 transition_count;
    u32 epoch;
} client_session_pipeline;

void client_session_pipeline_init(client_session_pipeline* pipeline);
int client_session_pipeline_apply_command(client_session_pipeline* pipeline, const char* command_id);
const char* client_session_pipeline_stage_name(const client_session_pipeline* pipeline);
const char* client_session_pipeline_last_refusal(const client_session_pipeline* pipeline);

#ifdef __cplusplus
}
#endif

#endif
