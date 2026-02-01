/*
FILE: include/domino/authority.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / authority
RESPONSIBILITY: Defines opaque authority tokens and scope descriptors.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Authority scopes are deterministic inputs to process execution.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_AUTHORITY_H
#define DOMINO_AUTHORITY_H

#include "domino/core/types.h"
#include "domino/world/domain_tile.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque authority token issued by engine/game initialization. */
typedef struct dom_authority_token dom_authority_token;

/* dom_authority_mutation_class: Bitmask of permitted mutation classes. */
typedef enum dom_authority_mutation_class {
    DOM_AUTH_MUTATE_TRANSFORMATIVE = (1u << 0u),
    DOM_AUTH_MUTATE_TRANSACTIONAL = (1u << 1u),
    DOM_AUTH_MUTATE_EPISTEMIC = (1u << 2u)
} dom_authority_mutation_class;

/* dom_authority_scope: Scope boundaries enforced for mutation. */
typedef struct dom_authority_scope {
    u64           jurisdiction_id;
    dom_domain_id domain_id;
    u32           mutation_class_mask; /* dom_authority_mutation_class */
    u64           audit_identity;
} dom_authority_scope;

/* dom_authority_token_kind: Token capabilities (read-only vs mutating). */
typedef enum dom_authority_token_kind {
    DOM_AUTH_TOKEN_READ_ONLY = 0,
    DOM_AUTH_TOKEN_MUTATING = 1
} dom_authority_token_kind;

/* dom_authority_token_desc: Read-only descriptor for token scope. */
typedef struct dom_authority_token_desc {
    dom_authority_token_kind kind;
    dom_authority_scope      scope;
} dom_authority_token_desc;

/* Purpose: Validate an authority token handle. */
d_bool dom_authority_is_valid(const dom_authority_token* token);

/* Purpose: Describe an authority token scope. */
int dom_authority_describe(const dom_authority_token* token,
                           dom_authority_token_desc* out_desc);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_AUTHORITY_H */
