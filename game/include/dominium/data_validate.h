/*
FILE: include/dominium/data_validate.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / data_validate
RESPONSIBILITY: Game-facing wrapper for shared data validation.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Validation report + result enum; no exceptions.
DETERMINISM: Validation is deterministic and side-effect free.
*/
#ifndef DOMINIUM_DATA_VALIDATE_H
#define DOMINIUM_DATA_VALIDATE_H

#include "domino/io/data_validate.h"

#ifdef __cplusplus
extern "C" {
#endif

dom_validation_result dominium_data_validate_tlv(const unsigned char* tlv,
                                                 u32 tlv_len,
                                                 u64 schema_id,
                                                 dom_schema_version version,
                                                 const char* source_path,
                                                 dom_validation_report* report,
                                                 const dom_data_validate_options* options);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_DATA_VALIDATE_H */
