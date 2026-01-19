/*
FILE: game/mods/mod_loader.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / mods
RESPONSIBILITY: Orchestrates mod graph resolution, compatibility, and safe-mode.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 standard headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic ordering and refusal-first behavior.
*/
#include "dominium/mods/mod_loader.h"

#include <cstring>

int mod_loader_resolve(const mod_loader_input* input,
                       mod_loader_output* out_output) {
    u32 i;
    mod_graph_identity_input identity_input;
    if (!input || !out_output) {
        return 1;
    }
    std::memset(out_output, 0, sizeof(*out_output));
    if (mod_graph_build(&out_output->graph, input->mods, input->mod_count,
                        &out_output->graph_refusal) != 0) {
        out_output->status = MOD_LOADER_GRAPH_REFUSED;
        return 0;
    }
    if (mod_graph_resolve(&out_output->graph, &out_output->graph_refusal) != 0) {
        out_output->status = MOD_LOADER_GRAPH_REFUSED;
        return 0;
    }

    out_output->report_count = out_output->graph.mod_count;
    for (i = 0u; i < out_output->graph.mod_count; ++i) {
        const mod_manifest* manifest = &out_output->graph.mods[out_output->graph.order[i]];
        mod_compat_check_manifest(manifest, &input->environment, &out_output->reports[i]);
        if (out_output->reports[i].result == MOD_COMPAT_REFUSE &&
            input->safe_mode == MOD_SAFE_MODE_NONE) {
            out_output->status = MOD_LOADER_COMPAT_REFUSED;
            return 0;
        }
    }

    if (mod_safe_mode_apply(&out_output->graph,
                            out_output->reports,
                            out_output->report_count,
                            input->safe_mode,
                            &out_output->safe_mode) != 0) {
        out_output->status = MOD_LOADER_SAFE_MODE_REFUSED;
        return 0;
    }

    identity_input.schemas = input->environment.schemas;
    identity_input.schema_count = input->environment.schema_count;
    identity_input.epochs = input->environment.epochs;
    identity_input.epoch_count = input->environment.epoch_count;
    out_output->graph_hash = mod_graph_identity_hash(&out_output->graph, &identity_input);
    out_output->status = MOD_LOADER_OK;
    return 0;
}

const char* mod_loader_status_to_string(mod_loader_status status) {
    switch (status) {
    case MOD_LOADER_OK:
        return "OK";
    case MOD_LOADER_GRAPH_REFUSED:
        return "GRAPH_REFUSED";
    case MOD_LOADER_COMPAT_REFUSED:
        return "COMPAT_REFUSED";
    case MOD_LOADER_SAFE_MODE_REFUSED:
        return "SAFE_MODE_REFUSED";
    case MOD_LOADER_INVALID:
        return "INVALID";
    default:
        return "UNKNOWN";
    }
}
