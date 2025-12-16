/*
FILE: source/dominium/launcher/core/src/launcher_core.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation)
RESPONSIBILITY: Implements launcher core orchestration (state model wiring + audit emission) with all side effects via services facade.
ALLOWED DEPENDENCIES: C++98 standard library and `include/domino/**` base APIs; no OS/UI/toolkit headers.
FORBIDDEN DEPENDENCIES: Platform APIs, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions across C ABI.
DETERMINISM: Core decisions are deterministic given explicit inputs; time and IO are injected via the services facade.
*/

#include "launcher_core_api.h"

#include <cstdio>
#include <cstring>
#include <ctime>
#include <new>
#include <string>
#include <vector>

#include "launcher_audit.h"
#include "launcher_instance.h"
#include "launcher_profile.h"
#include "launcher_task.h"
#include "launcher_tlv.h"

namespace {

struct CoreState {
    dom::launcher_core::LauncherProfile selected_profile;
    dom::launcher_core::LauncherInstanceManifest selected_instance;
    std::vector<dom::launcher_core::LauncherProfile> profiles;
    std::vector<dom::launcher_core::LauncherInstanceManifest> instances;
    std::vector<dom::launcher_core::LauncherTask> tasks;
    dom::launcher_core::LauncherAuditLog audit;

    CoreState() : selected_profile(), selected_instance(), profiles(), instances(), tasks(), audit() {}
};

static CoreState reduce_add_reason(const CoreState& cur, const std::string& reason) {
    CoreState next = cur;
    next.audit.reasons.push_back(reason);
    return next;
}

static bool upsert_profile(std::vector<dom::launcher_core::LauncherProfile>& dst,
                           const dom::launcher_core::LauncherProfile& p) {
    size_t i;
    for (i = 0u; i < dst.size(); ++i) {
        if (dst[i].profile_id == p.profile_id) {
            dst[i] = p;
            return true;
        }
    }
    dst.push_back(p);
    return true;
}

static bool upsert_instance(std::vector<dom::launcher_core::LauncherInstanceManifest>& dst,
                            const dom::launcher_core::LauncherInstanceManifest& m) {
    size_t i;
    for (i = 0u; i < dst.size(); ++i) {
        if (dst[i].instance_id == m.instance_id) {
            dst[i] = m;
            return true;
        }
    }
    dst.push_back(m);
    return true;
}

static CoreState reduce_select_profile(const CoreState& cur,
                                      const dom::launcher_core::LauncherProfile& profile,
                                      const std::string& why) {
    CoreState next = cur;
    next.selected_profile = profile;
    upsert_profile(next.profiles, profile);
    next.audit.selected_profile_id = profile.profile_id;
    next.audit.reasons.push_back(std::string("selected_profile:") + profile.profile_id);
    next.audit.reasons.push_back(std::string("why:") + why);
    return next;
}

static CoreState reduce_select_instance(const CoreState& cur,
                                       const dom::launcher_core::LauncherInstanceManifest& inst,
                                       const std::string& why) {
    CoreState next = cur;
    next.selected_instance = inst;
    upsert_instance(next.instances, inst);
    next.audit.reasons.push_back(std::string("selected_instance:") + inst.instance_id);
    next.audit.reasons.push_back(std::string("why:") + why);
    return next;
}

static CoreState reduce_finalize_audit(const CoreState& cur, i32 exit_result) {
    CoreState next = cur;
    next.audit.exit_result = exit_result;
    next.audit.manifest_hash64 = dom::launcher_core::launcher_instance_manifest_hash64(cur.selected_instance);
    next.audit.reasons.push_back("audit_emitted");
    return next;
}

static CoreState reduce_set_version_string(const CoreState& cur, const std::string& v) {
    CoreState next = cur;
    next.audit.version_string = v;
    return next;
}

static CoreState reduce_set_build_id(const CoreState& cur, const std::string& v) {
    CoreState next = cur;
    next.audit.build_id = v;
    return next;
}

static CoreState reduce_set_git_hash(const CoreState& cur, const std::string& v) {
    CoreState next = cur;
    next.audit.git_hash = v;
    return next;
}

static CoreState reduce_add_selected_backend(const CoreState& cur,
                                            const dom::launcher_core::LauncherAuditBackend& b) {
    CoreState next = cur;
    next.audit.selected_backends.push_back(b);
    return next;
}

static void u64_to_hex16(u64 v, char out_hex[17]) {
    static const char* hex = "0123456789abcdef";
    int i;
    for (i = 0; i < 16; ++i) {
        unsigned shift = (unsigned)((15 - i) * 4);
        unsigned nib = (unsigned)((v >> shift) & (u64)0xFu);
        out_hex[i] = hex[nib & 0xFu];
    }
    out_hex[16] = '\0';
}

} /* namespace */

struct launcher_core {
    const launcher_services_api_v1* services;
    const launcher_fs_api_v1* fs;
    const launcher_time_api_v1* time;
    const launcher_hash_api_v1* hash;

    std::string audit_output_path;

    CoreState state;
    bool audit_emitted;
};

/*------------------------------------------------------------
 * Null services backend (C ABI)
 *------------------------------------------------------------*/

namespace {

static u64 null_time_last_us = 0ull;

static u64 null_time_now_us(void) {
    /* Monotonic best-effort without OS headers: use wall time as seed + clamp monotonic. */
    u64 v = 0ull;
    time_t t = time((time_t*)0);
    if (t > 0) {
        v = (u64)t;
    }
    v *= 1000000ull;

    /* Mix in a counter to avoid collisions within a second. */
    v += (null_time_last_us & 0xFFFFFull);
    if (v <= null_time_last_us) {
        v = null_time_last_us + 1ull;
    }
    null_time_last_us = v;
    return v;
}

static bool null_fs_get_path(launcher_fs_path_kind kind, char* buf, size_t buf_size) {
    const char* val = 0;
    size_t n;
    if (!buf || buf_size == 0u) {
        return false;
    }
    switch (kind) {
    case LAUNCHER_FS_PATH_STATE: val = "."; break;
    case LAUNCHER_FS_PATH_AUDIT: val = "."; break;
    default: val = "."; break;
    }
    n = std::strlen(val);
    if (n + 1u > buf_size) {
        buf[0] = '\0';
        return false;
    }
    std::memcpy(buf, val, n);
    buf[n] = '\0';
    return true;
}

static void* null_fs_file_open(const char* path, const char* mode) {
    if (!path || !mode) {
        return 0;
    }
    return (void*)std::fopen(path, mode);
}

static size_t null_fs_file_read(void* fh, void* buf, size_t size) {
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    return std::fread(buf, 1u, size, (FILE*)fh);
}

static size_t null_fs_file_write(void* fh, const void* buf, size_t size) {
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    return std::fwrite(buf, 1u, size, (FILE*)fh);
}

static int null_fs_file_seek(void* fh, long offset, int origin) {
    if (!fh) {
        return -1;
    }
    return std::fseek((FILE*)fh, offset, origin);
}

static long null_fs_file_tell(void* fh) {
    if (!fh) {
        return -1L;
    }
    return std::ftell((FILE*)fh);
}

static int null_fs_file_close(void* fh) {
    if (!fh) {
        return -1;
    }
    return std::fclose((FILE*)fh);
}

static u64 null_hash_fnv1a64(const void* data, u32 len) {
    return dom::launcher_core::tlv_fnv1a64((const unsigned char*)data, (size_t)len);
}

static launcher_fs_api_v1 null_fs_api = {
    DOM_ABI_HEADER_INIT(1u, launcher_fs_api_v1),
    &null_fs_get_path,
    &null_fs_file_open,
    &null_fs_file_read,
    &null_fs_file_write,
    &null_fs_file_seek,
    &null_fs_file_tell,
    &null_fs_file_close
};

static launcher_time_api_v1 null_time_api = {
    DOM_ABI_HEADER_INIT(1u, launcher_time_api_v1),
    &null_time_now_us
};

static launcher_hash_api_v1 null_hash_api = {
    DOM_ABI_HEADER_INIT(1u, launcher_hash_api_v1),
    &null_hash_fnv1a64
};

static launcher_services_caps null_services_get_caps(void) {
    return (launcher_services_caps)(LAUNCHER_SERVICES_CAP_FILESYSTEM |
                                    LAUNCHER_SERVICES_CAP_TIME |
                                    LAUNCHER_SERVICES_CAP_HASHING);
}

static dom_abi_result null_services_query_interface(dom_iid iid, void** out_iface) {
    if (!out_iface) {
        return (dom_abi_result)-1;
    }
    *out_iface = 0;
    switch (iid) {
    case LAUNCHER_IID_FS_V1:
        *out_iface = (void*)&null_fs_api;
        return (dom_abi_result)0;
    case LAUNCHER_IID_TIME_V1:
        *out_iface = (void*)&null_time_api;
        return (dom_abi_result)0;
    case LAUNCHER_IID_HASH_V1:
        *out_iface = (void*)&null_hash_api;
        return (dom_abi_result)0;
    default:
        return (dom_abi_result)-1;
    }
}

static launcher_services_api_v1 null_services_api = {
    DOM_ABI_HEADER_INIT(1u, launcher_services_api_v1),
    &null_services_get_caps,
    &null_services_query_interface
};

} /* namespace */

extern "C" const launcher_services_api_v1* launcher_services_null_v1(void) {
    return &null_services_api;
}

/*------------------------------------------------------------
 * Core C ABI wrapper
 *------------------------------------------------------------*/

static const launcher_fs_api_v1* core_get_fs(const launcher_services_api_v1* services) {
    void* iface = 0;
    if (!services || !services->query_interface) {
        return 0;
    }
    if (services->query_interface(LAUNCHER_IID_FS_V1, &iface) != 0) {
        return 0;
    }
    return (const launcher_fs_api_v1*)iface;
}

static const launcher_time_api_v1* core_get_time(const launcher_services_api_v1* services) {
    void* iface = 0;
    if (!services || !services->query_interface) {
        return 0;
    }
    if (services->query_interface(LAUNCHER_IID_TIME_V1, &iface) != 0) {
        return 0;
    }
    return (const launcher_time_api_v1*)iface;
}

static const launcher_hash_api_v1* core_get_hash(const launcher_services_api_v1* services) {
    void* iface = 0;
    if (!services || !services->query_interface) {
        return 0;
    }
    if (services->query_interface(LAUNCHER_IID_HASH_V1, &iface) != 0) {
        return 0;
    }
    return (const launcher_hash_api_v1*)iface;
}

static bool core_write_all(const launcher_fs_api_v1* fs,
                           const std::string& path,
                           const std::vector<unsigned char>& bytes) {
    void* fh;
    size_t wrote;
    if (!fs || !fs->file_open || !fs->file_write || !fs->file_close) {
        return false;
    }
    fh = fs->file_open(path.c_str(), "wb");
    if (!fh) {
        return false;
    }
    wrote = 0u;
    if (!bytes.empty()) {
        wrote = fs->file_write(fh, &bytes[0], bytes.size());
    }
    (void)fs->file_close(fh);
    return wrote == bytes.size();
}

extern "C" launcher_core* launcher_core_create(const launcher_core_desc_v1* desc) {
    try {
        launcher_core* core;
        u64 now_us;
        u32 i;

        if (!desc || desc->struct_size < (u32)sizeof(launcher_core_desc_v1) || desc->struct_version != LAUNCHER_CORE_DESC_VERSION) {
            return 0;
        }
        if (!desc->services) {
            return 0;
        }

        core = new (std::nothrow) launcher_core();
        if (!core) {
            return 0;
        }

        core->services = desc->services;
        core->fs = core_get_fs(desc->services);
        core->time = core_get_time(desc->services);
        core->hash = core_get_hash(desc->services);
        core->audit_output_path.clear();
        core->audit_emitted = false;
        if (desc->audit_output_path) {
            core->audit_output_path = desc->audit_output_path;
        }

        /* Required capabilities for foundation: filesystem + monotonic time. */
        if (!core->fs || !core->fs->file_open || !core->fs->file_write || !core->fs->file_close) {
            delete core;
            return 0;
        }
        if (!core->time || !core->time->now_us) {
            delete core;
            return 0;
        }

        now_us = 0ull;
        now_us = core->time->now_us();

        core->state.audit.run_id = now_us;
        core->state.audit.timestamp_us = now_us;
        core->state.audit.selected_profile_id = desc->selected_profile_id ? desc->selected_profile_id : "null";
        core->state.audit.version_string = "launcher-core-foundation";
        /* Exit result is explicitly set on emission; default is 0 and will be called out if auto-emitted. */
        core->state.audit.exit_result = 0;

        if (desc->argv && desc->argv_count > 0u) {
            for (i = 0u; i < desc->argv_count; ++i) {
                const char* a = desc->argv[i];
                core->state.audit.inputs.push_back(a ? std::string(a) : std::string());
            }
        }

        /* Seed explicit null/default entities for determinism and audit completeness. */
        {
            dom::launcher_core::LauncherProfile initial_profile = dom::launcher_core::launcher_profile_make_null();
            if (desc->selected_profile_id && desc->selected_profile_id[0] != '\0') {
                initial_profile.profile_id = desc->selected_profile_id;
            }
            core->state = reduce_select_profile(core->state, initial_profile, "create_default_profile");
        }
        core->state = reduce_select_instance(core->state,
                                             dom::launcher_core::launcher_instance_manifest_make_null(),
                                             "create_default_null_instance");

        core->state = reduce_add_reason(core->state, "launcher_core_created");
        core->state = reduce_add_reason(core->state, "no_ui_assumptions");
        core->state = reduce_add_reason(core->state, "audit_required_each_run");
        core->state = reduce_add_reason(core->state, "selected_backends:none (foundation)");
        return core;
    } catch (...) {
        return 0;
    }
}

extern "C" void launcher_core_destroy(launcher_core* core) {
    try {
        if (!core) {
            return;
        }
        /* Mandatory audit: if the host never emitted, auto-emit and record that exit_result was defaulted. */
        if (!core->audit_emitted) {
            core->state = reduce_add_reason(core->state, "audit_auto_emitted_on_destroy");
            core->state = reduce_add_reason(core->state, "exit_result_defaulted_to_0");
            (void)launcher_core_emit_audit(core, (int)core->state.audit.exit_result);
            core->audit_emitted = true;
        }
        delete core;
    } catch (...) {
        /* swallow */
    }
}

extern "C" int launcher_core_load_null_profile(launcher_core* core) {
    try {
        if (!core) {
            return -1;
        }
        core->state = reduce_select_profile(core->state,
                                            dom::launcher_core::launcher_profile_make_null(),
                                            "explicit_null_profile");
        return 0;
    } catch (...) {
        return -1;
    }
}

extern "C" int launcher_core_add_reason(launcher_core* core, const char* reason) {
    try {
        if (!core || !reason) {
            return -1;
        }
        core->state = reduce_add_reason(core->state, std::string(reason));
        return 0;
    } catch (...) {
        return -1;
    }
}

extern "C" int launcher_core_select_profile_id(launcher_core* core, const char* profile_id, const char* why) {
    try {
        dom::launcher_core::LauncherProfile p;
        if (!core || !profile_id || profile_id[0] == '\0') {
            return -1;
        }
        p = dom::launcher_core::launcher_profile_make_null();
        p.profile_id = profile_id;
        core->state = reduce_select_profile(core->state, p, why ? std::string(why) : std::string("select_profile_id"));
        return 0;
    } catch (...) {
        return -1;
    }
}

extern "C" int launcher_core_set_version_string(launcher_core* core, const char* version_string) {
    try {
        if (!core || !version_string) {
            return -1;
        }
        core->state = reduce_set_version_string(core->state, std::string(version_string));
        return 0;
    } catch (...) {
        return -1;
    }
}

extern "C" int launcher_core_set_build_id(launcher_core* core, const char* build_id) {
    try {
        if (!core || !build_id) {
            return -1;
        }
        core->state = reduce_set_build_id(core->state, std::string(build_id));
        return 0;
    } catch (...) {
        return -1;
    }
}

extern "C" int launcher_core_set_git_hash(launcher_core* core, const char* git_hash) {
    try {
        if (!core || !git_hash) {
            return -1;
        }
        core->state = reduce_set_git_hash(core->state, std::string(git_hash));
        return 0;
    } catch (...) {
        return -1;
    }
}

extern "C" int launcher_core_add_selected_backend(launcher_core* core,
                                                  u32 subsystem_id,
                                                  const char* subsystem_name,
                                                  const char* backend_name,
                                                  u32 determinism_grade,
                                                  u32 perf_class,
                                                  u32 priority,
                                                  u32 chosen_by_override) {
    try {
        dom::launcher_core::LauncherAuditBackend b;
        if (!core) {
            return -1;
        }
        b.subsystem_id = subsystem_id;
        b.subsystem_name = subsystem_name ? std::string(subsystem_name) : std::string();
        b.backend_name = backend_name ? std::string(backend_name) : std::string();
        b.determinism_grade = determinism_grade;
        b.perf_class = perf_class;
        b.priority = priority;
        b.chosen_by_override = chosen_by_override;
        core->state = reduce_add_selected_backend(core->state, b);
        return 0;
    } catch (...) {
        return -1;
    }
}

extern "C" int launcher_core_create_empty_instance(launcher_core* core, const char* instance_id) {
    try {
        if (!core || !instance_id || instance_id[0] == '\0') {
            return -1;
        }
        core->state = reduce_select_instance(core->state,
                                             dom::launcher_core::launcher_instance_manifest_make_empty(std::string(instance_id)),
                                             "explicit_create_empty_instance");
        return 0;
    } catch (...) {
        return -1;
    }
}

extern "C" int launcher_core_emit_audit(launcher_core* core, int exit_result) {
    try {
        std::vector<unsigned char> bytes;
        std::string out_path;

        if (!core || !core->fs) {
            return -1;
        }

        core->state = reduce_finalize_audit(core->state, (i32)exit_result);

        if (!dom::launcher_core::launcher_audit_to_tlv_bytes(core->state.audit, bytes)) {
            return -1;
        }

        out_path = core->audit_output_path;
        if (out_path.empty()) {
            char hex[17];
            u64_to_hex16(core->state.audit.run_id, hex);
            out_path = std::string("launcher_audit_") + hex + ".tlv";
        }

        if (!core_write_all(core->fs, out_path, bytes)) {
            return -1;
        }
        core->audit_emitted = true;
        return 0;
    } catch (...) {
        return -1;
    }
}
