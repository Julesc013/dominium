#include "client_command_bridge.h"

#include <string.h>
#include <stdio.h>
#include <ctype.h>

typedef struct bridge_alias_t {
    const char* canonical;
    const char* legacy;
} bridge_alias;

typedef struct bridge_profile_binding_t {
    const char* experience_id;
    const char* law_profile_id;
    int allow_hud;
    int allow_overlay;
    int allow_console_ro;
    int allow_console_rw;
    int allow_freecam;
    int watermark_observer;
} bridge_profile_binding;

typedef struct bridge_experience_bundle_t {
    const char* experience_id;
    const char* parameter_bundle_id;
} bridge_experience_bundle;

typedef struct bridge_selection_state_t {
    char experience_id[96];
    char law_profile_id[96];
    char authority_context_id[128];
    char scenario_id[96];
    char mission_id[96];
    char parameter_bundle_id[96];
    int allow_hud;
    int allow_overlay;
    int allow_console_ro;
    int allow_console_rw;
    int allow_freecam;
    int watermark_observer;
} bridge_selection_state;

static const bridge_alias k_aliases[] = {
    /* @repox:infrastructure_only Canonical command alias routing only. */
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
    { "client.settings.set", "settings-set" },
    { "client.settings.reset", "settings-reset" },
    { "client.options.renderer.select", "renderer-next" },
    { "client.options.accessibility.set", "accessibility-next" },
    { "client.replay.list", "inspect-replay" },
    { "client.replay.inspect", "inspect-replay" },
    { "client.replay.export", "replay-save" },
    { "client.session.abort", "exit" }
};

static const bridge_profile_binding k_profile_bindings[] = {
    { "exp.observer", "law.observer.default", 1, 1, 1, 0, 1, 1 },
    { "exp.survival", "law.survival.default", 1, 0, 0, 0, 0, 0 },
    { "exp.hardcore", "law.survival.hardcore", 1, 0, 0, 0, 0, 0 },
    { "exp.creative", "law.creative.full", 1, 1, 1, 1, 0, 1 },
    { "exp.lab", "law.lab.default", 1, 1, 1, 1, 0, 1 },
    { "exp.mission", "law.mission.player", 1, 0, 1, 0, 0, 0 },
    { "exp.survival.softcore", "survival.softcore", 1, 0, 0, 0, 0, 0 }
};

static const char* k_scenario_ids[] = {
    "scenario.sandbox.minimal",
    "scenario.sol.system.demo",
    "scenario.earth.surface.demo"
};

static const char* k_mission_ids[] = {
    "mission.learn_observer",
    "mission.compare_two_runs",
    "mission.run_ensemble"
};

static const char* k_parameter_bundle_ids[] = {
    "observer.params.default",
    "survival.params.default",
    "survival.params.harsh",
    "creative.params.default",
    "lab.params.default",
    "mission.params.default"
};

static const bridge_experience_bundle k_experience_parameter_defaults[] = {
    { "exp.observer", "observer.params.default" },
    { "exp.survival", "survival.params.default" },
    { "exp.survival.softcore", "survival.params.default" },
    { "exp.hardcore", "survival.params.harsh" },
    { "exp.creative", "creative.params.default" },
    { "exp.lab", "lab.params.default" },
    { "exp.mission", "mission.params.default" }
};

static bridge_selection_state g_selection = {
    "", "", "", "", "", "", 0, 0, 0, 0, 0, 0
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

static int value_in_list(const char* value, const char* const* ids, u32 count)
{
    u32 i;
    if (!value || !value[0] || !ids || count == 0u) {
        return 0;
    }
    for (i = 0u; i < count; ++i) {
        if (ids[i] && strcmp(ids[i], value) == 0) {
            return 1;
        }
    }
    return 0;
}

static const bridge_profile_binding* find_profile_binding(const char* experience_id)
{
    u32 i;
    if (!experience_id || !experience_id[0]) {
        return 0;
    }
    for (i = 0u; i < (u32)(sizeof(k_profile_bindings) / sizeof(k_profile_bindings[0])); ++i) {
        if (strcmp(k_profile_bindings[i].experience_id, experience_id) == 0) {
            return &k_profile_bindings[i];
        }
    }
    return 0;
}

static void set_selection_id(char* out, size_t cap, const char* value)
{
    copy_text(out, cap, value);
}

static void parse_selection_value(const char* remainder, char* out, size_t out_cap)
{
    const char* p = remainder;
    size_t len = 0u;
    if (!out || out_cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (!p) {
        return;
    }
    while (*p && isspace((unsigned char)*p)) {
        p++;
    }
    if (!*p) {
        return;
    }
    while (p[len] && !isspace((unsigned char)p[len])) {
        len++;
    }
    if (len == 0u) {
        return;
    }
    if (len >= out_cap) {
        len = out_cap - 1u;
    }
    memcpy(out, p, len);
    out[len] = '\0';
    p = strchr(out, '=');
    if (p && p[1]) {
        const char* value = p + 1;
        memmove(out, value, strlen(value) + 1u);
    }
}

static void apply_profile_binding(const bridge_profile_binding* binding)
{
    const char* exp = "";
    const char* law = "";
    if (!binding) {
        return;
    }
    exp = binding->experience_id ? binding->experience_id : "";
    law = binding->law_profile_id ? binding->law_profile_id : "";
    set_selection_id(g_selection.experience_id, sizeof(g_selection.experience_id), exp);
    set_selection_id(g_selection.law_profile_id, sizeof(g_selection.law_profile_id), law);
    snprintf(g_selection.authority_context_id,
             sizeof(g_selection.authority_context_id),
             "ctx.%s.%s",
             exp[0] ? exp : "unknown",
             law[0] ? law : "unknown");
    g_selection.authority_context_id[sizeof(g_selection.authority_context_id) - 1u] = '\0';
    g_selection.allow_hud = binding->allow_hud;
    g_selection.allow_overlay = binding->allow_overlay;
    g_selection.allow_console_ro = binding->allow_console_ro;
    g_selection.allow_console_rw = binding->allow_console_rw;
    g_selection.allow_freecam = binding->allow_freecam;
    g_selection.watermark_observer = binding->watermark_observer;
}

static const char* default_parameter_bundle_for_experience(const char* experience_id)
{
    size_t i = 0u;
    if (!experience_id || !experience_id[0]) {
        return "";
    }
    for (i = 0u; i < (sizeof(k_experience_parameter_defaults) / sizeof(k_experience_parameter_defaults[0])); ++i) {
        if (strcmp(experience_id, k_experience_parameter_defaults[i].experience_id) == 0) {
            return k_experience_parameter_defaults[i].parameter_bundle_id;
        }
    }
    return "";
}

static int profile_selected(void)
{
    return g_selection.experience_id[0] != '\0' ? 1 : 0;
}

static int entitlement_allowed(const char* token)
{
    if (!token || !token[0]) {
        return 0;
    }
    if (strcmp(token, "client.ui.hud.show") == 0) {
        return g_selection.allow_hud;
    }
    if (strcmp(token, "client.ui.overlay.world_layers.show") == 0) {
        return g_selection.allow_overlay;
    }
    if (strcmp(token, "client.console.open") == 0) {
        return g_selection.allow_console_ro || g_selection.allow_console_rw;
    }
    if (strcmp(token, "client.console.open.readwrite") == 0) {
        return g_selection.allow_console_rw;
    }
    if (strcmp(token, "client.camera.freecam.enable") == 0) {
        return g_selection.allow_freecam;
    }
    return 0;
}

static void set_default_scenario_if_missing(void)
{
    if (!g_selection.scenario_id[0]) {
        set_selection_id(g_selection.scenario_id,
                         sizeof(g_selection.scenario_id),
                         k_scenario_ids[0]);
    }
}

static void set_default_parameter_if_missing(void)
{
    const char* default_id = "";
    if (g_selection.parameter_bundle_id[0]) {
        return;
    }
    default_id = default_parameter_bundle_for_experience(g_selection.experience_id);
    if (default_id && default_id[0]) {
        set_selection_id(g_selection.parameter_bundle_id,
                         sizeof(g_selection.parameter_bundle_id),
                         default_id);
    }
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
    if (strcmp(token, "client.play.open") == 0) {
        snprintf(out_message,
                 out_message_cap,
                 "result=ok command=%s workspaces=play_selector,scenario_selector,mission_selector",
                 token);
        return CLIENT_COMMAND_BRIDGE_SYNTHETIC_OK;
    }
    if (strcmp(token, "client.experience.list") == 0) {
        snprintf(out_message,
                 out_message_cap,
                 "result=ok command=%s experiences=exp.observer,exp.survival,exp.hardcore,exp.creative,exp.lab,exp.mission,exp.survival.softcore",
                 token);
        return CLIENT_COMMAND_BRIDGE_SYNTHETIC_OK;
    }
    if (strcmp(token, "client.experience.select") == 0) {
        char value[128];
        const bridge_profile_binding* binding = 0;
        parse_selection_value(remainder, value, sizeof(value));
        binding = find_profile_binding(value);
        if (!binding) {
            format_refusal(out_message, out_message_cap, "refuse.profile_unknown", token);
            return CLIENT_COMMAND_BRIDGE_REFUSED;
        }
        apply_profile_binding(binding);
        set_selection_id(g_selection.parameter_bundle_id,
                         sizeof(g_selection.parameter_bundle_id),
                         default_parameter_bundle_for_experience(binding->experience_id));
        snprintf(out_message,
                 out_message_cap,
                 "result=ok command=%s experience_id=%s law_profile_id=%s authority_context_id=%s watermark=%s",
                 token,
                 g_selection.experience_id,
                 g_selection.law_profile_id,
                 g_selection.authority_context_id,
                 g_selection.watermark_observer ? "OBSERVER MODE" : "none");
        return CLIENT_COMMAND_BRIDGE_SYNTHETIC_OK;
    }
    if (strcmp(token, "client.scenario.list") == 0) {
        snprintf(out_message,
                 out_message_cap,
                 "result=ok command=%s scenarios=scenario.sandbox.minimal,scenario.sol.system.demo,scenario.earth.surface.demo",
                 token);
        return CLIENT_COMMAND_BRIDGE_SYNTHETIC_OK;
    }
    if (strcmp(token, "client.scenario.select") == 0) {
        char value[128];
        parse_selection_value(remainder, value, sizeof(value));
        if (!value_in_list(value,
                           k_scenario_ids,
                           (u32)(sizeof(k_scenario_ids) / sizeof(k_scenario_ids[0])))) {
            format_refusal(out_message, out_message_cap, "refuse.scenario_unknown", token);
            return CLIENT_COMMAND_BRIDGE_REFUSED;
        }
        set_selection_id(g_selection.scenario_id, sizeof(g_selection.scenario_id), value);
        snprintf(out_message,
                 out_message_cap,
                 "result=ok command=%s scenario_id=%s",
                 token,
                 g_selection.scenario_id);
        return CLIENT_COMMAND_BRIDGE_SYNTHETIC_OK;
    }
    if (strcmp(token, "client.mission.list") == 0) {
        snprintf(out_message,
                 out_message_cap,
                 "result=ok command=%s missions=mission.learn_observer,mission.compare_two_runs,mission.run_ensemble",
                 token);
        return CLIENT_COMMAND_BRIDGE_SYNTHETIC_OK;
    }
    if (strcmp(token, "client.mission.select") == 0) {
        char value[128];
        parse_selection_value(remainder, value, sizeof(value));
        if (!value_in_list(value,
                           k_mission_ids,
                           (u32)(sizeof(k_mission_ids) / sizeof(k_mission_ids[0])))) {
            format_refusal(out_message, out_message_cap, "refuse.mission_unknown", token);
            return CLIENT_COMMAND_BRIDGE_REFUSED;
        }
        set_selection_id(g_selection.mission_id, sizeof(g_selection.mission_id), value);
        snprintf(out_message,
                 out_message_cap,
                 "result=ok command=%s mission_id=%s",
                 token,
                 g_selection.mission_id);
        return CLIENT_COMMAND_BRIDGE_SYNTHETIC_OK;
    }
    if (strcmp(token, "client.parameters.list") == 0) {
        snprintf(out_message,
                 out_message_cap,
                 "result=ok command=%s bundles=observer.params.default,survival.params.default,survival.params.harsh,creative.params.default,lab.params.default,mission.params.default",
                 token);
        return CLIENT_COMMAND_BRIDGE_SYNTHETIC_OK;
    }
    if (strcmp(token, "client.parameters.select") == 0) {
        char value[128];
        parse_selection_value(remainder, value, sizeof(value));
        if (!value_in_list(value,
                           k_parameter_bundle_ids,
                           (u32)(sizeof(k_parameter_bundle_ids) / sizeof(k_parameter_bundle_ids[0])))) {
            format_refusal(out_message, out_message_cap, "refuse.parameter_unknown", token);
            return CLIENT_COMMAND_BRIDGE_REFUSED;
        }
        set_selection_id(g_selection.parameter_bundle_id, sizeof(g_selection.parameter_bundle_id), value);
        snprintf(out_message,
                 out_message_cap,
                 "result=ok command=%s parameter_bundle_id=%s",
                 token,
                 g_selection.parameter_bundle_id);
        return CLIENT_COMMAND_BRIDGE_SYNTHETIC_OK;
    }
    if (strcmp(token, "client.session.create_from_selection") == 0) {
        const char* scenario_id = "";
        const char* parameter_bundle_id = "";
        const char* mission_id = "";
        if (!profile_selected()) {
            format_refusal(out_message, out_message_cap, "refuse.profile_not_selected", token);
            return CLIENT_COMMAND_BRIDGE_REFUSED;
        }
        set_default_scenario_if_missing();
        set_default_parameter_if_missing();
        scenario_id = g_selection.scenario_id[0] ? g_selection.scenario_id : "scenario.sandbox.minimal";
        parameter_bundle_id = g_selection.parameter_bundle_id[0] ? g_selection.parameter_bundle_id : "observer.params.default";
        mission_id = g_selection.mission_id[0] ? g_selection.mission_id : "none";
        snprintf(out_message,
                 out_message_cap,
                 "result=ok command=%s session_id=session.selected universe_id=universe.default save_id=none scenario_id=%s mission_id=%s experience_id=%s law_profile_id=%s parameter_bundle_id=%s pack_lock_hash=hash.unset authority_context_id=%s budget_policy_id=budget.dev.generous fidelity_policy_id=fidelity.default replay_policy=recording_disabled seed_bundle=seed.session.root workspace_id=ws.unset",
                 token,
                 scenario_id,
                 mission_id,
                 g_selection.experience_id,
                 g_selection.law_profile_id,
                 parameter_bundle_id,
                 g_selection.authority_context_id);
        return CLIENT_COMMAND_BRIDGE_SYNTHETIC_OK;
    }
    if (strcmp(token, "client.ui.hud.show") == 0 ||
        strcmp(token, "client.ui.overlay.world_layers.show") == 0 ||
        strcmp(token, "client.console.open") == 0 ||
        strcmp(token, "client.console.open.readwrite") == 0 ||
        strcmp(token, "client.camera.freecam.enable") == 0) {
        if (!profile_selected()) {
            format_refusal(out_message, out_message_cap, "refuse.profile_not_selected", token);
            return CLIENT_COMMAND_BRIDGE_REFUSED;
        }
        if (!entitlement_allowed(token)) {
            format_refusal(out_message, out_message_cap, "refuse.entitlement_required", token);
            return CLIENT_COMMAND_BRIDGE_REFUSED;
        }
        snprintf(out_message,
                 out_message_cap,
                 "result=ok command=%s experience_id=%s authority_context_id=%s watermark=%s",
                 token,
                 g_selection.experience_id,
                 g_selection.authority_context_id,
                 g_selection.watermark_observer ? "OBSERVER MODE" : "none");
        return CLIENT_COMMAND_BRIDGE_SYNTHETIC_OK;
    }
    if (starts_with(token, "client.session.")) {
        const char* warmup_sim = state_machine ? client_state_machine_warmup_simulation_step(state_machine) : "";
        const char* warmup_present = state_machine ? client_state_machine_warmup_presentation_step(state_machine) : "";
        int time_advanced = state_machine ? client_state_machine_simulation_time_advanced(state_machine) : 0;
        int world_ready = state_machine ? client_state_machine_world_ready(state_machine) : 0;
        int camera_placed = state_machine ? client_state_machine_camera_placed(state_machine) : 0;
        int actions_executed = state_machine ? client_state_machine_agent_actions_executed(state_machine) : 0;
        int map_open = state_machine ? client_state_machine_map_open(state_machine) : 0;
        int stats_visible = state_machine ? client_state_machine_stats_visible(state_machine) : 0;
        int replay_recording = state_machine ? client_state_machine_replay_recording_enabled(state_machine) : 0;
        snprintf(out_message,
                 out_message_cap,
                 "result=ok command=%s stage=%s workspace=session_transition authority_context_id=%s warmup.sim=%s warmup.presentation=%s time_advanced=%d world_ready=%d camera_placed=%d agent_actions_executed=%d map_open=%d stats_visible=%d replay_recording=%d",
                 token,
                 client_state_machine_stage_name(state_machine),
                 g_selection.authority_context_id[0] ? g_selection.authority_context_id : "ctx.unset",
                 warmup_sim,
                 warmup_present,
                 time_advanced,
                 world_ready,
                 camera_placed,
                 actions_executed,
                 map_open,
                 stats_visible,
                 replay_recording);
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
