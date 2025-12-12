#ifndef DOM_COMPAT_H
#define DOM_COMPAT_H

#include <string>
#include "dom_instance.h"

namespace dom {

enum CompatResult {
    COMPAT_OK = 0,
    COMPAT_LIMITED,
    COMPAT_READONLY,
    COMPAT_INCOMPATIBLE
};

struct ProductInfo {
    std::string product;       /* "game", "launcher", "setup", "tool" */
    std::string role_detail;   /* "client", "server", "headless", etc. */

    unsigned product_version;
    unsigned core_version;
    unsigned suite_version;
};

CompatResult evaluate_compat(
    const ProductInfo &prod,
    const InstanceInfo &inst
);

} // namespace dom

#endif
