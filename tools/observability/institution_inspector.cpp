/*
FILE: tools/observability/institution_inspector.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Implements read-only inspection of institution state, constraints, contracts, enforcement, and collapse.
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic filtering and iteration.
*/
#include "institution_inspector.h"

#include <string.h>

static void tool_institution_access_default(tool_access_context* access)
{
    if (!access) {
        return;
    }
    access->mode = TOOL_ACCESS_EPISTEMIC;
    access->knowledge_mask = 0u;
}

int tool_institution_inspector_init(tool_institution_inspector* insp,
                                    const tool_observation_store* store,
                                    const tool_access_context* access,
                                    u64 institution_id)
{
    if (!insp || !store) {
        return TOOL_OBSERVE_INVALID;
    }
    memset(insp, 0, sizeof(*insp));
    insp->store = store;
    insp->institution_id = institution_id;
    if (access) {
        insp->access = *access;
    } else {
        tool_institution_access_default(&insp->access);
    }
    return TOOL_OBSERVE_OK;
}

int tool_institution_inspector_reset(tool_institution_inspector* insp)
{
    if (!insp) {
        return TOOL_OBSERVE_INVALID;
    }
    insp->constraint_cursor = 0u;
    insp->contract_cursor = 0u;
    insp->delegation_cursor = 0u;
    insp->enforcement_cursor = 0u;
    insp->collapse_cursor = 0u;
    return TOOL_OBSERVE_OK;
}

int tool_institution_inspector_state(const tool_institution_inspector* insp,
                                     tool_institution_state* out_state)
{
    u32 i;
    if (!insp || !out_state || !insp->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!insp->store->institutions || insp->store->institution_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    for (i = 0u; i < insp->store->institution_count; ++i) {
        const tool_institution_state* state = &insp->store->institutions[i];
        if (insp->institution_id != 0u && state->institution_id != insp->institution_id) {
            continue;
        }
        if (!tool_inspect_access_allows(&insp->access, state->knowledge_mask)) {
            return TOOL_OBSERVE_REFUSED;
        }
        *out_state = *state;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}

int tool_institution_inspector_next_constraint(tool_institution_inspector* insp,
                                               tool_constraint_record* out_record)
{
    if (!insp || !out_record || !insp->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!insp->store->constraints || insp->store->constraint_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (insp->constraint_cursor < insp->store->constraint_count) {
        const tool_constraint_record* rec = &insp->store->constraints[insp->constraint_cursor++];
        if (insp->institution_id != 0u && rec->institution_id != insp->institution_id) {
            continue;
        }
        if (!tool_inspect_access_allows(&insp->access, rec->required_knowledge)) {
            continue;
        }
        *out_record = *rec;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}

int tool_institution_inspector_next_contract(tool_institution_inspector* insp,
                                             tool_contract_record* out_record)
{
    if (!insp || !out_record || !insp->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!insp->store->contracts || insp->store->contract_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (insp->contract_cursor < insp->store->contract_count) {
        const tool_contract_record* rec = &insp->store->contracts[insp->contract_cursor++];
        if (insp->institution_id != 0u && rec->institution_id != insp->institution_id) {
            continue;
        }
        if (!tool_inspect_access_allows(&insp->access, rec->required_knowledge)) {
            continue;
        }
        *out_record = *rec;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}

int tool_institution_inspector_next_delegation(tool_institution_inspector* insp,
                                               tool_delegation_record* out_record)
{
    if (!insp || !out_record || !insp->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!insp->store->delegations || insp->store->delegation_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (insp->delegation_cursor < insp->store->delegation_count) {
        const tool_delegation_record* rec = &insp->store->delegations[insp->delegation_cursor++];
        if (insp->institution_id != 0u && rec->institution_id != insp->institution_id) {
            continue;
        }
        if (!tool_inspect_access_allows(&insp->access, rec->required_knowledge)) {
            continue;
        }
        *out_record = *rec;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}

int tool_institution_inspector_next_enforcement(tool_institution_inspector* insp,
                                                tool_enforcement_record* out_record)
{
    if (!insp || !out_record || !insp->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!insp->store->enforcement || insp->store->enforcement_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (insp->enforcement_cursor < insp->store->enforcement_count) {
        const tool_enforcement_record* rec = &insp->store->enforcement[insp->enforcement_cursor++];
        if (insp->institution_id != 0u && rec->institution_id != insp->institution_id) {
            continue;
        }
        if (!tool_inspect_access_allows(&insp->access, rec->required_knowledge)) {
            continue;
        }
        *out_record = *rec;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}

int tool_institution_inspector_next_collapse(tool_institution_inspector* insp,
                                             tool_institution_collapse_record* out_record)
{
    if (!insp || !out_record || !insp->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!insp->store->collapses || insp->store->collapse_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (insp->collapse_cursor < insp->store->collapse_count) {
        const tool_institution_collapse_record* rec = &insp->store->collapses[insp->collapse_cursor++];
        if (insp->institution_id != 0u && rec->institution_id != insp->institution_id) {
            continue;
        }
        if (!tool_inspect_access_allows(&insp->access, rec->required_knowledge)) {
            continue;
        }
        *out_record = *rec;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}
