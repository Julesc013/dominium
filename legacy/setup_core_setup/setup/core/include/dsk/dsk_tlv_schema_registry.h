#ifndef DSK_TLV_SCHEMA_REGISTRY_H
#define DSK_TLV_SCHEMA_REGISTRY_H

#include "dsk_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Returns non-zero on success; safe to call multiple times. */
DSK_API int dsk_register_tlv_schemas(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSK_TLV_SCHEMA_REGISTRY_H */
