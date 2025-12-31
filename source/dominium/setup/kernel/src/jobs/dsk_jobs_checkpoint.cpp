#include "dsk_jobs_internal.h"

#include "dsk/dsk_contracts.h"

#include "dominium/core_audit.h"

#include <algorithm>

static dsk_status_t dsk_jobs_error(dsk_u16 code, dsk_u16 subcode) {
    return dsk_error_make(DSK_DOMAIN_KERNEL, code, subcode, DSK_ERROR_FLAG_USER_ACTIONABLE);
}

static dsk_status_t dsk_parse_u16(const dsk_tlv_record_t &rec, dsk_u16 *out) {
    if (!out) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length != 2u) {
        return dsk_jobs_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }
    *out = (dsk_u16)rec.payload[0] | (dsk_u16)((dsk_u16)rec.payload[1] << 8);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_parse_u32(const dsk_tlv_record_t &rec, dsk_u32 *out) {
    if (!out) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length != 4u) {
        return dsk_jobs_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }
    *out = (dsk_u32)rec.payload[0]
         | ((dsk_u32)rec.payload[1] << 8)
         | ((dsk_u32)rec.payload[2] << 16)
         | ((dsk_u32)rec.payload[3] << 24);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_parse_u64(const dsk_tlv_record_t &rec, dsk_u64 *out) {
    if (!out) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length != 8u) {
        return dsk_jobs_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }
    *out = (dsk_u64)rec.payload[0]
         | ((dsk_u64)rec.payload[1] << 8)
         | ((dsk_u64)rec.payload[2] << 16)
         | ((dsk_u64)rec.payload[3] << 24)
         | ((dsk_u64)rec.payload[4] << 32)
         | ((dsk_u64)rec.payload[5] << 40)
         | ((dsk_u64)rec.payload[6] << 48)
         | ((dsk_u64)rec.payload[7] << 56);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_parse_string(const dsk_tlv_record_t &rec, std::string *out) {
    if (!out) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    out->assign(reinterpret_cast<const char *>(rec.payload), rec.length);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_jobs_add_err_details(dsk_tlv_builder_t *builder,
                                             dsk_u16 entry_tag,
                                             const err_t &err) {
    dom::core_audit::ErrDetailTags tags;
    dom::core_tlv::TlvWriter detail_bytes;
    dom::core_tlv::TlvRecord rec;
    dsk_status_t st;
    const std::vector<unsigned char> &bytes = detail_bytes.bytes();

    if (!builder) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    tags.tag_key = DSK_TLV_TAG_ERR_DETAIL_KEY;
    tags.tag_type = DSK_TLV_TAG_ERR_DETAIL_TYPE;
    tags.tag_value_u32 = DSK_TLV_TAG_ERR_DETAIL_VALUE_U32;
    tags.tag_value_u64 = DSK_TLV_TAG_ERR_DETAIL_VALUE_U64;
    dom::core_audit::append_err_details(detail_bytes,
                                        (u32)entry_tag,
                                        err,
                                        tags);
    if (bytes.empty()) {
        return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    }
    dom::core_tlv::TlvReader reader(&bytes[0], bytes.size());
    while (reader.next(rec)) {
        st = dsk_tlv_builder_add_container(builder,
                                           (dsk_u16)rec.tag,
                                           rec.payload,
                                           rec.len);
        if (!dsk_error_is_ok(st)) {
            return st;
        }
    }
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

void dsk_job_journal_clear(dsk_job_journal_t *journal) {
    if (!journal) {
        return;
    }
    journal->run_id = 0u;
    journal->plan_digest64 = 0u;
    journal->selected_splat_id.clear();
    journal->stage_root.clear();
    journal->rollback_ref.clear();
    journal->last_error = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    journal->plan_bytes.clear();
    journal->checkpoints.clear();
}

dsk_status_t dsk_job_journal_parse(const dsk_u8 *data,
                                   dsk_u32 size,
                                   dsk_job_journal_t *out_journal) {
    dsk_tlv_view_t view;
    dsk_status_t st;
    dsk_u32 i;
    if (!out_journal) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    dsk_job_journal_clear(out_journal);
    st = dsk_tlv_parse(data, size, &view);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    for (i = 0u; i < view.record_count; ++i) {
        const dsk_tlv_record_t &rec = view.records[i];
        if (rec.type == DSK_TLV_TAG_JOB_RUN_ID) {
            st = dsk_parse_u64(rec, &out_journal->run_id);
        } else if (rec.type == DSK_TLV_TAG_JOB_PLAN_DIGEST64) {
            st = dsk_parse_u64(rec, &out_journal->plan_digest64);
        } else if (rec.type == DSK_TLV_TAG_JOB_SELECTED_SPLAT_ID) {
            st = dsk_parse_string(rec, &out_journal->selected_splat_id);
        } else if (rec.type == DSK_TLV_TAG_JOB_STAGE_ROOT) {
            st = dsk_parse_string(rec, &out_journal->stage_root);
        } else if (rec.type == DSK_TLV_TAG_JOB_ROLLBACK_REF) {
            st = dsk_parse_string(rec, &out_journal->rollback_ref);
        } else if (rec.type == DSK_TLV_TAG_JOB_PLAN_BYTES) {
            out_journal->plan_bytes.assign(rec.payload, rec.payload + rec.length);
            st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        } else if (rec.type == DSK_TLV_TAG_JOB_LAST_ERROR) {
            dsk_tlv_stream_t err_stream;
            dsk_status_t lst = dsk_tlv_parse_stream(rec.payload, rec.length, &err_stream);
            dsk_u32 j;
            dsk_u16 subcode = 0u;
            dsk_bool saw_msg_id = DSK_FALSE;
            if (!dsk_error_is_ok(lst)) {
                dsk_tlv_view_destroy(&view);
                return lst;
            }
            out_journal->last_error = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
            out_journal->last_error.detail_count = 0u;
            for (j = 0u; j < err_stream.record_count; ++j) {
                const dsk_tlv_record_t &field = err_stream.records[j];
                if (field.type == DSK_TLV_TAG_JOB_ERR_DOMAIN) {
                    dsk_u16 v;
                    lst = dsk_parse_u16(field, &v);
                    if (dsk_error_is_ok(lst)) out_journal->last_error.domain = v;
                } else if (field.type == DSK_TLV_TAG_JOB_ERR_CODE) {
                    dsk_u16 v;
                    lst = dsk_parse_u16(field, &v);
                    if (dsk_error_is_ok(lst)) out_journal->last_error.code = v;
                } else if (field.type == DSK_TLV_TAG_JOB_ERR_SUBCODE) {
                    dsk_u16 v;
                    lst = dsk_parse_u16(field, &v);
                    if (dsk_error_is_ok(lst)) subcode = v;
                } else if (field.type == DSK_TLV_TAG_JOB_ERR_FLAGS) {
                    dsk_u16 v;
                    lst = dsk_parse_u16(field, &v);
                    if (dsk_error_is_ok(lst)) out_journal->last_error.flags = v;
                } else if (field.type == DSK_TLV_TAG_JOB_ERR_MSG_ID) {
                    dsk_u32 v;
                    lst = dsk_parse_u32(field, &v);
                    if (dsk_error_is_ok(lst)) {
                        out_journal->last_error.msg_id = v;
                        saw_msg_id = DSK_TRUE;
                    }
                } else if (field.type == DSK_TLV_TAG_JOB_ERR_DETAIL) {
                    dom::core_audit::ErrDetailTags tags;
                    tags.tag_key = DSK_TLV_TAG_ERR_DETAIL_KEY;
                    tags.tag_type = DSK_TLV_TAG_ERR_DETAIL_TYPE;
                    tags.tag_value_u32 = DSK_TLV_TAG_ERR_DETAIL_VALUE_U32;
                    tags.tag_value_u64 = DSK_TLV_TAG_ERR_DETAIL_VALUE_U64;
                    (void)dom::core_audit::parse_err_detail_entry(field.payload,
                                                                  (size_t)field.length,
                                                                  out_journal->last_error,
                                                                  tags);
                } else {
                    continue;
                }
                if (!dsk_error_is_ok(lst)) {
                    dsk_tlv_stream_destroy(&err_stream);
                    dsk_tlv_view_destroy(&view);
                    return lst;
                }
            }
            dsk_tlv_stream_destroy(&err_stream);
            if (subcode != 0u &&
                dom::core_audit::err_subcode(out_journal->last_error) == 0u) {
                (void)err_add_detail_u32(&out_journal->last_error,
                                         (u32)ERR_DETAIL_KEY_SUBCODE,
                                         (u32)subcode);
            }
            if (!saw_msg_id && out_journal->last_error.code != 0u) {
                err_t base = dsk_error_make(out_journal->last_error.domain,
                                            out_journal->last_error.code,
                                            subcode,
                                            (dsk_u16)out_journal->last_error.flags);
                out_journal->last_error.msg_id = base.msg_id;
            }
            st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        } else if (rec.type == DSK_TLV_TAG_JOB_CHECKPOINTS) {
            dsk_tlv_stream_t list_stream;
            dsk_status_t lst = dsk_tlv_parse_stream(rec.payload, rec.length, &list_stream);
            dsk_u32 j;
            if (!dsk_error_is_ok(lst)) {
                dsk_tlv_view_destroy(&view);
                return lst;
            }
            for (j = 0u; j < list_stream.record_count; ++j) {
                const dsk_tlv_record_t &entry = list_stream.records[j];
                if (entry.type != DSK_TLV_TAG_JOB_CHECKPOINT_ENTRY) {
                    continue;
                }
                dsk_tlv_stream_t cp_stream;
                dsk_status_t cst = dsk_tlv_parse_stream(entry.payload, entry.length, &cp_stream);
                dsk_job_checkpoint_t cp;
                dsk_u32 k;
                if (!dsk_error_is_ok(cst)) {
                    dsk_tlv_stream_destroy(&list_stream);
                    dsk_tlv_view_destroy(&view);
                    return cst;
                }
                cp.job_id = 0u;
                cp.status = 0u;
                cp.last_completed_step = 0u;
                for (k = 0u; k < cp_stream.record_count; ++k) {
                    const dsk_tlv_record_t &field = cp_stream.records[k];
                    if (field.type == DSK_TLV_TAG_JOB_CHECKPOINT_ID) {
                        cst = dsk_parse_u32(field, &cp.job_id);
                    } else if (field.type == DSK_TLV_TAG_JOB_CHECKPOINT_STATUS) {
                        dsk_u16 v;
                        cst = dsk_parse_u16(field, &v);
                        if (dsk_error_is_ok(cst)) cp.status = v;
                    } else if (field.type == DSK_TLV_TAG_JOB_CHECKPOINT_LAST_STEP) {
                        cst = dsk_parse_u32(field, &cp.last_completed_step);
                    } else {
                        continue;
                    }
                    if (!dsk_error_is_ok(cst)) {
                        dsk_tlv_stream_destroy(&cp_stream);
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_view_destroy(&view);
                        return cst;
                    }
                }
                dsk_tlv_stream_destroy(&cp_stream);
                out_journal->checkpoints.push_back(cp);
            }
            dsk_tlv_stream_destroy(&list_stream);
            st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        } else {
            continue;
        }
        if (!dsk_error_is_ok(st)) {
            dsk_tlv_view_destroy(&view);
            return st;
        }
    }
    dsk_tlv_view_destroy(&view);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static bool dsk_checkpoint_less(const dsk_job_checkpoint_t &a,
                                const dsk_job_checkpoint_t &b) {
    return a.job_id < b.job_id;
}

dsk_status_t dsk_job_journal_write(const dsk_job_journal_t *journal,
                                   dsk_tlv_buffer_t *out_buf) {
    dsk_tlv_builder_t *builder;
    dsk_status_t st;
    dsk_u32 i;
    std::vector<dsk_job_checkpoint_t> checkpoints;
    if (!journal || !out_buf) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    builder = dsk_tlv_builder_create();
    if (!builder) {
        return dsk_jobs_error(DSK_CODE_INTERNAL_ERROR, DSK_SUBCODE_NONE);
    }
    dsk_tlv_builder_add_u64(builder, DSK_TLV_TAG_JOB_RUN_ID, journal->run_id);
    dsk_tlv_builder_add_u64(builder, DSK_TLV_TAG_JOB_PLAN_DIGEST64, journal->plan_digest64);
    dsk_tlv_builder_add_string(builder,
                               DSK_TLV_TAG_JOB_SELECTED_SPLAT_ID,
                               journal->selected_splat_id.c_str());
    if (!journal->stage_root.empty()) {
        dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_JOB_STAGE_ROOT, journal->stage_root.c_str());
    }
    if (!journal->rollback_ref.empty()) {
        dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_JOB_ROLLBACK_REF, journal->rollback_ref.c_str());
    }
    if (!journal->plan_bytes.empty()) {
        dsk_tlv_builder_add_bytes(builder,
                                  DSK_TLV_TAG_JOB_PLAN_BYTES,
                                  &journal->plan_bytes[0],
                                  (dsk_u32)journal->plan_bytes.size());
    }

    if (!dsk_error_is_ok(journal->last_error)) {
        dsk_tlv_builder_t *err_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t err_payload;
        dsk_u32 subcode = dom::core_audit::err_subcode(journal->last_error);
        dsk_tlv_builder_add_u16(err_builder, DSK_TLV_TAG_JOB_ERR_DOMAIN, journal->last_error.domain);
        dsk_tlv_builder_add_u16(err_builder, DSK_TLV_TAG_JOB_ERR_CODE, journal->last_error.code);
        dsk_tlv_builder_add_u16(err_builder, DSK_TLV_TAG_JOB_ERR_SUBCODE, (dsk_u16)subcode);
        dsk_tlv_builder_add_u16(err_builder, DSK_TLV_TAG_JOB_ERR_FLAGS, (dsk_u16)journal->last_error.flags);
        dsk_tlv_builder_add_u32(err_builder, DSK_TLV_TAG_JOB_ERR_MSG_ID, journal->last_error.msg_id);
        st = dsk_jobs_add_err_details(err_builder, DSK_TLV_TAG_JOB_ERR_DETAIL, journal->last_error);
        if (!dsk_error_is_ok(st)) {
            dsk_tlv_builder_destroy(err_builder);
            dsk_tlv_builder_destroy(builder);
            return st;
        }
        st = dsk_tlv_builder_finalize_payload(err_builder, &err_payload);
        dsk_tlv_builder_destroy(err_builder);
        if (!dsk_error_is_ok(st)) {
            dsk_tlv_builder_destroy(builder);
            return st;
        }
        dsk_tlv_builder_add_container(builder,
                                      DSK_TLV_TAG_JOB_LAST_ERROR,
                                      err_payload.data,
                                      err_payload.size);
        dsk_tlv_buffer_free(&err_payload);
    }

    checkpoints = journal->checkpoints;
    std::sort(checkpoints.begin(), checkpoints.end(), dsk_checkpoint_less);
    if (!checkpoints.empty()) {
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;
        for (i = 0u; i < checkpoints.size(); ++i) {
            const dsk_job_checkpoint_t &cp = checkpoints[i];
            dsk_tlv_builder_t *entry_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t entry_payload;
            dsk_tlv_builder_add_u32(entry_builder, DSK_TLV_TAG_JOB_CHECKPOINT_ID, cp.job_id);
            dsk_tlv_builder_add_u16(entry_builder, DSK_TLV_TAG_JOB_CHECKPOINT_STATUS, cp.status);
            dsk_tlv_builder_add_u32(entry_builder, DSK_TLV_TAG_JOB_CHECKPOINT_LAST_STEP, cp.last_completed_step);
            st = dsk_tlv_builder_finalize_payload(entry_builder, &entry_payload);
            dsk_tlv_builder_destroy(entry_builder);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(list_builder);
                dsk_tlv_builder_destroy(builder);
                return st;
            }
            dsk_tlv_builder_add_container(list_builder,
                                          DSK_TLV_TAG_JOB_CHECKPOINT_ENTRY,
                                          entry_payload.data,
                                          entry_payload.size);
            dsk_tlv_buffer_free(&entry_payload);
        }
        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) {
            dsk_tlv_builder_destroy(builder);
            return st;
        }
        dsk_tlv_builder_add_container(builder,
                                      DSK_TLV_TAG_JOB_CHECKPOINTS,
                                      list_payload.data,
                                      list_payload.size);
        dsk_tlv_buffer_free(&list_payload);
    }

    st = dsk_tlv_builder_finalize(builder, out_buf);
    dsk_tlv_builder_destroy(builder);
    return st;
}

dsk_status_t dsk_job_journal_load(const dss_fs_api_t *fs,
                                  const char *path,
                                  dsk_job_journal_t *out_journal) {
    std::vector<dsk_u8> bytes;
    dss_error_t st;
    if (!fs || !fs->read_file_bytes || !path || !out_journal) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    st = fs->read_file_bytes(fs->ctx, path, &bytes);
    if (!dss_error_is_ok(st)) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_IO_ERROR, DSK_SUBCODE_NONE, 0u);
    }
    return dsk_job_journal_parse(bytes.empty() ? 0 : &bytes[0],
                                 (dsk_u32)bytes.size(),
                                 out_journal);
}

dsk_status_t dsk_job_journal_store(const dss_fs_api_t *fs,
                                   const char *path,
                                   const dsk_job_journal_t *journal) {
    dsk_tlv_buffer_t buf;
    dsk_status_t st;
    if (!fs || !fs->write_file_bytes_atomic || !path || !journal) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    st = dsk_job_journal_write(journal, &buf);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    {
        dss_error_t wr = fs->write_file_bytes_atomic(fs->ctx,
                                                     path,
                                                     buf.data,
                                                     buf.size);
        dsk_tlv_buffer_free(&buf);
        if (!dss_error_is_ok(wr)) {
            return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_IO_ERROR, DSK_SUBCODE_NONE, 0u);
        }
    }
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

dsk_status_t dsk_write_audit_file(const dss_fs_api_t *fs,
                                  const char *path,
                                  const dsk_audit_t *audit) {
    dsk_tlv_buffer_t buf;
    dsk_status_t st;
    if (!fs || !fs->write_file_bytes_atomic || !path || !audit) {
        return dsk_jobs_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    st = dsk_audit_write(audit, &buf);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    {
        dss_error_t wr = fs->write_file_bytes_atomic(fs->ctx,
                                                     path,
                                                     buf.data,
                                                     buf.size);
        dsk_tlv_buffer_free(&buf);
        if (!dss_error_is_ok(wr)) {
            return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_IO_ERROR, DSK_SUBCODE_NONE, 0u);
        }
    }
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}
