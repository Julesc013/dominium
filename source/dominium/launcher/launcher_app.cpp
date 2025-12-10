#include "domino/pkg/repo.h"
#include "domino/system/dsys.h"
#include "dominium/launcher/launcher_app.hpp"
#include <cstdio>
#include <cstring>
#include <cstdlib>

LauncherApp::LauncherApp() {
}

LauncherApp::~LauncherApp() {
}

int LauncherApp::run(int argc, char** argv) {
    if (argc <= 1) {
        std::printf("Launcher usage:\n");
        std::printf("  dominium_launcher list\n");
        std::printf("  dominium_launcher run-game [--seed N] [--ticks N]\n");
        return 0;
    }

    if (std::strcmp(argv[1], "list") == 0) {
        return run_list_products();
    } else if (std::strcmp(argv[1], "run-game") == 0) {
        return run_run_game(argc - 1, argv + 1);
    } else {
        std::printf("Launcher: unknown command '%s'\n", argv[1]);
        return 1;
    }
}

int LauncherApp::run_list_products() {
    dom_product_info info;
    std::memset(&info, 0, sizeof(info));

    if (!dom_repo_load_primary_game(&info)) {
        std::printf("Launcher: failed to load primary game product manifest.\n");
        return 1;
    }

    std::printf("Launcher: primary game product:\n");
    std::printf("  product_id      = %s\n", info.product_id);
    std::printf("  role            = %d\n", (int)info.role);
    std::printf("  product_version = %s\n", info.product_version);
    std::printf("  core_version    = %s\n", info.core_version);
    std::printf("  os_family       = %d\n", (int)info.os_family);
    std::printf("  arch            = %d\n", (int)info.arch);
    std::printf("  exec_rel_path   = %s\n", info.exec_rel_path);
    std::printf("  compat.save_format_version    = %u\n", (unsigned)info.compat.save_format_version);
    std::printf("  compat.pack_format_version    = %u\n", (unsigned)info.compat.pack_format_version);
    std::printf("  compat.net_protocol_version   = %u\n", (unsigned)info.compat.net_protocol_version);
    std::printf("  compat.replay_format_version  = %u\n", (unsigned)info.compat.replay_format_version);
    std::printf("  compat.launcher_proto_version = %u\n", (unsigned)info.compat.launcher_proto_version);
    std::printf("  compat.tools_proto_version    = %u\n", (unsigned)info.compat.tools_proto_version);

    return 0;
}

int LauncherApp::run_run_game(int argc, char** argv) {
    unsigned long seed = 12345;
    unsigned long ticks = 100;
    int i;

    for (i = 1; i < argc; ++i) {
        if (std::strcmp(argv[i], "--seed") == 0 && (i + 1) < argc) {
            seed = std::strtoul(argv[++i], 0, 10);
        } else if (std::strcmp(argv[i], "--ticks") == 0 && (i + 1) < argc) {
            ticks = std::strtoul(argv[++i], 0, 10);
        } else {
            std::printf("Launcher: unknown or incomplete argument '%s'\n", argv[i]);
            return 1;
        }
    }

    dom_product_info info;
    std::memset(&info, 0, sizeof(info));
    if (!dom_repo_load_primary_game(&info)) {
        std::printf("Launcher: failed to load primary game product manifest.\n");
        return 1;
    }

    char root[512];
    if (!dom_repo_get_root(root, sizeof(root))) {
        std::printf("Launcher: dom_repo_get_root failed.\n");
        return 1;
    }

    /* Keep this in sync with repo path assumptions. */
    const char* platform_dir = "posix-x86_64";

    char exec_dir[768];
    std::snprintf(exec_dir, sizeof(exec_dir),
                  "%s/repo/products/%s/%s/core-%s/%s",
                  root,
                  info.product_id,
                  info.product_version,
                  info.core_version,
                  platform_dir);

    char exec_full_path[1024];
    std::snprintf(exec_full_path, sizeof(exec_full_path),
                  "%s/%s",
                  exec_dir,
                  info.exec_rel_path);

    std::printf("Launcher: spawning game:\n");
    std::printf("  path  = %s\n", exec_full_path);
    std::printf("  seed  = %lu\n", seed);
    std::printf("  ticks = %lu\n", ticks);

    char seed_buf[32];
    char ticks_buf[32];
    std::snprintf(seed_buf, sizeof(seed_buf), "--seed=%lu", seed);
    std::snprintf(ticks_buf, sizeof(ticks_buf), "--ticks=%lu", ticks);

    const char* game_argv[6];
    game_argv[0] = exec_full_path;
    game_argv[1] = "--mode=headless";
    game_argv[2] = seed_buf;
    game_argv[3] = ticks_buf;
    game_argv[4] = 0;

    dsys_process_handle handle;
    handle.impl = 0;

    if (dsys_init() != DSYS_OK) {
        std::printf("Launcher: dsys_init failed.\n");
        return 1;
    }

    dsys_proc_result pr = dsys_proc_spawn(exec_full_path, game_argv, 1, &handle);
    if (pr != DSYS_PROC_OK) {
        std::printf("Launcher: dsys_proc_spawn failed (%d)\n", (int)pr);
        dsys_shutdown();
        return 1;
    }

    int exit_code = -1;
    pr = dsys_proc_wait(&handle, &exit_code);
    if (pr != DSYS_PROC_OK) {
        std::printf("Launcher: dsys_proc_wait failed (%d)\n", (int)pr);
        dsys_shutdown();
        return 1;
    }

    std::printf("Launcher: game exited with code %d\n", exit_code);

    dsys_shutdown();
    return exit_code;
}

/* Usage notes:
   1) List products: dominium_launcher list
   2) Run headless game: dominium_launcher run-game --seed 12345 --ticks 100
      - Requires DOMINIUM_HOME and product.json present.
      - Game runs deterministic sim, prints checksum, writes world.tlv.
*/
