/*
FILE: source/dominium/tools/common/dom_tool_ops.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_ops
RESPONSIBILITY: Defines internal contract for `dom_tool_ops`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_TOOL_OPS_H
#define DOM_TOOL_OPS_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

namespace dom {
namespace tools {

bool load_tlv_file(const std::string &path,
                   std::vector<unsigned char> &out,
                   std::string *err);

bool save_tlv_file(const std::string &path,
                   const std::vector<unsigned char> &data,
                   std::string *err);

bool validate_tlv_against_schema(u32 schema_id,
                                 const std::vector<unsigned char> &payload,
                                 std::string *err);

/* Preview hooks (stubs for now; rendered via dgfx/d_view by tool UIs). */
bool preview_entity(u32 schema_id, u32 entity_id, std::string *err);
bool preview_world_slice(int x, int y, int z, int radius, std::string *err);
bool preview_process_flow(u32 process_id, std::string *err);

/* Spawn engine (or other validators) in a separate process for validation. */
bool open_in_engine_for_validation(const std::string &exe_path,
                                   const std::vector<std::string> &args,
                                   std::string *err);

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_OPS_H */

