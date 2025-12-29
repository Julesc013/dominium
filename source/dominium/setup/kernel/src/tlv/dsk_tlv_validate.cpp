#include "dsk/dsk_tlv.h"

static dsk_u32 dsk_crc_table[256];
static int dsk_crc_init = 0;

static void dsk_crc32_init(void) {
    dsk_u32 i;
    for (i = 0u; i < 256u; ++i) {
        dsk_u32 c = i;
        dsk_u32 j;
        for (j = 0u; j < 8u; ++j) {
            if (c & 1u) {
                c = 0xEDB88320u ^ (c >> 1u);
            } else {
                c >>= 1u;
            }
        }
        dsk_crc_table[i] = c;
    }
    dsk_crc_init = 1;
}

dsk_u32 dsk_tlv_crc32(const dsk_u8 *data, dsk_u32 size) {
    dsk_u32 crc = 0xFFFFFFFFu;
    dsk_u32 i;
    if (!dsk_crc_init) {
        dsk_crc32_init();
    }
    if (!data || size == 0u) {
        return crc ^ 0xFFFFFFFFu;
    }
    for (i = 0u; i < size; ++i) {
        dsk_u32 idx = (crc ^ data[i]) & 0xFFu;
        crc = dsk_crc_table[idx] ^ (crc >> 8u);
    }
    return crc ^ 0xFFFFFFFFu;
}
