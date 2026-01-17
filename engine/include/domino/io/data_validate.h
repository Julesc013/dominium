/*
FILE: include/domino/io/data_validate.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / io/data_validate
RESPONSIBILITY: Defines shared data validation contracts (schema registry + TLV validation).
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes and validation reports; no exceptions.
DETERMINISM: Validation is deterministic and side-effect free.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `schema/SCHEMA_VALIDATION.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_IO_DATA_VALIDATE_H_INCLUDED
#define DOMINO_IO_DATA_VALIDATE_H_INCLUDED

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Validation results and reporting
 *------------------------------------------------------------*/

typedef enum dom_validation_result {
    DOM_VALIDATION_ACCEPT = 0,
    DOM_VALIDATION_ACCEPT_WITH_WARNINGS = 1,
    DOM_VALIDATION_REFUSE = 2
} dom_validation_result;

typedef enum dom_validation_class {
    DOM_VALIDATION_SCHEMA = 1,
    DOM_VALIDATION_SEMANTIC = 2,
    DOM_VALIDATION_DETERMINISM = 3,
    DOM_VALIDATION_PERFORMANCE = 4,
    DOM_VALIDATION_MIGRATION = 5,
    DOM_VALIDATION_IO = 6
} dom_validation_class;

typedef enum dom_validation_severity {
    DOM_VALIDATION_SEV_WARNING = 1,
    DOM_VALIDATION_SEV_ERROR = 2
} dom_validation_severity;

typedef struct dom_validation_issue {
    dom_validation_class    cls;
    dom_validation_severity severity;
    char                    code[32];
    char                    message[128];
    char                    path[128];
    u32                     line;
} dom_validation_issue;

typedef struct dom_validation_report {
    dom_validation_issue* issues;
    u32                   issue_count;
    u32                   issue_capacity;
    u32                   warning_count;
    u32                   error_count;
} dom_validation_report;

void dom_validation_report_init(dom_validation_report* report,
                                dom_validation_issue* storage,
                                u32 storage_capacity);

void dom_validation_report_add(dom_validation_report* report,
                               dom_validation_class cls,
                               dom_validation_severity severity,
                               const char* code,
                               const char* message,
                               const char* path,
                               u32 line);

dom_validation_result dom_validation_report_result(const dom_validation_report* report);

/*------------------------------------------------------------
 * Schema descriptors
 *------------------------------------------------------------*/

typedef struct dom_schema_version {
    u16 major;
    u16 minor;
    u16 patch;
} dom_schema_version;

typedef enum dom_schema_stability {
    DOM_SCHEMA_STABILITY_CORE = 1,
    DOM_SCHEMA_STABILITY_EXTENSION = 2,
    DOM_SCHEMA_STABILITY_EXPERIMENTAL = 3
} dom_schema_stability;

typedef enum dom_schema_field_type {
    DOM_SCHEMA_FIELD_U32 = 1,
    DOM_SCHEMA_FIELD_U64 = 2,
    DOM_SCHEMA_FIELD_I32 = 3,
    DOM_SCHEMA_FIELD_BYTES = 4,
    DOM_SCHEMA_FIELD_STRING = 5,
    DOM_SCHEMA_FIELD_F32 = 6,
    DOM_SCHEMA_FIELD_F64 = 7
} dom_schema_field_type;

enum {
    DOM_SCHEMA_FIELD_REQUIRED  = 1u << 0,
    DOM_SCHEMA_FIELD_REPEAT    = 1u << 1,
    DOM_SCHEMA_FIELD_LOD       = 1u << 2,
    DOM_SCHEMA_FIELD_FALLBACK  = 1u << 3
};

enum {
    DOM_SCHEMA_FLAG_AUTHORITATIVE = 1u << 0,
    DOM_SCHEMA_FLAG_REQUIRE_LOD   = 1u << 1,
    DOM_SCHEMA_FLAG_REQUIRE_FALLBACK = 1u << 2
};

typedef struct dom_schema_field_desc {
    u32                    tag;
    dom_schema_field_type  type;
    u32                    flags;
    i64                    min_value;
    i64                    max_value;
    u32                    max_count;
} dom_schema_field_desc;

typedef struct dom_schema_desc {
    u64                     schema_id;
    dom_schema_version      version;
    dom_schema_stability    stability;
    u32                     flags;
    const dom_schema_field_desc* fields;
    u32                     field_count;
} dom_schema_desc;

/* Built-in validator schema used for tests and tooling scaffolding. */
#define DOM_DATA_TEST_SCHEMA_ID 0x444154415F544553ull

int dom_data_schema_register(const dom_schema_desc* desc);
void dom_data_schema_registry_reset(void);
const dom_schema_desc* dom_data_schema_find(u64 schema_id, dom_schema_version version);
void dom_data_schema_register_builtin(void);

/*------------------------------------------------------------
 * TLV validation
 *------------------------------------------------------------*/

typedef struct dom_data_validate_options {
    u32 max_records;
    int require_canon_order;
    int warn_unknown_tags;
} dom_data_validate_options;

dom_validation_result dom_data_validate_tlv(const unsigned char* tlv,
                                            u32 tlv_len,
                                            u64 schema_id,
                                            dom_schema_version version,
                                            const char* source_path,
                                            dom_validation_report* report,
                                            const dom_data_validate_options* options);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_IO_DATA_VALIDATE_H_INCLUDED */
