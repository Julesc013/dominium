/* Transport subsystem public interface (C89). */
#ifndef D_TRANS_H
#define D_TRANS_H

#include "trans/d_trans_spline.h"
#include "trans/d_trans_mover.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Subsystem registration hook (called once at startup). */
void d_trans_register_subsystem(void);

/* Debug validator hook. */
int d_trans_validate(const d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_TRANS_H */
