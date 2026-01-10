/*
FILE: source/dominium/launcher/launcher_coredata_sim.h
MODULE: Dominium
PURPOSE: Coredata pack sim-digest helper for launcher handshake identity.
*/
#ifndef DOMINIUM_LAUNCHER_COREDATA_SIM_H
#define DOMINIUM_LAUNCHER_COREDATA_SIM_H

#include <string>

extern "C" {
#include "domino/core/types.h"
}

#include "core/include/launcher_instance.h"

namespace dom {

bool launcher_coredata_sim_hash_from_manifest(const dom::launcher_core::LauncherInstanceManifest& manifest,
                                              const std::string& state_root,
                                              u64& out_hash,
                                              std::string& out_err);

} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_COREDATA_SIM_H */
