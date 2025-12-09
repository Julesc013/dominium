#include "vesa_bios.h"

/* Stub implementations; platform-specific VBE hooks can replace these. */

int vesa_bios_init(void)
{
    return -1;
}

int vesa_bios_find_mode(uint16_t req_w,
                        uint16_t req_h,
                        uint8_t req_bpp,
                        vesa_mode_info* out_mode)
{
    (void)req_w;
    (void)req_h;
    (void)req_bpp;
    (void)out_mode;
    return -1;
}

int vesa_bios_set_mode(const vesa_mode_info* mode, int use_linear)
{
    (void)mode;
    (void)use_linear;
    return -1;
}

void vesa_bios_restore_mode(void)
{
}

void* vesa_bios_map_lfb(const vesa_mode_info* mode)
{
    (void)mode;
    return (void*)0;
}

void vesa_bios_set_bank(uint16_t bank)
{
    (void)bank;
}
