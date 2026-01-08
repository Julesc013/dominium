/*
FILE: source/dominium/game/runtime/dom_universe_bundle.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/universe_bundle
RESPONSIBILITY: Portable universe bundle container (read/write + identity validation).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS-specific headers; direct filesystem probing.
*/
#ifndef DOM_UNIVERSE_BUNDLE_H
#define DOM_UNIVERSE_BUNDLE_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_U32_FOURCC(a,b,c,d) \
    ((u32)(a) | ((u32)(b) << 8) | ((u32)(c) << 16) | ((u32)(d) << 24))

enum {
    DOM_UNIVERSE_BUNDLE_OK = 0,
    DOM_UNIVERSE_BUNDLE_ERR = -1,
    DOM_UNIVERSE_BUNDLE_INVALID_ARGUMENT = -2,
    DOM_UNIVERSE_BUNDLE_INVALID_FORMAT = -3,
    DOM_UNIVERSE_BUNDLE_IDENTITY_MISMATCH = -4,
    DOM_UNIVERSE_BUNDLE_MIGRATION_REQUIRED = -5,
    DOM_UNIVERSE_BUNDLE_UNSUPPORTED_SCHEMA = -6,
    DOM_UNIVERSE_BUNDLE_IO_ERROR = -7,
    DOM_UNIVERSE_BUNDLE_NO_MEMORY = -8
};

enum {
    DOM_UNIVERSE_CHUNK_TIME = DOM_U32_FOURCC('T','I','M','E'),
    DOM_UNIVERSE_CHUNK_COSM = DOM_U32_FOURCC('C','O','S','M'),
    DOM_UNIVERSE_CHUNK_SYSM = DOM_U32_FOURCC('S','Y','S','M'),
    DOM_UNIVERSE_CHUNK_BODS = DOM_U32_FOURCC('B','O','D','S'),
    DOM_UNIVERSE_CHUNK_FRAM = DOM_U32_FOURCC('F','R','A','M'),
    DOM_UNIVERSE_CHUNK_TOPB = DOM_U32_FOURCC('T','O','P','B'),
    DOM_UNIVERSE_CHUNK_ORBT = DOM_U32_FOURCC('O','R','B','T'),
    DOM_UNIVERSE_CHUNK_SOVR = DOM_U32_FOURCC('S','O','V','R'),
    DOM_UNIVERSE_CHUNK_CNST = DOM_U32_FOURCC('C','N','S','T'),
    DOM_UNIVERSE_CHUNK_STAT = DOM_U32_FOURCC('S','T','A','T'),
    DOM_UNIVERSE_CHUNK_ROUT = DOM_U32_FOURCC('R','O','U','T'),
    DOM_UNIVERSE_CHUNK_TRAN = DOM_U32_FOURCC('T','R','A','N'),
    DOM_UNIVERSE_CHUNK_PROD = DOM_U32_FOURCC('P','R','O','D'),
    DOM_UNIVERSE_CHUNK_MECO = DOM_U32_FOURCC('M','E','C','O'),
    DOM_UNIVERSE_CHUNK_MEVT = DOM_U32_FOURCC('M','E','V','T'),
    DOM_UNIVERSE_CHUNK_CELE = DOM_U32_FOURCC('C','E','L','E'),
    DOM_UNIVERSE_CHUNK_VESL = DOM_U32_FOURCC('V','E','S','L'),
    DOM_UNIVERSE_CHUNK_SURF = DOM_U32_FOURCC('S','U','R','F'),
    DOM_UNIVERSE_CHUNK_LOCL = DOM_U32_FOURCC('L','O','C','L'),
    DOM_UNIVERSE_CHUNK_RNG  = DOM_U32_FOURCC('R','N','G',' '),
    DOM_UNIVERSE_CHUNK_FORN = DOM_U32_FOURCC('F','O','R','N')
};

enum {
    DOM_UNIVERSE_TLV_UNIVERSE_ID      = 0x0001u,
    DOM_UNIVERSE_TLV_INSTANCE_ID      = 0x0002u,
    DOM_UNIVERSE_TLV_CONTENT_HASH     = 0x0003u,
    DOM_UNIVERSE_TLV_SIM_FLAGS_HASH   = 0x0004u,
    DOM_UNIVERSE_TLV_UPS              = 0x0005u,
    DOM_UNIVERSE_TLV_TICK_INDEX       = 0x0006u,
    DOM_UNIVERSE_TLV_FEATURE_EPOCH    = 0x0007u,
    DOM_UNIVERSE_TLV_COSMO_HASH       = 0x0008u,
    DOM_UNIVERSE_TLV_SYSTEMS_HASH     = 0x0009u,
    DOM_UNIVERSE_TLV_BODIES_HASH      = 0x000Au,
    DOM_UNIVERSE_TLV_FRAMES_HASH      = 0x000Bu,
    DOM_UNIVERSE_TLV_TOPOLOGY_HASH    = 0x000Cu,
    DOM_UNIVERSE_TLV_ORBITS_HASH      = 0x000Du,
    DOM_UNIVERSE_TLV_SURFACE_HASH     = 0x000Eu,
    DOM_UNIVERSE_TLV_CONSTRUCTIONS_HASH = 0x000Fu,
    DOM_UNIVERSE_TLV_STATIONS_HASH    = 0x0010u,
    DOM_UNIVERSE_TLV_ROUTES_HASH      = 0x0011u,
    DOM_UNIVERSE_TLV_TRANSFERS_HASH   = 0x0012u,
    DOM_UNIVERSE_TLV_PRODUCTION_HASH  = 0x0013u,
    DOM_UNIVERSE_TLV_MACRO_ECONOMY_HASH = 0x0014u,
    DOM_UNIVERSE_TLV_MACRO_EVENTS_HASH  = 0x0015u
};

typedef struct dom_universe_bundle_identity {
    const char *universe_id;
    u32 universe_id_len;
    const char *instance_id;
    u32 instance_id_len;
    u64 content_graph_hash;
    u64 sim_flags_hash;
    u64 cosmo_graph_hash;
    u64 systems_hash;
    u64 bodies_hash;
    u64 frames_hash;
    u64 topology_hash;
    u64 orbits_hash;
    u64 surface_overrides_hash;
    u64 constructions_hash;
    u64 stations_hash;
    u64 routes_hash;
    u64 transfers_hash;
    u64 production_hash;
    u64 macro_economy_hash;
    u64 macro_events_hash;
    u32 ups;
    u64 tick_index;
    u32 feature_epoch;
} dom_universe_bundle_identity;

typedef struct dom_universe_bundle dom_universe_bundle;

/* Allocation and lifecycle. */
dom_universe_bundle *dom_universe_bundle_create(void);
void dom_universe_bundle_destroy(dom_universe_bundle *bundle);

/* Identity getters/setters (string pointers are copied into the bundle). */
int dom_universe_bundle_set_identity(dom_universe_bundle *bundle,
                                     const dom_universe_bundle_identity *id);
int dom_universe_bundle_get_identity(const dom_universe_bundle *bundle,
                                     dom_universe_bundle_identity *out_id);

/* Set/get raw payloads for required known chunks (excluding TIME/FORN). */
int dom_universe_bundle_set_chunk(dom_universe_bundle *bundle,
                                  u32 type_id,
                                  u16 version,
                                  const void *payload,
                                  u32 payload_size);
int dom_universe_bundle_get_chunk(const dom_universe_bundle *bundle,
                                  u32 type_id,
                                  const unsigned char **out_payload,
                                  u32 *out_size,
                                  u16 *out_version);

/* Foreign chunk preservation. */
int dom_universe_bundle_clear_foreign(dom_universe_bundle *bundle);
int dom_universe_bundle_add_foreign(dom_universe_bundle *bundle,
                                    u32 type_id,
                                    u16 version,
                                    u16 flags,
                                    const void *payload,
                                    u32 payload_size);

/* Read/write helpers. */
int dom_universe_bundle_read_file(const char *path,
                                  const dom_universe_bundle_identity *expected,
                                  dom_universe_bundle *out_bundle);
int dom_universe_bundle_write_file(const char *path,
                                   const dom_universe_bundle *bundle);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_UNIVERSE_BUNDLE_H */
