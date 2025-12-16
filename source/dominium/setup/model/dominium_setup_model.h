/*
FILE: source/dominium/setup/model/dominium_setup_model.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/model/dominium_setup_model
RESPONSIBILITY: Defines internal contract for `dominium_setup_model`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_SETUP_MODEL_H
#define DOMINIUM_SETUP_MODEL_H

#include "domino/version.h"

typedef struct dominium_installed_product {
    char          id[64];
    domino_semver version;
    int           content_api;
} dominium_installed_product;

int dominium_setup_list_installed(dominium_installed_product* out,
                                  unsigned int max_count,
                                  unsigned int* out_count);

#endif
