#include "domino/build_info.h"
#include "domino/config_base.h"

static const dom_build_info_v1 g_dom_build_info_v1 = {
    DOM_ABI_HEADER_INIT(DOM_BUILD_INFO_ABI_VERSION, dom_build_info_v1),
    DOM_BUILD_ID,
    DOM_GIT_HASH,
    1u,
    1u,
    DOM_PROFILE_BASELINE,
    0u
};

const dom_build_info_v1* dom_build_info_v1_get(void)
{
    return &g_dom_build_info_v1;
}

const char* dom_build_id(void)
{
    return g_dom_build_info_v1.build_id;
}

const char* dom_git_hash(void)
{
    return g_dom_build_info_v1.git_hash;
}

