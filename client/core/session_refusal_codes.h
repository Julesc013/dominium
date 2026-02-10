#ifndef DOMINIUM_CLIENT_SESSION_REFUSAL_CODES_H
#define DOMINIUM_CLIENT_SESSION_REFUSAL_CODES_H

#ifdef __cplusplus
extern "C" {
#endif

#define CLIENT_SESSION_REFUSE_INVALID_TRANSITION "refuse.invalid_transition"
#define CLIENT_SESSION_REFUSE_BEGIN_REQUIRES_READY "refuse.begin_requires_ready"
#define CLIENT_SESSION_REFUSE_RESUME_REQUIRES_SUSPEND "refuse.resume_requires_suspend"
#define CLIENT_SESSION_REFUSE_PACK_MISSING "refuse.pack_missing"
#define CLIENT_SESSION_REFUSE_SCHEMA_INCOMPATIBLE "refuse.schema_incompatible"
#define CLIENT_SESSION_REFUSE_WORLD_HASH_MISMATCH "refuse.world_hash_mismatch"
#define CLIENT_SESSION_REFUSE_AUTHORITY_DENIED "refuse.authority_denied"

int client_session_refusal_code_known(const char* refusal_code);

#ifdef __cplusplus
}
#endif

#endif
