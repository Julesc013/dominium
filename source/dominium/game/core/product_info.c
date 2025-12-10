#include "domino/compat.h"
#include "domino/platform.h"
#include "dominium/product_info.h"
#include "dominium/version.h"

static DomProductInfo g_dominium_game_product_info = {
    "game",
    DOM_COMP_ROLE_RUNTIME,
    "game",
    DOMINIUM_GAME_VERSION,
    DOMINIUM_CORE_VERSION,
    DOMINIUM_SUITE_VERSION,
    DOM_OSFAM_WIN_NT,
    DOM_ARCH_X86_64,
    DMN_EMPTY_COMPAT_PROFILE
};

static void dmn_init_game_product_info(void)
{
    static int initialized = 0;
    if (initialized) return;
    g_dominium_game_product_info.os_family = dominium_detect_os_family();
    g_dominium_game_product_info.arch = dominium_detect_arch();
    initialized = 1;
}

const DomProductInfo* dom_get_product_info_game(void)
{
    dmn_init_game_product_info();
    return &g_dominium_game_product_info;
}
