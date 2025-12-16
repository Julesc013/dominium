/*
FILE: include/dominium/launcher_ext_api.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / launcher_ext_api
RESPONSIBILITY: Defines the public contract for `launcher_ext_api` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_LAUNCHER_EXT_API_H
#define DOMINIUM_LAUNCHER_EXT_API_H

#include "domino/mod.h"

struct dominium_launcher_context;

/* Query instances */
int launcher_ext_list_instances(struct dominium_launcher_context* ctx,
                                domino_instance_desc* out,
                                unsigned int max_count,
                                unsigned int* out_count);

/* Launch an instance */
int launcher_ext_run_instance(struct dominium_launcher_context* ctx,
                              const char* instance_id);

/* Query launcher-target packages */
int launcher_ext_list_launcher_packages(struct dominium_launcher_context* ctx,
                                        domino_package_desc* out,
                                        unsigned int max_count,
                                        unsigned int* out_count);

#endif /* DOMINIUM_LAUNCHER_EXT_API_H */
