/*
FILE: source/dominium/setup/core/src/platform_iface/dsu_platform_iface_internal.h
MODULE: Dominium Setup
PURPOSE: Internal helpers for encoding/decoding platform registration intents (Plan S-6).
*/
#ifndef DSU_PLATFORM_IFACE_INTERNAL_H_INCLUDED
#define DSU_PLATFORM_IFACE_INTERNAL_H_INCLUDED

#include "dsu/dsu_platform_iface.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Encode/decode canonical registration strings stored in installed-state. */
dsu_status_t dsu__platform_encode_intent_v1(const dsu_platform_intent_t *intent, char **out_ascii);
dsu_status_t dsu__platform_decode_intent_v1(const char *ascii, dsu_platform_intent_t *out_intent);
void dsu__platform_intent_free_fields(dsu_platform_intent_t *intent);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_PLATFORM_IFACE_INTERNAL_H_INCLUDED */

