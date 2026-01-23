/*
FILE: include/domino/knowledge_state.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / knowledge_state
RESPONSIBILITY: Defines latent/known/inferred state metadata for epistemic data.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: All fields are deterministic inputs/outputs; no wall-clock dependence.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_KNOWLEDGE_STATE_H
#define DOMINO_KNOWLEDGE_STATE_H

#include "domino/dnumeric.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_knowledge_state: Knowledge classification for latent/unknown state. */
typedef enum dom_knowledge_state {
    DOM_KNOWLEDGE_UNKNOWN = 0,
    DOM_KNOWLEDGE_INFERRED = 1,
    DOM_KNOWLEDGE_KNOWN = 2
} dom_knowledge_state;

/* dom_knowledge_meta: Deterministic epistemic metadata (no implicit sensing). */
typedef struct dom_knowledge_meta {
    dom_knowledge_state state;
    u32                 uncertainty_q16; /* 0..65535, where 0 is certain */
    SimTick             observed_tick;
    SimTick             expires_tick;
} dom_knowledge_meta;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_KNOWLEDGE_STATE_H */
