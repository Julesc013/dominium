/*
FILE: tools/validation/validators_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / validation
RESPONSIBILITY: Registers and executes validation passes for GOV0.
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Validation order is deterministic.
*/
#ifndef DOMINIUM_TOOLS_VALIDATION_REGISTRY_H
#define DOMINIUM_TOOLS_VALIDATION_REGISTRY_H

#include "validator_common.h"

namespace dom {
namespace validation {

void run_all_validators(const ValidationContext& ctx, ValidationReport& report);

} /* namespace validation */
} /* namespace dom */

#endif /* DOMINIUM_TOOLS_VALIDATION_REGISTRY_H */
