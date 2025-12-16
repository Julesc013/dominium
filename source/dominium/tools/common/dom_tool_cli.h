/*
FILE: source/dominium/tools/common/dom_tool_cli.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_cli
RESPONSIBILITY: Defines internal contract for `dom_tool_cli`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_TOOL_CLI_H
#define DOM_TOOL_CLI_H

#include <string>

namespace dom {
namespace tools {

struct DomToolCliConfig {
    std::string home;
    std::string load;
    std::string sys_backend;
    std::string gfx_backend;
    bool demo;

    DomToolCliConfig() : home(), load(), sys_backend(), gfx_backend(), demo(false) {}
};

bool parse_tool_cli(int argc, char **argv, DomToolCliConfig &out, std::string &err);

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_CLI_H */

