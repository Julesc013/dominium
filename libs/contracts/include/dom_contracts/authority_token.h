/*
FILE: include/dom_contracts/authority_token.h
MODULE: Dominium
PURPOSE: Authority token format and deterministic validation helpers (TESTX3).
NOTES: Uses a deterministic checksum for test validation; production issuers
must provide signed tokens per platform policy.
REFERENCES: docs/arch/AUTHORITY_AND_ENTITLEMENTS.md
*/
#ifndef DOM_CONTRACTS_AUTHORITY_TOKEN_H
#define DOM_CONTRACTS_AUTHORITY_TOKEN_H

#include "dom_contracts/authority.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_MSC_VER)
#define DOM_AUTH_U64_FMT "I64u"
#define DOM_AUTH_STRTOULL _strtoui64
#else
#define DOM_AUTH_U64_FMT "llu"
#define DOM_AUTH_STRTOULL strtoull
#endif

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_AUTH_TOKEN_PREFIX "AUTH1"
#define DOM_AUTH_TOKEN_SALT "DOMINIUM_AUTH_V1"
#define DOM_AUTH_TOKEN_MAX 256u

typedef struct dom_authority_token_fields_s {
    u32 profile;
    u32 scope_id;
    u64 issued_act;
    u64 expires_act;
    u32 signature;
} dom_authority_token_fields;

static u32 dom_auth_token_fnv1a(const char* s)
{
    u32 hash = 2166136261u;
    const unsigned char* p = (const unsigned char*)s;
    while (*p) {
        hash ^= (u32)(*p);
        hash *= 16777619u;
        ++p;
    }
    return hash;
}

static u32 dom_auth_token_compute_signature(u32 profile,
                                            u32 scope_id,
                                            u64 issued_act,
                                            u64 expires_act)
{
    char payload[160];
    payload[0] = '\0';
    sprintf(payload,
            "%s|p=%u|s=%u|i=%" DOM_AUTH_U64_FMT "|e=%" DOM_AUTH_U64_FMT "|%s",
            DOM_AUTH_TOKEN_PREFIX,
            (unsigned int)profile,
            (unsigned int)scope_id,
            (unsigned long long)issued_act,
            (unsigned long long)expires_act,
            DOM_AUTH_TOKEN_SALT);
    return dom_auth_token_fnv1a(payload);
}

static int dom_auth_token_build(char* out,
                                u32 out_len,
                                u32 profile,
                                u32 scope_id,
                                u64 issued_act,
                                u64 expires_act)
{
    u32 sig;
    u32 written;
    if (!out || out_len < DOM_AUTH_TOKEN_MAX) {
        return 0;
    }
    sig = dom_auth_token_compute_signature(profile, scope_id, issued_act, expires_act);
    sprintf(out,
            "%s|p=%u|s=%u|i=%" DOM_AUTH_U64_FMT "|e=%" DOM_AUTH_U64_FMT "|sig=%08x",
            DOM_AUTH_TOKEN_PREFIX,
            (unsigned int)profile,
            (unsigned int)scope_id,
            (unsigned long long)issued_act,
            (unsigned long long)expires_act,
            (unsigned int)sig);
    written = (u32)strlen(out);
    if (written == 0u || written >= out_len) {
        return 0;
    }
    return 1;
}

static int dom_auth_token_parse(const char* token, dom_authority_token_fields* out)
{
    char buf[DOM_AUTH_TOKEN_MAX];
    char* rest;
    char* next;
    if (!token || !out) {
        return 0;
    }
    memset(out, 0, sizeof(*out));
    if (strlen(token) >= sizeof(buf)) {
        return 0;
    }
    strcpy(buf, token);
    if (strncmp(buf, DOM_AUTH_TOKEN_PREFIX, strlen(DOM_AUTH_TOKEN_PREFIX)) != 0) {
        return 0;
    }
    rest = buf + strlen(DOM_AUTH_TOKEN_PREFIX);
    if (*rest != '|') {
        return 0;
    }
    rest += 1;
    while (rest && *rest) {
        next = strchr(rest, '|');
        if (next) {
            *next = '\0';
        }
        if (rest[0] == 'p' && rest[1] == '=') {
            out->profile = (u32)strtoul(rest + 2, (char**)0, 10);
        } else if (rest[0] == 's' && rest[1] == '=') {
            out->scope_id = (u32)strtoul(rest + 2, (char**)0, 10);
        } else if (rest[0] == 'i' && rest[1] == '=') {
            out->issued_act = (u64)DOM_AUTH_STRTOULL(rest + 2, (char**)0, 10);
        } else if (rest[0] == 'e' && rest[1] == '=') {
            out->expires_act = (u64)DOM_AUTH_STRTOULL(rest + 2, (char**)0, 10);
        } else if (strncmp(rest, "sig=", 4) == 0) {
            out->signature = (u32)strtoul(rest + 4, (char**)0, 16);
        }
        if (!next) {
            break;
        }
        rest = next + 1;
    }
    return 1;
}

static int dom_auth_token_validate(const char* token, dom_authority_token_fields* out)
{
    u32 expected;
    dom_authority_token_fields fields;
    if (!dom_auth_token_parse(token, &fields)) {
        return 0;
    }
    expected = dom_auth_token_compute_signature(fields.profile,
                                               fields.scope_id,
                                               fields.issued_act,
                                               fields.expires_act);
    if (expected != fields.signature) {
        return 0;
    }
    if (out) {
        *out = fields;
    }
    return 1;
}

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_CONTRACTS_AUTHORITY_TOKEN_H */
