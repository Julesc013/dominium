/*
FILE: source/dominium/common/dom_feature_epoch.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/dom_feature_epoch
RESPONSIBILITY: Feature epoch helpers for compatibility checks.
*/
#include "dom_feature_epoch.h"

#include "dominium/feature_epoch.h"

namespace dom {

u32 dom_feature_epoch_current(void) {
    return (u32)DOM_FEATURE_EPOCH_DEFAULT;
}

bool dom_feature_epoch_supported(u32 epoch) {
    return epoch == (u32)DOM_FEATURE_EPOCH_DEFAULT;
}

bool dom_feature_epoch_requires_migration(u32 from_epoch, u32 to_epoch) {
    return from_epoch != to_epoch;
}

} // namespace dom
