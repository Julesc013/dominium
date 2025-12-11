/* Minimal TLV blob wrapper (public header). */
#ifndef D_TLV_H
#define D_TLV_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct d_tlv_blob {
    unsigned char *ptr;
    u32            len;
} d_tlv_blob;

#ifdef __cplusplus
}
#endif

#endif /* D_TLV_H */
