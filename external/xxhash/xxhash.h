#ifndef DOMINIUM_EXTERNAL_XXHASH_H
#define DOMINIUM_EXTERNAL_XXHASH_H

#include <stddef.h>
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

u64 dom_xxhash64(const void* data, size_t len, u64 seed);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_EXTERNAL_XXHASH_H */

