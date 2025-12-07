#ifndef DOMINO_MOD_H
#define DOMINO_MOD_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dm_mod_context dm_mod_context;

struct dm_mod_context {
    uint32_t placeholder;
};

dm_mod_context* dm_mod_create(void);
void            dm_mod_destroy(dm_mod_context* ctx);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_MOD_H */
