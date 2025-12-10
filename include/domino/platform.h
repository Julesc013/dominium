#ifndef DOMINO_PLATFORM_H
#define DOMINO_PLATFORM_H

#ifdef __cplusplus
extern "C" {
#endif

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

/* Legacy backend selector preserved for compatibility */
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
