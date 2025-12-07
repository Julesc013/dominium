#include "dom_core_version.h"

const char *dom_version_semver(void)
{
    return DOM_VERSION_SEMVER;
}

const char *dom_version_full(void)
{
    return DOM_VERSION_BUILD_STR;
}

dom_u32 dom_version_build_number(void)
{
    return (dom_u32)DOM_BUILD_NUMBER;
}
