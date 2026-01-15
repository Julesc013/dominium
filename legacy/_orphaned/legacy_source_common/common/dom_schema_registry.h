/*
FILE: source/dominium/common/dom_schema_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/schema_registry
RESPONSIBILITY: Schema registry for versioned formats and migration dispatch.
ALLOWED DEPENDENCIES: C++98 STL and `include/domino/**` base types.
FORBIDDEN DEPENDENCIES: Platform APIs; filesystem/time access.
*/
#ifndef DOM_SCHEMA_REGISTRY_H
#define DOM_SCHEMA_REGISTRY_H

#include <vector>

extern "C" {
#include "domino/core/types.h"
}

enum {
    DOM_SCHEMA_REGISTRY_OK = 0,
    DOM_SCHEMA_REGISTRY_ERR = -1,
    DOM_SCHEMA_REGISTRY_INVALID_ARGUMENT = -2,
    DOM_SCHEMA_REGISTRY_DUPLICATE = -3,
    DOM_SCHEMA_REGISTRY_NOT_FOUND = -4,
    DOM_SCHEMA_REGISTRY_NO_PATH = -5,
    DOM_SCHEMA_REGISTRY_MIGRATION_FAILED = -6
};

typedef int (*dom_migration_fn)(u64 schema_id, u32 from_version, u32 to_version, void *user);

typedef struct dom_schema_desc {
    u64 schema_id;
    u32 current_version;
    const char *name;
} dom_schema_desc;

typedef struct dom_migration_edge {
    u64 schema_id;
    u32 from_version;
    u32 to_version;
    dom_migration_fn fn;
    void *user;
} dom_migration_edge;

typedef struct dom_schema_registry {
    std::vector<dom_schema_desc> schemas;
    std::vector<dom_migration_edge> migrations;
} dom_schema_registry;

void dom_schema_registry_init(dom_schema_registry *registry);
void dom_schema_registry_dispose(dom_schema_registry *registry);

int dom_schema_registry_register(dom_schema_registry *registry,
                                 const dom_schema_desc *desc);
const dom_schema_desc *dom_schema_registry_find(const dom_schema_registry *registry,
                                                u64 schema_id);

#endif /* DOM_SCHEMA_REGISTRY_H */
