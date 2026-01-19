/*
FILE: game/include/dominium/mods/mod_loader.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game / mods
RESPONSIBILITY: Mod manifest ingestion and deterministic graph resolution.
ALLOWED DEPENDENCIES: engine/include public headers and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic ordering and refusal-first behavior.
*/
#ifndef DOMINIUM_MODS_MOD_LOADER_H
#define DOMINIUM_MODS_MOD_LOADER_H

#include "domino/core/types.h"
#include "dominium/mods/mod_manifest.h"
#include "dominium/mods/mod_graph_resolver.h"
#include "dominium/mods/mod_compat.h"
#include "dominium/mods/mod_safe_mode.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum mod_loader_status {
    MOD_LOADER_OK = 0,
    MOD_LOADER_GRAPH_REFUSED = 1,
    MOD_LOADER_COMPAT_REFUSED = 2,
    MOD_LOADER_SAFE_MODE_REFUSED = 3,
    MOD_LOADER_INVALID = 4
} mod_loader_status;

typedef struct mod_loader_input {
    const mod_manifest* mods;
    u32 mod_count;
    mod_compat_environment environment;
    mod_safe_mode_policy safe_mode;
} mod_loader_input;

typedef struct mod_loader_output {
    mod_loader_status status;
    mod_graph graph;
    mod_compat_report reports[DOM_MOD_MAX_MODS];
    u32 report_count;
    mod_safe_mode_result safe_mode;
    mod_graph_refusal graph_refusal;
    u64 graph_hash;
} mod_loader_output;

int mod_loader_resolve(const mod_loader_input* input,
                       mod_loader_output* out_output);
const char* mod_loader_status_to_string(mod_loader_status status);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_MODS_MOD_LOADER_H */
