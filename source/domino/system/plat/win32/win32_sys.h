#ifndef DOMINO_WIN32_SYS_H
#define DOMINO_WIN32_SYS_H

#ifndef DOMINO_SYS_INTERNAL
#define DOMINO_SYS_INTERNAL 1
#endif

#include "domino/sys.h"

const dsys_backend_vtable* dsys_win32_get_vtable(void);
const dsys_backend_vtable* dsys_win32_headless_get_vtable(void);

#endif /* DOMINO_WIN32_SYS_H */
