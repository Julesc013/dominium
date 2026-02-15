#ifndef DOMINIUM_CLIENT_SESSION_PIPELINE_H
#define DOMINIUM_CLIENT_SESSION_PIPELINE_H

#include "session_artifacts.h"
#include "session_stage_registry.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct client_session_stage_log_entry_t {
    char command_id[64];
    char from_stage[48];
    char to_stage[48];
    char status[16];
    char refusal_code[96];
} client_session_stage_log_entry;

typedef struct client_session_pipeline_t {
    client_session_stage_id stage_id;
    char last_refusal[96];
    client_session_stage_id last_stage_before_abort;
    int resume_snapshot_available;
    client_session_stage_log_entry stage_log[64];
    u32 stage_log_count;
    u32 transition_count;
    u32 epoch;
} client_session_pipeline;

void client_session_pipeline_init(client_session_pipeline* pipeline);
int client_session_pipeline_apply_command(client_session_pipeline* pipeline,
                                          const char* command_id,
                                          const client_session_artifacts* artifacts);
const char* client_session_pipeline_stage_name(const client_session_pipeline* pipeline);
const char* client_session_pipeline_last_refusal(const client_session_pipeline* pipeline);
u32 client_session_pipeline_stage_log_count(const client_session_pipeline* pipeline);
const client_session_stage_log_entry* client_session_pipeline_stage_log_at(const client_session_pipeline* pipeline,
                                                                           u32 index);

#ifdef __cplusplus
}
#endif

#endif
