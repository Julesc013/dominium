/*
FILE: source/domino/res/dg_data_validate.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / res/dg_data_validate
RESPONSIBILITY: Implements shared data validation (schema registry + TLV checks).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Validation report + result enum; no exceptions.
DETERMINISM: Deterministic ordering and checks; no randomness or OS time.
VERSIONING / ABI / DATA FORMAT NOTES: See schema/SCHEMA_VERSIONING.md.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "domino/io/data_validate.h"
#include "res/dg_tlv_canon.h"

#define DOM_DATA_SCHEMA_MAX 64u
#define DOM_DATA_FIELD_MAX 64u

#define DOM_DATA_DEFAULT_MAX_RECORDS 1024u
#define DOM_DATA_DEFAULT_REQUIRE_CANON 1
#define DOM_DATA_DEFAULT_WARN_UNKNOWN 1


static dom_schema_desc g_schema_registry[DOM_DATA_SCHEMA_MAX];
static u32 g_schema_count = 0u;

static void dom_copy_str(char* dst, size_t cap, const char* src) {
    size_t i;
    if (!dst || cap == 0u) {
        return;
    }
    if (!src) {
        dst[0] = '\0';
        return;
    }
    for (i = 0u; i + 1u < cap && src[i] != '\0'; ++i) {
        dst[i] = src[i];
    }
    dst[i] = '\0';
}

void dom_validation_report_init(dom_validation_report* report,
                                dom_validation_issue* storage,
                                u32 storage_capacity) {
    if (!report) {
        return;
    }
    report->issues = storage;
    report->issue_count = 0u;
    report->issue_capacity = storage_capacity;
    report->warning_count = 0u;
    report->error_count = 0u;
    if (storage && storage_capacity > 0u) {
        memset(storage, 0, sizeof(dom_validation_issue) * (size_t)storage_capacity);
    }
}

void dom_validation_report_add(dom_validation_report* report,
                               dom_validation_class cls,
                               dom_validation_severity severity,
                               const char* code,
                               const char* message,
                               const char* path,
                               u32 line) {
    dom_validation_issue* issue;
    if (!report) {
        return;
    }
    if (severity == DOM_VALIDATION_SEV_WARNING) {
        report->warning_count += 1u;
    } else {
        report->error_count += 1u;
    }
    if (!report->issues || report->issue_count >= report->issue_capacity) {
        return;
    }
    issue = &report->issues[report->issue_count++];
    issue->cls = cls;
    issue->severity = severity;
    issue->line = line;
    dom_copy_str(issue->code, sizeof(issue->code), code);
    dom_copy_str(issue->message, sizeof(issue->message), message);
    dom_copy_str(issue->path, sizeof(issue->path), path);
}

dom_validation_result dom_validation_report_result(const dom_validation_report* report) {
    if (!report) {
        return DOM_VALIDATION_REFUSE;
    }
    if (report->error_count > 0u) {
        return DOM_VALIDATION_REFUSE;
    }
    if (report->warning_count > 0u) {
        return DOM_VALIDATION_ACCEPT_WITH_WARNINGS;
    }
    return DOM_VALIDATION_ACCEPT;
}

static int dom_schema_version_cmp(dom_schema_version a, dom_schema_version b) {
    if (a.major < b.major) return -1;
    if (a.major > b.major) return 1;
    if (a.minor < b.minor) return -1;
    if (a.minor > b.minor) return 1;
    if (a.patch < b.patch) return -1;
    if (a.patch > b.patch) return 1;
    return 0;
}

int dom_data_schema_register(const dom_schema_desc* desc) {
    u32 i;
    if (!desc || !desc->fields || desc->field_count == 0u) {
        return -1;
    }
    if (g_schema_count >= DOM_DATA_SCHEMA_MAX) {
        return -2;
    }
    for (i = 0u; i < g_schema_count; ++i) {
        if (g_schema_registry[i].schema_id == desc->schema_id &&
            dom_schema_version_cmp(g_schema_registry[i].version, desc->version) == 0) {
            return -3;
        }
    }
    g_schema_registry[g_schema_count++] = *desc;
    return 0;
}

void dom_data_schema_registry_reset(void) {
    g_schema_count = 0u;
}

const dom_schema_desc* dom_data_schema_find(u64 schema_id, dom_schema_version version) {
    u32 i;
    for (i = 0u; i < g_schema_count; ++i) {
        if (g_schema_registry[i].schema_id == schema_id &&
            dom_schema_version_cmp(g_schema_registry[i].version, version) == 0) {
            return &g_schema_registry[i];
        }
    }
    return (const dom_schema_desc*)0;
}

static const dom_schema_desc* dom_data_schema_find_best(u64 schema_id,
                                                        dom_schema_version version,
                                                        int* out_exact,
                                                        int* out_major_mismatch,
                                                        dom_schema_version* out_latest_same_major) {
    const dom_schema_desc* best = (const dom_schema_desc*)0;
    const dom_schema_desc* latest_same_major = (const dom_schema_desc*)0;
    const dom_schema_desc* exact = (const dom_schema_desc*)0;
    u32 i;
    int has_any = 0;
    int major_match = 0;

    if (out_exact) *out_exact = 0;
    if (out_major_mismatch) *out_major_mismatch = 0;
    if (out_latest_same_major) {
        out_latest_same_major->major = 0u;
        out_latest_same_major->minor = 0u;
        out_latest_same_major->patch = 0u;
    }

    for (i = 0u; i < g_schema_count; ++i) {
        const dom_schema_desc* cur = &g_schema_registry[i];
        if (cur->schema_id != schema_id) {
            continue;
        }
        has_any = 1;
        if (cur->version.major != version.major) {
            continue;
        }
        major_match = 1;
        if (!latest_same_major || dom_schema_version_cmp(cur->version, latest_same_major->version) > 0) {
            latest_same_major = cur;
        }
        if (dom_schema_version_cmp(cur->version, version) == 0) {
            exact = cur;
        }
        if (dom_schema_version_cmp(cur->version, version) <= 0) {
            if (!best || dom_schema_version_cmp(cur->version, best->version) > 0) {
                best = cur;
            }
        }
    }

    if (exact) {
        if (out_exact) *out_exact = 1;
        return exact;
    }
    if (has_any && !major_match) {
        if (out_major_mismatch) *out_major_mismatch = 1;
        return (const dom_schema_desc*)0;
    }
    if (latest_same_major) {
        if (out_latest_same_major) *out_latest_same_major = latest_same_major->version;
        return best ? best : latest_same_major;
    }
    if (out_major_mismatch) *out_major_mismatch = 0;
    return (const dom_schema_desc*)0;
}

static const dom_schema_field_desc* dom_schema_find_field(const dom_schema_desc* schema,
                                                          u32 tag,
                                                          u32* out_index) {
    u32 i;
    if (!schema || !schema->fields) {
        return (const dom_schema_field_desc*)0;
    }
    for (i = 0u; i < schema->field_count; ++i) {
        if (schema->fields[i].tag == tag) {
            if (out_index) *out_index = i;
            return &schema->fields[i];
        }
    }
    return (const dom_schema_field_desc*)0;
}

static int dom_schema_requires_float(const dom_schema_desc* schema) {
    u32 i;
    if (!schema || !schema->fields) {
        return 0;
    }
    for (i = 0u; i < schema->field_count; ++i) {
        if (schema->fields[i].type == DOM_SCHEMA_FIELD_F32 ||
            schema->fields[i].type == DOM_SCHEMA_FIELD_F64) {
            return 1;
        }
    }
    return 0;
}

static void dom_add_version_warning(dom_validation_report* report,
                                    const char* code,
                                    const char* message,
                                    const char* path) {
    dom_validation_report_add(report,
                              DOM_VALIDATION_SCHEMA,
                              DOM_VALIDATION_SEV_WARNING,
                              code,
                              message,
                              path,
                              0u);
}

static void dom_data_register_builtin_schema(void) {
    static dom_schema_field_desc fields[] = {
        { 1u, DOM_SCHEMA_FIELD_U64, DOM_SCHEMA_FIELD_REQUIRED, 1, 0x7fffffffffffffffll, 0u },
        { 2u, DOM_SCHEMA_FIELD_U32, DOM_SCHEMA_FIELD_REQUIRED, 1, 1000, 0u },
        { 3u, DOM_SCHEMA_FIELD_U32, DOM_SCHEMA_FIELD_REQUIRED | DOM_SCHEMA_FIELD_LOD, 1, 16, 0u },
        { 4u, DOM_SCHEMA_FIELD_U64, DOM_SCHEMA_FIELD_REQUIRED | DOM_SCHEMA_FIELD_FALLBACK, 1, 0x7fffffffffffffffll, 0u },
        { 5u, DOM_SCHEMA_FIELD_U32, DOM_SCHEMA_FIELD_REPEAT, 0, 1000000, 8u }
    };
    dom_schema_desc schema;
    schema.schema_id = DOM_DATA_TEST_SCHEMA_ID;
    schema.version.major = 1u;
    schema.version.minor = 0u;
    schema.version.patch = 0u;
    schema.stability = DOM_SCHEMA_STABILITY_CORE;
    schema.flags = DOM_SCHEMA_FLAG_AUTHORITATIVE | DOM_SCHEMA_FLAG_REQUIRE_LOD | DOM_SCHEMA_FLAG_REQUIRE_FALLBACK;
    schema.fields = fields;
    schema.field_count = (u32)(sizeof(fields) / sizeof(fields[0]));
    (void)dom_data_schema_register(&schema);
}

void dom_data_schema_register_builtin(void) {
    if (g_schema_count == 0u) {
        dom_data_register_builtin_schema();
    }
}

static void dom_data_validate_field_payload(dom_validation_report* report,
                                            const dom_schema_field_desc* field,
                                            const unsigned char* payload,
                                            u32 payload_len,
                                            const char* path) {
    if (!field) {
        return;
    }
    switch (field->type) {
        case DOM_SCHEMA_FIELD_U32:
        case DOM_SCHEMA_FIELD_I32:
        case DOM_SCHEMA_FIELD_F32:
            if (payload_len != 4u) {
                dom_validation_report_add(report, DOM_VALIDATION_SCHEMA, DOM_VALIDATION_SEV_ERROR,
                                          "field_len_invalid", "expected 4-byte payload", path, 0u);
            }
            break;
        case DOM_SCHEMA_FIELD_U64:
        case DOM_SCHEMA_FIELD_F64:
            if (payload_len != 8u) {
                dom_validation_report_add(report, DOM_VALIDATION_SCHEMA, DOM_VALIDATION_SEV_ERROR,
                                          "field_len_invalid", "expected 8-byte payload", path, 0u);
            }
            break;
        case DOM_SCHEMA_FIELD_STRING:
            if (payload_len == 0u || !payload) {
                dom_validation_report_add(report, DOM_VALIDATION_SCHEMA, DOM_VALIDATION_SEV_ERROR,
                                          "field_empty_string", "string payload missing", path, 0u);
            } else if (payload[payload_len - 1u] != '\0') {
                dom_validation_report_add(report, DOM_VALIDATION_SCHEMA, DOM_VALIDATION_SEV_ERROR,
                                          "field_string_unterminated", "string missing NUL terminator", path, 0u);
            }
            break;
        case DOM_SCHEMA_FIELD_BYTES:
        default:
            break;
    }
}

static void dom_data_validate_field_range(dom_validation_report* report,
                                          const dom_schema_field_desc* field,
                                          const unsigned char* payload,
                                          u32 payload_len,
                                          const char* path) {
    i64 value = 0;
    if (!field || !payload) {
        return;
    }
    if (field->type == DOM_SCHEMA_FIELD_U32 && payload_len == 4u) {
        value = (i64)dg_le_read_u32(payload);
    } else if (field->type == DOM_SCHEMA_FIELD_I32 && payload_len == 4u) {
        value = (i64)(i32)dg_le_read_u32(payload);
    } else if (field->type == DOM_SCHEMA_FIELD_U64 && payload_len == 8u) {
        u64 v = dg_le_read_u64(payload);
        if (v > 0x7fffffffffffffffll) {
            dom_validation_report_add(report, DOM_VALIDATION_SEMANTIC, DOM_VALIDATION_SEV_ERROR,
                                      "field_range_overflow", "u64 exceeds signed range", path, 0u);
            return;
        }
        value = (i64)v;
    } else {
        return;
    }
    if (value < field->min_value || value > field->max_value) {
        dom_validation_report_add(report, DOM_VALIDATION_SEMANTIC, DOM_VALIDATION_SEV_ERROR,
                                  "field_out_of_range", "numeric value out of range", path, 0u);
    }
}

dom_validation_result dom_data_validate_tlv(const unsigned char* tlv,
                                            u32 tlv_len,
                                            u64 schema_id,
                                            dom_schema_version version,
                                            const char* source_path,
                                            dom_validation_report* report,
                                            const dom_data_validate_options* options) {
    dom_data_validate_options local_opts;
    const dom_schema_desc* schema;
    dom_schema_version latest_version;
    int exact = 0;
    int major_mismatch = 0;
    u32* counts = (u32*)0;
    u32 offset = 0u;
    u32 tag = 0u;
    u32 last_tag = 0u;
    u32 record_count = 0u;
    int have_lod = 0;
    int have_fallback = 0;

    if (!report) {
        return DOM_VALIDATION_REFUSE;
    }
    if (schema_id == 0u ||
        (version.major == 0u && version.minor == 0u && version.patch == 0u)) {
        dom_validation_report_add(report, DOM_VALIDATION_SCHEMA, DOM_VALIDATION_SEV_ERROR,
                                  "schema_meta_missing", "schema id or version missing",
                                  source_path, 0u);
        return dom_validation_report_result(report);
    }
    if (!tlv && tlv_len != 0u) {
        dom_validation_report_add(report, DOM_VALIDATION_SCHEMA, DOM_VALIDATION_SEV_ERROR,
                                  "tlv_null", "TLV buffer is NULL", source_path, 0u);
        return dom_validation_report_result(report);
    }

    local_opts.max_records = DOM_DATA_DEFAULT_MAX_RECORDS;
    local_opts.require_canon_order = DOM_DATA_DEFAULT_REQUIRE_CANON;
    local_opts.warn_unknown_tags = DOM_DATA_DEFAULT_WARN_UNKNOWN;
    if (options) {
        if (options->max_records > 0u) {
            local_opts.max_records = options->max_records;
        }
        local_opts.require_canon_order = options->require_canon_order;
        local_opts.warn_unknown_tags = options->warn_unknown_tags;
    }

    schema = dom_data_schema_find_best(schema_id, version, &exact, &major_mismatch, &latest_version);
    if (!schema) {
        if (major_mismatch) {
            dom_validation_report_add(report, DOM_VALIDATION_MIGRATION, DOM_VALIDATION_SEV_ERROR,
                                      "schema_major_mismatch", "schema major version requires migration",
                                      source_path, 0u);
        } else {
            dom_validation_report_add(report, DOM_VALIDATION_SCHEMA, DOM_VALIDATION_SEV_ERROR,
                                      "schema_unknown", "schema id not registered",
                                      source_path, 0u);
        }
        return dom_validation_report_result(report);
    }

    if (!exact) {
        int cmp = dom_schema_version_cmp(version, latest_version);
        if (cmp < 0) {
            dom_add_version_warning(report, "schema_version_behind",
                                    "schema version older than registry", source_path);
        } else if (cmp > 0) {
            dom_add_version_warning(report, "schema_version_ahead",
                                    "schema version newer than registry", source_path);
        }
    }

    if ((schema->flags & DOM_SCHEMA_FLAG_AUTHORITATIVE) != 0u && dom_schema_requires_float(schema)) {
        dom_validation_report_add(report, DOM_VALIDATION_DETERMINISM, DOM_VALIDATION_SEV_ERROR,
                                  "authoritative_float_forbidden",
                                  "authoritative schema contains floating point fields",
                                  source_path, 0u);
    }

    if (schema->field_count > DOM_DATA_FIELD_MAX) {
        dom_validation_report_add(report, DOM_VALIDATION_SCHEMA, DOM_VALIDATION_SEV_ERROR,
                                  "schema_field_count", "schema field count exceeds limit",
                                  source_path, 0u);
        return dom_validation_report_result(report);
    }

    counts = (u32*)malloc(sizeof(u32) * (size_t)schema->field_count);
    if (!counts) {
        dom_validation_report_add(report, DOM_VALIDATION_IO, DOM_VALIDATION_SEV_ERROR,
                                  "oom", "validation out of memory", source_path, 0u);
        return dom_validation_report_result(report);
    }
    memset(counts, 0, sizeof(u32) * (size_t)schema->field_count);

    for (;;) {
        const unsigned char* payload = (const unsigned char*)0;
        u32 payload_len = 0u;
        const dom_schema_field_desc* field;
        u32 field_index = 0u;
        int rc = dg_tlv_next(tlv, tlv_len, &offset, &tag, &payload, &payload_len);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            dom_validation_report_add(report, DOM_VALIDATION_SCHEMA, DOM_VALIDATION_SEV_ERROR,
                                      "tlv_malformed", "TLV is malformed", source_path, 0u);
            break;
        }
        record_count += 1u;
        if (record_count > local_opts.max_records) {
            dom_validation_report_add(report, DOM_VALIDATION_PERFORMANCE, DOM_VALIDATION_SEV_ERROR,
                                      "record_count_exceeded", "TLV record count exceeds limit",
                                      source_path, 0u);
        }
        if (local_opts.require_canon_order && record_count > 1u && tag < last_tag) {
            dom_validation_report_add(report, DOM_VALIDATION_DETERMINISM, DOM_VALIDATION_SEV_ERROR,
                                      "tag_order_noncanonical", "TLV tags not in canonical order",
                                      source_path, 0u);
        }
        last_tag = tag;

        field = dom_schema_find_field(schema, tag, &field_index);
        if (!field) {
            if (local_opts.warn_unknown_tags) {
                dom_validation_report_add(report, DOM_VALIDATION_SCHEMA, DOM_VALIDATION_SEV_WARNING,
                                          "unknown_tag", "unknown tag preserved", source_path, 0u);
            }
            continue;
        }

        counts[field_index] += 1u;
        if ((field->flags & DOM_SCHEMA_FIELD_REPEAT) == 0u && counts[field_index] > 1u) {
            dom_validation_report_add(report, DOM_VALIDATION_SCHEMA, DOM_VALIDATION_SEV_ERROR,
                                      "field_duplicate", "non-repeatable field repeated",
                                      source_path, 0u);
        }
        if ((field->flags & DOM_SCHEMA_FIELD_REPEAT) != 0u && field->max_count > 0u &&
            counts[field_index] > field->max_count) {
            dom_validation_report_add(report, DOM_VALIDATION_PERFORMANCE, DOM_VALIDATION_SEV_ERROR,
                                      "field_repeat_exceeded", "repeatable field exceeds max count",
                                      source_path, 0u);
        }

        if ((field->flags & DOM_SCHEMA_FIELD_LOD) != 0u) {
            have_lod = 1;
        }
        if ((field->flags & DOM_SCHEMA_FIELD_FALLBACK) != 0u) {
            have_fallback = 1;
        }

        dom_data_validate_field_payload(report, field, payload, payload_len, source_path);
        dom_data_validate_field_range(report, field, payload, payload_len, source_path);
    }

    {
        u32 i;
        for (i = 0u; i < schema->field_count; ++i) {
            const dom_schema_field_desc* field = &schema->fields[i];
            if ((field->flags & DOM_SCHEMA_FIELD_REQUIRED) != 0u && counts[i] == 0u) {
                dom_validation_report_add(report, DOM_VALIDATION_SCHEMA, DOM_VALIDATION_SEV_ERROR,
                                          "field_required_missing", "required field missing",
                                          source_path, 0u);
            }
            if ((field->flags & DOM_SCHEMA_FIELD_REPEAT) != 0u && field->max_count == 0u) {
                dom_validation_report_add(report, DOM_VALIDATION_PERFORMANCE, DOM_VALIDATION_SEV_ERROR,
                                          "field_repeat_unbounded", "repeatable field lacks max count",
                                          source_path, 0u);
            }
        }
    }

    if ((schema->flags & DOM_SCHEMA_FLAG_REQUIRE_LOD) != 0u && !have_lod) {
        dom_validation_report_add(report, DOM_VALIDATION_PERFORMANCE, DOM_VALIDATION_SEV_ERROR,
                                  "lod_missing", "LOD ladder field missing", source_path, 0u);
    }
    if ((schema->flags & DOM_SCHEMA_FLAG_REQUIRE_FALLBACK) != 0u && !have_fallback) {
        dom_validation_report_add(report, DOM_VALIDATION_PERFORMANCE, DOM_VALIDATION_SEV_ERROR,
                                  "fallback_missing", "fallback field missing", source_path, 0u);
    }

    if (counts) {
        free(counts);
    }
    return dom_validation_report_result(report);
}
