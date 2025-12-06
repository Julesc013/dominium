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
