#ifndef DOM_SETUP_OPS_H
#define DOM_SETUP_OPS_H

#include <string>

#include "dom_paths.h"

namespace dom {

bool setup_install(const Paths &paths, const std::string &source);
bool setup_repair(const Paths &paths, const std::string &product);
bool setup_uninstall(const Paths &paths, const std::string &product);
bool setup_import(const Paths &paths, const std::string &source);
bool setup_gc(const Paths &paths);
bool setup_validate(const Paths &paths, const std::string &target);

} // namespace dom

#endif
