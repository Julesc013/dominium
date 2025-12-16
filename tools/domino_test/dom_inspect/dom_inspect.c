/*
FILE: tools/domino_test/dom_inspect/dom_inspect.c
MODULE: Repository
LAYER / SUBSYSTEM: tools/domino_test/dom_inspect
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>
#include <string.h>

#include "save_universe.h"

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
        if (c != '/' && c != '\\') out[i++] = '/';
    }
    while (leaf[j] && i < cap - 1) {
        out[i++] = leaf[j++];
    }
    out[i] = '\0';
}

int main(int argc, char **argv)
{
    const char *universe = "saves/default";
    UniverseMeta meta;
    SurfaceMeta surface_meta;
    char universe_meta_path[512];
    char surface_path[512];
    if (argc > 1) {
        universe = argv[1];
    }
    path_join(universe_meta_path, sizeof(universe_meta_path), universe, "universe.meta");
    if (!load_universe_meta(universe_meta_path, &meta)) {
        printf("Universe meta not found at %s\n", universe_meta_path);
        return 1;
    }
    printf("Universe seed: %llu (ver %u)\n", (unsigned long long)meta.universe_seed, (unsigned int)meta.version);

    path_join(surface_path, sizeof(surface_path), universe, "surface_000.meta");
    if (load_surface_meta(surface_path, &surface_meta)) {
        printf("Surface 0 seed: %llu recipe=%u (ver %u)\n",
               (unsigned long long)surface_meta.seed,
               (unsigned int)surface_meta.recipe_id,
               (unsigned int)surface_meta.version);
    } else {
        printf("Surface 0 meta not found at %s\n", surface_path);
    }
    return 0;
}
