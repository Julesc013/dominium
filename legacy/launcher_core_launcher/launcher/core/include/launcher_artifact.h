/*
FILE: source/dominium/launcher/core/include/launcher_artifact.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / artifact
RESPONSIBILITY: Abstract artifact references used by tasks/manifests (no OS paths, no UI coupling).
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types only.
FORBIDDEN DEPENDENCIES: Platform APIs, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: N/A (pure data).
DETERMINISM: IDs and ordering are explicit; no pointer-identity semantics.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_ARTIFACT_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_ARTIFACT_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

namespace dom {
namespace launcher_core {

enum LauncherArtifactKind {
    LAUNCHER_ARTIFACT_UNKNOWN = 0,
    LAUNCHER_ARTIFACT_ENGINE_BUILD = 1,
    LAUNCHER_ARTIFACT_GAME_BUILD = 2,
    LAUNCHER_ARTIFACT_PACK = 3,
    LAUNCHER_ARTIFACT_MOD = 4
};

struct LauncherArtifactRef {
    u32 kind;
    std::string id;
    std::string build_id;
    std::vector<unsigned char> hash_bytes; /* optional; algorithm identified elsewhere */

    LauncherArtifactRef();
};

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_ARTIFACT_H */

