/*
FILE: source/dominium/common/core_job_schema.c
MODULE: Dominium
PURPOSE: Registers core_job TLV schemas with the shared core_tlv_schema registry.
*/
#include "dominium/core_job.h"
#include "dominium/core_tlv_schema.h"

static err_t core_job_err_invalid_args(void) {
    return err_make((u16)ERRD_COMMON,
                    (u16)ERRC_COMMON_INVALID_ARGS,
                    (u32)ERRF_FATAL,
                    (u32)ERRMSG_COMMON_INVALID_ARGS);
}

static err_t core_job_err_parse(void) {
    return err_make((u16)ERRD_TLV,
                    (u16)ERRC_TLV_PARSE_FAILED,
                    (u32)ERRF_INTEGRITY,
                    (u32)ERRMSG_TLV_PARSE_FAILED);
}

static err_t core_job_err_integrity(void) {
    return err_make((u16)ERRD_TLV,
                    (u16)ERRC_TLV_INTEGRITY,
                    (u32)ERRF_INTEGRITY,
                    (u32)ERRMSG_TLV_INTEGRITY);
}

static err_t core_job_identity_migrate(u32 from_version,
                                       u32 to_version,
                                       const unsigned char* data,
                                       u32 size,
                                       const core_tlv_schema_sink* sink) {
    if (!sink || !sink->write) {
        return core_job_err_invalid_args();
    }
    if (from_version != to_version) {
        err_t err = err_make((u16)ERRD_TLV,
                             (u16)ERRC_TLV_SCHEMA_VERSION,
                             (u32)(ERRF_POLICY_REFUSAL | ERRF_NOT_SUPPORTED),
                             (u32)ERRMSG_TLV_SCHEMA_VERSION);
        err_add_detail_u32(&err, (u32)ERR_DETAIL_KEY_SCHEMA_VERSION, from_version);
        return err;
    }
    if (size > 0u && !data) {
        return core_job_err_invalid_args();
    }
    if (size > 0u && sink->write(sink->user, data, size) != 0) {
        return err_make((u16)ERRD_COMMON,
                        (u16)ERRC_COMMON_INTERNAL,
                        (u32)ERRF_FATAL,
                        (u32)ERRMSG_COMMON_INTERNAL);
    }
    return err_ok();
}

static err_t core_job_validate_def(const unsigned char* data,
                                   u32 size,
                                   u32* out_version) {
    core_job_def def;
    if (!data || size == 0u || !out_version) {
        return core_job_err_invalid_args();
    }
    if (core_job_def_read_tlv(data, size, &def) != 0) {
        return core_job_err_parse();
    }
    *out_version = def.schema_version;
    if (!core_job_def_validate(&def)) {
        return core_job_err_integrity();
    }
    return err_ok();
}

static err_t core_job_validate_state(const unsigned char* data,
                                     u32 size,
                                     u32* out_version) {
    core_job_state st;
    if (!data || size == 0u || !out_version) {
        return core_job_err_invalid_args();
    }
    if (core_job_state_read_tlv(data, size, &st) != 0) {
        return core_job_err_parse();
    }
    *out_version = (u32)CORE_JOB_STATE_TLV_VERSION;
    return err_ok();
}

int core_job_register_tlv_schemas(void) {
    core_tlv_schema_entry def_entry;
    core_tlv_schema_entry state_entry;
    core_tlv_schema_result res;
    int ok = 1;

    def_entry.schema_id = (u32)CORE_TLV_SCHEMA_CORE_JOB_DEF;
    def_entry.name = "core_job_def";
    def_entry.current_version = (u32)CORE_JOB_DEF_TLV_VERSION;
    def_entry.min_version = (u32)CORE_JOB_DEF_TLV_VERSION;
    def_entry.max_version = (u32)CORE_JOB_DEF_TLV_VERSION;
    def_entry.validate = core_job_validate_def;
    def_entry.migrate = core_job_identity_migrate;
    res = core_tlv_schema_register(&def_entry);
    if (res != CORE_TLV_SCHEMA_OK && res != CORE_TLV_SCHEMA_ERR_CONFLICT) {
        ok = 0;
    }

    state_entry.schema_id = (u32)CORE_TLV_SCHEMA_CORE_JOB_STATE;
    state_entry.name = "core_job_state";
    state_entry.current_version = (u32)CORE_JOB_STATE_TLV_VERSION;
    state_entry.min_version = (u32)CORE_JOB_STATE_TLV_VERSION;
    state_entry.max_version = (u32)CORE_JOB_STATE_TLV_VERSION;
    state_entry.validate = core_job_validate_state;
    state_entry.migrate = core_job_identity_migrate;
    res = core_tlv_schema_register(&state_entry);
    if (res != CORE_TLV_SCHEMA_OK && res != CORE_TLV_SCHEMA_ERR_CONFLICT) {
        ok = 0;
    }

    return ok;
}
