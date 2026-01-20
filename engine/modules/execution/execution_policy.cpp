/*
FILE: engine/modules/execution/execution_policy.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/execution_policy
RESPONSIBILITY: Implements deterministic execution policy selection.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Selection is deterministic given identical inputs.
*/
#include "domino/execution/execution_policy.h"

#include "domino/io/container.h"

#include <string.h>
#include <stdio.h>
#include <stdlib.h>

static d_bool dom_exec_policy_is_scheduler_id(u32 id)
{
    return (id == DOM_EXEC_SCHED_EXEC2_SINGLE_THREAD ||
            id == DOM_EXEC_SCHED_EXEC3_PARALLEL) ? D_TRUE : D_FALSE;
}

static d_bool dom_exec_policy_is_kernel_id(u32 id)
{
    return (id <= DOM_KERNEL_BACKEND_GPU) ? D_TRUE : D_FALSE;
}

static d_bool dom_exec_policy_order_is_valid(const u32* order,
                                             u32 count,
                                             d_bool (*is_valid)(u32))
{
    u32 i;
    u32 j;
    if (!order || count == 0u || count > DOM_EXEC_POLICY_MAX_ORDER) {
        return D_FALSE;
    }
    for (i = 0u; i < count; ++i) {
        if (!is_valid(order[i])) {
            return D_FALSE;
        }
        for (j = 0u; j < i; ++j) {
            if (order[i] == order[j]) {
                return D_FALSE;
            }
        }
    }
    return D_TRUE;
}

static void dom_exec_copy_string(char* dst,
                                 u32 dst_cap,
                                 const unsigned char* src,
                                 u32 src_len)
{
    u32 copy_len;
    if (!dst || dst_cap == 0u) {
        return;
    }
    copy_len = src_len;
    if (copy_len >= dst_cap) {
        copy_len = dst_cap - 1u;
    }
    if (copy_len > 0u && src) {
        memcpy(dst, src, (size_t)copy_len);
    }
    dst[copy_len] = '\0';
}

void dom_exec_profile_init(dom_exec_profile_config* config)
{
    if (!config) {
        return;
    }
    memset(config, 0, sizeof(*config));
    dom_exec_budget_profile_init(&config->budget_profile);
}

void dom_exec_policy_init(dom_exec_policy* policy)
{
    if (!policy) {
        return;
    }
    memset(policy, 0, sizeof(*policy));
    policy->scheduler_backend = DOM_EXEC_SCHED_EXEC2_SINGLE_THREAD;
    policy->ecs_backend = DOM_EXEC_ECS_SOA_DEFAULT;
    policy->kernel_mask_strict = DOM_KERNEL_BACKEND_MASK_SCALAR;
    policy->kernel_mask_derived = DOM_KERNEL_BACKEND_MASK_SCALAR;
}

int dom_exec_profile_load_tlv(const char* path,
                              dom_exec_profile_config* out_config)
{
    dtlv_reader reader;
    const dtlv_dir_entry* entry;
    unsigned char* chunk_bytes = 0;
    u32 chunk_len = 0;
    u32 offset = 0;
    u32 tag = 0;
    const unsigned char* payload = 0;
    u32 payload_len = 0;
    u32 required_mask = 0u;
    int rc;

    enum {
        REQ_PROFILE_ID = 1u << 0u,
        REQ_SCHED_ORDER = 1u << 1u,
        REQ_KERNEL_ORDER = 1u << 2u,
        REQ_ALLOW_MASK = 1u << 3u,
        REQ_BUDGET_ID = 1u << 4u,
        REQ_BUDGET_CPU_AUTH = 1u << 5u,
        REQ_BUDGET_CPU_DER = 1u << 6u,
        REQ_BUDGET_IO_DER = 1u << 7u,
        REQ_BUDGET_NET = 1u << 8u,
        REQ_MEM_CLASS = 1u << 9u,
        REQ_DEGRADATION_ID = 1u << 10u,
        REQ_CPU_SCALE_MIN = 1u << 11u,
        REQ_CPU_SCALE_MAX = 1u << 12u,
        REQ_IO_SCALE_MAX = 1u << 13u,
        REQ_NET_SCALE_MAX = 1u << 14u
    };
    const u32 required_all = REQ_PROFILE_ID | REQ_SCHED_ORDER | REQ_KERNEL_ORDER |
                             REQ_ALLOW_MASK | REQ_BUDGET_ID | REQ_BUDGET_CPU_AUTH |
                             REQ_BUDGET_CPU_DER | REQ_BUDGET_IO_DER | REQ_BUDGET_NET |
                             REQ_MEM_CLASS | REQ_DEGRADATION_ID | REQ_CPU_SCALE_MIN |
                             REQ_CPU_SCALE_MAX | REQ_IO_SCALE_MAX | REQ_NET_SCALE_MAX;

    if (!path || !out_config) {
        return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
    }

    dom_exec_profile_init(out_config);
    dtlv_reader_init(&reader);
    if (dtlv_reader_open_file(&reader, path) != 0) {
        dtlv_reader_dispose(&reader);
        return DOM_EXEC_PROFILE_LOAD_ERR_IO;
    }
    entry = dtlv_reader_find_first(&reader, DOM_EXEC_PROFILE_CHUNK, DOM_EXEC_PROFILE_CHUNK_VERSION);
    if (!entry) {
        dtlv_reader_dispose(&reader);
        return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
    }
    if (dtlv_reader_read_chunk_alloc(&reader, entry, &chunk_bytes, &chunk_len) != 0) {
        dtlv_reader_dispose(&reader);
        return DOM_EXEC_PROFILE_LOAD_ERR_IO;
    }

    while ((rc = dtlv_tlv_next(chunk_bytes, chunk_len, &offset,
                               &tag, &payload, &payload_len)) == 0) {
        switch (tag) {
            case DOM_EXEC_TLV_PROFILE_ID:
                dom_exec_copy_string(out_config->profile_id,
                                     DOM_EXEC_PROFILE_ID_MAX,
                                     payload, payload_len);
                required_mask |= REQ_PROFILE_ID;
                break;
            case DOM_EXEC_TLV_SCHED_ORDER: {
                u32 count;
                u32 i;
                if (payload_len == 0u || (payload_len % 4u) != 0u) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                count = payload_len / 4u;
                if (count > DOM_EXEC_POLICY_MAX_ORDER) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                for (i = 0u; i < count; ++i) {
                    out_config->scheduler_order[i] = dtlv_le_read_u32(payload + (i * 4u));
                }
                out_config->scheduler_order_count = count;
                if (!dom_exec_policy_order_is_valid(out_config->scheduler_order,
                                                    out_config->scheduler_order_count,
                                                    dom_exec_policy_is_scheduler_id)) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                required_mask |= REQ_SCHED_ORDER;
                break;
            }
            case DOM_EXEC_TLV_KERNEL_ORDER: {
                u32 count;
                u32 i;
                if (payload_len == 0u || (payload_len % 4u) != 0u) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                count = payload_len / 4u;
                if (count > DOM_EXEC_POLICY_MAX_ORDER) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                for (i = 0u; i < count; ++i) {
                    out_config->kernel_order[i] = dtlv_le_read_u32(payload + (i * 4u));
                }
                out_config->kernel_order_count = count;
                if (!dom_exec_policy_order_is_valid(out_config->kernel_order,
                                                    out_config->kernel_order_count,
                                                    dom_exec_policy_is_kernel_id)) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                required_mask |= REQ_KERNEL_ORDER;
                break;
            }
            case DOM_EXEC_TLV_ALLOW_MASK:
                if (payload_len != 4u) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                out_config->allow_mask = dtlv_le_read_u32(payload);
                required_mask |= REQ_ALLOW_MASK;
                break;
            case DOM_EXEC_TLV_MIN_CORES:
                if (payload_len != 4u) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                out_config->min_cores_for_exec3 = dtlv_le_read_u32(payload);
                break;
            case DOM_EXEC_TLV_BUDGET_ID:
                dom_exec_copy_string(out_config->budget_profile.budget_profile_id,
                                     DOM_EXEC_BUDGET_ID_MAX,
                                     payload, payload_len);
                required_mask |= REQ_BUDGET_ID;
                break;
            case DOM_EXEC_TLV_BUDGET_CPU_AUTH:
                if (payload_len != 4u) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                out_config->budget_profile.base_cpu_authoritative = dtlv_le_read_u32(payload);
                required_mask |= REQ_BUDGET_CPU_AUTH;
                break;
            case DOM_EXEC_TLV_BUDGET_CPU_DER:
                if (payload_len != 4u) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                out_config->budget_profile.base_cpu_derived = dtlv_le_read_u32(payload);
                required_mask |= REQ_BUDGET_CPU_DER;
                break;
            case DOM_EXEC_TLV_BUDGET_IO_DER:
                if (payload_len != 4u) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                out_config->budget_profile.base_io_derived = dtlv_le_read_u32(payload);
                required_mask |= REQ_BUDGET_IO_DER;
                break;
            case DOM_EXEC_TLV_BUDGET_NET:
                if (payload_len != 4u) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                out_config->budget_profile.base_net = dtlv_le_read_u32(payload);
                required_mask |= REQ_BUDGET_NET;
                break;
            case DOM_EXEC_TLV_MEM_CLASS:
                if (payload_len != 4u) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                out_config->budget_profile.memory_class = dtlv_le_read_u32(payload);
                required_mask |= REQ_MEM_CLASS;
                break;
            case DOM_EXEC_TLV_DEGRADATION_ID:
                dom_exec_copy_string(out_config->budget_profile.degradation_policy_id,
                                     DOM_EXEC_DEGRADATION_ID_MAX,
                                     payload, payload_len);
                required_mask |= REQ_DEGRADATION_ID;
                break;
            case DOM_EXEC_TLV_CPU_SCALE_MIN:
                if (payload_len != 4u) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                out_config->budget_profile.cpu_scale_min = dtlv_le_read_u32(payload);
                required_mask |= REQ_CPU_SCALE_MIN;
                break;
            case DOM_EXEC_TLV_CPU_SCALE_MAX:
                if (payload_len != 4u) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                out_config->budget_profile.cpu_scale_max = dtlv_le_read_u32(payload);
                required_mask |= REQ_CPU_SCALE_MAX;
                break;
            case DOM_EXEC_TLV_IO_SCALE_MAX:
                if (payload_len != 4u) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                out_config->budget_profile.io_scale_max = dtlv_le_read_u32(payload);
                required_mask |= REQ_IO_SCALE_MAX;
                break;
            case DOM_EXEC_TLV_NET_SCALE_MAX:
                if (payload_len != 4u) {
                    free(chunk_bytes);
                    dtlv_reader_dispose(&reader);
                    return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
                }
                out_config->budget_profile.net_scale_max = dtlv_le_read_u32(payload);
                required_mask |= REQ_NET_SCALE_MAX;
                break;
            case DOM_EXEC_TLV_RENDER_ALLOW:
                if (out_config->render_allowlist_count < DOM_EXEC_POLICY_RENDER_ALLOWLIST_MAX) {
                    char* dst = out_config->render_allowlist[out_config->render_allowlist_count++];
                    dom_exec_copy_string(dst, DOM_EXEC_POLICY_RENDER_NAME_MAX, payload, payload_len);
                }
                break;
            default:
                break;
        }
    }

    free(chunk_bytes);
    dtlv_reader_dispose(&reader);

    if (rc < 0) {
        return DOM_EXEC_PROFILE_LOAD_ERR_FORMAT;
    }
    if ((required_mask & required_all) != required_all) {
        return DOM_EXEC_PROFILE_LOAD_ERR_MISSING;
    }
    return DOM_EXEC_PROFILE_LOAD_OK;
}

static d_bool dom_exec_caps_simd_available(const dom_sys_caps_v1* caps)
{
    if (!caps) {
        return D_FALSE;
    }
    return (caps->cpu.simd_caps.sse2 == DOM_SYS_CAPS_BOOL_TRUE ||
            caps->cpu.simd_caps.sse4 == DOM_SYS_CAPS_BOOL_TRUE ||
            caps->cpu.simd_caps.avx2 == DOM_SYS_CAPS_BOOL_TRUE ||
            caps->cpu.simd_caps.avx512 == DOM_SYS_CAPS_BOOL_TRUE ||
            caps->cpu.simd_caps.neon == DOM_SYS_CAPS_BOOL_TRUE ||
            caps->cpu.simd_caps.sve == DOM_SYS_CAPS_BOOL_TRUE) ? D_TRUE : D_FALSE;
}

static d_bool dom_exec_caps_gpu_available(const dom_sys_caps_v1* caps)
{
    if (!caps) {
        return D_FALSE;
    }
    if (!caps->gpu.has_gpu) {
        return D_FALSE;
    }
    return (caps->gpu.has_compute_queue == DOM_SYS_CAPS_BOOL_TRUE) ? D_TRUE : D_FALSE;
}

static const char* dom_exec_scheduler_name(u32 id)
{
    switch (id) {
        case DOM_EXEC_SCHED_EXEC2_SINGLE_THREAD: return "exec2_single_thread";
        case DOM_EXEC_SCHED_EXEC3_PARALLEL: return "exec3_parallel";
        default: return "unknown";
    }
}

static u64 dom_exec_policy_hash_u8(u64 h, u8 v)
{
    h ^= (u64)v;
    h *= 1099511628211ULL;
    return h;
}

static u64 dom_exec_policy_hash_u32(u64 h, u32 v)
{
    h = dom_exec_policy_hash_u8(h, (u8)(v & 0xFFu));
    h = dom_exec_policy_hash_u8(h, (u8)((v >> 8u) & 0xFFu));
    h = dom_exec_policy_hash_u8(h, (u8)((v >> 16u) & 0xFFu));
    h = dom_exec_policy_hash_u8(h, (u8)((v >> 24u) & 0xFFu));
    return h;
}

static u64 dom_exec_policy_hash_u64(u64 h, u64 v)
{
    h = dom_exec_policy_hash_u8(h, (u8)(v & 0xFFu));
    h = dom_exec_policy_hash_u8(h, (u8)((v >> 8u) & 0xFFu));
    h = dom_exec_policy_hash_u8(h, (u8)((v >> 16u) & 0xFFu));
    h = dom_exec_policy_hash_u8(h, (u8)((v >> 24u) & 0xFFu));
    h = dom_exec_policy_hash_u8(h, (u8)((v >> 32u) & 0xFFu));
    h = dom_exec_policy_hash_u8(h, (u8)((v >> 40u) & 0xFFu));
    h = dom_exec_policy_hash_u8(h, (u8)((v >> 48u) & 0xFFu));
    h = dom_exec_policy_hash_u8(h, (u8)((v >> 56u) & 0xFFu));
    return h;
}

int dom_exec_policy_select(const dom_sys_caps_v1* caps,
                           const dom_exec_profile_config* profile,
                           const dom_exec_law_constraints* law,
                           dom_exec_policy* out_policy)
{
    u32 sched_order_buf[2];
    const u32* sched_order = 0;
    u32 sched_count = 0u;
    u32 requested_sched = DOM_EXEC_SCHED_EXEC2_SINGLE_THREAD;
    u32 selected_sched = DOM_EXEC_SCHED_EXEC2_SINGLE_THREAD;
    d_bool found_sched = D_FALSE;
    u32 kernel_mask_profile;
    u32 kernel_mask_law;
    u32 kernel_mask_caps;
    u32 kernel_mask_strict;
    u32 kernel_mask_derived;
    d_bool simd_available;
    d_bool gpu_available;
    u32 i;
    int rc;

    if (!caps || !profile || !law || !out_policy) {
        return -1;
    }

    dom_exec_policy_init(out_policy);
    out_policy->audit.syscaps_hash = dom_sys_caps_hash64(caps);

    sched_order = profile->scheduler_order;
    sched_count = profile->scheduler_order_count;
    if (sched_count == 0u) {
        sched_order_buf[0] = DOM_EXEC_SCHED_EXEC2_SINGLE_THREAD;
        sched_order_buf[1] = DOM_EXEC_SCHED_EXEC3_PARALLEL;
        sched_order = sched_order_buf;
        sched_count = 2u;
    }
    requested_sched = sched_order[0];
    out_policy->audit.scheduler_requested = requested_sched;

    for (i = 0u; i < sched_count; ++i) {
        u32 candidate = sched_order[i];
        if (candidate == DOM_EXEC_SCHED_EXEC3_PARALLEL) {
            if ((profile->allow_mask & DOM_EXEC_PROFILE_ALLOW_EXEC3) == 0u) {
                out_policy->audit.flags |= DOM_EXEC_AUDIT_FLAG_PROFILE_DENY_EXEC3;
                continue;
            }
            if (!law->allow_multithread) {
                out_policy->audit.flags |= DOM_EXEC_AUDIT_FLAG_LAW_DENY_EXEC3;
                continue;
            }
            if (profile->min_cores_for_exec3 > 0u) {
                if (caps->cpu.logical_cores < profile->min_cores_for_exec3) {
                    out_policy->audit.flags |= DOM_EXEC_AUDIT_FLAG_CAPS_DENY_EXEC3;
                    continue;
                }
            }
            selected_sched = candidate;
            found_sched = D_TRUE;
            break;
        }
        if (candidate == DOM_EXEC_SCHED_EXEC2_SINGLE_THREAD) {
            selected_sched = candidate;
            found_sched = D_TRUE;
            break;
        }
    }

    if (!found_sched) {
        selected_sched = DOM_EXEC_SCHED_EXEC2_SINGLE_THREAD;
        out_policy->audit.flags |= DOM_EXEC_AUDIT_FLAG_FALLBACK_SCHED;
    }
    if (selected_sched != requested_sched) {
        out_policy->audit.flags |= DOM_EXEC_AUDIT_FLAG_FALLBACK_SCHED;
    }

    out_policy->scheduler_backend = selected_sched;
    out_policy->audit.scheduler_selected = selected_sched;
    out_policy->ecs_backend = DOM_EXEC_ECS_SOA_DEFAULT;

    kernel_mask_profile = DOM_KERNEL_BACKEND_MASK_SCALAR;
    if ((profile->allow_mask & DOM_EXEC_PROFILE_ALLOW_SIMD) != 0u) {
        kernel_mask_profile |= DOM_KERNEL_BACKEND_MASK_SIMD;
    } else {
        out_policy->audit.flags |= DOM_EXEC_AUDIT_FLAG_PROFILE_DENY_SIMD;
    }
    if ((profile->allow_mask & DOM_EXEC_PROFILE_ALLOW_GPU_DERIVED) != 0u) {
        kernel_mask_profile |= DOM_KERNEL_BACKEND_MASK_GPU;
    } else {
        out_policy->audit.flags |= DOM_EXEC_AUDIT_FLAG_PROFILE_DENY_GPU;
    }

    kernel_mask_law = kernel_mask_profile;
    if (!law->allow_simd) {
        kernel_mask_law &= ~DOM_KERNEL_BACKEND_MASK_SIMD;
        out_policy->audit.flags |= DOM_EXEC_AUDIT_FLAG_LAW_DENY_SIMD;
    }
    if (!law->allow_gpu_derived) {
        kernel_mask_law &= ~DOM_KERNEL_BACKEND_MASK_GPU;
        out_policy->audit.flags |= DOM_EXEC_AUDIT_FLAG_LAW_DENY_GPU;
    }
    kernel_mask_law |= DOM_KERNEL_BACKEND_MASK_SCALAR;

    simd_available = dom_exec_caps_simd_available(caps);
    gpu_available = dom_exec_caps_gpu_available(caps);
    kernel_mask_caps = kernel_mask_law;
    if (!simd_available) {
        kernel_mask_caps &= ~DOM_KERNEL_BACKEND_MASK_SIMD;
        out_policy->audit.flags |= DOM_EXEC_AUDIT_FLAG_CAPS_DENY_SIMD;
    }
    if (!gpu_available) {
        kernel_mask_caps &= ~DOM_KERNEL_BACKEND_MASK_GPU;
        out_policy->audit.flags |= DOM_EXEC_AUDIT_FLAG_CAPS_DENY_GPU;
    }
    kernel_mask_caps |= DOM_KERNEL_BACKEND_MASK_SCALAR;

    kernel_mask_strict = kernel_mask_caps & ~DOM_KERNEL_BACKEND_MASK_GPU;
    kernel_mask_strict |= DOM_KERNEL_BACKEND_MASK_SCALAR;
    kernel_mask_derived = kernel_mask_caps | DOM_KERNEL_BACKEND_MASK_SCALAR;

    out_policy->kernel_mask_strict = kernel_mask_strict;
    out_policy->kernel_mask_derived = kernel_mask_derived;
    if (profile->kernel_order_count == 0u) {
        out_policy->kernel_order[0] = DOM_KERNEL_BACKEND_SCALAR;
        out_policy->kernel_order[1] = DOM_KERNEL_BACKEND_SIMD;
        out_policy->kernel_order[2] = DOM_KERNEL_BACKEND_GPU;
        out_policy->kernel_order_count = 3u;
    } else {
        out_policy->kernel_order_count = profile->kernel_order_count;
        for (i = 0u; i < out_policy->kernel_order_count; ++i) {
            out_policy->kernel_order[i] = profile->kernel_order[i];
        }
    }
    out_policy->render_allowlist_count = profile->render_allowlist_count;
    for (i = 0u; i < out_policy->render_allowlist_count; ++i) {
        memcpy(out_policy->render_allowlist[i],
               profile->render_allowlist[i],
               DOM_EXEC_POLICY_RENDER_NAME_MAX);
        out_policy->render_allowlist[i][DOM_EXEC_POLICY_RENDER_NAME_MAX - 1u] = '\0';
    }

    out_policy->audit.kernel_mask_profile = kernel_mask_profile;
    out_policy->audit.kernel_mask_law = kernel_mask_law;
    out_policy->audit.kernel_mask_caps = kernel_mask_caps;
    out_policy->audit.kernel_mask_final_strict = kernel_mask_strict;
    out_policy->audit.kernel_mask_final_derived = kernel_mask_derived;

    rc = dom_exec_budget_resolve(caps, &profile->budget_profile, &out_policy->budgets);
    if (rc != 0) {
        return -2;
    }

    out_policy->audit.audit_hash = 14695981039346656037ULL;
    out_policy->audit.audit_hash = dom_exec_policy_hash_u32(out_policy->audit.audit_hash, out_policy->audit.flags);
    out_policy->audit.audit_hash = dom_exec_policy_hash_u32(out_policy->audit.audit_hash, out_policy->audit.scheduler_selected);
    out_policy->audit.audit_hash = dom_exec_policy_hash_u32(out_policy->audit.audit_hash, out_policy->audit.kernel_mask_final_strict);
    out_policy->audit.audit_hash = dom_exec_policy_hash_u32(out_policy->audit.audit_hash, out_policy->audit.kernel_mask_final_derived);
    out_policy->audit.audit_hash = dom_exec_policy_hash_u32(out_policy->audit.audit_hash, out_policy->budgets.per_tick_cpu_budget_units_authoritative);
    out_policy->audit.audit_hash = dom_exec_policy_hash_u32(out_policy->audit.audit_hash, out_policy->budgets.per_tick_cpu_budget_units_derived);
    out_policy->audit.audit_hash = dom_exec_policy_hash_u32(out_policy->audit.audit_hash, out_policy->budgets.per_tick_io_budget_units_derived);
    out_policy->audit.audit_hash = dom_exec_policy_hash_u32(out_policy->audit.audit_hash, out_policy->budgets.per_tick_net_budget_units);
    out_policy->audit.audit_hash = dom_exec_policy_hash_u32(out_policy->audit.audit_hash, out_policy->budgets.memory_class);
    out_policy->audit.audit_hash = dom_exec_policy_hash_u64(out_policy->audit.audit_hash, out_policy->audit.syscaps_hash);

    snprintf(out_policy->audit.summary,
             DOM_EXEC_POLICY_AUDIT_SUMMARY_MAX,
             "sched=%s kernel_strict=0x%X kernel_derived=0x%X cpu_auth=%u cpu_der=%u io=%u net=%u flags=0x%X",
             dom_exec_scheduler_name(out_policy->scheduler_backend),
             out_policy->kernel_mask_strict,
             out_policy->kernel_mask_derived,
             out_policy->budgets.per_tick_cpu_budget_units_authoritative,
             out_policy->budgets.per_tick_cpu_budget_units_derived,
             out_policy->budgets.per_tick_io_budget_units_derived,
             out_policy->budgets.per_tick_net_budget_units,
             out_policy->audit.flags);

    return 0;
}
