#include "g_modes.h"
#include <string.h>

int dmn_game_mode_from_string(const char* value, DmnGameMode* out)
{
    if (!value || !out) return 0;
    if (strcmp(value, "gui") == 0) {
        *out = DMN_GAME_MODE_GUI;
        return 1;
    }
    if (strcmp(value, "tui") == 0) {
        *out = DMN_GAME_MODE_TUI;
        return 1;
    }
    if (strcmp(value, "headless") == 0) {
        *out = DMN_GAME_MODE_HEADLESS;
        return 1;
    }
    return 0;
}

int dmn_game_server_mode_from_string(const char* value, DmnGameServerMode* out)
{
    if (!value || !out) return 0;
    if (strcmp(value, "off") == 0) {
        *out = DMN_GAME_SERVER_OFF;
        return 1;
    }
    if (strcmp(value, "listen") == 0) {
        *out = DMN_GAME_SERVER_LISTEN;
        return 1;
    }
    if (strcmp(value, "dedicated") == 0) {
        *out = DMN_GAME_SERVER_DEDICATED;
        return 1;
    }
    return 0;
}

const char* dmn_game_mode_to_string(DmnGameMode mode)
{
    switch (mode) {
    case DMN_GAME_MODE_GUI: return "gui";
    case DMN_GAME_MODE_TUI: return "tui";
    case DMN_GAME_MODE_HEADLESS: return "headless";
    default: break;
    }
    return "unknown";
}

const char* dmn_game_server_mode_to_string(DmnGameServerMode mode)
{
    switch (mode) {
    case DMN_GAME_SERVER_OFF: return "off";
    case DMN_GAME_SERVER_LISTEN: return "listen";
    case DMN_GAME_SERVER_DEDICATED: return "dedicated";
    default: break;
    }
    return "unknown";
}
