/*
Build identity provider for application-layer reporting.
*/
#ifndef DOM_BUILD_IDENTITY_H
#define DOM_BUILD_IDENTITY_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_build_identity {
    const char* build_kind;
    const char* bii;
    const char* gbn;
    const char* git_commit;
    const char* build_timestamp;
} dom_build_identity;

dom_build_identity dom_build_identity_get(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_BUILD_IDENTITY_H */
