/*
FILE: source/dominium/tools/coredata_compile/coredata_validate.h
MODULE: Dominium
PURPOSE: Coredata compiler validation (bounds + references).
*/
#ifndef DOMINIUM_TOOLS_COREDATA_VALIDATE_H
#define DOMINIUM_TOOLS_COREDATA_VALIDATE_H

#include <string>
#include <vector>

#include "coredata_load.h"

namespace dom {
namespace tools {

bool coredata_validate(const CoredataData &data,
                       std::vector<CoredataError> &errors);

} // namespace tools
} // namespace dom

#endif /* DOMINIUM_TOOLS_COREDATA_VALIDATE_H */
