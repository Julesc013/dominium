/*
FILE: source/dominium/game/runtime/dom_game_paths.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_paths
RESPONSIBILITY: Defines launcher-owned filesystem resolution contract for the game runtime.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Internal contract only; not ABI-stable.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_PATHS_H
#define DOM_GAME_PATHS_H

#include <string>

extern "C" {
#include "domino/core/types.h"
}

namespace dom {

enum DomGamePathBaseKind {
    DOM_GAME_PATH_BASE_RUN_ROOT = 0,
    DOM_GAME_PATH_BASE_HOME_ROOT = 1,
    DOM_GAME_PATH_BASE_INSTANCE_ROOT = 2,
    DOM_GAME_PATH_BASE_SAVE_DIR = 3,
    DOM_GAME_PATH_BASE_LOG_DIR = 4,
    DOM_GAME_PATH_BASE_CACHE_DIR = 5,
    DOM_GAME_PATH_BASE_REPLAY_DIR = 6
};

enum DomGamePathFlags {
    DOM_GAME_PATHS_FLAG_NONE = 0u,
    DOM_GAME_PATHS_FLAG_LAUNCHER_REQUIRED = 1u << 0,
    DOM_GAME_PATHS_FLAG_DEV_ALLOW_AD_HOC = 1u << 1
};

enum DomGamePathRefusalCode {
    DOM_GAME_PATHS_REFUSAL_OK = 0u,
    DOM_GAME_PATHS_REFUSAL_MISSING_RUN_ROOT = 1001u,
    DOM_GAME_PATHS_REFUSAL_MISSING_HOME_ROOT = 1002u,
    DOM_GAME_PATHS_REFUSAL_INVALID_RUN_ROOT = 1003u,
    DOM_GAME_PATHS_REFUSAL_INVALID_HOME_ROOT = 1004u,
    DOM_GAME_PATHS_REFUSAL_ABSOLUTE_PATH = 1101u,
    DOM_GAME_PATHS_REFUSAL_TRAVERSAL = 1102u,
    DOM_GAME_PATHS_REFUSAL_NORMALIZATION = 1103u,
    DOM_GAME_PATHS_REFUSAL_NON_CANONICAL = 1104u,
    DOM_GAME_PATHS_REFUSAL_OUTSIDE_ROOT = 1105u
};

struct DomGamePaths {
    std::string run_root;
    std::string home_root;
    std::string instance_root;
    std::string instance_id;
    std::string instance_root_ref_rel;
    u64 run_id;
    u32 flags;
    u32 last_refusal;
    DomGamePathBaseKind instance_root_ref_base;
    bool has_instance_root_ref;

    DomGamePaths();
};

bool dom_game_paths_init_from_env(DomGamePaths &paths,
                                  const std::string &instance_id,
                                  u64 run_id,
                                  u32 flags);

const std::string &dom_game_paths_get_run_root(const DomGamePaths &paths);
const std::string &dom_game_paths_get_instance_root(const DomGamePaths &paths);

std::string dom_game_paths_get_save_dir(const DomGamePaths &paths);
std::string dom_game_paths_get_log_dir(const DomGamePaths &paths);
std::string dom_game_paths_get_cache_dir(const DomGamePaths &paths);
std::string dom_game_paths_get_replay_dir(const DomGamePaths &paths);

bool dom_game_paths_resolve_rel(DomGamePaths &paths,
                                DomGamePathBaseKind base_kind,
                                const std::string &rel,
                                std::string &out_abs);

bool dom_game_paths_set_instance_root_ref(DomGamePaths &paths,
                                          DomGamePathBaseKind base_kind,
                                          const std::string &rel);

u32 dom_game_paths_last_refusal(const DomGamePaths &paths);

} // namespace dom

#endif /* DOM_GAME_PATHS_H */
