/*
FILE: include/domino/execution/execution_policy.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / execution/execution_policy
RESPONSIBILITY: Defines deterministic execution policy inputs and outputs.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Selection is deterministic given identical inputs.
VERSIONING / ABI / DATA FORMAT NOTES: See schema/execution specs.
EXTENSION POINTS: Extend via public headers and relevant specs.
*/
#ifndef DOMINO_EXECUTION_EXECUTION_POLICY_H
#define DOMINO_EXECUTION_EXECUTION_POLICY_H

#include "domino/core/types.h"
#include "domino/execution/kernel_iface.h"
#include "domino/execution/budget_model.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_EXEC_PROFILE_ID_MAX 32u
#define DOM_EXEC_POLICY_MAX_ORDER 4u
#define DOM_EXEC_POLICY_RENDER_ALLOWLIST_MAX 8u
#define DOM_EXEC_POLICY_RENDER_NAME_MAX 32u
#define DOM_EXEC_POLICY_AUDIT_SUMMARY_MAX 256u

#define DOM_EXEC_TAG(a,b,c,d) \
    ((u32)(a) | ((u32)(b) << 8u) | ((u32)(c) << 16u) | ((u32)(d) << 24u))

#define DOM_EXEC_PROFILE_CHUNK DOM_EXEC_TAG('E','P','R','F')
#define DOM_EXEC_PROFILE_CHUNK_VERSION 1u

#define DOM_EXEC_TLV_PROFILE_ID DOM_EXEC_TAG('P','I','D','0')
#define DOM_EXEC_TLV_SCHED_ORDER DOM_EXEC_TAG('S','C','H','D')
#define DOM_EXEC_TLV_KERNEL_ORDER DOM_EXEC_TAG('K','O','R','D')
#define DOM_EXEC_TLV_ALLOW_MASK DOM_EXEC_TAG('A','L','O','W')
#define DOM_EXEC_TLV_MIN_CORES DOM_EXEC_TAG('M','I','N','C')
#define DOM_EXEC_TLV_BUDGET_ID DOM_EXEC_TAG('B','I','D','0')
#define DOM_EXEC_TLV_BUDGET_CPU_AUTH DOM_EXEC_TAG('B','C','A','U')
#define DOM_EXEC_TLV_BUDGET_CPU_DER DOM_EXEC_TAG('B','C','D','R')
#define DOM_EXEC_TLV_BUDGET_IO_DER DOM_EXEC_TAG('B','I','O','D')
#define DOM_EXEC_TLV_BUDGET_NET DOM_EXEC_TAG('B','N','E','T')
#define DOM_EXEC_TLV_MEM_CLASS DOM_EXEC_TAG('M','E','M','C')
#define DOM_EXEC_TLV_DEGRADATION_ID DOM_EXEC_TAG('D','E','G','R')
#define DOM_EXEC_TLV_CPU_SCALE_MIN DOM_EXEC_TAG('C','S','M','N')
#define DOM_EXEC_TLV_CPU_SCALE_MAX DOM_EXEC_TAG('C','S','M','X')
#define DOM_EXEC_TLV_IO_SCALE_MAX DOM_EXEC_TAG('I','O','S','X')
#define DOM_EXEC_TLV_NET_SCALE_MAX DOM_EXEC_TAG('N','S','M','X')
#define DOM_EXEC_TLV_RENDER_ALLOW DOM_EXEC_TAG('R','N','D','L')

typedef enum dom_exec_scheduler_backend {
    DOM_EXEC_SCHED_EXEC2_SINGLE_THREAD = 0u,
    DOM_EXEC_SCHED_EXEC3_PARALLEL = 1u
} dom_exec_scheduler_backend;

typedef enum dom_exec_ecs_backend {
    DOM_EXEC_ECS_SOA_DEFAULT = 0u
} dom_exec_ecs_backend;

enum {
    DOM_EXEC_PROFILE_ALLOW_EXEC3 = 1u << 0u,
    DOM_EXEC_PROFILE_ALLOW_SIMD = 1u << 1u,
    DOM_EXEC_PROFILE_ALLOW_GPU_DERIVED = 1u << 2u
};

enum {
    DOM_EXEC_AUDIT_FLAG_PROFILE_DENY_EXEC3 = 1u << 0u,
    DOM_EXEC_AUDIT_FLAG_LAW_DENY_EXEC3 = 1u << 1u,
    DOM_EXEC_AUDIT_FLAG_CAPS_DENY_EXEC3 = 1u << 2u,
    DOM_EXEC_AUDIT_FLAG_PROFILE_DENY_SIMD = 1u << 3u,
    DOM_EXEC_AUDIT_FLAG_LAW_DENY_SIMD = 1u << 4u,
    DOM_EXEC_AUDIT_FLAG_CAPS_DENY_SIMD = 1u << 5u,
    DOM_EXEC_AUDIT_FLAG_PROFILE_DENY_GPU = 1u << 6u,
    DOM_EXEC_AUDIT_FLAG_LAW_DENY_GPU = 1u << 7u,
    DOM_EXEC_AUDIT_FLAG_CAPS_DENY_GPU = 1u << 8u,
    DOM_EXEC_AUDIT_FLAG_FALLBACK_SCHED = 1u << 9u
};

typedef struct dom_exec_law_constraints {
    u32 allow_multithread;
    u32 allow_simd;
    u32 allow_gpu_derived;
    u32 allow_modified_clients;
    u32 allow_unauthenticated;
    u32 allow_debug_tools;
} dom_exec_law_constraints;

typedef struct dom_exec_profile_config {
    char profile_id[DOM_EXEC_PROFILE_ID_MAX];
    u32 scheduler_order[DOM_EXEC_POLICY_MAX_ORDER];
    u32 scheduler_order_count;
    u32 kernel_order[DOM_EXEC_POLICY_MAX_ORDER];
    u32 kernel_order_count;
    u32 allow_mask;
    u32 min_cores_for_exec3;
    dom_exec_budget_profile budget_profile;
    u32 render_allowlist_count;
    char render_allowlist[DOM_EXEC_POLICY_RENDER_ALLOWLIST_MAX][DOM_EXEC_POLICY_RENDER_NAME_MAX];
} dom_exec_profile_config;

typedef struct dom_exec_policy_audit {
    u32 flags;
    u32 scheduler_requested;
    u32 scheduler_selected;
    u32 kernel_mask_profile;
    u32 kernel_mask_law;
    u32 kernel_mask_caps;
    u32 kernel_mask_final_strict;
    u32 kernel_mask_final_derived;
    u64 syscaps_hash;
    u64 audit_hash;
    char summary[DOM_EXEC_POLICY_AUDIT_SUMMARY_MAX];
} dom_exec_policy_audit;

typedef struct dom_exec_policy {
    u32 scheduler_backend; /* dom_exec_scheduler_backend */
    u32 ecs_backend;       /* dom_exec_ecs_backend */
    u32 kernel_mask_strict;
    u32 kernel_mask_derived;
    u32 kernel_order[DOM_EXEC_POLICY_MAX_ORDER];
    u32 kernel_order_count;
    u32 render_allowlist_count;
    char render_allowlist[DOM_EXEC_POLICY_RENDER_ALLOWLIST_MAX][DOM_EXEC_POLICY_RENDER_NAME_MAX];
    dom_exec_budget_result budgets;
    dom_exec_policy_audit audit;
} dom_exec_policy;

typedef enum dom_exec_profile_load_result {
    DOM_EXEC_PROFILE_LOAD_OK = 0,
    DOM_EXEC_PROFILE_LOAD_ERR_IO = -1,
    DOM_EXEC_PROFILE_LOAD_ERR_FORMAT = -2,
    DOM_EXEC_PROFILE_LOAD_ERR_MISSING = -3
} dom_exec_profile_load_result;

void dom_exec_profile_init(dom_exec_profile_config* config);
void dom_exec_policy_init(dom_exec_policy* policy);
int dom_exec_profile_load_tlv(const char* path,
                              dom_exec_profile_config* out_config);
int dom_exec_policy_select(const dom_sys_caps_v1* caps,
                           const dom_exec_profile_config* profile,
                           const dom_exec_law_constraints* law,
                           dom_exec_policy* out_policy);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_EXECUTION_EXECUTION_POLICY_H */
