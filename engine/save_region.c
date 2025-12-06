#include "save_region.h"

#include <stdlib.h>
#include <string.h>

b32 save_region_file(const char *path, ChunkRuntime **chunks, u32 chunk_count)
{
    FILE *f;
    RegionHeader header;
    ChunkEntry *entries;
    u32 i;
    u32 offset;
    if (!path) return FALSE;
    f = fopen(path, "wb");
    if (!f) {
        return FALSE;
    }
    entries = (ChunkEntry *)malloc(sizeof(ChunkEntry) * chunk_count);
    if (!entries && chunk_count > 0) {
        fclose(f);
        return FALSE;
    }

    header.magic = REGION_MAGIC;
    header.version = 1;
    header.chunk_count = (u16)chunk_count;
    if (fwrite(&header, sizeof(header), 1, f) != 1) {
        fclose(f);
        free(entries);
        return FALSE;
    }

    offset = (u32)(sizeof(header) + sizeof(ChunkEntry) * chunk_count);
    for (i = 0; i < chunk_count; ++i) {
        ChunkRuntime *chunk = chunks[i];
        entries[i].key = chunk->key;
        entries[i].offset = offset;
        entries[i].length = (u32)(2U * sizeof(ChunkSectionHeader));
        offset += entries[i].length;
    }

    if (chunk_count > 0) {
        if (fwrite(entries, sizeof(ChunkEntry), chunk_count, f) != chunk_count) {
            fclose(f);
            free(entries);
            return FALSE;
        }
    }

    for (i = 0; i < chunk_count; ++i) {
        if (!tlv_write_section(f, CHUNK_SEC_TERRAIN_OVERRIDES, 1, NULL, 0)) {
            fclose(f);
            free(entries);
            return FALSE;
        }
        if (!tlv_write_section(f, CHUNK_SEC_OBJECTS, 1, NULL, 0)) {
            fclose(f);
            free(entries);
            return FALSE;
        }
    }

    fclose(f);
    free(entries);
    return TRUE;
}

b32 load_region_index(const char *path, RegionHeader *out_header, ChunkEntry **out_entries)
{
    FILE *f;
    RegionHeader header;
    ChunkEntry *entries = NULL;
    if (!path) return FALSE;
    f = fopen(path, "rb");
    if (!f) return FALSE;
    if (fread(&header, sizeof(header), 1, f) != 1) {
        fclose(f);
        return FALSE;
    }
    if (header.magic != REGION_MAGIC) {
        fclose(f);
        return FALSE;
    }
    if (header.chunk_count > 0) {
        entries = (ChunkEntry *)malloc(sizeof(ChunkEntry) * header.chunk_count);
        if (!entries) {
            fclose(f);
            return FALSE;
        }
        if (fread(entries, sizeof(ChunkEntry), header.chunk_count, f) != header.chunk_count) {
            free(entries);
            fclose(f);
            return FALSE;
        }
    }
    fclose(f);
    if (out_header) *out_header = header;
    if (out_entries) {
        *out_entries = entries;
    } else if (entries) {
        free(entries);
    }
    return TRUE;
}
