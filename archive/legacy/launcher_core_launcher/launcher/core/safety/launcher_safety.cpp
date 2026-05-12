/*
FILE: source/dominium/launcher/core/src/safety/launcher_safety.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / safety
RESPONSIBILITY: Implements deterministic string/path guards for runtime hardening.
*/

#include "launcher_safety.h"

namespace dom {
namespace launcher_core {

namespace {

static bool is_sep(char c) { return c == '/' || c == '\\'; }

static bool is_ascii_alnum(char c) {
    if (c >= '0' && c <= '9') return true;
    if (c >= 'a' && c <= 'z') return true;
    if (c >= 'A' && c <= 'Z') return true;
    return false;
}

static std::string normalize_seps(const std::string& in) {
    std::string out = in;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') {
            out[i] = '/';
        }
    }
    return out;
}

static bool has_double_dot(const std::string& s) {
    size_t i;
    if (s.size() < 2u) {
        return false;
    }
    for (i = 0u; i + 1u < s.size(); ++i) {
        if (s[i] == '.' && s[i + 1u] == '.') {
            return true;
        }
    }
    return false;
}

} /* namespace */

bool launcher_is_safe_id_component(const std::string& s) {
    size_t i;
    if (s.empty()) {
        return false;
    }
    if (s == "." || s == "..") {
        return false;
    }
    if (has_double_dot(s)) {
        return false;
    }
    if (s[s.size() - 1u] == '.' || s[s.size() - 1u] == ' ') {
        return false;
    }
    if (s[0] == ' ') {
        return false;
    }

    for (i = 0u; i < s.size(); ++i) {
        const char c = s[i];
        if (is_sep(c)) {
            return false;
        }
        if (c == ':') {
            return false;
        }
        if (c == '\0') {
            return false;
        }
        if (c == ' ' || c == '\t' || c == '\r' || c == '\n') {
            return false;
        }
        if (is_ascii_alnum(c) || c == '_' || c == '-' || c == '.') {
            continue;
        }
        return false;
    }

    return true;
}

bool launcher_path_is_within_root(const std::string& root, const std::string& path) {
    std::string r = normalize_seps(root);
    std::string p = normalize_seps(path);

    if (r.empty() || p.empty()) {
        return false;
    }
    if (p.size() < r.size()) {
        return false;
    }
    if (p.compare(0u, r.size(), r) != 0) {
        return false;
    }
    if (p.size() == r.size()) {
        return true;
    }

    /* If root ends in a separator, any longer prefix match is within root. */
    if (!r.empty() && is_sep(r[r.size() - 1u])) {
        return true;
    }

    /* Otherwise require boundary separator. */
    return is_sep(p[r.size()]);
}

} /* namespace launcher_core */
} /* namespace dom */

