#include "session_stage_registry.h"

static const char* k_caps_none[] = { 0 };
static const char* k_caps_resolve[] = { "session.resolve" };
static const char* k_caps_acquire[] = { "session.world.acquire" };
static const char* k_caps_verify[] = { "session.world.verify" };
static const char* k_caps_warmup_sim[] = { "session.warmup.simulation" };
static const char* k_caps_warmup_presentation[] = { "session.warmup.presentation" };
static const char* k_caps_ready[] = { "session.ready" };
static const char* k_caps_running[] = { "session.run" };
static const char* k_caps_suspend[] = { "session.suspend" };
static const char* k_caps_resume[] = { "session.resume" };
static const char* k_caps_teardown[] = { "session.teardown" };

static const client_session_stage_id k_next_resolve[] = {
    CLIENT_SESSION_STAGE_ACQUIRE_WORLD,
    CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION
};
static const client_session_stage_id k_next_acquire[] = {
    CLIENT_SESSION_STAGE_VERIFY_WORLD,
    CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION
};
static const client_session_stage_id k_next_verify[] = {
    CLIENT_SESSION_STAGE_WARMUP_SIMULATION,
    CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION
};
static const client_session_stage_id k_next_warmup_simulation[] = {
    CLIENT_SESSION_STAGE_WARMUP_PRESENTATION,
    CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION
};
static const client_session_stage_id k_next_warmup_presentation[] = {
    CLIENT_SESSION_STAGE_SESSION_READY,
    CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION
};
static const client_session_stage_id k_next_ready[] = {
    CLIENT_SESSION_STAGE_SESSION_RUNNING,
    CLIENT_SESSION_STAGE_SUSPEND_SESSION,
    CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION
};
static const client_session_stage_id k_next_running[] = {
    CLIENT_SESSION_STAGE_SUSPEND_SESSION,
    CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION
};
static const client_session_stage_id k_next_suspend[] = {
    CLIENT_SESSION_STAGE_RESUME_SESSION,
    CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION
};
static const client_session_stage_id k_next_resume[] = {
    CLIENT_SESSION_STAGE_RESOLVE_SESSION,
    CLIENT_SESSION_STAGE_SESSION_READY,
    CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION
};
static const client_session_stage_id k_next_teardown[] = { 0 };

static const client_session_stage_desc k_stages[] = {
    { CLIENT_SESSION_STAGE_RESOLVE_SESSION, "stage.resolve_session", k_caps_resolve, 1u,
      k_next_resolve, 2u, 1, 0, 1, 0 },
    { CLIENT_SESSION_STAGE_ACQUIRE_WORLD, "stage.acquire_world", k_caps_acquire, 1u,
      k_next_acquire, 2u, 1, 0, 1, 0 },
    { CLIENT_SESSION_STAGE_VERIFY_WORLD, "stage.verify_world", k_caps_verify, 1u,
      k_next_verify, 2u, 1, 0, 1, 0 },
    { CLIENT_SESSION_STAGE_WARMUP_SIMULATION, "stage.warmup_simulation", k_caps_warmup_sim, 1u,
      k_next_warmup_simulation, 2u, 1, 0, 1, 0 },
    { CLIENT_SESSION_STAGE_WARMUP_PRESENTATION, "stage.warmup_presentation", k_caps_warmup_presentation, 1u,
      k_next_warmup_presentation, 2u, 1, 0, 1, 0 },
    { CLIENT_SESSION_STAGE_SESSION_READY, "stage.session_ready", k_caps_ready, 1u,
      k_next_ready, 3u, 1, 1, 1, 0 },
    { CLIENT_SESSION_STAGE_SESSION_RUNNING, "stage.session_running", k_caps_running, 1u,
      k_next_running, 2u, 1, 0, 1, 0 },
    { CLIENT_SESSION_STAGE_SUSPEND_SESSION, "stage.suspend_session", k_caps_suspend, 1u,
      k_next_suspend, 2u, 1, 1, 1, 0 },
    { CLIENT_SESSION_STAGE_RESUME_SESSION, "stage.resume_session", k_caps_resume, 1u,
      k_next_resume, 3u, 1, 1, 1, 0 },
    { CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION, "stage.teardown_session", k_caps_teardown, 1u,
      k_next_teardown, 0u, 0, 0, 1, 0 }
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
        return "stage.teardown_session";
    }
    return stage->stage_name;
}

int client_session_stage_transition_allowed(client_session_stage_id from_stage_id,
                                            client_session_stage_id to_stage_id)
{
    const client_session_stage_desc* stage = client_session_stage_find(from_stage_id);
    u32 i = 0u;
    if (!stage) {
        return 0;
    }
    for (i = 0u; i < stage->allowed_next_stage_count; ++i) {
        if (stage->allowed_next_stage_ids[i] == to_stage_id) {
            return 1;
        }
    }
    return 0;
}

int client_session_stage_abort_allowed(client_session_stage_id stage_id)
{
    const client_session_stage_desc* stage = client_session_stage_find(stage_id);
    if (!stage) {
        return 0;
    }
    return stage->abort_allowed ? 1 : 0;
}

int client_session_stage_resume_allowed(client_session_stage_id stage_id)
{
    const client_session_stage_desc* stage = client_session_stage_find(stage_id);
    if (!stage) {
        return 0;
    }
    return stage->resume_allowed ? 1 : 0;
}

int client_session_stage_deterministic(client_session_stage_id stage_id)
{
    const client_session_stage_desc* stage = client_session_stage_find(stage_id);
    if (!stage) {
        return 0;
    }
    return stage->deterministic ? 1 : 0;
}

client_session_stage_id client_session_stage_from_name(const char* stage_name)
{
    u32 count = 0u;
    u32 i = 0u;
    const client_session_stage_desc* stages = client_session_stage_registry(&count);
    if (!stage_name || !stage_name[0]) {
        return CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION;
    }
    for (i = 0u; i < count; ++i) {
        if (strcmp(stages[i].stage_name, stage_name) == 0) {
            return stages[i].stage_id;
        }
    }
    return CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION;
}
