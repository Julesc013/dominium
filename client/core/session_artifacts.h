#ifndef DOMINIUM_CLIENT_SESSION_ARTIFACTS_H
#define DOMINIUM_CLIENT_SESSION_ARTIFACTS_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum client_world_acquire_mode_e {
    CLIENT_WORLD_ACQUIRE_NONE = 0,
    CLIENT_WORLD_ACQUIRE_LOCAL_SNAPSHOT = 1,
    CLIENT_WORLD_ACQUIRE_WORLD_SPEC = 2,
    CLIENT_WORLD_ACQUIRE_SERVER_FETCH = 3,
    CLIENT_WORLD_ACQUIRE_MACRO_RECONSTRUCT = 4
} client_world_acquire_mode;

typedef struct client_session_artifacts_t {
    client_world_acquire_mode mode;
    char source_id[96];
    char world_hash[96];
    char expected_hash[96];
    char warmup_simulation_step[96];
    char warmup_presentation_step[96];
    int verified;
    int warmup_simulation_ready;
    int warmup_presentation_ready;
    int simulation_time_advanced;
} client_session_artifacts;

void client_session_artifacts_init(client_session_artifacts* artifacts);
void client_session_artifacts_acquire_local(client_session_artifacts* artifacts,
                                            const char* snapshot_id,
                                            const char* world_hash);
void client_session_artifacts_acquire_spec(client_session_artifacts* artifacts,
                                           const char* world_spec_id,
                                           const char* world_hash);
void client_session_artifacts_acquire_server(client_session_artifacts* artifacts,
                                             const char* server_id,
                                             const char* world_hash);
void client_session_artifacts_acquire_macro(client_session_artifacts* artifacts,
                                            const char* capsule_id,
                                            const char* world_hash);
int client_session_artifacts_verify_hash(client_session_artifacts* artifacts,
                                         const char* expected_hash,
                                         char* out_refusal,
                                         size_t out_refusal_cap);
void client_session_artifacts_warmup_simulation(client_session_artifacts* artifacts);
void client_session_artifacts_warmup_presentation(client_session_artifacts* artifacts);
int client_session_artifacts_layer_allowed(const char* layer_id);
const char* client_session_artifacts_mode_name(client_world_acquire_mode mode);
const char* client_session_artifacts_warmup_simulation_step(const client_session_artifacts* artifacts);
const char* client_session_artifacts_warmup_presentation_step(const client_session_artifacts* artifacts);
int client_session_artifacts_simulation_time_advanced(const client_session_artifacts* artifacts);

#ifdef __cplusplus
}
#endif

#endif
