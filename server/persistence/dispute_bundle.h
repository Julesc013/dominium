/*
FILE: server/persistence/dispute_bundle.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / persistence
RESPONSIBILITY: Deterministic dispute replay bundle definition.
ALLOWED DEPENDENCIES: engine public headers only.
FORBIDDEN DEPENDENCIES: game headers; OS/platform headers.
*/
#ifndef DOMINIUM_SERVER_PERSISTENCE_DISPUTE_BUNDLE_H
#define DOMINIUM_SERVER_PERSISTENCE_DISPUTE_BUNDLE_H

#include "integrity_checkpoints.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_dispute_bundle {
    u64 bundle_id;
    u64 snapshot_hash;
    u64 input_stream_hash;
    u64 rng_seed;
    u64 schema_version_hash;
    u64 mod_graph_hash;
    u64 engine_build_id;
    u64 game_build_id;
    const dom_integrity_checkpoint* checkpoints;
    u32 checkpoint_count;
} dom_dispute_bundle;

typedef struct dom_dispute_report {
    u32 mismatch_index;
    u32 ok;
} dom_dispute_report;

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
                             u32 checkpoint_count);

u64 dom_dispute_bundle_hash(const dom_dispute_bundle* bundle);

int dom_dispute_bundle_verify(const dom_dispute_bundle* bundle,
                              const u64* replay_hashes,
                              u32 replay_count,
                              dom_dispute_report* out_report);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_PERSISTENCE_DISPUTE_BUNDLE_H */
