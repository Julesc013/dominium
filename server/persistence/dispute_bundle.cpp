/*
FILE: server/persistence/dispute_bundle.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Server / persistence
RESPONSIBILITY: Deterministic dispute replay bundle helpers.
*/
#include "dispute_bundle.h"

#ifdef __cplusplus
extern "C" {
#endif

static u64 dom_dispute_hash_mix(u64 hash, u64 value)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        hash ^= (u64)((value >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

void dom_dispute_bundle_init(dom_dispute_bundle* bundle,
                             u64 bundle_id,
                             u64 snapshot_hash,
                             u64 input_stream_hash,
                             u64 rng_seed,
                             u64 schema_version_hash,
                             u64 mod_graph_hash,
                             u64 engine_build_id,
                             u64 game_build_id,
                             const dom_integrity_checkpoint* checkpoints,
                             u32 checkpoint_count)
{
    if (!bundle) {
        return;
    }
    bundle->bundle_id = bundle_id;
    bundle->snapshot_hash = snapshot_hash;
    bundle->input_stream_hash = input_stream_hash;
    bundle->rng_seed = rng_seed;
    bundle->schema_version_hash = schema_version_hash;
    bundle->mod_graph_hash = mod_graph_hash;
    bundle->engine_build_id = engine_build_id;
    bundle->game_build_id = game_build_id;
    bundle->checkpoints = checkpoints;
    bundle->checkpoint_count = checkpoint_count;
}

u64 dom_dispute_bundle_hash(const dom_dispute_bundle* bundle)
{
    u32 i;
    u64 hash = 1469598103934665603ULL;
    if (!bundle) {
        return hash;
    }
    hash = dom_dispute_hash_mix(hash, bundle->bundle_id);
    hash = dom_dispute_hash_mix(hash, bundle->snapshot_hash);
    hash = dom_dispute_hash_mix(hash, bundle->input_stream_hash);
    hash = dom_dispute_hash_mix(hash, bundle->rng_seed);
    hash = dom_dispute_hash_mix(hash, bundle->schema_version_hash);
    hash = dom_dispute_hash_mix(hash, bundle->mod_graph_hash);
    hash = dom_dispute_hash_mix(hash, bundle->engine_build_id);
    hash = dom_dispute_hash_mix(hash, bundle->game_build_id);
    hash = dom_dispute_hash_mix(hash, bundle->checkpoint_count);
    for (i = 0u; i < bundle->checkpoint_count; ++i) {
        hash = dom_dispute_hash_mix(hash, dom_integrity_checkpoint_hash(&bundle->checkpoints[i]));
    }
    return hash;
}

int dom_dispute_bundle_verify(const dom_dispute_bundle* bundle,
                              const u64* replay_hashes,
                              u32 replay_count,
                              dom_dispute_report* out_report)
{
    u32 i;
    if (!bundle || !replay_hashes || !out_report) {
        return -1;
    }
    out_report->mismatch_index = 0u;
    out_report->ok = 1u;
    if (replay_count != bundle->checkpoint_count) {
        out_report->ok = 0u;
        out_report->mismatch_index = replay_count < bundle->checkpoint_count ? replay_count : bundle->checkpoint_count;
        return 1;
    }
    for (i = 0u; i < bundle->checkpoint_count; ++i) {
        u64 expected = dom_integrity_checkpoint_hash(&bundle->checkpoints[i]);
        if (expected != replay_hashes[i]) {
            out_report->ok = 0u;
            out_report->mismatch_index = i;
            return 1;
        }
    }
    return 0;
}

#ifdef __cplusplus
} /* extern "C" */
#endif
