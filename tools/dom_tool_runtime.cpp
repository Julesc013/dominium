/*
FILE: source/dominium/tools/dom_tool_runtime.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/runtime
RESPONSIBILITY: Implements tool runtime harness enforcing handshake and path rules.
*/
#include "dom_tool_runtime.h"

#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

#include "dominium/caps_split.h"
#include "dominium/core_tlv.h"
#include "dom_caps.h"
#include "dom_paths.h"

extern "C" {
#include "domino/sys.h"
}

#if defined(_WIN32) || defined(_WIN64)
#include <direct.h>
#else
#include <sys/stat.h>
#endif

namespace dom {
namespace tools {

namespace {

enum {
    DOM_TOOL_REFUSAL_TLV_VERSION = 1u,
    DOM_TOOL_REFUSAL_TLV_TAG_CODE = 2u,
    DOM_TOOL_REFUSAL_TLV_TAG_MESSAGE = 3u,
    DOM_TOOL_REFUSAL_TLV_TAG_RUN_ID = 4u,
    DOM_TOOL_REFUSAL_TLV_TAG_INSTANCE_ID = 5u,
    DOM_TOOL_REFUSAL_TLV_TAG_TOOL_ID = 6u
};

static bool is_alpha(char c) {
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z');
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

static int dom_mkdir(const char *path) {
#if defined(_WIN32) || defined(_WIN64)
    return _mkdir(path);
#else
    return mkdir(path, 0755);
#endif
}

static bool mkdir_p(const std::string &path, std::string *err) {
    std::string p = normalize_seps(path);
    std::string prefix;
    std::string cur;
    size_t start = 0u;
    size_t i;
    std::string segment;

    if (p.empty()) {
        if (err) *err = "mkdir_p: empty path";
        return false;
    }

    if (p.size() >= 2u && is_alpha(p[0]) && p[1] == ':') {
        prefix.assign(p, 0u, 2u);
        start = 2u;
        if (start < p.size() && p[start] == '/') {
            prefix.push_back('/');
            start += 1u;
        }
    } else if (p.size() >= 2u && p[0] == '/' && p[1] == '/') {
        prefix = "//";
        start = 2u;
    } else if (p[0] == '/') {
        prefix = "/";
        start = 1u;
    }

    cur = prefix;
    for (i = start; i <= p.size(); ++i) {
        const char c = (i < p.size()) ? p[i] : '/';
        if (c == '/') {
            if (!segment.empty()) {
                if (!cur.empty() && cur[cur.size() - 1u] != '/') {
                    cur.push_back('/');
                }
                cur.append(segment);
                if (dom_mkdir(cur.c_str()) != 0) {
                    if (errno != EEXIST) {
                        if (err) {
                            *err = "mkdir_p: failed";
                        }
                        return false;
                    }
                }
                segment.clear();
            }
        } else {
            segment.push_back(c);
        }
    }

    return true;
}

static std::string sanitize_component(const std::string &in) {
    std::string out;
    size_t i;
    for (i = 0u; i < in.size(); ++i) {
        const char c = in[i];
        if (c == '/' || c == '\\' || c == ':' || c == '\0') {
            out.push_back('_');
        } else {
            out.push_back(c);
        }
    }
    if (out.empty()) {
        out = "unknown";
    }
    return out;
}

static bool write_bytes(const std::string &path,
                        const unsigned char *data,
                        size_t size,
                        std::string *err) {
    void *fh;
    size_t wrote;

    fh = dsys_file_open(path.c_str(), "wb");
    if (!fh) {
        if (err) *err = "write_bytes: open failed";
        return false;
    }
    wrote = 0u;
    if (size > 0u && data) {
        wrote = dsys_file_write(fh, data, size);
    }
    dsys_file_close(fh);
    if (wrote != size) {
        if (err) *err = "write_bytes: short write";
        return false;
    }
    return true;
}

static bool ensure_tool_root(const DomToolRuntime &rt,
                             std::string &out_dir,
                             std::string *err) {
    std::string run_root = dom_game_paths_get_run_root(rt.paths);
    std::string tool_id = sanitize_component(rt.tool_id);
    std::string tools_dir;

    if (run_root.empty()) {
        if (err) *err = "tool_output: missing run_root";
        return false;
    }
    tools_dir = dom::join(run_root, "tools");
    out_dir = dom::join(tools_dir, tool_id);

    if (!mkdir_p(tools_dir, err)) {
        return false;
    }
    if (!mkdir_p(out_dir, err)) {
        return false;
    }
    return true;
}

} // namespace

DomToolRuntime::DomToolRuntime()
    : tool_id(),
      handshake(),
      paths(),
      has_handshake(false),
      edit_mode(false),
      last_refusal(DOM_TOOL_REFUSAL_OK),
      last_error() {
}

bool tool_runtime_init(DomToolRuntime &rt,
                       const std::string &tool_id,
                       const std::string &handshake_rel,
                       u32 path_flags,
                       bool edit_mode,
                       std::string *err) {
    DomGamePaths tmp;
    std::string rel = handshake_rel.empty() ? std::string("handshake.tlv") : handshake_rel;
    std::string hs_path;

    rt = DomToolRuntime();
    rt.tool_id = tool_id;
    rt.edit_mode = edit_mode;

    if (!dom_game_paths_init_from_env(tmp, std::string(), 0ull, path_flags)) {
        rt.last_refusal = dom_game_paths_last_refusal(tmp);
        if (err) *err = "tool_runtime: path init failed";
        return false;
    }
    if (!dom_game_paths_resolve_rel(tmp, DOM_GAME_PATH_BASE_RUN_ROOT, rel, hs_path)) {
        rt.last_refusal = dom_game_paths_last_refusal(tmp);
        if (err) *err = "tool_runtime: handshake path refused";
        return false;
    }

    if (!dom_game_handshake_from_file(hs_path, rt.handshake)) {
        rt.last_refusal = DOM_TOOL_REFUSAL_HANDSHAKE_INVALID;
        if (err) *err = "tool_runtime: handshake parse failed";
        return false;
    }

    if (!dom_game_paths_init_from_env(rt.paths,
                                      rt.handshake.instance_id,
                                      rt.handshake.run_id,
                                      path_flags)) {
        rt.last_refusal = dom_game_paths_last_refusal(rt.paths);
        if (err) *err = "tool_runtime: path init failed";
        return false;
    }

    if (rt.handshake.instance_root_ref.has_value) {
        if (!dom_game_paths_set_instance_root_ref(rt.paths,
                                                  rt.handshake.instance_root_ref.base_kind,
                                                  rt.handshake.instance_root_ref.rel)) {
            rt.last_refusal = dom_game_paths_last_refusal(rt.paths);
            if (err) *err = "tool_runtime: instance root ref refused";
            return false;
        }
    }

    rt.has_handshake = true;
    return true;
}

bool tool_runtime_validate_identity(DomToolRuntime &rt,
                                    std::string *err) {
    DomSimCaps local_caps;
    dom_sim_caps_init_default(local_caps);
    if (!rt.has_handshake) {
        rt.last_refusal = DOM_TOOL_REFUSAL_HANDSHAKE_MISSING;
        if (err) *err = "tool_runtime: missing handshake";
        return false;
    }
    if (!dom_sim_caps_compatible(local_caps, rt.handshake.sim_caps)) {
        rt.last_refusal = DOM_TOOL_REFUSAL_SIM_CAPS_MISMATCH;
        if (err) *err = "tool_runtime: sim_caps mismatch";
        return false;
    }
    return true;
}

int tool_runtime_load_universe(DomToolRuntime &rt,
                               const DomGamePathRef &bundle_ref,
                               dom_universe_bundle **out_bundle,
                               dom_universe_bundle_identity *out_id,
                               std::string *err) {
    std::string abs_path;
    dom_universe_bundle *bundle;
    dom_universe_bundle_identity id;
    int rc;

    if (!out_bundle) {
        if (err) *err = "tool_runtime: out_bundle required";
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    *out_bundle = 0;
    if (!rt.has_handshake) {
        if (err) *err = "tool_runtime: missing handshake";
        rt.last_refusal = DOM_TOOL_REFUSAL_HANDSHAKE_MISSING;
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    if (!bundle_ref.has_value) {
        if (err) *err = "tool_runtime: missing bundle_ref";
        return DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT;
    }
    if (!dom_game_paths_resolve_rel(rt.paths, bundle_ref.base_kind, bundle_ref.rel, abs_path)) {
        rt.last_refusal = dom_game_paths_last_refusal(rt.paths);
        if (err) *err = "tool_runtime: bundle path refused";
        return DOM_UNIVERSE_BUNDLE_IO_ERROR;
    }

    bundle = dom_universe_bundle_create();
    if (!bundle) {
        if (err) *err = "tool_runtime: bundle alloc failed";
        return DOM_UNIVERSE_BUNDLE_NO_MEMORY;
    }
    rc = dom_universe_bundle_read_file(abs_path.c_str(), 0, bundle);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle);
        if (err) *err = "tool_runtime: bundle read failed";
        return rc;
    }

    if (dom_universe_bundle_get_identity(bundle, &id) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle);
        if (err) *err = "tool_runtime: bundle identity missing";
        return DOM_UNIVERSE_BUNDLE_INVALID_FORMAT;
    }

    if (!rt.handshake.instance_id.empty() && id.instance_id) {
        const std::string bid(id.instance_id, id.instance_id_len);
        if (bid != rt.handshake.instance_id) {
            dom_universe_bundle_destroy(bundle);
            rt.last_refusal = DOM_TOOL_REFUSAL_IDENTITY_MISMATCH;
            if (err) *err = "tool_runtime: bundle instance mismatch";
            return DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH;
        }
    }

    *out_bundle = bundle;
    if (out_id) {
        *out_id = id;
    }
    return DOM_UNIVERSE_BUNDLE_OK;
}

bool tool_runtime_emit_output(DomToolRuntime &rt,
                              const std::string &name,
                              const unsigned char *data,
                              size_t size,
                              std::string *err) {
    std::string out_dir;
    std::string rel;
    std::string abs;
    std::string tool_id = sanitize_component(rt.tool_id);

    if (name.empty()) {
        if (err) *err = "tool_output: empty name";
        return false;
    }
    if (!ensure_tool_root(rt, out_dir, err)) {
        return false;
    }
    rel = dom::join(dom::join("tools", tool_id), name);
    if (!dom_game_paths_resolve_rel(rt.paths, DOM_GAME_PATH_BASE_RUN_ROOT, rel, abs)) {
        rt.last_refusal = dom_game_paths_last_refusal(rt.paths);
        if (err) *err = "tool_output: path refused";
        return false;
    }

    return write_bytes(abs, data, size, err);
}

bool tool_runtime_refuse(DomToolRuntime &rt,
                         u32 code,
                         const std::string &message) {
    core_tlv::TlvWriter w;
    std::vector<unsigned char> bytes;

    w.add_u32(core_tlv::CORE_TLV_TAG_SCHEMA_VERSION, DOM_TOOL_REFUSAL_TLV_VERSION);
    w.add_u32(DOM_TOOL_REFUSAL_TLV_TAG_CODE, code);
    if (rt.handshake.run_id != 0ull) {
        w.add_u64(DOM_TOOL_REFUSAL_TLV_TAG_RUN_ID, rt.handshake.run_id);
    }
    if (!rt.handshake.instance_id.empty()) {
        w.add_string(DOM_TOOL_REFUSAL_TLV_TAG_INSTANCE_ID, rt.handshake.instance_id);
    }
    if (!rt.tool_id.empty()) {
        w.add_string(DOM_TOOL_REFUSAL_TLV_TAG_TOOL_ID, rt.tool_id);
    }
    if (!message.empty()) {
        w.add_string(DOM_TOOL_REFUSAL_TLV_TAG_MESSAGE, message);
    }

    bytes = w.bytes();
    return tool_runtime_emit_output(rt, "refusal.tlv",
                                    bytes.empty() ? 0 : &bytes[0],
                                    bytes.size(),
                                    0);
}

} // namespace tools
} // namespace dom
