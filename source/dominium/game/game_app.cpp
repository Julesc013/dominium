#include "dominium/game/game_app.hpp"
#include "domino/system/dsys.h"
#include "domino/sim/sim.h"
#include <cstdio>
#include <cstring>
#include <cstdlib>

GameApp::GameApp() {
}

GameApp::~GameApp() {
}

int GameApp::run(int argc, char** argv) {
    int i;
    for (i = 1; i < argc; ++i) {
        if (std::strcmp(argv[i], "--mode=headless") == 0) {
            return run_headless(argc, argv);
        }
    }
    std::printf("Game: only --mode=headless supported in this build.\n");
    return 1;
}

static d_bool parse_u32_arg(const char* arg, const char* key, u32* out_val) {
    size_t key_len = std::strlen(key);
    if (std::strncmp(arg, key, key_len) != 0) {
        return D_FALSE;
    }
    if (arg[key_len] != '=') {
        return D_FALSE;
    }
    {
        char* endp = 0;
        unsigned long v = std::strtoul(arg + key_len + 1, &endp, 10);
        if (endp == arg + key_len + 1) {
            return D_FALSE;
        }
        *out_val = (u32)v;
        return D_TRUE;
    }
}

int GameApp::run_headless(int argc, char** argv) {
    u32 seed = 12345u;
    u32 ticks = 100u;
    u32 width = 64u;
    u32 height = 64u;
    int i;

    for (i = 1; i < argc; ++i) {
        (void)parse_u32_arg(argv[i], "--seed", &seed);
        (void)parse_u32_arg(argv[i], "--ticks", &ticks);
        (void)parse_u32_arg(argv[i], "--width", &width);
        (void)parse_u32_arg(argv[i], "--height", &height);
    }

    d_world_config cfg;
    cfg.seed = seed;
    cfg.width = width;
    cfg.height = height;

    if (dsys_init() != DSYS_OK) {
        std::printf("Game: dsys_init failed.\n");
        return 1;
    }

    d_world* world = d_world_create(&cfg);
    if (!world) {
        std::printf("Game: d_world_create failed.\n");
        dsys_shutdown();
        return 1;
    }

    for (u32 t = 0; t < ticks; ++t) {
        d_world_tick(world);
    }

    u32 checksum = d_world_checksum(world);

    std::printf("Game headless result:\n");
    std::printf("  seed      = %u\n", (unsigned)seed);
    std::printf("  ticks     = %u\n", (unsigned)ticks);
    std::printf("  width     = %u\n", (unsigned)width);
    std::printf("  height    = %u\n", (unsigned)height);
    std::printf("  checksum  = %08X\n", (unsigned)checksum);

    {
        const char* path = "world.tlv";
        if (!d_world_save_tlv(world, path)) {
            std::printf("  save_tlv  = FAILED (%s)\n", path);
        } else {
            std::printf("  save_tlv  = OK (%s)\n", path);
        }
    }

    d_world_destroy(world);
    dsys_shutdown();
    return 0;
}
