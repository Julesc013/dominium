#include "dsk/dsk_splat.h"

static const char *k_splat_ids[] = {
    "splat_portable",
    "splat_win32_nt5",
    "splat_macos_pkg",
    "splat_linux_deb",
    "splat_linux_rpm",
    "splat_steam"
};

void dsk_splat_registry_list(std::vector<dsk_splat_info_t> &out) {
    size_t i;
    out.clear();
    for (i = 0u; i < sizeof(k_splat_ids) / sizeof(k_splat_ids[0]); ++i) {
        dsk_splat_info_t info;
        info.id = k_splat_ids[i];
        out.push_back(info);
    }
}

int dsk_splat_registry_contains(const std::string &id) {
    size_t i;
    for (i = 0u; i < sizeof(k_splat_ids) / sizeof(k_splat_ids[0]); ++i) {
        if (id == k_splat_ids[i]) {
            return 1;
        }
    }
    return 0;
}
