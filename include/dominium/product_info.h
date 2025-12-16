/*
FILE: include/dominium/product_info.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / product_info
RESPONSIBILITY: Defines the public contract for `product_info` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_PRODUCT_INFO_H
#define DOMINIUM_PRODUCT_INFO_H

#include "domino/compat.h"
#include <stdio.h>

#define DMN_EMPTY_COMPAT_PROFILE \
    { {0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0} }

#ifdef __cplusplus
extern "C" {
#endif

const DomProductInfo* dom_get_product_info_game(void);
const DomProductInfo* dom_get_product_info_launcher(void);
const DomProductInfo* dom_get_product_info_setup(void);
const DomProductInfo* dom_get_product_info_tools(void);

DomOSFamily dominium_detect_os_family(void);
DomArch dominium_detect_arch(void);

void dominium_print_product_info_json(const DomProductInfo* info, FILE* out);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_PRODUCT_INFO_H */
