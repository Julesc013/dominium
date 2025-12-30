#include "dsk_jobs_internal.h"

#include <algorithm>
#include <cstdio>

static dsk_status_t dsk_jobs_error(dsk_u16 code, dsk_u16 subcode) {
    return dsk_error_make(DSK_DOMAIN_KERNEL, code, subcode, DSK_ERROR_FLAG_USER_ACTIONABLE);
}

static bool dsk_path_has_parent_ref(const std::string &path) {
    size_t i;
    if (path.empty()) {
        return false;
    }
    if (!path.empty() && (path[0] == '/' || path[0] == '\\')) {
        return true;
    }
    if (path.size() >= 2u && ((path[0] >= 'A' && path[0] <= 'Z') || (path[0] >= 'a' && path[0] <= 'z'))
        && path[1] == ':') {
        return true;
    }
    for (i = 0u; i + 1u < path.size(); ++i) {
        if (path[i] == '.' && path[i + 1u] == '.') {
            if (i == 0u || path[i - 1u] == '/' || path[i - 1u] == '\\') {
                size_t end = i + 2u;
                if (end == path.size() || path[end] == '/' || path[end] == '\\') {
                    return true;
                }
            }
        }
    }
    return false;
}

static dsk_status_t dsk_fs_join(const dss_fs_api_t *fs,
                                const std::string &a,
                                const std::string &b,
                                std::string *out_path) {
    if (!out_path) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (!fs || !fs->join_path) {
        if (a.empty()) {
            *out_path = b;
        } else if (b.empty()) {
            *out_path = a;
        } else if (a[a.size() - 1u] == '/' || a[a.size() - 1u] == '\\') {
            *out_path = a + b;
        } else {
            *out_path = a + "/" + b;
        }
        return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    }
    {
        dss_error_t st = fs->join_path(fs->ctx, a.c_str(), b.c_str(), out_path);
        return dss_error_is_ok(st)
            ? dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u)
            : dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_IO_ERROR, DSK_SUBCODE_NONE, 0u);
    }
}

static bool dsk_is_root_dir(const std::string &path) {
    if (path == "/" || path == "\\") {
        return true;
    }
    if (path.size() == 2u) {
        char c = path[0u];
        if (((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z')) && path[1u] == ':') {
            return true;
        }
    }
    if (path.size() == 3u) {
        char c = path[0u];
        if (((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z')) &&
            path[1u] == ':' && (path[2u] == '/' || path[2u] == '\\')) {
            return true;
        }
    }
    return false;
}

static dsk_status_t dsk_fs_make_dirs(const dss_fs_api_t *fs, const std::string &path) {
    size_t i;
    std::string current;
    if (!fs || !fs->make_dir) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (path.empty()) {
        return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    }
    current.clear();
    for (i = 0u; i <= path.size(); ++i) {
        char c = (i < path.size()) ? path[i] : '\0';
        if (c == '/' || c == '\\' || c == '\0') {
            if (!current.empty()) {
                if (dsk_is_root_dir(current)) {
                    /* Skip drive roots or filesystem roots. */
                    if (current.size() == 2u && current[1u] == ':') {
                        current.push_back('/');
                    }
                    continue;
                }
                dss_error_t mk = fs->make_dir(fs->ctx, current.c_str());
                if (!dss_error_is_ok(mk)) {
                    if (mk.code == DSS_CODE_SANDBOX_VIOLATION) {
                        continue;
                    }
                    dss_bool exists = DSS_FALSE;
                    if (fs->exists && dss_error_is_ok(fs->exists(fs->ctx, current.c_str(), &exists)) && exists) {
                        /* ok */
                    } else {
                        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_IO_ERROR, DSK_SUBCODE_NONE, 0u);
                    }
                }
            }
        }
        if (c != '\0') {
            current.push_back(c);
        }
    }
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_copy_file(const dss_fs_api_t *fs,
                                  const std::string &src,
                                  const std::string &dst) {
    std::vector<dsk_u8> bytes;
    dss_error_t st;
    if (!fs || !fs->read_file_bytes || !fs->write_file_bytes_atomic) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    st = fs->read_file_bytes(fs->ctx, src.c_str(), &bytes);
    if (!dss_error_is_ok(st)) {
        return dss_to_dsk_error(st);
    }
    st = fs->write_file_bytes_atomic(fs->ctx,
                                     dst.c_str(),
                                     bytes.empty() ? 0 : &bytes[0],
                                     (dss_u32)bytes.size());
    if (!dss_error_is_ok(st)) {
        return dss_to_dsk_error(st);
    }
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static std::string dsk_format_hex64(dsk_u64 value) {
    char buf[17];
    std::snprintf(buf, sizeof(buf), "%016llx", (unsigned long long)value);
    return std::string(buf);
}

dsk_status_t dsk_stage_root_path(const dss_fs_api_t *fs,
                                 dsk_u64 plan_digest64,
                                 std::string *out_stage_root) {
    std::string temp;
    std::string stage_name;
    if (!out_stage_root || !fs || !fs->temp_dir) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    {
        dss_error_t st = fs->temp_dir(fs->ctx, &temp);
        if (!dss_error_is_ok(st)) {
            return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_IO_ERROR, DSK_SUBCODE_NONE, 0u);
        }
    }
    stage_name = std::string("dsk_stage_") + dsk_format_hex64(plan_digest64);
    return dsk_fs_join(fs, temp, stage_name, out_stage_root);
}

static bool dsk_is_root_token(const std::string &root) {
    return root.size() >= 5u && root.compare(0u, 5u, "root:") == 0;
}

dsk_status_t dsk_resolve_install_roots(const dsk_plan_t &plan,
                                       const dss_services_t *services,
                                       std::vector<std::string> *out_roots) {
    size_t i;
    if (!services || !out_roots) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    out_roots->clear();
    for (i = 0u; i < plan.install_roots.size(); ++i) {
        const std::string &root = plan.install_roots[i];
        if (!dsk_is_root_token(root)) {
            out_roots->push_back(root);
            continue;
        }
        if (!services->perms.get_user_scope_paths || !services->perms.get_system_scope_paths) {
            return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_UNSUPPORTED_PLATFORM, DSK_SUBCODE_NONE, 0u);
        }
        dss_scope_paths_t paths;
        if (root == "root:portable" || root == "root:steam_library") {
            dss_error_t st = services->perms.get_user_scope_paths(services->perms.ctx, &paths);
            if (!dss_error_is_ok(st) || paths.install_root.empty()) {
                return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_UNSUPPORTED_PLATFORM, DSK_SUBCODE_NONE, 0u);
            }
            out_roots->push_back(paths.install_root);
        } else {
            dss_error_t st = services->perms.get_system_scope_paths(services->perms.ctx, &paths);
            if (!dss_error_is_ok(st) || paths.install_root.empty()) {
                return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_UNSUPPORTED_PLATFORM, DSK_SUBCODE_NONE, 0u);
            }
            out_roots->push_back(paths.install_root);
        }
    }
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_stage_path_for_op(const dsk_plan_file_op_t &op,
                                          const std::string &stage_root,
                                          const dss_fs_api_t *fs,
                                          std::string *out_path) {
    std::string root_dir;
    std::string root_path;
    char buf[32];
    if (!out_path) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    std::snprintf(buf, sizeof(buf), "root_%u", (unsigned)op.target_root_id);
    root_dir = buf;
    dsk_status_t st = dsk_fs_join(fs, stage_root, root_dir, &root_path);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    return dsk_fs_join(fs, root_path, op.to_path, out_path);
}

dsk_status_t dsk_stage_file_op(const dsk_plan_file_op_t &op,
                               const dsk_plan_t &plan,
                               const std::string &stage_root,
                               const dss_services_t *services) {
    std::string src_path;
    std::string dst_path;
    std::string parent_dir;
    if (!services) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (op.target_root_id >= plan.install_roots.size()) {
        return dsk_jobs_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }
    if (dsk_path_has_parent_ref(op.to_path)) {
        return dsk_jobs_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }
    if ((op.op_kind == DSK_PLAN_FILE_OP_COPY || op.op_kind == DSK_PLAN_FILE_OP_EXTRACT) &&
        dsk_path_has_parent_ref(op.from_path)) {
        return dsk_jobs_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }

    dsk_status_t st = dsk_stage_path_for_op(op, stage_root, &services->fs, &dst_path);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    parent_dir = dst_path;
    {
        size_t pos = parent_dir.find_last_of("/\\");
        if (pos != std::string::npos) {
            parent_dir.erase(pos);
        } else {
            parent_dir.clear();
        }
    }

    if (op.op_kind == DSK_PLAN_FILE_OP_REMOVE) {
        return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    }

    if (op.op_kind == DSK_PLAN_FILE_OP_MKDIR) {
        st = dsk_fs_make_dirs(&services->fs, dst_path);
        if (!dsk_error_is_ok(st) && services->fs.make_dir) {
            dss_error_t mk = services->fs.make_dir(services->fs.ctx, dst_path.c_str());
            if (dss_error_is_ok(mk)) {
                st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
            }
        }
        return st;
    }

    if (plan.payload_root.empty()) {
        return dsk_jobs_error(DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_MISSING_FIELD);
    }
    st = dsk_fs_join(&services->fs, plan.payload_root, op.from_path, &src_path);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    if (!parent_dir.empty()) {
        st = dsk_fs_make_dirs(&services->fs, parent_dir);
        if (!dsk_error_is_ok(st) && services->fs.make_dir) {
            dss_error_t mk = services->fs.make_dir(services->fs.ctx, parent_dir.c_str());
            if (dss_error_is_ok(mk)) {
                st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
            }
        }
        if (!dsk_error_is_ok(st)) {
            return st;
        }
        if (services->fs.exists) {
            dss_bool exists = DSS_FALSE;
            dss_error_t ex = services->fs.exists(services->fs.ctx, parent_dir.c_str(), &exists);
            if (!dss_error_is_ok(ex)) {
                return dss_to_dsk_error(ex);
            }
            if (!exists && services->fs.make_dir) {
                dss_error_t mk = services->fs.make_dir(services->fs.ctx, parent_dir.c_str());
                if (!dss_error_is_ok(mk)) {
                    return dss_to_dsk_error(mk);
                }
            }
        }
    }
    if (op.op_kind == DSK_PLAN_FILE_OP_COPY) {
        return dsk_copy_file(&services->fs, src_path, dst_path);
    }
    if (op.op_kind == DSK_PLAN_FILE_OP_EXTRACT) {
        if (!services->archive.extract_deterministic) {
            return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
        }
        return dss_error_is_ok(services->archive.extract_deterministic(services->archive.ctx,
                                                                       src_path.c_str(),
                                                                       dst_path.c_str()))
            ? dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u)
            : dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_IO_ERROR, DSK_SUBCODE_NONE, 0u);
    }
    return dsk_jobs_error(DSK_CODE_UNSUPPORTED_PLATFORM, DSK_SUBCODE_NONE);
}

dsk_status_t dsk_verify_file_op(const dsk_plan_file_op_t &op,
                                const std::string &stage_root,
                                const dss_services_t *services) {
    std::string stage_path;
    if (!services) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    dsk_status_t st = dsk_stage_path_for_op(op, stage_root, &services->fs, &stage_path);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    if (op.op_kind != DSK_PLAN_FILE_OP_COPY) {
        return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    }
    if (op.digest64 != 0u) {
        dss_error_t hst;
        dss_u64 digest = 0u;
        if (!services->hash.compute_digest64_file) {
            return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
        }
        hst = services->hash.compute_digest64_file(services->hash.ctx, stage_path.c_str(), &digest);
        if (!dss_error_is_ok(hst) || digest != op.digest64) {
            return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INTEGRITY_ERROR, DSK_SUBCODE_INVALID_FIELD, 0u);
        }
    }
    if (op.size != 0u && services->fs.file_size) {
        dss_u64 size = 0u;
        dss_error_t sst = services->fs.file_size(services->fs.ctx, stage_path.c_str(), &size);
        if (!dss_error_is_ok(sst) || size != op.size) {
            return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INTEGRITY_ERROR, DSK_SUBCODE_INVALID_FIELD, 0u);
        }
    }
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}
