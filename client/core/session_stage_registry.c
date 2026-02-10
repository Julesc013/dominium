#include "session_stage_registry.h"

static const char* k_caps_none[] = { 0 };
static const char* k_caps_world_access[] = { "world.snapshot.read" };
static const char* k_caps_renderer[] = { "runtime.renderer" };
static const char* k_caps_authority[] = { "session.authority.connect" };

static const client_session_stage_desc k_stages[] = {
    { CLIENT_SESSION_STAGE_RESOLVE_SESSION, "ResolveSession", k_caps_none, 0u },
    { CLIENT_SESSION_STAGE_ACQUIRE_WORLD, "AcquireWorld", k_caps_world_access, 1u },
    { CLIENT_SESSION_STAGE_VERIFY_WORLD, "VerifyWorld", k_caps_none, 0u },
    { CLIENT_SESSION_STAGE_WARMUP_SIMULATION, "WarmupSimulation", k_caps_none, 0u },
    { CLIENT_SESSION_STAGE_WARMUP_PRESENTATION, "WarmupPresentation", k_caps_renderer, 1u },
    { CLIENT_SESSION_STAGE_SESSION_READY, "SessionReady", k_caps_none, 0u },
    { CLIENT_SESSION_STAGE_SESSION_RUNNING, "SessionRunning", k_caps_authority, 1u },
    { CLIENT_SESSION_STAGE_SUSPEND_SESSION, "SuspendSession", k_caps_none, 0u },
    { CLIENT_SESSION_STAGE_RESUME_SESSION, "ResumeSession", k_caps_none, 0u },
    { CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION, "TearDownSession", k_caps_none, 0u }
};

const client_session_stage_desc* client_session_stage_registry(u32* out_count)
{
    if (out_count) {
        *out_count = (u32)(sizeof(k_stages) / sizeof(k_stages[0]));
    }
    return k_stages;
}

const client_session_stage_desc* client_session_stage_find(client_session_stage_id stage_id)
{
    u32 count = 0u;
    u32 i = 0u;
    const client_session_stage_desc* stages = client_session_stage_registry(&count);
    for (i = 0u; i < count; ++i) {
        if (stages[i].stage_id == stage_id) {
            return &stages[i];
        }
    }
    return 0;
}

const char* client_session_stage_name(client_session_stage_id stage_id)
{
    const client_session_stage_desc* stage = client_session_stage_find(stage_id);
    if (!stage) {
        return "TearDownSession";
    }
    return stage->stage_name;
}
