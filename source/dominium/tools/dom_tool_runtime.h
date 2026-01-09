/*
FILE: source/dominium/tools/dom_tool_runtime.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/runtime
RESPONSIBILITY: Tool runtime harness enforcing launcher handshake and path rules.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C++98 STL.
FORBIDDEN DEPENDENCIES: Direct platform probes that bypass launcher roots.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/false; no exceptions.
DETERMINISM: N/A (tool runtime; must not affect sim state).
VERSIONING / ABI / DATA FORMAT NOTES: Internal contract only.
*/
#ifndef DOM_TOOL_RUNTIME_H
#define DOM_TOOL_RUNTIME_H

#include <string>

extern "C" {
#include "domino/core/types.h"
}

#include "runtime/dom_game_handshake.h"
#include "runtime/dom_game_paths.h"
#include "runtime/dom_universe_bundle.h"

namespace dom {
namespace tools {

enum DomToolRuntimeRefusalCode {
    DOM_TOOL_REFUSAL_OK = 0u,
    DOM_TOOL_REFUSAL_HANDSHAKE_MISSING = 3001u,
    DOM_TOOL_REFUSAL_HANDSHAKE_INVALID = 3002u,
    DOM_TOOL_REFUSAL_SIM_CAPS_MISMATCH = 3003u,
    DOM_TOOL_REFUSAL_PATH = 3004u,
    DOM_TOOL_REFUSAL_IDENTITY_MISMATCH = 3005u,
    DOM_TOOL_REFUSAL_IO = 3006u
};

struct DomToolRuntime {
    std::string tool_id;
    DomGameHandshake handshake;
    DomGamePaths paths;
    bool has_handshake;
    bool edit_mode;
    u32 last_refusal;
    std::string last_error;

    DomToolRuntime();
};

bool tool_runtime_init(DomToolRuntime &rt,
                       const std::string &tool_id,
                       const std::string &handshake_rel,
                       u32 path_flags,
                       bool edit_mode,
                       std::string *err);

bool tool_runtime_validate_identity(DomToolRuntime &rt,
                                    std::string *err);

int tool_runtime_load_universe(DomToolRuntime &rt,
                               const DomGamePathRef &bundle_ref,
                               dom_universe_bundle **out_bundle,
                               dom_universe_bundle_identity *out_id,
                               std::string *err);

bool tool_runtime_emit_output(DomToolRuntime &rt,
                              const std::string &name,
                              const unsigned char *data,
                              size_t size,
                              std::string *err);

bool tool_runtime_refuse(DomToolRuntime &rt,
                         u32 code,
                         const std::string &message);

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_RUNTIME_H */
