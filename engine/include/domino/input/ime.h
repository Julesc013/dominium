/*
FILE: include/domino/input/ime.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / input/ime
RESPONSIBILITY: Defines the public contract for `ime` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_INPUT_IME_H
#define DOMINO_INPUT_IME_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* d_ime_event: Public type used by `ime`. */
typedef struct d_ime_event {
    char composition[128];
    char committed[128];
    u8   has_composition;
    u8   has_commit;
} d_ime_event;

/* Purpose: Init ime.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void d_ime_init(void);
/* Purpose: Shutdown ime.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void d_ime_shutdown(void);
/* Purpose: Enable ime.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void d_ime_enable(void);
/* Purpose: Disable ime.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void d_ime_disable(void);
/* Purpose: Poll ime.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
u32  d_ime_poll(d_ime_event* out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_INPUT_IME_H */
