#include "dsk/dsk_audit.h"
#include "dsk/dsk_contracts.h"

#include "dominium/core_audit.h"

#include <algorithm>

static dsk_status_t dsk_audit_error(dsk_u16 code, dsk_u16 subcode) {
    return dsk_error_make(DSK_DOMAIN_KERNEL, code, subcode, DSK_ERROR_FLAG_USER_ACTIONABLE);
}

static dsk_status_t dsk_parse_u16(const dsk_tlv_record_t &rec, dsk_u16 *out) {
    if (!out) {
        return dsk_audit_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length != 2u) {
        return dsk_audit_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }
    *out = (dsk_u16)rec.payload[0] | (dsk_u16)((dsk_u16)rec.payload[1] << 8);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_parse_u32(const dsk_tlv_record_t &rec, dsk_u32 *out) {
    if (!out) {
        return dsk_audit_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length != 4u) {
        return dsk_audit_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
    }
    *out = (dsk_u32)rec.payload[0]
         | ((dsk_u32)rec.payload[1] << 8)
         | ((dsk_u32)rec.payload[2] << 16)
         | ((dsk_u32)rec.payload[3] << 24);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_parse_u64(const dsk_tlv_record_t &rec, dsk_u64 *out) {
    if (!out) {
        return dsk_audit_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    if (rec.length != 8u) {
        return dsk_audit_error(DSK_CODE_PARSE_ERROR, DSK_SUBCODE_INVALID_FIELD);
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
        return dsk_audit_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    out->assign(reinterpret_cast<const char *>(rec.payload), rec.length);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static dsk_status_t dsk_add_err_details(dsk_tlv_builder_t *builder,
                                        dsk_u16 entry_tag,
                                        const err_t &err) {
    dom::core_audit::ErrDetailTags tags;
    dom::core_tlv::TlvWriter detail_bytes;
    dom::core_tlv::TlvRecord rec;
    dsk_status_t st;
    const std::vector<unsigned char> &bytes = detail_bytes.bytes();

    if (!builder) {
        return dsk_audit_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
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

dsk_status_t dsk_audit_parse(const dsk_u8 *data, dsk_u32 size, dsk_audit_t *out_audit) {
    dsk_tlv_view_t view;
    dsk_status_t st;
    dsk_u32 i;

    if (!out_audit) {
        return dsk_audit_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }
    dsk_audit_clear(out_audit);

    st = dsk_tlv_parse(data, size, &view);
    if (!dsk_error_is_ok(st)) {
        return st;
    }

    for (i = 0u; i < view.record_count; ++i) {
        const dsk_tlv_record_t &rec = view.records[i];
        if (rec.type == DSK_TLV_TAG_AUDIT_RUN_ID) {
            st = dsk_parse_u64(rec, &out_audit->run_id);
        } else if (rec.type == DSK_TLV_TAG_AUDIT_MANIFEST_DIGEST64) {
            st = dsk_parse_u64(rec, &out_audit->manifest_digest64);
        } else if (rec.type == DSK_TLV_TAG_AUDIT_REQUEST_DIGEST64) {
            st = dsk_parse_u64(rec, &out_audit->request_digest64);
        } else if (rec.type == DSK_TLV_TAG_AUDIT_SPLAT_CAPS_DIGEST64) {
            st = dsk_parse_u64(rec, &out_audit->splat_caps_digest64);
        } else if (rec.type == DSK_TLV_TAG_AUDIT_RESOLVED_SET_DIGEST64) {
            st = dsk_parse_u64(rec, &out_audit->resolved_set_digest64);
        } else if (rec.type == DSK_TLV_TAG_AUDIT_PLAN_DIGEST64) {
            st = dsk_parse_u64(rec, &out_audit->plan_digest64);
        } else if (rec.type == DSK_TLV_TAG_AUDIT_SELECTED_SPLAT) {
            st = dsk_parse_string(rec, &out_audit->selected_splat);
        } else if (rec.type == DSK_TLV_TAG_AUDIT_FRONTEND_ID) {
            st = dsk_parse_string(rec, &out_audit->frontend_id);
        } else if (rec.type == DSK_TLV_TAG_AUDIT_PLATFORM_TRIPLE) {
            st = dsk_parse_string(rec, &out_audit->platform_triple);
        } else if (rec.type == DSK_TLV_TAG_AUDIT_OPERATION) {
            st = dsk_parse_u16(rec, &out_audit->operation);
        } else if (rec.type == DSK_TLV_TAG_AUDIT_REFUSALS) {
            dsk_tlv_stream_t list_stream;
            dsk_status_t lst;
            dsk_u32 j;
            lst = dsk_tlv_parse_stream(rec.payload, rec.length, &list_stream);
            if (!dsk_error_is_ok(lst)) {
                dsk_tlv_view_destroy(&view);
                return lst;
            }
            for (j = 0u; j < list_stream.record_count; ++j) {
                const dsk_tlv_record_t &entry = list_stream.records[j];
                if (entry.type != DSK_TLV_TAG_AUDIT_REFUSAL_ENTRY) {
                    continue;
                }
                dsk_tlv_stream_t ref_stream;
                dsk_audit_refusal_t refusal;
                dsk_u32 k;
                refusal.code = 0u;
                lst = dsk_tlv_parse_stream(entry.payload, entry.length, &ref_stream);
                if (!dsk_error_is_ok(lst)) {
                    dsk_tlv_stream_destroy(&list_stream);
                    dsk_tlv_view_destroy(&view);
                    return lst;
                }
                for (k = 0u; k < ref_stream.record_count; ++k) {
                    const dsk_tlv_record_t &rf = ref_stream.records[k];
                    if (rf.type == DSK_TLV_TAG_AUDIT_REFUSAL_CODE) {
                        dsk_u16 code;
                        lst = dsk_parse_u16(rf, &code);
                        if (dsk_error_is_ok(lst)) {
                            refusal.code = code;
                        }
                    } else if (rf.type == DSK_TLV_TAG_AUDIT_REFUSAL_DETAIL) {
                        lst = dsk_parse_string(rf, &refusal.detail);
                    } else {
                        continue;
                    }
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&ref_stream);
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_view_destroy(&view);
                        return lst;
                    }
                }
                dsk_tlv_stream_destroy(&ref_stream);
                out_audit->refusals.push_back(refusal);
            }
            dsk_tlv_stream_destroy(&list_stream);
            st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        } else if (rec.type == DSK_TLV_TAG_AUDIT_SELECTION_REASON) {
            dsk_tlv_stream_t sel_stream;
            dsk_status_t lst;
            dsk_u32 j;
            lst = dsk_tlv_parse_stream(rec.payload, rec.length, &sel_stream);
            if (!dsk_error_is_ok(lst)) {
                dsk_tlv_view_destroy(&view);
                return lst;
            }
            for (j = 0u; j < sel_stream.record_count; ++j) {
                const dsk_tlv_record_t &field = sel_stream.records[j];
                if (field.type == DSK_TLV_TAG_AUDIT_CANDIDATES) {
                    dsk_tlv_stream_t list_stream;
                    dsk_u32 k;
                    lst = dsk_tlv_parse_stream(field.payload, field.length, &list_stream);
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&sel_stream);
                        dsk_tlv_view_destroy(&view);
                        return lst;
                    }
                    for (k = 0u; k < list_stream.record_count; ++k) {
                        const dsk_tlv_record_t &entry = list_stream.records[k];
                        if (entry.type != DSK_TLV_TAG_AUDIT_CANDIDATE_ENTRY) {
                            continue;
                        }
                        dsk_tlv_stream_t cand_stream;
                        dsk_audit_selection_candidate_t cand;
                        dsk_u32 m;
                        cand.caps_digest64 = 0u;
                        lst = dsk_tlv_parse_stream(entry.payload, entry.length, &cand_stream);
                        if (!dsk_error_is_ok(lst)) {
                            dsk_tlv_stream_destroy(&list_stream);
                            dsk_tlv_stream_destroy(&sel_stream);
                            dsk_tlv_view_destroy(&view);
                            return lst;
                        }
                        for (m = 0u; m < cand_stream.record_count; ++m) {
                            const dsk_tlv_record_t &cf = cand_stream.records[m];
                            if (cf.type == DSK_TLV_TAG_AUDIT_CANDIDATE_ID) {
                                lst = dsk_parse_string(cf, &cand.id);
                            } else if (cf.type == DSK_TLV_TAG_AUDIT_CANDIDATE_CAPS_DIGEST64) {
                                lst = dsk_parse_u64(cf, &cand.caps_digest64);
                            } else {
                                continue;
                            }
                            if (!dsk_error_is_ok(lst)) {
                                dsk_tlv_stream_destroy(&cand_stream);
                                dsk_tlv_stream_destroy(&list_stream);
                                dsk_tlv_stream_destroy(&sel_stream);
                                dsk_tlv_view_destroy(&view);
                                return lst;
                            }
                        }
                        dsk_tlv_stream_destroy(&cand_stream);
                        if (!cand.id.empty()) {
                            out_audit->selection.candidates.push_back(cand);
                        }
                    }
                    dsk_tlv_stream_destroy(&list_stream);
                } else if (field.type == DSK_TLV_TAG_AUDIT_REJECTIONS) {
                    dsk_tlv_stream_t list_stream;
                    dsk_u32 k;
                    lst = dsk_tlv_parse_stream(field.payload, field.length, &list_stream);
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&sel_stream);
                        dsk_tlv_view_destroy(&view);
                        return lst;
                    }
                    for (k = 0u; k < list_stream.record_count; ++k) {
                        const dsk_tlv_record_t &entry = list_stream.records[k];
                        if (entry.type != DSK_TLV_TAG_AUDIT_REJECTION_ENTRY) {
                            continue;
                        }
                        dsk_tlv_stream_t rej_stream;
                        dsk_splat_rejection_t rej;
                        dsk_u32 m;
                        rej.code = 0u;
                        lst = dsk_tlv_parse_stream(entry.payload, entry.length, &rej_stream);
                        if (!dsk_error_is_ok(lst)) {
                            dsk_tlv_stream_destroy(&list_stream);
                            dsk_tlv_stream_destroy(&sel_stream);
                            dsk_tlv_view_destroy(&view);
                            return lst;
                        }
                        for (m = 0u; m < rej_stream.record_count; ++m) {
                            const dsk_tlv_record_t &rf = rej_stream.records[m];
                            if (rf.type == DSK_TLV_TAG_AUDIT_REJECTION_ID) {
                                lst = dsk_parse_string(rf, &rej.id);
                            } else if (rf.type == DSK_TLV_TAG_AUDIT_REJECTION_CODE) {
                                dsk_u16 code;
                                lst = dsk_parse_u16(rf, &code);
                                if (dsk_error_is_ok(lst)) {
                                    rej.code = code;
                                }
                            } else if (rf.type == DSK_TLV_TAG_AUDIT_REJECTION_DETAIL) {
                                lst = dsk_parse_string(rf, &rej.detail);
                            } else {
                                continue;
                            }
                            if (!dsk_error_is_ok(lst)) {
                                dsk_tlv_stream_destroy(&rej_stream);
                                dsk_tlv_stream_destroy(&list_stream);
                                dsk_tlv_stream_destroy(&sel_stream);
                                dsk_tlv_view_destroy(&view);
                                return lst;
                            }
                        }
                        dsk_tlv_stream_destroy(&rej_stream);
                        if (!rej.id.empty()) {
                            out_audit->selection.rejections.push_back(rej);
                        }
                    }
                    dsk_tlv_stream_destroy(&list_stream);
                } else if (field.type == DSK_TLV_TAG_AUDIT_SELECTED_ID) {
                    lst = dsk_parse_string(field, &out_audit->selection.selected_id);
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&sel_stream);
                        dsk_tlv_view_destroy(&view);
                        return lst;
                    }
                } else if (field.type == DSK_TLV_TAG_AUDIT_SELECTED_REASON) {
                    dsk_u16 reason;
                    lst = dsk_parse_u16(field, &reason);
                    if (dsk_error_is_ok(lst)) {
                        out_audit->selection.selected_reason = reason;
                    } else {
                        dsk_tlv_stream_destroy(&sel_stream);
                        dsk_tlv_view_destroy(&view);
                        return lst;
                    }
                }
            }
            dsk_tlv_stream_destroy(&sel_stream);
            st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        } else if (rec.type == DSK_TLV_TAG_AUDIT_RESULT) {
            dsk_tlv_stream_t res_stream;
            dsk_status_t lst;
            dsk_u32 j;
            dsk_u16 subcode = 0u;
            dsk_bool saw_msg_id = DSK_FALSE;
            lst = dsk_tlv_parse_stream(rec.payload, rec.length, &res_stream);
            if (!dsk_error_is_ok(lst)) {
                dsk_tlv_view_destroy(&view);
                return lst;
            }
            out_audit->result = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
            out_audit->result.detail_count = 0u;
            for (j = 0u; j < res_stream.record_count; ++j) {
                const dsk_tlv_record_t &field = res_stream.records[j];
                if (field.type == DSK_TLV_TAG_RESULT_DOMAIN) {
                    dsk_u16 v;
                    lst = dsk_parse_u16(field, &v);
                    if (dsk_error_is_ok(lst)) out_audit->result.domain = v;
                } else if (field.type == DSK_TLV_TAG_RESULT_CODE) {
                    dsk_u16 v;
                    lst = dsk_parse_u16(field, &v);
                    if (dsk_error_is_ok(lst)) out_audit->result.code = v;
                } else if (field.type == DSK_TLV_TAG_RESULT_SUBCODE) {
                    dsk_u16 v;
                    lst = dsk_parse_u16(field, &v);
                    if (dsk_error_is_ok(lst)) subcode = v;
                } else if (field.type == DSK_TLV_TAG_RESULT_FLAGS) {
                    dsk_u16 v;
                    lst = dsk_parse_u16(field, &v);
                    if (dsk_error_is_ok(lst)) out_audit->result.flags = v;
                } else if (field.type == DSK_TLV_TAG_RESULT_MSG_ID) {
                    dsk_u32 v;
                    lst = dsk_parse_u32(field, &v);
                    if (dsk_error_is_ok(lst)) {
                        out_audit->result.msg_id = v;
                        saw_msg_id = DSK_TRUE;
                    }
                } else if (field.type == DSK_TLV_TAG_RESULT_ERR_DETAIL) {
                    dom::core_audit::ErrDetailTags tags;
                    tags.tag_key = DSK_TLV_TAG_ERR_DETAIL_KEY;
                    tags.tag_type = DSK_TLV_TAG_ERR_DETAIL_TYPE;
                    tags.tag_value_u32 = DSK_TLV_TAG_ERR_DETAIL_VALUE_U32;
                    tags.tag_value_u64 = DSK_TLV_TAG_ERR_DETAIL_VALUE_U64;
                    (void)dom::core_audit::parse_err_detail_entry(field.payload,
                                                                  (size_t)field.length,
                                                                  out_audit->result,
                                                                  tags);
                } else {
                    continue;
                }
                if (!dsk_error_is_ok(lst)) {
                    dsk_tlv_stream_destroy(&res_stream);
                    dsk_tlv_view_destroy(&view);
                    return lst;
                }
            }
            dsk_tlv_stream_destroy(&res_stream);
            if (subcode != 0u &&
                dom::core_audit::err_subcode(out_audit->result) == 0u) {
                (void)err_add_detail_u32(&out_audit->result,
                                         (u32)ERR_DETAIL_KEY_SUBCODE,
                                         (u32)subcode);
            }
            if (!saw_msg_id && out_audit->result.code != 0u) {
                err_t base = dsk_error_make(out_audit->result.domain,
                                            out_audit->result.code,
                                            subcode,
                                            (dsk_u16)out_audit->result.flags);
                out_audit->result.msg_id = base.msg_id;
            }
            st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        } else if (rec.type == DSK_TLV_TAG_AUDIT_JOB_OUTCOMES) {
            dsk_tlv_stream_t list_stream;
            dsk_status_t lst;
            dsk_u32 j;
            lst = dsk_tlv_parse_stream(rec.payload, rec.length, &list_stream);
            if (!dsk_error_is_ok(lst)) {
                dsk_tlv_view_destroy(&view);
                return lst;
            }
            for (j = 0u; j < list_stream.record_count; ++j) {
                const dsk_tlv_record_t &entry = list_stream.records[j];
                if (entry.type != DSK_TLV_TAG_AUDIT_JOB_ENTRY) {
                    continue;
                }
                dsk_tlv_stream_t job_stream;
                dsk_audit_job_t job;
                dsk_u32 k;
                job.job_id = 0u;
                job.job_kind = 0u;
                job.job_status = 0u;
                lst = dsk_tlv_parse_stream(entry.payload, entry.length, &job_stream);
                if (!dsk_error_is_ok(lst)) {
                    dsk_tlv_stream_destroy(&list_stream);
                    dsk_tlv_view_destroy(&view);
                    return lst;
                }
                for (k = 0u; k < job_stream.record_count; ++k) {
                    const dsk_tlv_record_t &field = job_stream.records[k];
                    if (field.type == DSK_TLV_TAG_AUDIT_JOB_ID) {
                        lst = dsk_parse_u32(field, &job.job_id);
                    } else if (field.type == DSK_TLV_TAG_AUDIT_JOB_KIND) {
                        lst = dsk_parse_u16(field, &job.job_kind);
                    } else if (field.type == DSK_TLV_TAG_AUDIT_JOB_STATUS) {
                        lst = dsk_parse_u16(field, &job.job_status);
                    } else {
                        continue;
                    }
                    if (!dsk_error_is_ok(lst)) {
                        dsk_tlv_stream_destroy(&job_stream);
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_view_destroy(&view);
                        return lst;
                    }
                }
                dsk_tlv_stream_destroy(&job_stream);
                out_audit->jobs.push_back(job);
            }
            dsk_tlv_stream_destroy(&list_stream);
            st = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
        } else if (rec.type == DSK_TLV_TAG_AUDIT_EVENTS) {
            dsk_tlv_stream_t list_stream;
            dsk_status_t lst;
            dsk_u32 j;
            lst = dsk_tlv_parse_stream(rec.payload, rec.length, &list_stream);
            if (!dsk_error_is_ok(lst)) {
                dsk_tlv_view_destroy(&view);
                return lst;
            }
            for (j = 0u; j < list_stream.record_count; ++j) {
                const dsk_tlv_record_t &entry = list_stream.records[j];
                if (entry.type != DSK_TLV_TAG_AUDIT_EVENT_ENTRY) {
                    continue;
                }
                dsk_tlv_stream_t evt_stream;
                dsk_status_t evt;
                dsk_u32 k;
                dsk_audit_event_t event;
                dsk_u16 subcode = 0u;
                dsk_bool saw_msg_id = DSK_FALSE;
                event.event_id = 0u;
                event.error = dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
                event.error.detail_count = 0u;
                evt = dsk_tlv_parse_stream(entry.payload, entry.length, &evt_stream);
                if (!dsk_error_is_ok(evt)) {
                    dsk_tlv_stream_destroy(&list_stream);
                    dsk_tlv_view_destroy(&view);
                    return evt;
                }
                for (k = 0u; k < evt_stream.record_count; ++k) {
                    const dsk_tlv_record_t &field = evt_stream.records[k];
                    if (field.type == DSK_TLV_TAG_AUDIT_EVENT_ID) {
                        evt = dsk_parse_u16(field, &event.event_id);
                    } else if (field.type == DSK_TLV_TAG_AUDIT_EVENT_ERR_DOMAIN) {
                        dsk_u16 v;
                        evt = dsk_parse_u16(field, &v);
                        if (dsk_error_is_ok(evt)) event.error.domain = v;
                    } else if (field.type == DSK_TLV_TAG_AUDIT_EVENT_ERR_CODE) {
                        dsk_u16 v;
                        evt = dsk_parse_u16(field, &v);
                        if (dsk_error_is_ok(evt)) event.error.code = v;
                    } else if (field.type == DSK_TLV_TAG_AUDIT_EVENT_ERR_SUBCODE) {
                        dsk_u16 v;
                        evt = dsk_parse_u16(field, &v);
                        if (dsk_error_is_ok(evt)) subcode = v;
                    } else if (field.type == DSK_TLV_TAG_AUDIT_EVENT_ERR_FLAGS) {
                        dsk_u16 v;
                        evt = dsk_parse_u16(field, &v);
                        if (dsk_error_is_ok(evt)) event.error.flags = v;
                    } else if (field.type == DSK_TLV_TAG_AUDIT_EVENT_ERR_MSG_ID) {
                        dsk_u32 v;
                        evt = dsk_parse_u32(field, &v);
                        if (dsk_error_is_ok(evt)) {
                            event.error.msg_id = v;
                            saw_msg_id = DSK_TRUE;
                        }
                    } else if (field.type == DSK_TLV_TAG_AUDIT_EVENT_ERR_DETAIL) {
                        dom::core_audit::ErrDetailTags tags;
                        tags.tag_key = DSK_TLV_TAG_ERR_DETAIL_KEY;
                        tags.tag_type = DSK_TLV_TAG_ERR_DETAIL_TYPE;
                        tags.tag_value_u32 = DSK_TLV_TAG_ERR_DETAIL_VALUE_U32;
                        tags.tag_value_u64 = DSK_TLV_TAG_ERR_DETAIL_VALUE_U64;
                        (void)dom::core_audit::parse_err_detail_entry(field.payload,
                                                                      (size_t)field.length,
                                                                      event.error,
                                                                      tags);
                    } else {
                        continue;
                    }
                    if (!dsk_error_is_ok(evt)) {
                        dsk_tlv_stream_destroy(&evt_stream);
                        dsk_tlv_stream_destroy(&list_stream);
                        dsk_tlv_view_destroy(&view);
                        return evt;
                    }
                }
                dsk_tlv_stream_destroy(&evt_stream);
                if (subcode != 0u &&
                    dom::core_audit::err_subcode(event.error) == 0u) {
                    (void)err_add_detail_u32(&event.error,
                                             (u32)ERR_DETAIL_KEY_SUBCODE,
                                             (u32)subcode);
                }
                if (!saw_msg_id && event.error.code != 0u) {
                    err_t base = dsk_error_make(event.error.domain,
                                                event.error.code,
                                                subcode,
                                                (dsk_u16)event.error.flags);
                    event.error.msg_id = base.msg_id;
                }
                out_audit->events.push_back(event);
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

static bool dsk_candidate_less(const dsk_audit_selection_candidate_t &a,
                               const dsk_audit_selection_candidate_t &b) {
    return a.id < b.id;
}

static bool dsk_rejection_less(const dsk_splat_rejection_t &a,
                               const dsk_splat_rejection_t &b) {
    if (a.id != b.id) {
        return a.id < b.id;
    }
    return a.code < b.code;
}

dsk_status_t dsk_audit_write(const dsk_audit_t *audit, dsk_tlv_buffer_t *out_buf) {
    dsk_tlv_builder_t *builder;
    dsk_status_t st;
    dsk_u32 i;

    if (!audit || !out_buf) {
        return dsk_audit_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }

    builder = dsk_tlv_builder_create();
    if (!builder) {
        return dsk_audit_error(DSK_CODE_INTERNAL_ERROR, DSK_SUBCODE_NONE);
    }

    dsk_tlv_builder_add_u64(builder, DSK_TLV_TAG_AUDIT_RUN_ID, audit->run_id);
    dsk_tlv_builder_add_u64(builder, DSK_TLV_TAG_AUDIT_MANIFEST_DIGEST64, audit->manifest_digest64);
    dsk_tlv_builder_add_u64(builder, DSK_TLV_TAG_AUDIT_REQUEST_DIGEST64, audit->request_digest64);
    dsk_tlv_builder_add_u64(builder, DSK_TLV_TAG_AUDIT_SPLAT_CAPS_DIGEST64, audit->splat_caps_digest64);
    dsk_tlv_builder_add_u64(builder, DSK_TLV_TAG_AUDIT_RESOLVED_SET_DIGEST64, audit->resolved_set_digest64);
    dsk_tlv_builder_add_u64(builder, DSK_TLV_TAG_AUDIT_PLAN_DIGEST64, audit->plan_digest64);
    dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_AUDIT_SELECTED_SPLAT, audit->selected_splat.c_str());
    dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_AUDIT_FRONTEND_ID, audit->frontend_id.c_str());
    dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_AUDIT_PLATFORM_TRIPLE, audit->platform_triple.c_str());
    dsk_tlv_builder_add_u16(builder, DSK_TLV_TAG_AUDIT_OPERATION, audit->operation);

    if (!audit->refusals.empty()) {
        dsk_tlv_builder_t *ref_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t ref_payload;
        for (i = 0u; i < audit->refusals.size(); ++i) {
            const dsk_audit_refusal_t &refusal = audit->refusals[i];
            dsk_tlv_builder_t *entry_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t entry_payload;
            dsk_tlv_builder_add_u16(entry_builder, DSK_TLV_TAG_AUDIT_REFUSAL_CODE, refusal.code);
            if (!refusal.detail.empty()) {
                dsk_tlv_builder_add_string(entry_builder,
                                           DSK_TLV_TAG_AUDIT_REFUSAL_DETAIL,
                                           refusal.detail.c_str());
            }
            st = dsk_tlv_builder_finalize_payload(entry_builder, &entry_payload);
            dsk_tlv_builder_destroy(entry_builder);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(ref_builder);
                dsk_tlv_builder_destroy(builder);
                return st;
            }
            dsk_tlv_builder_add_container(ref_builder,
                                          DSK_TLV_TAG_AUDIT_REFUSAL_ENTRY,
                                          entry_payload.data,
                                          entry_payload.size);
            dsk_tlv_buffer_free(&entry_payload);
        }
        st = dsk_tlv_builder_finalize_payload(ref_builder, &ref_payload);
        dsk_tlv_builder_destroy(ref_builder);
        if (!dsk_error_is_ok(st)) {
            dsk_tlv_builder_destroy(builder);
            return st;
        }
        dsk_tlv_builder_add_container(builder,
                                      DSK_TLV_TAG_AUDIT_REFUSALS,
                                      ref_payload.data,
                                      ref_payload.size);
        dsk_tlv_buffer_free(&ref_payload);
    }

    {
        std::vector<dsk_audit_selection_candidate_t> candidates = audit->selection.candidates;
        std::vector<dsk_splat_rejection_t> rejections = audit->selection.rejections;
        std::sort(candidates.begin(), candidates.end(), dsk_candidate_less);
        std::sort(rejections.begin(), rejections.end(), dsk_rejection_less);

        dsk_tlv_builder_t *sel_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t sel_payload;

        {
            dsk_tlv_builder_t *cand_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t cand_payload;
            for (i = 0u; i < candidates.size(); ++i) {
                dsk_tlv_builder_t *entry_builder = dsk_tlv_builder_create();
                dsk_tlv_buffer_t entry_payload;
                dsk_tlv_builder_add_string(entry_builder,
                                           DSK_TLV_TAG_AUDIT_CANDIDATE_ID,
                                           candidates[i].id.c_str());
                dsk_tlv_builder_add_u64(entry_builder,
                                        DSK_TLV_TAG_AUDIT_CANDIDATE_CAPS_DIGEST64,
                                        candidates[i].caps_digest64);
                st = dsk_tlv_builder_finalize_payload(entry_builder, &entry_payload);
                dsk_tlv_builder_destroy(entry_builder);
                if (!dsk_error_is_ok(st)) {
                    dsk_tlv_builder_destroy(cand_builder);
                    dsk_tlv_builder_destroy(sel_builder);
                    dsk_tlv_builder_destroy(builder);
                    return st;
                }
                dsk_tlv_builder_add_container(cand_builder,
                                              DSK_TLV_TAG_AUDIT_CANDIDATE_ENTRY,
                                              entry_payload.data,
                                              entry_payload.size);
                dsk_tlv_buffer_free(&entry_payload);
            }
            st = dsk_tlv_builder_finalize_payload(cand_builder, &cand_payload);
            dsk_tlv_builder_destroy(cand_builder);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(sel_builder);
                dsk_tlv_builder_destroy(builder);
                return st;
            }
            dsk_tlv_builder_add_container(sel_builder,
                                          DSK_TLV_TAG_AUDIT_CANDIDATES,
                                          cand_payload.data,
                                          cand_payload.size);
            dsk_tlv_buffer_free(&cand_payload);
        }

        {
            dsk_tlv_builder_t *rej_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t rej_payload;
            for (i = 0u; i < rejections.size(); ++i) {
                dsk_tlv_builder_t *entry_builder = dsk_tlv_builder_create();
                dsk_tlv_buffer_t entry_payload;
                dsk_tlv_builder_add_string(entry_builder,
                                           DSK_TLV_TAG_AUDIT_REJECTION_ID,
                                           rejections[i].id.c_str());
                dsk_tlv_builder_add_u16(entry_builder,
                                        DSK_TLV_TAG_AUDIT_REJECTION_CODE,
                                        rejections[i].code);
                if (!rejections[i].detail.empty()) {
                    dsk_tlv_builder_add_string(entry_builder,
                                               DSK_TLV_TAG_AUDIT_REJECTION_DETAIL,
                                               rejections[i].detail.c_str());
                }
                st = dsk_tlv_builder_finalize_payload(entry_builder, &entry_payload);
                dsk_tlv_builder_destroy(entry_builder);
                if (!dsk_error_is_ok(st)) {
                    dsk_tlv_builder_destroy(rej_builder);
                    dsk_tlv_builder_destroy(sel_builder);
                    dsk_tlv_builder_destroy(builder);
                    return st;
                }
                dsk_tlv_builder_add_container(rej_builder,
                                              DSK_TLV_TAG_AUDIT_REJECTION_ENTRY,
                                              entry_payload.data,
                                              entry_payload.size);
                dsk_tlv_buffer_free(&entry_payload);
            }
            st = dsk_tlv_builder_finalize_payload(rej_builder, &rej_payload);
            dsk_tlv_builder_destroy(rej_builder);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(sel_builder);
                dsk_tlv_builder_destroy(builder);
                return st;
            }
            dsk_tlv_builder_add_container(sel_builder,
                                          DSK_TLV_TAG_AUDIT_REJECTIONS,
                                          rej_payload.data,
                                          rej_payload.size);
            dsk_tlv_buffer_free(&rej_payload);
        }

        dsk_tlv_builder_add_string(sel_builder,
                                   DSK_TLV_TAG_AUDIT_SELECTED_ID,
                                   audit->selection.selected_id.c_str());
        dsk_tlv_builder_add_u16(sel_builder,
                                DSK_TLV_TAG_AUDIT_SELECTED_REASON,
                                audit->selection.selected_reason);

        st = dsk_tlv_builder_finalize_payload(sel_builder, &sel_payload);
        dsk_tlv_builder_destroy(sel_builder);
        if (!dsk_error_is_ok(st)) {
            dsk_tlv_builder_destroy(builder);
            return st;
        }
        dsk_tlv_builder_add_container(builder,
                                      DSK_TLV_TAG_AUDIT_SELECTION_REASON,
                                      sel_payload.data,
                                      sel_payload.size);
        dsk_tlv_buffer_free(&sel_payload);
    }

    {
        dsk_tlv_builder_t *res_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t res_payload;
        dsk_u32 subcode = dom::core_audit::err_subcode(audit->result);
        dsk_tlv_builder_add_u16(res_builder, DSK_TLV_TAG_RESULT_DOMAIN, audit->result.domain);
        dsk_tlv_builder_add_u16(res_builder, DSK_TLV_TAG_RESULT_CODE, audit->result.code);
        dsk_tlv_builder_add_u16(res_builder, DSK_TLV_TAG_RESULT_SUBCODE, (dsk_u16)subcode);
        dsk_tlv_builder_add_u16(res_builder, DSK_TLV_TAG_RESULT_FLAGS, (dsk_u16)audit->result.flags);
        dsk_tlv_builder_add_u32(res_builder, DSK_TLV_TAG_RESULT_MSG_ID, audit->result.msg_id);
        st = dsk_add_err_details(res_builder, DSK_TLV_TAG_RESULT_ERR_DETAIL, audit->result);
        if (!dsk_error_is_ok(st)) {
            dsk_tlv_builder_destroy(res_builder);
            dsk_tlv_builder_destroy(builder);
            return st;
        }
        st = dsk_tlv_builder_finalize_payload(res_builder, &res_payload);
        dsk_tlv_builder_destroy(res_builder);
        if (!dsk_error_is_ok(st)) {
            dsk_tlv_builder_destroy(builder);
            return st;
        }
        dsk_tlv_builder_add_container(builder,
                                      DSK_TLV_TAG_AUDIT_RESULT,
                                      res_payload.data,
                                      res_payload.size);
        dsk_tlv_buffer_free(&res_payload);
    }

    if (!audit->jobs.empty()) {
        dsk_tlv_builder_t *job_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t job_payload;
        for (i = 0u; i < audit->jobs.size(); ++i) {
            const dsk_audit_job_t &job = audit->jobs[i];
            dsk_tlv_builder_t *entry_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t entry_payload;
            dsk_tlv_builder_add_u32(entry_builder, DSK_TLV_TAG_AUDIT_JOB_ID, job.job_id);
            dsk_tlv_builder_add_u16(entry_builder, DSK_TLV_TAG_AUDIT_JOB_KIND, job.job_kind);
            dsk_tlv_builder_add_u16(entry_builder, DSK_TLV_TAG_AUDIT_JOB_STATUS, job.job_status);
            st = dsk_tlv_builder_finalize_payload(entry_builder, &entry_payload);
            dsk_tlv_builder_destroy(entry_builder);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(job_builder);
                dsk_tlv_builder_destroy(builder);
                return st;
            }
            dsk_tlv_builder_add_container(job_builder,
                                          DSK_TLV_TAG_AUDIT_JOB_ENTRY,
                                          entry_payload.data,
                                          entry_payload.size);
            dsk_tlv_buffer_free(&entry_payload);
        }
        st = dsk_tlv_builder_finalize_payload(job_builder, &job_payload);
        dsk_tlv_builder_destroy(job_builder);
        if (!dsk_error_is_ok(st)) {
            dsk_tlv_builder_destroy(builder);
            return st;
        }
        dsk_tlv_builder_add_container(builder,
                                      DSK_TLV_TAG_AUDIT_JOB_OUTCOMES,
                                      job_payload.data,
                                      job_payload.size);
        dsk_tlv_buffer_free(&job_payload);
    }

    {
        dsk_tlv_builder_t *evt_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t evt_payload;
        for (i = 0u; i < audit->events.size(); ++i) {
            const dsk_audit_event_t &event = audit->events[i];
            dsk_tlv_builder_t *entry_builder = dsk_tlv_builder_create();
            dsk_tlv_buffer_t entry_payload;
            dsk_u32 subcode = dom::core_audit::err_subcode(event.error);
            dsk_tlv_builder_add_u16(entry_builder, DSK_TLV_TAG_AUDIT_EVENT_ID, event.event_id);
            dsk_tlv_builder_add_u16(entry_builder, DSK_TLV_TAG_AUDIT_EVENT_ERR_DOMAIN, event.error.domain);
            dsk_tlv_builder_add_u16(entry_builder, DSK_TLV_TAG_AUDIT_EVENT_ERR_CODE, event.error.code);
            dsk_tlv_builder_add_u16(entry_builder, DSK_TLV_TAG_AUDIT_EVENT_ERR_SUBCODE, (dsk_u16)subcode);
            dsk_tlv_builder_add_u16(entry_builder, DSK_TLV_TAG_AUDIT_EVENT_ERR_FLAGS, (dsk_u16)event.error.flags);
            dsk_tlv_builder_add_u32(entry_builder, DSK_TLV_TAG_AUDIT_EVENT_ERR_MSG_ID, event.error.msg_id);
            st = dsk_add_err_details(entry_builder, DSK_TLV_TAG_AUDIT_EVENT_ERR_DETAIL, event.error);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(entry_builder);
                dsk_tlv_builder_destroy(evt_builder);
                dsk_tlv_builder_destroy(builder);
                return st;
            }
            st = dsk_tlv_builder_finalize_payload(entry_builder, &entry_payload);
            dsk_tlv_builder_destroy(entry_builder);
            if (!dsk_error_is_ok(st)) {
                dsk_tlv_builder_destroy(evt_builder);
                dsk_tlv_builder_destroy(builder);
                return st;
            }
            dsk_tlv_builder_add_container(evt_builder,
                                          DSK_TLV_TAG_AUDIT_EVENT_ENTRY,
                                          entry_payload.data,
                                          entry_payload.size);
            dsk_tlv_buffer_free(&entry_payload);
        }
        st = dsk_tlv_builder_finalize_payload(evt_builder, &evt_payload);
        dsk_tlv_builder_destroy(evt_builder);
        if (!dsk_error_is_ok(st)) {
            dsk_tlv_builder_destroy(builder);
            return st;
        }
        dsk_tlv_builder_add_container(builder,
                                      DSK_TLV_TAG_AUDIT_EVENTS,
                                      evt_payload.data,
                                      evt_payload.size);
        dsk_tlv_buffer_free(&evt_payload);
    }

    st = dsk_tlv_builder_finalize(builder, out_buf);
    dsk_tlv_builder_destroy(builder);
    return st;
}
