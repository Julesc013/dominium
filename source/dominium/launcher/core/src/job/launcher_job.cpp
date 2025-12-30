/*
FILE: source/dominium/launcher/core/src/job/launcher_job.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / job
RESPONSIBILITY: Resumable job journal + execution wrapper for long launcher operations.
*/

#include "launcher_job.h"

#include <cstdio>
#include <cstring>

#include "launcher_audit.h"
#include "launcher_instance.h"
#include "launcher_instance_artifact_ops.h"
#include "launcher_instance_ops.h"
#include "launcher_instance_tx.h"
#include "launcher_launch_attempt.h"
#include "launcher_log.h"
#include "launcher_pack_resolver.h"
#include "launcher_tlv.h"

namespace dom {
namespace launcher_core {

namespace {

enum LauncherJobInputTlvTag {
    LAUNCHER_JOB_INPUT_TLV_TAG_JOB_TYPE = 2u,
    LAUNCHER_JOB_INPUT_TLV_TAG_INSTANCE_ID = 3u,
    LAUNCHER_JOB_INPUT_TLV_TAG_PATH = 4u,
    LAUNCHER_JOB_INPUT_TLV_TAG_AUX_PATH = 5u,
    LAUNCHER_JOB_INPUT_TLV_TAG_AUX_ID = 6u,
    LAUNCHER_JOB_INPUT_TLV_TAG_MODE = 7u,
    LAUNCHER_JOB_INPUT_TLV_TAG_FLAGS = 8u,
    LAUNCHER_JOB_INPUT_TLV_TAG_PACK_CHANGE = 20u,
    LAUNCHER_JOB_INPUT_TLV_TAG_OVERRIDES = 30u
};

enum LauncherJobInputPackChangeTag {
    LAUNCHER_JOB_INPUT_PACK_TAG_TYPE = 1u,
    LAUNCHER_JOB_INPUT_PACK_TAG_ID = 2u,
    LAUNCHER_JOB_INPUT_PACK_TAG_HAS_ENABLED = 3u,
    LAUNCHER_JOB_INPUT_PACK_TAG_ENABLED = 4u,
    LAUNCHER_JOB_INPUT_PACK_TAG_HAS_POLICY = 5u,
    LAUNCHER_JOB_INPUT_PACK_TAG_POLICY = 6u
};

enum LauncherJobInputOverrideTag {
    LAUNCHER_JOB_INPUT_OVERRIDE_SAFE_MODE = 1u,
    LAUNCHER_JOB_INPUT_OVERRIDE_SAFE_MODE_ALLOW_NET = 2u,
    LAUNCHER_JOB_INPUT_OVERRIDE_GFX_BACKEND = 3u,
    LAUNCHER_JOB_INPUT_OVERRIDE_RENDERER_API = 4u,
    LAUNCHER_JOB_INPUT_OVERRIDE_WINDOW_MODE = 5u,
    LAUNCHER_JOB_INPUT_OVERRIDE_WINDOW_WIDTH = 6u,
    LAUNCHER_JOB_INPUT_OVERRIDE_WINDOW_HEIGHT = 7u,
    LAUNCHER_JOB_INPUT_OVERRIDE_WINDOW_DPI = 8u,
    LAUNCHER_JOB_INPUT_OVERRIDE_WINDOW_MONITOR = 9u,
    LAUNCHER_JOB_INPUT_OVERRIDE_AUDIO_DEVICE_ID = 10u,
    LAUNCHER_JOB_INPUT_OVERRIDE_INPUT_BACKEND = 11u,
    LAUNCHER_JOB_INPUT_OVERRIDE_ALLOW_NETWORK = 12u,
    LAUNCHER_JOB_INPUT_OVERRIDE_DEBUG_FLAGS = 13u
};

struct LauncherJobPaths {
    std::string job_root;
    std::string def_path;
    std::string state_path;
    std::string input_path;
    std::string events_path;
    std::string audit_path;
    std::string checkpoint_path;
};

struct LauncherJobContext {
    const launcher_services_api_v1* services;
    LauncherJobInput input;
    core_job_def def;
    core_job_state state;
    LauncherJobPaths paths;
    std::string state_root;
    LauncherAuditLog audit;
    LauncherPrelaunchPlan* out_plan;
};

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

static const launcher_time_api_v1* get_time(const launcher_services_api_v1* services) {
    void* iface = 0;
    if (!services || !services->query_interface) {
        return 0;
    }
    if (services->query_interface(LAUNCHER_IID_TIME_V1, &iface) != 0) {
        return 0;
    }
    return (const launcher_time_api_v1*)iface;
}

static const launcher_process_api_v1* get_proc(const launcher_services_api_v1* services) {
    void* iface = 0;
    if (!services || !services->query_interface) {
        return 0;
    }
    if (services->query_interface(LAUNCHER_IID_PROC_V1, &iface) != 0) {
        return 0;
    }
    return (const launcher_process_api_v1*)iface;
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

static bool is_sep(char c) {
    return c == '/' || c == '\\';
}

static std::string path_join(const std::string& a, const std::string& b) {
    std::string aa = normalize_seps(a);
    std::string bb = normalize_seps(b);
    if (aa.empty()) {
        return bb;
    }
    if (bb.empty()) {
        return aa;
    }
    if (is_sep(aa[aa.size() - 1u])) {
        return aa + bb;
    }
    return aa + "/" + bb;
}

#if defined(_WIN32) || defined(_WIN64)
extern "C" int _mkdir(const char* path);
#else
extern "C" int mkdir(const char* path, unsigned int mode);
#endif

static bool mkdir_one_best_effort(const std::string& path) {
    if (path.empty()) {
        return false;
    }
    if (path == "." || path == "./") {
        return true;
    }
    if (path.size() == 2u && path[1] == ':') {
        return true;
    }
    if (path == "/") {
        return true;
    }
#if defined(_WIN32) || defined(_WIN64)
    return _mkdir(path.c_str()) == 0;
#else
    return mkdir(path.c_str(), 0777u) == 0;
#endif
}

static bool mkdir_p_best_effort(const std::string& path) {
    std::string p = normalize_seps(path);
    size_t i;

    if (p.empty()) {
        return false;
    }

    for (i = 0u; i < p.size(); ++i) {
        if (p[i] == '/') {
            std::string part = p.substr(0u, i);
            if (!part.empty()) {
                (void)mkdir_one_best_effort(part);
            }
        }
    }
    (void)mkdir_one_best_effort(p);
    return true;
}

static bool fs_write_all(const launcher_fs_api_v1* fs,
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

static bool fs_write_all_atomic(const launcher_fs_api_v1* fs,
                                const std::string& path,
                                const std::vector<unsigned char>& bytes) {
    std::string tmp = path + ".tmp";
    if (!fs_write_all(fs, tmp, bytes)) {
        return false;
    }
    if (std::rename(tmp.c_str(), path.c_str()) != 0) {
        (void)std::remove(tmp.c_str());
        return false;
    }
    return true;
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
    if (got != (size_t)sz) {
        out_bytes.clear();
        return false;
    }
    return true;
}

static bool fs_file_exists(const launcher_fs_api_v1* fs, const std::string& path) {
    void* fh;
    if (!fs || !fs->file_open || !fs->file_close) {
        return false;
    }
    fh = fs->file_open(path.c_str(), "rb");
    if (!fh) {
        return false;
    }
    (void)fs->file_close(fh);
    return true;
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

static std::string u64_hex16_string(u64 v) {
    char buf[17];
    u64_to_hex16(v, buf);
    return std::string(buf);
}

static void build_job_paths(const std::string& state_root,
                            const std::string& instance_id,
                            u64 job_id,
                            LauncherJobPaths& out_paths) {
    LauncherInstancePaths ipaths = launcher_instance_paths_make(state_root, instance_id);
    std::string jobs_root = path_join(ipaths.staging_root, "jobs");
    std::string job_dir = path_join(jobs_root, u64_hex16_string(job_id));

    out_paths.job_root = job_dir;
    out_paths.def_path = path_join(job_dir, "job_def.tlv");
    out_paths.state_path = path_join(job_dir, "job_state.tlv");
    out_paths.input_path = path_join(job_dir, "job_input.tlv");
    out_paths.events_path = path_join(job_dir, "job_events.tlv");
    out_paths.audit_path = path_join(job_dir, "job_audit.tlv");
    out_paths.checkpoint_path.clear();
}

struct MemSink {
    std::vector<unsigned char>* buf;
};

static dom_abi_result mem_sink_write(void* user, const void* data, u32 len) {
    MemSink* sink = (MemSink*)user;
    if (!sink || !sink->buf || !data || len == 0u) {
        return 0;
    }
    {
        size_t off = sink->buf->size();
        sink->buf->resize(off + (size_t)len);
        std::memcpy(&(*sink->buf)[off], data, (size_t)len);
    }
    return 0;
}

static bool write_job_def(const launcher_fs_api_v1* fs,
                          const LauncherJobPaths& paths,
                          const core_job_def& def) {
    std::vector<unsigned char> bytes;
    MemSink sink;
    core_job_write_sink csink;
    sink.buf = &bytes;
    csink.user = &sink;
    csink.write = mem_sink_write;
    if (core_job_def_write_tlv(&def, &csink) != 0) {
        return false;
    }
    return fs_write_all_atomic(fs, paths.def_path, bytes);
}

static bool write_job_state(const launcher_fs_api_v1* fs,
                            const LauncherJobPaths& paths,
                            const core_job_state& st) {
    std::vector<unsigned char> bytes;
    MemSink sink;
    core_job_write_sink csink;
    sink.buf = &bytes;
    csink.user = &sink;
    csink.write = mem_sink_write;
    if (core_job_state_write_tlv(&st, &csink) != 0) {
        return false;
    }
    return fs_write_all_atomic(fs, paths.state_path, bytes);
}

static bool read_job_state(const launcher_fs_api_v1* fs,
                           const LauncherJobPaths& paths,
                           core_job_state& out_state) {
    std::vector<unsigned char> bytes;
    if (!fs_read_all(fs, paths.state_path, bytes)) {
        return false;
    }
    if (bytes.empty()) {
        return false;
    }
    return core_job_state_read_tlv(&bytes[0], (u32)bytes.size(), out_state) == 0;
}

static bool read_job_def(const launcher_fs_api_v1* fs,
                         const LauncherJobPaths& paths,
                         core_job_def& out_def) {
    std::vector<unsigned char> bytes;
    if (!fs_read_all(fs, paths.def_path, bytes)) {
        return false;
    }
    if (bytes.empty()) {
        return false;
    }
    return core_job_def_read_tlv(&bytes[0], (u32)bytes.size(), out_def) == 0;
}

static void add_job_reason(LauncherAuditLog& audit,
                           const std::string& key,
                           const std::string& value) {
    audit.reasons.push_back(key + "=" + value);
}

static void append_job_event_file(const launcher_fs_api_v1* fs,
                                  const LauncherJobPaths& paths,
                                  const core_log_event& ev);

static void emit_job_event(LauncherJobContext& ctx,
                           u32 event_code,
                           u32 step_id,
                           const err_t* err,
                           u32 outcome) {
    core_log_event ev;
    core_log_scope scope;
    const bool safe_id = (!ctx.input.instance_id.empty() && launcher_is_safe_id_component(ctx.input.instance_id));

    core_log_event_clear(&ev);
    ev.domain = CORE_LOG_DOMAIN_LAUNCHER;
    ev.code = (u16)event_code;
    if (event_code == CORE_LOG_EVT_OP_FAIL) {
        ev.severity = CORE_LOG_SEV_ERROR;
    } else if (event_code == CORE_LOG_EVT_OP_REFUSED) {
        ev.severity = CORE_LOG_SEV_WARN;
    } else {
        ev.severity = CORE_LOG_SEV_INFO;
    }
    ev.msg_id = err ? err->msg_id : 0u;
    ev.t_mono = 0u;
    (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_OPERATION_ID, CORE_LOG_OP_LAUNCHER_JOB);
    (void)core_log_event_add_u64(&ev, CORE_LOG_KEY_JOB_ID, ctx.state.job_id);
    (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_JOB_TYPE, ctx.state.job_type);
    if (step_id != 0u) {
        (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_JOB_STEP_ID, step_id);
    }
    if (outcome != 0u) {
        (void)core_log_event_add_u32(&ev, CORE_LOG_KEY_JOB_OUTCOME, outcome);
    }
    if (err && !err_is_ok(err)) {
        launcher_log_add_err_fields(&ev, err);
    }

    std::memset(&scope, 0, sizeof(scope));
    scope.state_root = ctx.state_root.empty() ? (const char*)0 : ctx.state_root.c_str();
    if (safe_id) {
        scope.kind = CORE_LOG_SCOPE_INSTANCE;
        scope.instance_id = ctx.input.instance_id.c_str();
    } else {
        scope.kind = CORE_LOG_SCOPE_GLOBAL;
    }

    (void)launcher_services_emit_event(ctx.services, &scope, &ev);
    append_job_event_file(get_fs(ctx.services), ctx.paths, ev);
}

static void build_job_def(u32 job_type, core_job_def& out_def) {
    core_job_def def;
    u32 step_count = 0u;

    core_job_def_clear(&def);
    def.schema_version = CORE_JOB_DEF_TLV_VERSION;
    def.job_type = job_type;

    if (job_type == (u32)CORE_JOB_TYPE_LAUNCHER_VERIFY_INSTANCE ||
        job_type == (u32)CORE_JOB_TYPE_LAUNCHER_REPAIR_INSTANCE ||
        job_type == (u32)CORE_JOB_TYPE_LAUNCHER_EXPORT_INSTANCE ||
        job_type == (u32)CORE_JOB_TYPE_LAUNCHER_IMPORT_INSTANCE ||
        job_type == (u32)CORE_JOB_TYPE_LAUNCHER_DIAG_BUNDLE ||
        job_type == (u32)CORE_JOB_TYPE_LAUNCHER_LAUNCH_PREPARE) {
        step_count = 1u;
        def.steps[0].step_id = 1u;
        def.steps[0].flags = (u32)(CORE_JOB_STEP_IDEMPOTENT | CORE_JOB_STEP_RETRYABLE);
        def.steps[0].depends_on_count = 0u;
    } else if (job_type == (u32)CORE_JOB_TYPE_LAUNCHER_APPLY_PACKS) {
        step_count = 3u;
        def.steps[0].step_id = 1u;
        def.steps[0].flags = (u32)(CORE_JOB_STEP_IDEMPOTENT | CORE_JOB_STEP_RETRYABLE);
        def.steps[0].depends_on_count = 0u;

        def.steps[1].step_id = 2u;
        def.steps[1].flags = (u32)(CORE_JOB_STEP_IDEMPOTENT | CORE_JOB_STEP_RETRYABLE);
        def.steps[1].depends_on_count = 1u;
        def.steps[1].depends_on[0] = def.steps[0].step_id;

        def.steps[2].step_id = 3u;
        def.steps[2].flags = (u32)(CORE_JOB_STEP_IDEMPOTENT | CORE_JOB_STEP_RETRYABLE);
        def.steps[2].depends_on_count = 1u;
        def.steps[2].depends_on[0] = def.steps[1].step_id;
    }

    def.step_count = step_count;
    out_def = def;
}

static u64 generate_job_id(const launcher_services_api_v1* services) {
    const launcher_time_api_v1* time_api = get_time(services);
    if (time_api && time_api->now_us) {
        return time_api->now_us();
    }
    return 1ull;
}

static void init_job_audit(LauncherJobContext& ctx) {
    const launcher_time_api_v1* time_api = get_time(ctx.services);
    ctx.audit = LauncherAuditLog();
    ctx.audit.run_id = ctx.state.job_id;
    ctx.audit.timestamp_us = (time_api && time_api->now_us) ? time_api->now_us() : 0ull;
    add_job_reason(ctx.audit, "job_id", std::string("0x") + u64_hex16_string(ctx.state.job_id));
    add_job_reason(ctx.audit, "job_type", u64_hex16_string((u64)ctx.state.job_type));
    add_job_reason(ctx.audit, "instance_id", ctx.input.instance_id.empty() ? std::string("<none>") : ctx.input.instance_id);
}

static bool write_job_audit(const launcher_fs_api_v1* fs,
                            const LauncherJobContext& ctx) {
    std::vector<unsigned char> bytes;
    if (!launcher_audit_to_tlv_bytes(ctx.audit, bytes)) {
        return false;
    }
    return fs_write_all_atomic(fs, ctx.paths.audit_path, bytes);
}

static bool job_should_skip_apply_packs_step(const launcher_services_api_v1* services,
                                             const std::string& instance_id,
                                             const std::string& state_root,
                                             u32 step_id,
                                             core_job_state& st) {
    LauncherInstanceTx tx;
    if (!launcher_instance_tx_load(services, instance_id, state_root, tx)) {
        return false;
    }
    if (step_id == 1u && tx.phase >= (u32)LAUNCHER_INSTANCE_TX_PHASE_STAGE) {
        st.current_step = 0u;
        return true;
    }
    if (step_id == 2u && tx.phase >= (u32)LAUNCHER_INSTANCE_TX_PHASE_VERIFY) {
        st.current_step = 0u;
        return true;
    }
    if (step_id == 3u && tx.phase >= (u32)LAUNCHER_INSTANCE_TX_PHASE_DONE) {
        st.current_step = 0u;
        return true;
    }
    return false;
}

static bool load_tx_with_staged_manifest(const launcher_services_api_v1* services,
                                         const std::string& instance_id,
                                         const std::string& state_root,
                                         LauncherInstanceTx& out_tx,
                                         err_t* out_err) {
    const launcher_fs_api_v1* fs = get_fs(services);
    LauncherInstanceTx tx;
    LauncherInstancePaths paths;
    std::vector<unsigned char> bytes;
    LauncherInstanceManifest staged;

    if (!launcher_instance_tx_load(services, instance_id, state_root, tx)) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_TXN, (u16)ERRC_TXN_STAGE_FAILED, 0u, (u32)ERRMSG_TXN_STAGE_FAILED);
        }
        return false;
    }
    if (!fs) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_BAD_STATE);
        }
        return false;
    }

    paths = launcher_instance_paths_make(state_root, instance_id);
    if (!fs_read_all(fs, path_join(paths.staging_root, "manifest.tlv"), bytes) || bytes.empty()) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_FS, (u16)ERRC_FS_READ_FAILED, 0u, (u32)ERRMSG_FS_READ_FAILED);
        }
        return false;
    }
    if (!launcher_instance_manifest_from_tlv_bytes(&bytes[0], bytes.size(), staged)) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_TLV, (u16)ERRC_TLV_PARSE_FAILED, (u32)ERRF_INTEGRITY, (u32)ERRMSG_TLV_PARSE_FAILED);
        }
        return false;
    }

    tx.state_root = state_root;
    tx.after_manifest = staged;
    tx.after_manifest_hash64 = launcher_instance_manifest_hash64(staged);
    out_tx = tx;
    if (out_err) {
        *out_err = err_ok();
    }
    return true;
}

static bool execute_apply_packs_step(LauncherJobContext& ctx,
                                     u32 step_id,
                                     err_t* out_err) {
    const launcher_services_api_v1* services = ctx.services;
    LauncherAuditLog* audit = &ctx.audit;
    LauncherInstanceTx tx;

    if (step_id == 1u) {
        std::vector<LauncherResolvedPack> resolved;
        std::string resolve_err;
        std::vector<std::string> errs;
        bool ok;

        ok = launcher_instance_tx_prepare(services,
                                          ctx.input.instance_id,
                                          ctx.state_root,
                                          (u32)LAUNCHER_INSTANCE_TX_OP_UPDATE,
                                          tx,
                                          audit);
        if (!ok) {
            if (out_err) {
                *out_err = err_make((u16)ERRD_TXN, (u16)ERRC_TXN_STAGE_FAILED, 0u, (u32)ERRMSG_TXN_STAGE_FAILED);
            }
            return false;
        }

        tx.after_manifest = tx.before_manifest;

        for (size_t i = 0u; i < ctx.input.pack_changes.size(); ++i) {
            const LauncherJobPackChange& sc = ctx.input.pack_changes[i];
            bool found = false;
            size_t j;
            for (j = 0u; j < tx.after_manifest.content_entries.size(); ++j) {
                LauncherContentEntry& e = tx.after_manifest.content_entries[j];
                if (e.type != sc.content_type) {
                    continue;
                }
                if (e.id != sc.pack_id) {
                    continue;
                }
                found = true;
                if (sc.has_enabled) {
                    e.enabled = sc.enabled ? 1u : 0u;
                }
                if (sc.has_update_policy) {
                    e.update_policy = sc.update_policy;
                }
                break;
            }
            if (!found) {
                errs.push_back(std::string("pack_missing;id=") + sc.pack_id);
            }
        }

        if (!errs.empty()) {
            if (out_err) {
                *out_err = err_refuse((u16)ERRD_PACKS, (u16)ERRC_PACKS_PACK_NOT_FOUND, (u32)ERRMSG_PACKS_PACK_NOT_FOUND);
            }
            return false;
        }

        if (!launcher_pack_resolve_enabled(services, tx.after_manifest, ctx.state_root, resolved, &resolve_err)) {
            if (out_err) {
                *out_err = err_refuse((u16)ERRD_PACKS, (u16)ERRC_PACKS_DEPENDENCY_CONFLICT,
                                      (u32)ERRMSG_PACKS_DEPENDENCY_CONFLICT);
            }
            if (!resolve_err.empty()) {
                add_job_reason(*audit, "packs_resolve_error", resolve_err);
            }
            return false;
        }

        if (!launcher_instance_tx_stage_ex(services, tx, audit, out_err)) {
            return false;
        }
        return true;
    }

    if (step_id == 2u) {
        if (!load_tx_with_staged_manifest(services, ctx.input.instance_id, ctx.state_root, tx, out_err)) {
            return false;
        }
        if (!launcher_instance_tx_verify_ex(services, tx, audit, out_err)) {
            return false;
        }
        return true;
    }

    if (step_id == 3u) {
        if (!load_tx_with_staged_manifest(services, ctx.input.instance_id, ctx.state_root, tx, out_err)) {
            return false;
        }
        if (!launcher_instance_tx_commit_ex(services, tx, audit, out_err)) {
            return false;
        }
        return true;
    }

    if (out_err) {
        *out_err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INTERNAL, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_INTERNAL);
    }
    return false;
}

static bool execute_diag_bundle_step(LauncherJobContext& ctx, err_t* out_err) {
    const launcher_process_api_v1* proc = get_proc(ctx.services);
    const std::string python = "python";
    const std::string python3 = "python3";
    std::vector<std::string> args;
    std::vector<const char*> argv;
    launcher_process_desc_v1 desc;
    launcher_process* handle = 0;
    int exit_code = 0;
    size_t i;
    std::string format = ctx.input.aux_id.empty() ? std::string("zip") : ctx.input.aux_id;
    std::string mode = (ctx.input.mode == 1u) ? std::string("extended") : std::string("default");

    if (!proc || !proc->spawn || !proc->wait || !proc->destroy) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_PROC, (u16)ERRC_PROC_SPAWN_FAILED, (u32)ERRF_NOT_SUPPORTED,
                                (u32)ERRMSG_PROC_SPAWN_FAILED);
        }
        return false;
    }
    if (ctx.input.aux_path.empty() || ctx.input.path.empty() || ctx.input.instance_id.empty()) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
        }
        return false;
    }

    args.push_back(python);
    args.push_back(ctx.input.aux_path);
    args.push_back("--home");
    args.push_back(ctx.state_root);
    args.push_back("--instance");
    args.push_back(ctx.input.instance_id);
    args.push_back("--output");
    args.push_back(ctx.input.path);
    args.push_back("--format");
    args.push_back(format);
    args.push_back("--mode");
    args.push_back(mode);

    argv.clear();
    for (i = 0u; i < args.size(); ++i) {
        argv.push_back(args[i].c_str());
    }
    argv.push_back(0);

    std::memset(&desc, 0, sizeof(desc));
    desc.struct_size = (u32)sizeof(desc);
    desc.struct_version = 1u;
    desc.path = args[0].c_str();
    desc.argv = &argv[0];
    desc.argv_count = (u32)(argv.size() - 1u);
    desc.workdir = 0;

    handle = proc->spawn(&desc);
    if (!handle) {
        args[0] = python3;
        argv[0] = args[0].c_str();
        desc.path = args[0].c_str();
        handle = proc->spawn(&desc);
    }
    if (!handle) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_PROC, (u16)ERRC_PROC_SPAWN_FAILED, (u32)ERRF_TRANSIENT, (u32)ERRMSG_PROC_SPAWN_FAILED);
        }
        return false;
    }
    exit_code = proc->wait(handle);
    (void)proc->destroy(handle);
    if (exit_code != 0) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_PROC, (u16)ERRC_PROC_WAIT_FAILED, (u32)ERRF_TRANSIENT, (u32)ERRMSG_PROC_WAIT_FAILED);
        }
        return false;
    }
    if (out_err) {
        *out_err = err_ok();
    }
    return true;
}

static bool write_job_input(const launcher_fs_api_v1* fs,
                            const LauncherJobPaths& paths,
                            const LauncherJobInput& input) {
    std::vector<unsigned char> bytes;
    if (!launcher_job_input_to_tlv_bytes(input, bytes)) {
        return false;
    }
    return fs_write_all_atomic(fs, paths.input_path, bytes);
}

static bool read_job_input(const launcher_fs_api_v1* fs,
                           const LauncherJobPaths& paths,
                           LauncherJobInput& out_input) {
    std::vector<unsigned char> bytes;
    if (!fs_read_all(fs, paths.input_path, bytes)) {
        return false;
    }
    if (bytes.empty()) {
        return false;
    }
    return launcher_job_input_from_tlv_bytes(&bytes[0], bytes.size(), out_input);
}

struct FsSink {
    const launcher_fs_api_v1* fs;
    void* fh;
};

static dom_abi_result fs_sink_write(void* user, const void* data, u32 len) {
    FsSink* sink = (FsSink*)user;
    if (!sink || !sink->fs || !sink->fs->file_write || !sink->fh || !data || len == 0u) {
        return 0;
    }
    return (sink->fs->file_write(sink->fh, data, len) == (size_t)len) ? 0 : (dom_abi_result)-1;
}

static void append_job_event_file(const launcher_fs_api_v1* fs,
                                  const LauncherJobPaths& paths,
                                  const core_log_event& ev) {
    void* fh;
    if (!fs || !fs->file_open || !fs->file_close) {
        return;
    }
    fh = fs->file_open(paths.events_path.c_str(), "ab");
    if (!fh) {
        return;
    }
    {
        FsSink sink_ctx;
        core_log_write_sink sink;
        sink_ctx.fs = fs;
        sink_ctx.fh = fh;
        sink.user = &sink_ctx;
        sink.write = fs_sink_write;
        (void)core_log_event_write_tlv(&ev, &sink);
    }
    (void)fs->file_close(fh);
}

static bool prepare_job_context(const launcher_services_api_v1* services,
                                const LauncherJobInput& input,
                                const std::string& state_root_override,
                                LauncherJobContext& out_ctx,
                                err_t* out_err) {
    const launcher_fs_api_v1* fs = get_fs(services);
    LauncherJobContext ctx;
    std::string state_root;
    core_job_def def;
    core_job_state st;

    if (out_err) {
        *out_err = err_ok();
    }
    if (!services || !fs) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_BAD_STATE);
        }
        return false;
    }
    if (input.job_type == 0u || input.instance_id.empty()) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
        }
        return false;
    }
    if (!launcher_is_safe_id_component(input.instance_id)) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_INSTANCE_INVALID, 0u,
                                (u32)ERRMSG_LAUNCHER_INSTANCE_ID_INVALID);
        }
        return false;
    }

    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_STATE_ROOT_UNAVAILABLE, 0u,
                                (u32)ERRMSG_LAUNCHER_STATE_ROOT_UNAVAILABLE);
        }
        return false;
    }

    build_job_def(input.job_type, def);
    if (!core_job_def_validate(&def)) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_BAD_STATE);
        }
        return false;
    }

    core_job_state_init(&st, generate_job_id(services), input.job_type, def.step_count);

    build_job_paths(state_root, input.instance_id, st.job_id, ctx.paths);
    (void)mkdir_p_best_effort(ctx.paths.job_root);

    if (!write_job_input(fs, ctx.paths, input) ||
        !write_job_def(fs, ctx.paths, def) ||
        !write_job_state(fs, ctx.paths, st)) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_FS, (u16)ERRC_FS_WRITE_FAILED, 0u, (u32)ERRMSG_FS_WRITE_FAILED);
        }
        return false;
    }

    ctx.services = services;
    ctx.input = input;
    ctx.def = def;
    ctx.state = st;
    ctx.state_root = state_root;
    ctx.out_plan = 0;

    init_job_audit(ctx);
    (void)write_job_audit(fs, ctx);

    out_ctx = ctx;
    return true;
}

static bool load_job_context(const launcher_services_api_v1* services,
                             const std::string& state_root_override,
                             const std::string& instance_id,
                             u64 job_id,
                             LauncherJobContext& out_ctx,
                             err_t* out_err) {
    const launcher_fs_api_v1* fs = get_fs(services);
    LauncherJobContext ctx;
    std::string state_root;

    if (out_err) {
        *out_err = err_ok();
    }
    if (!services || !fs) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_BAD_STATE);
        }
        return false;
    }
    if (instance_id.empty() || job_id == 0ull) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
        }
        return false;
    }
    if (!launcher_is_safe_id_component(instance_id)) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_INSTANCE_INVALID, 0u,
                                (u32)ERRMSG_LAUNCHER_INSTANCE_ID_INVALID);
        }
        return false;
    }

    if (!state_root_override.empty()) {
        state_root = state_root_override;
    } else if (!get_state_root(fs, state_root)) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_STATE_ROOT_UNAVAILABLE, 0u,
                                (u32)ERRMSG_LAUNCHER_STATE_ROOT_UNAVAILABLE);
        }
        return false;
    }

    build_job_paths(state_root, instance_id, job_id, ctx.paths);
    if (!read_job_def(fs, ctx.paths, ctx.def) ||
        !read_job_state(fs, ctx.paths, ctx.state) ||
        !read_job_input(fs, ctx.paths, ctx.input)) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_FS, (u16)ERRC_FS_READ_FAILED, 0u, (u32)ERRMSG_FS_READ_FAILED);
        }
        return false;
    }

    if (!core_job_def_validate(&ctx.def) ||
        ctx.def.job_type != ctx.state.job_type ||
        ctx.state.job_id != job_id) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_BAD_STATE);
        }
        return false;
    }

    ctx.services = services;
    ctx.state_root = state_root;
    ctx.out_plan = 0;
    init_job_audit(ctx);
    out_ctx = ctx;
    return true;
}

static bool execute_job_step(LauncherJobContext& ctx, u32 step_id, err_t* out_err) {
    const launcher_services_api_v1* services = ctx.services;
    LauncherAuditLog* audit = &ctx.audit;

    if (out_err) {
        *out_err = err_ok();
    }

    if (ctx.state.job_type == (u32)CORE_JOB_TYPE_LAUNCHER_VERIFY_INSTANCE) {
        LauncherInstanceManifest updated;
        if (!launcher_instance_verify_or_repair(services, ctx.input.instance_id, ctx.state_root, 0u, updated, audit)) {
            if (out_err) {
                *out_err = err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_PAYLOAD_MISSING, (u32)ERRF_INTEGRITY,
                                    (u32)ERRMSG_LAUNCHER_INSTANCE_PAYLOAD_MISSING);
            }
            return false;
        }
        return true;
    }

    if (ctx.state.job_type == (u32)CORE_JOB_TYPE_LAUNCHER_REPAIR_INSTANCE) {
        LauncherInstanceManifest updated;
        if (!launcher_instance_verify_or_repair(services, ctx.input.instance_id, ctx.state_root, 1u, updated, audit)) {
            if (out_err) {
                *out_err = err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_PAYLOAD_MISSING, (u32)ERRF_INTEGRITY,
                                    (u32)ERRMSG_LAUNCHER_INSTANCE_PAYLOAD_MISSING);
            }
            return false;
        }
        return true;
    }

    if (ctx.state.job_type == (u32)CORE_JOB_TYPE_LAUNCHER_APPLY_PACKS) {
        return execute_apply_packs_step(ctx, step_id, out_err);
    }

    if (ctx.state.job_type == (u32)CORE_JOB_TYPE_LAUNCHER_EXPORT_INSTANCE) {
        if (!launcher_instance_export_instance_ex(services,
                                                  ctx.input.instance_id,
                                                  ctx.input.path,
                                                  ctx.state_root,
                                                  ctx.input.mode ? ctx.input.mode : (u32)LAUNCHER_INSTANCE_EXPORT_FULL_BUNDLE,
                                                  audit,
                                                  out_err)) {
            if (out_err && err_is_ok(out_err)) {
                *out_err = err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_EXPORT_FAILED, 0u,
                                    (u32)ERRMSG_LAUNCHER_INSTANCE_EXPORT_FAILED);
            }
            return false;
        }
        return true;
    }

    if (ctx.state.job_type == (u32)CORE_JOB_TYPE_LAUNCHER_IMPORT_INSTANCE) {
        LauncherInstanceManifest created;
        if (!launcher_instance_import_instance_ex(services,
                                                  ctx.input.path,
                                                  ctx.input.instance_id,
                                                  ctx.state_root,
                                                  ctx.input.mode ? ctx.input.mode : (u32)LAUNCHER_INSTANCE_IMPORT_FULL_BUNDLE,
                                                  ctx.input.flags,
                                                  created,
                                                  audit,
                                                  out_err)) {
            if (out_err && err_is_ok(out_err)) {
                *out_err = err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_IMPORT_FAILED, 0u,
                                    (u32)ERRMSG_LAUNCHER_INSTANCE_IMPORT_FAILED);
            }
            return false;
        }
        return true;
    }

    if (ctx.state.job_type == (u32)CORE_JOB_TYPE_LAUNCHER_DIAG_BUNDLE) {
        return execute_diag_bundle_step(ctx, out_err);
    }

    if (ctx.state.job_type == (u32)CORE_JOB_TYPE_LAUNCHER_LAUNCH_PREPARE) {
        LauncherPrelaunchPlan plan;
        LauncherRecoverySuggestion rec;
        std::string pre_err;
        bool ok = launcher_launch_prepare_attempt(services,
                                                  (const LauncherProfile*)0,
                                                  ctx.input.instance_id,
                                                  ctx.state_root,
                                                  ctx.input.overrides,
                                                  plan,
                                                  rec,
                                                  audit,
                                                  &pre_err);
        if (!ok) {
            if (out_err) {
                *out_err = err_make((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_HANDSHAKE_INVALID, 0u,
                                    (u32)ERRMSG_LAUNCHER_HANDSHAKE_INVALID);
            }
            return false;
        }
        if (!plan.validation.ok) {
            if (out_err) {
                *out_err = err_refuse((u16)ERRD_LAUNCHER, (u16)ERRC_LAUNCHER_HANDSHAKE_INVALID,
                                      (u32)ERRMSG_LAUNCHER_HANDSHAKE_INVALID);
            }
            if (ctx.out_plan) {
                *ctx.out_plan = plan;
            }
            return false;
        }
        if (ctx.out_plan) {
            *ctx.out_plan = plan;
        }
        return true;
    }

    if (out_err) {
        *out_err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_INVALID_ARGS, 0u, (u32)ERRMSG_COMMON_INVALID_ARGS);
    }
    return false;
}

static bool run_job_steps(LauncherJobContext& ctx, err_t* out_err) {
    const launcher_fs_api_v1* fs = get_fs(ctx.services);
    core_job_def* def = &ctx.def;
    core_job_state* st = &ctx.state;
    u32 step_index = 0u;

    if (out_err) {
        *out_err = err_ok();
    }
    if (!fs) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_BAD_STATE);
        }
        return false;
    }

    if (!core_job_def_validate(def)) {
        if (out_err) {
            *out_err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_BAD_STATE);
        }
        return false;
    }

    emit_job_event(ctx, CORE_LOG_EVT_OP_BEGIN, 0u, (const err_t*)0, 0u);

    if (st->outcome != (u32)CORE_JOB_OUTCOME_NONE) {
        if (out_err) {
            *out_err = st->last_error;
        }
        return err_is_ok(&st->last_error);
    }

    while (!core_job_state_all_steps_complete(def, st)) {
        u32 step_id = 0u;
        err_t step_err = err_ok();
        bool ok = false;

        if (st->current_step != 0u) {
            u32 idx = 0u;
            if (core_job_def_find_step_index(def, st->current_step, &idx) &&
                !core_job_state_step_complete(st, idx)) {
                step_index = idx;
                step_id = def->steps[idx].step_id;
            } else {
                st->current_step = 0u;
            }
        }

        if (step_id == 0u) {
            if (!core_job_next_step_index(def, st, &step_index)) {
                break;
            }
            step_id = def->steps[step_index].step_id;
        }

        if (ctx.state.job_type == (u32)CORE_JOB_TYPE_LAUNCHER_APPLY_PACKS) {
            if (job_should_skip_apply_packs_step(ctx.services,
                                                 ctx.input.instance_id,
                                                 ctx.state_root,
                                                 step_id,
                                                 *st)) {
                core_job_state_mark_step_complete(st, step_index);
                (void)write_job_state(fs, ctx.paths, *st);
                continue;
            }
        }

        st->current_step = step_id;
        if (!write_job_state(fs, ctx.paths, *st)) {
            if (out_err) {
                *out_err = err_make((u16)ERRD_FS, (u16)ERRC_FS_WRITE_FAILED, 0u, (u32)ERRMSG_FS_WRITE_FAILED);
            }
            return false;
        }

        emit_job_event(ctx, CORE_LOG_EVT_STATE, step_id, (const err_t*)0, 0u);
        ok = execute_job_step(ctx, step_id, &step_err);
        if (!ok) {
            st->last_error = step_err;
            st->retry_count[step_index] += 1u;
            st->outcome = (step_err.flags & (u32)ERRF_POLICY_REFUSAL) ? (u32)CORE_JOB_OUTCOME_REFUSED : (u32)CORE_JOB_OUTCOME_FAILED;
            ctx.audit.err = step_err;
            add_job_reason(ctx.audit, std::string("outcome=") + ((st->outcome == (u32)CORE_JOB_OUTCOME_REFUSED) ? "refused" : "failed"));
            (void)write_job_state(fs, ctx.paths, *st);
            (void)write_job_audit(fs, ctx);
            emit_job_event(ctx,
                           (st->outcome == (u32)CORE_JOB_OUTCOME_REFUSED) ? CORE_LOG_EVT_OP_REFUSED : CORE_LOG_EVT_OP_FAIL,
                           step_id,
                           &step_err,
                           st->outcome);
            if (out_err) {
                *out_err = step_err;
            }
            return false;
        }

        core_job_state_mark_step_complete(st, step_index);
        st->current_step = 0u;
        (void)write_job_state(fs, ctx.paths, *st);
        emit_job_event(ctx, CORE_LOG_EVT_OP_OK, step_id, (const err_t*)0, 0u);
    }

    if (core_job_state_all_steps_complete(def, st)) {
        st->outcome = (u32)CORE_JOB_OUTCOME_OK;
        st->last_error = err_ok();
        ctx.audit.err = err_ok();
        add_job_reason(ctx.audit, "outcome=ok");
        (void)write_job_state(fs, ctx.paths, *st);
        (void)write_job_audit(fs, ctx);
        emit_job_event(ctx, CORE_LOG_EVT_OP_OK, 0u, (const err_t*)0, st->outcome);
        return true;
    }

    if (out_err) {
        *out_err = err_make((u16)ERRD_COMMON, (u16)ERRC_COMMON_BAD_STATE, (u32)ERRF_FATAL, (u32)ERRMSG_COMMON_BAD_STATE);
    }
    return false;
}

} /* namespace */

LauncherJobPackChange::LauncherJobPackChange()
    : content_type(0u),
      pack_id(),
      has_enabled(0u),
      enabled(0u),
      has_update_policy(0u),
      update_policy(0u) {
}

LauncherJobInput::LauncherJobInput()
    : schema_version(LAUNCHER_JOB_INPUT_TLV_VERSION),
      job_type(0u),
      instance_id(),
      path(),
      aux_path(),
      aux_id(),
      mode(0u),
      flags(0u),
      overrides(),
      pack_changes() {
}

bool launcher_job_input_to_tlv_bytes(const LauncherJobInput& in,
                                     std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    TlvWriter overrides;
    size_t i;

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_JOB_INPUT_TLV_VERSION);
    if (in.job_type != 0u) {
        w.add_u32(LAUNCHER_JOB_INPUT_TLV_TAG_JOB_TYPE, in.job_type);
    }
    if (!in.instance_id.empty()) {
        w.add_string(LAUNCHER_JOB_INPUT_TLV_TAG_INSTANCE_ID, in.instance_id);
    }
    if (!in.path.empty()) {
        w.add_string(LAUNCHER_JOB_INPUT_TLV_TAG_PATH, in.path);
    }
    if (!in.aux_path.empty()) {
        w.add_string(LAUNCHER_JOB_INPUT_TLV_TAG_AUX_PATH, in.aux_path);
    }
    if (!in.aux_id.empty()) {
        w.add_string(LAUNCHER_JOB_INPUT_TLV_TAG_AUX_ID, in.aux_id);
    }
    if (in.mode != 0u) {
        w.add_u32(LAUNCHER_JOB_INPUT_TLV_TAG_MODE, in.mode);
    }
    if (in.flags != 0u) {
        w.add_u32(LAUNCHER_JOB_INPUT_TLV_TAG_FLAGS, in.flags);
    }

    if (in.overrides.request_safe_mode) {
        overrides.add_u32(LAUNCHER_JOB_INPUT_OVERRIDE_SAFE_MODE, 1u);
    }
    if (in.overrides.safe_mode_allow_network) {
        overrides.add_u32(LAUNCHER_JOB_INPUT_OVERRIDE_SAFE_MODE_ALLOW_NET, 1u);
    }
    if (in.overrides.has_gfx_backend) {
        overrides.add_string(LAUNCHER_JOB_INPUT_OVERRIDE_GFX_BACKEND, in.overrides.gfx_backend);
    }
    if (in.overrides.has_renderer_api) {
        overrides.add_string(LAUNCHER_JOB_INPUT_OVERRIDE_RENDERER_API, in.overrides.renderer_api);
    }
    if (in.overrides.has_window_mode) {
        overrides.add_u32(LAUNCHER_JOB_INPUT_OVERRIDE_WINDOW_MODE, in.overrides.window_mode);
    }
    if (in.overrides.has_window_width) {
        overrides.add_u32(LAUNCHER_JOB_INPUT_OVERRIDE_WINDOW_WIDTH, in.overrides.window_width);
    }
    if (in.overrides.has_window_height) {
        overrides.add_u32(LAUNCHER_JOB_INPUT_OVERRIDE_WINDOW_HEIGHT, in.overrides.window_height);
    }
    if (in.overrides.has_window_dpi) {
        overrides.add_u32(LAUNCHER_JOB_INPUT_OVERRIDE_WINDOW_DPI, in.overrides.window_dpi);
    }
    if (in.overrides.has_window_monitor) {
        overrides.add_u32(LAUNCHER_JOB_INPUT_OVERRIDE_WINDOW_MONITOR, in.overrides.window_monitor);
    }
    if (in.overrides.has_audio_device_id) {
        overrides.add_string(LAUNCHER_JOB_INPUT_OVERRIDE_AUDIO_DEVICE_ID, in.overrides.audio_device_id);
    }
    if (in.overrides.has_input_backend) {
        overrides.add_string(LAUNCHER_JOB_INPUT_OVERRIDE_INPUT_BACKEND, in.overrides.input_backend);
    }
    if (in.overrides.has_allow_network) {
        overrides.add_u32(LAUNCHER_JOB_INPUT_OVERRIDE_ALLOW_NETWORK, in.overrides.allow_network ? 1u : 0u);
    }
    if (in.overrides.has_debug_flags) {
        overrides.add_u32(LAUNCHER_JOB_INPUT_OVERRIDE_DEBUG_FLAGS, in.overrides.debug_flags);
    }
    if (!overrides.bytes().empty()) {
        w.add_container(LAUNCHER_JOB_INPUT_TLV_TAG_OVERRIDES, overrides.bytes());
    }

    for (i = 0u; i < in.pack_changes.size(); ++i) {
        const LauncherJobPackChange& pc = in.pack_changes[i];
        TlvWriter pack;
        pack.add_u32(LAUNCHER_JOB_INPUT_PACK_TAG_TYPE, pc.content_type);
        pack.add_string(LAUNCHER_JOB_INPUT_PACK_TAG_ID, pc.pack_id);
        pack.add_u32(LAUNCHER_JOB_INPUT_PACK_TAG_HAS_ENABLED, pc.has_enabled ? 1u : 0u);
        if (pc.has_enabled) {
            pack.add_u32(LAUNCHER_JOB_INPUT_PACK_TAG_ENABLED, pc.enabled ? 1u : 0u);
        }
        pack.add_u32(LAUNCHER_JOB_INPUT_PACK_TAG_HAS_POLICY, pc.has_update_policy ? 1u : 0u);
        if (pc.has_update_policy) {
            pack.add_u32(LAUNCHER_JOB_INPUT_PACK_TAG_POLICY, pc.update_policy);
        }
        w.add_container(LAUNCHER_JOB_INPUT_TLV_TAG_PACK_CHANGE, pack.bytes());
    }

    out_bytes = w.bytes();
    return true;
}

static void read_job_input_pack_change(const unsigned char* data, size_t size, LauncherJobPackChange& out_change) {
    TlvReader r(data, size);
    TlvRecord rec;
    LauncherJobPackChange pc;
    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_JOB_INPUT_PACK_TAG_TYPE: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                pc.content_type = v;
            }
            break;
        }
        case LAUNCHER_JOB_INPUT_PACK_TAG_ID:
            pc.pack_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_JOB_INPUT_PACK_TAG_HAS_ENABLED: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                pc.has_enabled = v ? 1u : 0u;
            }
            break;
        }
        case LAUNCHER_JOB_INPUT_PACK_TAG_ENABLED: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                pc.enabled = v ? 1u : 0u;
            }
            break;
        }
        case LAUNCHER_JOB_INPUT_PACK_TAG_HAS_POLICY: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                pc.has_update_policy = v ? 1u : 0u;
            }
            break;
        }
        case LAUNCHER_JOB_INPUT_PACK_TAG_POLICY: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                pc.update_policy = v;
            }
            break;
        }
        default:
            break;
        }
    }
    out_change = pc;
}

static void read_job_input_overrides(const unsigned char* data, size_t size, LauncherLaunchOverrides& out_ov) {
    TlvReader r(data, size);
    TlvRecord rec;
    LauncherLaunchOverrides ov;
    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_JOB_INPUT_OVERRIDE_SAFE_MODE: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                ov.request_safe_mode = v ? 1u : 0u;
            }
            break;
        }
        case LAUNCHER_JOB_INPUT_OVERRIDE_SAFE_MODE_ALLOW_NET: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                ov.safe_mode_allow_network = v ? 1u : 0u;
            }
            break;
        }
        case LAUNCHER_JOB_INPUT_OVERRIDE_GFX_BACKEND:
            ov.has_gfx_backend = 1u;
            ov.gfx_backend = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_JOB_INPUT_OVERRIDE_RENDERER_API:
            ov.has_renderer_api = 1u;
            ov.renderer_api = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_JOB_INPUT_OVERRIDE_WINDOW_MODE: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                ov.has_window_mode = 1u;
                ov.window_mode = v;
            }
            break;
        }
        case LAUNCHER_JOB_INPUT_OVERRIDE_WINDOW_WIDTH: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                ov.has_window_width = 1u;
                ov.window_width = v;
            }
            break;
        }
        case LAUNCHER_JOB_INPUT_OVERRIDE_WINDOW_HEIGHT: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                ov.has_window_height = 1u;
                ov.window_height = v;
            }
            break;
        }
        case LAUNCHER_JOB_INPUT_OVERRIDE_WINDOW_DPI: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                ov.has_window_dpi = 1u;
                ov.window_dpi = v;
            }
            break;
        }
        case LAUNCHER_JOB_INPUT_OVERRIDE_WINDOW_MONITOR: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                ov.has_window_monitor = 1u;
                ov.window_monitor = v;
            }
            break;
        }
        case LAUNCHER_JOB_INPUT_OVERRIDE_AUDIO_DEVICE_ID:
            ov.has_audio_device_id = 1u;
            ov.audio_device_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_JOB_INPUT_OVERRIDE_INPUT_BACKEND:
            ov.has_input_backend = 1u;
            ov.input_backend = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_JOB_INPUT_OVERRIDE_ALLOW_NETWORK: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                ov.has_allow_network = 1u;
                ov.allow_network = v ? 1u : 0u;
            }
            break;
        }
        case LAUNCHER_JOB_INPUT_OVERRIDE_DEBUG_FLAGS: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                ov.has_debug_flags = 1u;
                ov.debug_flags = v;
            }
            break;
        }
        default:
            break;
        }
    }
    out_ov = ov;
}

bool launcher_job_input_from_tlv_bytes(const unsigned char* data,
                                       size_t size,
                                       LauncherJobInput& out_in) {
    TlvReader r(data, size);
    TlvRecord rec;
    LauncherJobInput input;
    u32 schema_version = 0u;

    if (!data || size == 0u) {
        return false;
    }

    while (r.next(rec)) {
        if (rec.tag == LAUNCHER_TLV_TAG_SCHEMA_VERSION) {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                schema_version = v;
            }
            continue;
        }
        switch (rec.tag) {
        case LAUNCHER_JOB_INPUT_TLV_TAG_JOB_TYPE: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                input.job_type = v;
            }
            break;
        }
        case LAUNCHER_JOB_INPUT_TLV_TAG_INSTANCE_ID:
            input.instance_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_JOB_INPUT_TLV_TAG_PATH:
            input.path = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_JOB_INPUT_TLV_TAG_AUX_PATH:
            input.aux_path = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_JOB_INPUT_TLV_TAG_AUX_ID:
            input.aux_id = tlv_read_string(rec.payload, rec.len);
            break;
        case LAUNCHER_JOB_INPUT_TLV_TAG_MODE: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                input.mode = v;
            }
            break;
        }
        case LAUNCHER_JOB_INPUT_TLV_TAG_FLAGS: {
            u32 v = 0u;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                input.flags = v;
            }
            break;
        }
        case LAUNCHER_JOB_INPUT_TLV_TAG_PACK_CHANGE: {
            LauncherJobPackChange pc;
            read_job_input_pack_change(rec.payload, rec.len, pc);
            if (!pc.pack_id.empty() || pc.content_type != 0u) {
                input.pack_changes.push_back(pc);
            }
            break;
        }
        case LAUNCHER_JOB_INPUT_TLV_TAG_OVERRIDES:
            read_job_input_overrides(rec.payload, rec.len, input.overrides);
            break;
        default:
            break;
        }
    }

    if (schema_version == 0u) {
        schema_version = LAUNCHER_JOB_INPUT_TLV_VERSION;
    }
    if (schema_version > LAUNCHER_JOB_INPUT_TLV_VERSION) {
        return false;
    }
    input.schema_version = schema_version;
    out_in = input;
    return true;
}

bool launcher_job_run(const launcher_services_api_v1* services,
                      const LauncherJobInput& input,
                      const std::string& state_root_override,
                      core_job_state& out_state,
                      err_t* out_err,
                      LauncherAuditLog* out_audit) {
    LauncherJobContext ctx;
    bool ok;

    if (out_err) {
        *out_err = err_ok();
    }

    if (!prepare_job_context(services, input, state_root_override, ctx, out_err)) {
        core_job_state_clear(&out_state);
        return false;
    }

    ok = run_job_steps(ctx, out_err);
    out_state = ctx.state;
    if (out_audit) {
        *out_audit = ctx.audit;
    }
    return ok;
}

bool launcher_job_resume(const launcher_services_api_v1* services,
                         const std::string& state_root_override,
                         const std::string& instance_id,
                         u64 job_id,
                         core_job_state& out_state,
                         err_t* out_err,
                         LauncherAuditLog* out_audit) {
    LauncherJobContext ctx;
    bool ok;

    if (out_err) {
        *out_err = err_ok();
    }
    if (!load_job_context(services, state_root_override, instance_id, job_id, ctx, out_err)) {
        core_job_state_clear(&out_state);
        return false;
    }
    ok = run_job_steps(ctx, out_err);
    out_state = ctx.state;
    if (out_audit) {
        *out_audit = ctx.audit;
    }
    return ok;
}

bool launcher_job_state_load(const launcher_services_api_v1* services,
                             const std::string& state_root_override,
                             const std::string& instance_id,
                             u64 job_id,
                             core_job_state& out_state) {
    LauncherJobContext ctx;
    err_t err;
    if (!load_job_context(services, state_root_override, instance_id, job_id, ctx, &err)) {
        return false;
    }
    out_state = ctx.state;
    return true;
}

bool launcher_job_run_launch_prepare(const launcher_services_api_v1* services,
                                     const std::string& instance_id,
                                     const std::string& state_root_override,
                                     const LauncherLaunchOverrides& overrides,
                                     LauncherPrelaunchPlan& out_plan,
                                     err_t* out_err) {
    LauncherJobContext ctx;
    LauncherJobInput input;
    bool ok;

    input.job_type = (u32)CORE_JOB_TYPE_LAUNCHER_LAUNCH_PREPARE;
    input.instance_id = instance_id;
    input.overrides = overrides;

    if (!prepare_job_context(services, input, state_root_override, ctx, out_err)) {
        return false;
    }
    ctx.out_plan = &out_plan;
    ok = run_job_steps(ctx, out_err);
    return ok;
}

} /* namespace launcher_core */
} /* namespace dom */
