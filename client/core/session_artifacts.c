#include "session_artifacts.h"

#include "session_refusal_codes.h"

#include <string.h>

static void copy_text(char* out, size_t cap, const char* text)
{
    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (!text || !text[0]) {
        return;
    }
    strncpy(out, text, cap - 1u);
    out[cap - 1u] = '\0';
}

void client_session_artifacts_init(client_session_artifacts* artifacts)
{
    if (!artifacts) {
        return;
    }
    memset(artifacts, 0, sizeof(*artifacts));
    artifacts->mode = CLIENT_WORLD_ACQUIRE_NONE;
}

static void acquire_common(client_session_artifacts* artifacts,
                           client_world_acquire_mode mode,
                           const char* source_id,
                           const char* world_hash)
{
    if (!artifacts) {
        return;
    }
    artifacts->mode = mode;
    artifacts->verified = 0;
    copy_text(artifacts->source_id, sizeof(artifacts->source_id), source_id);
    copy_text(artifacts->world_hash, sizeof(artifacts->world_hash), world_hash);
    artifacts->expected_hash[0] = '\0';
}

void client_session_artifacts_acquire_local(client_session_artifacts* artifacts,
                                            const char* snapshot_id,
                                            const char* world_hash)
{
    acquire_common(artifacts, CLIENT_WORLD_ACQUIRE_LOCAL_SNAPSHOT, snapshot_id, world_hash);
}

void client_session_artifacts_acquire_spec(client_session_artifacts* artifacts,
                                           const char* world_spec_id,
                                           const char* world_hash)
{
    acquire_common(artifacts, CLIENT_WORLD_ACQUIRE_WORLD_SPEC, world_spec_id, world_hash);
}

void client_session_artifacts_acquire_server(client_session_artifacts* artifacts,
                                             const char* server_id,
                                             const char* world_hash)
{
    acquire_common(artifacts, CLIENT_WORLD_ACQUIRE_SERVER_FETCH, server_id, world_hash);
}

void client_session_artifacts_acquire_macro(client_session_artifacts* artifacts,
                                            const char* capsule_id,
                                            const char* world_hash)
{
    acquire_common(artifacts, CLIENT_WORLD_ACQUIRE_MACRO_RECONSTRUCT, capsule_id, world_hash);
}

int client_session_artifacts_verify_hash(client_session_artifacts* artifacts,
                                         const char* expected_hash,
                                         char* out_refusal,
                                         size_t out_refusal_cap)
{
    if (!artifacts || !expected_hash || !expected_hash[0]) {
        copy_text(out_refusal, out_refusal_cap, CLIENT_SESSION_REFUSE_SCHEMA_INCOMPATIBLE);
        return 0;
    }
    copy_text(artifacts->expected_hash, sizeof(artifacts->expected_hash), expected_hash);
    if (!artifacts->world_hash[0] || strcmp(artifacts->world_hash, expected_hash) != 0) {
        artifacts->verified = 0;
        copy_text(out_refusal, out_refusal_cap, CLIENT_SESSION_REFUSE_WORLD_HASH_MISMATCH);
        return 0;
    }
    artifacts->verified = 1;
    copy_text(out_refusal, out_refusal_cap, "");
    return 1;
}

int client_session_artifacts_layer_allowed(const char* layer_id)
{
    if (!layer_id || !layer_id[0]) {
        return 0;
    }
    if (strcmp(layer_id, "terrain.height") == 0) return 1;
    if (strcmp(layer_id, "hydrology.flow") == 0) return 1;
    if (strcmp(layer_id, "fogged.visibility") == 0) return 1;
    if (strcmp(layer_id, "truth.full") == 0) return 0;
    return 0;
}

const char* client_session_artifacts_mode_name(client_world_acquire_mode mode)
{
    if (mode == CLIENT_WORLD_ACQUIRE_LOCAL_SNAPSHOT) return "LocalWorldSnapshot";
    if (mode == CLIENT_WORLD_ACQUIRE_WORLD_SPEC) return "GenerateFromWorldSpec";
    if (mode == CLIENT_WORLD_ACQUIRE_SERVER_FETCH) return "FetchFromServer";
    if (mode == CLIENT_WORLD_ACQUIRE_MACRO_RECONSTRUCT) return "ReconstructFromMacroCapsules";
    return "Unspecified";
}
