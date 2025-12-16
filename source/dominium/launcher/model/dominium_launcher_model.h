/*
FILE: source/dominium/launcher/model/dominium_launcher_model.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/model/dominium_launcher_model
RESPONSIBILITY: Defines internal contract for `dominium_launcher_model`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_LAUNCHER_MODEL_H
#define DOMINIUM_LAUNCHER_MODEL_H

#include "domino/mod.h"
#include "dominium_launcher_core.h"

typedef struct dominium_launcher_instance_view {
    char id[64];
    char label[128];
    char product_id[64];
    domino_semver product_version;
    unsigned int mod_count;
    unsigned int pack_count;
    int compatible;
} dominium_launcher_instance_view;

int dominium_launcher_build_views(dominium_launcher_context* ctx,
                                  dominium_launcher_instance_view* out,
                                  unsigned int max_count,
                                  unsigned int* out_count);

#endif
