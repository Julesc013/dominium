/*
FILE: include/dominium/rules/survival/shelter_proxy.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / survival rules
RESPONSIBILITY: Defines minimal shelter proxy helpers for CIV0a.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Shelter adjustments are deterministic.
*/
#ifndef DOMINIUM_RULES_SURVIVAL_SHELTER_PROXY_H
#define DOMINIUM_RULES_SURVIVAL_SHELTER_PROXY_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

u32 survival_shelter_clamp(u32 level, u32 max_level);
u32 survival_shelter_apply(u32 current_level, u32 delta, u32 max_level);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_SURVIVAL_SHELTER_PROXY_H */
