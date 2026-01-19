/*
FILE: tools/validate/tool_validation.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / validate
RESPONSIBILITY: Tooling inventory validation hooks for GOV0.
ALLOWED DEPENDENCIES: tools/validation helpers and C++98 standard headers.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Reported via ValidationReport; no exceptions.
DETERMINISM: Deterministic traversal and reporting order.
*/
#ifndef DOMINIUM_TOOLS_VALIDATE_TOOL_VALIDATION_H
#define DOMINIUM_TOOLS_VALIDATE_TOOL_VALIDATION_H

#include "validation/validator_common.h"

namespace dom {
namespace validation {

void validate_tooling_inventory(const ValidationContext& ctx, ValidationReport& report);

} /* namespace validation */
} /* namespace dom */

#endif /* DOMINIUM_TOOLS_VALIDATE_TOOL_VALIDATION_H */
