#ifndef DOM_SAVE_TLV_H
#define DOM_SAVE_TLV_H

#include "core_types.h"
#include <stdio.h>

typedef struct ChunkSectionHeader {
    u32 type;
    u16 version;
    u16 reserved;
    u32 length;
} ChunkSectionHeader;

int tlv_read_header(FILE *f, ChunkSectionHeader *out);
int tlv_skip_section(FILE *f, const ChunkSectionHeader *hdr);
int tlv_write_section(FILE *f, u32 type, u16 version, const void *payload, u32 length);

#endif /* DOM_SAVE_TLV_H */
