/*
FILE: include/dominium/dom_rend.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / dom_rend
RESPONSIBILITY: Defines the public contract for `dom_rend` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_DOM_REND_H
#define DOMINIUM_DOM_REND_H

/* Renderer abstraction used by the game. Launcher/tools must not include this. */

#include "domino/baseline.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_REND_API_VERSION 1u

/* dom_rend_device: Public type used by `dom_rend`. */
typedef struct dom_rend_device dom_rend_device;

struct dom_rend_desc {
    int width;
    int height;
    int fullscreen;
};

struct dom_rend_vtable {
    uint32_t api_version;

    dom_rend_device* (*create_device)(const struct dom_rend_desc*);
/* Purpose: API entry point for `dom_rend`.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
    void             (*destroy_device)(dom_rend_device*);

/* Purpose: API entry point for `dom_rend`.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
    void (*begin_frame)(dom_rend_device*);
/* Purpose: API entry point for `dom_rend`.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
    void (*end_frame)(dom_rend_device*);

/* Purpose: API entry point for `dom_rend`.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
    void (*clear)(dom_rend_device*, uint32_t rgba);
/* Purpose: API entry point for `dom_rend`.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
    void (*draw_rect)(dom_rend_device*, int x, int y, int w, int h, uint32_t rgba);
};

/* Choose best available renderer (software baseline). */
const struct dom_rend_vtable* dom_rend_choose_best(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_DOM_REND_H */
