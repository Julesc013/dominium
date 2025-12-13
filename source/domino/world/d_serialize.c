#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/d_serialize_tags.h"
#include "core/d_subsystem.h"
#include "d_serialize.h"

typedef struct d_tlv_builder {
    unsigned char *data;
    u32            length;
    u32            capacity;
} d_tlv_builder;

static void d_tlv_builder_init(d_tlv_builder *b) {
    if (!b) {
        return;
    }
    b->data = (unsigned char *)0;
    b->length = 0u;
    b->capacity = 0u;
}

static void d_tlv_builder_reset(d_tlv_builder *b) {
    if (!b) {
        return;
    }
    if (b->data) {
        free(b->data);
    }
    b->data = (unsigned char *)0;
    b->length = 0u;
    b->capacity = 0u;
}

static int d_tlv_builder_reserve(d_tlv_builder *b, u32 extra) {
    u32 needed;
    u32 new_cap;
    unsigned char *new_data;
    if (!b) {
        return -1;
    }
    if (extra > 0xFFFFFFFFu - b->length) {
        return -1;
    }
    needed = b->length + extra;
    if (needed <= b->capacity) {
        return 0;
    }
    new_cap = b->capacity ? b->capacity : 256u;
    while (new_cap < needed) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = needed;
            break;
        }
        new_cap *= 2u;
    }
    new_data = (unsigned char *)realloc(b->data, new_cap);
    if (!new_data) {
        return -1;
    }
    b->data = new_data;
    b->capacity = new_cap;
    return 0;
}

static int d_tlv_builder_append_entry(d_tlv_builder *b, u32 tag, const unsigned char *payload, u32 payload_len) {
    int rc;
    rc = d_tlv_builder_reserve(b, 8u + payload_len);
    if (rc != 0) {
        return rc;
    }
    memcpy(b->data + b->length, &tag, sizeof(u32));
    b->length += 4u;
    memcpy(b->data + b->length, &payload_len, sizeof(u32));
    b->length += 4u;
    if (payload_len > 0u && payload) {
        memcpy(b->data + b->length, payload, payload_len);
        b->length += payload_len;
    } else if (payload_len > 0u && !payload) {
        return -1;
    }
    return 0;
}

static u32 d_tag_for_subsystem(d_subsystem_id id) {
    switch (id) {
        case D_SUBSYS_WORLD:  return TAG_SUBSYS_DWORLD;
        case D_SUBSYS_RES:    return TAG_SUBSYS_DRES;
        case D_SUBSYS_ENV:    return TAG_SUBSYS_DENV;
        case D_SUBSYS_BUILD:  return TAG_SUBSYS_DBULD;
        case D_SUBSYS_TRANS:  return TAG_SUBSYS_DTRANS;
        case D_SUBSYS_STRUCT: return TAG_SUBSYS_DSTRUCT;
        case D_SUBSYS_VEH:    return TAG_SUBSYS_DVEH;
        case D_SUBSYS_JOB:    return TAG_SUBSYS_DJOB;
        case D_SUBSYS_NET:    return TAG_SUBSYS_DNET;
        case D_SUBSYS_REPLAY: return TAG_SUBSYS_DREPLAY;
        case D_SUBSYS_HYDRO:  return TAG_SUBSYS_DHYDRO;
        case D_SUBSYS_LITHO:  return TAG_SUBSYS_DLITHO;
        default:              return 0u;
    }
}

static d_subsystem_id d_subsystem_for_tag(u32 tag) {
    switch (tag) {
        case TAG_SUBSYS_DWORLD:  return D_SUBSYS_WORLD;
        case TAG_SUBSYS_DRES:    return D_SUBSYS_RES;
        case TAG_SUBSYS_DENV:    return D_SUBSYS_ENV;
        case TAG_SUBSYS_DBULD:   return D_SUBSYS_BUILD;
        case TAG_SUBSYS_DTRANS:  return D_SUBSYS_TRANS;
        case TAG_SUBSYS_DSTRUCT: return D_SUBSYS_STRUCT;
        case TAG_SUBSYS_DVEH:    return D_SUBSYS_VEH;
        case TAG_SUBSYS_DJOB:    return D_SUBSYS_JOB;
        case TAG_SUBSYS_DNET:    return D_SUBSYS_NET;
        case TAG_SUBSYS_DREPLAY: return D_SUBSYS_REPLAY;
        case TAG_SUBSYS_DHYDRO:  return D_SUBSYS_HYDRO;
        case TAG_SUBSYS_DLITHO:  return D_SUBSYS_LITHO;
        default:                 return (d_subsystem_id)0;
    }
}

static int d_serialize_save_all(struct d_world *w, struct d_chunk *chunk, struct d_tlv_blob *out, int use_chunk_callbacks) {
    d_tlv_builder builder;
    u32 count;
    u32 i;

    if (!out) {
        return -1;
    }

    d_tlv_builder_init(&builder);
    count = d_subsystem_count();
    for (i = 0u; i < count; ++i) {
        const d_subsystem_desc *desc = d_subsystem_get_by_index(i);
        d_tlv_blob payload;
        u32 tag;
        int rc;

        if (!desc) {
            continue;
        }

        if (use_chunk_callbacks) {
            if (!desc->save_chunk) {
                continue;
            }
            payload.ptr = (unsigned char *)0;
            payload.len = 0u;
            rc = desc->save_chunk(w, chunk, &payload);
        } else {
            if (!desc->save_instance) {
                continue;
            }
            payload.ptr = (unsigned char *)0;
            payload.len = 0u;
            rc = desc->save_instance(w, &payload);
        }

        if (rc != 0) {
            d_tlv_builder_reset(&builder);
            return rc;
        }

        tag = d_tag_for_subsystem(desc->subsystem_id);
        if (tag == 0u) {
            fprintf(stderr, "d_serialize: unknown tag for subsystem %u\n", (unsigned int)desc->subsystem_id);
            d_tlv_builder_reset(&builder);
            return -1;
        }
        if (payload.len > 0u && payload.ptr == (unsigned char *)0) {
            fprintf(stderr, "d_serialize: subsystem %u returned null payload\n", (unsigned int)desc->subsystem_id);
            d_tlv_builder_reset(&builder);
            return -1;
        }
        rc = d_tlv_builder_append_entry(&builder, tag, payload.ptr, payload.len);
        if (rc != 0) {
            d_tlv_builder_reset(&builder);
            return rc;
        }
    }

    out->ptr = builder.data;
    out->len = builder.length;
    return 0;
}

static int d_serialize_load_all(struct d_world *w, struct d_chunk *chunk, const struct d_tlv_blob *in, int use_chunk_callbacks) {
    u32 offset;
    if (!in) {
        return -1;
    }
    if (!in->ptr || in->len == 0u) {
        return 0;
    }

    offset = 0u;
    while (offset < in->len) {
        u32 remaining = in->len - offset;
        u32 tag;
        u32 len;
        d_tlv_blob payload;
        d_subsystem_id sid;
        const d_subsystem_desc *desc;
        int rc;

        if (remaining < 8u) {
            fprintf(stderr, "d_serialize: truncated TLV header\n");
            return -1;
        }

        memcpy(&tag, in->ptr + offset, sizeof(u32));
        memcpy(&len, in->ptr + offset + 4u, sizeof(u32));
        offset += 8u;

        if (len > in->len - offset) {
            fprintf(stderr, "d_serialize: truncated TLV payload\n");
            return -1;
        }

        payload.ptr = (unsigned char *)(in->ptr + offset);
        payload.len = len;
        offset += len;

        sid = d_subsystem_for_tag(tag);
        if (sid == 0u) {
            continue;
        }
        desc = d_subsystem_get_by_id(sid);
        if (!desc) {
            continue;
        }

        if (use_chunk_callbacks) {
            if (!desc->load_chunk) {
                continue;
            }
            {
                const d_tlv_blob payload_view = { payload.ptr, payload.len };
                rc = desc->load_chunk(w, chunk, &payload_view);
            }
        } else {
            if (!desc->load_instance) {
                continue;
            }
            {
                const d_tlv_blob payload_view = { payload.ptr, payload.len };
                rc = desc->load_instance(w, &payload_view);
            }
        }
        if (rc != 0) {
            return rc;
        }
    }

    return 0;
}

int d_serialize_save_chunk_all(
    struct d_world    *w,
    struct d_chunk    *chunk,
    struct d_tlv_blob *out
) {
    return d_serialize_save_all(w, chunk, out, 1);
}

int d_serialize_load_chunk_all(
    struct d_world          *w,
    struct d_chunk          *chunk,
    const struct d_tlv_blob *in
) {
    return d_serialize_load_all(w, chunk, in, 1);
}

int d_serialize_save_instance_all(
    struct d_world    *w,
    struct d_tlv_blob *out
) {
    return d_serialize_save_all(w, (struct d_chunk *)0, out, 0);
}

int d_serialize_load_instance_all(
    struct d_world          *w,
    const struct d_tlv_blob *in
) {
    return d_serialize_load_all(w, (struct d_chunk *)0, in, 0);
}
