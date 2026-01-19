/*
FILE: game/mods/mod_manifest.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / mods
RESPONSIBILITY: Implements deterministic mod manifest parsing/validation.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 standard headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Parsing is deterministic and order-preserving.
*/
#include "dominium/mods/mod_manifest.h"

#include <cstring>
#include <cstdlib>
#include <string>

static void mod_set_error(mod_manifest_error* err,
                          mod_manifest_error_code code,
                          u32 line,
                          const char* msg) {
    if (!err) {
        return;
    }
    err->code = code;
    err->line = line;
    if (msg) {
        std::strncpy(err->message, msg, sizeof(err->message) - 1u);
        err->message[sizeof(err->message) - 1u] = '\0';
    } else {
        err->message[0] = '\0';
    }
}

static std::string mod_trim(const std::string& in) {
    size_t start = 0u;
    size_t end = in.size();
    while (start < end) {
        char c = in[start];
        if (c != ' ' && c != '\t' && c != '\r') {
            break;
        }
        start++;
    }
    while (end > start) {
        char c = in[end - 1u];
        if (c != ' ' && c != '\t' && c != '\r') {
            break;
        }
        end--;
    }
    return in.substr(start, end - start);
}

static void mod_copy_string(char* out, size_t cap, const std::string& value) {
    if (!out || cap == 0u) {
        return;
    }
    std::strncpy(out, value.c_str(), cap - 1u);
    out[cap - 1u] = '\0';
}

void mod_manifest_init(mod_manifest* out_manifest) {
    if (!out_manifest) {
        return;
    }
    std::memset(out_manifest, 0, sizeof(*out_manifest));
}

int mod_semver_parse(const char* text, mod_semver* out_version) {
    char* end = 0;
    unsigned long major = 0;
    unsigned long minor = 0;
    unsigned long patch = 0;
    const char* ptr = text;
    if (!text || !out_version) {
        return 1;
    }
    major = std::strtoul(ptr, &end, 10);
    if (end == ptr || *end != '.') {
        return 1;
    }
    ptr = end + 1;
    minor = std::strtoul(ptr, &end, 10);
    if (end == ptr || *end != '.') {
        return 1;
    }
    ptr = end + 1;
    patch = std::strtoul(ptr, &end, 10);
    if (end == ptr || *end != '\0') {
        return 1;
    }
    if (major > 65535u || minor > 65535u || patch > 65535u) {
        return 1;
    }
    out_version->major = (u16)major;
    out_version->minor = (u16)minor;
    out_version->patch = (u16)patch;
    return 0;
}

int mod_semver_compare(const mod_semver* a, const mod_semver* b) {
    if (a->major != b->major) {
        return (a->major < b->major) ? -1 : 1;
    }
    if (a->minor != b->minor) {
        return (a->minor < b->minor) ? -1 : 1;
    }
    if (a->patch != b->patch) {
        return (a->patch < b->patch) ? -1 : 1;
    }
    return 0;
}

int mod_version_in_range(const mod_semver* version, const mod_version_range* range) {
    if (!version || !range) {
        return 0;
    }
    if (range->has_min) {
        if (mod_semver_compare(version, &range->min) < 0) {
            return 0;
        }
    }
    if (range->has_max) {
        if (mod_semver_compare(version, &range->max) > 0) {
            return 0;
        }
    }
    return 1;
}

int mod_parse_hash64(const char* text, u64* out_hash) {
    const char* ptr = text;
    u64 value = 0u;
    int digits = 0;
    if (!text || !out_hash) {
        return 1;
    }
    if (std::strncmp(ptr, "fnv1a64:", 8) == 0) {
        ptr += 8;
    } else if (std::strncmp(ptr, "fnv64:", 6) == 0) {
        ptr += 6;
    }
    while (*ptr) {
        char c = *ptr++;
        u32 nibble = 0u;
        if (c >= '0' && c <= '9') {
            nibble = (u32)(c - '0');
        } else if (c >= 'a' && c <= 'f') {
            nibble = 10u + (u32)(c - 'a');
        } else if (c >= 'A' && c <= 'F') {
            nibble = 10u + (u32)(c - 'A');
        } else {
            return 1;
        }
        if (digits >= 16) {
            return 1;
        }
        value = (value << 4) | (u64)nibble;
        digits++;
    }
    if (digits == 0) {
        return 1;
    }
    *out_hash = value;
    return 0;
}

static int mod_parse_range(const std::string& text, mod_version_range* out_range) {
    std::string trimmed = mod_trim(text);
    size_t dash = trimmed.find('-');
    if (!out_range) {
        return 1;
    }
    out_range->has_min = D_FALSE;
    out_range->has_max = D_FALSE;
    std::memset(&out_range->min, 0, sizeof(out_range->min));
    std::memset(&out_range->max, 0, sizeof(out_range->max));
    if (trimmed == "*" || trimmed == "any") {
        return 0;
    }
    if (dash == std::string::npos) {
        if (mod_semver_parse(trimmed.c_str(), &out_range->min) != 0) {
            return 1;
        }
        out_range->max = out_range->min;
        out_range->has_min = D_TRUE;
        out_range->has_max = D_TRUE;
        return 0;
    }
    std::string left = mod_trim(trimmed.substr(0, dash));
    std::string right = mod_trim(trimmed.substr(dash + 1u));
    if (!left.empty()) {
        if (mod_semver_parse(left.c_str(), &out_range->min) != 0) {
            return 1;
        }
        out_range->has_min = D_TRUE;
    }
    if (!right.empty()) {
        if (mod_semver_parse(right.c_str(), &out_range->max) != 0) {
            return 1;
        }
        out_range->has_max = D_TRUE;
    }
    return 0;
}

static int mod_parse_epoch_range(const std::string& text, mod_feature_epoch_req* out_req) {
    std::string trimmed = mod_trim(text);
    size_t dash = trimmed.find('-');
    if (!out_req) {
        return 1;
    }
    out_req->has_min = D_FALSE;
    out_req->has_max = D_FALSE;
    out_req->min_epoch = 0u;
    out_req->max_epoch = 0u;
    if (trimmed == "*" || trimmed == "any") {
        return 0;
    }
    if (dash == std::string::npos) {
        char* end = 0;
        unsigned long val = std::strtoul(trimmed.c_str(), &end, 10);
        if (end == trimmed.c_str() || *end != '\0') {
            return 1;
        }
        out_req->min_epoch = (u32)val;
        out_req->max_epoch = (u32)val;
        out_req->has_min = D_TRUE;
        out_req->has_max = D_TRUE;
        return 0;
    }
    std::string left = mod_trim(trimmed.substr(0, dash));
    std::string right = mod_trim(trimmed.substr(dash + 1u));
    if (!left.empty()) {
        char* end = 0;
        unsigned long val = std::strtoul(left.c_str(), &end, 10);
        if (end == left.c_str() || *end != '\0') {
            return 1;
        }
        out_req->min_epoch = (u32)val;
        out_req->has_min = D_TRUE;
    }
    if (!right.empty()) {
        char* end = 0;
        unsigned long val = std::strtoul(right.c_str(), &end, 10);
        if (end == right.c_str() || *end != '\0') {
            return 1;
        }
        out_req->max_epoch = (u32)val;
        out_req->has_max = D_TRUE;
    }
    return 0;
}

int mod_manifest_parse_text(const char* text,
                            mod_manifest* out_manifest,
                            mod_manifest_error* out_error) {
    const char* ptr = text;
    u32 line_no = 1u;
    d_bool has_id = D_FALSE;
    d_bool has_version = D_FALSE;
    d_bool has_hash = D_FALSE;
    if (!text || !out_manifest) {
        mod_set_error(out_error, MOD_MANIFEST_ERR_INVALID, 0u, "null input");
        return 1;
    }
    mod_manifest_init(out_manifest);
    while (*ptr) {
        const char* line_start = ptr;
        while (*ptr && *ptr != '\n') {
            ptr++;
        }
        std::string line(line_start, ptr - line_start);
        if (*ptr == '\n') {
            ptr++;
        }
        line = mod_trim(line);
        if (line.empty() || line[0] == '#' || line[0] == ';') {
            line_no++;
            continue;
        }
        size_t eq = line.find('=');
        if (eq == std::string::npos) {
            mod_set_error(out_error, MOD_MANIFEST_ERR_INVALID, line_no, "missing '='");
            return 1;
        }
        std::string key = mod_trim(line.substr(0, eq));
        std::string value = mod_trim(line.substr(eq + 1u));
        if (key == "mod_id") {
            mod_copy_string(out_manifest->mod_id, sizeof(out_manifest->mod_id), value);
            has_id = D_TRUE;
        } else if (key == "mod_version") {
            if (mod_semver_parse(value.c_str(), &out_manifest->mod_version) != 0) {
                mod_set_error(out_error, MOD_MANIFEST_ERR_BAD_VERSION, line_no, "bad mod_version");
                return 1;
            }
            has_version = D_TRUE;
        } else if (key == "sim_affecting") {
            std::string v = mod_trim(value);
            out_manifest->sim_affecting = (v == "1" || v == "true" || v == "yes") ? D_TRUE : D_FALSE;
        } else if (key == "perf_budget_class") {
            out_manifest->perf_budget_class = (u32)std::strtoul(value.c_str(), 0, 10);
        } else if (key == "schema_dep") {
            if (out_manifest->schema_dep_count >= DOM_MOD_MAX_SCHEMA_DEPS) {
                mod_set_error(out_error, MOD_MANIFEST_ERR_TOO_MANY, line_no, "schema_dep overflow");
                return 1;
            }
            size_t at = value.find('@');
            if (at == std::string::npos) {
                mod_set_error(out_error, MOD_MANIFEST_ERR_BAD_RANGE, line_no, "schema_dep missing @");
                return 1;
            }
            std::string id = mod_trim(value.substr(0, at));
            std::string range = mod_trim(value.substr(at + 1u));
            mod_schema_dependency* dep = &out_manifest->schema_deps[out_manifest->schema_dep_count++];
            mod_copy_string(dep->schema_id, sizeof(dep->schema_id), id);
            if (mod_parse_range(range, &dep->range) != 0) {
                mod_set_error(out_error, MOD_MANIFEST_ERR_BAD_RANGE, line_no, "bad schema_dep range");
                return 1;
            }
        } else if (key == "feature_epoch") {
            if (out_manifest->feature_epoch_count >= DOM_MOD_MAX_FEATURE_EPOCHS) {
                mod_set_error(out_error, MOD_MANIFEST_ERR_TOO_MANY, line_no, "feature_epoch overflow");
                return 1;
            }
            size_t at = value.find('@');
            if (at == std::string::npos) {
                mod_set_error(out_error, MOD_MANIFEST_ERR_BAD_RANGE, line_no, "feature_epoch missing @");
                return 1;
            }
            std::string id = mod_trim(value.substr(0, at));
            std::string range = mod_trim(value.substr(at + 1u));
            mod_feature_epoch_req* req = &out_manifest->feature_epochs[out_manifest->feature_epoch_count++];
            mod_copy_string(req->epoch_id, sizeof(req->epoch_id), id);
            if (mod_parse_epoch_range(range, req) != 0) {
                mod_set_error(out_error, MOD_MANIFEST_ERR_BAD_RANGE, line_no, "bad feature_epoch range");
                return 1;
            }
        } else if (key == "dependency") {
            if (out_manifest->dependency_count >= DOM_MOD_MAX_DEPENDENCIES) {
                mod_set_error(out_error, MOD_MANIFEST_ERR_TOO_MANY, line_no, "dependency overflow");
                return 1;
            }
            size_t at = value.find('@');
            if (at == std::string::npos) {
                mod_set_error(out_error, MOD_MANIFEST_ERR_BAD_RANGE, line_no, "dependency missing @");
                return 1;
            }
            std::string id = mod_trim(value.substr(0, at));
            std::string range = mod_trim(value.substr(at + 1u));
            mod_dependency* dep = &out_manifest->dependencies[out_manifest->dependency_count++];
            mod_copy_string(dep->mod_id, sizeof(dep->mod_id), id);
            if (mod_parse_range(range, &dep->range) != 0) {
                mod_set_error(out_error, MOD_MANIFEST_ERR_BAD_RANGE, line_no, "bad dependency range");
                return 1;
            }
        } else if (key == "conflict") {
            if (out_manifest->conflict_count >= DOM_MOD_MAX_CONFLICTS) {
                mod_set_error(out_error, MOD_MANIFEST_ERR_TOO_MANY, line_no, "conflict overflow");
                return 1;
            }
            size_t at = value.find('@');
            if (at == std::string::npos) {
                mod_set_error(out_error, MOD_MANIFEST_ERR_BAD_RANGE, line_no, "conflict missing @");
                return 1;
            }
            std::string id = mod_trim(value.substr(0, at));
            std::string range = mod_trim(value.substr(at + 1u));
            mod_conflict* conf = &out_manifest->conflicts[out_manifest->conflict_count++];
            mod_copy_string(conf->mod_id, sizeof(conf->mod_id), id);
            if (mod_parse_range(range, &conf->range) != 0) {
                mod_set_error(out_error, MOD_MANIFEST_ERR_BAD_RANGE, line_no, "bad conflict range");
                return 1;
            }
        } else if (key == "required_capability") {
            if (out_manifest->capability_count >= DOM_MOD_MAX_CAPABILITIES) {
                mod_set_error(out_error, MOD_MANIFEST_ERR_TOO_MANY, line_no, "capability overflow");
                return 1;
            }
            mod_required_capability* cap = &out_manifest->capabilities[out_manifest->capability_count++];
            mod_copy_string(cap->capability_id, sizeof(cap->capability_id), value);
        } else if (key == "render_feature") {
            if (out_manifest->render_feature_count >= DOM_MOD_MAX_CAPABILITIES) {
                mod_set_error(out_error, MOD_MANIFEST_ERR_TOO_MANY, line_no, "render feature overflow");
                return 1;
            }
            mod_required_feature* feat = &out_manifest->render_features[out_manifest->render_feature_count++];
            mod_copy_string(feat->feature_id, sizeof(feat->feature_id), value);
        } else if (key == "payload_hash") {
            mod_copy_string(out_manifest->payload_hash_str,
                            sizeof(out_manifest->payload_hash_str),
                            value);
            if (mod_parse_hash64(value.c_str(), &out_manifest->payload_hash_value) != 0) {
                mod_set_error(out_error, MOD_MANIFEST_ERR_BAD_HASH, line_no, "bad payload_hash");
                return 1;
            }
            has_hash = D_TRUE;
        } else {
            mod_set_error(out_error, MOD_MANIFEST_ERR_INVALID, line_no, "unknown key");
            return 1;
        }
        line_no++;
    }
    if (!has_id || !has_version || !has_hash) {
        mod_set_error(out_error, MOD_MANIFEST_ERR_MISSING_FIELD, line_no, "missing required field");
        return 1;
    }
    return 0;
}

int mod_manifest_validate(const mod_manifest* manifest, mod_manifest_error* out_error) {
    if (!manifest) {
        mod_set_error(out_error, MOD_MANIFEST_ERR_INVALID, 0u, "null manifest");
        return 1;
    }
    if (manifest->mod_id[0] == '\0') {
        mod_set_error(out_error, MOD_MANIFEST_ERR_MISSING_FIELD, 0u, "mod_id missing");
        return 1;
    }
    if (manifest->payload_hash_str[0] == '\0') {
        mod_set_error(out_error, MOD_MANIFEST_ERR_MISSING_FIELD, 0u, "payload_hash missing");
        return 1;
    }
    return 0;
}
