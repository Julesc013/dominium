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

/* Purpose: Game product info.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const DomProductInfo* dom_get_product_info_game(void);
/* Purpose: Launcher product info.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const DomProductInfo* dom_get_product_info_launcher(void);
/* Purpose: Setup product info.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const DomProductInfo* dom_get_product_info_setup(void);
/* Purpose: Tools product info.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const DomProductInfo* dom_get_product_info_tools(void);

/* Purpose: Family dominium detect os.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
DomOSFamily dominium_detect_os_family(void);
/* Purpose: Arch dominium detect.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
DomArch dominium_detect_arch(void);

/* Purpose: Json product info.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void dominium_print_product_info_json(const DomProductInfo* info, FILE* out);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_PRODUCT_INFO_H */
