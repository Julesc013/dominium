#include <stdlib.h>
#include <string.h>

#include "d_net_proto.h"
#include "d_net_schema.h"
#include "core/d_tlv_kv.h"

enum {
    D_NET_FRAME_MAGIC0 = 'D',
    D_NET_FRAME_MAGIC1 = 'N',
    D_NET_FRAME_MAGIC2 = 'M',
    D_NET_FRAME_VERSION = 1u,
    D_NET_FRAME_HEADER_SIZE = 12u
};

static int d_net_write_tlv_entry(
    unsigned char *dst,
    u32            dst_size,
    u32           *in_out_offset,
    u32            tag,
    const void    *payload,
    u32            payload_len
) {
    u32 off;
    if (!dst || !in_out_offset) {
        return -1;
    }
    off = *in_out_offset;
    if (payload_len > 0u && !payload) {
        return -1;
    }
    if (dst_size - off < 8u + payload_len) {
        return -1;
    }
    memcpy(dst + off, &tag, sizeof(u32));
    memcpy(dst + off + 4u, &payload_len, sizeof(u32));
    off += 8u;
    if (payload_len > 0u) {
        memcpy(dst + off, payload, payload_len);
        off += payload_len;
    }
    *in_out_offset = off;
    return 0;
}

static int d_net_encode_frame(
    d_net_msg_type  type,
    const void     *payload,
    u32             payload_len,
    void           *buf,
    u32             buf_size,
    u32            *out_size
) {
    unsigned char *p;
    u32 total;
    if (!buf || !out_size) {
        return -1;
    }
    if (payload_len > 0u && !payload) {
        return -1;
    }
    total = D_NET_FRAME_HEADER_SIZE + payload_len;
    if (buf_size < total) {
        return -2;
    }
    p = (unsigned char *)buf;
    p[0] = (unsigned char)D_NET_FRAME_MAGIC0;
    p[1] = (unsigned char)D_NET_FRAME_MAGIC1;
    p[2] = (unsigned char)D_NET_FRAME_MAGIC2;
    p[3] = (unsigned char)D_NET_FRAME_VERSION;
    p[4] = (unsigned char)type;
    p[5] = 0u;
    p[6] = 0u;
    p[7] = 0u;
    memcpy(p + 8u, &payload_len, sizeof(u32));
    if (payload_len > 0u) {
        memcpy(p + D_NET_FRAME_HEADER_SIZE, payload, payload_len);
    }
    *out_size = total;
    return 0;
}

int d_net_decode_frame(
    const void     *buf,
    u32             size,
    d_net_msg_type *out_type,
    d_tlv_blob     *out_payload
) {
    const unsigned char *p;
    u32 payload_len;
    if (!buf || !out_type || !out_payload) {
        return -1;
    }
    *out_type = D_NET_MSG_NONE;
    out_payload->ptr = (unsigned char *)0;
    out_payload->len = 0u;
    if (size < D_NET_FRAME_HEADER_SIZE) {
        return -1;
    }
    p = (const unsigned char *)buf;
    if (p[0] != (unsigned char)D_NET_FRAME_MAGIC0 ||
        p[1] != (unsigned char)D_NET_FRAME_MAGIC1 ||
        p[2] != (unsigned char)D_NET_FRAME_MAGIC2) {
        return -2;
    }
    if (p[3] != (unsigned char)D_NET_FRAME_VERSION) {
        return -3;
    }
    *out_type = (d_net_msg_type)p[4];
    memcpy(&payload_len, p + 8u, sizeof(u32));
    if (payload_len > size - D_NET_FRAME_HEADER_SIZE) {
        return -4;
    }
    out_payload->ptr = (unsigned char *)(p + D_NET_FRAME_HEADER_SIZE);
    out_payload->len = payload_len;
    return 0;
}

int d_net_encode_cmd(const d_net_cmd *cmd, void *buf, u32 buf_size, u32 *out_size) {
    u32 tlv_len;
    u32 off;
    unsigned char *tmp;
    if (!cmd || !buf || !out_size) {
        return -1;
    }
    if (cmd->schema_id == 0u || cmd->schema_ver == 0u) {
        return -1;
    }
    if (cmd->payload.len > 0u && !cmd->payload.ptr) {
        return -1;
    }

    tlv_len =
        (8u + 4u) + /* id */
        (8u + 4u) + /* source */
        (8u + 4u) + /* tick */
        (8u + 4u) + /* schema_id */
        (8u + 2u) + /* schema_ver */
        (8u + cmd->payload.len); /* payload */

    tmp = (unsigned char *)malloc(tlv_len);
    if (!tmp) {
        return -2;
    }

    off = 0u;
    (void)d_net_write_tlv_entry(tmp, tlv_len, &off, D_NET_TLV_CMD_ID, &cmd->id, 4u);
    (void)d_net_write_tlv_entry(tmp, tlv_len, &off, D_NET_TLV_CMD_SOURCE, &cmd->source_peer, 4u);
    (void)d_net_write_tlv_entry(tmp, tlv_len, &off, D_NET_TLV_CMD_TICK, &cmd->tick, 4u);
    (void)d_net_write_tlv_entry(tmp, tlv_len, &off, D_NET_TLV_CMD_SCHEMA_ID, &cmd->schema_id, 4u);
    {
        u16 ver = cmd->schema_ver;
        (void)d_net_write_tlv_entry(tmp, tlv_len, &off, D_NET_TLV_CMD_SCHEMA_VER, &ver, 2u);
    }
    (void)d_net_write_tlv_entry(tmp, tlv_len, &off, D_NET_TLV_CMD_PAYLOAD, cmd->payload.ptr, cmd->payload.len);

    if (off != tlv_len) {
        free(tmp);
        return -3;
    }

    {
        int rc = d_net_encode_frame(D_NET_MSG_CMD, tmp, tlv_len, buf, buf_size, out_size);
        free(tmp);
        return rc;
    }
}

int d_net_decode_cmd(const void *buf, u32 size, d_net_cmd *out_cmd) {
    d_net_msg_type type;
    d_tlv_blob payload;
    u32 off;
    u32 tag;
    d_tlv_blob pl;
    int rc;
    int have_id = 0;
    int have_source = 0;
    int have_tick = 0;
    int have_schema_id = 0;
    int have_schema_ver = 0;
    int have_payload = 0;

    if (!out_cmd) {
        return -1;
    }
    memset(out_cmd, 0, sizeof(*out_cmd));

    rc = d_net_decode_frame(buf, size, &type, &payload);
    if (rc != 0) {
        return rc;
    }
    if (type != D_NET_MSG_CMD) {
        return -2;
    }

    off = 0u;
    while ((rc = d_tlv_kv_next(&payload, &off, &tag, &pl)) == 0) {
        if (tag == D_NET_TLV_CMD_ID) {
            u32 tmp = 0u;
            if (d_tlv_kv_read_u32(&pl, &tmp) == 0) {
                out_cmd->id = tmp;
                have_id = 1;
            }
        } else if (tag == D_NET_TLV_CMD_SOURCE) {
            u32 tmp = 0u;
            if (d_tlv_kv_read_u32(&pl, &tmp) == 0) {
                out_cmd->source_peer = (d_peer_id)tmp;
                have_source = 1;
            }
        } else if (tag == D_NET_TLV_CMD_TICK) {
            u32 tmp = 0u;
            if (d_tlv_kv_read_u32(&pl, &tmp) == 0) {
                out_cmd->tick = tmp;
                have_tick = 1;
            }
        } else if (tag == D_NET_TLV_CMD_SCHEMA_ID) {
            u32 tmp = 0u;
            if (d_tlv_kv_read_u32(&pl, &tmp) == 0) {
                out_cmd->schema_id = tmp;
                have_schema_id = 1;
            }
        } else if (tag == D_NET_TLV_CMD_SCHEMA_VER) {
            u16 tmp = 0u;
            if (d_tlv_kv_read_u16(&pl, &tmp) == 0) {
                out_cmd->schema_ver = tmp;
                have_schema_ver = 1;
            }
        } else if (tag == D_NET_TLV_CMD_PAYLOAD) {
            if (pl.len > 0u && pl.ptr) {
                out_cmd->payload.ptr = (unsigned char *)malloc(pl.len);
                if (!out_cmd->payload.ptr) {
                    return -3;
                }
                memcpy(out_cmd->payload.ptr, pl.ptr, pl.len);
                out_cmd->payload.len = pl.len;
            } else {
                out_cmd->payload.ptr = (unsigned char *)0;
                out_cmd->payload.len = 0u;
            }
            have_payload = 1;
        }
    }

    if (!have_id || !have_source || !have_tick || !have_schema_id || !have_schema_ver || !have_payload) {
        if (out_cmd->payload.ptr) {
            free(out_cmd->payload.ptr);
        }
        memset(out_cmd, 0, sizeof(*out_cmd));
        return -4;
    }
    return 0;
}

int d_net_encode_handshake(const d_net_handshake *hs, void *buf, u32 buf_size, u32 *out_size) {
    unsigned char tmp[128];
    u32 off = 0u;
    if (!hs || !buf || !out_size) {
        return -1;
    }
    (void)d_net_write_tlv_entry(tmp, sizeof(tmp), &off, D_NET_TLV_HANDSHAKE_SUITE_VERSION, &hs->suite_version, 4u);
    (void)d_net_write_tlv_entry(tmp, sizeof(tmp), &off, D_NET_TLV_HANDSHAKE_CORE_VERSION, &hs->core_version, 4u);
    (void)d_net_write_tlv_entry(tmp, sizeof(tmp), &off, D_NET_TLV_HANDSHAKE_NET_PROTO_VER, &hs->net_proto_version, 4u);
    (void)d_net_write_tlv_entry(tmp, sizeof(tmp), &off, D_NET_TLV_HANDSHAKE_COMPAT_PROFILE, &hs->compat_profile, 4u);
    (void)d_net_write_tlv_entry(tmp, sizeof(tmp), &off, D_NET_TLV_HANDSHAKE_ROLE, &hs->role, 4u);
    return d_net_encode_frame(D_NET_MSG_HANDSHAKE, tmp, off, buf, buf_size, out_size);
}

int d_net_decode_handshake(const void *buf, u32 size, d_net_handshake *out_hs) {
    d_net_msg_type type;
    d_tlv_blob payload;
    u32 off;
    u32 tag;
    d_tlv_blob pl;
    int rc;
    if (!out_hs) {
        return -1;
    }
    memset(out_hs, 0, sizeof(*out_hs));
    rc = d_net_decode_frame(buf, size, &type, &payload);
    if (rc != 0) {
        return rc;
    }
    if (type != D_NET_MSG_HANDSHAKE) {
        return -2;
    }
    off = 0u;
    while ((rc = d_tlv_kv_next(&payload, &off, &tag, &pl)) == 0) {
        if (tag == D_NET_TLV_HANDSHAKE_SUITE_VERSION) {
            (void)d_tlv_kv_read_u32(&pl, &out_hs->suite_version);
        } else if (tag == D_NET_TLV_HANDSHAKE_CORE_VERSION) {
            (void)d_tlv_kv_read_u32(&pl, &out_hs->core_version);
        } else if (tag == D_NET_TLV_HANDSHAKE_NET_PROTO_VER) {
            (void)d_tlv_kv_read_u32(&pl, &out_hs->net_proto_version);
        } else if (tag == D_NET_TLV_HANDSHAKE_COMPAT_PROFILE) {
            (void)d_tlv_kv_read_u32(&pl, &out_hs->compat_profile);
        } else if (tag == D_NET_TLV_HANDSHAKE_ROLE) {
            (void)d_tlv_kv_read_u32(&pl, &out_hs->role);
        }
    }
    return 0;
}

int d_net_encode_handshake_reply(const d_net_handshake_reply *r, void *buf, u32 buf_size, u32 *out_size) {
    unsigned char tmp[128];
    u32 off = 0u;
    if (!r || !buf || !out_size) {
        return -1;
    }
    (void)d_net_write_tlv_entry(tmp, sizeof(tmp), &off, D_NET_TLV_HANDSHAKE_REPLY_RESULT, &r->result, 4u);
    (void)d_net_write_tlv_entry(tmp, sizeof(tmp), &off, D_NET_TLV_HANDSHAKE_REPLY_REASON_CODE, &r->reason_code, 4u);
    (void)d_net_write_tlv_entry(tmp, sizeof(tmp), &off, D_NET_TLV_HANDSHAKE_REPLY_ASSIGNED_PEER, &r->assigned_peer, 4u);
    (void)d_net_write_tlv_entry(tmp, sizeof(tmp), &off, D_NET_TLV_HANDSHAKE_REPLY_SESSION_ID, &r->session_id, 4u);
    (void)d_net_write_tlv_entry(tmp, sizeof(tmp), &off, D_NET_TLV_HANDSHAKE_REPLY_TICK_RATE, &r->tick_rate, 4u);
    (void)d_net_write_tlv_entry(tmp, sizeof(tmp), &off, D_NET_TLV_HANDSHAKE_REPLY_TICK, &r->tick, 4u);
    return d_net_encode_frame(D_NET_MSG_HANDSHAKE_REPLY, tmp, off, buf, buf_size, out_size);
}

int d_net_decode_handshake_reply(const void *buf, u32 size, d_net_handshake_reply *out_r) {
    d_net_msg_type type;
    d_tlv_blob payload;
    u32 off;
    u32 tag;
    d_tlv_blob pl;
    int rc;
    if (!out_r) {
        return -1;
    }
    memset(out_r, 0, sizeof(*out_r));
    rc = d_net_decode_frame(buf, size, &type, &payload);
    if (rc != 0) {
        return rc;
    }
    if (type != D_NET_MSG_HANDSHAKE_REPLY) {
        return -2;
    }
    off = 0u;
    while ((rc = d_tlv_kv_next(&payload, &off, &tag, &pl)) == 0) {
        if (tag == D_NET_TLV_HANDSHAKE_REPLY_RESULT) {
            (void)d_tlv_kv_read_u32(&pl, &out_r->result);
        } else if (tag == D_NET_TLV_HANDSHAKE_REPLY_REASON_CODE) {
            (void)d_tlv_kv_read_u32(&pl, &out_r->reason_code);
        } else if (tag == D_NET_TLV_HANDSHAKE_REPLY_ASSIGNED_PEER) {
            u32 tmp = 0u;
            if (d_tlv_kv_read_u32(&pl, &tmp) == 0) {
                out_r->assigned_peer = (d_peer_id)tmp;
            }
        } else if (tag == D_NET_TLV_HANDSHAKE_REPLY_SESSION_ID) {
            u32 tmp = 0u;
            if (d_tlv_kv_read_u32(&pl, &tmp) == 0) {
                out_r->session_id = (d_session_id)tmp;
            }
        } else if (tag == D_NET_TLV_HANDSHAKE_REPLY_TICK_RATE) {
            (void)d_tlv_kv_read_u32(&pl, &out_r->tick_rate);
        } else if (tag == D_NET_TLV_HANDSHAKE_REPLY_TICK) {
            (void)d_tlv_kv_read_u32(&pl, &out_r->tick);
        }
    }
    return 0;
}

int d_net_encode_snapshot(const d_net_snapshot *snap, void *buf, u32 buf_size, u32 *out_size) {
    u32 tlv_len;
    u32 off;
    unsigned char *tmp;
    if (!snap || !buf || !out_size) {
        return -1;
    }
    if (snap->data.len > 0u && !snap->data.ptr) {
        return -1;
    }
    tlv_len = (8u + 4u) + (8u + snap->data.len);
    tmp = (unsigned char *)malloc(tlv_len);
    if (!tmp) {
        return -2;
    }
    off = 0u;
    (void)d_net_write_tlv_entry(tmp, tlv_len, &off, D_NET_TLV_SNAPSHOT_TICK, &snap->tick, 4u);
    (void)d_net_write_tlv_entry(tmp, tlv_len, &off, D_NET_TLV_SNAPSHOT_DATA, snap->data.ptr, snap->data.len);
    if (off != tlv_len) {
        free(tmp);
        return -3;
    }
    {
        int rc = d_net_encode_frame(D_NET_MSG_SNAPSHOT, tmp, tlv_len, buf, buf_size, out_size);
        free(tmp);
        return rc;
    }
}

int d_net_decode_snapshot(const void *buf, u32 size, d_net_snapshot *out_snap) {
    d_net_msg_type type;
    d_tlv_blob payload;
    u32 off;
    u32 tag;
    d_tlv_blob pl;
    int rc;
    if (!out_snap) {
        return -1;
    }
    memset(out_snap, 0, sizeof(*out_snap));
    rc = d_net_decode_frame(buf, size, &type, &payload);
    if (rc != 0) {
        return rc;
    }
    if (type != D_NET_MSG_SNAPSHOT) {
        return -2;
    }
    off = 0u;
    while ((rc = d_tlv_kv_next(&payload, &off, &tag, &pl)) == 0) {
        if (tag == D_NET_TLV_SNAPSHOT_TICK) {
            (void)d_tlv_kv_read_u32(&pl, &out_snap->tick);
        } else if (tag == D_NET_TLV_SNAPSHOT_DATA) {
            if (pl.len > 0u && pl.ptr) {
                out_snap->data.ptr = (unsigned char *)malloc(pl.len);
                if (!out_snap->data.ptr) {
                    d_net_snapshot_free(out_snap);
                    return -3;
                }
                memcpy(out_snap->data.ptr, pl.ptr, pl.len);
                out_snap->data.len = pl.len;
            }
        }
    }
    return 0;
}

int d_net_encode_tick(const d_net_tick *t, void *buf, u32 buf_size, u32 *out_size) {
    unsigned char tmp[32];
    u32 off = 0u;
    if (!t || !buf || !out_size) {
        return -1;
    }
    (void)d_net_write_tlv_entry(tmp, sizeof(tmp), &off, D_NET_TLV_TICK_TICK, &t->tick, 4u);
    return d_net_encode_frame(D_NET_MSG_TICK, tmp, off, buf, buf_size, out_size);
}

int d_net_decode_tick(const void *buf, u32 size, d_net_tick *out_t) {
    d_net_msg_type type;
    d_tlv_blob payload;
    u32 off;
    u32 tag;
    d_tlv_blob pl;
    int rc;
    if (!out_t) {
        return -1;
    }
    memset(out_t, 0, sizeof(*out_t));
    rc = d_net_decode_frame(buf, size, &type, &payload);
    if (rc != 0) {
        return rc;
    }
    if (type != D_NET_MSG_TICK) {
        return -2;
    }
    off = 0u;
    while ((rc = d_tlv_kv_next(&payload, &off, &tag, &pl)) == 0) {
        if (tag == D_NET_TLV_TICK_TICK) {
            (void)d_tlv_kv_read_u32(&pl, &out_t->tick);
        }
    }
    return 0;
}

int d_net_encode_hash(const d_net_hash *h, void *buf, u32 buf_size, u32 *out_size) {
    unsigned char tmp[64];
    u32 off = 0u;
    if (!h || !buf || !out_size) {
        return -1;
    }
    (void)d_net_write_tlv_entry(tmp, sizeof(tmp), &off, D_NET_TLV_HASH_TICK, &h->tick, 4u);
    (void)d_net_write_tlv_entry(tmp, sizeof(tmp), &off, D_NET_TLV_HASH_WORLD, &h->world_hash, 8u);
    return d_net_encode_frame(D_NET_MSG_HASH, tmp, off, buf, buf_size, out_size);
}

int d_net_decode_hash(const void *buf, u32 size, d_net_hash *out_h) {
    d_net_msg_type type;
    d_tlv_blob payload;
    u32 off;
    u32 tag;
    d_tlv_blob pl;
    int rc;
    if (!out_h) {
        return -1;
    }
    memset(out_h, 0, sizeof(*out_h));
    rc = d_net_decode_frame(buf, size, &type, &payload);
    if (rc != 0) {
        return rc;
    }
    if (type != D_NET_MSG_HASH) {
        return -2;
    }
    off = 0u;
    while ((rc = d_tlv_kv_next(&payload, &off, &tag, &pl)) == 0) {
        if (tag == D_NET_TLV_HASH_TICK) {
            (void)d_tlv_kv_read_u32(&pl, &out_h->tick);
        } else if (tag == D_NET_TLV_HASH_WORLD) {
            if (pl.len == 8u && pl.ptr) {
                memcpy(&out_h->world_hash, pl.ptr, 8u);
            }
        }
    }
    return 0;
}

int d_net_encode_error(const d_net_error *e, void *buf, u32 buf_size, u32 *out_size) {
    unsigned char tmp[32];
    u32 off = 0u;
    if (!e || !buf || !out_size) {
        return -1;
    }
    (void)d_net_write_tlv_entry(tmp, sizeof(tmp), &off, 0x01u, &e->code, 4u);
    return d_net_encode_frame(D_NET_MSG_ERROR, tmp, off, buf, buf_size, out_size);
}

int d_net_decode_error(const void *buf, u32 size, d_net_error *out_e) {
    d_net_msg_type type;
    d_tlv_blob payload;
    u32 off;
    u32 tag;
    d_tlv_blob pl;
    int rc;
    if (!out_e) {
        return -1;
    }
    memset(out_e, 0, sizeof(*out_e));
    rc = d_net_decode_frame(buf, size, &type, &payload);
    if (rc != 0) {
        return rc;
    }
    if (type != D_NET_MSG_ERROR) {
        return -2;
    }
    off = 0u;
    while ((rc = d_tlv_kv_next(&payload, &off, &tag, &pl)) == 0) {
        if (tag == 0x01u) {
            (void)d_tlv_kv_read_u32(&pl, &out_e->code);
        }
    }
    return 0;
}

void d_net_snapshot_free(d_net_snapshot *snap) {
    if (!snap) {
        return;
    }
    if (snap->data.ptr) {
        free(snap->data.ptr);
    }
    memset(snap, 0, sizeof(*snap));
}

