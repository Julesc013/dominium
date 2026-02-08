/*
FILE: libs/appcore/command/command_registry.c
MODULE: Dominium
PURPOSE: Canonical application command registry (data-only descriptors).
NOTES: CLI is canonical; GUI binds to this registry.
*/
#include "command_registry.h"
#include <string.h>

static const char* k_failure_common[] = { "ok", "usage", "failure", "unavailable" };
static const int k_exit_common[] = { 0, 1, 2, 3 };
static const char* k_required_caps_none[] = { 0 };
static const char* k_cap_world_life_nonintelligent[] = { "dominium.capability.world.life.nonintelligent" };
static const char* k_cap_world_life_intelligent[] = { "dominium.capability.world.life.intelligent" };
static const char* k_cap_society_institutions[] = { "dominium.capability.society.institutions" };
static const char* k_cap_infrastructure_industry[] = { "dominium.capability.infrastructure.industry" };
static const char* k_cap_future_affordances[] = { "dominium.capability.future.affordances" };

static const dom_app_command_desc k_commands[] = {
    { DOM_APP_CMD_LAUNCHER_VERSION, "version", "launcher", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_LIST_PROFILES, "list-profiles", "launcher", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_CAPABILITIES, "capabilities", "launcher", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_NEW_WORLD, "new-world", "launcher", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_LOAD_WORLD, "load-world", "launcher", DOM_APP_ARG_SCHEMA_PATH,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_INSPECT_REPLAY, "inspect-replay", "launcher", DOM_APP_ARG_SCHEMA_PATH,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_INSTALLS, "installs", "launcher", DOM_APP_ARG_SCHEMA_SUBCOMMAND,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_INSTANCES, "instances", "launcher", DOM_APP_ARG_SCHEMA_SUBCOMMAND,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_PROFILES, "profiles", "launcher", DOM_APP_ARG_SCHEMA_SUBCOMMAND,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_PREFLIGHT, "preflight", "launcher", DOM_APP_ARG_SCHEMA_SUBCOMMAND,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_RUN, "run", "launcher", DOM_APP_ARG_SCHEMA_SUBCOMMAND,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_PACKS, "packs", "launcher", DOM_APP_ARG_SCHEMA_SUBCOMMAND,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_BUNDLES, "bundles", "launcher", DOM_APP_ARG_SCHEMA_SUBCOMMAND,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_PATHS, "paths", "launcher", DOM_APP_ARG_SCHEMA_SUBCOMMAND,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_OPS, "ops", "launcher", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_SHARE, "share", "launcher", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_BUGREPORT, "bugreport", "launcher", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_TOOLS, "tools", "launcher", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_SETTINGS, "settings", "launcher", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_EXIT, "exit", "launcher", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },

    { DOM_APP_CMD_SETUP_VERSION, "version", "setup", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_STATUS, "status", "setup", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_PREPARE, "prepare", "setup", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_INSTALL, "install", "setup", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_REPAIR, "repair", "setup", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_UNINSTALL, "uninstall", "setup", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_ROLLBACK, "rollback", "setup", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_EXPORT_INVOCATION, "export-invocation", "setup", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_PLAN, "plan", "setup", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_APPLY, "apply", "setup", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_DETECT, "detect", "setup", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_MANIFEST, "manifest", "setup", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_OPS, "ops", "setup", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_SHARE, "share", "setup", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },

    { DOM_APP_CMD_CLIENT_NEW_WORLD, "new-world", "client", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_CREATE_WORLD, "create-world", "client", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_LOAD_WORLD, "load-world", "client", DOM_APP_ARG_SCHEMA_PATH,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_SCENARIO_LOAD, "scenario-load", "client", DOM_APP_ARG_SCHEMA_PATH,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_INSPECT_REPLAY, "inspect-replay", "client", DOM_APP_ARG_SCHEMA_PATH,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_SAVE, "save", "client", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_REPLAY_SAVE, "replay-save", "client", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_PROFILE_NEXT, "profile-next", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_PROFILE_PREV, "profile-prev", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_PRESET_NEXT, "preset-next", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_PRESET_PREV, "preset-prev", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_ACCESSIBILITY_NEXT, "accessibility-next", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_KEYBIND_NEXT, "keybind-next", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_REPLAY_STEP, "replay-step", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_REPLAY_REWIND, "replay-rewind", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_REPLAY_PAUSE, "replay-pause", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_TEMPLATES, "templates", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_MODE, "mode", "client", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_MOVE, "move", "client", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_SPAWN, "spawn", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_CAMERA, "camera", "client", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_CAMERA_NEXT, "camera-next", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_INSPECT_TOGGLE, "inspect-toggle", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_HUD_TOGGLE, "hud-toggle", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_DOMAIN, "domain", "client", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_WHERE, "where", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_SIMULATE, "simulate", "client", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_AGENTS, "agents", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_cap_world_life_nonintelligent, 1u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_AGENT_ADD, "agent-add", "client", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_cap_world_life_intelligent, 1u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_GOALS, "goals", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_GOAL_ADD, "goal-add", "client", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_DELEGATE, "delegate", "client", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_DELEGATIONS, "delegations", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_AUTHORITY_GRANT, "authority-grant", "client", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_AUTHORITY_LIST, "authority-list", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_CONSTRAINT_ADD, "constraint-add", "client", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_CONSTRAINT_LIST, "constraint-list", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_INSTITUTION_CREATE, "institution-create", "client", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_cap_society_institutions, 1u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_INSTITUTION_LIST, "institution-list", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_cap_society_institutions, 1u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_NETWORK_CREATE, "network-create", "client", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_cap_infrastructure_industry, 1u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_NETWORK_LIST, "network-list", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_cap_infrastructure_industry, 1u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_TOOLS, "tools", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_SETTINGS, "settings", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_EXIT, "exit", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },

    { DOM_APP_CMD_TOOLS_INSPECT, "inspect", "tools", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_FULL },
    { DOM_APP_CMD_TOOLS_VALIDATE, "validate", "tools", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_REPLAY, "replay", "tools", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_FULL },
    { DOM_APP_CMD_TOOLS_NEW_WORLD, "new-world", "tools", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_LOAD_WORLD, "load-world", "tools", DOM_APP_ARG_SCHEMA_PATH,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_INSPECT_REPLAY, "inspect-replay", "tools", DOM_APP_ARG_SCHEMA_PATH,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_SNAPSHOT_VIEWER, "snapshot-viewer", "tools", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_TOOLS_MENU, "tools", "tools", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_SETTINGS, "settings", "tools", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_WORLD_INSPECTOR, "world-inspector", "tools", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_HISTORY_VIEWER, "history-viewer", "tools", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_TEMPLATE_TOOLS, "template-tools", "tools", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_PACK_INSPECTOR, "pack-inspector", "tools", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_WORLDDEF, "worlddef", "tools", DOM_APP_ARG_SCHEMA_SUBCOMMAND,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_SCALE, "scale", "tools", DOM_APP_ARG_SCHEMA_SUBCOMMAND,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_MMO, "mmo", "tools", DOM_APP_ARG_SCHEMA_SUBCOMMAND,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_OPS, "ops", "tools", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_AI, "ai", "tools", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_cap_future_affordances, 1u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_SHARE, "share", "tools", DOM_APP_ARG_SCHEMA_ARGS,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOLS_EXIT, "exit", "tools", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },

    { DOM_APP_CMD_LAUNCHER_UI_NAV_PLAY, "launcher.nav.play", "launcher", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_UI_NAV_INSTANCES, "launcher.nav.instances", "launcher", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_UI_NAV_SETTINGS, "launcher.nav.settings", "launcher", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_UI_NAV_MODS, "launcher.nav.mods", "launcher", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_UI_INSTANCES_SELECT, "launcher.instances.select", "launcher", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_UI_INSTANCES_PLAY_SELECTED, "launcher.instances.play_selected", "launcher",
      DOM_APP_ARG_SCHEMA_NONE, k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_UI_INSTANCES_EDIT_SELECTED, "launcher.instances.edit_selected", "launcher",
      DOM_APP_ARG_SCHEMA_NONE, k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_UI_INSTANCES_DELETE_SELECTED, "launcher.instances.delete_selected", "launcher",
      DOM_APP_ARG_SCHEMA_NONE, k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_LAUNCHER_UI_SETTINGS_APPLY, "launcher.settings.apply", "launcher", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },

    { DOM_APP_CMD_SETUP_UI_BROWSE_PATH, "setup.browse_path", "setup", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_UI_OPTIONS_CHANGED, "setup.options.changed", "setup", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_UI_NAV_BACK, "setup.nav.back", "setup", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_UI_NAV_NEXT, "setup.nav.next", "setup", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_UI_NAV_INSTALL, "setup.nav.install", "setup", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_UI_NAV_FINISH, "setup.nav.finish", "setup", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SETUP_UI_NAV_CANCEL, "setup.nav.cancel", "setup", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },

    { DOM_APP_CMD_TOOL_EDITOR_UI_TAB_CHANGE, "tool_editor.tab_change", "tools", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOL_EDITOR_UI_NEW, "tool_editor.new", "tools", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOL_EDITOR_UI_OPEN, "tool_editor.open", "tools", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOL_EDITOR_UI_SAVE, "tool_editor.save", "tools", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOL_EDITOR_UI_SAVE_AS, "tool_editor.save_as", "tools", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOL_EDITOR_UI_VALIDATE, "tool_editor.validate", "tools", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOL_EDITOR_UI_ADD_WIDGET, "tool_editor.add_widget", "tools", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOL_EDITOR_UI_DELETE_WIDGET, "tool_editor.delete_widget", "tools", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOL_EDITOR_UI_HIERARCHY_SELECT, "tool_editor.hierarchy_select", "tools",
      DOM_APP_ARG_SCHEMA_NONE, k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOL_EDITOR_UI_PROP_NAME, "tool_editor.prop_name", "tools", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOL_EDITOR_UI_PROP_X, "tool_editor.prop_x", "tools", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOL_EDITOR_UI_PROP_Y, "tool_editor.prop_y", "tools", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOL_EDITOR_UI_PROP_W, "tool_editor.prop_w", "tools", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_TOOL_EDITOR_UI_PROP_H, "tool_editor.prop_h", "tools", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_CLIENT_UI_NAV_PLAY, "client.ui.nav.play", "client", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL },
    { DOM_APP_CMD_SERVER_UI_STATUS, "ops.server.status", "server", DOM_APP_ARG_SCHEMA_NONE,
      k_failure_common, 4u, k_exit_common, 4u, k_required_caps_none, 0u, DOM_EPISTEMIC_SCOPE_PARTIAL }
};

const dom_app_command_desc* appcore_command_registry(u32* out_count)
{
    if (out_count) {
        *out_count = (u32)(sizeof(k_commands) / sizeof(k_commands[0]));
    }
    return k_commands;
}

const dom_app_command_desc* appcore_command_find(const char* name)
{
    u32 count = 0u;
    u32 i;
    const dom_app_command_desc* cmds = appcore_command_registry(&count);
    if (!name || !cmds) {
        return 0;
    }
    for (i = 0u; i < count; ++i) {
        if (cmds[i].name && strcmp(cmds[i].name, name) == 0) {
            return &cmds[i];
        }
    }
    return 0;
}

int appcore_command_capabilities_allowed(const dom_app_command_desc* cmd,
                                         const char* const* capability_ids,
                                         u32 capability_count)
{
    u32 i;
    u32 j;
    int found;

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
        if (!required || !required[0]) {
            return 0;
        }
        found = 0;
        for (j = 0u; j < capability_count; ++j) {
            const char* available = capability_ids[j];
            if (available && strcmp(required, available) == 0) {
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
