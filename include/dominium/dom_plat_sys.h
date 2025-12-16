/*
FILE: include/dominium/dom_plat_sys.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / dom_plat_sys
RESPONSIBILITY: Defines the public contract for `dom_plat_sys` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_DOM_PLAT_SYS_H
#define DOMINIUM_DOM_PLAT_SYS_H

/* System-level platform abstraction: no UI or rendering.
 * All OS interaction above the C runtime should go through this vtable.
 */

#include <stddef.h>
#include "domino/baseline.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_SYS_API_VERSION 1u

struct dom_sys_vtable {
    uint32_t api_version;

    int      (*init)(void);
    void     (*shutdown)(void);

    /* filesystem roots */
    int      (*get_program_root)(char* buf, size_t cap);
    int      (*get_data_root)(char* buf, size_t cap);
    int      (*get_state_root)(char* buf, size_t cap);

    /* filesystem helpers */
    int      (*fs_mkdir_p)(const char* path);
    int      (*fs_exists)(const char* path);
    int      (*fs_remove)(const char* path);

    /* process / IPC */
    int      (*spawn_process)(const char* path,
                              char* const argv[],
                              int flags,
                              int* out_exit_code);

    /* timing */
    uint64_t (*ticks)(void);   /* monotonic */
    double   (*seconds)(void); /* wall-clock; ok to use doubles outside sim core */
};

/* Select the best available system vtable for the current platform. */
const struct dom_sys_vtable* dom_plat_sys_choose_best(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_DOM_PLAT_SYS_H */
