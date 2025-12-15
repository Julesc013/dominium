#ifndef DOMINO_BUILD_INFO_H_INCLUDED
#define DOMINO_BUILD_INFO_H_INCLUDED
/*
 * Embedded build metadata (C89/C++98 visible).
 *
 * Values are configured at CMake configure time; when unavailable they fall
 * back to "unknown".
 */

#include "domino/abi.h"
#include "domino/profile.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_BUILD_INFO_ABI_VERSION 1u

typedef struct dom_build_info_v1 {
    DOM_ABI_HEADER;

    const char* build_id;
    const char* git_hash;

    u32 sim_schema_version;
    u32 content_schema_version;

    dom_profile_kind default_profile_kind;
    u32 default_lockstep_strict;
} dom_build_info_v1;

const dom_build_info_v1* dom_build_info_v1_get(void);

const char* dom_build_id(void);
const char* dom_git_hash(void);

/* Deterministic simulation schema identifier (public serialization ABI). */
u64 dom_sim_schema_id(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_BUILD_INFO_H_INCLUDED */
