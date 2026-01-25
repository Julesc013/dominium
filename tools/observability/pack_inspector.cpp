/*
FILE: tools/observability/pack_inspector.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Implements read-only inspection of packs, capabilities, and overrides.
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic filtering and ordering.
*/
#include "pack_inspector.h"

#include <string.h>

int tool_pack_inspector_init(tool_pack_inspector* insp,
                             const tool_observation_store* store)
{
    if (!insp || !store) {
        return TOOL_OBSERVE_INVALID;
    }
    memset(insp, 0, sizeof(*insp));
    insp->store = store;
    return TOOL_OBSERVE_OK;
}

int tool_pack_inspector_next(tool_pack_inspector* insp,
                             tool_pack_record* out_pack)
{
    if (!insp || !out_pack || !insp->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!insp->store->packs || insp->store->pack_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    if (insp->cursor >= insp->store->pack_count) {
        return TOOL_OBSERVE_NO_DATA;
    }
    *out_pack = insp->store->packs[insp->cursor++];
    return TOOL_OBSERVE_OK;
}

int tool_pack_inspector_overrides(const tool_observation_store* store,
                                  tool_pack_record* out_packs,
                                  u32 max_packs,
                                  u32* out_count)
{
    u32 count = 0u;
    u32 i;
    if (!store || !out_packs || !out_count) {
        return TOOL_OBSERVE_INVALID;
    }
    *out_count = 0u;
    if (!store->packs || store->pack_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    for (i = 0u; i < store->pack_count; ++i) {
        const tool_pack_record* pack = &store->packs[i];
        if ((pack->flags & TOOL_PACK_FLAG_OVERRIDE) == 0u) {
            continue;
        }
        if (count < max_packs) {
            out_packs[count] = *pack;
        }
        count += 1u;
    }
    *out_count = count;
    return (count == 0u) ? TOOL_OBSERVE_NO_DATA : TOOL_OBSERVE_OK;
}

int tool_pack_inspector_pack_capabilities(const tool_observation_store* store,
                                          u64 pack_id,
                                          tool_capability_record* out_caps,
                                          u32 max_caps,
                                          u32* out_count)
{
    u32 count = 0u;
    u32 i;
    if (!store || !out_caps || !out_count) {
        return TOOL_OBSERVE_INVALID;
    }
    *out_count = 0u;
    if (!store->capabilities || store->capability_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    for (i = 0u; i < store->capability_count; ++i) {
        const tool_capability_record* cap = &store->capabilities[i];
        if (pack_id != 0u && cap->pack_id != pack_id) {
            continue;
        }
        if (count < max_caps) {
            out_caps[count] = *cap;
        }
        count += 1u;
    }
    *out_count = count;
    return (count == 0u) ? TOOL_OBSERVE_NO_DATA : TOOL_OBSERVE_OK;
}

int tool_pack_inspector_missing_capabilities(const tool_observation_store* store,
                                             const u64* required_ids,
                                             u32 required_count,
                                             u64* out_missing,
                                             u32 max_missing,
                                             u32* out_count)
{
    u32 i;
    u32 count = 0u;
    if (!store || !required_ids || !out_missing || !out_count) {
        return TOOL_OBSERVE_INVALID;
    }
    *out_count = 0u;
    if (required_count == 0u) {
        return TOOL_OBSERVE_OK;
    }
    for (i = 0u; i < required_count; ++i) {
        u64 required_id = required_ids[i];
        u32 j;
        int found = 0;
        if (!store->capabilities || store->capability_count == 0u) {
            found = 0;
        } else {
            for (j = 0u; j < store->capability_count; ++j) {
                if (store->capabilities[j].capability_id == required_id) {
                    found = 1;
                    break;
                }
            }
        }
        if (!found) {
            if (count < max_missing) {
                out_missing[count] = required_id;
            }
            count += 1u;
        }
    }
    *out_count = count;
    return (count == 0u) ? TOOL_OBSERVE_NO_DATA : TOOL_OBSERVE_OK;
}
