/*
FILE: source/dominium/launcher/core/src/pack/launcher_pack_resolver.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (ecosystem) / pack_resolver
RESPONSIBILITY: Implements deterministic dependency resolution and simulation safety validation for pack-like content.
*/

#include "launcher_pack_resolver.h"

#include <cstdio>
#include <cstring>

#include "launcher_artifact_store.h"
#include "launcher_log.h"
#include "launcher_safety.h"
#include "launcher_tlv.h"

namespace dom {
namespace launcher_core {

namespace {

static const launcher_fs_api_v1* get_fs(const launcher_services_api_v1* services) {
    void* iface = 0;
    if (!services || !services->query_interface) {
        return 0;
    }
    if (services->query_interface(LAUNCHER_IID_FS_V1, &iface) != 0) {
        return 0;
    }
    return (const launcher_fs_api_v1*)iface;
}

static bool get_state_root(const launcher_fs_api_v1* fs, std::string& out_state_root) {
    char buf[260];
    if (!fs || !fs->get_path) {
        return false;
    }
    std::memset(buf, 0, sizeof(buf));
    if (!fs->get_path(LAUNCHER_FS_PATH_STATE, buf, sizeof(buf))) {
        return false;
    }
    out_state_root = std::string(buf);
    return !out_state_root.empty();
}

static void emit_pack_event(const launcher_services_api_v1* services,
                            const LauncherInstanceManifest& manifest,
                            const std::string& state_root_override,
                            u32 op_id,
                            u32 event_code,
                            const err_t* err) {
    core_log_event ev;
    core_log_scope scope;
    const bool safe_id = (!manifest.instance_id.empty() && launcher_is_safe_id_component(manifest.instance_id));

    core_log_event_clear(&ev);
    ev.domain = CORE_LOG_DOMAIN_PACKS;
    ev.code = (u16)event_code;
    ev.severity = (u8)((event_code == CORE_LOG_EVT_OP_FAIL) ? CORE_LOG_SEV_ERROR : CORE_LOG_SEV_INFO);
    ev.msg_id = 0u;
    ev.t_mono = 0u;
    (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_OPERATION_ID, op_id);
    if (err && !err_is_ok(err)) {
        launcher_log_add_err_fields(&ev, err);
    }

    std::memset(&scope, 0, sizeof(scope));
    scope.state_root = state_root_override.empty() ? (const char*)0 : state_root_override.c_str();
    if (safe_id) {
        scope.kind = CORE_LOG_SCOPE_INSTANCE;
        scope.instance_id = manifest.instance_id.c_str();
    } else {
        scope.kind = CORE_LOG_SCOPE_GLOBAL;
    }
    (void)launcher_services_emit_event(services, &scope, &ev);
}

static bool fs_read_all(const launcher_fs_api_v1* fs,
                        const std::string& path,
                        std::vector<unsigned char>& out_bytes) {
    void* fh;
    long sz;
    size_t got;

    out_bytes.clear();
    if (!fs || !fs->file_open || !fs->file_read || !fs->file_seek || !fs->file_tell || !fs->file_close) {
        return false;
    }
    fh = fs->file_open(path.c_str(), "rb");
    if (!fh) {
        return false;
    }
    if (fs->file_seek(fh, 0L, SEEK_END) != 0) {
        (void)fs->file_close(fh);
        return false;
    }
    sz = fs->file_tell(fh);
    if (sz < 0L) {
        (void)fs->file_close(fh);
        return false;
    }
    if (fs->file_seek(fh, 0L, SEEK_SET) != 0) {
        (void)fs->file_close(fh);
        return false;
    }

    out_bytes.resize((size_t)sz);
    got = 0u;
    if (sz > 0L) {
        got = fs->file_read(fh, &out_bytes[0], (size_t)sz);
    }
    (void)fs->file_close(fh);
    return got == (size_t)sz;
}

static bool is_pack_like_type(u32 content_type) {
    return content_type == (u32)LAUNCHER_CONTENT_PACK ||
           content_type == (u32)LAUNCHER_CONTENT_MOD ||
           content_type == (u32)LAUNCHER_CONTENT_RUNTIME;
}

static bool starts_with(const std::string& s, const char* prefix) {
    size_t n;
    if (!prefix) {
        return false;
    }
    n = std::strlen(prefix);
    if (s.size() < n) {
        return false;
    }
    return s.compare(0u, n, prefix) == 0;
}

static err_t pack_error_from_text(const std::string& text) {
    if (starts_with(text, "missing_services_or_fs")) {
        return err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_BAD_STATE);
    }
    if (starts_with(text, "missing_state_root")) {
        return err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_STATE_ROOT_UNAVAILABLE, 0u, (u32)ERRMSG_LAUNCHER_STATE_ROOT_UNAVAILABLE);
    }
    if (starts_with(text, "missing_required_pack")) {
        return err_make((u16)ERRD_PACKS, (u16)ERRC_PACKS_DEPENDENCY_MISSING, (u32)ERRF_USER_ACTIONABLE, (u32)ERRMSG_PACKS_DEPENDENCY_MISSING);
    }
    if (starts_with(text, "conflict_violation") ||
        starts_with(text, "required_version_mismatch") ||
        starts_with(text, "optional_version_mismatch") ||
        starts_with(text, "duplicate_pack_id") ||
        starts_with(text, "cycle_detected")) {
        return err_make((u16)ERRD_PACKS, (u16)ERRC_PACKS_DEPENDENCY_CONFLICT, (u32)ERRF_USER_ACTIONABLE, (u32)ERRMSG_PACKS_DEPENDENCY_CONFLICT);
    }
    if (starts_with(text, "pack_manifest_payload_missing") ||
        starts_with(text, "artifact_store_paths_failed")) {
        return err_make((u16)ERRD_PACKS, (u16)ERRC_PACKS_PACK_NOT_FOUND, 0u, (u32)ERRMSG_PACKS_PACK_NOT_FOUND);
    }
    if (starts_with(text, "pack_manifest_load_failed") ||
        starts_with(text, "pack_manifest_decode_failed") ||
        starts_with(text, "pack_manifest_invalid") ||
        starts_with(text, "pack_id_mismatch") ||
        starts_with(text, "pack_version_mismatch") ||
        starts_with(text, "pack_type_mismatch")) {
        return err_make((u16)ERRD_PACKS, (u16)ERRC_PACKS_PACK_INVALID, (u32)ERRF_INTEGRITY, (u32)ERRMSG_PACKS_PACK_INVALID);
    }
    if (starts_with(text, "sim_safety_resolve_failed")) {
        return err_make((u16)ERRD_PACKS, (u16)ERRC_PACKS_DEPENDENCY_CONFLICT, (u32)ERRF_USER_ACTIONABLE, (u32)ERRMSG_PACKS_DEPENDENCY_CONFLICT);
    }
    if (starts_with(text, "sim_affecting_pack_unpinned")) {
        return err_make((u16)ERRD_PACKS, (u16)ERRC_PACKS_SIM_FLAGS_MISSING, (u32)(ERRF_POLICY_REFUSAL | ERRF_USER_ACTIONABLE),
                        (u32)ERRMSG_PACKS_SIM_FLAGS_MISSING);
    }
    return err_make((u16)ERRD_PACKS, (u16)ERRC_PACKS_PACK_INVALID, (u32)ERRF_INTEGRITY, (u32)ERRMSG_PACKS_PACK_INVALID);
}

static u32 content_type_from_pack_type(u32 pack_type) {
    switch (pack_type) {
    case LAUNCHER_PACK_TYPE_CONTENT: return (u32)LAUNCHER_CONTENT_PACK;
    case LAUNCHER_PACK_TYPE_MOD: return (u32)LAUNCHER_CONTENT_MOD;
    case LAUNCHER_PACK_TYPE_RUNTIME: return (u32)LAUNCHER_CONTENT_RUNTIME;
    default: return (u32)LAUNCHER_CONTENT_UNKNOWN;
    }
}

static bool parse_uint(const std::string& s, size_t& io_pos, int& out_v) {
    unsigned long v = 0ul;
    size_t pos = io_pos;
    size_t start = pos;
    while (pos < s.size() && s[pos] >= '0' && s[pos] <= '9') {
        v = (v * 10ul) + (unsigned long)(s[pos] - '0');
        ++pos;
        if (v > 2147483647ul) {
            return false;
        }
    }
    if (pos == start) {
        return false;
    }
    out_v = (int)v;
    io_pos = pos;
    return true;
}

static bool parse_semver3(const std::string& s, int& out_major, int& out_minor, int& out_patch) {
    size_t pos = 0u;
    int maj = 0, min = 0, pat = 0;
    if (s.empty()) {
        return false;
    }
    if (!parse_uint(s, pos, maj)) {
        return false;
    }
    if (pos < s.size() && s[pos] == '.') {
        ++pos;
        if (!parse_uint(s, pos, min)) {
            return false;
        }
    }
    if (pos < s.size() && s[pos] == '.') {
        ++pos;
        if (!parse_uint(s, pos, pat)) {
            return false;
        }
    }
    out_major = maj;
    out_minor = min;
    out_patch = pat;
    return true;
}

static int compare_versions(const std::string& a, const std::string& b) {
    int amaj, amin, apat;
    int bmaj, bmin, bpat;
    bool ap = parse_semver3(a, amaj, amin, apat);
    bool bp = parse_semver3(b, bmaj, bmin, bpat);
    if (ap && bp) {
        if (amaj != bmaj) return (amaj < bmaj) ? -1 : 1;
        if (amin != bmin) return (amin < bmin) ? -1 : 1;
        if (apat != bpat) return (apat < bpat) ? -1 : 1;
        return 0;
    }
    if (a == b) return 0;
    return (a < b) ? -1 : 1;
}

static bool version_in_range(const std::string& v, const LauncherPackVersionRange& range) {
    if (!range.min_version.empty()) {
        if (compare_versions(v, range.min_version) < 0) {
            return false;
        }
    }
    if (!range.max_version.empty()) {
        if (compare_versions(v, range.max_version) > 0) {
            return false;
        }
    }
    return true;
}

static std::string range_to_string(const LauncherPackVersionRange& range) {
    std::string out = "[";
    out += range.min_version.empty() ? std::string("*") : range.min_version;
    out += ",";
    out += range.max_version.empty() ? std::string("*") : range.max_version;
    out += "]";
    return out;
}

static bool dep_less(const LauncherPackDependency& a, const LauncherPackDependency& b) {
    if (a.pack_id < b.pack_id) return true;
    if (b.pack_id < a.pack_id) return false;
    if (a.version_range.min_version < b.version_range.min_version) return true;
    if (b.version_range.min_version < a.version_range.min_version) return false;
    return a.version_range.max_version < b.version_range.max_version;
}

static void stable_sort_deps(std::vector<LauncherPackDependency>& v) {
    size_t i;
    for (i = 1u; i < v.size(); ++i) {
        LauncherPackDependency key = v[i];
        size_t j = i;
        while (j > 0u && dep_less(key, v[j - 1u])) {
            v[j] = v[j - 1u];
            --j;
        }
        v[j] = key;
    }
}

struct Node {
    std::string pack_id;
    u32 content_type;
    std::string version;
    std::vector<unsigned char> artifact_hash;

    u32 phase;
    i32 effective_order;

    std::vector<LauncherPackDependency> required;
    std::vector<LauncherPackDependency> optional;
    std::vector<LauncherPackDependency> conflicts;

    std::vector<std::string> sim_flags;

    Node() : pack_id(), content_type((u32)LAUNCHER_CONTENT_UNKNOWN), version(), artifact_hash(),
             phase((u32)LAUNCHER_PACK_PHASE_NORMAL), effective_order(0),
             required(), optional(), conflicts(), sim_flags() {}
};

static bool find_node_index_by_id(const std::vector<Node>& nodes, const std::string& id, size_t& out_idx) {
    size_t i;
    for (i = 0u; i < nodes.size(); ++i) {
        if (nodes[i].pack_id == id) {
            out_idx = i;
            return true;
        }
    }
    return false;
}

static void stable_sort_indices_by_pack_id(const std::vector<Node>& nodes, std::vector<size_t>& io_indices) {
    size_t i;
    for (i = 1u; i < io_indices.size(); ++i) {
        size_t key = io_indices[i];
        size_t j = i;
        while (j > 0u) {
            const Node& a = nodes[key];
            const Node& b = nodes[io_indices[j - 1u]];
            if (!(a.pack_id < b.pack_id)) {
                break;
            }
            io_indices[j] = io_indices[j - 1u];
            --j;
        }
        io_indices[j] = key;
    }
}

static int phase_rank(u32 phase) {
    switch (phase) {
    case LAUNCHER_PACK_PHASE_EARLY: return 0;
    case LAUNCHER_PACK_PHASE_NORMAL: return 1;
    case LAUNCHER_PACK_PHASE_LATE: return 2;
    default: return 3;
    }
}

static bool key_less(const Node& a, const Node& b) {
    const int ar = phase_rank(a.phase);
    const int br = phase_rank(b.phase);
    if (ar != br) return ar < br;
    if (a.effective_order != b.effective_order) return a.effective_order < b.effective_order;
    return a.pack_id < b.pack_id;
}

static bool load_pack_manifest_for_entry(const launcher_services_api_v1* services,
                                         const std::string& state_root,
                                         const LauncherContentEntry& entry,
                                         Node& out_node,
                                         std::string& out_error) {
    const launcher_fs_api_v1* fs = get_fs(services);
    std::string dir;
    std::string meta_path;
    std::string payload_path;
    std::vector<unsigned char> payload;
    LauncherPackManifest pm;
    std::string verr;
    u32 expected_type;

    out_error.clear();
    if (!services || !fs) {
        out_error = "missing_services_or_fs";
        return false;
    }
    if (!is_pack_like_type(entry.type)) {
        out_error = "not_pack_like_entry";
        return false;
    }
    if (entry.id.empty() || entry.version.empty()) {
        out_error = "bad_entry_id_or_version";
        return false;
    }
    if (entry.hash_bytes.empty()) {
        out_error = "missing_entry_hash_bytes";
        return false;
    }

    if (!launcher_artifact_store_paths(state_root, entry.hash_bytes, dir, meta_path, payload_path)) {
        out_error = "artifact_store_paths_failed";
        return false;
    }
    if (!fs_read_all(fs, payload_path, payload)) {
        out_error = std::string("pack_manifest_payload_missing;path=") + payload_path;
        return false;
    }
    if (!launcher_pack_manifest_from_tlv_bytes(payload.empty() ? (const unsigned char*)0 : &payload[0], payload.size(), pm)) {
        out_error = "pack_manifest_decode_failed";
        return false;
    }
    if (!launcher_pack_manifest_validate(pm, &verr)) {
        out_error = std::string("pack_manifest_invalid;") + verr;
        return false;
    }

    if (pm.pack_id != entry.id) {
        out_error = std::string("pack_id_mismatch;expected=") + entry.id + ";got=" + pm.pack_id;
        return false;
    }
    if (pm.version != entry.version) {
        out_error = std::string("pack_version_mismatch;expected=") + entry.version + ";got=" + pm.version;
        return false;
    }
    expected_type = content_type_from_pack_type(pm.pack_type);
    if (expected_type != entry.type) {
        out_error = std::string("pack_type_mismatch;expected=") + std::string(entry.type == (u32)LAUNCHER_CONTENT_PACK ? "pack" :
                                                                             entry.type == (u32)LAUNCHER_CONTENT_MOD ? "mod" :
                                                                             entry.type == (u32)LAUNCHER_CONTENT_RUNTIME ? "runtime" : "unknown") +
                    ";got=" + std::string(expected_type == (u32)LAUNCHER_CONTENT_PACK ? "pack" :
                                          expected_type == (u32)LAUNCHER_CONTENT_MOD ? "mod" :
                                          expected_type == (u32)LAUNCHER_CONTENT_RUNTIME ? "runtime" : "unknown");
        return false;
    }

    out_node.pack_id = pm.pack_id;
    out_node.content_type = entry.type;
    out_node.version = pm.version;
    out_node.artifact_hash = entry.hash_bytes;
    out_node.phase = pm.phase;
    out_node.effective_order = entry.has_explicit_order_override ? entry.explicit_order_override : pm.explicit_order;
    out_node.required = pm.required_packs;
    out_node.optional = pm.optional_packs;
    out_node.conflicts = pm.conflicts;
    out_node.sim_flags = pm.sim_affecting_flags;
    return true;
}

} /* namespace */

LauncherResolvedPack::LauncherResolvedPack()
    : pack_id(),
      content_type((u32)LAUNCHER_CONTENT_UNKNOWN),
      version(),
      artifact_hash_bytes(),
      phase((u32)LAUNCHER_PACK_PHASE_NORMAL),
      effective_order(0),
      sim_affecting_flags() {
}

bool launcher_pack_resolve_enabled(const launcher_services_api_v1* services,
                                   const LauncherInstanceManifest& manifest,
                                   const std::string& state_root_override,
                                   std::vector<LauncherResolvedPack>& out_ordered,
                                   std::string* out_error) {
    const launcher_fs_api_v1* fs = get_fs(services);
    std::string state_root;
    std::vector<Node> nodes;
    std::vector<std::string> duplicate_ids;
    std::vector<size_t> order_nodes;
    std::vector< std::vector<size_t> > edges;
    std::vector<u32> indeg;
    std::vector<size_t> ready;
    std::vector<size_t> topo;
    size_t i;

    out_ordered.clear();
    if (out_error) {
        out_error->clear();
    }

    if (!services || !fs) {
        if (out_error) *out_error = "missing_services_or_fs";
        return false;
    }
    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        if (out_error) *out_error = "missing_state_root";
        return false;
    }

    /* Collect enabled pack-like nodes and validate their pack manifests. */
    for (i = 0u; i < manifest.content_entries.size(); ++i) {
        const LauncherContentEntry& e = manifest.content_entries[i];
        Node n;
        std::string err;
        size_t existing;

        if (e.enabled == 0u) {
            continue;
        }
        if (!is_pack_like_type(e.type)) {
            continue;
        }

        if (find_node_index_by_id(nodes, e.id, existing)) {
            duplicate_ids.push_back(e.id);
            continue;
        }

        if (!load_pack_manifest_for_entry(services, state_root, e, n, err)) {
            if (out_error) {
                *out_error = std::string("pack_manifest_load_failed;pack_id=") + e.id + ";" + err;
            }
            return false;
        }
        nodes.push_back(n);
    }

    if (!duplicate_ids.empty()) {
        /* Deterministic: report the smallest duplicated id. */
        size_t j;
        for (j = 1u; j < duplicate_ids.size(); ++j) {
            std::string key = duplicate_ids[j];
            size_t k = j;
            while (k > 0u && key < duplicate_ids[k - 1u]) {
                duplicate_ids[k] = duplicate_ids[k - 1u];
                --k;
            }
            duplicate_ids[k] = key;
        }
        if (out_error) {
            *out_error = std::string("duplicate_pack_id;pack_id=") + duplicate_ids[0];
        }
        return false;
    }

    /* Build deterministic node index order for validation. */
    order_nodes.clear();
    for (i = 0u; i < nodes.size(); ++i) {
        order_nodes.push_back(i);
    }
    stable_sort_indices_by_pack_id(nodes, order_nodes);

    /* Build dependency edges and enforce constraints strictly. */
    edges.assign(nodes.size(), std::vector<size_t>());
    indeg.assign(nodes.size(), 0u);

    for (size_t oi = 0u; oi < order_nodes.size(); ++oi) {
        const size_t nidx = order_nodes[oi];
        Node& n = nodes[nidx];
        std::vector<LauncherPackDependency> req = n.required;
        std::vector<LauncherPackDependency> opt = n.optional;
        std::vector<LauncherPackDependency> conf = n.conflicts;

        stable_sort_deps(req);
        stable_sort_deps(opt);
        stable_sort_deps(conf);

        for (size_t di = 0u; di < conf.size(); ++di) {
            size_t dep_idx;
            if (find_node_index_by_id(nodes, conf[di].pack_id, dep_idx)) {
                const Node& target = nodes[dep_idx];
                if (version_in_range(target.version, conf[di].version_range)) {
                    if (out_error) {
                        *out_error = std::string("conflict_violation;pack_id=") + n.pack_id +
                                     ";conflicts_with=" + target.pack_id +
                                     ";range=" + range_to_string(conf[di].version_range) +
                                     ";found_version=" + target.version;
                    }
                    return false;
                }
            }
        }

        for (size_t di = 0u; di < req.size(); ++di) {
            size_t dep_idx;
            if (!find_node_index_by_id(nodes, req[di].pack_id, dep_idx)) {
                if (out_error) {
                    *out_error = std::string("missing_required_pack;pack_id=") + n.pack_id +
                                 ";requires=" + req[di].pack_id +
                                 ";range=" + range_to_string(req[di].version_range);
                }
                return false;
            }
            if (!version_in_range(nodes[dep_idx].version, req[di].version_range)) {
                if (out_error) {
                    *out_error = std::string("required_version_mismatch;pack_id=") + n.pack_id +
                                 ";requires=" + req[di].pack_id +
                                 ";range=" + range_to_string(req[di].version_range) +
                                 ";found_version=" + nodes[dep_idx].version;
                }
                return false;
            }

            /* Edge: dep -> n (dep must load before dependent). */
            edges[dep_idx].push_back(nidx);
            indeg[nidx] += 1u;
        }

        for (size_t di = 0u; di < opt.size(); ++di) {
            size_t dep_idx;
            if (!find_node_index_by_id(nodes, opt[di].pack_id, dep_idx)) {
                continue; /* optional not present */
            }
            if (!version_in_range(nodes[dep_idx].version, opt[di].version_range)) {
                if (out_error) {
                    *out_error = std::string("optional_version_mismatch;pack_id=") + n.pack_id +
                                 ";optional=" + opt[di].pack_id +
                                 ";range=" + range_to_string(opt[di].version_range) +
                                 ";found_version=" + nodes[dep_idx].version;
                }
                return false;
            }
            edges[dep_idx].push_back(nidx);
            indeg[nidx] += 1u;
        }
    }

    /* Kahn topological sort with deterministic selection. */
    ready.clear();
    for (i = 0u; i < nodes.size(); ++i) {
        if (indeg[i] == 0u) {
            ready.push_back(i);
        }
    }

    topo.clear();
    while (!ready.empty()) {
        size_t best_pos = 0u;
        size_t best_idx = ready[0];
        for (size_t rp = 1u; rp < ready.size(); ++rp) {
            size_t cand = ready[rp];
            if (key_less(nodes[cand], nodes[best_idx])) {
                best_idx = cand;
                best_pos = rp;
            }
        }

        topo.push_back(best_idx);
        ready[best_pos] = ready[ready.size() - 1u];
        ready.pop_back();

        for (size_t ei = 0u; ei < edges[best_idx].size(); ++ei) {
            size_t to = edges[best_idx][ei];
            if (indeg[to] > 0u) {
                indeg[to] -= 1u;
                if (indeg[to] == 0u) {
                    ready.push_back(to);
                }
            }
        }
    }

    if (topo.size() != nodes.size()) {
        /* Cycle or duplicate edges: report remaining nodes deterministically. */
        std::vector<size_t> remaining;
        for (i = 0u; i < nodes.size(); ++i) {
            if (indeg[i] != 0u) {
                remaining.push_back(i);
            }
        }
        stable_sort_indices_by_pack_id(nodes, remaining);
        if (out_error) {
            std::string msg = "cycle_detected;remaining=";
            for (i = 0u; i < remaining.size(); ++i) {
                if (i) msg += ",";
                msg += nodes[remaining[i]].pack_id;
            }
            *out_error = msg;
        }
        return false;
    }

    /* Emit resolved order. */
    for (i = 0u; i < topo.size(); ++i) {
        const Node& n = nodes[topo[i]];
        LauncherResolvedPack rp;
        rp.pack_id = n.pack_id;
        rp.content_type = n.content_type;
        rp.version = n.version;
        rp.artifact_hash_bytes = n.artifact_hash;
        rp.phase = n.phase;
        rp.effective_order = n.effective_order;
        rp.sim_affecting_flags = n.sim_flags;
        out_ordered.push_back(rp);
    }

    return true;
}

bool launcher_pack_validate_simulation_safety(const launcher_services_api_v1* services,
                                              const LauncherInstanceManifest& manifest,
                                              const std::string& state_root_override,
                                              std::string* out_error) {
    std::vector<LauncherResolvedPack> ordered;
    std::string err;
    size_t i;

    if (out_error) {
        out_error->clear();
    }

    if (!launcher_pack_resolve_enabled(services, manifest, state_root_override, ordered, &err)) {
        if (out_error) {
            *out_error = std::string("sim_safety_resolve_failed;") + err;
        }
        return false;
    }

    for (i = 0u; i < ordered.size(); ++i) {
        const LauncherResolvedPack& p = ordered[i];
        if (p.sim_affecting_flags.empty()) {
            continue;
        }
        if (p.artifact_hash_bytes.empty()) {
            if (out_error) {
                *out_error = std::string("sim_affecting_pack_unpinned;pack_id=") + p.pack_id;
            }
            return false;
        }
    }

    return true;
}

bool launcher_pack_resolve_enabled_ex(const launcher_services_api_v1* services,
                                      const LauncherInstanceManifest& manifest,
                                      const std::string& state_root_override,
                                      std::vector<LauncherResolvedPack>& out_ordered,
                                      err_t* out_err) {
    std::string err;
    if (launcher_pack_resolve_enabled(services, manifest, state_root_override, out_ordered, &err)) {
        if (out_err) {
            *out_err = err_ok();
        }
        emit_pack_event(services, manifest, state_root_override,
                        CORE_LOG_OP_LAUNCHER_PACK_RESOLVE, CORE_LOG_EVT_OP_OK, (const err_t*)0);
        return true;
    }
    if (out_err) {
        *out_err = pack_error_from_text(err);
    }
    {
        err_t e = pack_error_from_text(err);
        emit_pack_event(services, manifest, state_root_override,
                        CORE_LOG_OP_LAUNCHER_PACK_RESOLVE, CORE_LOG_EVT_OP_FAIL, &e);
    }
    return false;
}

bool launcher_pack_validate_simulation_safety_ex(const launcher_services_api_v1* services,
                                                 const LauncherInstanceManifest& manifest,
                                                 const std::string& state_root_override,
                                                 err_t* out_err) {
    std::string err;
    if (launcher_pack_validate_simulation_safety(services, manifest, state_root_override, &err)) {
        if (out_err) {
            *out_err = err_ok();
        }
        emit_pack_event(services, manifest, state_root_override,
                        CORE_LOG_OP_LAUNCHER_SIM_SAFETY_VALIDATE, CORE_LOG_EVT_OP_OK, (const err_t*)0);
        return true;
    }
    if (out_err) {
        *out_err = pack_error_from_text(err);
    }
    {
        err_t e = pack_error_from_text(err);
        emit_pack_event(services, manifest, state_root_override,
                        CORE_LOG_OP_LAUNCHER_SIM_SAFETY_VALIDATE, CORE_LOG_EVT_OP_FAIL, &e);
    }
    return false;
}

std::string launcher_pack_resolved_order_summary(const std::vector<LauncherResolvedPack>& ordered) {
    std::string out;
    size_t i;
    for (i = 0u; i < ordered.size(); ++i) {
        if (i) out += ",";
        out += ordered[i].pack_id;
    }
    return out;
}

} /* namespace launcher_core */
} /* namespace dom */
