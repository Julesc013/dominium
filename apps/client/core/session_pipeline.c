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

static void copy_text(char* out, size_t cap, const char* value)
{
    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (!value || !value[0]) {
        return;
    }
    strncpy(out, value, cap - 1u);
    out[cap - 1u] = '\0';
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

static void append_stage_log(client_session_pipeline* pipeline,
                             const char* command_id,
                             client_session_stage_id from_stage_id,
                             client_session_stage_id to_stage_id,
                             const char* status,
                             const char* refusal_code)
{
    client_session_stage_log_entry* row = 0;
    if (!pipeline) {
        return;
    }
    if (pipeline->stage_log_count >= (u32)(sizeof(pipeline->stage_log) / sizeof(pipeline->stage_log[0]))) {
        memmove(&pipeline->stage_log[0],
                &pipeline->stage_log[1],
                sizeof(pipeline->stage_log) - sizeof(pipeline->stage_log[0]));
        pipeline->stage_log_count -= 1u;
    }
    row = &pipeline->stage_log[pipeline->stage_log_count];
    memset(row, 0, sizeof(*row));
    copy_text(row->command_id, sizeof(row->command_id), command_id);
    copy_text(row->from_stage, sizeof(row->from_stage), client_session_stage_name(from_stage_id));
    copy_text(row->to_stage, sizeof(row->to_stage), client_session_stage_name(to_stage_id));
    copy_text(row->status, sizeof(row->status), status);
    copy_text(row->refusal_code, sizeof(row->refusal_code), refusal_code);
    pipeline->stage_log_count += 1u;
}

static int transition_to(client_session_pipeline* pipeline, client_session_stage_id stage_id)
{
    if (!pipeline) {
        return 0;
    }
    if (pipeline->stage_id == stage_id) {
        return 1;
    }
    if (!client_session_stage_transition_allowed(pipeline->stage_id, stage_id)) {
        set_refusal(pipeline, CLIENT_SESSION_REFUSE_STAGE_INVALID_TRANSITION);
        return 0;
    }
    pipeline->stage_id = stage_id;
    pipeline->transition_count += 1u;
    return 1;
}

static int artifacts_ready_for_session_ready(const client_session_artifacts* artifacts, const char** out_refusal)
{
    if (out_refusal) {
        *out_refusal = CLIENT_SESSION_REFUSE_SESSION_READY_ARTIFACTS_MISSING;
    }
    if (!artifacts) {
        return 0;
    }
    if (artifacts->mode == CLIENT_WORLD_ACQUIRE_NONE) {
        return 0;
    }
    if (!artifacts->verified || !artifacts->warmup_simulation_ready || !artifacts->warmup_presentation_ready) {
        return 0;
    }
    if (artifacts->simulation_time_advanced != 0) {
        if (out_refusal) {
            *out_refusal = CLIENT_SESSION_REFUSE_SESSION_READY_TIME_NONZERO;
        }
        return 0;
    }
    return 1;
}

static int session_ready_only_command(const char* command_id)
{
    if (!command_id || !command_id[0]) {
        return 0;
    }
    if (strcmp(command_id, "client.session.inspect") == 0) return 1;
    if (strcmp(command_id, "client.session.map.open") == 0) return 1;
    if (strcmp(command_id, "client.session.stats") == 0) return 1;
    if (strcmp(command_id, "client.session.replay.toggle") == 0) return 1;
    return 0;
}

void client_session_pipeline_init(client_session_pipeline* pipeline)
{
    if (!pipeline) {
        return;
    }
    memset(pipeline, 0, sizeof(*pipeline));
    pipeline->stage_id = CLIENT_SESSION_STAGE_RESOLVE_SESSION;
    pipeline->last_stage_before_abort = CLIENT_SESSION_STAGE_RESOLVE_SESSION;
    pipeline->resume_snapshot_available = 0;
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

int client_session_pipeline_apply_command(client_session_pipeline* pipeline,
                                          const char* command_id,
                                          const client_session_artifacts* artifacts)
{
    client_session_stage_id from_stage;
    client_session_stage_id target_stage;
    const char* ready_refusal = CLIENT_SESSION_REFUSE_SESSION_READY_ARTIFACTS_MISSING;
    if (!pipeline || !command_id || !command_id[0]) {
        return 0;
    }
    from_stage = pipeline->stage_id;
    clear_refusal(pipeline);

    if (!starts_with(command_id, "client.")) {
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }

    if (strcmp(command_id, "client.boot.start") == 0) {
        pipeline->epoch += 1u;
        pipeline->transition_count = 0u;
        pipeline->stage_id = CLIENT_SESSION_STAGE_RESOLVE_SESSION;
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }
    if (strcmp(command_id, "client.menu.open") == 0) {
        pipeline->stage_id = CLIENT_SESSION_STAGE_RESOLVE_SESSION;
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }
    if (strcmp(command_id, "client.session.stage") == 0) {
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }
    if (strcmp(command_id, "client.world.play") == 0 ||
        strcmp(command_id, "client.server.connect") == 0 ||
        strcmp(command_id, "client.session.acquire.local") == 0 ||
        strcmp(command_id, "client.session.acquire.spec") == 0 ||
        strcmp(command_id, "client.session.acquire.server") == 0 ||
        strcmp(command_id, "client.session.acquire.macro") == 0) {
        if (!transition_to(pipeline, CLIENT_SESSION_STAGE_ACQUIRE_WORLD)) {
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }
    if (strcmp(command_id, "client.session.verify") == 0 ||
        strcmp(command_id, "client.session.verify.mismatch") == 0) {
        if (strcmp(command_id, "client.session.verify.mismatch") == 0) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_WORLD_HASH_MISMATCH);
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        if (!transition_to(pipeline, CLIENT_SESSION_STAGE_VERIFY_WORLD)) {
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }
    if (strcmp(command_id, "client.session.warmup.simulation") == 0) {
        if (!transition_to(pipeline, CLIENT_SESSION_STAGE_WARMUP_SIMULATION)) {
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }
    if (strcmp(command_id, "client.session.warmup.presentation") == 0) {
        if (!transition_to(pipeline, CLIENT_SESSION_STAGE_WARMUP_PRESENTATION)) {
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }
    if (strcmp(command_id, "client.session.ready") == 0) {
        if (!artifacts_ready_for_session_ready(artifacts, &ready_refusal)) {
            set_refusal(pipeline, ready_refusal);
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        if (!transition_to(pipeline, CLIENT_SESSION_STAGE_SESSION_READY)) {
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }
    if (session_ready_only_command(command_id)) {
        if (pipeline->stage_id != CLIENT_SESSION_STAGE_SESSION_READY) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_STAGE_INVALID_TRANSITION);
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }
    if (strcmp(command_id, "client.experience.select") == 0 ||
        strcmp(command_id, "client.scenario.select") == 0 ||
        strcmp(command_id, "client.parameters.select") == 0) {
        if (pipeline->stage_id == CLIENT_SESSION_STAGE_SESSION_RUNNING) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_STAGE_INVALID_TRANSITION);
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }
    if (strcmp(command_id, "client.session.begin") == 0) {
        if (pipeline->stage_id != CLIENT_SESSION_STAGE_SESSION_READY) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_BEGIN_REQUIRES_READY);
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        if (!transition_to(pipeline, CLIENT_SESSION_STAGE_SESSION_RUNNING)) {
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }
    if (strcmp(command_id, "client.session.abort") == 0 ||
        strcmp(command_id, "client.menu.quit") == 0) {
        if (!client_session_stage_abort_allowed(pipeline->stage_id)) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_STAGE_INVALID_TRANSITION);
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        pipeline->last_stage_before_abort = pipeline->stage_id;
        pipeline->resume_snapshot_available = client_session_stage_resume_allowed(pipeline->stage_id);
        if (!transition_to(pipeline, CLIENT_SESSION_STAGE_TEAR_DOWN_SESSION)) {
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }
    if (strcmp(command_id, "client.session.suspend") == 0) {
        if (!transition_to(pipeline, CLIENT_SESSION_STAGE_SUSPEND_SESSION)) {
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        pipeline->resume_snapshot_available = 1;
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }
    if (strcmp(command_id, "client.session.resume") == 0) {
        if (pipeline->stage_id != CLIENT_SESSION_STAGE_SUSPEND_SESSION) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_RESUME_REQUIRES_SUSPEND);
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        if (!pipeline->resume_snapshot_available) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_RESUME_INCOMPATIBLE);
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        if (!transition_to(pipeline, CLIENT_SESSION_STAGE_RESUME_SESSION)) {
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }
    if (strcmp(command_id, "client.session.reentry") == 0 ||
        starts_with(command_id, "client.session.reentry.")) {
        pipeline->stage_id = CLIENT_SESSION_STAGE_RESOLVE_SESSION;
        pipeline->transition_count += 1u;
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }

    if (starts_with(command_id, "client.world.") || starts_with(command_id, "client.server.")) {
        if (pipeline->stage_id == CLIENT_SESSION_STAGE_SESSION_RUNNING) {
            set_refusal(pipeline, CLIENT_SESSION_REFUSE_STAGE_INVALID_TRANSITION);
            append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "refusal", pipeline->last_refusal);
            return 0;
        }
        append_stage_log(pipeline, command_id, from_stage, pipeline->stage_id, "pass", "");
        return 1;
    }
    target_stage = pipeline->stage_id;
    append_stage_log(pipeline, command_id, from_stage, target_stage, "pass", "");
    return 1;
}

u32 client_session_pipeline_stage_log_count(const client_session_pipeline* pipeline)
{
    if (!pipeline) {
        return 0u;
    }
    return pipeline->stage_log_count;
}

const client_session_stage_log_entry* client_session_pipeline_stage_log_at(const client_session_pipeline* pipeline,
                                                                           u32 index)
{
    if (!pipeline) {
        return 0;
    }
    if (index >= pipeline->stage_log_count) {
        return 0;
    }
    return &pipeline->stage_log[index];
}
