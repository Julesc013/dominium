/*
FILE: source/dominium/common/dom_feature_epoch.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/dom_feature_epoch
RESPONSIBILITY: Feature epoch helpers for compatibility checks.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: OS-specific headers; no exceptions.
*/
#ifndef DOM_FEATURE_EPOCH_COMMON_H
#define DOM_FEATURE_EPOCH_COMMON_H

extern "C" {
#include "domino/core/types.h"
}

namespace dom {

u32 dom_feature_epoch_current(void);
bool dom_feature_epoch_supported(u32 epoch);
bool dom_feature_epoch_requires_migration(u32 from_epoch, u32 to_epoch);

} // namespace dom

#endif /* DOM_FEATURE_EPOCH_COMMON_H */
