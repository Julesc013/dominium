#include "client_commands_registry.h"

#include <string.h>

static const char* k_caps_none[] = { 0 };
static const char* k_caps_blueprint_place[] = { "ui.blueprint.place" };
static const char* k_caps_tool_observation[] = { "tool.observation.stream" };
static const char* k_caps_tool_memory[] = { "tool.memory.read" };
static const char* k_refusal_common[] = {
    "ok",
    "usage",
    "REFUSE_CAPABILITY_MISSING",
    "REFUSE_INVALID_STATE",
    "REFUSE_UNAVAILABLE"
};
static const char* k_refusal_world[] = {
    "ok",
    "usage",
    "REFUSE_WORLD_NOT_FOUND",
    "REFUSE_WORLD_INCOMPATIBLE",
    "REFUSE_CAPABILITY_MISSING"
};
static const char* k_refusal_server[] = {
    "ok",
    "usage",
    "REFUSE_PROVIDER_UNAVAILABLE",
    "REFUSE_SERVER_INCOMPATIBLE",
    "REFUSE_NETWORK_UNAVAILABLE"
};

static const client_command_desc k_commands[] = {
    { "client.boot.start", k_caps_none, 0u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.boot.progress_poll", k_caps_none, 0u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },

    { "client.menu.open", k_caps_none, 0u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.menu.select.singleplayer", k_caps_none, 0u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.menu.select.multiplayer", k_caps_tool_observation, 1u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.menu.select.options", k_caps_none, 0u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.menu.select.about", k_caps_none, 0u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.menu.quit", k_caps_none, 0u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },

    { "client.world.list", k_caps_none, 0u, "partial", k_refusal_world, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.world.create", k_caps_none, 0u, "partial", k_refusal_world, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.world.inspect", k_caps_none, 0u, "partial", k_refusal_world, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.world.modify", k_caps_blueprint_place, 1u, "partial", k_refusal_world, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.world.delete", k_caps_blueprint_place, 1u, "partial", k_refusal_world, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.world.play", k_caps_blueprint_place, 1u, "partial", k_refusal_world, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },

    { "client.server.list", k_caps_tool_observation, 1u, "partial", k_refusal_server, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.server.add_manual", k_caps_tool_observation, 1u, "partial", k_refusal_server, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.server.refresh", k_caps_tool_observation, 1u, "partial", k_refusal_server, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.server.connect", k_caps_tool_observation, 1u, "partial", k_refusal_server, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },

    { "client.options.get", k_caps_none, 0u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.options.set", k_caps_none, 0u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.settings.get", k_caps_none, 0u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.settings.set", k_caps_none, 0u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.settings.reset", k_caps_none, 0u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.options.renderer.select", k_caps_none, 0u, "obs_only", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.options.accessibility.set", k_caps_none, 0u, "obs_only", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.options.network.set", k_caps_tool_observation, 1u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },

    { "client.about.show", k_caps_none, 0u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.diag.show_build_identity", k_caps_none, 0u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.diag.show_lock_hash", k_caps_none, 0u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.diag.export_bugreport", k_caps_tool_memory, 1u, "partial", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },

    { "client.replay.list", k_caps_tool_memory, 1u, "memory_only", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.replay.inspect", k_caps_tool_memory, 1u, "memory_only", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI },
    { "client.replay.export", k_caps_tool_memory, 1u, "memory_only", k_refusal_common, 5u,
      CLIENT_CMD_MODE_CLI | CLIENT_CMD_MODE_TUI | CLIENT_CMD_MODE_GUI }
};

const client_command_desc* client_command_registry(u32* out_count)
{
    if (out_count) {
        *out_count = (u32)(sizeof(k_commands) / sizeof(k_commands[0]));
    }
    return k_commands;
}

const client_command_desc* client_command_find(const char* command_id)
{
    u32 count = 0u;
    u32 i = 0u;
    const client_command_desc* cmds = client_command_registry(&count);
    if (!command_id || !command_id[0]) {
        return 0;
    }
    for (i = 0u; i < count; ++i) {
        if (strcmp(cmds[i].command_id, command_id) == 0) {
            return &cmds[i];
        }
    }
    return 0;
}

int client_command_mode_available(const client_command_desc* cmd, const char* mode_id)
{
    u32 bit = 0u;
    if (!cmd || !mode_id || !mode_id[0]) {
        return 0;
    }
    if (strcmp(mode_id, "cli") == 0) {
        bit = CLIENT_CMD_MODE_CLI;
    } else if (strcmp(mode_id, "tui") == 0) {
        bit = CLIENT_CMD_MODE_TUI;
    } else if (strcmp(mode_id, "gui") == 0) {
        bit = CLIENT_CMD_MODE_GUI;
    }
    if (bit == 0u) {
        return 0;
    }
    return (cmd->mode_mask & bit) != 0u ? 1 : 0;
}

int client_command_capabilities_allowed(const client_command_desc* cmd,
                                        const char* const* capability_ids,
                                        u32 capability_count)
{
    u32 i;
    if (!cmd) {
        return 0;
    }
    if (!cmd->required_capabilities || cmd->required_capability_count == 0u) {
        return 1;
    }
    if (!capability_ids || capability_count == 0u) {
        return 0;
    }
    for (i = 0u; i < cmd->required_capability_count; ++i) {
        const char* required = cmd->required_capabilities[i];
        u32 j = 0u;
        int found = 0;
        for (j = 0u; j < capability_count; ++j) {
            if (capability_ids[j] && strcmp(required, capability_ids[j]) == 0) {
                found = 1;
                break;
            }
        }
        if (!found) {
            return 0;
        }
    }
    return 1;
}
