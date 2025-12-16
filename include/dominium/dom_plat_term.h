/*
FILE: include/dominium/dom_plat_term.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / dom_plat_term
RESPONSIBILITY: Defines the public contract for `dom_plat_term` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_DOM_PLAT_TERM_H
#define DOMINIUM_DOM_PLAT_TERM_H

/* Terminal (CLI/TUI) abstraction. */

#include <stddef.h>
#include "domino/baseline.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_TERM_API_VERSION 1u

struct dom_sys_vtable; /* fwd */

struct dom_term_vtable {
    uint32_t api_version;

    int  (*attach)(void);   /* bind to stdin/stdout/tty */
/* Purpose: API entry point for `dom_plat_term`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    void (*detach)(void);

/* Purpose: API entry point for `dom_plat_term`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    int  (*write)(const char* s, size_t n);
/* Purpose: API entry point for `dom_plat_term`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    int  (*read_line)(char* buf, size_t cap);

/* Purpose: API entry point for `dom_plat_term`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    int  (*enter_alt_screen)(void);
/* Purpose: API entry point for `dom_plat_term`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    void (*leave_alt_screen)(void);

/* Purpose: API entry point for `dom_plat_term`.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
    void (*set_cursor_pos)(int x, int y);
    void (*set_attr)(uint32_t attr_flags); /* attr flags TBD */
};

/* Purpose: Probe dom plat term.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const struct dom_term_vtable* dom_plat_term_probe(const struct dom_sys_vtable* sys);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_DOM_PLAT_TERM_H */
