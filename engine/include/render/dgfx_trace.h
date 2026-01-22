/*
FILE: include/render/dgfx_trace.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / render/dgfx_trace
RESPONSIBILITY: Defines the public contract for `dgfx_trace`; does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: Single-threaded usage expected; no internal locking.
ERROR MODEL: Best-effort capture; trace may be truncated deterministically.
DETERMINISM: Trace output must be deterministic for the same IR stream.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DGFX_TRACE_H
#define DGFX_TRACE_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DGFX_TRACE_MAGIC 0x52544744u /* 'DGTR' */
#define DGFX_TRACE_VERSION 1u

enum {
    DGFX_TRACE_EVENT_FRAME_BEGIN = 1,
    DGFX_TRACE_EVENT_FRAME_END = 2,
    DGFX_TRACE_EVENT_IR_STREAM = 3,
    DGFX_TRACE_EVENT_BACKEND_SUBMIT_BEGIN = 4,
    DGFX_TRACE_EVENT_BACKEND_SUBMIT_END = 5,
    DGFX_TRACE_EVENT_BACKEND_PRESENT_BEGIN = 6,
    DGFX_TRACE_EVENT_BACKEND_PRESENT_END = 7,
    DGFX_TRACE_EVENT_ACCEPTED_COUNT = 8,
    DGFX_TRACE_EVENT_REJECTED_COUNT = 9,
    DGFX_TRACE_EVENT_PRIMITIVE_COUNT = 10,
    DGFX_TRACE_EVENT_BBOX = 11,
    DGFX_TRACE_EVENT_TEXT_GLYPH_COUNT = 12,
    DGFX_TRACE_EVENT_STALL_MS = 13
};

typedef struct dgfx_trace_blob {
    const unsigned char *data;
    u32 size;
} dgfx_trace_blob;

void dgfx_trace_begin(u64 frame_id);
void dgfx_trace_record_ir(const unsigned char *bytes, u32 len);
void dgfx_trace_record_backend_event(u16 kind, const void *payload, u16 payload_size);
int  dgfx_trace_end(dgfx_trace_blob *out_blob);

u64 dgfx_trace_hash(const unsigned char *bytes, u32 len);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DGFX_TRACE_H */
