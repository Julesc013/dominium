#include "dom_compat.h"

namespace dom {

CompatResult evaluate_compat(
    const ProductInfo &prod,
    const InstanceInfo &inst
) {
    if (prod.core_version < inst.core_version) {
        return COMPAT_INCOMPATIBLE;
    }
    if (prod.suite_version < inst.suite_version) {
        return COMPAT_READONLY;
    }
    if (prod.suite_version > inst.suite_version) {
        /* Assume limited forward compatibility until declared otherwise. */
        return COMPAT_LIMITED;
    }

    /* TODO: evaluate declared compat profile once instances start exposing it. */
    (void)prod.product;
    (void)prod.role_detail;
    (void)prod.product_version;

    return COMPAT_OK;
}

} // namespace dom
