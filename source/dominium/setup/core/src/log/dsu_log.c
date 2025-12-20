/*
FILE: source/dominium/setup/core/src/log/dsu_log.c
MODULE: Dominium Setup
PURPOSE: Audit log implementation (in-memory + deterministic binary export/import).
*/
#include "../../include/dsu/dsu_log.h"

#include "../dsu_ctx_internal.h"
#include "dsu_events.h"
#include "../util/dsu_util_internal.h"

#include <stdio.h>
#include <string.h>
#include <time.h>

#define DSU_LOG_MAGIC_0 'D'
#define DSU_LOG_MAGIC_1 'S'
#define DSU_LOG_MAGIC_2 'U'
#define DSU_LOG_MAGIC_3 'L'
#define DSU_LOG_FORMAT_VERSION 2u

/* TLV payload format (v2). */
#define DSU_LOG_TLV_ROOT 0x0001u
#define DSU_LOG_TLV_ROOT_VERSION 0x0002u /* u32 */

#define DSU_LOG_TLV_EVENT 0x0010u
#define DSU_LOG_TLV_EVENT_VERSION 0x0011u /* u32 */
#define DSU_LOG_TLV_EVENT_SEQ 0x0012u     /* u32 */
#define DSU_LOG_TLV_EVENT_ID 0x0013u      /* u32 */
#define DSU_LOG_TLV_SEVERITY 0x0014u      /* u8 */
#define DSU_LOG_TLV_CATEGORY 0x0015u      /* u8 */
#define DSU_LOG_TLV_PHASE 0x0016u         /* u8 */
#define DSU_LOG_TLV_TIMESTAMP 0x0017u     /* u32 */

#define DSU_LOG_TLV_MESSAGE 0x0100u       /* string (utf-8) */
#define DSU_LOG_TLV_PATH 0x0101u          /* string (canonical DSU path) */
#define DSU_LOG_TLV_COMPONENT_ID 0x0102u  /* string (ascii id) */
#define DSU_LOG_TLV_STATUS_CODE 0x0103u   /* u32 */
#define DSU_LOG_TLV_DIGEST64_A 0x0104u    /* u64 */
#define DSU_LOG_TLV_DIGEST64_B 0x0105u    /* u64 */
#define DSU_LOG_TLV_DIGEST64_C 0x0106u    /* u64 */

typedef struct dsu_log_event_rec_t {
    dsu_u32 event_seq;
    dsu_u32 event_id;
    dsu_u8 severity;
    dsu_u8 category;
    dsu_u8 phase;
    dsu_u8 reserved8;
    dsu_u32 timestamp;
    dsu_u32 status_code;
    dsu_u64 digest64_a;
    dsu_u64 digest64_b;
    dsu_u64 digest64_c;
    char *message;
    char *path;
    char *component_id;
} dsu_log_event_rec_t;

struct dsu_log {
    dsu_u32 count;
    dsu_u32 cap;
    dsu_u32 next_seq;
    dsu_u8 has_last_written_digest;
    dsu_u8 reserved8[3];
    dsu_u64 last_written_digest64;
    char *opened_path;
    dsu_log_event_rec_t *events;
};

static dsu_status_t dsu__log_ensure_capacity(dsu_log_t *log, dsu_u32 needed);
static dsu_u32 dsu__ctx_timestamp(const dsu_ctx_t *ctx);

static void dsu__log_event_free(dsu_log_event_rec_t *ev) {
    if (!ev) {
        return;
    }
    dsu__free(ev->message);
    ev->message = NULL;
    dsu__free(ev->path);
    ev->path = NULL;
    dsu__free(ev->component_id);
    ev->component_id = NULL;
}

void dsu_log_event_init(dsu_log_event_t *ev) {
    if (!ev) {
        return;
    }
    memset(ev, 0, sizeof(*ev));
    ev->struct_size = (dsu_u32)sizeof(*ev);
    ev->struct_version = 1u;
    ev->phase = (dsu_u8)DSU_LOG_PHASE_CLI;
}

dsu_bool dsu_log_has_last_written_digest64(const dsu_log_t *log) {
    if (!log) return 0;
    return log->has_last_written_digest ? 1 : 0;
}

dsu_u64 dsu_log_last_written_digest64(const dsu_log_t *log) {
    if (!log || !log->has_last_written_digest) return 0u;
    return log->last_written_digest64;
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
    log->next_seq = 1u;
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
    dsu__free(log->opened_path);
    log->opened_path = NULL;
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
    log->next_seq = 1u;
    log->has_last_written_digest = 0u;
    log->last_written_digest64 = 0u;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_log_open(dsu_ctx_t *ctx, const char *path, dsu_log_t **out_log) {
    dsu_status_t st;
    dsu_log_t *log;
    if (!ctx || !path || !out_log) return DSU_STATUS_INVALID_ARGS;
    *out_log = NULL;
    st = dsu_log_create(ctx, &log);
    if (st != DSU_STATUS_SUCCESS) return st;
    log->opened_path = dsu__strdup(path);
    if (!log->opened_path) {
        dsu_log_destroy(ctx, log);
        return DSU_STATUS_IO_ERROR;
    }
    *out_log = log;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_log_close(dsu_ctx_t *ctx, dsu_log_t *log) {
    dsu_status_t st;
    const char *path;
    if (!ctx || !log) return DSU_STATUS_INVALID_ARGS;
    path = log->opened_path;
    if (!path || path[0] == '\0') {
        dsu_log_destroy(ctx, log);
        return DSU_STATUS_INVALID_ARGS;
    }
    st = dsu_log_write_file(ctx, log, path);
    dsu_log_destroy(ctx, log);
    return st;
}

dsu_status_t dsu_log_event(dsu_ctx_t *ctx, dsu_log_t *log, const dsu_log_event_t *ev) {
    dsu_status_t st;
    dsu_log_event_rec_t *dst;
    dsu_u32 timestamp;
    char *msg_copy;
    char *path_copy = NULL;
    char *comp_copy = NULL;

    if (!ctx || !log || !ev) return DSU_STATUS_INVALID_ARGS;
    if (ev->struct_version != 1u || ev->struct_size < (dsu_u32)sizeof(*ev)) return DSU_STATUS_INVALID_ARGS;

    timestamp = ev->timestamp;
    if ((ctx->config.flags & DSU_CONFIG_FLAG_DETERMINISTIC) != 0u) {
        timestamp = 0u;
    } else if (timestamp == 0u) {
        timestamp = dsu__ctx_timestamp(ctx);
    }

    msg_copy = dsu__strdup(ev->message ? ev->message : "");
    if (!msg_copy) return DSU_STATUS_IO_ERROR;

    if (ev->path && ev->path[0] != '\0') {
        path_copy = dsu__strdup(ev->path);
        if (!path_copy) {
            dsu__free(msg_copy);
            return DSU_STATUS_IO_ERROR;
        }
    }
    if (ev->component_id && ev->component_id[0] != '\0') {
        comp_copy = dsu__strdup(ev->component_id);
        if (!comp_copy) {
            dsu__free(path_copy);
            dsu__free(msg_copy);
            return DSU_STATUS_IO_ERROR;
        }
    }

    st = dsu__log_ensure_capacity(log, log->count + 1u);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(comp_copy);
        dsu__free(path_copy);
        dsu__free(msg_copy);
        return st;
    }

    dst = &log->events[log->count];
    memset(dst, 0, sizeof(*dst));
    dst->event_seq = (ev->event_seq != 0u) ? ev->event_seq : log->next_seq;
    if (dst->event_seq != log->next_seq) {
        dsu__free(comp_copy);
        dsu__free(path_copy);
        dsu__free(msg_copy);
        return DSU_STATUS_INVALID_ARGS;
    }
    log->next_seq += 1u;

    dst->event_id = ev->event_id;
    dst->severity = ev->severity;
    dst->category = ev->category;
    dst->phase = ev->phase;
    dst->reserved8 = 0u;
    dst->timestamp = timestamp;
    dst->status_code = ev->status_code;
    dst->digest64_a = ev->digest64_a;
    dst->digest64_b = ev->digest64_b;
    dst->digest64_c = ev->digest64_c;
    dst->message = msg_copy;
    dst->path = path_copy;
    dst->component_id = comp_copy;
    log->count += 1u;

    if (ctx->callbacks.log) {
        ctx->callbacks.log(ctx->callbacks_user,
                           dst->event_id,
                           dst->severity,
                           dst->category,
                           dst->timestamp,
                           dst->message ? dst->message : "");
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__log_ensure_capacity(dsu_log_t *log, dsu_u32 needed) {
    dsu_u32 new_cap;
    dsu_log_event_rec_t *p;
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
    p = (dsu_log_event_rec_t *)dsu__realloc(log->events, (dsu_u32)(new_cap * (dsu_u32)sizeof(*p)));
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

static dsu_u8 dsu__phase_for_event_id(dsu_u32 event_id) {
    switch (event_id) {
        case DSU_EVENT_TXN_STAGE_START:
        case DSU_EVENT_TXN_STAGE_COMPLETE:
        case DSU_EVENT_TXN_JOURNAL_WRITTEN:
            return (dsu_u8)DSU_LOG_PHASE_STAGE;
        case DSU_EVENT_TXN_VERIFY_START:
        case DSU_EVENT_TXN_VERIFY_COMPLETE:
            return (dsu_u8)DSU_LOG_PHASE_VERIFY;
        case DSU_EVENT_TXN_COMMIT_START:
        case DSU_EVENT_TXN_COMMIT_ENTRY:
        case DSU_EVENT_TXN_COMMIT_COMPLETE:
            return (dsu_u8)DSU_LOG_PHASE_COMMIT;
        case DSU_EVENT_TXN_ROLLBACK_START:
        case DSU_EVENT_TXN_ROLLBACK_ENTRY:
        case DSU_EVENT_TXN_ROLLBACK_COMPLETE:
            return (dsu_u8)DSU_LOG_PHASE_ROLLBACK;
        case DSU_EVENT_TXN_STATE_WRITTEN:
        case DSU_EVENT_AUDIT_LOG_WRITTEN:
            return (dsu_u8)DSU_LOG_PHASE_STATE;
        default:
            return (dsu_u8)DSU_LOG_PHASE_CLI;
    }
}

dsu_status_t dsu_log_emit(dsu_ctx_t *ctx,
                         dsu_log_t *log,
                         dsu_u32 event_id,
                         dsu_u8 severity,
                         dsu_u8 category,
                         const char *message) {
    dsu_status_t st;
    dsu_log_event_rec_t *ev;
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
    ev->event_seq = log->next_seq++;
    ev->event_id = event_id;
    ev->severity = severity;
    ev->category = category;
    ev->phase = dsu__phase_for_event_id(event_id);
    ev->reserved8 = 0u;
    ev->timestamp = timestamp;
    ev->status_code = 0u;
    ev->digest64_a = 0u;
    ev->digest64_b = 0u;
    ev->digest64_c = 0u;
    ev->message = msg_copy;
    ev->path = NULL;
    ev->component_id = NULL;
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
    const dsu_log_event_rec_t *ev;
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

static dsu_status_t dsu__blob_put_tlv_u8(dsu_blob_t *b, dsu_u16 type, dsu_u8 v) {
    return dsu__blob_put_tlv(b, type, &v, 1u);
}

static dsu_status_t dsu__blob_put_tlv_u32(dsu_blob_t *b, dsu_u16 type, dsu_u32 v) {
    dsu_u8 tmp[4];
    tmp[0] = (dsu_u8)(v & 0xFFu);
    tmp[1] = (dsu_u8)((v >> 8) & 0xFFu);
    tmp[2] = (dsu_u8)((v >> 16) & 0xFFu);
    tmp[3] = (dsu_u8)((v >> 24) & 0xFFu);
    return dsu__blob_put_tlv(b, type, tmp, 4u);
}

static dsu_status_t dsu__blob_put_tlv_u64(dsu_blob_t *b, dsu_u16 type, dsu_u64 v) {
    dsu_u8 tmp[8];
    tmp[0] = (dsu_u8)(v & 0xFFu);
    tmp[1] = (dsu_u8)((v >> 8) & 0xFFu);
    tmp[2] = (dsu_u8)((v >> 16) & 0xFFu);
    tmp[3] = (dsu_u8)((v >> 24) & 0xFFu);
    tmp[4] = (dsu_u8)((v >> 32) & 0xFFu);
    tmp[5] = (dsu_u8)((v >> 40) & 0xFFu);
    tmp[6] = (dsu_u8)((v >> 48) & 0xFFu);
    tmp[7] = (dsu_u8)((v >> 56) & 0xFFu);
    return dsu__blob_put_tlv(b, type, tmp, 8u);
}

static dsu_status_t dsu__blob_put_tlv_str(dsu_blob_t *b, dsu_u16 type, const char *s) {
    dsu_u32 n;
    if (!s) s = "";
    n = dsu__strlen(s);
    if (n == 0xFFFFFFFFu) return DSU_STATUS_INVALID_ARGS;
    return dsu__blob_put_tlv(b, type, s, n);
}

dsu_status_t dsu_log_write_file(dsu_ctx_t *ctx, const dsu_log_t *log, const char *path) {
    dsu_blob_t root;
    dsu_blob_t payload;
    dsu_blob_t file_bytes;
    dsu_u8 magic[4];
    dsu_u32 i;
    dsu_status_t st;

    if (!ctx || !log || !path) {
        return DSU_STATUS_INVALID_ARGS;
    }

    dsu__blob_init(&root);
    dsu__blob_init(&payload);
    dsu__blob_init(&file_bytes);

    st = dsu__blob_put_tlv_u32(&root, (dsu_u16)DSU_LOG_TLV_ROOT_VERSION, 2u);
    for (i = 0u; st == DSU_STATUS_SUCCESS && i < log->count; ++i) {
        const dsu_log_event_rec_t *ev = &log->events[i];
        dsu_blob_t eb;
        dsu__blob_init(&eb);

        st = dsu__blob_put_tlv_u32(&eb, (dsu_u16)DSU_LOG_TLV_EVENT_VERSION, 1u);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u32(&eb, (dsu_u16)DSU_LOG_TLV_EVENT_SEQ, ev->event_seq);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u32(&eb, (dsu_u16)DSU_LOG_TLV_EVENT_ID, ev->event_id);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&eb, (dsu_u16)DSU_LOG_TLV_SEVERITY, ev->severity);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&eb, (dsu_u16)DSU_LOG_TLV_CATEGORY, ev->category);
        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_u8(&eb, (dsu_u16)DSU_LOG_TLV_PHASE, ev->phase);
        if (st == DSU_STATUS_SUCCESS && ev->timestamp != 0u) st = dsu__blob_put_tlv_u32(&eb, (dsu_u16)DSU_LOG_TLV_TIMESTAMP, ev->timestamp);

        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv_str(&eb, (dsu_u16)DSU_LOG_TLV_MESSAGE, ev->message ? ev->message : "");
        if (st == DSU_STATUS_SUCCESS && ev->path) st = dsu__blob_put_tlv_str(&eb, (dsu_u16)DSU_LOG_TLV_PATH, ev->path);
        if (st == DSU_STATUS_SUCCESS && ev->component_id) st = dsu__blob_put_tlv_str(&eb, (dsu_u16)DSU_LOG_TLV_COMPONENT_ID, ev->component_id);
        if (st == DSU_STATUS_SUCCESS && ev->status_code != 0u) st = dsu__blob_put_tlv_u32(&eb, (dsu_u16)DSU_LOG_TLV_STATUS_CODE, ev->status_code);
        if (st == DSU_STATUS_SUCCESS && ev->digest64_a != 0u) st = dsu__blob_put_tlv_u64(&eb, (dsu_u16)DSU_LOG_TLV_DIGEST64_A, ev->digest64_a);
        if (st == DSU_STATUS_SUCCESS && ev->digest64_b != 0u) st = dsu__blob_put_tlv_u64(&eb, (dsu_u16)DSU_LOG_TLV_DIGEST64_B, ev->digest64_b);
        if (st == DSU_STATUS_SUCCESS && ev->digest64_c != 0u) st = dsu__blob_put_tlv_u64(&eb, (dsu_u16)DSU_LOG_TLV_DIGEST64_C, ev->digest64_c);

        if (st == DSU_STATUS_SUCCESS) st = dsu__blob_put_tlv(&root, (dsu_u16)DSU_LOG_TLV_EVENT, eb.data, eb.size);
        dsu__blob_free(&eb);
    }

    if (st != DSU_STATUS_SUCCESS) {
        dsu__blob_free(&root);
        dsu__blob_free(&payload);
        dsu__blob_free(&file_bytes);
        return st;
    }

    st = dsu__blob_put_tlv(&payload, (dsu_u16)DSU_LOG_TLV_ROOT, root.data, root.size);
    dsu__blob_free(&root);
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
    if (st == DSU_STATUS_SUCCESS) {
        ((dsu_log_t *)log)->last_written_digest64 = dsu_digest64_bytes(file_bytes.data, file_bytes.size);
        ((dsu_log_t *)log)->has_last_written_digest = 1u;
    }
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
    dsu_log_event_rec_t *ev;
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
    ev->event_seq = log->next_seq++;
    ev->event_id = event_id;
    ev->severity = severity;
    ev->category = category;
    ev->phase = (dsu_u8)DSU_LOG_PHASE_CLI;
    ev->reserved8 = 0u;
    ev->timestamp = timestamp;
    ev->status_code = 0u;
    ev->digest64_a = 0u;
    ev->digest64_b = 0u;
    ev->digest64_c = 0u;
    ev->message = msg_copy;
    ev->path = NULL;
    ev->component_id = NULL;
    log->count += 1u;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__dup_bytes_cstr(const dsu_u8 *bytes, dsu_u32 len, char **out_str) {
    char *s;
    dsu_u32 i;
    if (!out_str) return DSU_STATUS_INVALID_ARGS;
    *out_str = NULL;
    if (!bytes && len != 0u) return DSU_STATUS_INVALID_ARGS;

    s = (char *)dsu__malloc(len + 1u);
    if (!s) return DSU_STATUS_IO_ERROR;
    if (len) memcpy(s, bytes, (size_t)len);
    s[len] = '\0';

    for (i = 0u; i < len; ++i) {
        if (((const unsigned char *)s)[i] == 0u) {
            dsu__free(s);
            return DSU_STATUS_PARSE_ERROR;
        }
    }
    *out_str = s;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__read_tlv_u8(const dsu_u8 *v, dsu_u32 len, dsu_u8 *out) {
    dsu_u32 off = 0u;
    if (!v || !out) return DSU_STATUS_INVALID_ARGS;
    if (len != 1u) return DSU_STATUS_INTEGRITY_ERROR;
    return dsu__read_u8(v, len, &off, out);
}

static dsu_status_t dsu__read_tlv_u32(const dsu_u8 *v, dsu_u32 len, dsu_u32 *out) {
    dsu_u32 off = 0u;
    if (!v || !out) return DSU_STATUS_INVALID_ARGS;
    if (len != 4u) return DSU_STATUS_INTEGRITY_ERROR;
    return dsu__read_u32le(v, len, &off, out);
}

static dsu_status_t dsu__read_tlv_u64(const dsu_u8 *v, dsu_u32 len, dsu_u64 *out) {
    dsu_u32 off = 0u;
    if (!v || !out) return DSU_STATUS_INVALID_ARGS;
    if (len != 8u) return DSU_STATUS_INTEGRITY_ERROR;
    return dsu__read_u64le(v, len, &off, out);
}

static dsu_status_t dsu__log_parse_event_v2(dsu_log_t *log, const dsu_u8 *buf, dsu_u32 len) {
    dsu_status_t st = DSU_STATUS_SUCCESS;
    dsu_u32 off = 0u;
    dsu_u32 ver = 0u;
    dsu_u32 seq = 0u;
    dsu_u32 event_id = 0u;
    dsu_u8 severity = 0u;
    dsu_u8 category = 0u;
    dsu_u8 phase = (dsu_u8)DSU_LOG_PHASE_CLI;
    dsu_u32 timestamp = 0u;
    dsu_u32 status_code = 0u;
    dsu_u64 da = 0u;
    dsu_u64 db = 0u;
    dsu_u64 dc = 0u;
    char *message = NULL;
    char *path = NULL;
    char *component_id = NULL;

    if (!log || (!buf && len != 0u)) return DSU_STATUS_INVALID_ARGS;

    while (off < len && st == DSU_STATUS_SUCCESS) {
        dsu_u16 t;
        dsu_u32 n;
        const dsu_u8 *v;
        st = dsu__tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) break;
        if (len - off < n) {
            st = DSU_STATUS_INTEGRITY_ERROR;
            break;
        }
        v = buf + off;

        if (t == (dsu_u16)DSU_LOG_TLV_EVENT_VERSION) st = dsu__read_tlv_u32(v, n, &ver);
        else if (t == (dsu_u16)DSU_LOG_TLV_EVENT_SEQ) st = dsu__read_tlv_u32(v, n, &seq);
        else if (t == (dsu_u16)DSU_LOG_TLV_EVENT_ID) st = dsu__read_tlv_u32(v, n, &event_id);
        else if (t == (dsu_u16)DSU_LOG_TLV_SEVERITY) st = dsu__read_tlv_u8(v, n, &severity);
        else if (t == (dsu_u16)DSU_LOG_TLV_CATEGORY) st = dsu__read_tlv_u8(v, n, &category);
        else if (t == (dsu_u16)DSU_LOG_TLV_PHASE) st = dsu__read_tlv_u8(v, n, &phase);
        else if (t == (dsu_u16)DSU_LOG_TLV_TIMESTAMP) st = dsu__read_tlv_u32(v, n, &timestamp);
        else if (t == (dsu_u16)DSU_LOG_TLV_STATUS_CODE) st = dsu__read_tlv_u32(v, n, &status_code);
        else if (t == (dsu_u16)DSU_LOG_TLV_DIGEST64_A) st = dsu__read_tlv_u64(v, n, &da);
        else if (t == (dsu_u16)DSU_LOG_TLV_DIGEST64_B) st = dsu__read_tlv_u64(v, n, &db);
        else if (t == (dsu_u16)DSU_LOG_TLV_DIGEST64_C) st = dsu__read_tlv_u64(v, n, &dc);
        else if (t == (dsu_u16)DSU_LOG_TLV_MESSAGE) {
            dsu__free(message);
            message = NULL;
            st = dsu__dup_bytes_cstr(v, n, &message);
        } else if (t == (dsu_u16)DSU_LOG_TLV_PATH) {
            dsu__free(path);
            path = NULL;
            st = dsu__dup_bytes_cstr(v, n, &path);
        } else if (t == (dsu_u16)DSU_LOG_TLV_COMPONENT_ID) {
            dsu__free(component_id);
            component_id = NULL;
            st = dsu__dup_bytes_cstr(v, n, &component_id);
        } else {
            st = dsu__tlv_skip_value(len, &off, n);
            continue;
        }

        if (st != DSU_STATUS_SUCCESS) break;
        off += n;
    }

    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(message);
        dsu__free(path);
        dsu__free(component_id);
        return st;
    }
    if (ver != 1u) {
        dsu__free(message);
        dsu__free(path);
        dsu__free(component_id);
        return DSU_STATUS_UNSUPPORTED_VERSION;
    }

    if (!message) {
        message = dsu__strdup("");
        if (!message) {
            dsu__free(path);
            dsu__free(component_id);
            return DSU_STATUS_IO_ERROR;
        }
    }

    if (seq == 0u) seq = log->next_seq;
    if (seq != log->next_seq) {
        dsu__free(message);
        dsu__free(path);
        dsu__free(component_id);
        return DSU_STATUS_INTEGRITY_ERROR;
    }

    st = dsu__log_ensure_capacity(log, log->count + 1u);
    if (st != DSU_STATUS_SUCCESS) {
        dsu__free(message);
        dsu__free(path);
        dsu__free(component_id);
        return st;
    }

    {
        dsu_log_event_rec_t *dst = &log->events[log->count];
        memset(dst, 0, sizeof(*dst));
        dst->event_seq = seq;
        dst->event_id = event_id;
        dst->severity = severity;
        dst->category = category;
        dst->phase = phase;
        dst->reserved8 = 0u;
        dst->timestamp = timestamp;
        dst->status_code = status_code;
        dst->digest64_a = da;
        dst->digest64_b = db;
        dst->digest64_c = dc;
        dst->message = message;
        dst->path = (path && path[0] != '\0') ? path : NULL;
        dst->component_id = (component_id && component_id[0] != '\0') ? component_id : NULL;
        if (dst->path == NULL) dsu__free(path);
        if (dst->component_id == NULL) dsu__free(component_id);
        log->count += 1u;
        log->next_seq += 1u;
    }

    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__log_parse_root_v2(dsu_log_t *log, const dsu_u8 *buf, dsu_u32 len) {
    dsu_status_t st = DSU_STATUS_SUCCESS;
    dsu_u32 off = 0u;
    dsu_u32 root_ver = 0u;

    if (!log || (!buf && len != 0u)) return DSU_STATUS_INVALID_ARGS;

    while (off < len && st == DSU_STATUS_SUCCESS) {
        dsu_u16 t;
        dsu_u32 n;
        const dsu_u8 *v;
        st = dsu__tlv_read_header(buf, len, &off, &t, &n);
        if (st != DSU_STATUS_SUCCESS) break;
        if (len - off < n) {
            st = DSU_STATUS_INTEGRITY_ERROR;
            break;
        }
        v = buf + off;

        if (t == (dsu_u16)DSU_LOG_TLV_ROOT_VERSION) {
            st = dsu__read_tlv_u32(v, n, &root_ver);
            off += n;
            continue;
        }
        if (t == (dsu_u16)DSU_LOG_TLV_EVENT) {
            st = dsu__log_parse_event_v2(log, v, n);
            off += n;
            continue;
        }
        st = dsu__tlv_skip_value(len, &off, n);
    }

    if (st != DSU_STATUS_SUCCESS) return st;
    if (root_ver != 2u) return DSU_STATUS_UNSUPPORTED_VERSION;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_log_read_file(dsu_ctx_t *ctx, const char *path, dsu_log_t **out_log) {
    dsu_u8 *file_bytes;
    dsu_u32 file_len;
    dsu_u8 magic[4];
    const dsu_u8 *payload;
    dsu_u32 payload_len;
    dsu_u32 off;
    dsu_u32 i;
    dsu_status_t st;
    dsu_log_t *log;
    dsu_u16 ver;

    if (!ctx || !path || !out_log) {
        return DSU_STATUS_INVALID_ARGS;
    }
    *out_log = NULL;

    st = dsu__fs_read_all(&ctx->config, path, &file_bytes, &file_len);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    if (file_len < DSU_FILE_HEADER_BASE_SIZE) {
        dsu__free(file_bytes);
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    if (file_bytes[0] != (dsu_u8)DSU_LOG_MAGIC_0 ||
        file_bytes[1] != (dsu_u8)DSU_LOG_MAGIC_1 ||
        file_bytes[2] != (dsu_u8)DSU_LOG_MAGIC_2 ||
        file_bytes[3] != (dsu_u8)DSU_LOG_MAGIC_3) {
        dsu__free(file_bytes);
        return DSU_STATUS_INTEGRITY_ERROR;
    }
    ver = (dsu_u16)((dsu_u16)file_bytes[4] | ((dsu_u16)file_bytes[5] << 8));

    magic[0] = (dsu_u8)DSU_LOG_MAGIC_0;
    magic[1] = (dsu_u8)DSU_LOG_MAGIC_1;
    magic[2] = (dsu_u8)DSU_LOG_MAGIC_2;
    magic[3] = (dsu_u8)DSU_LOG_MAGIC_3;

    if (ver == 1u) {
        st = dsu__file_unwrap_payload(file_bytes, file_len, magic, (dsu_u16)1u, &payload, &payload_len);
    } else {
        st = dsu__file_unwrap_payload(file_bytes, file_len, magic, (dsu_u16)DSU_LOG_FORMAT_VERSION, &payload, &payload_len);
    }
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
    if (ver == 1u) {
        dsu_u32 event_count;
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
    } else {
        while (off < payload_len && st == DSU_STATUS_SUCCESS) {
            dsu_u16 t;
            dsu_u32 n;
            const dsu_u8 *v;
            st = dsu__tlv_read_header(payload, payload_len, &off, &t, &n);
            if (st != DSU_STATUS_SUCCESS) break;
            if (payload_len - off < n) {
                st = DSU_STATUS_INTEGRITY_ERROR;
                break;
            }
            v = payload + off;
            if (t == (dsu_u16)DSU_LOG_TLV_ROOT) {
                st = dsu__log_parse_root_v2(log, v, n);
            }
            off += n;
        }
    }

    dsu__free(file_bytes);

    if (st != DSU_STATUS_SUCCESS) {
        dsu_log_destroy(ctx, log);
        return st;
    }
    *out_log = log;
    return DSU_STATUS_SUCCESS;
}

static void dsu__u64_hex16(char out16[17], dsu_u64 v) {
    static const char *hex = "0123456789abcdef";
    int i;
    for (i = 0; i < 16; ++i) {
        int shift = (15 - i) * 4;
        out16[i] = hex[(unsigned char)((v >> shift) & 0xFu)];
    }
    out16[16] = '\0';
}

static dsu_status_t dsu__blob_append_cstr(dsu_blob_t *b, const char *s) {
    dsu_u32 n;
    if (!b) return DSU_STATUS_INVALID_ARGS;
    if (!s) s = "";
    n = dsu__strlen(s);
    if (n == 0xFFFFFFFFu) return DSU_STATUS_INVALID_ARGS;
    return dsu__blob_append(b, s, n);
}

static dsu_status_t dsu__json_put_escaped(dsu_blob_t *b, const char *s) {
    static const char hex[] = "0123456789abcdef";
    const unsigned char *p = (const unsigned char *)(s ? s : "");
    dsu_status_t st;
    unsigned char c;

    st = dsu__blob_put_u8(b, (dsu_u8)'"');
    if (st != DSU_STATUS_SUCCESS) return st;

    while ((c = *p++) != 0u) {
        if (c == '\\' || c == '"') {
            st = dsu__blob_put_u8(b, (dsu_u8)'\\');
            if (st != DSU_STATUS_SUCCESS) return st;
            st = dsu__blob_put_u8(b, (dsu_u8)c);
            if (st != DSU_STATUS_SUCCESS) return st;
        } else if (c == '\b') {
            st = dsu__blob_append_cstr(b, "\\b");
            if (st != DSU_STATUS_SUCCESS) return st;
        } else if (c == '\f') {
            st = dsu__blob_append_cstr(b, "\\f");
            if (st != DSU_STATUS_SUCCESS) return st;
        } else if (c == '\n') {
            st = dsu__blob_append_cstr(b, "\\n");
            if (st != DSU_STATUS_SUCCESS) return st;
        } else if (c == '\r') {
            st = dsu__blob_append_cstr(b, "\\r");
            if (st != DSU_STATUS_SUCCESS) return st;
        } else if (c == '\t') {
            st = dsu__blob_append_cstr(b, "\\t");
            if (st != DSU_STATUS_SUCCESS) return st;
        } else if (c < 0x20u) {
            dsu_u8 tmp[6];
            tmp[0] = (dsu_u8)'\\';
            tmp[1] = (dsu_u8)'u';
            tmp[2] = (dsu_u8)'0';
            tmp[3] = (dsu_u8)'0';
            tmp[4] = (dsu_u8)hex[(c >> 4) & 0xFu];
            tmp[5] = (dsu_u8)hex[c & 0xFu];
            st = dsu__blob_append(b, tmp, 6u);
            if (st != DSU_STATUS_SUCCESS) return st;
        } else {
            st = dsu__blob_put_u8(b, (dsu_u8)c);
            if (st != DSU_STATUS_SUCCESS) return st;
        }
    }

    return dsu__blob_put_u8(b, (dsu_u8)'"');
}

dsu_status_t dsu_log_export_json(dsu_ctx_t *ctx, const char *path, const char *out_json_path) {
    dsu_status_t st;
    dsu_log_t *log = NULL;
    dsu_blob_t b;
    dsu_u32 i;
    char num[32];

    if (!ctx || !path || !out_json_path) return DSU_STATUS_INVALID_ARGS;

    st = dsu_log_read_file(ctx, path, &log);
    if (st != DSU_STATUS_SUCCESS) return st;

    dsu__blob_init(&b);

    st = dsu__blob_append_cstr(&b, "{\"format_version\":2,\"event_count\":");
    if (st == DSU_STATUS_SUCCESS) {
        sprintf(num, "%lu", (unsigned long)log->count);
        st = dsu__blob_append_cstr(&b, num);
    }
    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, ",\"events\":[");

    for (i = 0u; st == DSU_STATUS_SUCCESS && i < log->count; ++i) {
        const dsu_log_event_rec_t *ev = &log->events[i];
        char hx[17];
        char hx2[17];
        char hx3[17];
        if (i != 0u) st = dsu__blob_put_u8(&b, (dsu_u8)',');
        if (st != DSU_STATUS_SUCCESS) break;

        st = dsu__blob_append_cstr(&b, "{\"seq\":");
        if (st != DSU_STATUS_SUCCESS) break;
        sprintf(num, "%lu", (unsigned long)ev->event_seq);
        st = dsu__blob_append_cstr(&b, num);
        if (st != DSU_STATUS_SUCCESS) break;

        st = dsu__blob_append_cstr(&b, ",\"event_id\":");
        if (st != DSU_STATUS_SUCCESS) break;
        sprintf(num, "%lu", (unsigned long)ev->event_id);
        st = dsu__blob_append_cstr(&b, num);
        if (st != DSU_STATUS_SUCCESS) break;

        st = dsu__blob_append_cstr(&b, ",\"severity\":");
        if (st != DSU_STATUS_SUCCESS) break;
        sprintf(num, "%lu", (unsigned long)ev->severity);
        st = dsu__blob_append_cstr(&b, num);
        if (st != DSU_STATUS_SUCCESS) break;

        st = dsu__blob_append_cstr(&b, ",\"category\":");
        if (st != DSU_STATUS_SUCCESS) break;
        sprintf(num, "%lu", (unsigned long)ev->category);
        st = dsu__blob_append_cstr(&b, num);
        if (st != DSU_STATUS_SUCCESS) break;

        st = dsu__blob_append_cstr(&b, ",\"phase\":");
        if (st != DSU_STATUS_SUCCESS) break;
        sprintf(num, "%lu", (unsigned long)ev->phase);
        st = dsu__blob_append_cstr(&b, num);
        if (st != DSU_STATUS_SUCCESS) break;

        st = dsu__blob_append_cstr(&b, ",\"timestamp\":");
        if (st != DSU_STATUS_SUCCESS) break;
        sprintf(num, "%lu", (unsigned long)ev->timestamp);
        st = dsu__blob_append_cstr(&b, num);
        if (st != DSU_STATUS_SUCCESS) break;

        st = dsu__blob_append_cstr(&b, ",\"message\":");
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__json_put_escaped(&b, ev->message ? ev->message : "");
        if (st != DSU_STATUS_SUCCESS) break;

        st = dsu__blob_append_cstr(&b, ",\"path\":");
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__json_put_escaped(&b, ev->path ? ev->path : "");
        if (st != DSU_STATUS_SUCCESS) break;

        st = dsu__blob_append_cstr(&b, ",\"component_id\":");
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__json_put_escaped(&b, ev->component_id ? ev->component_id : "");
        if (st != DSU_STATUS_SUCCESS) break;

        st = dsu__blob_append_cstr(&b, ",\"status_code\":");
        if (st != DSU_STATUS_SUCCESS) break;
        sprintf(num, "%lu", (unsigned long)ev->status_code);
        st = dsu__blob_append_cstr(&b, num);
        if (st != DSU_STATUS_SUCCESS) break;

        dsu__u64_hex16(hx, ev->digest64_a);
        dsu__u64_hex16(hx2, ev->digest64_b);
        dsu__u64_hex16(hx3, ev->digest64_c);
        st = dsu__blob_append_cstr(&b, ",\"digests\":[\"0x");
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_append_cstr(&b, hx);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_append_cstr(&b, "\",\"0x");
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_append_cstr(&b, hx2);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_append_cstr(&b, "\",\"0x");
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_append_cstr(&b, hx3);
        if (st != DSU_STATUS_SUCCESS) break;
        st = dsu__blob_append_cstr(&b, "\"]}");
    }

    if (st == DSU_STATUS_SUCCESS) st = dsu__blob_append_cstr(&b, "]}\n");
    if (st == DSU_STATUS_SUCCESS) st = dsu__fs_write_all(out_json_path, b.data, b.size);

    dsu__blob_free(&b);
    dsu_log_destroy(ctx, log);
    return st;
}
