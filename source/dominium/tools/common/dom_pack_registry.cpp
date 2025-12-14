#include "dom_pack_registry.h"

namespace dom {
namespace tools {

DomPackRegistry::DomPackRegistry() {}

DomPackRegistry::~DomPackRegistry() {}

void DomPackRegistry::clear() {}

bool DomPackRegistry::load_from_home(const std::string &home, std::string &err) {
    (void)home;
    err = "DomPackRegistry: TODO";
    return false;
}

} // namespace tools
} // namespace dom

