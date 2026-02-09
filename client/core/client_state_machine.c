#include "client_state_machine.h"

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

void client_state_machine_init(client_state_machine* machine)
{
    if (!machine) {
        return;
    }
    memset(machine, 0, sizeof(*machine));
    machine->state = CLIENT_SESSION_STATE_BOOT_PROGRESS;
}

const char* client_state_machine_state_name(client_session_state state)
{
    switch (state) {
    case CLIENT_SESSION_STATE_BOOT_PROGRESS: return "BootProgress";
    case CLIENT_SESSION_STATE_MAIN_MENU: return "MainMenu";
    case CLIENT_SESSION_STATE_SINGLEPLAYER_WORLD_MANAGER: return "SingleplayerWorldManager";
    case CLIENT_SESSION_STATE_MULTIPLAYER_SERVER_BROWSER: return "MultiplayerServerBrowser";
    case CLIENT_SESSION_STATE_OPTIONS: return "Options";
    case CLIENT_SESSION_STATE_ABOUT: return "About";
    case CLIENT_SESSION_STATE_SESSION_LAUNCHING: return "SessionLaunching";
    case CLIENT_SESSION_STATE_SESSION_RUNNING: return "SessionRunning";
    case CLIENT_SESSION_STATE_REFUSAL_ERROR: return "RefusalError";
    default: break;
    }
    return "Unknown";
}

const char* client_state_machine_last_command(const client_state_machine* machine)
{
    if (!machine || !machine->last_command[0]) {
        return "";
    }
    return machine->last_command;
}

const char* client_state_machine_last_refusal(const client_state_machine* machine)
{
    if (!machine || !machine->last_refusal[0]) {
        return "";
    }
    return machine->last_refusal;
}

int client_state_machine_apply(client_state_machine* machine, const char* command_id)
{
    if (!machine || !command_id || !command_id[0]) {
        return 0;
    }
    copy_text(machine->last_command, sizeof(machine->last_command), command_id);
    machine->last_refusal[0] = '\0';

    if (!starts_with(command_id, "client.")) {
        return 1;
    }
    machine->transition_count += 1u;

    if (strcmp(command_id, "client.boot.start") == 0) {
        machine->state = CLIENT_SESSION_STATE_BOOT_PROGRESS;
        return 1;
    }
    if (strcmp(command_id, "client.boot.progress_poll") == 0) {
        machine->state = CLIENT_SESSION_STATE_MAIN_MENU;
        return 1;
    }
    if (strcmp(command_id, "client.menu.open") == 0) {
        machine->state = CLIENT_SESSION_STATE_MAIN_MENU;
        return 1;
    }
    if (strcmp(command_id, "client.menu.select.singleplayer") == 0) {
        machine->state = CLIENT_SESSION_STATE_SINGLEPLAYER_WORLD_MANAGER;
        return 1;
    }
    if (strcmp(command_id, "client.menu.select.multiplayer") == 0) {
        machine->state = CLIENT_SESSION_STATE_MULTIPLAYER_SERVER_BROWSER;
        return 1;
    }
    if (strcmp(command_id, "client.menu.select.options") == 0) {
        machine->state = CLIENT_SESSION_STATE_OPTIONS;
        return 1;
    }
    if (strcmp(command_id, "client.menu.select.about") == 0) {
        machine->state = CLIENT_SESSION_STATE_ABOUT;
        return 1;
    }
    if (strcmp(command_id, "client.world.play") == 0 ||
        strcmp(command_id, "client.server.connect") == 0) {
        machine->state = CLIENT_SESSION_STATE_SESSION_LAUNCHING;
        return 1;
    }
    if (strcmp(command_id, "client.menu.quit") == 0) {
        machine->state = CLIENT_SESSION_STATE_REFUSAL_ERROR;
        return 1;
    }
    if (starts_with(command_id, "client.world.")) {
        machine->state = CLIENT_SESSION_STATE_SINGLEPLAYER_WORLD_MANAGER;
        return 1;
    }
    if (starts_with(command_id, "client.server.")) {
        machine->state = CLIENT_SESSION_STATE_MULTIPLAYER_SERVER_BROWSER;
        return 1;
    }
    if (starts_with(command_id, "client.options.")) {
        machine->state = CLIENT_SESSION_STATE_OPTIONS;
        return 1;
    }
    if (starts_with(command_id, "client.about.") || starts_with(command_id, "client.diag.")) {
        machine->state = CLIENT_SESSION_STATE_ABOUT;
        return 1;
    }
    if (starts_with(command_id, "client.replay.")) {
        machine->state = CLIENT_SESSION_STATE_SESSION_RUNNING;
        return 1;
    }
    return 1;
}
