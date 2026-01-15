/*
FILE: source/dominium/game/runtime/dom_game_paths.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_paths
RESPONSIBILITY: Implements launcher-owned filesystem resolution for the game runtime.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Internal implementation detail only.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_game_paths.h"

#include <cstdlib>
#include <cstring>
#include <vector>

#if defined(_WIN32) || defined(_WIN64)
#include <direct.h>
#else
#include <unistd.h>
#endif

#include "dom_paths.h"

namespace dom {

namespace {

static bool is_alpha(char c) {
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z');
}

static bool is_abs_path(const std::string &path) {
    if (path.empty()) {
        return false;
    }
    if (path[0] == '/' || path[0] == '\\') {
        return true;
    }
    if (path.size() >= 2u && is_alpha(path[0]) && path[1] == ':') {
        return true;
    }
    return false;
}

static std::string normalize_seps(const std::string &in) {
    std::string out = in;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') {
            out[i] = '/';
        }
    }
    return out;
}

static bool get_cwd(std::string &out) {
    char buf[1024];
#if defined(_WIN32) || defined(_WIN64)
    if (!_getcwd(buf, sizeof(buf))) {
        return false;
    }
#else
    if (!getcwd(buf, sizeof(buf))) {
        return false;
    }
#endif
    out.assign(buf);
    return true;
}

static bool set_refusal(DomGamePaths &paths, u32 code) {
    paths.last_refusal = code;
    return false;
}

static u32 normalize_root_path(const std::string &input, std::string &out) {
    if (input.empty()) {
        return DOM_GAME_PATHS_REFUSAL_NORMALIZATION;
    }

    std::string path = normalize_seps(input);
    std::string prefix;
    size_t start = 0u;
    bool non_canonical = false;

    if (path.size() >= 2u && is_alpha(path[0]) && path[1] == ':') {
        prefix.assign(path, 0u, 2u);
        start = 2u;
        if (start < path.size() && path[start] == '/') {
            start += 1u;
        }
        prefix.append("/");
    } else if (path.size() >= 2u && path[0] == '/' && path[1] == '/') {
        prefix = "//";
        start = 2u;
    } else if (path[0] == '/') {
        prefix = "/";
        start = 1u;
    } else {
        return DOM_GAME_PATHS_REFUSAL_NORMALIZATION;
    }

    std::vector<std::string> parts;
    std::string segment;
    size_t i;
    for (i = start; i <= path.size(); ++i) {
        const char c = (i < path.size()) ? path[i] : '/';
        if (c == '/') {
            if (segment.empty()) {
                non_canonical = true;
            } else if (segment == ".") {
                non_canonical = true;
            } else if (segment == "..") {
                return DOM_GAME_PATHS_REFUSAL_TRAVERSAL;
            } else {
                parts.push_back(segment);
            }
            segment.clear();
        } else {
            segment.push_back(c);
        }
    }

    if (non_canonical) {
        return DOM_GAME_PATHS_REFUSAL_NON_CANONICAL;
    }

    out = prefix;
    for (i = 0u; i < parts.size(); ++i) {
        if (!out.empty() && out[out.size() - 1u] != '/') {
            out.push_back('/');
        }
        out.append(parts[i]);
    }
    if (parts.empty() && prefix.size() == 2u && prefix[1] == ':') {
        out = prefix;
        out.push_back('/');
    }
    return DOM_GAME_PATHS_REFUSAL_OK;
}

static bool normalize_rel_path(DomGamePaths &paths, const std::string &input, std::string &out) {
    if (input.empty()) {
        return set_refusal(paths, DOM_GAME_PATHS_REFUSAL_NORMALIZATION);
    }
    if (is_abs_path(input)) {
        return set_refusal(paths, DOM_GAME_PATHS_REFUSAL_ABSOLUTE_PATH);
    }

    std::vector<std::string> parts;
    std::string segment;
    bool non_canonical = false;
    size_t i;
    for (i = 0u; i <= input.size(); ++i) {
        const char c = (i < input.size()) ? input[i] : '/';
        if (c == '/' || c == '\\') {
            if (segment.empty()) {
                non_canonical = true;
            } else if (segment == ".") {
                non_canonical = true;
            } else if (segment == "..") {
                return set_refusal(paths, DOM_GAME_PATHS_REFUSAL_TRAVERSAL);
            } else {
                parts.push_back(segment);
            }
            segment.clear();
        } else {
            segment.push_back(c);
        }
    }

    if (non_canonical) {
        return set_refusal(paths, DOM_GAME_PATHS_REFUSAL_NON_CANONICAL);
    }
    if (parts.empty()) {
        return set_refusal(paths, DOM_GAME_PATHS_REFUSAL_NORMALIZATION);
    }

    out.clear();
    for (i = 0u; i < parts.size(); ++i) {
        if (i > 0u) {
            out.push_back('/');
        }
        out.append(parts[i]);
    }
    return true;
}

static bool resolve_root_from_env(DomGamePaths &paths,
                                  const char *env,
                                  u32 invalid_code,
                                  std::string &out_root) {
    std::string raw;
    std::string abs;
    std::string normalized;
    u32 rc;

    if (!env || env[0] == '\0') {
        return false;
    }

    raw.assign(env);
    abs = raw;
    if (!is_abs_path(raw)) {
        std::string cwd;
        if (!get_cwd(cwd)) {
            return set_refusal(paths, invalid_code);
        }
        abs = join(cwd, raw);
    }

    rc = normalize_root_path(abs, normalized);
    if (rc != DOM_GAME_PATHS_REFUSAL_OK) {
        if (rc == DOM_GAME_PATHS_REFUSAL_TRAVERSAL ||
            rc == DOM_GAME_PATHS_REFUSAL_NON_CANONICAL) {
            return set_refusal(paths, rc);
        }
        return set_refusal(paths, invalid_code);
    }

    out_root.swap(normalized);
    return true;
}

static bool get_base_root(DomGamePaths &paths,
                          DomGamePathBaseKind base_kind,
                          std::string &out_root) {
    out_root.clear();
    switch (base_kind) {
    case DOM_GAME_PATH_BASE_RUN_ROOT:
        out_root = paths.run_root;
        break;
    case DOM_GAME_PATH_BASE_HOME_ROOT:
        out_root = paths.home_root;
        break;
    case DOM_GAME_PATH_BASE_INSTANCE_ROOT:
        out_root = paths.instance_root;
        break;
    case DOM_GAME_PATH_BASE_SAVE_DIR:
        out_root = dom_game_paths_get_save_dir(paths);
        break;
    case DOM_GAME_PATH_BASE_LOG_DIR:
        out_root = dom_game_paths_get_log_dir(paths);
        break;
    case DOM_GAME_PATH_BASE_CACHE_DIR:
        out_root = dom_game_paths_get_cache_dir(paths);
        break;
    case DOM_GAME_PATH_BASE_REPLAY_DIR:
        out_root = dom_game_paths_get_replay_dir(paths);
        break;
    default:
        break;
    }

    if (out_root.empty()) {
        if (base_kind == DOM_GAME_PATH_BASE_RUN_ROOT ||
            base_kind == DOM_GAME_PATH_BASE_SAVE_DIR ||
            base_kind == DOM_GAME_PATH_BASE_LOG_DIR ||
            base_kind == DOM_GAME_PATH_BASE_CACHE_DIR ||
            base_kind == DOM_GAME_PATH_BASE_REPLAY_DIR) {
            return set_refusal(paths, DOM_GAME_PATHS_REFUSAL_MISSING_RUN_ROOT);
        }
        return set_refusal(paths, DOM_GAME_PATHS_REFUSAL_MISSING_HOME_ROOT);
    }
    return true;
}

static bool is_path_prefix(const std::string &base, const std::string &full) {
    if (base.empty() || full.empty()) {
        return false;
    }
    if (full == base) {
        return true;
    }
    if (full.size() <= base.size()) {
        return false;
    }
    if (full.compare(0u, base.size(), base) != 0) {
        return false;
    }
    return full[base.size()] == '/';
}

} // namespace

DomGamePaths::DomGamePaths()
    : run_root(),
      home_root(),
      instance_root(),
      instance_id(),
      instance_root_ref_rel(),
      run_id(0u),
      flags(0u),
      last_refusal(DOM_GAME_PATHS_REFUSAL_OK),
      instance_root_ref_base(DOM_GAME_PATH_BASE_RUN_ROOT),
      has_instance_root_ref(false) {
}

bool dom_game_paths_init_from_env(DomGamePaths &paths,
                                  const std::string &instance_id,
                                  u64 run_id,
                                  u32 flags) {
    const char *env_run = std::getenv("DOMINIUM_RUN_ROOT");
    const char *env_home = std::getenv("DOMINIUM_HOME");
    bool has_run = false;
    bool has_home = false;

    paths.run_root.clear();
    paths.home_root.clear();
    paths.instance_root.clear();
    paths.instance_id = instance_id;
    paths.run_id = run_id;
    paths.flags = flags;
    paths.last_refusal = DOM_GAME_PATHS_REFUSAL_OK;
    paths.has_instance_root_ref = false;
    paths.instance_root_ref_rel.clear();
    paths.instance_root_ref_base = DOM_GAME_PATH_BASE_RUN_ROOT;

    has_run = resolve_root_from_env(paths, env_run,
                                    DOM_GAME_PATHS_REFUSAL_INVALID_RUN_ROOT,
                                    paths.run_root);
    if (paths.last_refusal != DOM_GAME_PATHS_REFUSAL_OK) {
        return false;
    }

    has_home = resolve_root_from_env(paths, env_home,
                                     DOM_GAME_PATHS_REFUSAL_INVALID_HOME_ROOT,
                                     paths.home_root);
    if (paths.last_refusal != DOM_GAME_PATHS_REFUSAL_OK) {
        return false;
    }

    if (!has_run && (flags & DOM_GAME_PATHS_FLAG_LAUNCHER_REQUIRED) &&
        !(flags & DOM_GAME_PATHS_FLAG_DEV_ALLOW_AD_HOC)) {
        return set_refusal(paths, DOM_GAME_PATHS_REFUSAL_MISSING_RUN_ROOT);
    }

    if (has_home && !paths.instance_id.empty()) {
        std::string inst_dir = join(paths.home_root, "instances");
        paths.instance_root = join(inst_dir, paths.instance_id);
    }

    return true;
}

const std::string &dom_game_paths_get_run_root(const DomGamePaths &paths) {
    return paths.run_root;
}

const std::string &dom_game_paths_get_instance_root(const DomGamePaths &paths) {
    return paths.instance_root;
}

std::string dom_game_paths_get_save_dir(const DomGamePaths &paths) {
    if (paths.run_root.empty()) {
        return std::string();
    }
    return join(paths.run_root, "saves");
}

std::string dom_game_paths_get_log_dir(const DomGamePaths &paths) {
    if (paths.run_root.empty()) {
        return std::string();
    }
    return join(paths.run_root, "logs");
}

std::string dom_game_paths_get_cache_dir(const DomGamePaths &paths) {
    if (paths.run_root.empty()) {
        return std::string();
    }
    return join(paths.run_root, "cache");
}

std::string dom_game_paths_get_replay_dir(const DomGamePaths &paths) {
    if (paths.run_root.empty()) {
        return std::string();
    }
    return join(paths.run_root, "replays");
}

bool dom_game_paths_resolve_rel(DomGamePaths &paths,
                                DomGamePathBaseKind base_kind,
                                const std::string &rel,
                                std::string &out_abs) {
    std::string base;
    std::string normalized_rel;
    std::string combined;

    out_abs.clear();
    paths.last_refusal = DOM_GAME_PATHS_REFUSAL_OK;

    if (!get_base_root(paths, base_kind, base)) {
        return false;
    }
    if (!normalize_rel_path(paths, rel, normalized_rel)) {
        return false;
    }

    combined = join(base, normalized_rel);
    if (!is_path_prefix(base, combined)) {
        return set_refusal(paths, DOM_GAME_PATHS_REFUSAL_OUTSIDE_ROOT);
    }

    out_abs.swap(combined);
    return true;
}

bool dom_game_paths_set_instance_root_ref(DomGamePaths &paths,
                                          DomGamePathBaseKind base_kind,
                                          const std::string &rel) {
    std::string resolved;

    if (!paths.home_root.empty()) {
        return true;
    }
    if (base_kind != DOM_GAME_PATH_BASE_RUN_ROOT &&
        base_kind != DOM_GAME_PATH_BASE_HOME_ROOT) {
        return set_refusal(paths, DOM_GAME_PATHS_REFUSAL_NORMALIZATION);
    }
    if (!dom_game_paths_resolve_rel(paths, base_kind, rel, resolved)) {
        return false;
    }

    paths.instance_root = resolved;
    paths.instance_root_ref_rel = rel;
    paths.instance_root_ref_base = base_kind;
    paths.has_instance_root_ref = true;
    return true;
}

u32 dom_game_paths_last_refusal(const DomGamePaths &paths) {
    return paths.last_refusal;
}

} // namespace dom
