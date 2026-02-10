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

static int as_flag(int value)
{
    return value ? 1 : 0;
}

void client_session_artifacts_init(client_session_artifacts* artifacts)
{
    if (!artifacts) {
        return;
    }
    memset(artifacts, 0, sizeof(*artifacts));
    artifacts->mode = CLIENT_WORLD_ACQUIRE_NONE;
    artifacts->simulation_time_advanced = 0;
    artifacts->world_ready = 0;
    artifacts->camera_placed = 0;
    artifacts->agent_actions_executed = 0;
    artifacts->map_open = 0;
    artifacts->stats_visible = 0;
    artifacts->replay_recording_enabled = 0;
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
    artifacts->warmup_simulation_ready = 0;
    artifacts->warmup_presentation_ready = 0;
    artifacts->simulation_time_advanced = 0;
    artifacts->world_ready = 0;
    artifacts->camera_placed = 0;
    artifacts->agent_actions_executed = 0;
    artifacts->map_open = 0;
    artifacts->stats_visible = 0;
    artifacts->replay_recording_enabled = 0;
    copy_text(artifacts->source_id, sizeof(artifacts->source_id), source_id);
    copy_text(artifacts->world_hash, sizeof(artifacts->world_hash), world_hash);
    artifacts->expected_hash[0] = '\0';
    artifacts->warmup_simulation_step[0] = '\0';
    artifacts->warmup_presentation_step[0] = '\0';
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

void client_session_artifacts_warmup_simulation(client_session_artifacts* artifacts)
{
    if (!artifacts) {
        return;
    }
    copy_text(artifacts->warmup_simulation_step,
              sizeof(artifacts->warmup_simulation_step),
              "rng_streams_initialized>macro_capsules_seeded>fields_initialized>agent_shells_initialized>authority_policies_bound");
    artifacts->warmup_simulation_ready = 1;
    artifacts->simulation_time_advanced = 0;
}

void client_session_artifacts_warmup_presentation(client_session_artifacts* artifacts)
{
    if (!artifacts) {
        return;
    }
    copy_text(artifacts->warmup_presentation_step,
              sizeof(artifacts->warmup_presentation_step),
              "layout_loaded>renderer_backend_loaded>input_mappings_loaded>camera_defaults_prepared");
    artifacts->warmup_presentation_ready = 1;
}

void client_session_artifacts_mark_session_ready(client_session_artifacts* artifacts)
{
    if (!artifacts) {
        return;
    }
    artifacts->world_ready = 1;
    artifacts->camera_placed = 1;
    artifacts->agent_actions_executed = 0;
    artifacts->simulation_time_advanced = 0;
}

void client_session_artifacts_set_map_open(client_session_artifacts* artifacts, int enabled)
{
    if (!artifacts) {
        return;
    }
    artifacts->map_open = as_flag(enabled);
}

void client_session_artifacts_set_stats_visible(client_session_artifacts* artifacts, int enabled)
{
    if (!artifacts) {
        return;
    }
    artifacts->stats_visible = as_flag(enabled);
}

void client_session_artifacts_set_replay_recording(client_session_artifacts* artifacts, int enabled)
{
    if (!artifacts) {
        return;
    }
    artifacts->replay_recording_enabled = as_flag(enabled);
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

const char* client_session_artifacts_warmup_simulation_step(const client_session_artifacts* artifacts)
{
    if (!artifacts || !artifacts->warmup_simulation_step[0]) {
        return "";
    }
    return artifacts->warmup_simulation_step;
}

const char* client_session_artifacts_warmup_presentation_step(const client_session_artifacts* artifacts)
{
    if (!artifacts || !artifacts->warmup_presentation_step[0]) {
        return "";
    }
    return artifacts->warmup_presentation_step;
}

int client_session_artifacts_simulation_time_advanced(const client_session_artifacts* artifacts)
{
    if (!artifacts) {
        return 0;
    }
    return artifacts->simulation_time_advanced;
}

int client_session_artifacts_world_ready(const client_session_artifacts* artifacts)
{
    if (!artifacts) {
        return 0;
    }
    return artifacts->world_ready;
}

int client_session_artifacts_camera_placed(const client_session_artifacts* artifacts)
{
    if (!artifacts) {
        return 0;
    }
    return artifacts->camera_placed;
}

int client_session_artifacts_agent_actions_executed(const client_session_artifacts* artifacts)
{
    if (!artifacts) {
        return 0;
    }
    return artifacts->agent_actions_executed;
}

int client_session_artifacts_map_open(const client_session_artifacts* artifacts)
{
    if (!artifacts) {
        return 0;
    }
    return artifacts->map_open;
}

int client_session_artifacts_stats_visible(const client_session_artifacts* artifacts)
{
    if (!artifacts) {
        return 0;
    }
    return artifacts->stats_visible;
}

int client_session_artifacts_replay_recording_enabled(const client_session_artifacts* artifacts)
{
    if (!artifacts) {
        return 0;
    }
    return artifacts->replay_recording_enabled;
}
