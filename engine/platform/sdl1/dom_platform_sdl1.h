#ifndef DOM_PLATFORM_SDL1_H
#define DOM_PLATFORM_SDL1_H

#include "dom_core_types.h"
#include "dom_core_err.h"

#ifdef __cplusplus
extern "C" {
#endif

int  dom_platform_sdl1_init(void);
void dom_platform_sdl1_shutdown(void);

#ifdef __cplusplus
}
#endif

#endif /* DOM_PLATFORM_SDL1_H */
