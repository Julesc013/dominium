#include "dominium/version.h"

void dominium_game_get_version(domino_semver* out)
{
    if (!out) return;
    out->major = DOMINIUM_VERSION_MAJOR;
    out->minor = DOMINIUM_VERSION_MINOR;
    out->patch = DOMINIUM_VERSION_PATCH;
}

void dominium_launcher_get_version(domino_semver* out)
{
    if (!out) return;
    out->major = DOMINIUM_VERSION_MAJOR;
    out->minor = DOMINIUM_VERSION_MINOR;
    out->patch = DOMINIUM_VERSION_PATCH;
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
