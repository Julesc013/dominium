/*
FILE: include/domino/agent.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / agent
RESPONSIBILITY: Defines agent identity, lifecycle, and access contracts.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Agent queries and snapshots are deterministic for identical inputs.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_AGENT_H
#define DOMINO_AGENT_H

#include "domino/core/types.h"
#include "domino/process.h"
#include "domino/capability.h"
#include "domino/authority.h"
#include "domino/provenance.h"
#include "domino/snapshot.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_agent_id: Stable, globally-unique agent identifier. */
typedef u64 dom_agent_id;
#define DOM_AGENT_ID_INVALID ((dom_agent_id)0u)

/* Opaque handles for agent view lifetimes. */
typedef struct dom_agent_capability_handle dom_agent_capability_handle;
typedef struct dom_agent_authority_handle dom_agent_authority_handle;
typedef struct dom_agent_history_handle dom_agent_history_handle;

/* dom_agent_snapshot_kind: Subjective by default (zero). */
typedef enum dom_agent_snapshot_kind {
    DOM_AGENT_SNAPSHOT_SUBJECTIVE = 0,
    DOM_AGENT_SNAPSHOT_OBJECTIVE = 1
} dom_agent_snapshot_kind;

/* dom_agent_snapshot_request: Inputs to agent snapshot creation. */
typedef struct dom_agent_snapshot_request {
    u64                     schema_id;
    u32                     schema_version;
    dom_agent_snapshot_kind kind; /* default: DOM_AGENT_SNAPSHOT_SUBJECTIVE */
    u32                     flags; /* dom_snapshot_flags */
    const dom_authority_token* authority;
    dom_capability_set_view   capability_filter;
} dom_agent_snapshot_request;

/* dom_agent_desc: Read-only agent metadata. */
typedef struct dom_agent_desc {
    dom_agent_id      id;
    u32               existence_state_id; /* schema-defined */
    u32               flags;
    dom_provenance_id provenance_id; /* latest authoritative provenance */
    dom_process_id    last_process_id; /* 0 when unknown */
} dom_agent_desc;

/* dom_agent_create_request: Inputs for agent creation via process execution. */
typedef struct dom_agent_create_request {
    const dom_process_exec_context* process;
    u64                              archetype_id; /* data-defined */
    u32                              existence_state_id; /* 0 uses process default */
    dom_capability_set_view          initial_capabilities;
    const dom_authority_token* const* authority_tokens;
    u32                              authority_token_count;
    u32                              flags;
} dom_agent_create_request;

/* dom_agent_terminate_request: Inputs for agent termination via process execution. */
typedef struct dom_agent_terminate_request {
    const dom_process_exec_context* process;
    dom_agent_id                    agent_id;
    u32                             termination_reason_id; /* data-defined */
    u32                             flags;
} dom_agent_terminate_request;

/* dom_agent_authority_view: Borrowed authority token list. */
typedef struct dom_agent_authority_view {
    const dom_authority_token* const* tokens;
    u32                               count;
} dom_agent_authority_view;

/* dom_agent_history_desc: Read-only history metadata. */
typedef struct dom_agent_history_desc {
    dom_agent_id      id;
    u32               flags;
    dom_provenance_id first_provenance_id;
    dom_provenance_id last_provenance_id;
} dom_agent_history_desc;

/* dom_agent_history_query: Opaque history query envelope. */
typedef struct dom_agent_history_query {
    u32         query_id;
    const void* in;
    u32         in_size;
    void*       out;
    u32         out_size;
} dom_agent_history_query;

/* Purpose: Create a new agent via a process execution context. */
int dom_agent_create(const dom_agent_create_request* request,
                     dom_agent_id* out_agent_id,
                     dom_agent_desc* out_desc);

/* Purpose: Query agent metadata by id. */
int dom_agent_query(dom_agent_id agent_id,
                    dom_agent_desc* out_desc);

/* Purpose: Query agent capabilities (borrowed view + explicit release). */
int dom_agent_capabilities(dom_agent_id agent_id,
                           dom_agent_capability_handle** out_handle,
                           dom_capability_set_view* out_caps);

/* Purpose: Release a capability view handle. */
void dom_agent_capabilities_release(dom_agent_capability_handle* handle);

/* Purpose: Query agent authority tokens (borrowed view + explicit release). */
int dom_agent_authority(dom_agent_id agent_id,
                        dom_agent_authority_handle** out_handle,
                        dom_agent_authority_view* out_view);

/* Purpose: Release an authority view handle. */
void dom_agent_authority_release(dom_agent_authority_handle* handle);

/* Purpose: Create an agent snapshot (subjective by default). */
int dom_agent_snapshot(dom_agent_id agent_id,
                       const dom_agent_snapshot_request* request,
                       dom_snapshot_handle** out_snapshot,
                       dom_snapshot_desc* out_desc);

/* Purpose: Open agent history for query. */
int dom_agent_history(dom_agent_id agent_id,
                      dom_agent_history_handle** out_handle,
                      dom_agent_history_desc* out_desc);

/* Purpose: Query agent history (read-only). */
int dom_agent_history_query(const dom_agent_history_handle* history,
                            const dom_agent_history_query* query);

/* Purpose: Release an agent history handle. */
void dom_agent_history_release(dom_agent_history_handle* history);

/* Purpose: Terminate an agent via a process execution context. */
int dom_agent_terminate(const dom_agent_terminate_request* request,
                        dom_agent_desc* out_desc);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_AGENT_H */
