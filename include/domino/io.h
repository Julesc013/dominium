/*
FILE: include/domino/io.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / io
RESPONSIBILITY: Defines the public contract for `io` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_IO_H
#define DOMINO_IO_H
/*
 * Domino streaming IO facade template (C89/C++98 visible).
 *
 * This header defines ABI-safe vtables for a future IO backend (files, memory,
 * packaged assets, etc). It is intentionally header-only (no implementation).
 */

#include "domino/abi.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dio_result_e {
    DIO_OK = 0,
    DIO_ERR,
    DIO_ERR_EOF,
    DIO_ERR_UNSUPPORTED
} dio_result;

/* Interface IDs (u32 constants) */
#define DIO_IID_STREAM_API_V1 ((dom_iid)0x44494F01u)

/* Reserved extension slots (placeholders) */
#define DIO_IID_EXT_RESERVED0 ((dom_iid)0x44494F80u)
#define DIO_IID_EXT_RESERVED1 ((dom_iid)0x44494F81u)

typedef enum dio_seek_origin_e {
    DIO_SEEK_SET = 0,
    DIO_SEEK_CUR,
    DIO_SEEK_END
} dio_seek_origin;

typedef enum dio_open_flags_e {
    DIO_OPEN_READ  = 1u << 0,
    DIO_OPEN_WRITE = 1u << 1,
    DIO_OPEN_TRUNC = 1u << 2
} dio_open_flags;

typedef struct dio_open_desc_v1 {
    DOM_ABI_HEADER;
    u32 flags;
} dio_open_desc_v1;

typedef struct dio_stream_api_v1 {
    DOM_ABI_HEADER;
    dom_query_interface_fn query_interface;

    void* (*open)(const char* uri, const dio_open_desc_v1* desc);
    void  (*close)(void* stream);

    dio_result (*read)(void* stream, void* buf, u32 bytes_to_read, u32* out_bytes_read);
    dio_result (*write)(void* stream, const void* buf, u32 bytes_to_write, u32* out_bytes_written);

    dio_result (*seek)(void* stream, u64 offset, dio_seek_origin origin);
    dio_result (*tell)(void* stream, u64* out_offset);
    dio_result (*size)(void* stream, u64* out_size);
} dio_stream_api_v1;

dio_result dio_get_stream_api(u32 requested_abi, dio_stream_api_v1* out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_IO_H */

