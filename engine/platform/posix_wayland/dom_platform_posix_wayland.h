#ifndef DOM_PLATFORM_POSIX_WAYLAND_H
#define DOM_PLATFORM_POSIX_WAYLAND_H

#include "dom_core_types.h"
#include "dom_core_err.h"

#ifdef __cplusplus
extern "C" {
#endif

int  dom_platform_posix_wayland_init(void);
void dom_platform_posix_wayland_shutdown(void);

#ifdef __cplusplus
}
#endif

#endif /* DOM_PLATFORM_POSIX_WAYLAND_H */
