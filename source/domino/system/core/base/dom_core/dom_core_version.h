#ifndef DOM_CORE_VERSION_H
#define DOM_CORE_VERSION_H

#include "dom_core_types.h"
#include "dom_build_version.h"

/* Runtime accessors for semantic version + global build number. */
const char *dom_version_semver(void);
const char *dom_version_full(void);
dom_u32 dom_version_build_number(void);

#endif /* DOM_CORE_VERSION_H */
