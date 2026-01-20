/*
FILE: engine/modules/execution/budget_model.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/budget_model
RESPONSIBILITY: Implements deterministic budget scaling.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: No wall-clock inputs; deterministic scaling only.
*/
#include "domino/execution/budget_model.h"

#include <string.h>

static u32 dom_exec_budget_scale_from_cores(u32 cores)
{
    if (cores >= 16u) return 4u;
    if (cores >= 8u) return 3u;
    if (cores >= 4u) return 2u;
    if (cores >= 2u) return 1u;
    return 1u;
}

static u32 dom_exec_budget_scale_from_storage(u8 storage_class)
{
    switch (storage_class) {
        case DOM_SYS_CAPS_STORAGE_NVME: return 3u;
        case DOM_SYS_CAPS_STORAGE_SSD: return 2u;
        case DOM_SYS_CAPS_STORAGE_HDD: return 1u;
        default: return 1u;
    }
}

static u32 dom_exec_budget_scale_from_net(u8 net_class)
{
    switch (net_class) {
        case DOM_SYS_CAPS_NET_LAN: return 2u;
        case DOM_SYS_CAPS_NET_WAN: return 1u;
        case DOM_SYS_CAPS_NET_OFFLINE: return 1u;
        default: return 1u;
    }
}

static u32 dom_exec_budget_clamp_scale(u32 scale, u32 min_scale, u32 max_scale)
{
    if (min_scale == 0u) {
        min_scale = 1u;
    }
    if (max_scale == 0u) {
        max_scale = min_scale;
    }
    if (scale < min_scale) {
        return min_scale;
    }
    if (scale > max_scale) {
        return max_scale;
    }
    return scale;
}

static u32 dom_exec_budget_mul_u32(u32 a, u32 b)
{
    u64 prod = (u64)a * (u64)b;
    if (prod > 0xFFFFFFFFu) {
        return 0xFFFFFFFFu;
    }
    return (u32)prod;
}

void dom_exec_budget_profile_init(dom_exec_budget_profile* profile)
{
    if (!profile) {
        return;
    }
    memset(profile, 0, sizeof(*profile));
    profile->memory_class = DOM_EXEC_MEM_UNKNOWN;
    profile->cpu_scale_min = 1u;
    profile->cpu_scale_max = 1u;
    profile->io_scale_max = 1u;
    profile->net_scale_max = 1u;
}

int dom_exec_budget_resolve(const dom_sys_caps_v1* caps,
                            const dom_exec_budget_profile* profile,
                            dom_exec_budget_result* out_result)
{
    u32 cpu_scale;
    u32 io_scale;
    u32 net_scale;

    if (!caps || !profile || !out_result) {
        return -1;
    }

    cpu_scale = dom_exec_budget_scale_from_cores(caps->cpu.logical_cores);
    cpu_scale = dom_exec_budget_clamp_scale(cpu_scale,
                                            profile->cpu_scale_min,
                                            profile->cpu_scale_max);

    io_scale = dom_exec_budget_scale_from_storage(caps->storage.storage_class);
    io_scale = dom_exec_budget_clamp_scale(io_scale, 1u, profile->io_scale_max);

    net_scale = dom_exec_budget_scale_from_net(caps->network.net_class);
    net_scale = dom_exec_budget_clamp_scale(net_scale, 1u, profile->net_scale_max);

    memset(out_result, 0, sizeof(*out_result));
    out_result->cpu_scale = cpu_scale;
    out_result->io_scale = io_scale;
    out_result->net_scale = net_scale;
    out_result->memory_class = profile->memory_class;

    out_result->per_tick_cpu_budget_units_authoritative =
        dom_exec_budget_mul_u32(profile->base_cpu_authoritative, cpu_scale);
    out_result->per_tick_cpu_budget_units_derived =
        dom_exec_budget_mul_u32(profile->base_cpu_derived, cpu_scale);
    out_result->per_tick_io_budget_units_derived =
        dom_exec_budget_mul_u32(profile->base_io_derived, io_scale);
    out_result->per_tick_net_budget_units =
        dom_exec_budget_mul_u32(profile->base_net, net_scale);

    if (profile->degradation_policy_id[0] != '\0') {
        strncpy(out_result->degradation_policy_id,
                profile->degradation_policy_id,
                DOM_EXEC_DEGRADATION_ID_MAX - 1u);
        out_result->degradation_policy_id[DOM_EXEC_DEGRADATION_ID_MAX - 1u] = '\0';
    }

    return 0;
}
