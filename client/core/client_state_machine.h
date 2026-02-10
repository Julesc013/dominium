#ifndef DOMINIUM_CLIENT_STATE_MACHINE_H
#define DOMINIUM_CLIENT_STATE_MACHINE_H

#include "domino/core/types.h"
#include "session_pipeline.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum client_session_state_e {
    CLIENT_SESSION_STATE_BOOT_PROGRESS = 0,
    CLIENT_SESSION_STATE_MAIN_MENU = 1,
    CLIENT_SESSION_STATE_SINGLEPLAYER_WORLD_MANAGER = 2,
    CLIENT_SESSION_STATE_MULTIPLAYER_SERVER_BROWSER = 3,
    CLIENT_SESSION_STATE_OPTIONS = 4,
    CLIENT_SESSION_STATE_ABOUT = 5,
    CLIENT_SESSION_STATE_SESSION_LAUNCHING = 6,
    CLIENT_SESSION_STATE_SESSION_READY = 7,
    CLIENT_SESSION_STATE_SESSION_RUNNING = 8,
    CLIENT_SESSION_STATE_REFUSAL_ERROR = 9
} client_session_state;

typedef struct client_state_machine_t {
    client_session_state state;
    client_session_pipeline pipeline;
    char last_command[96];
    char last_refusal[96];
    u32 transition_count;
} client_state_machine;

void client_state_machine_init(client_state_machine* machine);
int client_state_machine_apply(client_state_machine* machine, const char* command_id);
const char* client_state_machine_state_name(client_session_state state);
const char* client_state_machine_last_command(const client_state_machine* machine);
const char* client_state_machine_last_refusal(const client_state_machine* machine);
const char* client_state_machine_stage_name(const client_state_machine* machine);

#ifdef __cplusplus
}
#endif

#endif
