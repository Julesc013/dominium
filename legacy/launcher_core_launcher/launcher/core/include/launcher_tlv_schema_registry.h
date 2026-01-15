/*
FILE: source/dominium/launcher/core/include/launcher_tlv_schema_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / tlv
RESPONSIBILITY: Registers launcher TLV schemas with the shared core_tlv_schema registry.
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types only.
FORBIDDEN DEPENDENCIES: Platform APIs, renderer/UI headers, and any Plan 8 contract changes.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_TLV_SCHEMA_REGISTRY_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_TLV_SCHEMA_REGISTRY_H

namespace dom {
namespace launcher_core {

/* Returns non-zero on success; safe to call multiple times. */
int launcher_register_tlv_schemas(void);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_TLV_SCHEMA_REGISTRY_H */
