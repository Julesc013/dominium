/*
FILE: tools/validation/validator_reports.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / validation
RESPONSIBILITY: Formats validation reports as JSON and text.
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Report output is deterministic for a given report.
*/
#ifndef DOMINIUM_TOOLS_VALIDATION_REPORTS_H
#define DOMINIUM_TOOLS_VALIDATION_REPORTS_H

#include <string>

#include "validator_common.h"

namespace dom {
namespace validation {

std::string report_to_json(const ValidationReport& report);
std::string report_to_text(const ValidationReport& report);

} /* namespace validation */
} /* namespace dom */

#endif /* DOMINIUM_TOOLS_VALIDATION_REPORTS_H */
