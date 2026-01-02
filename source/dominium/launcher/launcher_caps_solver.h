/*
FILE: source/dominium/launcher/launcher_caps_solver.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher / caps_solver
RESPONSIBILITY: Typed caps + solver adapter for launcher backend selection.
*/
#ifndef DOMINIUM_LAUNCHER_CAPS_SOLVER_H
#define DOMINIUM_LAUNCHER_CAPS_SOLVER_H

#include <string>
#include <vector>

extern "C" {
#include "dominium/core_caps.h"
#include "dominium/core_solver.h"
#include "domino/profile.h"
}

#include "launcher_caps_snapshot.h"

namespace dom {

struct LauncherCapsProviderChoice {
    std::string provider_type;
    std::string provider_id;
    std::string why;

    LauncherCapsProviderChoice();
};

struct LauncherCapsSolveResult {
    core_solver_result solver_result;
    core_caps host_caps;
    core_caps effective_caps;

    std::vector<LauncherCapsBackend> backends;
    std::vector<LauncherCapsSelection> selections;

    std::vector<std::string> platform_backends;
    std::vector<std::string> renderer_backends;
    std::string ui_backend;
    std::vector<LauncherCapsProviderChoice> provider_backends;

    std::string note;

    LauncherCapsSolveResult();
};

bool launcher_caps_solve(const dom_profile* profile,
                         LauncherCapsSolveResult& out_result,
                         std::string& out_error);

bool launcher_caps_write_effective_caps_tlv(const core_caps& caps,
                                            std::vector<unsigned char>& out_bytes);

bool launcher_caps_write_explain_tlv(const core_solver_result& result,
                                     std::vector<unsigned char>& out_bytes);

} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CAPS_SOLVER_H */
