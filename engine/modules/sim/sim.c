/*
FILE: source/domino/sim/sim.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/sim
RESPONSIBILITY: Implements `sim`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/rng.h"
#include "core/d_subsystem.h"
#include "core/d_serialize_tags.h"
#include "domino/core/d_tlv.h"
#include "world/d_serialize.h"
#include "domino/sim/sim.h"

#define TLV_WORLD_CONFIG 1
#define TLV_WORLD_TILES  2
#define WORLD_MAGIC_0 'D'
#define WORLD_MAGIC_1 'W'
#define WORLD_MAGIC_2 'R'
#define WORLD_MAGIC_3 'L'
#define WORLD_VERSION        2
#define WORLD_VERSION_LEGACY 1

static int g_world_subsystem_registered = 0;
static unsigned char *g_world_save_blob = (unsigned char *)0;
static int d_world_save_instance_subsys(struct d_world *w, struct d_tlv_blob *out);
static int d_world_load_instance_subsys(struct d_world *w, const struct d_tlv_blob *in);

static q24_8 d_q24_8_saturate_i64(i64 v) {
    if (v > (i64)0x7FFFFFFF) {
        return (q24_8)0x7FFFFFFF;
    }
    if (v < (i64)0x80000000) {
        return (q24_8)0x80000000;
    }
    return (q24_8)v;
}

static q24_8 d_q24_8_add_saturate(q24_8 a, q24_8 b) {
    i64 sum = (i64)a + (i64)b;
    return d_q24_8_saturate_i64(sum);
}

static void d_world_init_tiles(struct d_world* w) {
    u32 count = w->width * w->height;
    u32 i;
    for (i = 0; i < count; ++i) {
        w->tile_type[i] = (u16)(d_rng_next_u32(&w->rng) & 3u);
        {
            u32 r = d_rng_next_u32(&w->rng);
            i32 base = (i32)(r & 0xFFu);
            base -= 128;
            w->tile_height[i] = (q24_8)(base << Q24_8_FRAC_BITS);
        }
    }
}

d_world* d_world_create_from_config(const d_world_config* cfg) {
    d_world_meta meta;
    d_world* w;
    u32 count;

    if (!cfg) return (d_world*)0;
    if (cfg->width == 0 || cfg->height == 0) return (d_world*)0;
    if (cfg->width > 1024 || cfg->height > 1024) return (d_world*)0;
    if (cfg->width > (0xFFFFFFFFu / cfg->height)) return (d_world*)0; /* overflow guard */

    meta.seed = cfg->seed;
    meta.world_size_m = cfg->width;
    meta.vertical_min = d_q16_16_from_int(-2000);
    meta.vertical_max = d_q16_16_from_int(2000);
    meta.core_version = 1u;
    meta.suite_version = 1u;
    meta.compat_profile_id = 0u;
    meta.extra.ptr = (unsigned char *)0;
    meta.extra.len = 0u;

    w = d_world_create(&meta);
    if (!w) {
        return (d_world *)0;
    }

    w->width = cfg->width;
    w->height = cfg->height;
    w->tick_count = 0u;
    d_rng_seed(&w->rng, cfg->seed);

    count = w->width * w->height;
    w->tile_type = (u16*)malloc(sizeof(u16) * count);
    w->tile_height = (q24_8*)malloc(sizeof(q24_8) * count);
    if (!w->tile_type || !w->tile_height) {
        d_world_destroy((d_world*)w);
        return (d_world*)0;
    }

    d_world_init_tiles(w);
    return (d_world*)w;
}

void d_world_destroy_instance(d_world* world) {
    if (!world) {
        return;
    }
    d_world_destroy((d_world*)world);
}

void d_world_tick(d_world* world) {
    struct d_world* w = (struct d_world*)world;
    u32 count;
    u32 i;
    if (!w) return;

    count = w->width * w->height;
    for (i = 0; i < count; ++i) {
        u32 r = d_rng_next_u32(&w->rng);
        i32 delta = (i32)((r & 0x0Fu) - 8); /* -8..+7 */
        q24_8 dh = (q24_8)(delta << (Q24_8_FRAC_BITS - 4));
        w->tile_height[i] = d_q24_8_add_saturate(w->tile_height[i], dh);
        if (r & 0x100u) {
            w->tile_type[i] = (u16)((w->tile_type[i] + 1u) & 3u);
        }
    }
    w->tick_count += 1u;
}

u32 d_world_checksum(const d_world* world) {
    const struct d_world* w = (const struct d_world*)world;
    u32 hash = 2166136261u;
    u32 count;
    u32 i;
    if (!w) return 0u;

    count = w->width * w->height;

    hash ^= (u32)(w->meta.seed & 0xFFFFFFFFu); hash *= 16777619u;
    hash ^= w->width;    hash *= 16777619u;
    hash ^= w->height;   hash *= 16777619u;
    hash ^= w->tick_count; hash *= 16777619u;

    for (i = 0; i < count; ++i) {
        hash ^= (u32)w->tile_type[i];
        hash *= 16777619u;
    }
    for (i = 0; i < count; ++i) {
        u32 v = (u32)w->tile_height[i];
        hash ^= v;
        hash *= 16777619u;
    }
    return hash;
}

static d_bool d_write_u16(FILE* f, u16 v) {
    return fwrite(&v, sizeof(u16), 1, f) == 1;
}
static d_bool d_write_u32(FILE* f, u32 v) {
    return fwrite(&v, sizeof(u32), 1, f) == 1;
}
static d_bool d_write_i32(FILE* f, i32 v) {
    return fwrite(&v, sizeof(i32), 1, f) == 1;
}

static d_bool d_read_u16(FILE* f, u16* v) {
    return fread(v, sizeof(u16), 1, f) == 1;
}
static d_bool d_read_u32(FILE* f, u32* v) {
    return fread(v, sizeof(u32), 1, f) == 1;
}
static d_bool d_read_i32(FILE* f, i32* v) {
    return fread(v, sizeof(i32), 1, f) == 1;
}

static void d_world_release_save_blob(void) {
    if (g_world_save_blob) {
        free(g_world_save_blob);
        g_world_save_blob = (unsigned char *)0;
    }
}

static int d_world_register_subsystem(void) {
    d_subsystem_desc desc;
    const d_subsystem_desc *existing;
    int rc;

    if (g_world_subsystem_registered) {
        return 1;
    }
    existing = d_subsystem_get_by_id(D_SUBSYS_WORLD);
    if (existing) {
        g_world_subsystem_registered = 1;
        return 1;
    }

    desc.subsystem_id = D_SUBSYS_WORLD;
    desc.name = "world";
    desc.version = 1u;
    desc.register_models = (void (*)(void))0;
    desc.load_protos = (void (*)(const struct d_tlv_blob *))0;
    desc.init_instance = (void (*)(struct d_world *))0;
    desc.tick = (void (*)(struct d_world *, u32))0;
    desc.save_chunk = (int (*)(struct d_world *, struct d_chunk *, struct d_tlv_blob *))0;
    desc.load_chunk = (int (*)(struct d_world *, struct d_chunk *, const struct d_tlv_blob *))0;
    desc.save_instance = d_world_save_instance_subsys;
    desc.load_instance = d_world_load_instance_subsys;

    rc = d_subsystem_register(&desc);
    if (rc == 0) {
        g_world_subsystem_registered = 1;
        return 1;
    }
    return 0;
}

static int d_world_save_instance_subsys(struct d_world *w, struct d_tlv_blob *out) {
    u32 count;
    u32 len_tiles;
    u32 total_len;
    unsigned char *buf;
    unsigned char *dst;
    u16 type;
    u32 config_len;
    u32 i;

    if (!w || !out) {
        return -1;
    }

    d_world_release_save_blob();

    count = w->width * w->height;
    len_tiles = count * (2u + 4u);
    if (count != 0u && len_tiles / count != 6u) {
        return -1;
    }
    config_len = 16u;
    total_len = 2u + 4u + config_len + 2u + 4u + len_tiles;
    if (total_len < len_tiles) {
        return -1;
    }

    buf = (unsigned char *)malloc(total_len);
    if (!buf && total_len != 0u) {
        return -1;
    }
    dst = buf;

    {
        u32 seed32 = (u32)(w->meta.seed & 0xFFFFFFFFu);
        type = (u16)TLV_WORLD_CONFIG;
        memcpy(dst, &type, sizeof(u16));
        dst += 2u;
        memcpy(dst, &config_len, sizeof(u32));
        dst += 4u;
        memcpy(dst, &seed32, sizeof(u32));
        dst += 4u;
    }
    memcpy(dst, &w->width, sizeof(u32));
    dst += 4u;
    memcpy(dst, &w->height, sizeof(u32));
    dst += 4u;
    memcpy(dst, &w->tick_count, sizeof(u32));
    dst += 4u;

    type = (u16)TLV_WORLD_TILES;
    memcpy(dst, &type, sizeof(u16));
    dst += 2u;
    memcpy(dst, &len_tiles, sizeof(u32));
    dst += 4u;

    for (i = 0u; i < count; ++i) {
        i32 theight = (i32)w->tile_height[i];
        memcpy(dst, &w->tile_type[i], sizeof(u16));
        dst += 2u;
        memcpy(dst, &theight, sizeof(i32));
        dst += 4u;
    }

    out->ptr = buf;
    out->len = total_len;
    g_world_save_blob = buf;
    return 0;
}

static int d_world_load_instance_subsys(struct d_world *w, const struct d_tlv_blob *in) {
    u32 offset;
    int cfg_read = 0;
    int tiles_read = 0;
    u32 loaded_tick = 0u;
    u32 cfg_seed = 0u;
    u32 cfg_width = 0u;
    u32 cfg_height = 0u;

    if (!w || !in) {
        return -1;
    }
    if (in->len > 0u && !in->ptr) {
        return -1;
    }

    offset = 0u;
    while (offset + 6u <= in->len) {
        u16 tlv_type;
        u32 tlv_len;

        memcpy(&tlv_type, in->ptr + offset, sizeof(u16));
        memcpy(&tlv_len, in->ptr + offset + 2u, sizeof(u32));
        offset += 6u;

        if (tlv_len > in->len - offset) {
            return -1;
        }

        if (tlv_type == TLV_WORLD_CONFIG) {
            if (tlv_len != 16u) {
                return -1;
            }
            memcpy(&cfg_seed, in->ptr + offset, sizeof(u32));
            memcpy(&cfg_width, in->ptr + offset + 4u, sizeof(u32));
            memcpy(&cfg_height, in->ptr + offset + 8u, sizeof(u32));
            memcpy(&loaded_tick, in->ptr + offset + 12u, sizeof(u32));
            if (cfg_width != w->width || cfg_height != w->height) {
                return -1;
            }
            w->meta.seed = cfg_seed;
            d_rng_seed(&w->rng, w->meta.seed);
            cfg_read = 1;
        } else if (tlv_type == TLV_WORLD_TILES) {
            u32 count;
            u32 i;
            const unsigned char *p;
            if (!cfg_read) {
                return -1;
            }
            count = w->width * w->height;
            if (tlv_len != count * (2u + 4u)) {
                return -1;
            }
            p = in->ptr + offset;
            for (i = 0u; i < count; ++i) {
                u16 ttype;
                i32 theight;
                memcpy(&ttype, p, sizeof(u16));
                p += 2u;
                memcpy(&theight, p, sizeof(i32));
                p += 4u;
                w->tile_type[i] = ttype;
                w->tile_height[i] = (q24_8)theight;
            }
            tiles_read = 1;
        }
        offset += tlv_len;
    }

    if (offset != in->len) {
        return -1;
    }
    if (!cfg_read || !tiles_read) {
        return -1;
    }
    w->tick_count = loaded_tick;
    return 0;
}

static int d_world_find_payload(const d_tlv_blob *container, d_tlv_blob *out_payload) {
    u32 offset;
    if (!container || !out_payload) {
        return -1;
    }
    if (container->len > 0u && !container->ptr) {
        return -1;
    }

    offset = 0u;
    while (offset + 8u <= container->len) {
        u32 tag;
        u32 len;
        memcpy(&tag, container->ptr + offset, sizeof(u32));
        memcpy(&len, container->ptr + offset + 4u, sizeof(u32));
        offset += 8u;
        if (len > container->len - offset) {
            return -1;
        }
        if (tag == TAG_SUBSYS_DWORLD) {
            out_payload->ptr = container->ptr + offset;
            out_payload->len = len;
            return 0;
        }
        offset += len;
    }
    return -1;
}

static int d_world_extract_config(const d_tlv_blob *payload, d_world_config *out_cfg, u32 *out_tick_count) {
    u32 offset;
    if (!payload || !out_cfg || !out_tick_count) {
        return -1;
    }
    if (payload->len > 0u && !payload->ptr) {
        return -1;
    }

    memset(out_cfg, 0, sizeof(*out_cfg));
    *out_tick_count = 0u;

    offset = 0u;
    while (offset + 6u <= payload->len) {
        u16 tlv_type;
        u32 tlv_len;
        memcpy(&tlv_type, payload->ptr + offset, sizeof(u16));
        memcpy(&tlv_len, payload->ptr + offset + 2u, sizeof(u32));
        offset += 6u;
        if (tlv_len > payload->len - offset) {
            return -1;
        }
        if (tlv_type == TLV_WORLD_CONFIG) {
            if (tlv_len != 16u) {
                return -1;
            }
            memcpy(&out_cfg->seed, payload->ptr + offset, sizeof(u32));
            memcpy(&out_cfg->width, payload->ptr + offset + 4u, sizeof(u32));
            memcpy(&out_cfg->height, payload->ptr + offset + 8u, sizeof(u32));
            memcpy(out_tick_count, payload->ptr + offset + 12u, sizeof(u32));
            return 0;
        }
        offset += tlv_len;
    }
    return -1;
}

d_world* d_world_clone(const d_world* world) {
    d_tlv_blob container;
    d_tlv_blob world_payload;
    d_world_config cfg;
    u32 loaded_tick = 0u;
    struct d_world* cloned = 0;
    int rc;

    if (!world) {
        return (d_world*)0;
    }
    if (!d_world_register_subsystem()) {
        return (d_world*)0;
    }

    container.ptr = (unsigned char*)0;
    container.len = 0u;
    rc = d_serialize_save_instance_all((struct d_world*)world, &container);
    d_world_release_save_blob();
    if (rc != 0 || (container.len > 0u && !container.ptr)) {
        if (container.ptr) {
            free(container.ptr);
        }
        return (d_world*)0;
    }

    if (d_world_find_payload(&container, &world_payload) != 0 ||
        d_world_extract_config(&world_payload, &cfg, &loaded_tick) != 0) {
        if (container.ptr) {
            free(container.ptr);
        }
        return (d_world*)0;
    }

    cloned = (struct d_world*)d_world_create_from_config(&cfg);
    if (!cloned) {
        if (container.ptr) {
            free(container.ptr);
        }
        return (d_world*)0;
    }
    cloned->tick_count = loaded_tick;

    if (d_serialize_load_instance_all(cloned, &container) != 0) {
        d_world_destroy((d_world*)cloned);
        cloned = 0;
    }
    if (container.ptr) {
        free(container.ptr);
    }
    return (d_world*)cloned;
}

static d_world* d_world_load_v1(FILE *f) {
    u16 tlv_type;
    u32 tlv_len;
    d_world_config cfg;
    d_bool cfg_read = D_FALSE;
    d_bool tiles_read = D_FALSE;
    struct d_world* w = 0;
    u32 loaded_tick_count = 0;

    if (!f) return (d_world*)0;

    memset(&cfg, 0, sizeof(cfg));

    while (d_read_u16(f, &tlv_type)) {
        if (!d_read_u32(f, &tlv_len)) { if (w) d_world_destroy((d_world*)w); return (d_world*)0; }
        if (tlv_type == TLV_WORLD_CONFIG) {
            if (tlv_len != 16) { if (w) d_world_destroy((d_world*)w); return (d_world*)0; }
            if (!d_read_u32(f, &cfg.seed)) { if (w) d_world_destroy((d_world*)w); return (d_world*)0; }
            if (!d_read_u32(f, &cfg.width)) { if (w) d_world_destroy((d_world*)w); return (d_world*)0; }
            if (!d_read_u32(f, &cfg.height)) { if (w) d_world_destroy((d_world*)w); return (d_world*)0; }
            if (!d_read_u32(f, &loaded_tick_count)) { if (w) d_world_destroy((d_world*)w); return (d_world*)0; }
            cfg_read = D_TRUE;
        } else if (tlv_type == TLV_WORLD_TILES) {
            u32 count;
            u32 i;
            if (!cfg_read) { if (w) d_world_destroy((d_world*)w); return (d_world*)0; }
            count = cfg.width * cfg.height;
            if (tlv_len != count * (2 + 4)) { if (w) d_world_destroy((d_world*)w); return (d_world*)0; }
            w = (struct d_world*)d_world_create_from_config(&cfg);
            if (!w) { return (d_world*)0; }
            w->tick_count = loaded_tick_count;
            for (i = 0; i < count; ++i) {
                u16 ttype;
                i32 theight;
                if (!d_read_u16(f, &ttype)) { d_world_destroy((d_world*)w); return (d_world*)0; }
                if (!d_read_i32(f, &theight)) { d_world_destroy((d_world*)w); return (d_world*)0; }
                w->tile_type[i] = ttype;
                w->tile_height[i] = (q24_8)theight;
            }
            tiles_read = D_TRUE;
        } else {
            if (fseek(f, (long)tlv_len, SEEK_CUR) != 0) { if (w) d_world_destroy((d_world*)w); return (d_world*)0; }
        }
    }

    if (cfg_read && tiles_read) {
        return (d_world*)w;
    }
    if (w) {
        d_world_destroy((d_world*)w);
    }
    return (d_world*)0;
}

static d_world* d_world_load_v2(FILE *f) {
    long payload_start;
    long file_end;
    u32 data_len;
    unsigned char *buffer;
    d_tlv_blob container;
    d_tlv_blob world_payload;
    d_world_config cfg;
    u32 loaded_tick = 0u;
    struct d_world *w;

    if (!f) return (d_world*)0;

    payload_start = ftell(f);
    if (payload_start < 0) {
        return (d_world*)0;
    }
    if (fseek(f, 0, SEEK_END) != 0) {
        return (d_world*)0;
    }
    file_end = ftell(f);
    if (file_end < payload_start) {
        return (d_world*)0;
    }
    data_len = (u32)(file_end - payload_start);
    if (fseek(f, payload_start, SEEK_SET) != 0) {
        return (d_world*)0;
    }

    buffer = (unsigned char *)malloc(data_len);
    if (!buffer && data_len != 0u) {
        return (d_world*)0;
    }
    if (data_len > 0u) {
        if (fread(buffer, 1, data_len, f) != data_len) {
            free(buffer);
            return (d_world*)0;
        }
    }

    container.ptr = buffer;
    container.len = data_len;

    if (d_world_find_payload(&container, &world_payload) != 0) {
        free(buffer);
        return (d_world*)0;
    }
    if (d_world_extract_config(&world_payload, &cfg, &loaded_tick) != 0) {
        free(buffer);
        return (d_world*)0;
    }

    w = (struct d_world*)d_world_create_from_config(&cfg);
    if (!w) {
        free(buffer);
        return (d_world*)0;
    }
    w->tick_count = loaded_tick;

    if (!d_world_register_subsystem()) {
        free(buffer);
        d_world_destroy((d_world*)w);
        return (d_world*)0;
    }

    if (d_serialize_load_instance_all((struct d_world *)w, &container) != 0) {
        free(buffer);
        d_world_destroy((d_world*)w);
        return (d_world*)0;
    }

    free(buffer);
    return (d_world*)w;
}

d_bool d_world_save_tlv(const d_world* world, const char* path) {
    const struct d_world* w = (const struct d_world*)world;
    FILE* f = (FILE *)0;
    d_tlv_blob blob;
    int rc;

    if (!w || !path) return D_FALSE;

    blob.ptr = (unsigned char *)0;
    blob.len = 0u;

    if (!d_world_register_subsystem()) {
        return D_FALSE;
    }

    rc = d_serialize_save_instance_all((struct d_world *)world, &blob);
    d_world_release_save_blob();
    if (rc != 0) {
        if (blob.ptr) {
            free(blob.ptr);
        }
        return D_FALSE;
    }

    f = fopen(path, "wb");
    if (!f) {
        if (blob.ptr) {
            free(blob.ptr);
        }
        return D_FALSE;
    }

    if (fwrite("DWRL", 1, 4, f) != 4) { fclose(f); if (blob.ptr) free(blob.ptr); return D_FALSE; }
    if (!d_write_u16(f, (u16)WORLD_VERSION)) { fclose(f); if (blob.ptr) free(blob.ptr); return D_FALSE; }
    if (blob.len > 0u) {
        if (fwrite(blob.ptr, 1, blob.len, f) != blob.len) { fclose(f); if (blob.ptr) free(blob.ptr); return D_FALSE; }
    }

    fclose(f);
    if (blob.ptr) {
        free(blob.ptr);
    }
    return D_TRUE;
}

d_world* d_world_load_tlv(const char* path) {
    FILE* f;
    char magic[4];
    u16 version;
    d_world* w = (d_world*)0;

    if (!path) return (d_world*)0;
    f = fopen(path, "rb");
    if (!f) return (d_world*)0;

    if (fread(magic, 1, 4, f) != 4) { fclose(f); return (d_world*)0; }
    if (magic[0] != WORLD_MAGIC_0 || magic[1] != WORLD_MAGIC_1 || magic[2] != WORLD_MAGIC_2 || magic[3] != WORLD_MAGIC_3) {
        fclose(f);
        return (d_world*)0;
    }
    if (!d_read_u16(f, &version)) { fclose(f); return (d_world*)0; }

    if (version == WORLD_VERSION_LEGACY) {
        w = d_world_load_v1(f);
    } else if (version == WORLD_VERSION) {
        w = d_world_load_v2(f);
    } else {
        w = (d_world*)0;
    }

    fclose(f);
    return w;
}
