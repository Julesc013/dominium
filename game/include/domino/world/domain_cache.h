/*


FILE: include/domino/world/domain_cache.h


MODULE: Domino


LAYER / SUBSYSTEM: Domino API / world/domain_cache


RESPONSIBILITY: Defines deterministic domain tile caching and invalidation.


ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.


FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.


THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.


ERROR MODEL: Return codes/NULL pointers; no exceptions.


DETERMINISM: Deterministic eviction and stable ordering.


VERSIONING / ABI / DATA FORMAT NOTES: Versioned by DOMAIN1 specs.


EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.


*/


#ifndef DOMINO_WORLD_DOMAIN_CACHE_H


#define DOMINO_WORLD_DOMAIN_CACHE_H





#include "domino/world/domain_tile.h"





#ifdef __cplusplus


extern "C" {


#endif





typedef struct dom_domain_cache_entry {


    dom_domain_id  domain_id;


    u64            tile_id;


    u32            resolution;        /* dom_domain_resolution */


    u32            authoring_version;


    u64            last_used;


    u64            insert_order;


    d_bool         valid;


    dom_domain_tile tile;


} dom_domain_cache_entry;





typedef struct dom_domain_cache {


    dom_domain_cache_entry *entries;


    u32                    capacity;


    u32                    count;


    u64                    use_counter;


    u64                    next_insert_order;


} dom_domain_cache;





void dom_domain_cache_init(dom_domain_cache* cache);


void dom_domain_cache_free(dom_domain_cache* cache);


int  dom_domain_cache_reserve(dom_domain_cache* cache, u32 capacity);





const dom_domain_tile* dom_domain_cache_peek(const dom_domain_cache* cache,


                                             dom_domain_id domain_id,


                                             u64 tile_id,


                                             u32 resolution,


                                             u32 authoring_version);





const dom_domain_tile* dom_domain_cache_get(dom_domain_cache* cache,


                                            dom_domain_id domain_id,


                                            u64 tile_id,


                                            u32 resolution,


                                            u32 authoring_version);





dom_domain_tile* dom_domain_cache_put(dom_domain_cache* cache,


                                      dom_domain_id domain_id,


                                      dom_domain_tile* tile);





void dom_domain_cache_invalidate_domain(dom_domain_cache* cache, dom_domain_id domain_id);


void dom_domain_cache_invalidate_version(dom_domain_cache* cache, u32 authoring_version);


void dom_domain_cache_invalidate_all(dom_domain_cache* cache);





#ifdef __cplusplus


} /* extern "C" */


#endif





#endif /* DOMINO_WORLD_DOMAIN_CACHE_H */


