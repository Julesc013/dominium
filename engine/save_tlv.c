#include "save_tlv.h"

#include <string.h>

int tlv_read_header(FILE *f, ChunkSectionHeader *out)
{
    if (!f || !out) return 0;
    return fread(out, sizeof(ChunkSectionHeader), 1, f) == 1;
}

int tlv_skip_section(FILE *f, const ChunkSectionHeader *hdr)
{
    if (!f || !hdr) return 0;
    return fseek(f, (long)hdr->length, SEEK_CUR) == 0;
}

int tlv_write_section(FILE *f, u32 type, u16 version, const void *payload, u32 length)
{
    ChunkSectionHeader hdr;
    if (!f) return 0;
    hdr.type = type;
    hdr.version = version;
    hdr.reserved = 0;
    hdr.length = length;
    if (fwrite(&hdr, sizeof(hdr), 1, f) != 1) {
        return 0;
    }
    if (length > 0 && payload) {
        if (fwrite(payload, 1, length, f) != length) {
            return 0;
        }
    } else if (length > 0 && !payload) {
        /* zero payload */
        static const char zero = 0;
        u32 i;
        for (i = 0; i < length; ++i) {
            if (fwrite(&zero, 1, 1, f) != 1) {
                return 0;
            }
        }
    }
    return 1;
}
