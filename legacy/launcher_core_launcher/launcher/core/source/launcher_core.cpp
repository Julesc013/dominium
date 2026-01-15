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

static CoreState reduce_add_reason_id(const CoreState& cur, u32 reason_msg_id) {
    CoreState next = cur;
    if (reason_msg_id != 0u) {
        next.audit.reason_msg_ids.push_back(reason_msg_id);
        next.audit.reasons.push_back(std::string(err_msg_id_token(reason_msg_id)));
    }
    return next;
}

static CoreState reduce_set_error(const CoreState& cur, const err_t& err) {
    CoreState next = cur;
    next.audit.err = err;
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

extern "C" launcher_core* launcher_core_create_ex(const launcher_core_desc_v1* desc, err_t* out_err) {
    launcher_core* core = 0;
    err_t err = err_ok();
    try {
        u64 now_us;
        u32 i;

        if (!desc || desc->struct_size < (u32)sizeof(launcher_core_desc_v1) || desc->struct_version != LAUNCHER_CORE_DESC_VERSION) {
            err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
            goto fail;
        }
        if (!desc->services) {
            err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
            goto fail;
        }

        core = new (std::nothrow) launcher_core();
        if (!core) {
            err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_OUT_OF_MEMORY, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_OUT_OF_MEMORY);
            goto fail;
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
            err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_BAD_STATE);
            goto fail;
        }
        if (!core->time || !core->time->now_us) {
            err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_BAD_STATE);
            goto fail;
        }

        now_us = 0ull;
        now_us = core->time->now_us();

        core->state.audit.run_id = now_us;
        core->state.audit.timestamp_us = now_us;
        core->state.audit.selected_profile_id = desc->selected_profile_id ? desc->selected_profile_id : "null";
        core->state.audit.version_string = "launcher-core-foundation";
        core->state.audit.exit_result = 0;
        core->state.audit.err = err_ok();

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
        if (out_err) {
            *out_err = err_ok();
        }
        return core;
    } catch (...) {
        err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INTERNAL, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_INTERNAL);
    }
fail:
    if (core) {
        delete core;
    }
    if (out_err) {
        *out_err = err;
    }
    return 0;
}

extern "C" launcher_core* launcher_core_create(const launcher_core_desc_v1* desc) {
    return launcher_core_create_ex(desc, (err_t*)0);
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

extern "C" int launcher_core_load_null_profile_ex(launcher_core* core, err_t* out_err) {
    err_t err = err_ok();
    try {
        if (!core) {
            err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
            if (out_err) *out_err = err;
            return -1;
        }
        core->state = reduce_select_profile(core->state,
                                            dom::launcher_core::launcher_profile_make_null(),
                                            "explicit_null_profile");
        if (out_err) *out_err = err_ok();
        return 0;
    } catch (...) {
        err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INTERNAL, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_INTERNAL);
        if (out_err) *out_err = err;
        return -1;
    }
}

extern "C" int launcher_core_load_null_profile(launcher_core* core) {
    return launcher_core_load_null_profile_ex(core, (err_t*)0);
}

extern "C" int launcher_core_add_reason_id(launcher_core* core, u32 reason_msg_id) {
    try {
        if (!core || reason_msg_id == 0u) {
            return -1;
        }
        core->state = reduce_add_reason_id(core->state, reason_msg_id);
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

extern "C" int launcher_core_select_profile_id_ex(launcher_core* core, const char* profile_id, u32 reason_msg_id, err_t* out_err) {
    err_t err = err_ok();
    try {
        dom::launcher_core::LauncherProfile p;
        if (!core || !profile_id || profile_id[0] == '\0') {
            err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
            if (out_err) *out_err = err;
            return -1;
        }
        p = dom::launcher_core::launcher_profile_make_null();
        p.profile_id = profile_id;
        core->state = reduce_select_profile(core->state, p,
                                            reason_msg_id != 0u ? err_msg_id_token(reason_msg_id) : "select_profile_id");
        if (reason_msg_id != 0u) {
            core->state = reduce_add_reason_id(core->state, reason_msg_id);
        }
        if (out_err) *out_err = err_ok();
        return 0;
    } catch (...) {
        err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INTERNAL, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_INTERNAL);
        if (out_err) *out_err = err;
        return -1;
    }
}

extern "C" int launcher_core_select_profile_id(launcher_core* core, const char* profile_id, const char* why) {
    (void)why;
    return launcher_core_select_profile_id_ex(core, profile_id, 0u, (err_t*)0);
}

extern "C" int launcher_core_set_version_string_ex(launcher_core* core, const char* version_string, err_t* out_err) {
    err_t err = err_ok();
    try {
        if (!core || !version_string) {
            err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
            if (out_err) *out_err = err;
            return -1;
        }
        core->state = reduce_set_version_string(core->state, std::string(version_string));
        if (out_err) *out_err = err_ok();
        return 0;
    } catch (...) {
        err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INTERNAL, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_INTERNAL);
        if (out_err) *out_err = err;
        return -1;
    }
}

extern "C" int launcher_core_set_version_string(launcher_core* core, const char* version_string) {
    return launcher_core_set_version_string_ex(core, version_string, (err_t*)0);
}

extern "C" int launcher_core_set_build_id_ex(launcher_core* core, const char* build_id, err_t* out_err) {
    err_t err = err_ok();
    try {
        if (!core || !build_id) {
            err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
            if (out_err) *out_err = err;
            return -1;
        }
        core->state = reduce_set_build_id(core->state, std::string(build_id));
        if (out_err) *out_err = err_ok();
        return 0;
    } catch (...) {
        err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INTERNAL, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_INTERNAL);
        if (out_err) *out_err = err;
        return -1;
    }
}

extern "C" int launcher_core_set_build_id(launcher_core* core, const char* build_id) {
    return launcher_core_set_build_id_ex(core, build_id, (err_t*)0);
}

extern "C" int launcher_core_set_git_hash_ex(launcher_core* core, const char* git_hash, err_t* out_err) {
    err_t err = err_ok();
    try {
        if (!core || !git_hash) {
            err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
            if (out_err) *out_err = err;
            return -1;
        }
        core->state = reduce_set_git_hash(core->state, std::string(git_hash));
        if (out_err) *out_err = err_ok();
        return 0;
    } catch (...) {
        err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INTERNAL, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_INTERNAL);
        if (out_err) *out_err = err;
        return -1;
    }
}

extern "C" int launcher_core_set_git_hash(launcher_core* core, const char* git_hash) {
    return launcher_core_set_git_hash_ex(core, git_hash, (err_t*)0);
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

extern "C" int launcher_core_create_empty_instance_ex(launcher_core* core, const char* instance_id, err_t* out_err) {
    err_t err = err_ok();
    try {
        if (!core || !instance_id || instance_id[0] == '\0') {
            err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
            if (out_err) *out_err = err;
            return -1;
        }
        core->state = reduce_select_instance(core->state,
                                             dom::launcher_core::launcher_instance_manifest_make_empty(std::string(instance_id)),
                                             "explicit_create_empty_instance");
        if (out_err) *out_err = err_ok();
        return 0;
    } catch (...) {
        err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INTERNAL, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_INTERNAL);
        if (out_err) *out_err = err;
        return -1;
    }
}

extern "C" int launcher_core_create_empty_instance(launcher_core* core, const char* instance_id) {
    return launcher_core_create_empty_instance_ex(core, instance_id, (err_t*)0);
}

extern "C" int launcher_core_set_error(launcher_core* core, const err_t* err) {
    try {
        if (!core) {
            return -1;
        }
        core->state = reduce_set_error(core->state, err ? *err : err_ok());
        return 0;
    } catch (...) {
        return -1;
    }
}

extern "C" int launcher_core_emit_audit_ex(launcher_core* core, int exit_result, err_t* out_err) {
    err_t err = err_ok();
    try {
        std::vector<unsigned char> bytes;
        std::string out_path;

        if (!core || !core->fs) {
            err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
            goto fail;
        }

        core->state = reduce_finalize_audit(core->state, (i32)exit_result);

        if (!dom::launcher_core::launcher_audit_to_tlv_bytes(core->state.audit, bytes)) {
            err = err_make((u16)ERRD_TLV, (u16)ERRC_TLV_INTEGRITY, (u32)ERRF_INTEGRITY, (u32)ERRMSG_TLV_INTEGRITY);
            goto fail;
        }

        out_path = core->audit_output_path;
        if (out_path.empty()) {
            char hex[17];
            u64_to_hex16(core->state.audit.run_id, hex);
            out_path = std::string("launcher_audit_") + hex + ".tlv";
        }

        if (!core_write_all(core->fs, out_path, bytes)) {
            err = err_make((u16)ERRD_FS, (u16)ERRC_FS_WRITE_FAILED, 0u, (u32)ERRMSG_FS_WRITE_FAILED);
            goto fail;
        }
        core->audit_emitted = true;
        if (out_err) *out_err = err_ok();
        return 0;
    } catch (...) {
        err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INTERNAL, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_INTERNAL);
    }
fail:
    if (core) {
        core->state = reduce_set_error(core->state, err);
    }
    if (out_err) {
        *out_err = err;
    }
    return -1;
}

extern "C" int launcher_core_emit_audit(launcher_core* core, int exit_result) {
    return launcher_core_emit_audit_ex(core, exit_result, (err_t*)0);
}
