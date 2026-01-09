/*
FILE: source/dominium/game/runtime/dom_ocean_provider.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/ocean_provider
RESPONSIBILITY: Ocean provider contract (stub for v1).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`.
FORBIDDEN DEPENDENCIES: OS headers; floating-point math.
*/
#ifndef DOM_OCEAN_PROVIDER_H
#define DOM_OCEAN_PROVIDER_H

#include "runtime/dom_media_provider.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_OCEAN_OK = 0,
    DOM_OCEAN_ERR = -1,
    DOM_OCEAN_INVALID_ARGUMENT = -2
};

int dom_ocean_register_stub(dom_media_registry *registry);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_OCEAN_PROVIDER_H */
