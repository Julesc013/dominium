#ifndef DOMINIUM_SOFT_BLIT_H
#define DOMINIUM_SOFT_BLIT_H

#include "soft_gfx.h"

typedef void (*soft_present_fn)(
    void* native_window,
    const soft_framebuffer* fb
);

/* Must be set up by platform integration code at startup */
void soft_blit_set_present_callback(soft_present_fn fn);
soft_present_fn soft_blit_get_present_callback(void);

#endif /* DOMINIUM_SOFT_BLIT_H */
