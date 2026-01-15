/*
FILE: source/dominium/launcher/core/include/launcher_installed_state.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core / installed state
PURPOSE: Launcher-side helpers for setup installed_state.tlv handoff.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_INSTALLED_STATE_H
#define DOMINIUM_LAUNCHER_CORE_INSTALLED_STATE_H

#include <string>
#include <vector>

#include "dominium/core_err.h"
#include "dominium/core_installed_state.h"

namespace dom {
namespace launcher_core {

typedef dom::core_installed_state::InstalledStateArtifact LauncherInstalledStateArtifact;
typedef dom::core_installed_state::InstalledStateRegistration LauncherInstalledStateRegistration;
typedef dom::core_installed_state::InstalledState LauncherInstalledState;

bool launcher_installed_state_from_tlv_bytes(const unsigned char* data,
                                             size_t size,
                                             LauncherInstalledState& out_state);
bool launcher_installed_state_from_tlv_bytes_ex(const unsigned char* data,
                                                size_t size,
                                                LauncherInstalledState& out_state,
                                                err_t* out_err);
bool launcher_installed_state_to_tlv_bytes(const LauncherInstalledState& state,
                                           std::vector<unsigned char>& out_bytes);
bool launcher_installed_state_to_tlv_bytes_ex(const LauncherInstalledState& state,
                                              std::vector<unsigned char>& out_bytes,
                                              err_t* out_err);
u64 launcher_installed_state_hash64(const LauncherInstalledState& state);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_INSTALLED_STATE_H */
