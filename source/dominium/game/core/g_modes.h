#ifndef DMN_GAME_MODES_H
#define DMN_GAME_MODES_H

#include "g_runtime.h"

int dmn_game_mode_from_string(const char* value, DmnGameMode* out);
int dmn_game_server_mode_from_string(const char* value, DmnGameServerMode* out);
const char* dmn_game_mode_to_string(DmnGameMode mode);
const char* dmn_game_server_mode_to_string(DmnGameServerMode mode);

#endif /* DMN_GAME_MODES_H */
