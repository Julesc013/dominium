/*
FILE: source/dominium/launcher/core/src/pack/launcher_pack_manifest.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (ecosystem) / pack_manifest
RESPONSIBILITY: Implements pack manifest TLV encode/decode + validation (deterministic; skip-unknown).
*/

#include "launcher_pack_manifest.h"

#include <cstring>

#include "launcher_tlv.h"
#include "launcher_tlv_migrations.h"

namespace dom {
namespace launcher_core {

namespace {

static void tlv_unknown_capture(std::vector<LauncherTlvUnknownRecord>& dst, const TlvRecord& rec) {
    LauncherTlvUnknownRecord u;
    u.tag = rec.tag;
    u.payload.clear();
    if (rec.len > 0u && rec.payload) {
        u.payload.assign(rec.payload, rec.payload + (size_t)rec.len);
    }
    dst.push_back(u);
}

static void tlv_unknown_emit(TlvWriter& w, const std::vector<LauncherTlvUnknownRecord>& src) {
    size_t i;
    for (i = 0u; i < src.size(); ++i) {
        if (!src[i].payload.empty()) {
            w.add_bytes(src[i].tag, &src[i].payload[0], (u32)src[i].payload.size());
        } else {
            w.add_bytes(src[i].tag, (const unsigned char*)0, 0u);
        }
    }
}

static void stable_sort_strings(std::vector<std::string>& v) {
    size_t i;
    for (i = 1u; i < v.size(); ++i) {
        std::string key = v[i];
        size_t j = i;
        while (j > 0u && key < v[j - 1u]) {
            v[j] = v[j - 1u];
            --j;
        }
        v[j] = key;
    }
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

static bool range_to_tlv_bytes(const LauncherPackVersionRange& range, std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    if (!range.min_version.empty()) {
        w.add_string((u32)LAUNCHER_PACK_RANGE_TLV_TAG_MIN, range.min_version);
    }
    if (!range.max_version.empty()) {
        w.add_string((u32)LAUNCHER_PACK_RANGE_TLV_TAG_MAX, range.max_version);
    }
    tlv_unknown_emit(w, range.unknown_fields);
    out_bytes = w.bytes();
    return true;
}

static bool range_from_tlv_bytes(const unsigned char* data, size_t size, LauncherPackVersionRange& out_range) {
    TlvReader r(data, size);
    TlvRecord rec;
    LauncherPackVersionRange range;
    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_PACK_RANGE_TLV_TAG_MIN:
            range.min_version = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_PACK_RANGE_TLV_TAG_MAX:
            range.max_version = tlv_read_string(rec.payload, rec.len);
            break;
        default:
            tlv_unknown_capture(range.unknown_fields, rec);
            break;
        }
    }
    out_range = range;
    return true;
}

static bool dep_to_tlv_bytes(const LauncherPackDependency& dep, std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    std::vector<unsigned char> range_bytes;
    w.add_string((u32)LAUNCHER_PACK_DEP_TLV_TAG_ID, dep.pack_id);
    (void)range_to_tlv_bytes(dep.version_range, range_bytes);
    w.add_container((u32)LAUNCHER_PACK_DEP_TLV_TAG_RANGE, range_bytes);
    tlv_unknown_emit(w, dep.unknown_fields);
    out_bytes = w.bytes();
    return true;
}

static bool dep_from_tlv_bytes(const unsigned char* data, size_t size, LauncherPackDependency& out_dep) {
    TlvReader r(data, size);
    TlvRecord rec;
    LauncherPackDependency dep;
    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_PACK_DEP_TLV_TAG_ID:
            dep.pack_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_PACK_DEP_TLV_TAG_RANGE:
            (void)range_from_tlv_bytes(rec.payload, (size_t)rec.len, dep.version_range);
            break;
        default:
            tlv_unknown_capture(dep.unknown_fields, rec);
            break;
        }
    }
    out_dep = dep;
    return true;
}

static bool task_to_tlv_bytes(const LauncherPackTask& task, std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    w.add_u32((u32)LAUNCHER_PACK_TASK_TLV_TAG_KIND, task.kind);
    w.add_string((u32)LAUNCHER_PACK_TASK_TLV_TAG_PATH, task.path);
    tlv_unknown_emit(w, task.unknown_fields);
    out_bytes = w.bytes();
    return true;
}

static bool task_from_tlv_bytes(const unsigned char* data, size_t size, LauncherPackTask& out_task) {
    TlvReader r(data, size);
    TlvRecord rec;
    LauncherPackTask task;
    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_PACK_TASK_TLV_TAG_KIND: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                task.kind = v;
            }
            break;
        }
        case LAUNCHER_PACK_TASK_TLV_TAG_PATH:
            task.path = tlv_read_string(rec.payload, rec.len);
            break;
        default:
            tlv_unknown_capture(task.unknown_fields, rec);
            break;
        }
    }
    out_task = task;
    return true;
}

static bool string_in_list(const std::vector<std::string>& v, const std::string& s) {
    size_t i;
    for (i = 0u; i < v.size(); ++i) {
        if (v[i] == s) {
            return true;
        }
    }
    return false;
}

} /* namespace */

LauncherPackVersionRange::LauncherPackVersionRange()
    : min_version(),
      max_version(),
      unknown_fields() {
}

LauncherPackDependency::LauncherPackDependency()
    : pack_id(),
      version_range(),
      unknown_fields() {
}

LauncherPackTask::LauncherPackTask()
    : kind((u32)LAUNCHER_PACK_TASK_REQUIRE_FILE),
      path(),
      unknown_fields() {
}

LauncherPackManifest::LauncherPackManifest()
    : schema_version(LAUNCHER_PACK_MANIFEST_TLV_VERSION),
      pack_id(),
      pack_type((u32)LAUNCHER_PACK_TYPE_CONTENT),
      version(),
      pack_hash_bytes(),
      compatible_engine_range(),
      compatible_game_range(),
      has_compatible_engine_range(1u),
      has_compatible_game_range(1u),
      required_packs(),
      optional_packs(),
      conflicts(),
      phase((u32)LAUNCHER_PACK_PHASE_NORMAL),
      explicit_order(0),
      declared_capabilities(),
      sim_affecting_flags(),
      install_tasks(),
      verify_tasks(),
      prelaunch_tasks(),
      unknown_fields() {
}

bool launcher_pack_manifest_to_tlv_bytes(const LauncherPackManifest& manifest,
                                         std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    std::vector<unsigned char> tmp;
    std::vector<std::string> caps;
    std::vector<std::string> sim;
    std::vector<LauncherPackDependency> req;
    std::vector<LauncherPackDependency> opt;
    std::vector<LauncherPackDependency> conf;
    size_t i;

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_PACK_MANIFEST_TLV_VERSION);
    w.add_string((u32)LAUNCHER_PACK_TLV_TAG_PACK_ID, manifest.pack_id);
    w.add_u32((u32)LAUNCHER_PACK_TLV_TAG_PACK_TYPE, manifest.pack_type);
    w.add_string((u32)LAUNCHER_PACK_TLV_TAG_VERSION, manifest.version);
    if (!manifest.pack_hash_bytes.empty()) {
        w.add_bytes((u32)LAUNCHER_PACK_TLV_TAG_PACK_HASH_BYTES, &manifest.pack_hash_bytes[0], (u32)manifest.pack_hash_bytes.size());
    } else {
        w.add_bytes((u32)LAUNCHER_PACK_TLV_TAG_PACK_HASH_BYTES, (const unsigned char*)0, 0u);
    }

    tmp.clear();
    (void)range_to_tlv_bytes(manifest.compatible_engine_range, tmp);
    w.add_container((u32)LAUNCHER_PACK_TLV_TAG_COMPAT_ENGINE_RANGE, tmp);
    tmp.clear();
    (void)range_to_tlv_bytes(manifest.compatible_game_range, tmp);
    w.add_container((u32)LAUNCHER_PACK_TLV_TAG_COMPAT_GAME_RANGE, tmp);

    w.add_u32((u32)LAUNCHER_PACK_TLV_TAG_PHASE, manifest.phase);
    w.add_i32((u32)LAUNCHER_PACK_TLV_TAG_EXPLICIT_ORDER, manifest.explicit_order);

    req = manifest.required_packs;
    opt = manifest.optional_packs;
    conf = manifest.conflicts;
    stable_sort_deps(req);
    stable_sort_deps(opt);
    stable_sort_deps(conf);

    for (i = 0u; i < req.size(); ++i) {
        tmp.clear();
        (void)dep_to_tlv_bytes(req[i], tmp);
        w.add_container((u32)LAUNCHER_PACK_TLV_TAG_REQUIRED_DEP, tmp);
    }
    for (i = 0u; i < opt.size(); ++i) {
        tmp.clear();
        (void)dep_to_tlv_bytes(opt[i], tmp);
        w.add_container((u32)LAUNCHER_PACK_TLV_TAG_OPTIONAL_DEP, tmp);
    }
    for (i = 0u; i < conf.size(); ++i) {
        tmp.clear();
        (void)dep_to_tlv_bytes(conf[i], tmp);
        w.add_container((u32)LAUNCHER_PACK_TLV_TAG_CONFLICT, tmp);
    }

    caps = manifest.declared_capabilities;
    sim = manifest.sim_affecting_flags;
    stable_sort_strings(caps);
    stable_sort_strings(sim);
    for (i = 0u; i < caps.size(); ++i) {
        w.add_string((u32)LAUNCHER_PACK_TLV_TAG_CAPABILITY, caps[i]);
    }
    for (i = 0u; i < sim.size(); ++i) {
        w.add_string((u32)LAUNCHER_PACK_TLV_TAG_SIM_FLAG, sim[i]);
    }

    for (i = 0u; i < manifest.install_tasks.size(); ++i) {
        tmp.clear();
        (void)task_to_tlv_bytes(manifest.install_tasks[i], tmp);
        w.add_container((u32)LAUNCHER_PACK_TLV_TAG_INSTALL_TASK, tmp);
    }
    for (i = 0u; i < manifest.verify_tasks.size(); ++i) {
        tmp.clear();
        (void)task_to_tlv_bytes(manifest.verify_tasks[i], tmp);
        w.add_container((u32)LAUNCHER_PACK_TLV_TAG_VERIFY_TASK, tmp);
    }
    for (i = 0u; i < manifest.prelaunch_tasks.size(); ++i) {
        tmp.clear();
        (void)task_to_tlv_bytes(manifest.prelaunch_tasks[i], tmp);
        w.add_container((u32)LAUNCHER_PACK_TLV_TAG_PRELAUNCH_TASK, tmp);
    }

    tlv_unknown_emit(w, manifest.unknown_fields);
    out_bytes = w.bytes();
    return true;
}

bool launcher_pack_manifest_from_tlv_bytes(const unsigned char* data,
                                           size_t size,
                                           LauncherPackManifest& out_manifest) {
    u32 version = 1u;
    TlvReader r(data, size);
    TlvRecord rec;
    LauncherPackManifest m;

    if (!data || size == 0u) {
        return false;
    }
    if (!tlv_read_schema_version_or_default(data,
                                            size,
                                            version,
                                            launcher_tlv_schema_min_version(LAUNCHER_TLV_SCHEMA_PACK_MANIFEST))) {
        return false;
    }
    if (!launcher_tlv_schema_accepts_version(LAUNCHER_TLV_SCHEMA_PACK_MANIFEST, version)) {
        return false;
    }
    if (version != LAUNCHER_PACK_MANIFEST_TLV_VERSION) {
        return false;
    }

    /* Presence flags default to 1 for in-memory construction; reset for decode. */
    m.has_compatible_engine_range = 0u;
    m.has_compatible_game_range = 0u;

    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_TLV_TAG_SCHEMA_VERSION:
            break;
        case LAUNCHER_PACK_TLV_TAG_PACK_ID:
            m.pack_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_PACK_TLV_TAG_PACK_TYPE: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                m.pack_type = v;
            }
            break;
        }
        case LAUNCHER_PACK_TLV_TAG_VERSION:
            m.version = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_PACK_TLV_TAG_PACK_HASH_BYTES:
            m.pack_hash_bytes.clear();
            if (rec.len > 0u && rec.payload) {
                m.pack_hash_bytes.assign(rec.payload, rec.payload + (size_t)rec.len);
            }
            break;
        case LAUNCHER_PACK_TLV_TAG_COMPAT_ENGINE_RANGE:
            m.has_compatible_engine_range = 1u;
            (void)range_from_tlv_bytes(rec.payload, (size_t)rec.len, m.compatible_engine_range);
            break;
        case LAUNCHER_PACK_TLV_TAG_COMPAT_GAME_RANGE:
            m.has_compatible_game_range = 1u;
            (void)range_from_tlv_bytes(rec.payload, (size_t)rec.len, m.compatible_game_range);
            break;
        case LAUNCHER_PACK_TLV_TAG_REQUIRED_DEP: {
            LauncherPackDependency d;
            (void)dep_from_tlv_bytes(rec.payload, (size_t)rec.len, d);
            m.required_packs.push_back(d);
            break;
        }
        case LAUNCHER_PACK_TLV_TAG_OPTIONAL_DEP: {
            LauncherPackDependency d;
            (void)dep_from_tlv_bytes(rec.payload, (size_t)rec.len, d);
            m.optional_packs.push_back(d);
            break;
        }
        case LAUNCHER_PACK_TLV_TAG_CONFLICT: {
            LauncherPackDependency d;
            (void)dep_from_tlv_bytes(rec.payload, (size_t)rec.len, d);
            m.conflicts.push_back(d);
            break;
        }
        case LAUNCHER_PACK_TLV_TAG_PHASE: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                m.phase = v;
            }
            break;
        }
        case LAUNCHER_PACK_TLV_TAG_EXPLICIT_ORDER: {
            i32 v;
            if (tlv_read_i32_le(rec.payload, rec.len, v)) {
                m.explicit_order = v;
            }
            break;
        }
        case LAUNCHER_PACK_TLV_TAG_CAPABILITY:
            m.declared_capabilities.push_back(tlv_read_string(rec.payload, rec.len));
            break;
        case LAUNCHER_PACK_TLV_TAG_SIM_FLAG:
            m.sim_affecting_flags.push_back(tlv_read_string(rec.payload, rec.len));
            break;
        case LAUNCHER_PACK_TLV_TAG_INSTALL_TASK: {
            LauncherPackTask t;
            (void)task_from_tlv_bytes(rec.payload, (size_t)rec.len, t);
            m.install_tasks.push_back(t);
            break;
        }
        case LAUNCHER_PACK_TLV_TAG_VERIFY_TASK: {
            LauncherPackTask t;
            (void)task_from_tlv_bytes(rec.payload, (size_t)rec.len, t);
            m.verify_tasks.push_back(t);
            break;
        }
        case LAUNCHER_PACK_TLV_TAG_PRELAUNCH_TASK: {
            LauncherPackTask t;
            (void)task_from_tlv_bytes(rec.payload, (size_t)rec.len, t);
            m.prelaunch_tasks.push_back(t);
            break;
        }
        default:
            tlv_unknown_capture(m.unknown_fields, rec);
            break;
        }
    }

    m.schema_version = LAUNCHER_PACK_MANIFEST_TLV_VERSION;
    out_manifest = m;
    return true;
}

bool launcher_pack_manifest_validate(const LauncherPackManifest& manifest,
                                     std::string* out_error) {
    size_t i;
    if (out_error) {
        out_error->clear();
    }

    if (manifest.schema_version != LAUNCHER_PACK_MANIFEST_TLV_VERSION) {
        if (out_error) *out_error = "unsupported_schema_version";
        return false;
    }
    if (manifest.pack_id.empty()) {
        if (out_error) *out_error = "missing_pack_id";
        return false;
    }
    if (manifest.pack_type != (u32)LAUNCHER_PACK_TYPE_CONTENT &&
        manifest.pack_type != (u32)LAUNCHER_PACK_TYPE_MOD &&
        manifest.pack_type != (u32)LAUNCHER_PACK_TYPE_RUNTIME) {
        if (out_error) *out_error = "invalid_pack_type";
        return false;
    }
    if (manifest.version.empty()) {
        if (out_error) *out_error = "missing_version";
        return false;
    }
    if (manifest.pack_hash_bytes.empty()) {
        if (out_error) *out_error = "missing_pack_hash";
        return false;
    }
    if (!manifest.has_compatible_engine_range || !manifest.has_compatible_game_range) {
        if (out_error) *out_error = "missing_compatible_range";
        return false;
    }
    if (manifest.phase != (u32)LAUNCHER_PACK_PHASE_EARLY &&
        manifest.phase != (u32)LAUNCHER_PACK_PHASE_NORMAL &&
        manifest.phase != (u32)LAUNCHER_PACK_PHASE_LATE) {
        if (out_error) *out_error = "invalid_phase";
        return false;
    }

    for (i = 0u; i < manifest.sim_affecting_flags.size(); ++i) {
        if (!string_in_list(manifest.declared_capabilities, manifest.sim_affecting_flags[i])) {
            if (out_error) {
                *out_error = std::string("sim_flag_not_declared:") + manifest.sim_affecting_flags[i];
            }
            return false;
        }
    }

    for (i = 0u; i < manifest.required_packs.size(); ++i) {
        if (manifest.required_packs[i].pack_id.empty()) {
            if (out_error) *out_error = "required_dep_missing_id";
            return false;
        }
    }
    for (i = 0u; i < manifest.optional_packs.size(); ++i) {
        if (manifest.optional_packs[i].pack_id.empty()) {
            if (out_error) *out_error = "optional_dep_missing_id";
            return false;
        }
    }
    for (i = 0u; i < manifest.conflicts.size(); ++i) {
        if (manifest.conflicts[i].pack_id.empty()) {
            if (out_error) *out_error = "conflict_missing_id";
            return false;
        }
    }

    for (i = 0u; i < manifest.install_tasks.size(); ++i) {
        if (manifest.install_tasks[i].kind == 0u) {
            if (out_error) *out_error = "install_task_invalid_kind";
            return false;
        }
    }
    for (i = 0u; i < manifest.verify_tasks.size(); ++i) {
        if (manifest.verify_tasks[i].kind == 0u) {
            if (out_error) *out_error = "verify_task_invalid_kind";
            return false;
        }
    }
    for (i = 0u; i < manifest.prelaunch_tasks.size(); ++i) {
        if (manifest.prelaunch_tasks[i].kind == 0u) {
            if (out_error) *out_error = "prelaunch_task_invalid_kind";
            return false;
        }
    }

    return true;
}

} /* namespace launcher_core */
} /* namespace dom */
