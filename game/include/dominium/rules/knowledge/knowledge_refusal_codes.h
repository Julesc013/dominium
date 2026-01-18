/*
FILE: include/dominium/rules/knowledge/knowledge_refusal_codes.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / knowledge
RESPONSIBILITY: Defines refusal codes for CIV3 knowledge/research/tech.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Refusal codes are stable and deterministic.
*/
#ifndef DOMINIUM_RULES_KNOWLEDGE_REFUSAL_CODES_H
#define DOMINIUM_RULES_KNOWLEDGE_REFUSAL_CODES_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum knowledge_refusal_code {
    KNOW_REFUSAL_NONE = 0,
    KNOW_REFUSAL_MISSING_PREREQUISITES,
    KNOW_REFUSAL_INSUFFICIENT_CAPACITY,
    KNOW_REFUSAL_SECRECY_POLICY_BLOCKS,
    KNOW_REFUSAL_UNKNOWN_KNOWLEDGE,
    KNOW_REFUSAL_INSTITUTION_NOT_AUTHORIZED
} knowledge_refusal_code;

const char* knowledge_refusal_to_string(knowledge_refusal_code code);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_KNOWLEDGE_REFUSAL_CODES_H */
