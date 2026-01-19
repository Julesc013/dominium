/*
FILE: game/core/life/life_refusal_codes.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Provides string names for death/estate refusal codes.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: String mapping is stable.
*/
#include "dominium/life/life_refusal_codes.h"

const char* life_death_refusal_to_string(life_death_refusal_code code)
{
    switch (code) {
        case LIFE_DEATH_REFUSAL_NONE: return "none";
        case LIFE_DEATH_REFUSAL_BODY_NOT_ALIVE: return "body_not_alive";
        case LIFE_DEATH_REFUSAL_PERSON_MISSING: return "person_missing";
        case LIFE_DEATH_REFUSAL_LEDGER_ACCOUNT_MISSING: return "ledger_account_missing";
        case LIFE_DEATH_REFUSAL_ESTATE_ALREADY_EXISTS: return "estate_already_exists";
        case LIFE_DEATH_REFUSAL_NO_EXECUTOR_AUTHORITY: return "no_executor_authority";
        case LIFE_DEATH_REFUSAL_SCHEDULE_INVALID: return "schedule_invalid";
        default: return "unknown";
    }
}
