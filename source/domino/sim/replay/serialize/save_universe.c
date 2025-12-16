/*
FILE: source/domino/sim/replay/serialize/save_universe.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/replay/serialize/save_universe
RESPONSIBILITY: Implements `save_universe`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "save_universe.h"

#include <stdio.h>

b32 save_universe_meta(const char *path, const UniverseMeta *meta)
{
    FILE *f;
    if (!path || !meta) return FALSE;
    f = fopen(path, "wb");
    if (!f) return FALSE;
    if (fwrite(meta, sizeof(*meta), 1, f) != 1) {
        fclose(f);
        return FALSE;
    }
    fclose(f);
    return TRUE;
}

b32 load_universe_meta(const char *path, UniverseMeta *out_meta)
{
    FILE *f;
    if (!path || !out_meta) return FALSE;
    f = fopen(path, "rb");
    if (!f) return FALSE;
    if (fread(out_meta, sizeof(*out_meta), 1, f) != 1) {
        fclose(f);
        return FALSE;
    }
    fclose(f);
    return TRUE;
}

b32 save_surface_meta(const char *path, const SurfaceMeta *meta)
{
    FILE *f;
    if (!path || !meta) return FALSE;
    f = fopen(path, "wb");
    if (!f) return FALSE;
    if (fwrite(meta, sizeof(*meta), 1, f) != 1) {
        fclose(f);
        return FALSE;
    }
    fclose(f);
    return TRUE;
}

b32 load_surface_meta(const char *path, SurfaceMeta *out_meta)
{
    FILE *f;
    if (!path || !out_meta) return FALSE;
    f = fopen(path, "rb");
    if (!f) return FALSE;
    if (fread(out_meta, sizeof(*out_meta), 1, f) != 1) {
        fclose(f);
        return FALSE;
    }
    fclose(f);
    return TRUE;
}
