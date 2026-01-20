/*
FILE: tools/inspect/dispute_replay_inspector.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / inspect
RESPONSIBILITY: Deterministic dispute replay verification (offline).
ALLOWED DEPENDENCIES: Engine public headers and C89/C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game/server internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic hashing and ordering.
*/
#include "inspect_access.h"

#include "domino/core/types.h"

typedef struct tool_dispute_bundle_view {
    u64 bundle_id;
    u64 snapshot_hash;
    u64 input_stream_hash;
    u64 rng_seed;
    u64 schema_version_hash;
    u64 mod_graph_hash;
    u64 engine_build_id;
    u64 game_build_id;
    const u64* checkpoint_hashes;
    u32 checkpoint_count;
} tool_dispute_bundle_view;

typedef struct tool_dispute_report {
    u32 mismatch_index;
    u32 ok;
} tool_dispute_report;

static u64 tool_dispute_hash_mix(u64 hash, u64 value)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        hash ^= (u64)((value >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static u64 tool_dispute_bundle_hash(const tool_dispute_bundle_view* bundle)
{
    u32 i;
    u64 hash = 1469598103934665603ULL;
    if (!bundle) {
        return hash;
    }
    hash = tool_dispute_hash_mix(hash, bundle->bundle_id);
    hash = tool_dispute_hash_mix(hash, bundle->snapshot_hash);
    hash = tool_dispute_hash_mix(hash, bundle->input_stream_hash);
    hash = tool_dispute_hash_mix(hash, bundle->rng_seed);
    hash = tool_dispute_hash_mix(hash, bundle->schema_version_hash);
    hash = tool_dispute_hash_mix(hash, bundle->mod_graph_hash);
    hash = tool_dispute_hash_mix(hash, bundle->engine_build_id);
    hash = tool_dispute_hash_mix(hash, bundle->game_build_id);
    hash = tool_dispute_hash_mix(hash, bundle->checkpoint_count);
    for (i = 0u; i < bundle->checkpoint_count; ++i) {
        hash = tool_dispute_hash_mix(hash, bundle->checkpoint_hashes[i]);
    }
    return hash;
}

int tool_dispute_replay_verify(const tool_dispute_bundle_view* bundle,
                               const u64* replay_hashes,
                               u32 replay_count,
                               tool_dispute_report* out_report)
{
    u32 i;
    if (!bundle || !replay_hashes || !out_report) {
        return TOOL_INSPECT_INVALID;
    }
    out_report->mismatch_index = 0u;
    out_report->ok = 1u;
    if (replay_count != bundle->checkpoint_count) {
        out_report->ok = 0u;
        out_report->mismatch_index = replay_count < bundle->checkpoint_count ? replay_count : bundle->checkpoint_count;
        return TOOL_INSPECT_REFUSED;
    }
    for (i = 0u; i < bundle->checkpoint_count; ++i) {
        if (replay_hashes[i] != bundle->checkpoint_hashes[i]) {
            out_report->ok = 0u;
            out_report->mismatch_index = i;
            return TOOL_INSPECT_REFUSED;
        }
    }
    (void)tool_dispute_bundle_hash(bundle);
    return TOOL_INSPECT_OK;
}
