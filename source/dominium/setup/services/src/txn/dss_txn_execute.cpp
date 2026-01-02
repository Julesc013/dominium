#include "dss_txn_internal.h"

#include <cstring>

static dss_error_t dss_txn_error(dss_u16 code, dss_u16 subcode) {
    return dss_error_make(DSS_DOMAIN_SERVICES, code, subcode, DSS_ERROR_FLAG_USER_ACTIONABLE);
}

static dss_error_t dss_txn_copy_file(const dss_fs_api_t *fs,
                                     const std::string &src,
                                     const std::string &dst) {
    std::vector<dss_u8> bytes;
    dss_error_t st;
    if (!fs || !fs->read_file_bytes || !fs->write_file_bytes_atomic) {
        return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    st = fs->read_file_bytes(fs->ctx, src.c_str(), &bytes);
    if (!dss_error_is_ok(st)) {
        return st;
    }
    return fs->write_file_bytes_atomic(fs->ctx,
                                       dst.c_str(),
                                       bytes.empty() ? 0 : &bytes[0],
                                       (dss_u32)bytes.size());
}

dss_error_t dss_txn_execute_step(const dss_fs_api_t *fs,
                                 const dss_archive_api_t *archive,
                                 const dss_txn_step_t *step) {
    dss_error_t st;
    dss_bool exists = DSS_FALSE;
    if (!step) {
        return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    switch (step->op_kind) {
    case DSS_TXN_STEP_MKDIR:
        if (!fs || !fs->exists || !fs->make_dir) {
            return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
        }
        st = fs->exists(fs->ctx, step->dst_path.c_str(), &exists);
        if (dss_error_is_ok(st) && exists) {
            st = dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
            break;
        }
        st = fs->make_dir(fs->ctx, step->dst_path.c_str());
        break;
    case DSS_TXN_STEP_COPY_FILE:
        st = dss_txn_copy_file(fs, step->src_path, step->dst_path);
        break;
    case DSS_TXN_STEP_EXTRACT_ARCHIVE:
        if (!archive || !archive->extract_deterministic) {
            return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
        }
        st = archive->extract_deterministic(archive->ctx,
                                            step->src_path.c_str(),
                                            step->dst_path.c_str());
        break;
    case DSS_TXN_STEP_ATOMIC_RENAME:
        if (!fs || !fs->exists || !fs->atomic_rename) {
            return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
        }
        st = fs->exists(fs->ctx, step->src_path.c_str(), &exists);
        if (dss_error_is_ok(st) && !exists) {
            st = dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
            break;
        }
        st = fs->atomic_rename(fs->ctx, step->src_path.c_str(), step->dst_path.c_str());
        break;
    case DSS_TXN_STEP_DIR_SWAP:
        if (!fs || !fs->dir_swap) {
            return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
        }
        st = fs->dir_swap(fs->ctx, step->src_path.c_str(), step->dst_path.c_str());
        break;
    case DSS_TXN_STEP_DELETE_FILE:
        if (!fs || !fs->exists || !fs->remove_file) {
            return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
        }
        st = fs->exists(fs->ctx, step->dst_path.c_str(), &exists);
        if (dss_error_is_ok(st) && !exists) {
            st = dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
            break;
        }
        st = fs->remove_file(fs->ctx, step->dst_path.c_str());
        break;
    case DSS_TXN_STEP_REMOVE_DIR:
        if (!fs || !fs->exists || !fs->remove_dir_if_empty) {
            return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
        }
        st = fs->exists(fs->ctx, step->dst_path.c_str(), &exists);
        if (dss_error_is_ok(st) && !exists) {
            st = dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
            break;
        }
        st = fs->remove_dir_if_empty(fs->ctx, step->dst_path.c_str());
        break;
    default:
        return dss_txn_error(DSS_CODE_NOT_SUPPORTED, DSS_SUBCODE_NONE);
    }
    if (!dss_error_is_ok(st)) {
        return st;
    }
    if (dss_txn_failpoint_after_commit_step(step->step_id)) {
        return dss_txn_error(DSS_CODE_INTERNAL, DSS_SUBCODE_NONE);
    }
    return st;
}

dss_error_t dss_txn_execute(const dss_fs_api_t *fs,
                            const dss_archive_api_t *archive,
                            const dss_txn_journal_t *journal,
                            dss_u32 start_step,
                            dss_u32 *out_last_step) {
    dss_u32 i;
    dss_u32 last_step = 0u;
    if (out_last_step) {
        *out_last_step = 0u;
    }
    if (!journal) {
        return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    for (i = 0u; i < journal->steps.size(); ++i) {
        const dss_txn_step_t &step = journal->steps[i];
        if (step.step_id < start_step) {
            last_step = step.step_id;
            continue;
        }
        dss_error_t st = dss_txn_execute_step(fs, archive, &step);
        if (!dss_error_is_ok(st)) {
            if (out_last_step) {
                *out_last_step = last_step;
            }
            return st;
        }
        last_step = step.step_id;
        if (out_last_step) {
            *out_last_step = last_step;
        }
    }
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}
