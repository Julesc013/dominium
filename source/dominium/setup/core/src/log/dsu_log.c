/*
FILE: source/dominium/setup/core/src/log/dsu_log.c
MODULE: Dominium Setup
PURPOSE: Audit log implementation (in-memory + deterministic binary export/import).
*/
#include "../../include/dsu/dsu_log.h"

#include "../dsu_ctx_internal.h"
#include "../util/dsu_util_internal.h"

#include <string.h>
#include <time.h>

#define DSU_LOG_MAGIC_0 'D'
#define DSU_LOG_MAGIC_1 'S'
#define DSU_LOG_MAGIC_2 'U'
#define DSU_LOG_MAGIC_3 'L'
#define DSU_LOG_FORMAT_VERSION 1u

typedef struct dsu_log_event_t {
    dsu_u32 event_id;
    dsu_u8 severity;
    dsu_u8 category;
    dsu_u16 reserved;
    dsu_u32 timestamp;
    char *message;
} dsu_log_event_t;

struct dsu_log {
    dsu_u32 count;
    dsu_u32 cap;
    dsu_log_event_t *events;
};

static void dsu__log_event_free(dsu_log_event_t *ev) {
    if (!ev) {
        return;
    }
    dsu__free(ev->message);
    ev->message = NULL;
}

dsu_status_t dsu_log_create(dsu_ctx_t *ctx, dsu_log_t **out_log) {
    dsu_log_t *log;
    (void)ctx;
    if (!out_log) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_log = NULL;
    log = (dsu_log_t *)dsu__malloc((dsu_u32)sizeof(*log));
    if (!log) {
        return DSU_STATUS_IO_ERROR;
    }
    memset(log, 0, sizeof(*log));
    *out_log = log;
    return DSU_STATUS_SUCCESS;
}

void dsu_log_destroy(dsu_ctx_t *ctx, dsu_log_t *log) {
    dsu_u32 i;
    (void)ctx;
    if (!log) {
        return;
    }
    for (i = 0u; i < log->count; ++i) {
        dsu__log_event_free(&log->events[i]);
    }
    dsu__free(log->events);
    log->events = NULL;
    log->count = 0u;
    log->cap = 0u;
    dsu__free(log);
}

dsu_status_t dsu_log_reset(dsu_ctx_t *ctx, dsu_log_t *log) {
    dsu_u32 i;
    (void)ctx;
    if (!log) {
        return DSU_STATUS_INVALID_ARGS;
    }
    for (i = 0u; i < log->count; ++i) {
        dsu__log_event_free(&log->events[i]);
    }
    log->count = 0u;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__log_ensure_capacity(dsu_log_t *log, dsu_u32 needed) {
    dsu_u32 new_cap;
    dsu_log_event_t *p;
    if (needed <= log->cap) {
        return DSU_STATUS_SUCCESS;
    }
    new_cap = (log->cap == 0u) ? 8u : log->cap;
    while (new_cap < needed) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = needed;
            break;
        }
        new_cap *= 2u;
    }
    p = (dsu_log_event_t *)dsu__realloc(log->events, (dsu_u32)(new_cap * (dsu_u32)sizeof(*p)));
    if (!p) {
        return DSU_STATUS_IO_ERROR;
    }
    if (new_cap > log->cap) {
        memset(p + log->cap, 0, (size_t)(new_cap - log->cap) * sizeof(*p));
    }
    log->events = p;
    log->cap = new_cap;
    return DSU_STATUS_SUCCESS;
}

static dsu_u32 dsu__ctx_timestamp(const dsu_ctx_t *ctx) {
    time_t t;
    if (!ctx) {
        return 0u;
    }
    if ((ctx->config.flags & DSU_CONFIG_FLAG_DETERMINISTIC) != 0u) {
        return 0u;
    }
    t = time(NULL);
    if (t <= 0) {
        return 0u;
    }
    if ((unsigned long)t > 0xFFFFFFFFul) {
        return 0u;
    }
    return (dsu_u32)t;
}

dsu_status_t dsu_log_emit(dsu_ctx_t *ctx,
                         dsu_log_t *log,
                         dsu_u32 event_id,
                         dsu_u8 severity,
                         dsu_u8 category,
                         const char *message) {
    dsu_status_t st;
    dsu_log_event_t *ev;
    char *msg_copy;
    dsu_u32 timestamp;

    if (!ctx || !log || !message) {
        return DSU_STATUS_INVALID_ARGS;
    }

    timestamp = dsu__ctx_timestamp(ctx);
    msg_copy = dsu__strdup(message);
    if (!msg_copy) {
        return DSU_STATUS_IO_ERROR;
    }

    st = dsu__log_ensure_capacity(log, log->count + 1u);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(msg_copy);
        return st;
    }

    ev = &log->events[log->count];
    memset(ev, 0, sizeof(*ev));
    ev->event_id = event_id;
    ev->severity = severity;
    ev->category = category;
    ev->reserved = 0u;
    ev->timestamp = timestamp;
    ev->message = msg_copy;
    log->count += 1u;

    if (ctx->callbacks.log) {
        ctx->callbacks.log(ctx->callbacks_user,
                           event_id,
                           severity,
                           category,
                           timestamp,
                           message);
    }
    return DSU_STATUS_SUCCESS;
}

dsu_u32 dsu_log_event_count(const dsu_log_t *log) {
    if (!log) {
        return 0u;
    }
    return log->count;
}

dsu_status_t dsu_log_event_get(const dsu_log_t *log,
                              dsu_u32 index,
                              dsu_u32 *out_event_id,
                              dsu_u8 *out_severity,
                              dsu_u8 *out_category,
                              dsu_u32 *out_timestamp,
                              const char **out_message) {
    const dsu_log_event_t *ev;
    if (!log) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (index >= log->count) {
        return DSU_STATUS_INVALID_ARGS;
    }
    ev = &log->events[index];
    if (out_event_id) {
        *out_event_id = ev->event_id;
    }
    if (out_severity) {
        *out_severity = ev->severity;
    }
    if (out_category) {
        *out_category = ev->category;
    }
    if (out_timestamp) {
        *out_timestamp = ev->timestamp;
    }
    if (out_message) {
        *out_message = ev->message ? ev->message : "";
    }
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_log_write_file(dsu_ctx_t *ctx, const dsu_log_t *log, const char *path) {
    dsu_blob_t payload;
    dsu_blob_t file_bytes;
    dsu_u8 magic[4];
    dsu_u32 i;
    dsu_status_t st;

    if (!ctx || !log || !path) {
        return DSU_STATUS_INVALID_ARGS;
    }

    dsu__blob_init(&payload);
    dsu__blob_init(&file_bytes);

    /* payload: event_count u32, flags u32, then events. */
    st = dsu__blob_put_u32le(&payload, log->count);
    if (st == DSU_STATUS_SUCCESS) {
        st = dsu__blob_put_u32le(&payload, ctx->config.flags);
    }
    for (i = 0u; st == DSU_STATUS_SUCCESS && i < log->count; ++i) {
        const dsu_log_event_t *ev = &log->events[i];
        dsu_u32 msg_len = dsu__strlen(ev->message ? ev->message : "");

        st = dsu__blob_put_u32le(&payload, ev->event_id);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u8(&payload, ev->severity);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u8(&payload, ev->category);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u16le(&payload, 0u);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u32le(&payload, ev->timestamp);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_put_u32le(&payload, msg_len);
        if (st != DSU_STATUS_SUCCESS) break;
        if (msg_len) {
            st = dsu__blob_append(&payload, ev->message, msg_len);
            if (st != DSU_STATUS_SUCCESS) break;
        }
    }

    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&payload);
        dsu__blob_free(&file_bytes);
        return st;
    }

    magic[0] = (dsu_u8)DSU_LOG_MAGIC_0;
    magic[1] = (dsu_u8)DSU_LOG_MAGIC_1;
    magic[2] = (dsu_u8)DSU_LOG_MAGIC_2;
    magic[3] = (dsu_u8)DSU_LOG_MAGIC_3;

    st = dsu__file_wrap_payload(magic, (dsu_u16)DSU_LOG_FORMAT_VERSION, payload.data, payload.size, &file_bytes);
    dsu__blob_free(&payload);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&file_bytes);
        return st;
    }

    st = dsu__fs_write_all(path, file_bytes.data, file_bytes.size);
    dsu__blob_free(&file_bytes);
    return st;
}

static dsu_status_t dsu__log_append_from_fields(dsu_log_t *log,
                                               dsu_u32 event_id,
                                               dsu_u8 severity,
                                               dsu_u8 category,
                                               dsu_u32 timestamp,
                                               const char *message,
                                               dsu_u32 message_len) {
    dsu_status_t st;
    dsu_log_event_t *ev;
    char *msg_copy;
    dsu_u32 i;

    if (!log || (!message && message_len != 0u)) {
        return DSU_STATUS_INVALID_ARGS;
    }
    msg_copy = (char *)dsu__malloc(message_len + 1u);
    if (!msg_copy) {
        return DSU_STATUS_IO_ERROR;
    }
    for (i = 0u; i < message_len; ++i) {
        if (((const unsigned char *)message)[i] == 0u) {
            dsu__free(msg_copy);
            return DSU_STATUS_INTEGRITY_ERROR;
        }
    }
    if (message_len) {
        memcpy(msg_copy, message, (size_t)message_len);
    }
    msg_copy[message_len] = '\0';

    st = dsu__log_ensure_capacity(log, log->count + 1u);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(msg_copy);
        return st;
    }

    ev = &log->events[log->count];
    memset(ev, 0, sizeof(*ev));
    ev->event_id = event_id;
    ev->severity = severity;
    ev->category = category;
    ev->reserved = 0u;
    ev->timestamp = timestamp;
    ev->message = msg_copy;
    log->count += 1u;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_log_read_file(dsu_ctx_t *ctx, const char *path, dsu_log_t **out_log) {
    dsu_u8 *file_bytes;
    dsu_u32 file_len;
    dsu_u8 magic[4];
    const dsu_u8 *payload;
    dsu_u32 payload_len;
    dsu_u32 off;
    dsu_u32 event_count;
    dsu_u32 i;
    dsu_status_t st;
    dsu_log_t *log;

    if (!ctx || !path || !out_log) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_log = NULL;

    st = dsu__fs_read_all(&ctx->config, path, &file_bytes, &file_len);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    magic[0] = (dsu_u8)DSU_LOG_MAGIC_0;
    magic[1] = (dsu_u8)DSU_LOG_MAGIC_1;
    magic[2] = (dsu_u8)DSU_LOG_MAGIC_2;
    magic[3] = (dsu_u8)DSU_LOG_MAGIC_3;

    st = dsu__file_unwrap_payload(file_bytes,
                                  file_len,
                                  magic,
                                  (dsu_u16)DSU_LOG_FORMAT_VERSION,
                                  &payload,
                                  &payload_len);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(file_bytes);
        return st;
    }

    st = dsu_log_create(ctx, &log);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(file_bytes);
        return st;
    }

    off = 0u;
    st = dsu__read_u32le(payload, payload_len, &off, &event_count);
    if (st == DSU_STATUS_SUCCESS) {
        dsu_u32 flags_ignored;
        st = dsu__read_u32le(payload, payload_len, &off, &flags_ignored);
    }
    for (i = 0u; st == DSU_STATUS_SUCCESS && i < event_count; ++i) {
        dsu_u32 event_id;
        dsu_u8 severity;
        dsu_u8 category;
        dsu_u16 reserved16;
        dsu_u32 timestamp;
        dsu_u32 msg_len;
        const dsu_u8 *msg_ptr;

        st = dsu__read_u32le(payload, payload_len, &off, &event_id);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u8(payload, payload_len, &off, &severity);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u8(payload, payload_len, &off, &category);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u16le(payload, payload_len, &off, &reserved16);
        if (st != DSU_STATUS_SUCCESS) break;
        (void)reserved16;
        st = dsu__read_u32le(payload, payload_len, &off, &timestamp);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__read_u32le(payload, payload_len, &off, &msg_len);
        if (st != DSU_STATUS_SUCCESS) break;
        if (payload_len - off < msg_len) {
            st = DSU_STATUS_INTEGRITY_ERROR;
            break;
        }
        msg_ptr = payload + off;
        off += msg_len;

        st = dsu__log_append_from_fields(log,
                                         event_id,
                                         severity,
                                         category,
                                         timestamp,
                                         (const char *)msg_ptr,
                                         msg_len);
    }

    dsu__free(file_bytes);

    if (st != DSU_STATUS_SUCCESS) {
        dsu_log_destroy(ctx, log);
        return st;
    }
    *out_log = log;
    return DSU_STATUS_SUCCESS;
}

