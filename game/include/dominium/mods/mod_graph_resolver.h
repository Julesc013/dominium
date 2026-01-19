/*
FILE: game/include/dominium/mods/mod_graph_resolver.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game / mods
RESPONSIBILITY: Deterministic mod graph resolution and identity hashing.
ALLOWED DEPENDENCIES: engine/include public headers and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Stable ordering and refusal-first resolution.
*/
#ifndef DOMINIUM_MODS_MOD_GRAPH_RESOLVER_H
#define DOMINIUM_MODS_MOD_GRAPH_RESOLVER_H

#include "domino/core/types.h"
#include "dominium/mods/mod_manifest.h"
#include "dominium/mods/mod_hash.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_MOD_MAX_MODS 64

typedef struct mod_schema_version {
    char schema_id[DOM_MOD_ID_MAX];
    mod_semver version;
} mod_schema_version;

typedef struct mod_feature_epoch {
    char epoch_id[DOM_MOD_ID_MAX];
    u32 epoch;
} mod_feature_epoch;

typedef enum mod_graph_refusal_code {
    MOD_GRAPH_OK = 0,
    MOD_GRAPH_ERR_TOO_MANY = 1,
    MOD_GRAPH_ERR_DUPLICATE = 2,
    MOD_GRAPH_ERR_MISSING_DEP = 3,
    MOD_GRAPH_ERR_DEP_VERSION = 4,
    MOD_GRAPH_ERR_CONFLICT = 5,
    MOD_GRAPH_ERR_CYCLE = 6
} mod_graph_refusal_code;

typedef struct mod_graph_refusal {
    mod_graph_refusal_code code;
    char mod_id[DOM_MOD_ID_MAX];
    char detail_id[DOM_MOD_ID_MAX];
} mod_graph_refusal;

typedef struct mod_graph {
    mod_manifest mods[DOM_MOD_MAX_MODS];
    u32 mod_count;
    u32 order[DOM_MOD_MAX_MODS];
} mod_graph;

typedef struct mod_graph_identity_input {
    const mod_schema_version* schemas;
    u32 schema_count;
    const mod_feature_epoch* epochs;
    u32 epoch_count;
} mod_graph_identity_input;

int mod_graph_build(mod_graph* out_graph,
                    const mod_manifest* mods,
                    u32 mod_count,
                    mod_graph_refusal* out_refusal);
int mod_graph_resolve(mod_graph* graph,
                      mod_graph_refusal* out_refusal);
u64 mod_graph_identity_hash(const mod_graph* graph,
                            const mod_graph_identity_input* input);
const char* mod_graph_refusal_to_string(mod_graph_refusal_code code);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_MODS_MOD_GRAPH_RESOLVER_H */
