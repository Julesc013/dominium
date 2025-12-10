#include "dominium/version.h"

void dominium_game_get_version(domino_semver* out)
{
    if (!out) return;
    domino_semver_parse(DOMINIUM_GAME_VERSION, out);
}

void dominium_launcher_get_version(domino_semver* out)
{
    if (!out) return;
    domino_semver_parse(DOMINIUM_LAUNCHER_VERSION, out);
}

const char* dominium_get_core_version_string(void)
{
    return DOMINIUM_CORE_VERSION;
}

const char* dominium_get_game_version_string(void)
{
    return DOMINIUM_GAME_VERSION;
}

const char* dominium_get_launcher_version_string(void)
{
    return DOMINIUM_LAUNCHER_VERSION;
}

const char* dominium_get_setup_version_string(void)
{
    return DOMINIUM_SETUP_VERSION;
}

const char* dominium_get_tools_version_string(void)
{
    return DOMINIUM_TOOLS_VERSION;
}

const char* dominium_get_suite_version_string(void)
{
    return DOMINIUM_SUITE_VERSION;
}

int dominium_game_get_content_api(void)
{
    return 1;
}

int dominium_launcher_get_content_api(void)
{
    return 1;
}

int dominium_launcher_get_ext_api(void)
{
    return 1;
}
