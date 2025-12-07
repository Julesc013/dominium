#ifndef DOM_PLATFORM_POSIX_X11_H
#define DOM_PLATFORM_POSIX_X11_H

#include "dom_core_types.h"
#include "dom_core_err.h"

#ifdef __cplusplus
extern "C" {
#endif

int  dom_platform_posix_x11_init(void);
void dom_platform_posix_x11_shutdown(void);

#ifdef __cplusplus
}
#endif

#endif /* DOM_PLATFORM_POSIX_X11_H */
