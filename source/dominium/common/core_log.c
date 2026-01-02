/*
FILE: source/dominium/common/core_log.c
MODULE: Dominium
PURPOSE: Structured event logging helpers + deterministic TLV encoding.
*/
#include "dominium/core_log.h"

#include <string.h>
#include <ctype.h>

/*------------------------------------------------------------
 * TLV tags (internal to core_log).
 *------------------------------------------------------------*/
enum {
    CORE_LOG_TLV_TAG_EVENT = 1u,
    CORE_LOG_TLV_TAG_EVENT_DOMAIN = 2u,
    CORE_LOG_TLV_TAG_EVENT_CODE = 3u,
    CORE_LOG_TLV_TAG_EVENT_SEVERITY = 4u,
    CORE_LOG_TLV_TAG_EVENT_FLAGS = 5u,
    CORE_LOG_TLV_TAG_EVENT_MSG_ID = 6u,
    CORE_LOG_TLV_TAG_EVENT_T_MONO = 7u,
    CORE_LOG_TLV_TAG_EVENT_FIELD_COUNT = 8u,
    CORE_LOG_TLV_TAG_EVENT_FIELD = 9u
};

enum {
    CORE_LOG_TLV_TAG_FIELD_KEY = 1u,
    CORE_LOG_TLV_TAG_FIELD_TYPE = 2u,
    CORE_LOG_TLV_TAG_FIELD_FLAGS = 3u,
    CORE_LOG_TLV_TAG_FIELD_VALUE_U32 = 4u,
    CORE_LOG_TLV_TAG_FIELD_VALUE_U64 = 5u,
    CORE_LOG_TLV_TAG_FIELD_VALUE_STR = 6u
};

/*------------------------------------------------------------
 * Helpers.
 *------------------------------------------------------------*/
static void core_log_write_u32_le(unsigned char out[4], u32 v) {
    out[0] = (unsigned char)(v & 0xFFu);
    out[1] = (unsigned char)((v >> 8u) & 0xFFu);
    out[2] = (unsigned char)((v >> 16u) & 0xFFu);
    out[3] = (unsigned char)((v >> 24u) & 0xFFu);
}

static void core_log_write_u64_le(unsigned char out[8], u64 v) {
    core_log_write_u32_le(out, (u32)(v & 0xFFFFFFFFull));
    core_log_write_u32_le(out + 4, (u32)((v >> 32u) & 0xFFFFFFFFull));
}

static u32 core_log_read_u32_le(const unsigned char* p) {
    return (u32)p[0] | ((u32)p[1] << 8u) | ((u32)p[2] << 16u) | ((u32)p[3] << 24u);
}

static u64 core_log_read_u64_le(const unsigned char* p) {
    u64 lo = (u64)core_log_read_u32_le(p);
    u64 hi = (u64)core_log_read_u32_le(p + 4);
    return lo | (hi << 32u);
}

static dom_abi_result core_log_sink_write(const core_log_write_sink* sink,
                                          const void* data,
                                          u32 len) {
    if (!sink || !sink->write) {
        return (dom_abi_result)-1;
    }
    return sink->write(sink->user, data, len);
}

static dom_abi_result core_log_write_tlv_u32(const core_log_write_sink* sink, u32 tag, u32 value) {
    unsigned char hdr[8];
    unsigned char payload[4];
    core_log_write_u32_le(hdr, tag);
    core_log_write_u32_le(hdr + 4, 4u);
    core_log_write_u32_le(payload, value);
    if (core_log_sink_write(sink, hdr, 8u) != 0) return (dom_abi_result)-1;
    if (core_log_sink_write(sink, payload, 4u) != 0) return (dom_abi_result)-1;
    return 0;
}

static dom_abi_result core_log_write_tlv_u64(const core_log_write_sink* sink, u32 tag, u64 value) {
    unsigned char hdr[8];
    unsigned char payload[8];
    core_log_write_u32_le(hdr, tag);
    core_log_write_u32_le(hdr + 4, 8u);
    core_log_write_u64_le(payload, value);
    if (core_log_sink_write(sink, hdr, 8u) != 0) return (dom_abi_result)-1;
    if (core_log_sink_write(sink, payload, 8u) != 0) return (dom_abi_result)-1;
    return 0;
}

static dom_abi_result core_log_write_tlv_bytes(const core_log_write_sink* sink,
                                               u32 tag,
                                               const unsigned char* data,
                                               u32 len) {
    unsigned char hdr[8];
    core_log_write_u32_le(hdr, tag);
    core_log_write_u32_le(hdr + 4, len);
    if (core_log_sink_write(sink, hdr, 8u) != 0) return (dom_abi_result)-1;
    if (len > 0u && data) {
        if (core_log_sink_write(sink, data, len) != 0) return (dom_abi_result)-1;
    }
    return 0;
}

static u32 core_log_field_payload_size(const core_log_field* f) {
    u32 size = 0u;
    if (!f) return 0u;
    size += 8u + 4u; /* key */
    size += 8u + 4u; /* type */
    size += 8u + 4u; /* flags */
    switch (f->type) {
    case CORE_LOG_FIELD_U32:
    case CORE_LOG_FIELD_BOOL:
    case CORE_LOG_FIELD_MSG_ID:
        size += 8u + 4u;
        break;
    case CORE_LOG_FIELD_U64:
    case CORE_LOG_FIELD_HASH64:
        size += 8u + 8u;
        break;
    case CORE_LOG_FIELD_PATH_REL: {
        u32 len = 0u;
        if (f->v.path[0] != '\0') {
            len = (u32)strlen(f->v.path);
        }
        size += 8u + len;
        break;
    }
    case CORE_LOG_FIELD_PATH_REDACTED:
    default:
        break;
    }
    return size;
}

static u32 core_log_event_payload_size(const core_log_event* ev) {
    u32 size = 0u;
    u32 i;
    if (!ev) return 0u;
    size += 8u + 4u; /* domain */
    size += 8u + 4u; /* code */
    size += 8u + 4u; /* severity */
    size += 8u + 4u; /* flags */
    size += 8u + 4u; /* msg_id */
    size += 8u + 8u; /* t_mono */
    size += 8u + 4u; /* field_count */
    for (i = 0u; i < ev->field_count && i < CORE_LOG_MAX_FIELDS; ++i) {
        u32 field_payload = core_log_field_payload_size(&ev->fields[i]);
        size += 8u + field_payload; /* field container */
    }
    return size;
}

u32 core_log_event_encoded_size(const core_log_event* ev) {
    if (!ev) {
        return 0u;
    }
    return 8u + core_log_event_payload_size(ev);
}

static void core_log_normalize_path(const char* in, char* out, u32 out_cap, u32 case_insensitive) {
    u32 w = 0u;
    u32 i = 0u;
    char last = '\0';
    if (!out || out_cap == 0u) {
        return;
    }
    if (!in) {
        out[0] = '\0';
        return;
    }
    while (in[i] != '\0' && (w + 1u) < out_cap) {
        char c = in[i];
        if (c == '\\') {
            c = '/';
        }
        if (case_insensitive) {
            c = (char)tolower((unsigned char)c);
        }
        if (c == '/' && last == '/') {
            i += 1u;
            continue;
        }
        out[w++] = c;
        last = c;
        i += 1u;
    }
    out[w] = '\0';
}

void core_log_event_clear(core_log_event* ev) {
    if (!ev) return;
    memset(ev, 0, sizeof(*ev));
}

static dom_abi_result core_log_field_append(core_log_event* ev, const core_log_field* f) {
    if (!ev || !f) {
        return (dom_abi_result)-1;
    }
    if (ev->field_count >= CORE_LOG_MAX_FIELDS) {
        ev->flags = (u8)(ev->flags | CORE_LOG_EVT_FLAG_TRUNCATED);
        return (dom_abi_result)-1;
    }
    ev->fields[ev->field_count] = *f;
    ev->field_count += 1u;
    if (f->type == CORE_LOG_FIELD_PATH_REL || f->type == CORE_LOG_FIELD_PATH_REDACTED) {
        ev->flags = (u8)(ev->flags | CORE_LOG_EVT_FLAG_HAS_PATH);
    }
    if (f->type == CORE_LOG_FIELD_HASH64) {
        ev->flags = (u8)(ev->flags | CORE_LOG_EVT_FLAG_HAS_HASH);
    }
    if ((f->flags & CORE_LOG_FIELD_FLAG_REDACTED) != 0u) {
        ev->flags = (u8)(ev->flags | CORE_LOG_EVT_FLAG_REDACTED);
    }
    return 0;
}

dom_abi_result core_log_event_add_u32(core_log_event* ev, u32 key_id, u32 value) {
    core_log_field f;
    memset(&f, 0, sizeof(f));
    f.key_id = key_id;
    f.type = (u8)CORE_LOG_FIELD_U32;
    f.v.u32_value = value;
    return core_log_field_append(ev, &f);
}

dom_abi_result core_log_event_add_u64(core_log_event* ev, u32 key_id, u64 value) {
    core_log_field f;
    memset(&f, 0, sizeof(f));
    f.key_id = key_id;
    f.type = (u8)CORE_LOG_FIELD_U64;
    f.v.u64_value = value;
    return core_log_field_append(ev, &f);
}

dom_abi_result core_log_event_add_bool(core_log_event* ev, u32 key_id, u32 value) {
    core_log_field f;
    memset(&f, 0, sizeof(f));
    f.key_id = key_id;
    f.type = (u8)CORE_LOG_FIELD_BOOL;
    f.v.u32_value = value ? 1u : 0u;
    return core_log_field_append(ev, &f);
}

dom_abi_result core_log_event_add_msg_id(core_log_event* ev, u32 key_id, u32 msg_id) {
    core_log_field f;
    memset(&f, 0, sizeof(f));
    f.key_id = key_id;
    f.type = (u8)CORE_LOG_FIELD_MSG_ID;
    f.v.u32_value = msg_id;
    return core_log_field_append(ev, &f);
}

dom_abi_result core_log_event_add_hash64(core_log_event* ev, u32 key_id, u64 hash64) {
    core_log_field f;
    memset(&f, 0, sizeof(f));
    f.key_id = key_id;
    f.type = (u8)CORE_LOG_FIELD_HASH64;
    f.v.u64_value = hash64;
    return core_log_field_append(ev, &f);
}

dom_abi_result core_log_event_add_path_rel(core_log_event* ev, u32 key_id, const char* rel_path) {
    core_log_field f;
    size_t len;
    memset(&f, 0, sizeof(f));
    f.key_id = key_id;
    f.type = (u8)CORE_LOG_FIELD_PATH_REL;
    if (!rel_path) {
        f.v.path[0] = '\0';
        return core_log_field_append(ev, &f);
    }
    len = strlen(rel_path);
    if (len >= CORE_LOG_MAX_PATH) {
        len = CORE_LOG_MAX_PATH - 1u;
        f.flags = (u8)(f.flags | CORE_LOG_FIELD_FLAG_REDACTED);
        if (ev) {
            ev->flags = (u8)(ev->flags | CORE_LOG_EVT_FLAG_TRUNCATED);
        }
    }
    memcpy(f.v.path, rel_path, len);
    f.v.path[len] = '\0';
    return core_log_field_append(ev, &f);
}

dom_abi_result core_log_event_add_path_redacted(core_log_event* ev, u32 key_id) {
    core_log_field f;
    memset(&f, 0, sizeof(f));
    f.key_id = key_id;
    f.type = (u8)CORE_LOG_FIELD_PATH_REDACTED;
    f.flags = (u8)(f.flags | CORE_LOG_FIELD_FLAG_REDACTED);
    f.v.path[0] = '\0';
    return core_log_field_append(ev, &f);
}

int core_log_path_make_relative(const char* root,
                                const char* path,
                                char* out_rel,
                                u32 out_cap,
                                u32 case_insensitive) {
    char norm_root[CORE_LOG_MAX_PATH];
    char norm_path[CORE_LOG_MAX_PATH];
    size_t root_len;
    size_t path_len;

    if (!out_rel || out_cap == 0u) {
        return 0;
    }
    out_rel[0] = '\0';
    if (!root || !path) {
        return 0;
    }

    core_log_normalize_path(root, norm_root, (u32)sizeof(norm_root), case_insensitive);
    core_log_normalize_path(path, norm_path, (u32)sizeof(norm_path), case_insensitive);

    root_len = strlen(norm_root);
    path_len = strlen(norm_path);
    if (root_len == 0u || path_len == 0u) {
        return 0;
    }

    while (root_len > 0u && norm_root[root_len - 1u] == '/') {
        norm_root[root_len - 1u] = '\0';
        root_len -= 1u;
    }

    if (path_len <= root_len) {
        return 0;
    }
    if (strncmp(norm_path, norm_root, root_len) != 0) {
        return 0;
    }
    if (norm_path[root_len] != '/') {
        return 0;
    }

    {
        const char* rel = norm_path + root_len + 1u;
        size_t rel_len = strlen(rel);
        if (rel_len + 1u > out_cap) {
            return 0;
        }
        memcpy(out_rel, rel, rel_len + 1u);
    }

    return 1;
}

dom_abi_result core_log_event_write_tlv(const core_log_event* ev, const core_log_write_sink* sink) {
    u32 payload_len;
    unsigned char hdr[8];
    u32 i;

    if (!ev || !sink || !sink->write) {
        return (dom_abi_result)-1;
    }

    payload_len = core_log_event_payload_size(ev);
    core_log_write_u32_le(hdr, (u32)CORE_LOG_TLV_TAG_EVENT);
    core_log_write_u32_le(hdr + 4, payload_len);
    if (core_log_sink_write(sink, hdr, 8u) != 0) {
        return (dom_abi_result)-1;
    }

    if (core_log_write_tlv_u32(sink, CORE_LOG_TLV_TAG_EVENT_DOMAIN, (u32)ev->domain) != 0) return (dom_abi_result)-1;
    if (core_log_write_tlv_u32(sink, CORE_LOG_TLV_TAG_EVENT_CODE, (u32)ev->code) != 0) return (dom_abi_result)-1;
    if (core_log_write_tlv_u32(sink, CORE_LOG_TLV_TAG_EVENT_SEVERITY, (u32)ev->severity) != 0) return (dom_abi_result)-1;
    if (core_log_write_tlv_u32(sink, CORE_LOG_TLV_TAG_EVENT_FLAGS, (u32)ev->flags) != 0) return (dom_abi_result)-1;
    if (core_log_write_tlv_u32(sink, CORE_LOG_TLV_TAG_EVENT_MSG_ID, (u32)ev->msg_id) != 0) return (dom_abi_result)-1;
    if (core_log_write_tlv_u64(sink, CORE_LOG_TLV_TAG_EVENT_T_MONO, (u64)ev->t_mono) != 0) return (dom_abi_result)-1;
    if (core_log_write_tlv_u32(sink, CORE_LOG_TLV_TAG_EVENT_FIELD_COUNT, (u32)ev->field_count) != 0) return (dom_abi_result)-1;

    for (i = 0u; i < ev->field_count && i < CORE_LOG_MAX_FIELDS; ++i) {
        const core_log_field* f = &ev->fields[i];
        u32 field_payload = core_log_field_payload_size(f);
        unsigned char fhdr[8];
        core_log_write_u32_le(fhdr, (u32)CORE_LOG_TLV_TAG_EVENT_FIELD);
        core_log_write_u32_le(fhdr + 4, field_payload);
        if (core_log_sink_write(sink, fhdr, 8u) != 0) return (dom_abi_result)-1;

        if (core_log_write_tlv_u32(sink, CORE_LOG_TLV_TAG_FIELD_KEY, f->key_id) != 0) return (dom_abi_result)-1;
        if (core_log_write_tlv_u32(sink, CORE_LOG_TLV_TAG_FIELD_TYPE, (u32)f->type) != 0) return (dom_abi_result)-1;
        if (core_log_write_tlv_u32(sink, CORE_LOG_TLV_TAG_FIELD_FLAGS, (u32)f->flags) != 0) return (dom_abi_result)-1;

        switch (f->type) {
        case CORE_LOG_FIELD_U32:
        case CORE_LOG_FIELD_BOOL:
        case CORE_LOG_FIELD_MSG_ID:
            if (core_log_write_tlv_u32(sink, CORE_LOG_TLV_TAG_FIELD_VALUE_U32, f->v.u32_value) != 0) return (dom_abi_result)-1;
            break;
        case CORE_LOG_FIELD_U64:
        case CORE_LOG_FIELD_HASH64:
            if (core_log_write_tlv_u64(sink, CORE_LOG_TLV_TAG_FIELD_VALUE_U64, f->v.u64_value) != 0) return (dom_abi_result)-1;
            break;
        case CORE_LOG_FIELD_PATH_REL: {
            u32 len = 0u;
            if (f->v.path[0] != '\0') {
                len = (u32)strlen(f->v.path);
            }
            if (core_log_write_tlv_bytes(sink, CORE_LOG_TLV_TAG_FIELD_VALUE_STR,
                                         (const unsigned char*)f->v.path, len) != 0) return (dom_abi_result)-1;
            break;
        }
        case CORE_LOG_FIELD_PATH_REDACTED:
        default:
            break;
        }
    }

    return 0;
}

dom_abi_result core_log_event_read_tlv(const unsigned char* data,
                                       u32 size,
                                       core_log_event* out_ev,
                                       u32* out_used) {
    u32 off = 0u;
    u32 end = 0u;

    if (!data || size < 8u || !out_ev) {
        return (dom_abi_result)-1;
    }
    core_log_event_clear(out_ev);

    if (core_log_read_u32_le(data) != (u32)CORE_LOG_TLV_TAG_EVENT) {
        return (dom_abi_result)-1;
    }
    end = 8u + core_log_read_u32_le(data + 4);
    if (end > size) {
        return (dom_abi_result)-1;
    }

    off = 8u;
    while (off + 8u <= end) {
        u32 tag = core_log_read_u32_le(data + off);
        u32 len = core_log_read_u32_le(data + off + 4u);
        const unsigned char* payload = data + off + 8u;
        off += 8u;
        if (off + len > end) {
            return (dom_abi_result)-1;
        }

        switch (tag) {
        case CORE_LOG_TLV_TAG_EVENT_DOMAIN:
            if (len == 4u) out_ev->domain = (u16)core_log_read_u32_le(payload);
            break;
        case CORE_LOG_TLV_TAG_EVENT_CODE:
            if (len == 4u) out_ev->code = (u16)core_log_read_u32_le(payload);
            break;
        case CORE_LOG_TLV_TAG_EVENT_SEVERITY:
            if (len == 4u) out_ev->severity = (u8)core_log_read_u32_le(payload);
            break;
        case CORE_LOG_TLV_TAG_EVENT_FLAGS:
            if (len == 4u) out_ev->flags = (u8)core_log_read_u32_le(payload);
            break;
        case CORE_LOG_TLV_TAG_EVENT_MSG_ID:
            if (len == 4u) out_ev->msg_id = core_log_read_u32_le(payload);
            break;
        case CORE_LOG_TLV_TAG_EVENT_T_MONO:
            if (len == 8u) out_ev->t_mono = core_log_read_u64_le(payload);
            break;
        case CORE_LOG_TLV_TAG_EVENT_FIELD:
            if (len > 0u && out_ev->field_count < CORE_LOG_MAX_FIELDS) {
                core_log_field f;
                u32 foff = 0u;
                u32 fend = len;
                memset(&f, 0, sizeof(f));

                while (foff + 8u <= fend) {
                    u32 ftag = core_log_read_u32_le(payload + foff);
                    u32 flen = core_log_read_u32_le(payload + foff + 4u);
                    const unsigned char* fpl = payload + foff + 8u;
                    foff += 8u;
                    if (foff + flen > fend) {
                        break;
                    }
                    switch (ftag) {
                    case CORE_LOG_TLV_TAG_FIELD_KEY:
                        if (flen == 4u) f.key_id = core_log_read_u32_le(fpl);
                        break;
                    case CORE_LOG_TLV_TAG_FIELD_TYPE:
                        if (flen == 4u) f.type = (u8)core_log_read_u32_le(fpl);
                        break;
                    case CORE_LOG_TLV_TAG_FIELD_FLAGS:
                        if (flen == 4u) f.flags = (u8)core_log_read_u32_le(fpl);
                        break;
                    case CORE_LOG_TLV_TAG_FIELD_VALUE_U32:
                        if (flen == 4u) f.v.u32_value = core_log_read_u32_le(fpl);
                        break;
                    case CORE_LOG_TLV_TAG_FIELD_VALUE_U64:
                        if (flen == 8u) f.v.u64_value = core_log_read_u64_le(fpl);
                        break;
                    case CORE_LOG_TLV_TAG_FIELD_VALUE_STR: {
                        u32 cpy = flen;
                        if (cpy >= CORE_LOG_MAX_PATH) {
                            cpy = CORE_LOG_MAX_PATH - 1u;
                        }
                        if (cpy > 0u) {
                            memcpy(f.v.path, fpl, cpy);
                        }
                        f.v.path[cpy] = '\0';
                        break;
                    }
                    default:
                        break;
                    }
                    foff += flen;
                }

                out_ev->fields[out_ev->field_count] = f;
                out_ev->field_count += 1u;
            }
            break;
        default:
            break;
        }

        off += len;
    }

    if (out_used) {
        *out_used = end;
    }
    return 0;
}

u64 core_log_hash64(const void* data, u32 len) {
    const unsigned char* p = (const unsigned char*)data;
    u64 h = 1469598103934665603ull;
    u32 i;
    if (!p || len == 0u) {
        return h;
    }
    for (i = 0u; i < len; ++i) {
        h ^= (u64)p[i];
        h *= 1099511628211ull;
    }
    return h;
}
