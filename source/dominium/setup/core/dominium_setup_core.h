/*
FILE: source/dominium/setup/core/dominium_setup_core.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/core/dominium_setup_core
RESPONSIBILITY: Implements `dominium_setup_core`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_SETUP_CORE_H
#define DOMINIUM_SETUP_CORE_H

#include "domino/version.h"

typedef enum {
    DOMINIUM_SETUP_MODE_INSTALL,
    DOMINIUM_SETUP_MODE_REPAIR,
    DOMINIUM_SETUP_MODE_UNINSTALL
} dominium_setup_mode;

typedef struct dominium_setup_plan {
    dominium_setup_mode mode;

    char install_root[260];

    char product_id[64];
    domino_semver product_version;
} dominium_setup_plan;

int dominium_setup_execute(const dominium_setup_plan* plan);

#endif
