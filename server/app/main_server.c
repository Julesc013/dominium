/*
Minimal server entrypoint with MP0 loopback/local modes.
*/
#include "domino/control.h"
#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/config_base.h"
#include "domino/gfx.h"
#include "domino/app/runtime.h"
#include "domino/version.h"
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"
#include "dominium/app/app_runtime.h"
#include "dominium/app/compat_report.h"
#include "dominium/app/readonly_adapter.h"
#include "dominium/app/readonly_format.h"
#include "dominium/session/mp0_session.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <ctype.h>
#include <errno.h>
#include <time.h>
#if defined(_WIN32)
#include <direct.h>
#endif

#if !defined(_WIN32)
int mkdir(const char* path, int mode);
#endif

#define SERVER_PATH_MAX 512
#define SERVER_DEFAULT_TICKS 60u
#define SERVER_LOG_ROTATE_MAX 5
#define SERVER_REPLAY_ROTATE_MAX 5
#define SERVER_LOG_DEFAULT_MAX_BYTES (1024u * 1024u)
#define SERVER_COMPAT_DEFAULT_BASELINE "BASELINE_MAINLINE_CORE"
#define SERVER_COMPAT_REPORT_NAME "compat_report.json"
#define SERVER_NULL_UUID "00000000-0000-0000-0000-000000000000"
#define SERVER_LOG_HEADER "{\"schema\":\"server_log_v1\"}"
#define SERVER_REPLAY_HEADER "DOMINIUM_REPLAY_V1"

static void print_help(void)
{
    printf("usage: server [options]\n");
    printf("options:\n");
    printf("  --help                      Show this help\n");
    printf("  --version                   Show product version\n");
    printf("  --build-info                Show build info + control capabilities\n");
    printf("  --status                    Show active control layers\n");
    printf("  --smoke                     Run deterministic CLI smoke\n");
    printf("  --selftest                  Alias for --smoke\n");
    printf("  --ui=none|tui|gui           Select UI shell (headless default)\n");
    printf("  --deterministic             Use fixed timestep (no wall-clock sleep)\n");
    printf("  --interactive               Use variable timestep (wall-clock)\n");
    printf("  --headless                   Run headless server (default)\n");
    printf("  --inspect                    Run read-only inspection mode\n");
    printf("  --validate                   Validate compatibility and exit\n");
    printf("  --replay <file>              Inspect replay file\n");
    printf("  --replay-step <n>            Start replay at event index\n");
    printf("  --replay-steps <n>           Emit N replay events (with --replay-step)\n");
    printf("  --replay-rewind              Rewind replay to event 0\n");
    printf("  --replay-pause               Open replay without playback\n");
    printf("  --format <text|json>         Output format for inspect\n");
    printf("  --data-root <path>           Override data root\n");
    printf("  --log-root <path>            Override log root\n");
    printf("  --log-max-bytes <n>          Max bytes per log file (0 disables)\n");
    printf("  --log-rotate-max <n>         Max rotated log files\n");
    printf("  --replay-out <path>          Replay output path (headless)\n");
    printf("  --replay-rotate-max <n>      Max rotated replay files\n");
    printf("  --no-replay                  Disable replay generation\n");
    printf("  --compat-report <path>       Write compat_report JSON\n");
    printf("  --instance-id <id>           Instance identifier\n");
    printf("  --ticks <n>                  Tick count for headless runs\n");
    printf("  --checkpoint-interval <n>    Emit checkpoint logs every N ticks\n");
    printf("  --health-interval <n>        Emit health logs every N ticks\n");
    printf("  --expect-engine-version <v>  Require engine version match\n");
    printf("  --expect-game-version <v>    Require game version match\n");
    printf("  --expect-build-id <id>       Require build id match\n");
    printf("  --expect-sim-schema <id>     Require sim schema id match\n");
    printf("  --expect-build-info-abi <v>  Require build-info ABI match\n");
    printf("  --expect-caps-abi <v>        Require caps ABI match\n");
    printf("  --expect-gfx-api <v>         Require gfx API match\n");
    printf("  --control-enable=K1,K2       Enable control capabilities (canonical keys)\n");
    printf("  --control-registry <path>    Override control registry path\n");
    printf("  --mp0-loopback               Run MP0 loopback demo\n");
    printf("  --mp0-server-auth            Run MP0 server-auth demo\n");
}

static void print_version(const char* product_version)
{
    printf("server %s\n", product_version);
}

static void print_build_info(const char* product_name, const char* product_version)
{
    dom_app_build_info info;
    dom_app_build_info_init(&info, product_name, product_version);
    dom_app_print_build_info(&info);
}

static void print_control_caps(const dom_control_caps* caps)
{
    const dom_registry* reg = dom_control_caps_registry(caps);
    u32 i;
    u32 enabled = dom_control_caps_enabled_count(caps);
#if DOM_CONTROL_HOOKS
    printf("control_hooks=enabled\n");
#else
    printf("control_hooks=removed\n");
#endif
    printf("control_caps_enabled=%u\n", (unsigned int)enabled);
    if (!reg) {
        return;
    }
    for (i = 0u; i < reg->count; ++i) {
        const dom_registry_entry* entry = &reg->entries[i];
        if (dom_control_caps_is_enabled(caps, entry->id)) {
            printf("control_cap=%s\n", entry->key);
        }
    }
}

static int enable_control_list(dom_control_caps* caps, const char* list)
{
    char buf[512];
    size_t len;
    char* token;
    if (!list || !caps) {
        return 0;
    }
    len = strlen(list);
    if (len >= sizeof(buf)) {
        return -1;
    }
    memcpy(buf, list, len + 1u);
    token = buf;
    while (token) {
        char* comma = strchr(token, ',');
        if (comma) {
            *comma = '\0';
        }
        if (*token) {
            if (dom_control_caps_enable_key(caps, token) != DOM_CONTROL_OK) {
                return -1;
            }
        }
        token = comma ? (comma + 1u) : (char*)0;
    }
    return 0;
}

typedef struct server_log {
    FILE* handle;
    char path[SERVER_PATH_MAX];
    unsigned long long seq;
    unsigned long long tick;
    unsigned int max_bytes;
    unsigned int bytes;
    int rotate_max;
} server_log;

typedef struct server_replay {
    FILE* handle;
    unsigned long long event_count;
} server_replay;

typedef struct server_run_config {
    char data_root[SERVER_PATH_MAX];
    char log_root[SERVER_PATH_MAX];
    char log_path[SERVER_PATH_MAX];
    char replay_path[SERVER_PATH_MAX];
    char compat_report_path[SERVER_PATH_MAX];
    char instance_id[64];
    unsigned int ticks;
    unsigned int checkpoint_interval;
    unsigned int health_interval;
    unsigned int log_max_bytes;
    int log_rotate_max;
    int replay_rotate_max;
    int replay_enabled;
    int deterministic;
} server_run_config;

static const char* server_env_or_default(const char* key, const char* fallback)
{
    const char* value = getenv(key);
    if (value && value[0]) {
        return value;
    }
    return fallback;
}

static void server_copy_string(char* out, size_t cap, const char* value)
{
    if (!out || cap == 0u) {
        return;
    }
    if (!value) {
        out[0] = '\0';
        return;
    }
    strncpy(out, value, cap - 1u);
    out[cap - 1u] = '\0';
}

static void server_join_path(char* out, size_t cap, const char* base, const char* leaf)
{
    size_t len;
    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (!base || !base[0]) {
        server_copy_string(out, cap, leaf ? leaf : "");
        return;
    }
    server_copy_string(out, cap, base);
    len = strlen(out);
    if (len + 1u >= cap) {
        return;
    }
    if (len > 0u && out[len - 1u] != '/' && out[len - 1u] != '\\') {
        out[len++] = '/';
        out[len] = '\0';
    }
    if (leaf && leaf[0] && len + strlen(leaf) < cap) {
        strncat(out, leaf, cap - len - 1u);
    }
}

static int server_mkdir_single(const char* path)
{
    if (!path || !path[0]) {
        return 0;
    }
#if defined(_WIN32)
    if (_mkdir(path) == 0) {
        return 1;
    }
#else
    if (mkdir(path, 0755) == 0) {
        return 1;
    }
#endif
    return (errno == EEXIST);
}

static int server_ensure_dir(const char* path)
{
    char tmp[SERVER_PATH_MAX];
    size_t len;
    size_t i;
    if (!path || !path[0]) {
        return 0;
    }
    server_copy_string(tmp, sizeof(tmp), path);
    len = strlen(tmp);
    if (len == 0u) {
        return 0;
    }
    for (i = 1u; i < len; ++i) {
        if (tmp[i] == '/' || tmp[i] == '\\') {
            char ch = tmp[i];
            tmp[i] = '\0';
            if (!server_mkdir_single(tmp)) {
                tmp[i] = ch;
                return 0;
            }
            tmp[i] = ch;
        }
    }
    return server_mkdir_single(tmp);
}

static int server_ensure_dir_for_file(const char* path)
{
    char dir[SERVER_PATH_MAX];
    char* slash;
    char* bslash;
    if (!path || !path[0]) {
        return 0;
    }
    server_copy_string(dir, sizeof(dir), path);
    slash = strrchr(dir, '/');
    bslash = strrchr(dir, '\\');
    if (bslash && (!slash || bslash > slash)) {
        slash = bslash;
    }
    if (!slash) {
        return 1;
    }
    *slash = '\0';
    if (!dir[0]) {
        return 1;
    }
    return server_ensure_dir(dir);
}

static int server_file_exists(const char* path)
{
    FILE* f;
    if (!path || !path[0]) {
        return 0;
    }
    f = fopen(path, "rb");
    if (f) {
        fclose(f);
        return 1;
    }
    return 0;
}

static void server_build_instance_id(char* out, size_t cap, const char* value)
{
    size_t i;
    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (!value || !value[0]) {
        return;
    }
    for (i = 0u; value[i] && i + 1u < cap; ++i) {
        char c = value[i];
        if ((c >= 'a' && c <= 'z') ||
            (c >= 'A' && c <= 'Z') ||
            (c >= '0' && c <= '9') ||
            c == '_' || c == '-') {
            out[i] = c;
        } else {
            out[i] = '_';
        }
    }
    out[i] = '\0';
}

static int server_is_uuid(const char* value)
{
    size_t i;
    if (!value) {
        return 0;
    }
    if (strlen(value) != 36u) {
        return 0;
    }
    for (i = 0u; i < 36u; ++i) {
        char c = value[i];
        if (i == 8u || i == 13u || i == 18u || i == 23u) {
            if (c != '-') {
                return 0;
            }
            continue;
        }
        if (!isxdigit((unsigned char)c)) {
            return 0;
        }
    }
    return 1;
}

static void server_format_timestamp(char* out, size_t cap, int deterministic)
{
    if (!out || cap == 0u) {
        return;
    }
    if (deterministic) {
        server_copy_string(out, cap, "2000-01-01T00:00:00Z");
        return;
    }
    {
        time_t now = time(NULL);
        struct tm utc;
        int ok = 0;
#if defined(_WIN32)
        if (gmtime_s(&utc, &now) == 0) {
            ok = 1;
        }
#else
        if (gmtime_r(&now, &utc)) {
            ok = 1;
        }
#endif
        if (!ok) {
            server_copy_string(out, cap, "1970-01-01T00:00:00Z");
            return;
        }
        snprintf(out, cap, "%04d-%02d-%02dT%02d:%02d:%02dZ",
                 utc.tm_year + 1900,
                 utc.tm_mon + 1,
                 utc.tm_mday,
                 utc.tm_hour,
                 utc.tm_min,
                 utc.tm_sec);
    }
}

static void server_build_data_root(const char* override, char* out, size_t cap)
{
    const char* data_root = override;
    if (!data_root || !data_root[0]) {
        data_root = server_env_or_default("DOM_DATA_ROOT", "");
    }
    if (!data_root || !data_root[0]) {
        data_root = server_env_or_default("DOM_INSTANCE_ROOT", "");
    }
    if (!data_root || !data_root[0]) {
        data_root = "data";
    }
    server_copy_string(out, cap, data_root);
}

static int server_rotate_file(const char* path, int max_files)
{
    int i;
    if (!path || !path[0]) {
        return 0;
    }
    if (max_files <= 0) {
        return 1;
    }
    for (i = max_files - 1; i >= 1; --i) {
        char src[SERVER_PATH_MAX];
        char dst[SERVER_PATH_MAX];
        snprintf(src, sizeof(src), "%s.%d", path, i);
        snprintf(dst, sizeof(dst), "%s.%d", path, i + 1);
        if (server_file_exists(src)) {
            (void)remove(dst);
            (void)rename(src, dst);
        }
    }
    if (server_file_exists(path)) {
        char dst[SERVER_PATH_MAX];
        snprintf(dst, sizeof(dst), "%s.1", path);
        (void)remove(dst);
        (void)rename(path, dst);
    }
    return 1;
}

static void server_write_json_string(FILE* out, const char* value)
{
    const unsigned char* p = (const unsigned char*)value;
    if (!out) {
        return;
    }
    fputc('"', out);
    if (!value) {
        fputc('"', out);
        return;
    }
    while (*p) {
        unsigned char c = *p++;
        if (c == '"' || c == '\\') {
            fputc('\\', out);
            fputc((int)c, out);
        } else if (c == '\n') {
            fputs("\\n", out);
        } else if (c == '\r') {
            fputs("\\r", out);
        } else if (c == '\t') {
            fputs("\\t", out);
        } else {
            fputc((int)c, out);
        }
    }
    fputc('"', out);
}

static int server_log_open(server_log* log,
                           const char* path,
                           int rotate_max,
                           unsigned int max_bytes)
{
    unsigned int header_bytes;
    if (!log) {
        return 0;
    }
    memset(log, 0, sizeof(*log));
    if (!path || !path[0]) {
        return 0;
    }
    server_copy_string(log->path, sizeof(log->path), path);
    log->rotate_max = rotate_max;
    header_bytes = (unsigned int)strlen(SERVER_LOG_HEADER) + 1u;
    if (max_bytes > 0u && max_bytes <= header_bytes) {
        max_bytes = 0u;
    }
    log->max_bytes = max_bytes;
    server_rotate_file(path, rotate_max);
    log->handle = fopen(path, "w");
    if (!log->handle) {
        return 0;
    }
    fprintf(log->handle, "%s\n", SERVER_LOG_HEADER);
    log->bytes = header_bytes;
    return 1;
}

static void server_log_close(server_log* log)
{
    if (!log || !log->handle) {
        return;
    }
    fclose(log->handle);
    log->handle = 0;
}

static int server_log_rotate_if_needed(server_log* log)
{
    if (!log || !log->handle) {
        return 0;
    }
    if (log->max_bytes == 0u || log->bytes < log->max_bytes) {
        return 1;
    }
    fclose(log->handle);
    log->handle = 0;
    if (!log->path[0]) {
        return 0;
    }
    server_rotate_file(log->path, log->rotate_max);
    log->handle = fopen(log->path, "w");
    if (!log->handle) {
        return 0;
    }
    fprintf(log->handle, "%s\n", SERVER_LOG_HEADER);
    log->bytes = (unsigned int)strlen(SERVER_LOG_HEADER) + 1u;
    return 1;
}

static void server_log_emit(server_log* log,
                            const char* level,
                            const char* domain,
                            const char* event,
                            const char* message,
                            int refusal_code_id,
                            const char* refusal_code)
{
    long pos;
    if (!log || !log->handle) {
        return;
    }
    if (!server_log_rotate_if_needed(log)) {
        return;
    }
    fprintf(log->handle, "{\"seq\":%llu,\"tick\":%llu,",
            (unsigned long long)(log->seq + 1u),
            (unsigned long long)log->tick);
    fprintf(log->handle, "\"level\":");
    server_write_json_string(log->handle, level ? level : "info");
    fprintf(log->handle, ",\"domain\":");
    server_write_json_string(log->handle, domain ? domain : "server");
    fprintf(log->handle, ",\"event\":");
    server_write_json_string(log->handle, event ? event : "event");
    if (message && message[0]) {
        fprintf(log->handle, ",\"message\":");
        server_write_json_string(log->handle, message);
    }
    if (refusal_code_id > 0 || (refusal_code && refusal_code[0])) {
        fprintf(log->handle, ",\"refusal_code_id\":%d", refusal_code_id);
        fprintf(log->handle, ",\"refusal_code\":");
        server_write_json_string(log->handle, refusal_code ? refusal_code : "");
    }
    fprintf(log->handle, "}\n");
    log->seq += 1u;
    fflush(log->handle);
    pos = ftell(log->handle);
    if (pos >= 0) {
        log->bytes = (unsigned int)pos;
    }
}

static int server_replay_open(server_replay* replay, const char* path, int rotate_max)
{
    if (!replay) {
        return 0;
    }
    memset(replay, 0, sizeof(*replay));
    if (!path || !path[0]) {
        return 0;
    }
    server_rotate_file(path, rotate_max);
    replay->handle = fopen(path, "w");
    if (!replay->handle) {
        return 0;
    }
    fprintf(replay->handle, "%s\n", SERVER_REPLAY_HEADER);
    return 1;
}

static void server_replay_emit(server_replay* replay, const char* line)
{
    if (!replay || !replay->handle || !line || !line[0]) {
        return;
    }
    fprintf(replay->handle, "%s\n", line);
    replay->event_count += 1u;
}

static void server_replay_close(server_replay* replay)
{
    if (!replay || !replay->handle) {
        return;
    }
    fclose(replay->handle);
    replay->handle = 0;
}

static void server_config_init(server_run_config* cfg)
{
    if (!cfg) {
        return;
    }
    memset(cfg, 0, sizeof(*cfg));
    cfg->ticks = SERVER_DEFAULT_TICKS;
    cfg->checkpoint_interval = 0u;
    cfg->health_interval = 0u;
    cfg->log_max_bytes = SERVER_LOG_DEFAULT_MAX_BYTES;
    cfg->log_rotate_max = SERVER_LOG_ROTATE_MAX;
    cfg->replay_rotate_max = SERVER_REPLAY_ROTATE_MAX;
    cfg->replay_enabled = 1;
    cfg->deterministic = 0;
}

static int server_write_compat_report_json(const char* path,
                                           const char* context,
                                           const server_run_config* cfg,
                                           const dom_app_compat_report* report,
                                           const char* compat_mode,
                                           int refusal_code_id,
                                           const char* refusal_code)
{
    FILE* f;
    char timestamp[32];
    const char* context_tag = (context && context[0]) ? context : "run";
    const char* instance_uuid = SERVER_NULL_UUID;
    const char* instance_note = 0;
    const char* mode = compat_mode;
    int deterministic = 0;
    int has_refusal = 0;
    if (!path || !path[0] || !report) {
        return 0;
    }
    if (cfg) {
        deterministic = cfg->deterministic;
        if (cfg->instance_id[0]) {
            if (server_is_uuid(cfg->instance_id)) {
                instance_uuid = cfg->instance_id;
            } else {
                instance_note = cfg->instance_id;
            }
        }
    }
    if (!mode || !mode[0]) {
        mode = report->ok ? "full" : "refuse";
    }
    if (!refusal_code || !refusal_code[0]) {
        if (!report->ok) {
            refusal_code = "REFUSE_INTEGRITY_VIOLATION";
            refusal_code_id = 5;
        }
    }
    has_refusal = (refusal_code_id > 0 || (refusal_code && refusal_code[0]));
    server_format_timestamp(timestamp, sizeof(timestamp), deterministic);
    if (!server_ensure_dir_for_file(path)) {
        return 0;
    }
    f = fopen(path, "w");
    if (!f) {
        return 0;
    }
    fprintf(f, "{");
    fprintf(f, "\"context\":");
    server_write_json_string(f, context_tag);
    fprintf(f, ",\"install_id\":");
    server_write_json_string(f, SERVER_NULL_UUID);
    fprintf(f, ",\"instance_id\":");
    server_write_json_string(f, instance_uuid);
    fprintf(f, ",\"runtime_id\":");
    server_write_json_string(f, SERVER_NULL_UUID);
    fprintf(f, ",\"capability_baseline\":");
    server_write_json_string(f, SERVER_COMPAT_DEFAULT_BASELINE);
    fprintf(f, ",\"required_capabilities\":[]");
    fprintf(f, ",\"provided_capabilities\":[]");
    fprintf(f, ",\"missing_capabilities\":[]");
    fprintf(f, ",\"compatibility_mode\":");
    server_write_json_string(f, mode);
    fprintf(f, ",\"refusal_codes\":");
    if (has_refusal) {
        fprintf(f, "[");
        server_write_json_string(f, refusal_code);
        fprintf(f, "]");
    } else {
        fprintf(f, "[]");
    }
    fprintf(f, ",\"mitigation_hints\":[]");
    fprintf(f, ",\"timestamp\":");
    server_write_json_string(f, timestamp);
    fprintf(f, ",\"extensions\":{");
    fprintf(f, "\"app_compat\":{");
    fprintf(f, "\"product\":");
    server_write_json_string(f, report->product ? report->product : "");
    fprintf(f, ",\"ok\":%s", report->ok ? "true" : "false");
    fprintf(f, ",\"engine_version\":");
    server_write_json_string(f, report->engine_version ? report->engine_version : "");
    fprintf(f, ",\"game_version\":");
    server_write_json_string(f, report->game_version ? report->game_version : "");
    fprintf(f, ",\"build_id\":");
    server_write_json_string(f, report->build_id ? report->build_id : "");
    fprintf(f, ",\"git_hash\":");
    server_write_json_string(f, report->git_hash ? report->git_hash : "");
    fprintf(f, ",\"toolchain_id\":");
    server_write_json_string(f, report->toolchain_id ? report->toolchain_id : "");
    fprintf(f, ",\"sim_schema_id\":%llu", (unsigned long long)report->sim_schema_id);
    fprintf(f, ",\"build_info_abi\":%u", (unsigned int)report->build_info_abi);
    fprintf(f, ",\"build_info_struct_size\":%u", (unsigned int)report->build_info_struct_size);
    fprintf(f, ",\"caps_abi\":%u", (unsigned int)report->caps_abi);
    fprintf(f, ",\"gfx_api\":%u", (unsigned int)report->gfx_api);
    fprintf(f, ",\"message\":");
    server_write_json_string(f, report->message);
    fprintf(f, "}");
    fprintf(f, "}");
    if (has_refusal) {
        fprintf(f, ",\"refusal\":{");
        fprintf(f, "\"code_id\":%d", refusal_code_id);
        fprintf(f, ",\"code\":");
        server_write_json_string(f, refusal_code);
        fprintf(f, ",\"message\":");
        server_write_json_string(f, report->message[0] ? report->message : "refused");
        fprintf(f, ",\"details\":{}");
        fprintf(f, ",\"explanation_classification\":");
        server_write_json_string(f, "PUBLIC");
        fprintf(f, "}");
    }
    if (instance_note) {
        fprintf(f, ",\"notes\":{");
        fprintf(f, "\"instance_id_raw\":");
        server_write_json_string(f, instance_note);
        fprintf(f, "}");
    }
    fprintf(f, "}\n");
    fclose(f);
    return 1;
}

static int mp0_build_state(dom_mp0_state* state)
{
    (void)dom_mp0_state_init(state, 0);
    state->consumption.params.consumption_interval = 5;
    state->consumption.params.hunger_max = 2;
    state->consumption.params.thirst_max = 2;
    if (dom_mp0_register_cohort(state, 1u, 1u, 100u, 101u, 201u, 301u) != 0) {
        return -1;
    }
    if (dom_mp0_register_cohort(state, 2u, 1u, 100u, 102u, 202u, 302u) != 0) {
        return -2;
    }
    if (dom_mp0_set_needs(state, 1u, 0u, 0u, 1u) != 0) {
        return -3;
    }
    if (dom_mp0_set_needs(state, 2u, 5u, 5u, 1u) != 0) {
        return -4;
    }
    if (dom_mp0_bind_controller(state, 1u, 101u) != 0) {
        return -5;
    }
    return 0;
}

static int mp0_build_commands(dom_mp0_command_queue* queue, dom_mp0_command* storage)
{
    survival_production_action_input gather;
    life_cmd_continuation_select cont;

    dom_mp0_command_queue_init(queue, storage, DOM_MP0_MAX_COMMANDS);
    memset(&gather, 0, sizeof(gather));
    gather.cohort_id = 2u;
    gather.type = SURVIVAL_ACTION_GATHER_FOOD;
    gather.start_tick = 0;
    gather.duration_ticks = 5;
    gather.output_food = 4u;
    gather.provenance_ref = 900u;
    if (dom_mp0_command_add_production(queue, 0, &gather) != 0) {
        return -1;
    }

    memset(&cont, 0, sizeof(cont));
    cont.controller_id = 1u;
    cont.policy_id = LIFE_POLICY_S1;
    cont.target_person_id = 102u;
    cont.action = LIFE_CONT_ACTION_TRANSFER;
    if (dom_mp0_command_add_continuation(queue, 15, &cont) != 0) {
        return -2;
    }
    dom_mp0_command_sort(queue);
    return 0;
}

static int mp0_run_server_auth(void)
{
    static dom_mp0_state server;
    static dom_mp0_state client;
    dom_mp0_command_queue queue;
    dom_mp0_command storage[DOM_MP0_MAX_COMMANDS];
    u64 hash_server;
    u64 hash_client;

    if (mp0_build_commands(&queue, storage) != 0) {
        return D_APP_EXIT_FAILURE;
    }
    if (mp0_build_state(&server) != 0) {
        return D_APP_EXIT_FAILURE;
    }
    if (mp0_build_state(&client) != 0) {
        return D_APP_EXIT_FAILURE;
    }
    (void)dom_mp0_run(&server, &queue, 30);
    dom_mp0_copy_authoritative(&server, &client);
    hash_server = dom_mp0_hash_state(&server);
    hash_client = dom_mp0_hash_state(&client);
    printf("MP0 server-auth hash: %llu (client %llu)\n",
           (unsigned long long)hash_server,
           (unsigned long long)hash_client);
    return (hash_server == hash_client) ? D_APP_EXIT_OK : D_APP_EXIT_FAILURE;
}

static int mp0_run_loopback(void)
{
    static dom_mp0_state state;
    dom_mp0_command_queue queue;
    dom_mp0_command storage[DOM_MP0_MAX_COMMANDS];
    u64 hash_state;

    if (mp0_build_commands(&queue, storage) != 0) {
        return D_APP_EXIT_FAILURE;
    }
    if (mp0_build_state(&state) != 0) {
        return D_APP_EXIT_FAILURE;
    }
    (void)dom_mp0_run(&state, &queue, 30);
    hash_state = dom_mp0_hash_state(&state);
    printf("MP0 loopback hash: %llu\n", (unsigned long long)hash_state);
    return D_APP_EXIT_OK;
}

static int server_parse_u32(const char* text, uint32_t* out_value)
{
    char* end = 0;
    unsigned long value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtoul(text, &end, 10);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = (uint32_t)value;
    return 1;
}

static int server_parse_u64(const char* text, uint64_t* out_value)
{
    unsigned long long value = 0u;
    int base = 10;
    const char* p;
    if (!text || !out_value) {
        return 0;
    }
    p = text;
    if (p[0] == '0' && (p[1] == 'x' || p[1] == 'X')) {
        base = 16;
        p += 2;
    }
    if (*p == '\0') {
        return 0;
    }
    while (*p) {
        int digit;
        char c = *p++;
        if (c >= '0' && c <= '9') {
            digit = c - '0';
        } else if (base == 16 && c >= 'a' && c <= 'f') {
            digit = 10 + (c - 'a');
        } else if (base == 16 && c >= 'A' && c <= 'F') {
            digit = 10 + (c - 'A');
        } else {
            return 0;
        }
        value = value * (unsigned long long)base + (unsigned long long)digit;
    }
    *out_value = (uint64_t)value;
    return 1;
}

static int server_parse_int(const char* text, int* out_value)
{
    char* end = 0;
    long value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtol(text, &end, 10);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = (int)value;
    return 1;
}

static void server_log_control_caps(server_log* log, const dom_control_caps* caps)
{
    const dom_registry* reg;
    u32 i;
    if (!log || !log->handle || !caps) {
        return;
    }
    reg = dom_control_caps_registry(caps);
    if (!reg) {
        server_log_emit(log, "warn", "control_caps", "registry_missing",
                        "control registry missing", 0, 0);
        return;
    }
    for (i = 0u; i < reg->count; ++i) {
        const dom_registry_entry* entry = &reg->entries[i];
        if (dom_control_caps_is_enabled(caps, entry->id)) {
            server_log_emit(log, "info", "control_caps", "enabled",
                            entry->key, 0, 0);
        }
    }
}

static int server_replay_scan(const char* path,
                              int step_index,
                              int max_steps,
                              int emit_all,
                              int* out_events)
{
    FILE* f;
    char line[256];
    int header_checked = 0;
    int events = 0;
    int emitted = 0;
    if (out_events) {
        *out_events = 0;
    }
    if (!path || !path[0]) {
        fprintf(stderr, "server: replay path missing\n");
        return 0;
    }
    f = fopen(path, "r");
    if (!f) {
        fprintf(stderr, "server: replay open failed\n");
        return 0;
    }
    while (fgets(line, sizeof(line), f)) {
        size_t len = strlen(line);
        while (len > 0u && (line[len - 1u] == '\n' || line[len - 1u] == '\r')) {
            line[--len] = '\0';
        }
        if (!header_checked) {
            header_checked = 1;
            if (strcmp(line, SERVER_REPLAY_HEADER) == 0) {
                continue;
            }
        }
        if (!line[0]) {
            continue;
        }
        if (step_index >= 0) {
            if (events == step_index) {
                printf("replay_event=%s\n", line);
                emitted = 1;
                if (max_steps <= 1) {
                    events += 1;
                    break;
                }
            }
            if (events > step_index && max_steps > 0) {
                if (emitted < max_steps) {
                    printf("replay_event=%s\n", line);
                    emitted += 1;
                    if (emitted >= max_steps) {
                        events += 1;
                        break;
                    }
                }
            }
        } else if (emit_all) {
            printf("replay_event=%s\n", line);
        }
        events += 1;
    }
    fclose(f);
    if (out_events) {
        *out_events = events;
    }
    if (step_index >= 0 && emitted == 0) {
        fprintf(stderr, "server: replay step unavailable\n");
        return 0;
    }
    if (events <= 0) {
        fprintf(stderr, "server: replay empty\n");
        return 0;
    }
    return 1;
}

static int server_build_paths(server_run_config* cfg,
                              const char* data_root_override,
                              const char* log_root_override,
                              const char* replay_override,
                              const char* compat_override,
                              const char* instance_override)
{
    char tmp[SERVER_PATH_MAX];
    const char* instance_dir;
    if (!cfg) {
        return 0;
    }
    server_build_data_root(data_root_override, cfg->data_root, sizeof(cfg->data_root));
    server_build_instance_id(cfg->instance_id, sizeof(cfg->instance_id),
                             instance_override && instance_override[0]
                                 ? instance_override
                                 : server_env_or_default("DOM_INSTANCE_ID", ""));
    instance_dir = cfg->instance_id[0] ? cfg->instance_id : "default";
    if (log_root_override && log_root_override[0]) {
        server_copy_string(cfg->log_root, sizeof(cfg->log_root), log_root_override);
    } else {
        server_join_path(cfg->log_root, sizeof(cfg->log_root), cfg->data_root, "logs/server");
    }
    if (instance_dir && instance_dir[0]) {
        server_join_path(tmp, sizeof(tmp), cfg->log_root, instance_dir);
        server_copy_string(cfg->log_root, sizeof(cfg->log_root), tmp);
    }
    if (!server_ensure_dir(cfg->log_root)) {
        return 0;
    }
    server_join_path(cfg->log_path, sizeof(cfg->log_path), cfg->log_root, "server.log");

    if (replay_override && replay_override[0]) {
        server_copy_string(cfg->replay_path, sizeof(cfg->replay_path), replay_override);
        if (!server_ensure_dir_for_file(cfg->replay_path)) {
            return 0;
        }
    } else {
        server_join_path(tmp, sizeof(tmp), cfg->data_root, "replays");
        if (instance_dir && instance_dir[0]) {
            char replay_root[SERVER_PATH_MAX];
            server_join_path(replay_root, sizeof(replay_root), tmp, instance_dir);
            server_copy_string(tmp, sizeof(tmp), replay_root);
        }
        if (!server_ensure_dir(tmp)) {
            return 0;
        }
        server_join_path(cfg->replay_path, sizeof(cfg->replay_path), tmp, "server.replay");
    }

    if (compat_override && compat_override[0]) {
        server_copy_string(cfg->compat_report_path, sizeof(cfg->compat_report_path), compat_override);
        if (!server_ensure_dir_for_file(cfg->compat_report_path)) {
            return 0;
        }
    } else {
        server_join_path(tmp, sizeof(tmp), cfg->data_root, "compat");
        if (instance_dir && instance_dir[0]) {
            char compat_root[SERVER_PATH_MAX];
            server_join_path(compat_root, sizeof(compat_root), tmp, instance_dir);
            server_copy_string(tmp, sizeof(tmp), compat_root);
        }
        if (!server_ensure_dir(tmp)) {
            return 0;
        }
        server_join_path(cfg->compat_report_path, sizeof(cfg->compat_report_path), tmp,
                         SERVER_COMPAT_REPORT_NAME);
    }
    return 1;
}

static int server_run_headless(const server_run_config* cfg,
                               const dom_app_compat_expect* expect,
                               const dom_control_caps* caps,
                               int caps_loaded)
{
    server_log log;
    server_replay replay;
    dom_app_compat_report report;
    unsigned int tick;
    int ok;
    const char* compat_mode;
    if (!cfg) {
        return D_APP_EXIT_FAILURE;
    }
    dom_app_compat_report_init(&report, "server");
    ok = dom_app_compat_check(expect, &report);
    compat_mode = ok ? "full" : "refuse";
    if (!server_log_open(&log, cfg->log_path, cfg->log_rotate_max, cfg->log_max_bytes)) {
        fprintf(stderr, "server: failed to open log\n");
        return D_APP_EXIT_FAILURE;
    }
    server_log_emit(&log, "info", "server", "start", "headless", 0, 0);
    if (!cfg->compat_report_path[0] ||
        !server_write_compat_report_json(cfg->compat_report_path,
                                         "run",
                                         cfg,
                                         &report,
                                         compat_mode,
                                         ok ? 0 : 5,
                                         ok ? 0 : "REFUSE_INTEGRITY_VIOLATION")) {
        server_log_emit(&log, "error", "compat", "report_failed",
                        "compat_report write failed", 5, "REFUSE_INTEGRITY_VIOLATION");
        server_log_close(&log);
        return D_APP_EXIT_FAILURE;
    }
    if (!ok) {
        server_log_emit(&log, "error", "compat", "failed", report.message,
                        5, "REFUSE_INTEGRITY_VIOLATION");
        dom_app_compat_print_report(&report, stderr);
        server_log_close(&log);
        return D_APP_EXIT_UNAVAILABLE;
    }
    server_log_emit(&log, "info", "compat", "ok", "compat_report ok", 0, 0);
    if (caps_loaded && caps) {
        server_log_control_caps(&log, caps);
    } else {
        server_log_emit(&log, "warn", "control_caps", "unavailable",
                        "control registry unavailable", 0, 0);
    }
    if (cfg->replay_enabled) {
        if (!server_replay_open(&replay, cfg->replay_path, cfg->replay_rotate_max)) {
            server_log_emit(&log, "error", "replay", "open_failed",
                            "replay open failed", 5, "REFUSE_INTEGRITY_VIOLATION");
            server_log_close(&log);
            return D_APP_EXIT_FAILURE;
        }
        server_replay_emit(&replay, "event=server.start");
    } else {
        server_log_emit(&log, "warn", "replay", "disabled", "replay disabled", 0, 0);
    }
    for (tick = 0u; tick < cfg->ticks; ++tick) {
        char line[128];
        log.tick = tick;
        server_log_emit(&log, "info", "tick", "advance", "tick", 0, 0);
        if (cfg->replay_enabled) {
            snprintf(line, sizeof(line), "tick=%u event=server.tick", tick);
            server_replay_emit(&replay, line);
        }
        if (cfg->checkpoint_interval > 0u && (tick % cfg->checkpoint_interval) == 0u) {
            server_log_emit(&log, "info", "checkpoint", "emitted",
                            "checkpoint metadata written", 0, 0);
        }
        if (cfg->health_interval > 0u && (tick % cfg->health_interval) == 0u) {
            server_log_emit(&log, "warn", "health", "memory_plateau",
                            "memory plateau check unsupported", 1, "REFUSE_INVALID_INTENT");
        }
    }
    if (cfg->replay_enabled) {
        server_replay_emit(&replay, "event=server.shutdown");
        server_replay_close(&replay);
    }
    server_log_emit(&log, "info", "server", "shutdown", "normal", 0, 0);
    server_log_close(&log);
    return D_APP_EXIT_OK;
}

static int server_run_inspect(const server_run_config* cfg,
                              dom_app_output_format format,
                              const dom_app_compat_expect* expect,
                              const dom_control_caps* caps,
                              int caps_loaded)
{
    server_log log;
    dom_app_readonly_adapter ro;
    dom_app_ro_core_info core_info;
    dom_app_ro_tree_node nodes[256];
    dom_app_ro_tree_info tree_info;
    dom_app_compat_report report;
    int ok;
    if (!cfg) {
        return D_APP_EXIT_FAILURE;
    }
    if (!format) {
        format = DOM_APP_FORMAT_TEXT;
    }
    dom_app_compat_report_init(&report, "server");
    ok = dom_app_compat_check(expect, &report);
    if (!server_log_open(&log, cfg->log_path, cfg->log_rotate_max, cfg->log_max_bytes)) {
        fprintf(stderr, "server: failed to open log\n");
        return D_APP_EXIT_FAILURE;
    }
    server_log_emit(&log, "info", "server", "start", "inspect", 0, 0);
    if (!cfg->compat_report_path[0] ||
        !server_write_compat_report_json(cfg->compat_report_path,
                                         "inspect",
                                         cfg,
                                         &report,
                                         ok ? "inspect-only" : "refuse",
                                         ok ? 0 : 5,
                                         ok ? 0 : "REFUSE_INTEGRITY_VIOLATION")) {
        server_log_emit(&log, "error", "compat", "report_failed",
                        "compat_report write failed", 5, "REFUSE_INTEGRITY_VIOLATION");
        server_log_close(&log);
        return D_APP_EXIT_FAILURE;
    }
    if (!ok) {
        server_log_emit(&log, "error", "compat", "failed", report.message,
                        5, "REFUSE_INTEGRITY_VIOLATION");
        dom_app_compat_print_report(&report, stderr);
        server_log_close(&log);
        return D_APP_EXIT_UNAVAILABLE;
    }
    server_log_emit(&log, "info", "compat", "ok", "compat_report ok", 0, 0);
    if (caps_loaded && caps) {
        server_log_control_caps(&log, caps);
    } else {
        server_log_emit(&log, "warn", "control_caps", "unavailable",
                        "control registry unavailable", 0, 0);
    }
    dom_app_ro_init(&ro);
    if (!dom_app_ro_open(&ro, expect, &report)) {
        fprintf(stderr, "server: compatibility failure: %s\n",
                report.message[0] ? report.message : "unknown");
        dom_app_compat_print_report(&report, stderr);
        server_log_emit(&log, "error", "inspect", "open_failed",
                        "readonly adapter unavailable", 5, "REFUSE_INTEGRITY_VIOLATION");
        dom_app_ro_close(&ro);
        server_log_close(&log);
        return D_APP_EXIT_UNAVAILABLE;
    }
    if (dom_app_ro_get_core_info(&ro, &core_info) != DOM_APP_RO_OK) {
        fprintf(stderr, "server: inspector core unavailable\n");
        server_log_emit(&log, "error", "inspect", "core_missing",
                        "inspector core unavailable", 5, "REFUSE_INTEGRITY_VIOLATION");
        dom_app_ro_close(&ro);
        server_log_close(&log);
        return D_APP_EXIT_UNAVAILABLE;
    }
    if (dom_app_ro_get_tree(&ro, "packages_tree", nodes,
                            (uint32_t)(sizeof(nodes) / sizeof(nodes[0])),
                            &tree_info) != DOM_APP_RO_OK) {
        fprintf(stderr, "server: topology unavailable\n");
        server_log_emit(&log, "error", "inspect", "topology_missing",
                        "topology unavailable", 5, "REFUSE_INTEGRITY_VIOLATION");
        dom_app_ro_close(&ro);
        server_log_close(&log);
        return D_APP_EXIT_UNAVAILABLE;
    }
    dom_app_ro_print_inspector_bundle(format,
                                      &core_info,
                                      "packages_tree",
                                      nodes,
                                      tree_info.count,
                                      tree_info.truncated,
                                      dom_app_ro_snapshots_supported(),
                                      dom_app_ro_events_supported(),
                                      dom_app_ro_replay_supported());
    dom_app_ro_close(&ro);
    server_log_emit(&log, "info", "server", "shutdown", "inspect_complete", 0, 0);
    server_log_close(&log);
    return D_APP_EXIT_OK;
}

static int server_run_validate(const server_run_config* cfg,
                               const dom_app_compat_expect* expect,
                               const dom_control_caps* caps,
                               int caps_loaded)
{
    server_log log;
    dom_app_compat_report report;
    int ok;
    if (!cfg) {
        return D_APP_EXIT_FAILURE;
    }
    dom_app_compat_report_init(&report, "server");
    ok = dom_app_compat_check(expect, &report);
    if (!server_log_open(&log, cfg->log_path, cfg->log_rotate_max, cfg->log_max_bytes)) {
        fprintf(stderr, "server: failed to open log\n");
        return D_APP_EXIT_FAILURE;
    }
    server_log_emit(&log, "info", "server", "start", "validate", 0, 0);
    if (!cfg->compat_report_path[0] ||
        !server_write_compat_report_json(cfg->compat_report_path,
                                         "validate",
                                         cfg,
                                         &report,
                                         ok ? "full" : "refuse",
                                         ok ? 0 : 5,
                                         ok ? 0 : "REFUSE_INTEGRITY_VIOLATION")) {
        server_log_emit(&log, "error", "compat", "report_failed",
                        "compat_report write failed", 5, "REFUSE_INTEGRITY_VIOLATION");
        server_log_close(&log);
        return D_APP_EXIT_FAILURE;
    }
    if (ok) {
        server_log_emit(&log, "info", "compat", "ok", "compat_report ok", 0, 0);
    } else {
        server_log_emit(&log, "error", "compat", "failed", report.message,
                        5, "REFUSE_INTEGRITY_VIOLATION");
    }
    if (caps_loaded && caps) {
        server_log_control_caps(&log, caps);
    } else {
        server_log_emit(&log, "warn", "control_caps", "unavailable",
                        "control registry unavailable", 0, 0);
    }
    printf("validate_status=%s\n", ok ? "ok" : "failed");
    dom_app_compat_print_report(&report, stdout);
    server_log_emit(&log, "info", "server", "shutdown", "validate_complete", 0, 0);
    server_log_close(&log);
    return ok ? D_APP_EXIT_OK : D_APP_EXIT_UNAVAILABLE;
}

static int server_run_replay(const server_run_config* cfg,
                             const dom_app_compat_expect* expect,
                             const dom_control_caps* caps,
                             int caps_loaded,
                             const char* replay_path,
                             int step_index,
                             int max_steps,
                             int rewind,
                             int pause)
{
    server_log log;
    dom_app_compat_report report;
    int ok;
    int events = 0;
    int emit_all = 0;
    int step = step_index;
    int steps = max_steps;
    if (!cfg || !replay_path || !replay_path[0]) {
        fprintf(stderr, "server: replay path missing\n");
        return D_APP_EXIT_USAGE;
    }
    dom_app_compat_report_init(&report, "server");
    ok = dom_app_compat_check(expect, &report);
    if (!server_log_open(&log, cfg->log_path, cfg->log_rotate_max, cfg->log_max_bytes)) {
        fprintf(stderr, "server: failed to open log\n");
        return D_APP_EXIT_FAILURE;
    }
    server_log_emit(&log, "info", "server", "start", "replay", 0, 0);
    if (!cfg->compat_report_path[0] ||
        !server_write_compat_report_json(cfg->compat_report_path,
                                         "replay",
                                         cfg,
                                         &report,
                                         ok ? "inspect-only" : "refuse",
                                         ok ? 0 : 5,
                                         ok ? 0 : "REFUSE_INTEGRITY_VIOLATION")) {
        server_log_emit(&log, "error", "compat", "report_failed",
                        "compat_report write failed", 5, "REFUSE_INTEGRITY_VIOLATION");
        server_log_close(&log);
        return D_APP_EXIT_FAILURE;
    }
    if (!ok) {
        server_log_emit(&log, "error", "compat", "failed", report.message,
                        5, "REFUSE_INTEGRITY_VIOLATION");
        dom_app_compat_print_report(&report, stderr);
        server_log_close(&log);
        return D_APP_EXIT_UNAVAILABLE;
    }
    server_log_emit(&log, "info", "compat", "ok", "compat_report ok", 0, 0);
    if (caps_loaded && caps) {
        server_log_control_caps(&log, caps);
    } else {
        server_log_emit(&log, "warn", "control_caps", "unavailable",
                        "control registry unavailable", 0, 0);
    }
    if (pause) {
        printf("replay_paused=1\n");
        server_log_emit(&log, "info", "replay", "paused", "replay paused", 0, 0);
        server_log_close(&log);
        return D_APP_EXIT_OK;
    }
    if (rewind && step < 0) {
        step = 0;
    }
    if (step >= 0) {
        if (steps <= 0) {
            steps = 1;
        }
    } else {
        emit_all = 1;
    }
    if (!server_replay_scan(replay_path, step, steps, emit_all, &events)) {
        server_log_emit(&log, "error", "replay", "read_failed",
                        "replay scan failed", 1, "REFUSE_INVALID_INTENT");
        server_log_close(&log);
        return D_APP_EXIT_UNAVAILABLE;
    }
    printf("replay_events=%d\n", events);
    server_log_emit(&log, "info", "replay", "complete", "replay scan complete", 0, 0);
    server_log_close(&log);
    return D_APP_EXIT_OK;
}

static int server_run_tui(void)
{
    fprintf(stderr, "server: tui not implemented\n");
    return D_APP_EXIT_UNAVAILABLE;
}

static int server_run_gui(void)
{
    fprintf(stderr, "server: gui not implemented\n");
    return D_APP_EXIT_UNAVAILABLE;
}

typedef enum server_mode {
    SERVER_MODE_NONE = 0,
    SERVER_MODE_HEADLESS,
    SERVER_MODE_INSPECT,
    SERVER_MODE_VALIDATE,
    SERVER_MODE_REPLAY,
    SERVER_MODE_MP0_LOOPBACK,
    SERVER_MODE_MP0_SERVER_AUTH
} server_mode;

int server_main(int argc, char** argv)
{
    const char* control_registry_path = "data/registries/control_capabilities.registry";
    const char* control_enable = 0;
    const char* data_root_override = 0;
    const char* log_root_override = 0;
    const char* replay_out_override = 0;
    const char* compat_report_override = 0;
    const char* instance_override = 0;
    const char* replay_input = 0;
    int replay_step = -1;
    int replay_steps = 0;
    int replay_rewind = 0;
    int replay_pause = 0;
    int ticks_set = 0;
    int checkpoint_set = 0;
    int health_set = 0;
    int replay_out_set = 0;
    int no_replay_set = 0;
    int format_set = 0;
    int want_help = 0;
    int want_version = 0;
    int want_build_info = 0;
    int want_status = 0;
    int want_loopback = 0;
    int want_server_auth = 0;
    int want_smoke = 0;
    int want_selftest = 0;
    int want_deterministic = 0;
    int want_interactive = 0;
    dom_app_output_format output_format = DOM_APP_FORMAT_TEXT;
    dom_app_ui_request ui_req;
    dom_app_ui_mode ui_mode = DOM_APP_UI_NONE;
    dom_control_caps control_caps;
    dom_app_compat_expect compat_expect;
    server_run_config cfg;
    server_mode mode = SERVER_MODE_NONE;
    int control_loaded = 0;
    int i;
    server_config_init(&cfg);
    dom_app_compat_expect_init(&compat_expect);
    dom_app_ui_request_init(&ui_req);
    for (i = 1; i < argc; ++i) {
        int ui_consumed = 0;
        char ui_err[96];
        int ui_res = dom_app_parse_ui_arg(&ui_req,
                                          argv[i],
                                          (i + 1 < argc) ? argv[i + 1] : 0,
                                          &ui_consumed,
                                          ui_err,
                                          sizeof(ui_err));
        if (ui_res < 0) {
            fprintf(stderr, "server: %s\n", ui_err);
            return D_APP_EXIT_USAGE;
        }
        if (ui_res > 0) {
            i += ui_consumed - 1;
            continue;
        }
        if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            want_help = 1;
            continue;
        }
        if (strcmp(argv[i], "--version") == 0) {
            want_version = 1;
            continue;
        }
        if (strcmp(argv[i], "--build-info") == 0) {
            want_build_info = 1;
            continue;
        }
        if (strcmp(argv[i], "--status") == 0) {
            want_status = 1;
            continue;
        }
        if (strcmp(argv[i], "--headless") == 0) {
            if (mode != SERVER_MODE_NONE && mode != SERVER_MODE_HEADLESS) {
                fprintf(stderr, "server: multiple run modes specified\n");
                return D_APP_EXIT_USAGE;
            }
            mode = SERVER_MODE_HEADLESS;
            continue;
        }
        if (strcmp(argv[i], "--inspect") == 0) {
            if (mode != SERVER_MODE_NONE && mode != SERVER_MODE_INSPECT) {
                fprintf(stderr, "server: multiple run modes specified\n");
                return D_APP_EXIT_USAGE;
            }
            mode = SERVER_MODE_INSPECT;
            continue;
        }
        if (strcmp(argv[i], "--validate") == 0) {
            if (mode != SERVER_MODE_NONE && mode != SERVER_MODE_VALIDATE) {
                fprintf(stderr, "server: multiple run modes specified\n");
                return D_APP_EXIT_USAGE;
            }
            mode = SERVER_MODE_VALIDATE;
            continue;
        }
        if (strncmp(argv[i], "--replay=", 9) == 0) {
            if (mode != SERVER_MODE_NONE && mode != SERVER_MODE_REPLAY) {
                fprintf(stderr, "server: multiple run modes specified\n");
                return D_APP_EXIT_USAGE;
            }
            mode = SERVER_MODE_REPLAY;
            replay_input = argv[i] + 9;
            continue;
        }
        if (strcmp(argv[i], "--replay") == 0 && i + 1 < argc) {
            if (mode != SERVER_MODE_NONE && mode != SERVER_MODE_REPLAY) {
                fprintf(stderr, "server: multiple run modes specified\n");
                return D_APP_EXIT_USAGE;
            }
            mode = SERVER_MODE_REPLAY;
            replay_input = argv[i + 1];
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--replay-step=", 14) == 0) {
            int value = -1;
            if (!server_parse_int(argv[i] + 14, &value) || value < 0) {
                fprintf(stderr, "server: invalid --replay-step value\n");
                return D_APP_EXIT_USAGE;
            }
            replay_step = value;
            continue;
        }
        if (strcmp(argv[i], "--replay-step") == 0 && i + 1 < argc) {
            int value = -1;
            if (!server_parse_int(argv[i + 1], &value) || value < 0) {
                fprintf(stderr, "server: invalid --replay-step value\n");
                return D_APP_EXIT_USAGE;
            }
            replay_step = value;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--replay-steps=", 15) == 0) {
            int value = 0;
            if (!server_parse_int(argv[i] + 15, &value) || value <= 0) {
                fprintf(stderr, "server: invalid --replay-steps value\n");
                return D_APP_EXIT_USAGE;
            }
            replay_steps = value;
            continue;
        }
        if (strcmp(argv[i], "--replay-steps") == 0 && i + 1 < argc) {
            int value = 0;
            if (!server_parse_int(argv[i + 1], &value) || value <= 0) {
                fprintf(stderr, "server: invalid --replay-steps value\n");
                return D_APP_EXIT_USAGE;
            }
            replay_steps = value;
            i += 1;
            continue;
        }
        if (strcmp(argv[i], "--replay-rewind") == 0) {
            replay_rewind = 1;
            continue;
        }
        if (strcmp(argv[i], "--replay-pause") == 0) {
            replay_pause = 1;
            continue;
        }
        if (strncmp(argv[i], "--format=", 9) == 0) {
            if (!dom_app_parse_output_format(argv[i] + 9, &output_format)) {
                fprintf(stderr, "server: invalid --format value\n");
                return D_APP_EXIT_USAGE;
            }
            format_set = 1;
            continue;
        }
        if (strcmp(argv[i], "--format") == 0 && i + 1 < argc) {
            if (!dom_app_parse_output_format(argv[i + 1], &output_format)) {
                fprintf(stderr, "server: invalid --format value\n");
                return D_APP_EXIT_USAGE;
            }
            format_set = 1;
            i += 1;
            continue;
        }
        if (strcmp(argv[i], "--smoke") == 0) {
            want_smoke = 1;
            continue;
        }
        if (strcmp(argv[i], "--selftest") == 0) {
            want_selftest = 1;
            continue;
        }
        if (strcmp(argv[i], "--deterministic") == 0) {
            want_deterministic = 1;
            continue;
        }
        if (strcmp(argv[i], "--interactive") == 0) {
            want_interactive = 1;
            continue;
        }
        if (strncmp(argv[i], "--data-root=", 12) == 0) {
            data_root_override = argv[i] + 12;
            continue;
        }
        if (strcmp(argv[i], "--data-root") == 0 && i + 1 < argc) {
            data_root_override = argv[i + 1];
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--log-root=", 11) == 0) {
            log_root_override = argv[i] + 11;
            continue;
        }
        if (strcmp(argv[i], "--log-root") == 0 && i + 1 < argc) {
            log_root_override = argv[i + 1];
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--log-max-bytes=", 16) == 0) {
            uint32_t value = 0;
            if (!server_parse_u32(argv[i] + 16, &value)) {
                fprintf(stderr, "server: invalid --log-max-bytes value\n");
                return D_APP_EXIT_USAGE;
            }
            cfg.log_max_bytes = value;
            continue;
        }
        if (strcmp(argv[i], "--log-max-bytes") == 0 && i + 1 < argc) {
            uint32_t value = 0;
            if (!server_parse_u32(argv[i + 1], &value)) {
                fprintf(stderr, "server: invalid --log-max-bytes value\n");
                return D_APP_EXIT_USAGE;
            }
            cfg.log_max_bytes = value;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--log-rotate-max=", 17) == 0) {
            int value = 0;
            if (!server_parse_int(argv[i] + 17, &value) || value < 0) {
                fprintf(stderr, "server: invalid --log-rotate-max value\n");
                return D_APP_EXIT_USAGE;
            }
            cfg.log_rotate_max = value;
            continue;
        }
        if (strcmp(argv[i], "--log-rotate-max") == 0 && i + 1 < argc) {
            int value = 0;
            if (!server_parse_int(argv[i + 1], &value) || value < 0) {
                fprintf(stderr, "server: invalid --log-rotate-max value\n");
                return D_APP_EXIT_USAGE;
            }
            cfg.log_rotate_max = value;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--replay-out=", 13) == 0) {
            replay_out_override = argv[i] + 13;
            replay_out_set = 1;
            continue;
        }
        if (strcmp(argv[i], "--replay-out") == 0 && i + 1 < argc) {
            replay_out_override = argv[i + 1];
            replay_out_set = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--replay-rotate-max=", 20) == 0) {
            int value = 0;
            if (!server_parse_int(argv[i] + 20, &value) || value < 0) {
                fprintf(stderr, "server: invalid --replay-rotate-max value\n");
                return D_APP_EXIT_USAGE;
            }
            cfg.replay_rotate_max = value;
            continue;
        }
        if (strcmp(argv[i], "--replay-rotate-max") == 0 && i + 1 < argc) {
            int value = 0;
            if (!server_parse_int(argv[i + 1], &value) || value < 0) {
                fprintf(stderr, "server: invalid --replay-rotate-max value\n");
                return D_APP_EXIT_USAGE;
            }
            cfg.replay_rotate_max = value;
            i += 1;
            continue;
        }
        if (strcmp(argv[i], "--no-replay") == 0) {
            cfg.replay_enabled = 0;
            no_replay_set = 1;
            continue;
        }
        if (strncmp(argv[i], "--compat-report=", 16) == 0) {
            compat_report_override = argv[i] + 16;
            continue;
        }
        if (strcmp(argv[i], "--compat-report") == 0 && i + 1 < argc) {
            compat_report_override = argv[i + 1];
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--instance-id=", 14) == 0) {
            instance_override = argv[i] + 14;
            continue;
        }
        if (strcmp(argv[i], "--instance-id") == 0 && i + 1 < argc) {
            instance_override = argv[i + 1];
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--ticks=", 8) == 0) {
            uint32_t value = 0;
            if (!server_parse_u32(argv[i] + 8, &value)) {
                fprintf(stderr, "server: invalid --ticks value\n");
                return D_APP_EXIT_USAGE;
            }
            cfg.ticks = value;
            ticks_set = 1;
            continue;
        }
        if (strcmp(argv[i], "--ticks") == 0 && i + 1 < argc) {
            uint32_t value = 0;
            if (!server_parse_u32(argv[i + 1], &value)) {
                fprintf(stderr, "server: invalid --ticks value\n");
                return D_APP_EXIT_USAGE;
            }
            cfg.ticks = value;
            ticks_set = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--checkpoint-interval=", 23) == 0) {
            uint32_t value = 0;
            if (!server_parse_u32(argv[i] + 23, &value)) {
                fprintf(stderr, "server: invalid --checkpoint-interval value\n");
                return D_APP_EXIT_USAGE;
            }
            cfg.checkpoint_interval = value;
            checkpoint_set = 1;
            continue;
        }
        if (strcmp(argv[i], "--checkpoint-interval") == 0 && i + 1 < argc) {
            uint32_t value = 0;
            if (!server_parse_u32(argv[i + 1], &value)) {
                fprintf(stderr, "server: invalid --checkpoint-interval value\n");
                return D_APP_EXIT_USAGE;
            }
            cfg.checkpoint_interval = value;
            checkpoint_set = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--health-interval=", 18) == 0) {
            uint32_t value = 0;
            if (!server_parse_u32(argv[i] + 18, &value)) {
                fprintf(stderr, "server: invalid --health-interval value\n");
                return D_APP_EXIT_USAGE;
            }
            cfg.health_interval = value;
            health_set = 1;
            continue;
        }
        if (strcmp(argv[i], "--health-interval") == 0 && i + 1 < argc) {
            uint32_t value = 0;
            if (!server_parse_u32(argv[i + 1], &value)) {
                fprintf(stderr, "server: invalid --health-interval value\n");
                return D_APP_EXIT_USAGE;
            }
            cfg.health_interval = value;
            health_set = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-engine-version=", 24) == 0) {
            compat_expect.engine_version = argv[i] + 24;
            compat_expect.has_engine_version = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-engine-version") == 0 && i + 1 < argc) {
            compat_expect.engine_version = argv[i + 1];
            compat_expect.has_engine_version = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-game-version=", 22) == 0) {
            compat_expect.game_version = argv[i] + 22;
            compat_expect.has_game_version = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-game-version") == 0 && i + 1 < argc) {
            compat_expect.game_version = argv[i + 1];
            compat_expect.has_game_version = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-build-id=", 18) == 0) {
            compat_expect.build_id = argv[i] + 18;
            compat_expect.has_build_id = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-build-id") == 0 && i + 1 < argc) {
            compat_expect.build_id = argv[i + 1];
            compat_expect.has_build_id = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-sim-schema=", 21) == 0) {
            uint64_t value = 0;
            if (!server_parse_u64(argv[i] + 21, &value)) {
                fprintf(stderr, "server: invalid --expect-sim-schema value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.sim_schema_id = value;
            compat_expect.has_sim_schema_id = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-sim-schema") == 0 && i + 1 < argc) {
            uint64_t value = 0;
            if (!server_parse_u64(argv[i + 1], &value)) {
                fprintf(stderr, "server: invalid --expect-sim-schema value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.sim_schema_id = value;
            compat_expect.has_sim_schema_id = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-build-info-abi=", 25) == 0) {
            uint32_t value = 0;
            if (!server_parse_u32(argv[i] + 25, &value)) {
                fprintf(stderr, "server: invalid --expect-build-info-abi value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.build_info_abi = value;
            compat_expect.has_build_info_abi = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-build-info-abi") == 0 && i + 1 < argc) {
            uint32_t value = 0;
            if (!server_parse_u32(argv[i + 1], &value)) {
                fprintf(stderr, "server: invalid --expect-build-info-abi value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.build_info_abi = value;
            compat_expect.has_build_info_abi = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-caps-abi=", 19) == 0) {
            uint32_t value = 0;
            if (!server_parse_u32(argv[i] + 19, &value)) {
                fprintf(stderr, "server: invalid --expect-caps-abi value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.caps_abi = value;
            compat_expect.has_caps_abi = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-caps-abi") == 0 && i + 1 < argc) {
            uint32_t value = 0;
            if (!server_parse_u32(argv[i + 1], &value)) {
                fprintf(stderr, "server: invalid --expect-caps-abi value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.caps_abi = value;
            compat_expect.has_caps_abi = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-gfx-api=", 17) == 0) {
            uint32_t value = 0;
            if (!server_parse_u32(argv[i] + 17, &value)) {
                fprintf(stderr, "server: invalid --expect-gfx-api value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.gfx_api = value;
            compat_expect.has_gfx_api = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-gfx-api") == 0 && i + 1 < argc) {
            uint32_t value = 0;
            if (!server_parse_u32(argv[i + 1], &value)) {
                fprintf(stderr, "server: invalid --expect-gfx-api value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.gfx_api = value;
            compat_expect.has_gfx_api = 1;
            i += 1;
            continue;
        }
        if (strcmp(argv[i], "--control-registry") == 0 && i + 1 < argc) {
            control_registry_path = argv[i + 1];
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--control-enable=", 17) == 0) {
            control_enable = argv[i] + 17;
            continue;
        }
        if (strcmp(argv[i], "--control-enable") == 0 && i + 1 < argc) {
            control_enable = argv[i + 1];
            i += 1;
            continue;
        }
        if (strcmp(argv[i], "--mp0-loopback") == 0) {
            want_loopback = 1;
        }
        if (strcmp(argv[i], "--mp0-server-auth") == 0) {
            want_server_auth = 1;
        }
    }
    if (want_help) {
        print_help();
        return D_APP_EXIT_OK;
    }
    if (want_version) {
        print_version(DOMINIUM_GAME_VERSION);
        return D_APP_EXIT_OK;
    }
    ui_mode = dom_app_select_ui_mode(&ui_req, DOM_APP_UI_NONE);
    if (want_deterministic && want_interactive) {
        fprintf(stderr, "server: --deterministic and --interactive are mutually exclusive\n");
        return D_APP_EXIT_USAGE;
    }
    if ((want_smoke || want_selftest) && want_interactive) {
        fprintf(stderr, "server: --smoke requires deterministic mode\n");
        return D_APP_EXIT_USAGE;
    }
    if (want_smoke || want_selftest) {
        want_loopback = 1;
    }
    if (want_loopback) {
        if (mode != SERVER_MODE_NONE && mode != SERVER_MODE_MP0_LOOPBACK) {
            fprintf(stderr, "server: multiple run modes specified\n");
            return D_APP_EXIT_USAGE;
        }
        mode = SERVER_MODE_MP0_LOOPBACK;
    }
    if (want_server_auth) {
        if (mode != SERVER_MODE_NONE && mode != SERVER_MODE_MP0_SERVER_AUTH) {
            fprintf(stderr, "server: multiple run modes specified\n");
            return D_APP_EXIT_USAGE;
        }
        mode = SERVER_MODE_MP0_SERVER_AUTH;
    }
    if ((ui_mode == DOM_APP_UI_TUI || ui_mode == DOM_APP_UI_GUI) &&
        (want_build_info || want_status || mode != SERVER_MODE_NONE)) {
        fprintf(stderr, "server: --ui=%s cannot combine with CLI actions\n",
                dom_app_ui_mode_name(ui_mode));
        return D_APP_EXIT_USAGE;
    }
    if (control_enable || want_status) {
        if (dom_control_caps_init(&control_caps, control_registry_path) != DOM_CONTROL_OK) {
            fprintf(stderr, "server: failed to load control registry: %s\n", control_registry_path);
            return D_APP_EXIT_FAILURE;
        }
        control_loaded = 1;
        if (control_enable && enable_control_list(&control_caps, control_enable) != 0) {
            fprintf(stderr, "server: invalid control capability list\n");
            dom_control_caps_free(&control_caps);
            return D_APP_EXIT_USAGE;
        }
    } else if (want_build_info ||
               mode == SERVER_MODE_NONE ||
               mode == SERVER_MODE_HEADLESS ||
               mode == SERVER_MODE_INSPECT ||
               mode == SERVER_MODE_VALIDATE ||
               mode == SERVER_MODE_REPLAY) {
        if (dom_control_caps_init(&control_caps, control_registry_path) == DOM_CONTROL_OK) {
            control_loaded = 1;
        }
    }
    if (want_build_info) {
        print_build_info("server", DOMINIUM_GAME_VERSION);
        if (control_loaded) {
            print_control_caps(&control_caps);
            dom_control_caps_free(&control_caps);
        }
        return D_APP_EXIT_OK;
    }
    if (want_status) {
        if (!control_loaded) {
            fprintf(stderr, "server: failed to load control registry: %s\n", control_registry_path);
            return D_APP_EXIT_FAILURE;
        }
        print_control_caps(&control_caps);
        dom_control_caps_free(&control_caps);
        return D_APP_EXIT_OK;
    }
    if (ui_mode == DOM_APP_UI_TUI) {
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return server_run_tui();
    }
    if (ui_mode == DOM_APP_UI_GUI) {
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return server_run_gui();
    }
    if (mode == SERVER_MODE_MP0_LOOPBACK) {
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return mp0_run_loopback();
    }
    if (mode == SERVER_MODE_MP0_SERVER_AUTH) {
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return mp0_run_server_auth();
    }
    if (format_set && mode != SERVER_MODE_INSPECT) {
        fprintf(stderr, "server: --format only applies to --inspect\n");
        return D_APP_EXIT_USAGE;
    }
    if (mode == SERVER_MODE_NONE) {
        mode = SERVER_MODE_HEADLESS;
    }
    if (mode != SERVER_MODE_HEADLESS) {
        if (replay_out_set || no_replay_set || ticks_set || checkpoint_set || health_set) {
            fprintf(stderr, "server: headless-only options used with non-headless mode\n");
            return D_APP_EXIT_USAGE;
        }
    }
    if (mode != SERVER_MODE_REPLAY) {
        if (replay_step >= 0 || replay_steps > 0 || replay_rewind || replay_pause) {
            fprintf(stderr, "server: replay step/pause options require --replay\n");
            return D_APP_EXIT_USAGE;
        }
    }
    if (mode == SERVER_MODE_REPLAY && !replay_input) {
        fprintf(stderr, "server: --replay requires a file path\n");
        return D_APP_EXIT_USAGE;
    }
    if (replay_steps > 0 && replay_step < 0 && !replay_rewind) {
        fprintf(stderr, "server: --replay-steps requires --replay-step or --replay-rewind\n");
        return D_APP_EXIT_USAGE;
    }
    if (replay_pause && (replay_step >= 0 || replay_steps > 0 || replay_rewind)) {
        fprintf(stderr, "server: --replay-pause cannot combine with step/rewind\n");
        return D_APP_EXIT_USAGE;
    }
    if (want_deterministic) {
        cfg.deterministic = 1;
    } else if (want_interactive) {
        cfg.deterministic = 0;
    } else {
        cfg.deterministic = 1;
    }
    if (!server_build_paths(&cfg,
                            data_root_override,
                            log_root_override,
                            replay_out_override,
                            compat_report_override,
                            instance_override)) {
        fprintf(stderr, "server: failed to prepare data/log paths\n");
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return D_APP_EXIT_FAILURE;
    }
    if (mode == SERVER_MODE_HEADLESS) {
        int res = server_run_headless(&cfg, &compat_expect,
                                      control_loaded ? &control_caps : 0,
                                      control_loaded);
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return res;
    }
    if (mode == SERVER_MODE_INSPECT) {
        int res = server_run_inspect(&cfg, output_format, &compat_expect,
                                     control_loaded ? &control_caps : 0,
                                     control_loaded);
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return res;
    }
    if (mode == SERVER_MODE_VALIDATE) {
        int res = server_run_validate(&cfg, &compat_expect,
                                      control_loaded ? &control_caps : 0,
                                      control_loaded);
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return res;
    }
    if (mode == SERVER_MODE_REPLAY) {
        int res = server_run_replay(&cfg, &compat_expect,
                                    control_loaded ? &control_caps : 0,
                                    control_loaded,
                                    replay_input,
                                    replay_step,
                                    replay_steps,
                                    replay_rewind,
                                    replay_pause);
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return res;
    }
    printf("Dominium server stub. Use --help.\\n");
    if (control_loaded) {
        dom_control_caps_free(&control_caps);
    }
    return D_APP_EXIT_OK;
}

int main(int argc, char** argv)
{
    return server_main(argc, argv);
}
