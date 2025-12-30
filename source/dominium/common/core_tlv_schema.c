/*
FILE: source/dominium/common/core_tlv_schema.c
MODULE: Dominium
PURPOSE: Central TLV schema registry with version checks and migration hooks.
*/
#include "dominium/core_tlv_schema.h"

#include <string.h>

static core_tlv_schema_entry g_entries[CORE_TLV_SCHEMA_MAX_ENTRIES];
static u32 g_entry_count = 0u;

void core_tlv_schema_reset_registry(void) {
    memset(g_entries, 0, sizeof(g_entries));
    g_entry_count = 0u;
}

static int core_tlv_schema_conflicts(const core_tlv_schema_entry* a,
                                     const core_tlv_schema_entry* b) {
    if (!a || !b) {
        return 0;
    }
    if (a->schema_id == b->schema_id) {
        return 1;
    }
    return 0;
}

core_tlv_schema_result core_tlv_schema_register(const core_tlv_schema_entry* entry) {
    u32 i;
    if (!entry) {
        return CORE_TLV_SCHEMA_ERR_NULL;
    }
    if (g_entry_count >= (u32)CORE_TLV_SCHEMA_MAX_ENTRIES) {
        return CORE_TLV_SCHEMA_ERR_FULL;
    }
    for (i = 0u; i < g_entry_count; ++i) {
        if (core_tlv_schema_conflicts(&g_entries[i], entry)) {
            return CORE_TLV_SCHEMA_ERR_CONFLICT;
        }
    }
    g_entries[g_entry_count] = *entry;
    g_entry_count += 1u;
    return CORE_TLV_SCHEMA_OK;
}

u32 core_tlv_schema_count(void) {
    return g_entry_count;
}

const core_tlv_schema_entry* core_tlv_schema_at(u32 index) {
    if (index >= g_entry_count) {
        return 0;
    }
    return &g_entries[index];
}

const core_tlv_schema_entry* core_tlv_schema_find(u32 schema_id) {
    u32 i;
    for (i = 0u; i < g_entry_count; ++i) {
        if (g_entries[i].schema_id == schema_id) {
            return &g_entries[i];
        }
    }
    return 0;
}

int core_tlv_schema_accepts_version(const core_tlv_schema_entry* entry, u32 version) {
    if (!entry) {
        return 0;
    }
    if (version < entry->min_version) {
        return 0;
    }
    if (version > entry->max_version) {
        return 0;
    }
    return 1;
}

err_t core_tlv_schema_validate_entry(const core_tlv_schema_entry* entry,
                                     const unsigned char* data,
                                     u32 size,
                                     u32* out_version) {
    err_t err;
    if (!entry || !entry->validate) {
        return err_make((u16)ERRD_COMMON,
                        (u16)ERRC_COMMON_INVALID_ARGS,
                        (u32)ERRF_FATAL,
                        (u32)ERRMSG_COMMON_INVALID_ARGS);
    }
    err = entry->validate(data, size, out_version);
    if (!err_is_ok(&err)) {
        return err;
    }
    if (!out_version) {
        return err_make((u16)ERRD_COMMON,
                        (u16)ERRC_COMMON_INVALID_ARGS,
                        (u32)ERRF_FATAL,
                        (u32)ERRMSG_COMMON_INVALID_ARGS);
    }
    if (!core_tlv_schema_accepts_version(entry, *out_version)) {
        err_t version_err = err_make((u16)ERRD_TLV,
                                     (u16)ERRC_TLV_SCHEMA_VERSION,
                                     (u32)(ERRF_POLICY_REFUSAL | ERRF_NOT_SUPPORTED),
                                     (u32)ERRMSG_TLV_SCHEMA_VERSION);
        err_add_detail_u32(&version_err, (u32)ERR_DETAIL_KEY_SCHEMA_VERSION, *out_version);
        return version_err;
    }
    return err_ok();
}

err_t core_tlv_schema_validate(u32 schema_id,
                               const unsigned char* data,
                               u32 size,
                               u32* out_version) {
    const core_tlv_schema_entry* entry = core_tlv_schema_find(schema_id);
    if (!entry) {
        return err_make((u16)ERRD_COMMON,
                        (u16)ERRC_COMMON_NOT_FOUND,
                        (u32)ERRF_FATAL,
                        (u32)ERRMSG_COMMON_NOT_FOUND);
    }
    return core_tlv_schema_validate_entry(entry, data, size, out_version);
}

err_t core_tlv_schema_migrate(u32 schema_id,
                              u32 from_version,
                              u32 to_version,
                              const unsigned char* data,
                              u32 size,
                              const core_tlv_schema_sink* sink) {
    const core_tlv_schema_entry* entry = core_tlv_schema_find(schema_id);
    if (!entry) {
        return err_make((u16)ERRD_COMMON,
                        (u16)ERRC_COMMON_NOT_FOUND,
                        (u32)ERRF_FATAL,
                        (u32)ERRMSG_COMMON_NOT_FOUND);
    }
    if (!entry->migrate) {
        err_t err = err_make((u16)ERRD_TLV,
                             (u16)ERRC_TLV_SCHEMA_VERSION,
                             (u32)(ERRF_POLICY_REFUSAL | ERRF_NOT_SUPPORTED),
                             (u32)ERRMSG_TLV_SCHEMA_VERSION);
        err_add_detail_u32(&err, (u32)ERR_DETAIL_KEY_SCHEMA_VERSION, from_version);
        return err;
    }
    return entry->migrate(from_version, to_version, data, size, sink);
}
