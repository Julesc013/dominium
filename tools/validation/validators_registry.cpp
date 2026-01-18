/*
FILE: tools/validation/validators_registry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / validation
RESPONSIBILITY: Registers and executes validation passes for GOV0.
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Validation order is deterministic.
*/
#include "validators_registry.h"

namespace dom {
namespace validation {

void run_all_validators(const ValidationContext& ctx, ValidationReport& report) {
    (void)ctx;
    (void)report;
}

} /* namespace validation */
} /* namespace dom */
