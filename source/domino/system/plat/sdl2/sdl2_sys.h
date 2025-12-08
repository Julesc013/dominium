#ifndef DOMINO_SDL2_SYS_H
#define DOMINO_SDL2_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"
#include "../dsys_internal.h"

const dsys_backend_vtable* dsys_sdl2_get_vtable(void);

#endif /* DOMINO_SDL2_SYS_H */
