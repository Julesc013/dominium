#ifndef DMN_GAME_RUNTIME_H
#define DMN_GAME_RUNTIME_H

typedef enum DmnGameMode_ {
    DMN_GAME_MODE_GUI,
    DMN_GAME_MODE_TUI,
    DMN_GAME_MODE_HEADLESS
} DmnGameMode;

typedef enum DmnGameServerMode_ {
    DMN_GAME_SERVER_OFF,
    DMN_GAME_SERVER_LISTEN,
    DMN_GAME_SERVER_DEDICATED
} DmnGameServerMode;

typedef struct DmnGameLaunchOptions_ {
    DmnGameMode       mode;
    DmnGameServerMode server_mode;
    int               demo_mode;
} DmnGameLaunchOptions;

void dmn_game_default_options(DmnGameLaunchOptions* out);
void dmn_game_set_launch_options(const DmnGameLaunchOptions* opts);
const DmnGameLaunchOptions* dmn_game_get_launch_options(void);

#endif /* DMN_GAME_RUNTIME_H */
