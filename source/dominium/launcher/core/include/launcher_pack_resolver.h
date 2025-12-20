/*
FILE: source/dominium/launcher/core/include/launcher_pack_resolver.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (ecosystem) / pack_resolver
RESPONSIBILITY: Deterministic pack dependency resolution + load-order computation + simulation safety validation (instance-scoped).
ALLOWED DEPENDENCIES: C++98 standard headers and launcher core instance/artifact/pack manifest models; services facade for artifact reads.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; detailed failure reasons returned via out_error and/or audit reasons in higher layers.
DETERMINISM: Same inputs produce the same resolved order and failure strings.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_PACK_RESOLVER_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_PACK_RESOLVER_H

#include <string>
#include <vector>

extern "C" {
#include "launcher_core_api.h"
}

#include "launcher_instance.h"
#include "launcher_pack_manifest.h"

namespace dom {
namespace launcher_core {

struct LauncherResolvedPack {
    std::string pack_id;
    u32 content_type; /* `LauncherContentType` (pack/mod/runtime) */
    std::string version;
    std::vector<unsigned char> artifact_hash_bytes;

    u32 phase; /* `LauncherPackPhase` */
    i32 effective_order; /* pack explicit order, overridden by instance when present */

    std::vector<std::string> sim_affecting_flags;

    LauncherResolvedPack();
};

/* Resolves enabled pack-like entries (type pack/mod/runtime) from an instance manifest.
 *
 * Rules:
 * - Validates each enabled pack entry against its pack_manifest (id/type/version match).
 * - Enforces required dependencies and conflicts strictly.
 * - Optional dependencies constrain ordering only when present, and must satisfy their version range when present.
 * - Produces a deterministic topological order with tie-breakers:
 *     phase, effective_order, lexicographic pack_id
 */
bool launcher_pack_resolve_enabled(const launcher_services_api_v1* services,
                                   const LauncherInstanceManifest& manifest,
                                   const std::string& state_root_override,
                                   std::vector<LauncherResolvedPack>& out_ordered,
                                   std::string* out_error);

/* Simulation safety: refuses when any enabled, sim-affecting pack is missing, mismatched, or cannot be validated. */
bool launcher_pack_validate_simulation_safety(const launcher_services_api_v1* services,
                                              const LauncherInstanceManifest& manifest,
                                              const std::string& state_root_override,
                                              std::string* out_error);

/* Deterministic summary string for audit/logging (comma-separated pack ids in resolved order). */
std::string launcher_pack_resolved_order_summary(const std::vector<LauncherResolvedPack>& ordered);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_PACK_RESOLVER_H */

