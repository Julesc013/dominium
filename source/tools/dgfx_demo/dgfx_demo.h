#ifndef DOMINIUM_DGFX_DEMO_H
#define DOMINIUM_DGFX_DEMO_H

#include "domino/gfx.h"

/* Run a simple, blocking demo loop for a given backend.
   Returns 0 on success, non-zero on failure. */
int dgfx_run_demo(dgfx_backend_t backend);

/* Optional single-frame helper. */
int dgfx_run_demo_single_frame(dgfx_backend_t backend);

#endif /* DOMINIUM_DGFX_DEMO_H */
