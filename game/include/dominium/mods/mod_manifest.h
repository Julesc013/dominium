/*
FILE: game/include/dominium/mods/mod_manifest.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game / mods
RESPONSIBILITY: Mod manifest data model and parsing utilities.
ALLOWED DEPENDENCIES: engine/include public headers and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Parsing is order-preserving and deterministic.
*/
#ifndef DOMINIUM_MODS_MOD_MANIFEST_H
#define DOMINIUM_MODS_MOD_MANIFEST_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_MOD_ID_MAX 64
#define DOM_MOD_CAP_MAX 32
#define DOM_MOD_MAX_SCHEMA_DEPS 16
#define DOM_MOD_MAX_FEATURE_EPOCHS 16
#define DOM_MOD_MAX_DEPENDENCIES 32
#define DOM_MOD_MAX_CONFLICTS 32
#define DOM_MOD_MAX_CAPABILITIES 32
#define DOM_MOD_HASH_STR_MAX 80

typedef struct mod_semver {
    u16 major;
    u16 minor;
    u16 patch;
} mod_semver;

typedef struct mod_version_range {
    d_bool has_min;
    d_bool has_max;
    mod_semver min;
    mod_semver max;
} mod_version_range;

typedef struct mod_schema_dependency {
    char schema_id[DOM_MOD_ID_MAX];
    mod_version_range range;
} mod_schema_dependency;

typedef struct mod_feature_epoch_req {
    char epoch_id[DOM_MOD_ID_MAX];
    u32 min_epoch;
    u32 max_epoch;
    d_bool has_min;
    d_bool has_max;
} mod_feature_epoch_req;

typedef struct mod_dependency {
    char mod_id[DOM_MOD_ID_MAX];
    mod_version_range range;
} mod_dependency;

typedef struct mod_conflict {
    char mod_id[DOM_MOD_ID_MAX];
    mod_version_range range;
} mod_conflict;

typedef struct mod_required_capability {
    char capability_id[DOM_MOD_CAP_MAX];
} mod_required_capability;

typedef struct mod_required_feature {
    char feature_id[DOM_MOD_CAP_MAX];
} mod_required_feature;

typedef struct mod_manifest {
    char mod_id[DOM_MOD_ID_MAX];
    mod_semver mod_version;
    d_bool sim_affecting;
    u32 perf_budget_class;

    u32 schema_dep_count;
    mod_schema_dependency schema_deps[DOM_MOD_MAX_SCHEMA_DEPS];

    u32 feature_epoch_count;
    mod_feature_epoch_req feature_epochs[DOM_MOD_MAX_FEATURE_EPOCHS];

    u32 dependency_count;
    mod_dependency dependencies[DOM_MOD_MAX_DEPENDENCIES];

    u32 conflict_count;
    mod_conflict conflicts[DOM_MOD_MAX_CONFLICTS];

    u32 capability_count;
    mod_required_capability capabilities[DOM_MOD_MAX_CAPABILITIES];

    u32 render_feature_count;
    mod_required_feature render_features[DOM_MOD_MAX_CAPABILITIES];

    char payload_hash_str[DOM_MOD_HASH_STR_MAX];
    u64 payload_hash_value;
} mod_manifest;

typedef enum mod_manifest_error_code {
    MOD_MANIFEST_OK = 0,
    MOD_MANIFEST_ERR_INVALID = 1,
    MOD_MANIFEST_ERR_MISSING_FIELD = 2,
    MOD_MANIFEST_ERR_TOO_MANY = 3,
    MOD_MANIFEST_ERR_BAD_VERSION = 4,
    MOD_MANIFEST_ERR_BAD_RANGE = 5,
    MOD_MANIFEST_ERR_BAD_HASH = 6
} mod_manifest_error_code;

typedef struct mod_manifest_error {
    mod_manifest_error_code code;
    u32 line;
    char message[128];
} mod_manifest_error;

void mod_manifest_init(mod_manifest* out_manifest);
int mod_semver_parse(const char* text, mod_semver* out_version);
int mod_semver_compare(const mod_semver* a, const mod_semver* b);
int mod_version_in_range(const mod_semver* version, const mod_version_range* range);
int mod_manifest_parse_text(const char* text,
                            mod_manifest* out_manifest,
                            mod_manifest_error* out_error);
int mod_manifest_validate(const mod_manifest* manifest, mod_manifest_error* out_error);
int mod_parse_hash64(const char* text, u64* out_hash);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_MODS_MOD_MANIFEST_H */
