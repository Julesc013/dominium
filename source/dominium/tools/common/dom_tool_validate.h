/*
FILE: source/dominium/tools/common/dom_tool_validate.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_validate
RESPONSIBILITY: Implements `dom_tool_validate`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_TOOL_VALIDATE_H
#define DOM_TOOL_VALIDATE_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
#include "domino/core/d_tlv.h"
}

namespace dom {
namespace tools {

/* Validates a schema payload (no outer record tag). */
bool validate_schema_payload(u32 schema_id,
                             const std::vector<unsigned char> &payload,
                             std::string *err);

/* Validates a record stream: [schema_id, len, payload]* and validates each payload. */
bool validate_record_stream(const std::vector<unsigned char> &stream,
                            std::string *err);

/* Load record stream into d_content and run relevant validators. */
bool validate_with_engine_content(const std::vector<unsigned char> &content_stream,
                                  std::string *err);

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_VALIDATE_H */

