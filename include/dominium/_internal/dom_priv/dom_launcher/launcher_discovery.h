#ifndef DOM_LAUNCHER_DISCOVERY_H
#define DOM_LAUNCHER_DISCOVERY_H

#include <vector>
#include "dom_shared/manifest_install.h"
#include "dom_launcher/launcher_state.h"

namespace dom_launcher {

std::vector<dom_shared::InstallInfo> discover_installs(const LauncherState& state);

// Helper to merge discovered installs into state.db.installs sensibly.
void merge_discovered_installs(LauncherState& state,
                               const std::vector<dom_shared::InstallInfo>& discovered);

} // namespace dom_launcher

#endif
