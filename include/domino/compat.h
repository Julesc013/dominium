/*
FILE: include/domino/compat.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / compat
RESPONSIBILITY: Defines the public contract for `compat` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_COMPAT_H
#define DOMINO_COMPAT_H

#include "domino/platform.h"
#include "domino/baseline.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct DomVersionedCapability_ {
    uint32_t current;
    uint32_t min_compat;
    uint32_t max_compat;
} DomVersionedCapability;

typedef struct DomCompatProfile_ {
    DomVersionedCapability core;
    DomVersionedCapability save_format;
    DomVersionedCapability pack_format;
    DomVersionedCapability replay_format;
    DomVersionedCapability net_proto;
    DomVersionedCapability launcher_game_proto;
    DomVersionedCapability tools_game_proto;
} DomCompatProfile;

typedef enum {
    DOM_COMP_ROLE_RUNTIME,   /* game/server */
    DOM_COMP_ROLE_LAUNCHER,
    DOM_COMP_ROLE_INSTALLER,
    DOM_COMP_ROLE_TOOL,
    DOM_COMP_ROLE_SERVICE
} DomComponentRole;

typedef struct DomProductInfo_ {
    const char        *product;        /* "game", "launcher", "setup", "tools" */
    DomComponentRole   role;
    const char        *role_detail;    /* "game", "listen-server", "modcheck", etc. */

    const char        *product_version;
    const char        *core_version;
    const char        *suite_version;  /* == game version */

    DomOSFamily        os_family;
    DomArch            arch;

    DomCompatProfile   compat;
} DomProductInfo;

typedef enum {
    DOM_COMPAT_OK_FULL,
    DOM_COMPAT_OK_LIMITED,
    DOM_COMPAT_OK_READONLY,
    DOM_COMPAT_INCOMPATIBLE
} DomCompatDecision;

int dom_compat_check_core(const DomCompatProfile *a, const DomCompatProfile *b);
int dom_compat_check_format(const DomCompatProfile *a, const DomCompatProfile *b, int kind);
int dom_compat_check_net(const DomCompatProfile *a, const DomCompatProfile *b);
DomCompatDecision dom_decide_compat(const DomCompatProfile *a, const DomCompatProfile *b);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_COMPAT_H */
