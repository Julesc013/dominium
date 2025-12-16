/*
FILE: source/dominium/launcher/core/src/artifact/launcher_artifact.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / artifact
RESPONSIBILITY: Implements artifact model constructors (pure data).
*/

#include "launcher_artifact.h"

namespace dom {
namespace launcher_core {

LauncherArtifactRef::LauncherArtifactRef()
    : kind((u32)LAUNCHER_ARTIFACT_UNKNOWN),
      id(),
      build_id(),
      hash_bytes() {
}

} /* namespace launcher_core */
} /* namespace dom */

