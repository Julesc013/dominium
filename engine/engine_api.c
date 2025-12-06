#include "engine_api.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <direct.h>
#else
#include <sys/stat.h>
#include <sys/types.h>
#endif

#include "save_universe.h"
#include "save_region.h"
#include "world_surface.h"
#include "registry_material.h"
#include "registry_volume.h"
#include "registry_recipe.h"
#include "sim_systems.h"

#define UNIVERSE_META_VERSION 1
#define SURFACE_META_VERSION  1
#define DEFAULT_MAX_SURFACES  4U

struct Engine {
    EngineConfig    config;
    UniverseMeta    meta;
    SurfaceRuntime *surfaces;
    u32             surface_count;
    u32             surface_capacity;
    MaterialRegistry mat_reg;
    VolumeRegistry   vol_reg;
    RecipeRegistry   recipe_reg;
    WorldServices    services;
};

static void create_dir(const char *path)
{
    if (!path || !path[0]) return;
#ifdef _WIN32
    _mkdir(path);
#else
    mkdir(path, 0755);
#endif
}

static void ensure_directory(const char *path)
{
    char tmp[512];
    size_t i;
    size_t len;
    if (!path) return;
    len = strlen(path);
    if (len >= sizeof(tmp)) len = sizeof(tmp) - 1;
    memset(tmp, 0, sizeof(tmp));
    for (i = 0; i < len; ++i) {
        char c = path[i];
        tmp[i] = c;
        tmp[i + 1] = '\0';
        if (c == '/' || c == '\\') {
            create_dir(tmp);
        }
    }
    tmp[len] = '\0';
    create_dir(tmp);
}

static void path_join(char *out, size_t cap, const char *base, const char *leaf)
{
    size_t i = 0;
    size_t j = 0;
    size_t base_len;
    if (!out || cap == 0) return;
    out[0] = '\0';
    if (!base) base = "";
    if (!leaf) leaf = "";
    base_len = strlen(base);
    if (base_len >= cap) base_len = cap - 1;
    for (i = 0; i < base_len; ++i) {
        out[i] = base[i];
    }
    if (i > 0 && i < cap - 1) {
        char c = out[i - 1];
        if (c != '/' && c != '\\') {
            out[i++] = '/';
        }
    }
    while (leaf[j] && i < cap - 1) {
        out[i++] = leaf[j++];
    }
    out[i] = '\0';
}

static void init_registries(struct Engine *engine)
{
    MaterialDesc air;
    MaterialDesc stone;
    RecipeDesc base_recipe;
    if (!engine) return;
    material_registry_init(&engine->mat_reg, 8);
    volume_registry_init(&engine->vol_reg, 4);
    recipe_registry_init(&engine->recipe_reg, 4);

    memset(&air, 0, sizeof(air));
    air.name = "air";
    air.density = 0;
    air.hardness = 0;
    air.melting_point = 0;
    air.boiling_point = 0;
    material_register(&engine->mat_reg, &air);

    memset(&stone, 0, sizeof(stone));
    stone.name = "stone";
    stone.density = fix32_from_int(2600);
    stone.hardness = fix32_from_int(5);
    stone.melting_point = fix32_from_int(1500);
    stone.boiling_point = fix32_from_int(3000);
    material_register(&engine->mat_reg, &stone);

    memset(&base_recipe, 0, sizeof(base_recipe));
    base_recipe.name = "default_surface";
    base_recipe.base_height_m = 32;
    base_recipe.height_range_m = 24;
    recipe_register(&engine->recipe_reg, &base_recipe);
}

static void free_registries(struct Engine *engine)
{
    material_registry_free(&engine->mat_reg);
    volume_registry_free(&engine->vol_reg);
    recipe_registry_free(&engine->recipe_reg);
}

static SurfaceRuntime *find_surface(struct Engine *engine, u32 surface_id)
{
    u32 i;
    for (i = 0; i < engine->surface_count; ++i) {
        if (engine->surfaces[i].surface_id == surface_id) {
            return &engine->surfaces[i];
        }
    }
    return NULL;
}

static b32 ensure_surface_capacity(struct Engine *engine, u32 needed)
{
    u32 new_cap;
    SurfaceRuntime *new_arr;
    if (engine->surface_capacity >= needed) {
        return TRUE;
    }
    new_cap = (engine->surface_capacity == 0) ? DEFAULT_MAX_SURFACES : (engine->surface_capacity * 2U);
    if (new_cap < needed) new_cap = needed;
    new_arr = (SurfaceRuntime *)realloc(engine->surfaces, sizeof(SurfaceRuntime) * new_cap);
    if (!new_arr) {
        return FALSE;
    }
    engine->surfaces = new_arr;
    engine->surface_capacity = new_cap;
    return TRUE;
}

static SurfaceRuntime *create_surface(struct Engine *engine, const SurfaceMeta *meta)
{
    SurfaceRuntime *surface;
    if (engine->surface_count >= engine->config.max_surfaces) {
        return NULL;
    }
    if (!ensure_surface_capacity(engine, engine->surface_count + 1U)) {
        return NULL;
    }
    surface = &engine->surfaces[engine->surface_count++];
    surface_runtime_init(surface,
                         meta->surface_id,
                         meta->seed,
                         &engine->mat_reg,
                         &engine->vol_reg,
                         &engine->recipe_reg,
                         meta->recipe_id);
    surface->rng_weather = meta->rng_weather;
    surface->rng_hydro = meta->rng_hydro;
    surface->rng_misc = meta->rng_misc;
    return surface;
}

Engine *engine_create(const EngineConfig *cfg)
{
    Engine *engine = (Engine *)malloc(sizeof(Engine));
    if (!engine) {
        return NULL;
    }
    memset(engine, 0, sizeof(*engine));
    if (cfg) {
        engine->config = *cfg;
    } else {
        engine->config.max_surfaces = DEFAULT_MAX_SURFACES;
        engine->config.universe_seed = 1;
    }
    if (engine->config.max_surfaces == 0) {
        engine->config.max_surfaces = DEFAULT_MAX_SURFACES;
    }
    if (engine->config.universe_seed == 0) {
        engine->config.universe_seed = 1;
    }
    engine->meta.version = UNIVERSE_META_VERSION;
    engine->meta.universe_seed = engine->config.universe_seed;
    init_registries(engine);
    world_services_init(&engine->services);
    return engine;
}

void engine_destroy(Engine *engine)
{
    u32 i;
    if (!engine) return;
    for (i = 0; i < engine->surface_count; ++i) {
        surface_runtime_free(&engine->surfaces[i]);
    }
    if (engine->surfaces) {
        free(engine->surfaces);
        engine->surfaces = NULL;
    }
    free_registries(engine);
    free(engine);
}

static void surface_meta_from_runtime(const SurfaceRuntime *surface, SurfaceMeta *out_meta)
{
    if (!surface || !out_meta) return;
    out_meta->version = SURFACE_META_VERSION;
    out_meta->surface_id = surface->surface_id;
    out_meta->seed = surface->seed;
    out_meta->recipe_id = surface->recipe_id;
    out_meta->rng_weather = surface->rng_weather;
    out_meta->rng_hydro = surface->rng_hydro;
    out_meta->rng_misc = surface->rng_misc;
}

static void build_surface_meta_path(char *out, size_t cap, const char *base, u32 surface_id)
{
    char leaf[64];
    sprintf(leaf, "surface_%03u.meta", surface_id);
    path_join(out, cap, base, leaf);
}

static void build_region_path(char *out, size_t cap, const char *base, u32 surface_id)
{
    char leaf[64];
    char dir_path[512];
    path_join(dir_path, sizeof(dir_path), base, "regions");
    ensure_directory(dir_path);
    sprintf(leaf, "surface_%03u_region.bin", surface_id);
    path_join(out, cap, dir_path, leaf);
}

b32 engine_load_universe(Engine *engine, const char *universe_path)
{
    char meta_path[512];
    UniverseMeta meta;
    if (!engine || !universe_path) return FALSE;
    ensure_directory(universe_path);
    path_join(meta_path, sizeof(meta_path), universe_path, "universe.meta");
    if (!load_universe_meta(meta_path, &meta)) {
        meta.version = UNIVERSE_META_VERSION;
        meta.universe_seed = engine->config.universe_seed;
        save_universe_meta(meta_path, &meta);
    }
    engine->meta = meta;
    return engine_load_surface(engine, universe_path, 0);
}

b32 engine_load_surface(Engine *engine, const char *universe_path, u32 surface_id)
{
    char meta_path[512];
    SurfaceMeta meta;
    SurfaceRuntime *surface;
    if (!engine || !universe_path) return FALSE;

    surface = find_surface(engine, surface_id);
    if (surface) {
        return TRUE;
    }

    build_surface_meta_path(meta_path, sizeof(meta_path), universe_path, surface_id);
    if (!load_surface_meta(meta_path, &meta)) {
        meta.version = SURFACE_META_VERSION;
        meta.surface_id = surface_id;
        meta.seed = engine->meta.universe_seed ^ (u64)surface_id;
        meta.recipe_id = 0;
        rng_seed(&meta.rng_weather, meta.seed ^ 0x1ULL);
        rng_seed(&meta.rng_hydro, meta.seed ^ 0x2ULL);
        rng_seed(&meta.rng_misc, meta.seed ^ 0x3ULL);
        save_surface_meta(meta_path, &meta);
    }

    if (!create_surface(engine, &meta)) {
        return FALSE;
    }
    /* Region contents are not loaded in this pass; index is parsed to validate */
    {
        char region_path[512];
        RegionHeader header;
        ChunkEntry *entries = NULL;
        build_region_path(region_path, sizeof(region_path), universe_path, surface_id);
        if (load_region_index(region_path, &header, &entries)) {
            /* Ignore for now; runtime caches rebuild lazily */
        }
        if (entries) free(entries);
    }
    return TRUE;
}

static ChunkRuntime **collect_chunks(SurfaceRuntime *surface, u32 *out_count)
{
    u32 count = 0;
    u32 i;
    u32 idx = 0;
    ChunkRuntime **list = NULL;
    for (i = 0; i < SURFACE_CHUNK_TABLE_SIZE; ++i) {
        if (surface->chunks[i].used && surface->chunks[i].chunk) {
            count++;
        }
    }
    if (out_count) *out_count = count;
    if (count == 0) return NULL;
    list = (ChunkRuntime **)malloc(sizeof(ChunkRuntime *) * count);
    if (!list) {
        if (out_count) *out_count = 0;
        return NULL;
    }
    for (i = 0; i < SURFACE_CHUNK_TABLE_SIZE; ++i) {
        if (surface->chunks[i].used && surface->chunks[i].chunk) {
            list[idx++] = surface->chunks[i].chunk;
        }
    }
    return list;
}

b32 engine_save(Engine *engine, const char *universe_path)
{
    char meta_path[512];
    u32 i;
    if (!engine || !universe_path) return FALSE;
    ensure_directory(universe_path);
    path_join(meta_path, sizeof(meta_path), universe_path, "universe.meta");
    engine->meta.version = UNIVERSE_META_VERSION;
    if (!save_universe_meta(meta_path, &engine->meta)) {
        return FALSE;
    }

    for (i = 0; i < engine->surface_count; ++i) {
        SurfaceMeta meta;
        char surface_meta_path[512];
        char region_path[512];
        ChunkRuntime **chunks = NULL;
        u32 chunk_count = 0;
        surface_meta_from_runtime(&engine->surfaces[i], &meta);
        build_surface_meta_path(surface_meta_path, sizeof(surface_meta_path), universe_path, engine->surfaces[i].surface_id);
        save_surface_meta(surface_meta_path, &meta);

        build_region_path(region_path, sizeof(region_path), universe_path, engine->surfaces[i].surface_id);
        chunks = collect_chunks(&engine->surfaces[i], &chunk_count);
        if (!save_region_file(region_path, chunks, chunk_count)) {
            if (chunks) free(chunks);
            return FALSE;
        }
        if (chunks) free(chunks);
    }
    return TRUE;
}

void engine_tick(Engine *engine, fix32 dt)
{
    u32 i;
    if (!engine) return;
    for (i = 0; i < engine->surface_count; ++i) {
        sim_tick_surface(&engine->surfaces[i], &engine->services, dt);
    }
}

void engine_get_services(Engine *engine, u32 surface_id, WorldServices *out)
{
    SurfaceRuntime *surface;
    if (!engine || !out) return;
    *out = engine->services;
    surface = find_surface(engine, surface_id);
    (void)surface;
}
