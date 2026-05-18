/*
Build identity provider implementation.
*/
#include "dom_build_identity/build_identity.h"

#include "dom_contracts/_internal/dom_build_version.h"
#include "domino/config_base.h"

dom_build_identity dom_build_identity_get(void)
{
    dom_build_identity identity;
    identity.build_kind = DOM_BUILD_KIND;
    identity.bii = DOM_BUILD_BII;
    identity.gbn = DOM_BUILD_GBN;
    identity.git_commit = DOM_GIT_HASH;
    identity.build_timestamp = DOM_BUILD_TIMESTAMP;
    return identity;
}
