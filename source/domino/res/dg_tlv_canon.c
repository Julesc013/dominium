#include <stdlib.h>
#include <string.h>

#include "res/dg_tlv_canon.h"

u16 dg_le_read_u16(const unsigned char *p) {
    return (u16)((u16)p[0] | (u16)((u16)p[1] << 8));
}

u32 dg_le_read_u32(const unsigned char *p) {
    return (u32)(
        (u32)p[0] |
        ((u32)p[1] << 8) |
        ((u32)p[2] << 16) |
        ((u32)p[3] << 24)
    );
}

u64 dg_le_read_u64(const unsigned char *p) {
    u32 lo = dg_le_read_u32(p);
    u32 hi = dg_le_read_u32(p + 4u);
    return (u64)lo | ((u64)hi << 32);
}

void dg_le_write_u16(unsigned char *p, u16 v) {
    p[0] = (unsigned char)(v & 0xFFu);
    p[1] = (unsigned char)((v >> 8) & 0xFFu);
}

void dg_le_write_u32(unsigned char *p, u32 v) {
    p[0] = (unsigned char)(v & 0xFFu);
    p[1] = (unsigned char)((v >> 8) & 0xFFu);
    p[2] = (unsigned char)((v >> 16) & 0xFFu);
    p[3] = (unsigned char)((v >> 24) & 0xFFu);
}

void dg_le_write_u64(unsigned char *p, u64 v) {
    dg_le_write_u32(p, (u32)(v & 0xFFFFFFFFu));
    dg_le_write_u32(p + 4u, (u32)(v >> 32));
}

int dg_tlv_next(
    const unsigned char  *tlv,
    u32                   tlv_len,
    u32                  *offset,
    u32                  *tag_out,
    const unsigned char **payload_out,
    u32                  *payload_len_out
) {
    u32 off;
    u32 tag;
    u32 len;
    u32 remaining;

    if (!offset || !tag_out || !payload_out || !payload_len_out) {
        return -1;
    }

    off = *offset;
    if (off >= tlv_len) {
        return 1;
    }

    remaining = tlv_len - off;
    if (!tlv || remaining < 8u) {
        return -2;
    }

    tag = dg_le_read_u32(tlv + off);
    len = dg_le_read_u32(tlv + off + 4u);
    off += 8u;

    if (len > (tlv_len - off)) {
        return -3;
    }

    *tag_out = tag;
    *payload_out = tlv + off;
    *payload_len_out = len;
    off += len;
    *offset = off;
    return 0;
}

typedef struct dg_tlv_rec {
    u32                  tag;
    const unsigned char *payload;
    u32                  payload_len;
} dg_tlv_rec;

static int dg_tlv_rec_cmp(const void *a, const void *b) {
    const dg_tlv_rec *ra = (const dg_tlv_rec *)a;
    const dg_tlv_rec *rb = (const dg_tlv_rec *)b;
    u32 min_len;
    int cmp;

    if (ra->tag < rb->tag) return -1;
    if (ra->tag > rb->tag) return 1;

    /* Tie-break by payload bytes (lexicographic), then length. */
    min_len = (ra->payload_len < rb->payload_len) ? ra->payload_len : rb->payload_len;
    if (min_len != 0u) {
        cmp = memcmp(ra->payload, rb->payload, (size_t)min_len);
        if (cmp != 0) {
            return cmp;
        }
    }
    if (ra->payload_len < rb->payload_len) return -1;
    if (ra->payload_len > rb->payload_len) return 1;
    return 0;
}

static int dg_tlv_count_records(const unsigned char *tlv, u32 tlv_len, u32 *out_count) {
    u32 offset = 0u;
    u32 count = 0u;
    u32 tag;
    const unsigned char *payload;
    u32 payload_len;
    int rc;

    if (!out_count) {
        return -1;
    }
    *out_count = 0u;

    for (;;) {
        rc = dg_tlv_next(tlv, tlv_len, &offset, &tag, &payload, &payload_len);
        if (rc != 0) {
            break;
        }
        count += 1u;
    }

    if (rc == 1) {
        *out_count = count;
        return 0;
    }
    return rc;
}

int dg_tlv_canon(
    const unsigned char *tlv,
    u32                  tlv_len,
    unsigned char       *out,
    u32                  out_cap,
    u32                 *out_len
) {
    dg_tlv_rec *recs;
    u32 rec_count;
    u32 offset;
    u32 i;
    u32 out_off;
    int rc;

    if (!out_len) {
        return -1;
    }
    *out_len = 0u;

    if (tlv_len == 0u) {
        return 0;
    }
    if (!tlv || !out) {
        return -2;
    }
    if (out_cap < tlv_len) {
        return -3;
    }

    rc = dg_tlv_count_records(tlv, tlv_len, &rec_count);
    if (rc != 0) {
        return rc;
    }

    recs = (dg_tlv_rec *)0;
    if (rec_count != 0u) {
        recs = (dg_tlv_rec *)malloc(sizeof(dg_tlv_rec) * rec_count);
        if (!recs) {
            return -4;
        }
    }

    offset = 0u;
    for (i = 0u; i < rec_count; ++i) {
        u32 tag;
        const unsigned char *payload;
        u32 payload_len;
        rc = dg_tlv_next(tlv, tlv_len, &offset, &tag, &payload, &payload_len);
        if (rc != 0) {
            free(recs);
            return -5;
        }
        recs[i].tag = tag;
        recs[i].payload = payload;
        recs[i].payload_len = payload_len;
    }

    if (rec_count > 1u) {
        qsort(recs, (size_t)rec_count, sizeof(dg_tlv_rec), dg_tlv_rec_cmp);
    }

    out_off = 0u;
    for (i = 0u; i < rec_count; ++i) {
        dg_le_write_u32(out + out_off, recs[i].tag);
        dg_le_write_u32(out + out_off + 4u, recs[i].payload_len);
        out_off += 8u;
        if (recs[i].payload_len != 0u) {
            memcpy(out + out_off, recs[i].payload, (size_t)recs[i].payload_len);
            out_off += recs[i].payload_len;
        }
    }

    if (recs) {
        free(recs);
    }
    *out_len = out_off;
    return 0;
}

