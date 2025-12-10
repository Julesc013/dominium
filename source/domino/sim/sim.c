#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/rng.h"
#include "domino/sim/sim.h"

#define TLV_WORLD_CONFIG 1
#define TLV_WORLD_TILES  2
#define WORLD_MAGIC_0 'D'
#define WORLD_MAGIC_1 'W'
#define WORLD_MAGIC_2 'R'
#define WORLD_MAGIC_3 'L'
#define WORLD_VERSION  1

struct d_world {
    d_world_config cfg;
    d_rng_state    rng;
    u32            tick_count;

    u32            width;
    u32            height;

    u16*           tile_type;
    q24_8*         tile_height;
};

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

d_world* d_world_create(const d_world_config* cfg) {
    struct d_world* w;
    u32 count;

    if (!cfg) return (d_world*)0;
    if (cfg->width == 0 || cfg->height == 0) return (d_world*)0;
    if (cfg->width > 1024 || cfg->height > 1024) return (d_world*)0;
    if (cfg->width > (0xFFFFFFFFu / cfg->height)) return (d_world*)0; /* overflow guard */

    w = (struct d_world*)malloc(sizeof(struct d_world));
    if (!w) return (d_world*)0;
    memset(w, 0, sizeof(*w));

    w->cfg = *cfg;
    w->width = cfg->width;
    w->height = cfg->height;
    w->tick_count = 0;
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

void d_world_destroy(d_world* world) {
    struct d_world* w = (struct d_world*)world;
    if (!w) return;
    if (w->tile_type) {
        free(w->tile_type);
        w->tile_type = 0;
    }
    if (w->tile_height) {
        free(w->tile_height);
        w->tile_height = 0;
    }
    free(w);
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

    hash ^= w->cfg.seed; hash *= 16777619u;
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

d_bool d_world_save_tlv(const d_world* world, const char* path) {
    const struct d_world* w = (const struct d_world*)world;
    FILE* f;
    u32 count;
    u32 len;
    u32 i;

    if (!w || !path) return D_FALSE;
    f = fopen(path, "wb");
    if (!f) return D_FALSE;

    if (fwrite("DWRL", 1, 4, f) != 4) { fclose(f); return D_FALSE; }
    if (!d_write_u16(f, (u16)WORLD_VERSION)) { fclose(f); return D_FALSE; }

    /* WORLD_CONFIG TLV */
    if (!d_write_u16(f, (u16)TLV_WORLD_CONFIG)) { fclose(f); return D_FALSE; }
    if (!d_write_u32(f, (u32)16)) { fclose(f); return D_FALSE; }
    if (!d_write_u32(f, w->cfg.seed)) { fclose(f); return D_FALSE; }
    if (!d_write_u32(f, w->width)) { fclose(f); return D_FALSE; }
    if (!d_write_u32(f, w->height)) { fclose(f); return D_FALSE; }
    if (!d_write_u32(f, w->tick_count)) { fclose(f); return D_FALSE; }

    /* WORLD_TILES TLV */
    count = w->width * w->height;
    len = count * (2 + 4); /* u16 + i32 per tile */
    if (!d_write_u16(f, (u16)TLV_WORLD_TILES)) { fclose(f); return D_FALSE; }
    if (!d_write_u32(f, len)) { fclose(f); return D_FALSE; }
    for (i = 0; i < count; ++i) {
        if (!d_write_u16(f, w->tile_type[i])) { fclose(f); return D_FALSE; }
        if (!d_write_i32(f, (i32)w->tile_height[i])) { fclose(f); return D_FALSE; }
    }

    fclose(f);
    return D_TRUE;
}

d_world* d_world_load_tlv(const char* path) {
    FILE* f;
    char magic[4];
    u16 version;
    u16 tlv_type;
    u32 tlv_len;
    d_world_config cfg;
    d_bool cfg_read = D_FALSE;
    d_bool tiles_read = D_FALSE;
    struct d_world* w = 0;
    u32 loaded_tick_count = 0;

    if (!path) return (d_world*)0;
    f = fopen(path, "rb");
    if (!f) return (d_world*)0;

    if (fread(magic, 1, 4, f) != 4) { fclose(f); return (d_world*)0; }
    if (magic[0] != WORLD_MAGIC_0 || magic[1] != WORLD_MAGIC_1 || magic[2] != WORLD_MAGIC_2 || magic[3] != WORLD_MAGIC_3) {
        fclose(f);
        return (d_world*)0;
    }
    if (!d_read_u16(f, &version)) { fclose(f); return (d_world*)0; }
    if (version != WORLD_VERSION) { fclose(f); return (d_world*)0; }

    memset(&cfg, 0, sizeof(cfg));

    while (d_read_u16(f, &tlv_type)) {
        if (!d_read_u32(f, &tlv_len)) { fclose(f); return (d_world*)0; }
        if (tlv_type == TLV_WORLD_CONFIG) {
            if (tlv_len != 16) { fclose(f); return (d_world*)0; }
            if (!d_read_u32(f, &cfg.seed)) { fclose(f); return (d_world*)0; }
            if (!d_read_u32(f, &cfg.width)) { fclose(f); return (d_world*)0; }
            if (!d_read_u32(f, &cfg.height)) { fclose(f); return (d_world*)0; }
            if (!d_read_u32(f, &loaded_tick_count)) { fclose(f); return (d_world*)0; }
            cfg_read = D_TRUE;
        } else if (tlv_type == TLV_WORLD_TILES) {
            u32 count;
            u32 i;
            if (!cfg_read) { fclose(f); return (d_world*)0; }
            count = cfg.width * cfg.height;
            if (tlv_len != count * (2 + 4)) { fclose(f); return (d_world*)0; }
            w = (struct d_world*)d_world_create(&cfg);
            if (!w) { fclose(f); return (d_world*)0; }
            w->tick_count = loaded_tick_count;
            for (i = 0; i < count; ++i) {
                u16 ttype;
                i32 theight;
                if (!d_read_u16(f, &ttype)) { d_world_destroy((d_world*)w); fclose(f); return (d_world*)0; }
                if (!d_read_i32(f, &theight)) { d_world_destroy((d_world*)w); fclose(f); return (d_world*)0; }
                w->tile_type[i] = ttype;
                w->tile_height[i] = (q24_8)theight;
            }
            tiles_read = D_TRUE;
        } else {
            /* skip unknown TLV */
            if (fseek(f, (long)tlv_len, SEEK_CUR) != 0) { fclose(f); return (d_world*)0; }
        }
    }

    fclose(f);
    if (cfg_read && tiles_read) {
        return (d_world*)w;
    }
    if (w) {
        d_world_destroy((d_world*)w);
    }
    return (d_world*)0;
}
