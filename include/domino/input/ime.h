#ifndef DOMINO_INPUT_IME_H
#define DOMINO_INPUT_IME_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct d_ime_event {
    char composition[128];
    char committed[128];
    u8   has_composition;
    u8   has_commit;
} d_ime_event;

void d_ime_init(void);
void d_ime_shutdown(void);
void d_ime_enable(void);
void d_ime_disable(void);
u32  d_ime_poll(d_ime_event* out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_INPUT_IME_H */
