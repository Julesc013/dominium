/*
FILE: tools/validate/policy_validation.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / validate
RESPONSIBILITY: Policy documentation validation for FINAL0 governance.
ALLOWED DEPENDENCIES: tools/validation helpers and C++98 standard headers.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Reported via ValidationReport; no exceptions.
DETERMINISM: Deterministic checks for required policy docs.
*/
#ifndef DOMINIUM_TOOLS_VALIDATE_POLICY_VALIDATION_H
#define DOMINIUM_TOOLS_VALIDATE_POLICY_VALIDATION_H

#include "validation/validator_common.h"

namespace dom {
namespace validation {

void validate_policy_docs(const ValidationContext& ctx, ValidationReport& report);

} /* namespace validation */
} /* namespace dom */

#endif /* DOMINIUM_TOOLS_VALIDATE_POLICY_VALIDATION_H */
