/*
FILE: game/rules/knowledge/knowledge_refusal_codes.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / knowledge
RESPONSIBILITY: Implements refusal code string conversion.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Refusal codes are stable and deterministic.
*/
#include "dominium/rules/knowledge/knowledge_refusal_codes.h"

const char* knowledge_refusal_to_string(knowledge_refusal_code code)
{
    switch (code) {
        case KNOW_REFUSAL_NONE: return "none";
        case KNOW_REFUSAL_MISSING_PREREQUISITES: return "missing_prerequisites";
        case KNOW_REFUSAL_INSUFFICIENT_CAPACITY: return "insufficient_capacity";
        case KNOW_REFUSAL_SECRECY_POLICY_BLOCKS: return "secrecy_policy_blocks";
        case KNOW_REFUSAL_UNKNOWN_KNOWLEDGE: return "unknown_knowledge";
        case KNOW_REFUSAL_INSTITUTION_NOT_AUTHORIZED: return "institution_not_authorized";
        default: return "unknown";
    }
}
