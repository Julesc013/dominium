/*
FILE: source/dominium/tools/coredata_validate/coredata_validate_checks.h
MODULE: Dominium
PURPOSE: Coredata validator checks for authoring data and compiled packs.
*/
#ifndef DOMINIUM_TOOLS_COREDATA_VALIDATE_CHECKS_H
#define DOMINIUM_TOOLS_COREDATA_VALIDATE_CHECKS_H

#include <vector>

#include "coredata_validate_load.h"
#include "coredata_validate_report.h"

namespace dom {
namespace tools {

void coredata_validate_report_errors(const std::vector<CoredataError> &errors,
                                     CoredataValidationReport &report);

void coredata_validate_authoring_policy(const CoredataData &data,
                                        CoredataValidationReport &report);

void coredata_validate_pack_checks(const CoredataPackView &pack,
                                   const CoredataManifestView *manifest,
                                   CoredataValidationReport &report);

} // namespace tools
} // namespace dom

#endif /* DOMINIUM_TOOLS_COREDATA_VALIDATE_CHECKS_H */
