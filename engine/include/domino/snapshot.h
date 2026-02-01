/*


FILE: include/domino/snapshot.h


MODULE: Domino


LAYER / SUBSYSTEM: Domino API / snapshot


RESPONSIBILITY: Defines immutable snapshot interfaces (objective/subjective).


ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.


FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.


THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.


ERROR MODEL: Return codes/NULL pointers; no exceptions.


DETERMINISM: Snapshot creation and iteration order are deterministic.


VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md`.


EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.


*/


#ifndef DOMINO_SNAPSHOT_H


#define DOMINO_SNAPSHOT_H





#include "domino/core/types.h"


#include "domino/knowledge_state.h"


#include "domino/capability.h"


#include "domino/authority.h"


#include "domino/provenance.h"





#ifdef __cplusplus


extern "C" {


#endif





/* Opaque snapshot handle. */


typedef struct dom_snapshot_handle dom_snapshot_handle;





/* dom_snapshot_kind: Objective or subjective snapshot. */


typedef enum dom_snapshot_kind {


    DOM_SNAPSHOT_OBJECTIVE = 0,


    DOM_SNAPSHOT_SUBJECTIVE = 1


} dom_snapshot_kind;





/* dom_snapshot_flags: Creation flags (explicit cost accounting required). */


typedef enum dom_snapshot_flags {


    DOM_SNAPSHOT_FLAG_NONE = 0u,


    DOM_SNAPSHOT_FLAG_INCLUDE_LATENT = (1u << 0u),


    DOM_SNAPSHOT_FLAG_INCLUDE_UNKNOWN = (1u << 1u)


} dom_snapshot_flags;





/* dom_snapshot_cost: Explicit creation cost metadata. */


typedef struct dom_snapshot_cost {


    u32 cost_units;


    u64 bytes_owned;


    u64 bytes_shared;


} dom_snapshot_cost;





/* dom_snapshot_request: Inputs to snapshot creation. */


typedef struct dom_snapshot_request {


    u64                 schema_id;


    u32                 schema_version;


    dom_snapshot_kind   kind;


    u32                 flags; /* dom_snapshot_flags */


    const dom_authority_token* authority;


    dom_capability_set_view    capability_filter;


} dom_snapshot_request;





/* dom_snapshot_desc: Read-only snapshot metadata. */


typedef struct dom_snapshot_desc {


    u64               schema_id;


    u32               schema_version;


    dom_snapshot_kind kind;


    dom_snapshot_cost cost;


    dom_provenance_id provenance_id;


} dom_snapshot_desc;





/* dom_snapshot_query: Generic query envelope (opaque payloads). */


typedef struct dom_snapshot_query {


    u32        query_id;


    const void* in;


    u32        in_size;


    void*      out;


    u32        out_size;


} dom_snapshot_query;





/* Purpose: Create an immutable snapshot. */


int dom_snapshot_create(const dom_snapshot_request* request,


                        dom_snapshot_handle** out_handle,


                        dom_snapshot_desc* out_desc);





/* Purpose: Release a snapshot handle. */


void dom_snapshot_release(dom_snapshot_handle* snapshot);





/* Purpose: Query a snapshot (read-only). */


int dom_snapshot_query(const dom_snapshot_handle* snapshot,


                       const dom_snapshot_query* query);





#ifdef __cplusplus


} /* extern "C" */


#endif





#endif /* DOMINO_SNAPSHOT_H */


