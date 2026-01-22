/*
FILE: include/domino/system/d_system.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / system/d_system
RESPONSIBILITY: Defines the public contract for `d_system` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Minimal Domino system wrapper (C89). */
#ifndef D_SYSTEM_H
#define D_SYSTEM_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Purpose: Init system.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int d_system_init(const char *backend_name);
/* Purpose: Shutdown system.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void d_system_shutdown(void);
/* Purpose: Pump events.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int  d_system_pump_events(void);
/* Purpose: Sleep ms.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void d_system_sleep_ms(u32 ms);
/* Purpose: Process spawn.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int  d_system_process_spawn(const char *path, const char *args);

/* Returns a native window handle for the current platform (e.g. HWND on Win32),
 * or NULL when no window exists (e.g. headless).
 */
void* d_system_get_native_window_handle(void);
/* Purpose: Set native window handle for presentation (external window ownership).
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void d_system_set_native_window_handle(void* handle);

/* Purpose: Present framebuffer.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int d_system_present_framebuffer(
    const void *pixels,
    i32         width,
    i32         height,
    i32         pitch_bytes
);

#ifdef __cplusplus
}
#endif

#endif /* D_SYSTEM_H */
