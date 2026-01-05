/*
FILE: source/dominium/common/dom_schema_registry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/schema_registry
RESPONSIBILITY: Schema registry for versioned formats and migration dispatch.
*/
#include "dom_schema_registry.h"

#include <stddef.h>

void dom_schema_registry_init(dom_schema_registry *registry) {
    if (!registry) {
        return;
    }
    registry->schemas.clear();
    registry->migrations.clear();
}

void dom_schema_registry_dispose(dom_schema_registry *registry) {
    if (!registry) {
        return;
    }
    registry->schemas.clear();
    registry->migrations.clear();
}

int dom_schema_registry_register(dom_schema_registry *registry,
                                 const dom_schema_desc *desc) {
    size_t i;
    if (!registry || !desc || desc->schema_id == 0u) {
        return DOM_SCHEMA_REGISTRY_INVALID_ARGUMENT;
    }
    for (i = 0u; i < registry->schemas.size(); ++i) {
        if (registry->schemas[i].schema_id == desc->schema_id) {
            return DOM_SCHEMA_REGISTRY_DUPLICATE;
        }
    }
    registry->schemas.push_back(*desc);
    return DOM_SCHEMA_REGISTRY_OK;
}

const dom_schema_desc *dom_schema_registry_find(const dom_schema_registry *registry,
                                                u64 schema_id) {
    size_t i;
    if (!registry || schema_id == 0u) {
        return (const dom_schema_desc *)0;
    }
    for (i = 0u; i < registry->schemas.size(); ++i) {
        if (registry->schemas[i].schema_id == schema_id) {
            return &registry->schemas[i];
        }
    }
    return (const dom_schema_desc *)0;
}
