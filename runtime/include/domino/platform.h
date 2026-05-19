/*
FILE: include/domino/platform.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / platform
RESPONSIBILITY: Defines the public contract for `platform` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_PLATFORM_H
#define DOMINO_PLATFORM_H

#ifdef __cplusplus
extern "C" {
#endif

/* Purpose: Coarse OS-family classification for platform selection and reporting.
 *
 * Notes:
 * - This enum is distinct from repository-manifest OS families (see `domino/pkg/repo.h`).
 */
typedef enum DomOSFamily_ {
    DOM_OSFAM_WIN_NT,
    DOM_OSFAM_WIN_9X,
    DOM_OSFAM_WIN_3X,
    DOM_OSFAM_DOS,
    DOM_OSFAM_MAC_OS_X,
    DOM_OSFAM_MAC_CLASSIC,
    DOM_OSFAM_LINUX,
    DOM_OSFAM_ANDROID,
    DOM_OSFAM_CPM,
    DOM_OSFAM_WEB
} DomOSFamily;

/* Purpose: Coarse CPU/VM architecture classification for platform selection and reporting. */
typedef enum DomArch_ {
    DOM_ARCH_X86_16,
    DOM_ARCH_X86_32,
    DOM_ARCH_X86_64,
    DOM_ARCH_ARM_32,
    DOM_ARCH_ARM_64,
    DOM_ARCH_M68K_32,
    DOM_ARCH_PPC_32,
    DOM_ARCH_PPC_64,
    DOM_ARCH_Z80_8,
    DOM_ARCH_WASM_32,
    DOM_ARCH_WASM_64
} DomArch;

/* Purpose: Legacy platform-backend selector preserved for compatibility.
 *
 * Notes:
 * - Values correspond to historical backend directories and are not an exhaustive modern platform list.
 */
typedef enum dom_platform_e {
    DOM_PLATFORM_WIN32 = 0,      /* /src/platform/win32/ */
    DOM_PLATFORM_MACOSX,         /* /src/platform/cocoa/ */
    DOM_PLATFORM_POSIX_HEADLESS, /* /src/platform/shared/posix_headless/ */
    DOM_PLATFORM_POSIX_X11,      /* /src/platform/x11/ */
    DOM_PLATFORM_POSIX_WAYLAND,  /* /src/platform/wayland/ */
    DOM_PLATFORM_SDL1,           /* /src/platform/sdl1/ */
    DOM_PLATFORM_SDL2            /* /src/platform/sdl2/ */
} dom_platform;

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_PLATFORM_H */
