#include "session_refusal_codes.h"

#include <string.h>

static const char* k_known_refusal_codes[] = {
    CLIENT_SESSION_REFUSE_INVALID_TRANSITION,
    CLIENT_SESSION_REFUSE_BEGIN_REQUIRES_READY,
    CLIENT_SESSION_REFUSE_RESUME_REQUIRES_SUSPEND,
    CLIENT_SESSION_REFUSE_PACK_MISSING,
    CLIENT_SESSION_REFUSE_SCHEMA_INCOMPATIBLE,
    CLIENT_SESSION_REFUSE_WORLD_HASH_MISMATCH,
    CLIENT_SESSION_REFUSE_AUTHORITY_DENIED
};

int client_session_refusal_code_known(const char* refusal_code)
{
    unsigned int i = 0u;
    if (!refusal_code || !refusal_code[0]) {
        return 0;
    }
    for (i = 0u; i < (unsigned int)(sizeof(k_known_refusal_codes) / sizeof(k_known_refusal_codes[0])); ++i) {
        if (strcmp(refusal_code, k_known_refusal_codes[i]) == 0) {
            return 1;
        }
    }
    return 0;
}
