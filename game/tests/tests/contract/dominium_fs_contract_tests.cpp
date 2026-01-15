/*
FILE: tests/contract/dominium_fs_contract_tests.cpp
MODULE: Repository
LAYER / SUBSYSTEM: tests/contract
RESPONSIBILITY: Validates launcher-owned filesystem resolution contract helpers.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <cstdio>
#include <cstdlib>
#include <string>

#include "dom_paths.h"
#include "runtime/dom_game_paths.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static void set_env_value(const char *key, const char *value) {
#if defined(_WIN32) || defined(_WIN64)
    if (value) {
        _putenv_s(key, value);
    } else {
        std::string expr = std::string(key) + "=";
        _putenv(expr.c_str());
    }
#else
    if (value) {
        setenv(key, value, 1);
    } else {
        unsetenv(key);
    }
#endif
}

struct EnvGuard {
    const char *key;
    std::string old_value;
    bool had_value;

    EnvGuard(const char *key_in, const char *value)
        : key(key_in),
          old_value(),
          had_value(false) {
        const char *prev = std::getenv(key);
        if (prev) {
            old_value = prev;
            had_value = true;
        }
        set_env_value(key, value);
    }

    ~EnvGuard() {
        if (had_value) {
            set_env_value(key, old_value.c_str());
        } else {
            set_env_value(key, 0);
        }
    }
};

static int test_missing_roots_refusal(void) {
    EnvGuard run_root("DOMINIUM_RUN_ROOT", 0);
    EnvGuard home_root("DOMINIUM_HOME", 0);

    dom::DomGamePaths paths;
    if (dom::dom_game_paths_init_from_env(paths,
                                          "demo",
                                          1ull,
                                          dom::DOM_GAME_PATHS_FLAG_LAUNCHER_REQUIRED)) {
        return fail("expected missing run root refusal");
    }
    if (dom::dom_game_paths_last_refusal(paths) != dom::DOM_GAME_PATHS_REFUSAL_MISSING_RUN_ROOT) {
        return fail("missing run root refusal code mismatch");
    }
    return 0;
}

static int test_traversal_rejected(void) {
    EnvGuard run_root("DOMINIUM_RUN_ROOT", "run_root");
    EnvGuard home_root("DOMINIUM_HOME", 0);
    dom::DomGamePaths paths;
    std::string out;

    if (!dom::dom_game_paths_init_from_env(paths, "demo", 1ull, dom::DOM_GAME_PATHS_FLAG_NONE)) {
        return fail("init failed for traversal test");
    }
    if (dom::dom_game_paths_resolve_rel(paths,
                                        dom::DOM_GAME_PATH_BASE_SAVE_DIR,
                                        "../escape",
                                        out)) {
        return fail("expected traversal rejection '../'");
    }
    if (dom::dom_game_paths_last_refusal(paths) != dom::DOM_GAME_PATHS_REFUSAL_TRAVERSAL) {
        return fail("traversal refusal code mismatch '../'");
    }
    if (dom::dom_game_paths_resolve_rel(paths,
                                        dom::DOM_GAME_PATH_BASE_SAVE_DIR,
                                        "..\\escape",
                                        out)) {
        return fail("expected traversal rejection '..\\\\'");
    }
    if (dom::dom_game_paths_last_refusal(paths) != dom::DOM_GAME_PATHS_REFUSAL_TRAVERSAL) {
        return fail("traversal refusal code mismatch '..\\\\'");
    }
    return 0;
}

static int test_absolute_save_rejected(void) {
    EnvGuard run_root("DOMINIUM_RUN_ROOT", "run_root");
    EnvGuard home_root("DOMINIUM_HOME", 0);
    dom::DomGamePaths paths;
    std::string out;

    if (!dom::dom_game_paths_init_from_env(paths,
                                           "demo",
                                           1ull,
                                           dom::DOM_GAME_PATHS_FLAG_LAUNCHER_REQUIRED)) {
        return fail("init failed for absolute save test");
    }
#if defined(_WIN32) || defined(_WIN64)
    const std::string abs_path = "C:\\abs\\save.dmsg";
#else
    const std::string abs_path = "/abs/save.dmsg";
#endif
    if (dom::dom_game_paths_resolve_rel(paths,
                                        dom::DOM_GAME_PATH_BASE_SAVE_DIR,
                                        abs_path,
                                        out)) {
        return fail("expected absolute save rejection");
    }
    if (dom::dom_game_paths_last_refusal(paths) != dom::DOM_GAME_PATHS_REFUSAL_ABSOLUTE_PATH) {
        return fail("absolute save refusal code mismatch");
    }
    return 0;
}

static int test_absolute_run_root_rejected(void) {
    EnvGuard run_root("DOMINIUM_RUN_ROOT", "run_root");
    EnvGuard home_root("DOMINIUM_HOME", 0);
    dom::DomGamePaths paths;
    std::string out;

    if (!dom::dom_game_paths_init_from_env(paths,
                                           "demo",
                                           1ull,
                                           dom::DOM_GAME_PATHS_FLAG_LAUNCHER_REQUIRED)) {
        return fail("init failed for absolute run root test");
    }
#if defined(_WIN32) || defined(_WIN64)
    const std::string abs_path = "C:\\abs\\universe.dmu";
#else
    const std::string abs_path = "/abs/universe.dmu";
#endif
    if (dom::dom_game_paths_resolve_rel(paths,
                                        dom::DOM_GAME_PATH_BASE_RUN_ROOT,
                                        abs_path,
                                        out)) {
        return fail("expected absolute run root rejection");
    }
    if (dom::dom_game_paths_last_refusal(paths) != dom::DOM_GAME_PATHS_REFUSAL_ABSOLUTE_PATH) {
        return fail("absolute run root refusal code mismatch");
    }
    return 0;
}

static int test_run_root_scopes_outputs(void) {
    EnvGuard run_root("DOMINIUM_RUN_ROOT", "run_root");
    EnvGuard home_root("DOMINIUM_HOME", 0);
    dom::DomGamePaths paths;
    std::string out;

    if (!dom::dom_game_paths_init_from_env(paths, "demo", 42ull, dom::DOM_GAME_PATHS_FLAG_NONE)) {
        return fail("init failed for run root output test");
    }
    const std::string save_dir = dom::dom_game_paths_get_save_dir(paths);
    const std::string log_dir = dom::dom_game_paths_get_log_dir(paths);
    const std::string replay_dir = dom::dom_game_paths_get_replay_dir(paths);

    if (save_dir.empty() || log_dir.empty() || replay_dir.empty()) {
        return fail("expected run-scoped dirs");
    }
    if (!dom::dom_game_paths_resolve_rel(paths,
                                         dom::DOM_GAME_PATH_BASE_SAVE_DIR,
                                         "slot1.dmsg",
                                         out)) {
        return fail("save resolve failed");
    }
    if (out != dom::join(save_dir, "slot1.dmsg")) {
        return fail("save path mismatch");
    }
    if (!dom::dom_game_paths_resolve_rel(paths,
                                         dom::DOM_GAME_PATH_BASE_LOG_DIR,
                                         "session.log",
                                         out)) {
        return fail("log resolve failed");
    }
    if (out != dom::join(log_dir, "session.log")) {
        return fail("log path mismatch");
    }
    if (!dom::dom_game_paths_resolve_rel(paths,
                                         dom::DOM_GAME_PATH_BASE_REPLAY_DIR,
                                         "demo.dmrp",
                                         out)) {
        return fail("replay resolve failed");
    }
    if (out != dom::join(replay_dir, "demo.dmrp")) {
        return fail("replay path mismatch");
    }
    return 0;
}

static int test_home_instance_root(void) {
    EnvGuard run_root("DOMINIUM_RUN_ROOT", 0);
    EnvGuard home_root("DOMINIUM_HOME", "home_root");
    dom::DomGamePaths paths;

    if (!dom::dom_game_paths_init_from_env(paths, "inst_alpha", 7ull, dom::DOM_GAME_PATHS_FLAG_NONE)) {
        return fail("init failed for home root test");
    }
    const std::string expected = dom::join(paths.home_root, "instances/inst_alpha");
    if (dom::dom_game_paths_get_instance_root(paths) != expected) {
        return fail("instance root mismatch");
    }
    return 0;
}

static int test_run_root_precedence(void) {
    EnvGuard run_root("DOMINIUM_RUN_ROOT", "run_root");
    EnvGuard home_root("DOMINIUM_HOME", "home_root");
    dom::DomGamePaths paths;

    if (!dom::dom_game_paths_init_from_env(paths, "inst_beta", 9ull, dom::DOM_GAME_PATHS_FLAG_NONE)) {
        return fail("init failed for run root precedence test");
    }
    const std::string expected = dom::join(paths.run_root, "saves");
    if (dom::dom_game_paths_get_save_dir(paths) != expected) {
        return fail("run root precedence mismatch");
    }
    return 0;
}

int main(void) {
    int rc = 0;
    if ((rc = test_missing_roots_refusal()) != 0) return rc;
    if ((rc = test_traversal_rejected()) != 0) return rc;
    if ((rc = test_absolute_save_rejected()) != 0) return rc;
    if ((rc = test_absolute_run_root_rejected()) != 0) return rc;
    if ((rc = test_run_root_scopes_outputs()) != 0) return rc;
    if ((rc = test_home_instance_root()) != 0) return rc;
    if ((rc = test_run_root_precedence()) != 0) return rc;
    std::printf("dominium fs contract tests passed\n");
    return 0;
}
