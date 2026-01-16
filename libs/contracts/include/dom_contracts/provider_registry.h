/*
FILE: include/dominium/provider_registry.h
MODULE: Dominium
PURPOSE: Registry of built-in providers with caps/constraints for solver integration.
NOTES: Entries are append-only; provider IDs are stable ASCII tokens.
*/
#ifndef DOMINIUM_PROVIDER_REGISTRY_H
#define DOMINIUM_PROVIDER_REGISTRY_H

#include "domino/core/types.h"
#include "dom_contracts/core_caps.h"
#include "dom_contracts/core_solver.h"
#include "dom_contracts/provider_base.h"
#include "dom_contracts/provider_content_source.h"
#include "dom_contracts/provider_trust.h"
#include "dom_contracts/provider_keychain.h"
#include "dom_contracts/provider_net.h"
#include "dom_contracts/provider_os_integration.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct provider_registry_entry_t {
    const char* provider_id;
    u32 category_id;
    u32 priority;

    const core_cap_entry* provides;
    u32 provides_count;

    const core_solver_constraint* requires;
    u32 requires_count;

    const core_solver_constraint* forbids;
    u32 forbids_count;

    const core_solver_constraint* prefers;
    u32 prefers_count;

    const char* const* conflicts;
    u32 conflicts_count;

    const provider_base_v1* provider;
} provider_registry_entry;

void provider_registry_get_entries(const provider_registry_entry** out_entries, u32* out_count);
const provider_registry_entry* provider_registry_find(u32 category_id, const char* provider_id);

const provider_content_source_v1* provider_registry_get_content(const char* provider_id);
const provider_trust_v1* provider_registry_get_trust(const char* provider_id);
const provider_keychain_v1* provider_registry_get_keychain(const char* provider_id);
const provider_net_v1* provider_registry_get_net(const char* provider_id);
const provider_os_integration_v1* provider_registry_get_os_integration(const char* provider_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PROVIDER_REGISTRY_H */
