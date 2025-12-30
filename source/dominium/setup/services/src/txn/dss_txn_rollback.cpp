#include "dss/dss_txn.h"

#include <algorithm>

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

static dss_error_t dss_txn_exec_simple(const dss_fs_api_t *fs,
                                       const dss_archive_api_t *archive,
                                       dss_u16 op_kind,
                                       const std::string &src,
                                       const std::string &dst) {
    dss_error_t st;
    dss_bool exists = DSS_FALSE;
    switch (op_kind) {
    case DSS_TXN_STEP_MKDIR:
        if (!fs || !fs->exists || !fs->make_dir) {
            return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
        }
        st = fs->exists(fs->ctx, dst.c_str(), &exists);
        if (dss_error_is_ok(st) && exists) {
            return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
        }
        return fs->make_dir(fs->ctx, dst.c_str());
    case DSS_TXN_STEP_COPY_FILE:
        return dss_txn_copy_file(fs, src, dst);
    case DSS_TXN_STEP_EXTRACT_ARCHIVE:
        if (!archive || !archive->extract_deterministic) {
            return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
        }
        return archive->extract_deterministic(archive->ctx, src.c_str(), dst.c_str());
    case DSS_TXN_STEP_ATOMIC_RENAME:
        if (!fs || !fs->exists || !fs->atomic_rename) {
            return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
        }
        st = fs->exists(fs->ctx, src.c_str(), &exists);
        if (dss_error_is_ok(st) && !exists) {
            return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
        }
        return fs->atomic_rename(fs->ctx, src.c_str(), dst.c_str());
    case DSS_TXN_STEP_DIR_SWAP:
        if (!fs || !fs->dir_swap) {
            return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
        }
        return fs->dir_swap(fs->ctx, src.c_str(), dst.c_str());
    case DSS_TXN_STEP_DELETE_FILE:
        if (!fs || !fs->exists || !fs->remove_file) {
            return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
        }
        st = fs->exists(fs->ctx, dst.c_str(), &exists);
        if (dss_error_is_ok(st) && !exists) {
            return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
        }
        return fs->remove_file(fs->ctx, dst.c_str());
    case DSS_TXN_STEP_REMOVE_DIR:
        if (!fs || !fs->exists || !fs->remove_dir_if_empty) {
            return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
        }
        st = fs->exists(fs->ctx, dst.c_str(), &exists);
        if (dss_error_is_ok(st) && !exists) {
            return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
        }
        st = fs->remove_dir_if_empty(fs->ctx, dst.c_str());
        if (dss_error_is_ok(st)) {
            return st;
        }
        if (fs->list_dir) {
            std::vector<std::string> entries;
            dss_error_t lst = fs->list_dir(fs->ctx, dst.c_str(), &entries);
            if (dss_error_is_ok(lst) && !entries.empty()) {
                return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
            }
        }
        return st;
    default:
        return dss_txn_error(DSS_CODE_NOT_SUPPORTED, DSS_SUBCODE_NONE);
    }
}

dss_error_t dss_txn_rollback(const dss_fs_api_t *fs,
                             const dss_txn_journal_t *journal,
                             dss_u32 last_completed_step) {
    if (!journal) {
        return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    if (journal->steps.empty()) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
    }
    for (std::vector<dss_txn_step_t>::const_reverse_iterator it = journal->steps.rbegin();
         it != journal->steps.rend();
         ++it) {
        const dss_txn_step_t &step = *it;
        if (step.step_id > last_completed_step) {
            continue;
        }
        dss_error_t st = dss_txn_exec_simple(fs,
                                             0,
                                             step.rollback_kind,
                                             step.rollback_src,
                                             step.rollback_dst);
        if (!dss_error_is_ok(st)) {
            return st;
        }
    }
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}
