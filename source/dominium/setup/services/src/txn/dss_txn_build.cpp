#include "dss/dss_txn.h"

#include "../fs/dss_fs_internal.h"

#include <algorithm>
#include <cstdio>
#include <cstring>

static dss_error_t dss_txn_error(dss_u16 code, dss_u16 subcode) {
    return dss_error_make(DSS_DOMAIN_SERVICES, code, subcode, DSS_ERROR_FLAG_USER_ACTIONABLE);
}

static dss_error_t dss_parse_u16(const dsk_tlv_record_t &rec, dss_u16 *out) {
    if (!out) {
        return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    if (rec.length != 2u) {
        return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    *out = (dss_u16)rec.payload[0] | (dss_u16)((dss_u16)rec.payload[1] << 8);
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_parse_u32(const dsk_tlv_record_t &rec, dss_u32 *out) {
    if (!out) {
        return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    if (rec.length != 4u) {
        return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    *out = (dss_u32)rec.payload[0]
         | ((dss_u32)rec.payload[1] << 8)
         | ((dss_u32)rec.payload[2] << 16)
         | ((dss_u32)rec.payload[3] << 24);
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_parse_u64(const dsk_tlv_record_t &rec, dss_u64 *out) {
    if (!out) {
        return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    if (rec.length != 8u) {
        return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    *out = (dss_u64)rec.payload[0]
         | ((dss_u64)rec.payload[1] << 8)
         | ((dss_u64)rec.payload[2] << 16)
         | ((dss_u64)rec.payload[3] << 24)
         | ((dss_u64)rec.payload[4] << 32)
         | ((dss_u64)rec.payload[5] << 40)
         | ((dss_u64)rec.payload[6] << 48)
         | ((dss_u64)rec.payload[7] << 56);
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_parse_string(const dsk_tlv_record_t &rec, std::string *out) {
    if (!out) {
        return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    out->assign(reinterpret_cast<const char *>(rec.payload), rec.length);
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static std::string dss_txn_root_dir(dss_u32 index) {
    char buf[32];
    std::snprintf(buf, sizeof(buf), "root_%u", (unsigned)index);
    return std::string(buf);
}

static dss_error_t dss_txn_join(const std::string &a,
                                const std::string &b,
                                std::string *out) {
    if (!out) {
        return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    if (a.empty()) {
        *out = b;
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
    }
    if (b.empty()) {
        *out = a;
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
    }
    return dss_fs_join_path(a.c_str(), b.c_str(), out);
}

static std::string dss_txn_parent_dir(const std::string &path) {
    size_t i;
    for (i = path.size(); i > 0u; --i) {
        char c = path[i - 1u];
        if (c == '/' || c == '\\') {
            return path.substr(0u, i - 1u);
        }
    }
    return std::string();
}

static bool dss_txn_path_has_parent_ref(const std::string &path) {
    size_t i;
    if (path.empty()) {
        return false;
    }
    if (dss_fs_is_abs_path(path)) {
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

void dss_txn_journal_clear(dss_txn_journal_t *journal) {
    if (!journal) {
        return;
    }
    journal->plan_digest64 = 0u;
    journal->stage_root.clear();
    journal->steps.clear();
}

dss_error_t dss_txn_journal_parse(const dss_u8 *data,
                                  dss_u32 size,
                                  dss_txn_journal_t *out_journal) {
    dsk_tlv_view_t view;
    dss_error_t st;
    dsk_status_t pst;
    dsk_u32 i;
    if (!out_journal) {
        return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    dss_txn_journal_clear(out_journal);
    pst = dsk_tlv_parse(data, size, &view);
    if (!dsk_error_is_ok(pst)) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    for (i = 0u; i < view.record_count; ++i) {
        const dsk_tlv_record_t &rec = view.records[i];
        if (rec.type == DSS_TLV_TAG_TXN_PLAN_DIGEST64) {
            dss_u64 val = 0u;
            st = dss_parse_u64(rec, &val);
            if (dss_error_is_ok(st)) {
                out_journal->plan_digest64 = val;
            }
        } else if (rec.type == DSS_TLV_TAG_TXN_STAGE_ROOT) {
            st = dss_parse_string(rec, &out_journal->stage_root);
        } else if (rec.type == DSS_TLV_TAG_TXN_STEPS) {
            dsk_tlv_stream_t list_stream;
            dsk_status_t lst = dsk_tlv_parse_stream(rec.payload, rec.length, &list_stream);
            dsk_u32 j;
            if (!dsk_error_is_ok(lst)) {
                dsk_tlv_view_destroy(&view);
                return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
            }
            for (j = 0u; j < list_stream.record_count; ++j) {
                const dsk_tlv_record_t &entry = list_stream.records[j];
                if (entry.type != DSS_TLV_TAG_TXN_STEP_ENTRY) {
                    continue;
                }
                dsk_tlv_stream_t step_stream;
                dsk_status_t sst = dsk_tlv_parse_stream(entry.payload, entry.length, &step_stream);
                dss_txn_step_t step;
                dsk_u32 k;
                if (!dsk_error_is_ok(sst)) {
                    dsk_tlv_stream_destroy(&list_stream);
                    dsk_tlv_view_destroy(&view);
                    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
                }
                step.step_id = 0u;
                step.op_kind = 0u;
                step.rollback_kind = 0u;
                for (k = 0u; k < step_stream.record_count; ++k) {
                    const dsk_tlv_record_t &field = step_stream.records[k];
                    if (field.type == DSS_TLV_TAG_TXN_STEP_ID) {
                        dss_u32 val = 0u;
                        st = dss_parse_u32(field, &val);
                        if (dss_error_is_ok(st)) step.step_id = val;
                    } else if (field.type == DSS_TLV_TAG_TXN_STEP_KIND) {
                        dss_u16 val = 0u;
                        st = dss_parse_u16(field, &val);
                        if (dss_error_is_ok(st)) step.op_kind = val;
                    } else if (field.type == DSS_TLV_TAG_TXN_STEP_SRC) {
                        st = dss_parse_string(field, &step.src_path);
                    } else if (field.type == DSS_TLV_TAG_TXN_STEP_DST) {
                        st = dss_parse_string(field, &step.dst_path);
                    } else if (field.type == DSS_TLV_TAG_TXN_STEP_ROLLBACK_KIND) {
                        dss_u16 val = 0u;
                        st = dss_parse_u16(field, &val);
                        if (dss_error_is_ok(st)) step.rollback_kind = val;
                    } else if (field.type == DSS_TLV_TAG_TXN_STEP_ROLLBACK_SRC) {
                        st = dss_parse_string(field, &step.rollback_src);
                    } else if (field.type == DSS_TLV_TAG_TXN_STEP_ROLLBACK_DST) {
                        st = dss_parse_string(field, &step.rollback_dst);
                    } else {
                        continue;
                    }
                    if (!dss_error_is_ok(st)) {
                        dsk_tlv_stream_destroy(&step_stream);
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_view_destroy(&view);
                        return st;
                    }
                }
                dsk_tlv_stream_destroy(&step_stream);
                out_journal->steps.push_back(step);
            }
            dsk_tlv_stream_destroy(&list_stream);
            st = dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
        } else {
            continue;
        }
        if (!dss_error_is_ok(st)) {
            dsk_tlv_view_destroy(&view);
            return st;
        }
    }
    dsk_tlv_view_destroy(&view);
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

dss_error_t dss_txn_journal_write(const dss_txn_journal_t *journal,
                                  dsk_tlv_buffer_t *out_buf) {
    dsk_tlv_builder_t *builder;
    dsk_status_t st;
    dsk_u32 i;

    if (!journal || !out_buf) {
        return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    builder = dsk_tlv_builder_create();
    if (!builder) {
        return dss_txn_error(DSS_CODE_INTERNAL, DSS_SUBCODE_NONE);
    }
    dsk_tlv_builder_add_u64(builder, DSS_TLV_TAG_TXN_PLAN_DIGEST64, journal->plan_digest64);
    if (!journal->stage_root.empty()) {
        dsk_tlv_builder_add_string(builder, DSS_TLV_TAG_TXN_STAGE_ROOT, journal->stage_root.c_str());
    }

    if (!journal->steps.empty()) {
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;
        for (i = 0u; i < journal->steps.size(); ++i) {
            const dss_txn_step_t &step = journal->steps[i];
            dsk_tlv_builder_t *entry_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t entry_payload;
            dsk_tlv_builder_add_u32(entry_builder, DSS_TLV_TAG_TXN_STEP_ID, step.step_id);
            dsk_tlv_builder_add_u16(entry_builder, DSS_TLV_TAG_TXN_STEP_KIND, step.op_kind);
            if (!step.src_path.empty()) {
                dsk_tlv_builder_add_string(entry_builder, DSS_TLV_TAG_TXN_STEP_SRC, step.src_path.c_str());
            }
            if (!step.dst_path.empty()) {
                dsk_tlv_builder_add_string(entry_builder, DSS_TLV_TAG_TXN_STEP_DST, step.dst_path.c_str());
            }
            dsk_tlv_builder_add_u16(entry_builder, DSS_TLV_TAG_TXN_STEP_ROLLBACK_KIND, step.rollback_kind);
            if (!step.rollback_src.empty()) {
                dsk_tlv_builder_add_string(entry_builder,
                                           DSS_TLV_TAG_TXN_STEP_ROLLBACK_SRC,
                                           step.rollback_src.c_str());
            }
            if (!step.rollback_dst.empty()) {
                dsk_tlv_builder_add_string(entry_builder,
                                           DSS_TLV_TAG_TXN_STEP_ROLLBACK_DST,
                                           step.rollback_dst.c_str());
            }
            st = dsk_tlv_builder_finalize_payload(entry_builder, &entry_payload);
            dsk_tlv_builder_destroy(entry_builder);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(list_builder);
                dsk_tlv_builder_destroy(builder);
                return dss_txn_error(DSS_CODE_INTERNAL, DSS_SUBCODE_NONE);
            }
            dsk_tlv_builder_add_container(list_builder,
                                          DSS_TLV_TAG_TXN_STEP_ENTRY,
                                          entry_payload.data,
                                          entry_payload.size);
            dsk_tlv_buffer_free(&entry_payload);
        }
        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) {
            dsk_tlv_builder_destroy(builder);
            return dss_txn_error(DSS_CODE_INTERNAL, DSS_SUBCODE_NONE);
        }
        dsk_tlv_builder_add_container(builder,
                                      DSS_TLV_TAG_TXN_STEPS,
                                      list_payload.data,
                                      list_payload.size);
        dsk_tlv_buffer_free(&list_payload);
    }

    st = dsk_tlv_builder_finalize(builder, out_buf);
    dsk_tlv_builder_destroy(builder);
    if (!dsk_error_is_ok(st)) {
        return dss_txn_error(DSS_CODE_INTERNAL, DSS_SUBCODE_NONE);
    }
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static bool dss_file_op_less(const dsk_plan_file_op_t &a,
                             const dsk_plan_file_op_t &b) {
    if (a.target_root_id != b.target_root_id) {
        return a.target_root_id < b.target_root_id;
    }
    if (a.to_path != b.to_path) {
        return a.to_path < b.to_path;
    }
    if (a.from_path != b.from_path) {
        return a.from_path < b.from_path;
    }
    return a.op_kind < b.op_kind;
}

dss_error_t dss_txn_build(const dsk_plan_t *plan,
                          const std::vector<std::string> &install_roots,
                          const std::string &stage_root,
                          dss_bool supports_atomic_swap,
                          dss_txn_journal_t *out_journal) {
    dss_u32 step_id = 0u;
    dss_u32 i;
    if (!plan || !out_journal) {
        return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    dss_txn_journal_clear(out_journal);
    out_journal->plan_digest64 = plan->plan_digest64;
    out_journal->stage_root = stage_root;

    if (supports_atomic_swap) {
        for (i = 0u; i < (dss_u32)install_roots.size(); ++i) {
            dss_txn_step_t step;
            std::string root_dir = dss_txn_root_dir(i);
            std::string src;
            dss_txn_join(stage_root, root_dir, &src);
            step.step_id = ++step_id;
            step.op_kind = DSS_TXN_STEP_DIR_SWAP;
            step.src_path = src;
            step.dst_path = install_roots[i];
            step.rollback_kind = DSS_TXN_STEP_DIR_SWAP;
            step.rollback_src = step.src_path;
            step.rollback_dst = step.dst_path;
            out_journal->steps.push_back(step);
        }
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
    }

    {
        std::vector<dsk_plan_file_op_t> ops = plan->file_ops;
        std::sort(ops.begin(), ops.end(), dss_file_op_less);
        for (i = 0u; i < ops.size(); ++i) {
            const dsk_plan_file_op_t &op = ops[i];
            if (op.target_root_id >= install_roots.size()) {
                return dss_txn_error(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
            }
            if (dss_txn_path_has_parent_ref(op.to_path)) {
                return dss_txn_error(DSS_CODE_SANDBOX_VIOLATION, DSS_SUBCODE_PATH_TRAVERSAL);
            }
            if (op.op_kind == DSK_PLAN_FILE_OP_EXTRACT) {
                return dss_txn_error(DSS_CODE_NOT_SUPPORTED, DSS_SUBCODE_NONE);
            }

            std::string root_dir = dss_txn_root_dir(op.target_root_id);
            std::string stage_root_dir;
            std::string stage_path;
            std::string dest_path;
            dss_txn_join(stage_root, root_dir, &stage_root_dir);
            dss_txn_join(stage_root_dir, op.to_path, &stage_path);
            dss_txn_join(install_roots[op.target_root_id], op.to_path, &dest_path);

            if (op.op_kind == DSK_PLAN_FILE_OP_MKDIR) {
                dss_txn_step_t step;
                step.step_id = ++step_id;
                step.op_kind = DSS_TXN_STEP_MKDIR;
                step.src_path.clear();
                step.dst_path = dest_path;
                step.rollback_kind = DSS_TXN_STEP_REMOVE_DIR;
                step.rollback_src.clear();
                step.rollback_dst = dest_path;
                out_journal->steps.push_back(step);
                continue;
            }

            if (op.op_kind == DSK_PLAN_FILE_OP_REMOVE) {
                dss_txn_step_t step;
                step.step_id = ++step_id;
                step.op_kind = DSS_TXN_STEP_DELETE_FILE;
                step.src_path.clear();
                step.dst_path = dest_path;
                step.rollback_kind = DSS_TXN_STEP_DELETE_FILE;
                step.rollback_src.clear();
                step.rollback_dst.clear();
                out_journal->steps.push_back(step);
                continue;
            }

            if (op.op_kind != DSK_PLAN_FILE_OP_COPY) {
                return dss_txn_error(DSS_CODE_NOT_SUPPORTED, DSS_SUBCODE_NONE);
            }

            {
                std::string parent = dss_txn_parent_dir(dest_path);
                if (!parent.empty()) {
                    dss_txn_step_t mk;
                    mk.step_id = ++step_id;
                    mk.op_kind = DSS_TXN_STEP_MKDIR;
                    mk.src_path.clear();
                    mk.dst_path = parent;
                    mk.rollback_kind = DSS_TXN_STEP_REMOVE_DIR;
                    mk.rollback_src.clear();
                    mk.rollback_dst = parent;
                    out_journal->steps.push_back(mk);
                }
            }

            {
                dss_txn_step_t backup;
                backup.step_id = ++step_id;
                backup.op_kind = DSS_TXN_STEP_ATOMIC_RENAME;
                backup.src_path = dest_path;
                backup.dst_path = dest_path + ".dsk_bak";
                backup.rollback_kind = DSS_TXN_STEP_ATOMIC_RENAME;
                backup.rollback_src = backup.dst_path;
                backup.rollback_dst = backup.src_path;
                out_journal->steps.push_back(backup);
            }

            {
                dss_txn_step_t copy;
                copy.step_id = ++step_id;
                copy.op_kind = DSS_TXN_STEP_COPY_FILE;
                copy.src_path = stage_path;
                copy.dst_path = dest_path;
                copy.rollback_kind = DSS_TXN_STEP_DELETE_FILE;
                copy.rollback_src.clear();
                copy.rollback_dst = dest_path;
                out_journal->steps.push_back(copy);
            }
        }
    }

    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}
