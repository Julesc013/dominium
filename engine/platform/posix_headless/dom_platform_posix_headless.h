#ifndef DOM_PLATFORM_POSIX_HEADLESS_H
#define DOM_PLATFORM_POSIX_HEADLESS_H

#include "dom_core_types.h"
#include "dom_core_err.h"

#ifdef __cplusplus
extern "C" {
#endif

/* CLI-only platform stub: no window system. */
int  dom_platform_posix_headless_init(void);
void dom_platform_posix_headless_shutdown(void);

#ifdef __cplusplus
}
#endif

#endif /* DOM_PLATFORM_POSIX_HEADLESS_H */
