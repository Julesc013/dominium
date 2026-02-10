#include "client_command_bridge.h"

#include <string.h>
#include <stdio.h>
#include <ctype.h>

typedef struct bridge_alias_t {
    const char* canonical;
    const char* legacy;
} bridge_alias;

static const bridge_alias k_aliases[] = {
    { "client.menu.select.singleplayer", "new-world" },
    { "client.menu.select.options", "settings" },
    { "client.menu.quit", "exit" },
    { "client.world.create", "create-world" },
    { "client.world.inspect", "where" },
    { "client.world.list", "load-world" },
    { "client.world.play", "load-world" },
    { "client.options.get", "settings" },
    { "client.options.set", "settings" },
    { "client.settings.get", "settings" },
    { "client.settings.set", "settings" },
    { "client.settings.reset", "settings-reset" },
    { "client.options.renderer.select", "renderer-next" },
    { "client.options.accessibility.set", "accessibility-next" },
    { "client.replay.list", "inspect-replay" },
    { "client.replay.inspect", "inspect-replay" },
    { "client.replay.export", "replay-save" },
    { "client.session.abort", "exit" }
};

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

static void parse_token(const char* raw_cmd, char* token, size_t token_cap, const char** out_remainder)
{
    const char* p = raw_cmd;
    size_t len = 0u;
    if (token && token_cap > 0u) {
        token[0] = '\0';
    }
    if (out_remainder) {
        *out_remainder = "";
    }
    if (!raw_cmd || !token || token_cap == 0u) {
        return;
    }
    while (*p && isspace((unsigned char)*p)) {
        p++;
    }
    while (p[len] && !isspace((unsigned char)p[len])) {
        len++;
    }
    if (len > (token_cap - 1u)) {
        len = token_cap - 1u;
    }
    memcpy(token, p, len);
    token[len] = '\0';
    p += len;
    while (*p && isspace((unsigned char)*p)) {
        p++;
    }
    if (out_remainder) {
        *out_remainder = p;
    }
}

static const char* lookup_alias(const char* token)
{
    u32 i;
    for (i = 0u; i < (u32)(sizeof(k_aliases) / sizeof(k_aliases[0])); ++i) {
        if (strcmp(token, k_aliases[i].canonical) == 0) {
            return k_aliases[i].legacy;
        }
    }
    return 0;
}

static void format_refusal(char* out_message,
                           size_t out_message_cap,
                           const char* refusal_code,
                           const char* command_id)
{
    if (!out_message || out_message_cap == 0u) {
        return;
    }
    snprintf(out_message,
             out_message_cap,
             "refusal=%s command=%s",
             refusal_code ? refusal_code : "REFUSE_UNAVAILABLE",
             command_id ? command_id : "");
}

client_command_bridge_result client_command_bridge_prepare(const char* raw_cmd,
                                                           char* out_cmd,
                                                           size_t out_cap,
                                                           char* out_message,
                                                           size_t out_message_cap,
                                                           const char* const* capability_ids,
                                                           u32 capability_count,
                                                           client_state_machine* state_machine)
{
    char token[128];
    const char* remainder = "";
    const char* legacy = 0;
    const client_command_desc* desc = 0;
    int machine_ok = 1;

    if (!out_cmd || out_cap == 0u) {
        return CLIENT_COMMAND_BRIDGE_NOT_CANONICAL;
    }
    out_cmd[0] = '\0';
    if (out_message && out_message_cap > 0u) {
        out_message[0] = '\0';
    }
    if (!raw_cmd || !raw_cmd[0]) {
        return CLIENT_COMMAND_BRIDGE_NOT_CANONICAL;
    }

    parse_token(raw_cmd, token, sizeof(token), &remainder);
    if (!starts_with(token, "client.")) {
        return CLIENT_COMMAND_BRIDGE_NOT_CANONICAL;
    }
    if (state_machine) {
        machine_ok = client_state_machine_apply(state_machine, token);
    }
    if (!machine_ok) {
        format_refusal(out_message,
                       out_message_cap,
                       state_machine ? client_state_machine_last_refusal(state_machine) : "REFUSE_INVALID_STATE",
                       token);
        return CLIENT_COMMAND_BRIDGE_REFUSED;
    }

    desc = client_command_find(token);
    if (!desc) {
        format_refusal(out_message, out_message_cap, "REFUSE_UNAVAILABLE", token);
        return CLIENT_COMMAND_BRIDGE_REFUSED;
    }
    if (!client_command_capabilities_allowed(desc, capability_ids, capability_count)) {
        format_refusal(out_message, out_message_cap, "REFUSE_CAPABILITY_MISSING", token);
        return CLIENT_COMMAND_BRIDGE_REFUSED;
    }

    if (strcmp(token, "client.boot.start") == 0 ||
        strcmp(token, "client.boot.progress_poll") == 0 ||
        strcmp(token, "client.menu.open") == 0) {
        snprintf(out_message, out_message_cap, "result=ok command=%s", token);
        return CLIENT_COMMAND_BRIDGE_SYNTHETIC_OK;
    }
    if (strcmp(token, "client.about.show") == 0 ||
        strcmp(token, "client.diag.show_build_identity") == 0 ||
        strcmp(token, "client.diag.show_lock_hash") == 0 ||
        strcmp(token, "client.diag.export_bugreport") == 0) {
        snprintf(out_message, out_message_cap, "result=ok command=%s", token);
        return CLIENT_COMMAND_BRIDGE_SYNTHETIC_OK;
    }
    if (starts_with(token, "client.session.")) {
        snprintf(out_message,
                 out_message_cap,
                 "result=ok command=%s stage=%s",
                 token,
                 client_state_machine_stage_name(state_machine));
        return CLIENT_COMMAND_BRIDGE_SYNTHETIC_OK;
    }
    if (starts_with(token, "client.server.") ||
        strcmp(token, "client.menu.select.multiplayer") == 0 ||
        strcmp(token, "client.world.modify") == 0 ||
        strcmp(token, "client.world.delete") == 0 ||
        strcmp(token, "client.options.network.set") == 0) {
        format_refusal(out_message, out_message_cap, "REFUSE_UNAVAILABLE", token);
        return CLIENT_COMMAND_BRIDGE_REFUSED;
    }

    legacy = lookup_alias(token);
    if (!legacy) {
        format_refusal(out_message, out_message_cap, "REFUSE_UNAVAILABLE", token);
        return CLIENT_COMMAND_BRIDGE_REFUSED;
    }

    if (remainder && remainder[0]) {
        snprintf(out_cmd, out_cap, "%s %s", legacy, remainder);
    } else {
        snprintf(out_cmd, out_cap, "%s", legacy);
    }
    return CLIENT_COMMAND_BRIDGE_REWRITTEN;
}
