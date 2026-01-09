/*
FILE: source/dominium/tools/validator/validator_checks.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/validator
RESPONSIBILITY: Deterministic validation checks for universe bundles.
*/
#ifndef DOM_VALIDATOR_CHECKS_H
#define DOM_VALIDATOR_CHECKS_H

#include <string>

#include "runtime/dom_universe_bundle.h"
#include "common/dom_tool_diagnostics.h"

namespace dom {
namespace tools {

bool validator_check_bundle(dom_universe_bundle *bundle,
                            DomToolDiagnostics &diag,
                            dom_universe_bundle_identity *out_id);

std::string validator_report_json(const DomToolDiagnostics &diag,
                                  const dom_universe_bundle_identity *id,
                                  bool ok);

} // namespace tools
} // namespace dom

#endif /* DOM_VALIDATOR_CHECKS_H */
