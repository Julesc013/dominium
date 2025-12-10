#ifndef DOMINIUM_GAME_APP_HPP
#define DOMINIUM_GAME_APP_HPP

#include "domino/core/types.h"

class GameApp {
public:
    GameApp();
    ~GameApp();

    int run(int argc, char** argv);

private:
    int run_headless(u32 seed, u32 ticks, u32 width, u32 height);
    int load_world_checksum(const char* path, u32* checksum_out);
    int run_tui_mode(void);
    int run_gui_mode(void);
};

#endif /* DOMINIUM_GAME_APP_HPP */
