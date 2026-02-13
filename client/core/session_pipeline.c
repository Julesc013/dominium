#include "session_pipeline.h"

#include "session_refusal_codes.h"

#include <string.h>

static int starts_with(const char* value, const char* prefix)
{
    size_t n = 0u;
    if (!value || !prefix) {
        return 0;
    }
    n = strlen(prefix);
    return strncmp(value, prefix, n) == 0 ? 1 : 0;
}

static void set_refusal(client_session_pipeline* pipeline, const char* refusal_code)
{
    if (!pipeline) {
        return;
    }
    pipeline->last_refusal[0] = '\0';
    if (!refusal_code || !refusal_code[0]) {
        return;
    }
    strncpy(pipeline->last_refusal, refusal_code, sizeof(pipeline->last_refusal) - 1u);
    pipeline->last_refusal[sizeof(pipeline->last_refusal) - 1u] = '\0';
}

static void clear_refusal(client_session_pipeline* pipeline)
{
    if (!pipeline) {
        return;
    }
    pipeline->last_refusal[0] = '\0';
}

static void transition_to(client_session_pipeline* pipeline, client_session_stage_id stage_id)
{
    if (!pipeline) {
        return;
    }
    pipeline->stage_id = stage_id;
    pipeline->transition_count += 1u;
}

void client_session_pipeline_init(client_session_pipeline* pipeline)
{
    if (!pipeline) {
        return;
    }
    memset(pipeline, 0, sizeof(*pipeline));
    pipeline->stage_id = CLIENT_SESSION_STAGE_RESOLVE_SESSION;
}

const char* client_session_pipeline_stage_name(const client_session_pipeline* pipeline)
{
    if (!pipeline) {
        return client_session_stage_name(CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION);
    }
    return client_session_stage_name(pipeline->stage_id);
}

const char* client_session_pipeline_last_refusal(const client_session_pipeline* pipeline)
{
    if (!pipeline || !pipeline->last_refusal[0]) {
        return "";
    }
    return pipeline->last_refusal;
}

int client_session_pipeline_apply_command(client_session_pipeline* pipeline, const char* command_id)
{
    if (!pipeline || !command_id || !command_id[0]) {
        return 0;
    }
    clear_refusal(pipeline);

    if (!starts_with(command_id, "client.")) {
        return 1;
    }

    if (strcmp(command_id, "client.boot.start") == 0) {
        pipeline->epoch += 1u;
        pipeline->transition_count = 0u;
        transition_to(pipeline, CLIENT_SESSION_STAGE_RESOLVE_SESSION);
        return 1;
    }
    if (strcmp(command_id, "client.menu.open") == 0) {
        transition_to(pipeline, CLIENT_SESSION_STAGE_RESOLVE_SESSION);
        return 1;
    }
    if (strcmp(command_id, "client.world.play") == 0 ||
        strcmp(command_id, "client.server.connect") == 0) {
        transition_to(pipeline, CLIENT_SESSION_STAGE_ACQUIRE_WORLD);
        transition_to(pipeline, CLIENT_SESSION_STAGE_VERIFY_WORLD);
        transition_to(pipeline, CLIENT_SESSION_STAGE_WARMUP_SIMULATION);
        transition_to(pipeline, CLIENT_SESSION_STAGE_WARMUP_PRESENTATION);
        transition_to(pipeline, CLIENT_SESSION_STAGE_SESSION_READY);
        return 1;
    }
    if (strcmp(command_id, "client.session.acquire.local") == 0 ||
        strcmp(command_id, "client.session.acquire.spec") == 0 ||
        strcmp(command_id, "client.session.acquire.server") == 0 ||
        strcmp(command_id, "client.session.acquire.macro") == 0) {
        if (pipeline->stage_id == CLIENT_SESSION_STAGE_SESSION_RUNNING) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_INVALID_TRANSITION);
            return 0;
        }
        transition_to(pipeline, CLIENT_SESSION_STAGE_ACQUIRE_WORLD);
        return 1;
    }
    if (strcmp(command_id, "client.session.verify") == 0 ||
        strcmp(command_id, "client.session.verify.mismatch") == 0) {
        if (pipeline->stage_id != CLIENT_SESSION_STAGE_ACQUIRE_WORLD &&
            pipeline->stage_id != CLIENT_SESSION_STAGE_VERIFY_WORLD) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_INVALID_TRANSITION);
            return 0;
        }
        if (strcmp(command_id, "client.session.verify.mismatch") == 0) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_WORLD_HASH_MISMATCH);
            return 0;
        }
        transition_to(pipeline, CLIENT_SESSION_STAGE_VERIFY_WORLD);
        transition_to(pipeline, CLIENT_SESSION_STAGE_WARMUP_SIMULATION);
        transition_to(pipeline, CLIENT_SESSION_STAGE_WARMUP_PRESENTATION);
        transition_to(pipeline, CLIENT_SESSION_STAGE_SESSION_READY);
        return 1;
    }
    if (strcmp(command_id, "client.session.inspect") == 0 ||
        strcmp(command_id, "client.session.map.open") == 0 ||
        strcmp(command_id, "client.session.stats") == 0 ||
        strcmp(command_id, "client.session.replay.toggle") == 0) {
        if (pipeline->stage_id != CLIENT_SESSION_STAGE_SESSION_READY) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_INVALID_TRANSITION);
            return 0;
        }
        return 1;
    }
    if (strcmp(command_id, "client.experience.select") == 0 ||
        strcmp(command_id, "client.scenario.select") == 0 ||
        strcmp(command_id, "client.parameters.select") == 0) {
        if (pipeline->stage_id == CLIENT_SESSION_STAGE_SESSION_RUNNING) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_INVALID_TRANSITION);
            return 0;
        }
        return 1;
    }
    if (strcmp(command_id, "client.session.begin") == 0) {
        if (pipeline->stage_id != CLIENT_SESSION_STAGE_SESSION_READY) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_BEGIN_REQUIRES_READY);
            return 0;
        }
        transition_to(pipeline, CLIENT_SESSION_STAGE_SESSION_RUNNING);
        return 1;
    }
    if (strcmp(command_id, "client.session.abort") == 0 ||
        strcmp(command_id, "client.menu.quit") == 0) {
        transition_to(pipeline, CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION);
        return 1;
    }
    if (strcmp(command_id, "client.session.suspend") == 0) {
        if (pipeline->stage_id != CLIENT_SESSION_STAGE_SESSION_RUNNING) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_INVALID_TRANSITION);
            return 0;
        }
        transition_to(pipeline, CLIENT_SESSION_STAGE_SUSPEND_SESSION);
        return 1;
    }
    if (strcmp(command_id, "client.session.resume") == 0) {
        if (pipeline->stage_id != CLIENT_SESSION_STAGE_SUSPEND_SESSION) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_RESUME_REQUIRES_SUSPEND);
            return 0;
        }
        transition_to(pipeline, CLIENT_SESSION_STAGE_RESUME_SESSION);
        transition_to(pipeline, CLIENT_SESSION_STAGE_SESSION_READY);
        return 1;
    }
    if (strcmp(command_id, "client.session.reentry") == 0 ||
        starts_with(command_id, "client.session.reentry.")) {
        transition_to(pipeline, CLIENT_SESSION_STAGE_RESOLVE_SESSION);
        transition_to(pipeline, CLIENT_SESSION_STAGE_ACQUIRE_WORLD);
        transition_to(pipeline, CLIENT_SESSION_STAGE_VERIFY_WORLD);
        transition_to(pipeline, CLIENT_SESSION_STAGE_WARMUP_SIMULATION);
        transition_to(pipeline, CLIENT_SESSION_STAGE_WARMUP_PRESENTATION);
        transition_to(pipeline, CLIENT_SESSION_STAGE_SESSION_READY);
        return 1;
    }

    if (starts_with(command_id, "client.world.") || starts_with(command_id, "client.server.")) {
        if (pipeline->stage_id == CLIENT_SESSION_STAGE_SESSION_RUNNING) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_INVALID_TRANSITION);
            return 0;
        }
        return 1;
    }
    return 1;
}
