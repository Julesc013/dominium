/*
FILE: source/domino/render/dgfx_trace.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/dgfx_trace
RESPONSIBILITY: Implements `dgfx_trace`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `include/render/**`, and C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: Single-threaded usage expected; no internal locking.
ERROR MODEL: Best-effort capture; trace may be truncated deterministically.
DETERMINISM: Trace output must be deterministic for the same IR stream.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "render/dgfx_trace.h"

#include <string.h>

enum {
    DGFX_TRACE_MAX_BYTES = 65536u,
    DGFX_TRACE_HEADER_BYTES = 24u
};

static unsigned char g_trace_buf[DGFX_TRACE_MAX_BYTES];
static u32 g_trace_size = 0u;
static u32 g_trace_events = 0u;
static u32 g_trace_flags = 0u;
static int g_trace_active = 0;

static void trace_write_u16(unsigned char *dst, u16 v)
{
    dst[0] = (unsigned char)(v & 0xffu);
    dst[1] = (unsigned char)((v >> 8u) & 0xffu);
}

static void trace_write_u32(unsigned char *dst, u32 v)
{
    dst[0] = (unsigned char)(v & 0xffu);
    dst[1] = (unsigned char)((v >> 8u) & 0xffu);
    dst[2] = (unsigned char)((v >> 16u) & 0xffu);
    dst[3] = (unsigned char)((v >> 24u) & 0xffu);
}

static void trace_write_u64(unsigned char *dst, u64 v)
{
    trace_write_u32(dst, (u32)(v & 0xffffffffull));
    trace_write_u32(dst + 4u, (u32)((v >> 32u) & 0xffffffffull));
}

static void trace_reset(void)
{
    g_trace_size = 0u;
    g_trace_events = 0u;
    g_trace_flags = 0u;
}

static void trace_append_bytes(const void *data, u32 len)
{
    if (!data || len == 0u) {
        return;
    }
    if (g_trace_size + len > DGFX_TRACE_MAX_BYTES) {
        g_trace_flags |= 1u;
        return;
    }
    memcpy(g_trace_buf + g_trace_size, data, len);
    g_trace_size += len;
}

static void trace_append_u16(u16 v)
{
    unsigned char buf[2];
    trace_write_u16(buf, v);
    trace_append_bytes(buf, 2u);
}

static void trace_append_u32(u32 v)
{
    unsigned char buf[4];
    trace_write_u32(buf, v);
    trace_append_bytes(buf, 4u);
}

static void trace_append_u64(u64 v)
{
    unsigned char buf[8];
    trace_write_u64(buf, v);
    trace_append_bytes(buf, 8u);
}

void dgfx_trace_begin(u64 frame_id)
{
    trace_reset();
    g_trace_active = 1;
    trace_append_u32(DGFX_TRACE_MAGIC);
    trace_append_u32(DGFX_TRACE_VERSION);
    trace_append_u64(frame_id);
    trace_append_u32(0u); /* event count placeholder */
    trace_append_u32(0u); /* flags placeholder */
}

void dgfx_trace_record_ir(const unsigned char *bytes, u32 len)
{
    if (!g_trace_active) {
        return;
    }
    if (len > 0xffffu) {
        len = 0xffffu;
        g_trace_flags |= 2u;
    }
    dgfx_trace_record_backend_event((u16)DGFX_TRACE_EVENT_IR_STREAM, bytes, (u16)len);
}

void dgfx_trace_record_backend_event(u16 kind, const void *payload, u16 payload_size)
{
    if (!g_trace_active) {
        return;
    }
    if (g_trace_size + 4u + payload_size > DGFX_TRACE_MAX_BYTES) {
        g_trace_flags |= 1u;
        return;
    }
    trace_append_u16(kind);
    trace_append_u16(payload_size);
    trace_append_bytes(payload, payload_size);
    g_trace_events += 1u;
}

int dgfx_trace_end(dgfx_trace_blob *out_blob)
{
    if (!g_trace_active || !out_blob) {
        return 0;
    }
    if (g_trace_size >= DGFX_TRACE_HEADER_BYTES) {
        trace_write_u32(g_trace_buf + 16u, g_trace_events);
        trace_write_u32(g_trace_buf + 20u, g_trace_flags);
    }
    out_blob->data = g_trace_buf;
    out_blob->size = g_trace_size;
    g_trace_active = 0;
    return 1;
}

u64 dgfx_trace_hash(const unsigned char *bytes, u32 len)
{
    u64 hash = 14695981039346656037ull;
    u32 i;
    if (!bytes || len == 0u) {
        return hash;
    }
    for (i = 0u; i < len; ++i) {
        hash ^= (u64)bytes[i];
        hash *= 1099511628211ull;
    }
    return hash;
}
