#ifndef DOMINIUM_CLIENT_SESSION_STAGE_REGISTRY_H
#define DOMINIUM_CLIENT_SESSION_STAGE_REGISTRY_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum client_session_stage_id_e {
    CLIENT_SESSION_STAGE_RESOLVE_SESSION = 0,
    CLIENT_SESSION_STAGE_ACQUIRE_WORLD = 1,
    CLIENT_SESSION_STAGE_VERIFY_WORLD = 2,
    CLIENT_SESSION_STAGE_WARMUP_SIMULATION = 3,
    CLIENT_SESSION_STAGE_WARMUP_PRESENTATION = 4,
    CLIENT_SESSION_STAGE_SESSION_READY = 5,
    CLIENT_SESSION_STAGE_SESSION_RUNNING = 6,
    CLIENT_SESSION_STAGE_SUSPEND_SESSION = 7,
    CLIENT_SESSION_STAGE_RESUME_SESSION = 8,
    CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION = 9
} client_session_stage_id;

typedef struct client_session_stage_desc_t {
    client_session_stage_id stage_id;
    const char* stage_name;
    const char* const* required_capabilities;
    u32 required_capability_count;
    const client_session_stage_id* allowed_next_stage_ids;
    u32 allowed_next_stage_count;
    int abort_allowed;
    int resume_allowed;
    int deterministic;
    int run_meta_only;
} client_session_stage_desc;

const client_session_stage_desc* client_session_stage_registry(u32* out_count);
const client_session_stage_desc* client_session_stage_find(client_session_stage_id stage_id);
const char* client_session_stage_name(client_session_stage_id stage_id);
int client_session_stage_transition_allowed(client_session_stage_id from_stage_id,
                                            client_session_stage_id to_stage_id);
int client_session_stage_abort_allowed(client_session_stage_id stage_id);
int client_session_stage_resume_allowed(client_session_stage_id stage_id);
int client_session_stage_deterministic(client_session_stage_id stage_id);
client_session_stage_id client_session_stage_from_name(const char* stage_name);

#ifdef __cplusplus
}
#endif

#endif
