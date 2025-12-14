#include <string>
#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "dom_game_app.h"

namespace dom {

void init_default_game_config(GameConfig &cfg) {
    cfg.dominium_home.clear();
    cfg.instance_id = "demo";
    cfg.connect_addr.clear();
    cfg.net_port = 7777u;
    cfg.mode = GAME_MODE_GUI;
    cfg.server_mode = SERVER_OFF;
    cfg.demo_mode = false;
    cfg.platform_backend.clear();
    cfg.gfx_backend.clear();
    cfg.tick_rate_hz = 60u;
    cfg.dev_mode = false;
    cfg.deterministic_test = false;
    cfg.replay_record_path.clear();
    cfg.replay_play_path.clear();
}

static int str_ieq(const char *a, const char *b) {
    size_t i;
    size_t len_a;
    size_t len_b;
    if (!a || !b) {
        return 0;
    }
    len_a = std::strlen(a);
    len_b = std::strlen(b);
    if (len_a != len_b) {
        return 0;
    }
    for (i = 0u; i < len_a; ++i) {
        char ca = a[i];
        char cb = b[i];
        if (ca >= 'A' && ca <= 'Z') ca = static_cast<char>(ca - 'A' + 'a');
        if (cb >= 'A' && cb <= 'Z') cb = static_cast<char>(cb - 'A' + 'a');
        if (ca != cb) {
            return 0;
        }
    }
    return 1;
}

static bool parse_tick_rate(const char *val, unsigned &out_rate) {
    char *endp = 0;
    unsigned long v;
    if (!val) {
        return false;
    }
    v = std::strtoul(val, &endp, 10);
    if (val == endp) {
        return false;
    }
    out_rate = static_cast<unsigned>(v);
    return true;
}

bool parse_game_cli_args(int argc, char **argv, GameConfig &cfg) {
    int i;
    for (i = 1; i < argc; ++i) {
        const char *arg = argv[i];
        if (!arg) {
            continue;
        }

        if (std::strncmp(arg, "--mode=", 7) == 0) {
            const char *val = arg + 7;
            if (str_ieq(val, "gui")) cfg.mode = GAME_MODE_GUI;
            else if (str_ieq(val, "tui")) cfg.mode = GAME_MODE_TUI;
            else if (str_ieq(val, "headless")) cfg.mode = GAME_MODE_HEADLESS;
            else {
                std::printf("Unknown mode '%s'\n", val);
                return false;
            }
            continue;
        }
        if (str_ieq(arg, "--server")) {
            cfg.server_mode = SERVER_DEDICATED;
            if (cfg.mode == GAME_MODE_GUI) {
                cfg.mode = GAME_MODE_HEADLESS;
            }
            continue;
        }
        if (str_ieq(arg, "--listen")) {
            cfg.server_mode = SERVER_LISTEN;
            continue;
        }
        if (std::strncmp(arg, "--server=", 9) == 0) {
            const char *val = arg + 9;
            if (str_ieq(val, "off")) cfg.server_mode = SERVER_OFF;
            else if (str_ieq(val, "listen")) cfg.server_mode = SERVER_LISTEN;
            else if (str_ieq(val, "dedicated")) cfg.server_mode = SERVER_DEDICATED;
            else {
                std::printf("Unknown server mode '%s'\n", val);
                return false;
            }
            continue;
        }
        if (std::strncmp(arg, "--connect=", 10) == 0) {
            cfg.connect_addr = std::string(arg + 10);
            continue;
        }
        if (std::strncmp(arg, "--port=", 7) == 0) {
            unsigned rate = 0u;
            if (!parse_tick_rate(arg + 7, rate) || rate == 0u || rate > 65535u) {
                std::printf("Invalid port '%s'\n", arg + 7);
                return false;
            }
            cfg.net_port = rate;
            continue;
        }
        if (std::strncmp(arg, "--instance=", 11) == 0) {
            cfg.instance_id = std::string(arg + 11);
            continue;
        }
        if (std::strncmp(arg, "--platform=", 11) == 0) {
            cfg.platform_backend = std::string(arg + 11);
            continue;
        }
        if (std::strncmp(arg, "--gfx=", 6) == 0) {
            cfg.gfx_backend = std::string(arg + 6);
            continue;
        }
        if (std::strncmp(arg, "--tickrate=", 11) == 0) {
            unsigned rate = cfg.tick_rate_hz;
            if (!parse_tick_rate(arg + 11, rate)) {
                std::printf("Invalid tickrate '%s'\n", arg + 11);
                return false;
            }
            cfg.tick_rate_hz = rate;
            continue;
        }
        if (std::strncmp(arg, "--home=", 7) == 0) {
            cfg.dominium_home = std::string(arg + 7);
            continue;
        }
        if (str_ieq(arg, "--demo")) {
            cfg.demo_mode = true;
            continue;
        }
        if (str_ieq(arg, "--devmode")) {
            cfg.dev_mode = true;
            cfg.deterministic_test = true;
            continue;
        }
        if (str_ieq(arg, "--deterministic-test")) {
            cfg.deterministic_test = true;
            continue;
        }
        if (std::strncmp(arg, "--record-replay=", 16) == 0) {
            cfg.replay_record_path = std::string(arg + 16);
            continue;
        }
        if (std::strncmp(arg, "--play-replay=", 14) == 0) {
            cfg.replay_play_path = std::string(arg + 14);
            continue;
        }
    }
    return true;
}

} // namespace dom

int main(int argc, char **argv) {
    dom::GameConfig cfg;
    dom::DomGameApp app;

    dom::init_default_game_config(cfg);
    if (!dom::parse_game_cli_args(argc, argv, cfg)) {
        return 1;
    }

    if (!app.init_from_cli(cfg)) {
        return 1;
    }

    app.run();
    app.shutdown();
    return 0;
}
