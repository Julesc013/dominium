/*
FILE: source/dominium/launcher/core/include/launcher_safety.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / safety
RESPONSIBILITY: Deterministic string/path guards used to enforce instance-root isolation and prevent path traversal.
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: Stateless.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Pure string operations; ASCII-only classification.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_SAFETY_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_SAFETY_H

#include <string>

namespace dom {
namespace launcher_core {

/* Returns true only for a single safe path component suitable for instance IDs and similar identifiers.
 * This intentionally forbids separators, traversal, and platform-special characters.
 */
bool launcher_is_safe_id_component(const std::string& s);

/* Best-effort containment check after separator normalization:
 * returns true if `path` is equal to `root` or is under `root/`.
 */
bool launcher_path_is_within_root(const std::string& root, const std::string& path);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_SAFETY_H */

