/*
FILE: source/dominium/common/dom_profile_cli.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/dom_profile_cli
RESPONSIBILITY: Defines internal contract for `dom_profile_cli`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_PROFILE_CLI_H
#define DOM_PROFILE_CLI_H

#include <cstdio>
#include <string>

extern "C" {
#include "domino/profile.h"
}

namespace dom {

struct ProfileCli {
    dom_profile profile;
    bool print_caps;
    bool print_selection;
};

void init_default_profile_cli(ProfileCli &out);
bool parse_profile_cli_args(int argc, char **argv, ProfileCli &io, std::string &err);

void print_caps(FILE *out);
int print_selection(const dom_profile &profile, FILE *out, FILE *err);

} // namespace dom

#endif /* DOM_PROFILE_CLI_H */

