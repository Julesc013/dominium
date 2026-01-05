/*
FILE: source/dominium/common/dom_migration.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/migration
RESPONSIBILITY: Migration registration, path selection, and audit hooks.
ALLOWED DEPENDENCIES: C++98 STL and `include/domino/**` base types.
FORBIDDEN DEPENDENCIES: Platform APIs; filesystem/time access.
*/
#ifndef DOM_MIGRATION_H
#define DOM_MIGRATION_H

#include "dom_schema_registry.h"

typedef struct dom_migration_desc {
    u64 schema_id;
    u32 from_version;
    u32 to_version;
    dom_migration_fn fn;
    void *user;
} dom_migration_desc;

typedef struct dom_migration_audit_record {
    u64 schema_id;
    u32 from_version;
    u32 to_version;
    int result;
} dom_migration_audit_record;

typedef void (*dom_migration_audit_fn)(const dom_migration_audit_record *rec, void *user);

typedef struct dom_migration_audit_sink {
    dom_migration_audit_fn write;
    void *user;
} dom_migration_audit_sink;

int dom_migration_register(dom_schema_registry *registry,
                           const dom_migration_desc *desc);

int dom_migration_find_path(const dom_schema_registry *registry,
                            u64 schema_id,
                            u32 from_version,
                            u32 to_version,
                            u32 *out_versions,
                            u32 out_cap,
                            u32 *out_count);

int dom_migration_apply_chain(const dom_schema_registry *registry,
                              u64 schema_id,
                              u32 from_version,
                              u32 to_version,
                              const dom_migration_audit_sink *audit);

#endif /* DOM_MIGRATION_H */
