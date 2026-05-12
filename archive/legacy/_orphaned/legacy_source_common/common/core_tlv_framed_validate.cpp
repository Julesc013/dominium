/*
FILE: source/dominium/common/core_tlv_framed_validate.cpp
MODULE: Dominium
PURPOSE: CRC32 helper for framed TLV format.
*/

#include "dominium/core_tlv.h"

static u32 core_crc_table[256];
static int core_crc_init = 0;

static void core_crc32_init(void) {
    u32 i;
    for (i = 0u; i < 256u; ++i) {
        u32 c = i;
        u32 j;
        for (j = 0u; j < 8u; ++j) {
            if (c & 1u) {
                c = 0xEDB88320u ^ (c >> 1u);
            } else {
                c >>= 1u;
            }
        }
        core_crc_table[i] = c;
    }
    core_crc_init = 1;
}

u32 core_tlv_crc32(const unsigned char* data, u32 size) {
    u32 crc = 0xFFFFFFFFu;
    u32 i;
    if (!core_crc_init) {
        core_crc32_init();
    }
    if (!data || size == 0u) {
        return crc ^ 0xFFFFFFFFu;
    }
    for (i = 0u; i < size; ++i) {
        u32 idx = (crc ^ data[i]) & 0xFFu;
        crc = core_crc_table[idx] ^ (crc >> 8u);
    }
    return crc ^ 0xFFFFFFFFu;
}
