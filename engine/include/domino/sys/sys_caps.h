/*
FILE: include/domino/sys/sys_caps.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / sys/sys_caps
RESPONSIBILITY: Defines the public SysCaps descriptor and collection APIs.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: SysCaps are inputs to policy only; no wall-clock or benchmarking.
VERSIONING / ABI / DATA FORMAT NOTES: Versioned via version_major/minor.
EXTENSION POINTS: Extend via public headers and relevant schema docs.
*/
#ifndef DOMINO_SYS_SYSCAPS_H
#define DOMINO_SYS_SYSCAPS_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_SYS_CAPS_VERSION_MAJOR 1u
#define DOM_SYS_CAPS_VERSION_MINOR 0u

typedef enum dom_sys_caps_bool {
    DOM_SYS_CAPS_BOOL_UNKNOWN = 0,
    DOM_SYS_CAPS_BOOL_FALSE = 1,
    DOM_SYS_CAPS_BOOL_TRUE = 2
} dom_sys_caps_bool;

typedef enum dom_sys_caps_core_class {
    DOM_SYS_CAPS_CORE_UNKNOWN = 0,
    DOM_SYS_CAPS_CORE_HOMOGENEOUS = 1,
    DOM_SYS_CAPS_CORE_HETEROGENEOUS = 2
} dom_sys_caps_core_class;

typedef enum dom_sys_caps_cache_l3_class {
    DOM_SYS_CAPS_L3_UNKNOWN = 0,
    DOM_SYS_CAPS_L3_TINY = 1,
    DOM_SYS_CAPS_L3_SMALL = 2,
    DOM_SYS_CAPS_L3_MEDIUM = 3,
    DOM_SYS_CAPS_L3_LARGE = 4,
    DOM_SYS_CAPS_L3_HUGE = 5
} dom_sys_caps_cache_l3_class;

typedef enum dom_sys_caps_gpu_mem_model {
    DOM_SYS_CAPS_GPU_MEM_UNKNOWN = 0,
    DOM_SYS_CAPS_GPU_MEM_UNIFIED = 1,
    DOM_SYS_CAPS_GPU_MEM_DISCRETE = 2
} dom_sys_caps_gpu_mem_model;

typedef enum dom_sys_caps_gpu_class {
    DOM_SYS_CAPS_GPU_UNKNOWN = 0,
    DOM_SYS_CAPS_GPU_NONE = 1,
    DOM_SYS_CAPS_GPU_LOW = 2,
    DOM_SYS_CAPS_GPU_MID = 3,
    DOM_SYS_CAPS_GPU_HIGH = 4
} dom_sys_caps_gpu_class;

typedef enum dom_sys_caps_storage_class {
    DOM_SYS_CAPS_STORAGE_UNKNOWN = 0,
    DOM_SYS_CAPS_STORAGE_HDD = 1,
    DOM_SYS_CAPS_STORAGE_SSD = 2,
    DOM_SYS_CAPS_STORAGE_NVME = 3
} dom_sys_caps_storage_class;

typedef enum dom_sys_caps_net_class {
    DOM_SYS_CAPS_NET_UNKNOWN = 0,
    DOM_SYS_CAPS_NET_OFFLINE = 1,
    DOM_SYS_CAPS_NET_LAN = 2,
    DOM_SYS_CAPS_NET_WAN = 3
} dom_sys_caps_net_class;

typedef enum dom_sys_caps_os_family {
    DOM_SYS_CAPS_OS_UNKNOWN = 0,
    DOM_SYS_CAPS_OS_WINDOWS = 1,
    DOM_SYS_CAPS_OS_LINUX = 2,
    DOM_SYS_CAPS_OS_MACOS = 3
} dom_sys_caps_os_family;

typedef enum dom_sys_caps_arch_family {
    DOM_SYS_CAPS_ARCH_UNKNOWN = 0,
    DOM_SYS_CAPS_ARCH_X86 = 1,
    DOM_SYS_CAPS_ARCH_X64 = 2,
    DOM_SYS_CAPS_ARCH_ARM64 = 3
} dom_sys_caps_arch_family;

typedef struct dom_sys_caps_simd {
    u8 sse2;
    u8 sse4;
    u8 avx2;
    u8 avx512;
    u8 neon;
    u8 sve;
} dom_sys_caps_simd;

typedef struct dom_sys_caps_cpu {
    u32 logical_cores;
    u32 physical_cores_estimate;
    u8  smt_present;    /* dom_sys_caps_bool */
    u8  core_classes;   /* dom_sys_caps_core_class */
    u16 reserved0;
    u32 perf_cores_estimate;
    u32 eff_cores_estimate;
    u32 numa_nodes_estimate; /* 0 = unknown */
    struct {
        u8 l3_size_class;  /* dom_sys_caps_cache_l3_class */
        u8 vcache_present; /* dom_sys_caps_bool */
        u16 reserved1;
    } cache_class;
    dom_sys_caps_simd simd_caps;
} dom_sys_caps_cpu;

typedef struct dom_sys_caps_gpu {
    u8 has_gpu;            /* 0/1 */
    u8 gpu_memory_model;   /* dom_sys_caps_gpu_mem_model */
    u8 has_compute_queue;  /* dom_sys_caps_bool */
    u8 gpu_class;          /* dom_sys_caps_gpu_class */
} dom_sys_caps_gpu;

typedef struct dom_sys_caps_storage {
    u8 storage_class;            /* dom_sys_caps_storage_class */
    u8 direct_storage_available; /* dom_sys_caps_bool */
    u16 reserved;
} dom_sys_caps_storage;

typedef struct dom_sys_caps_network {
    u8 net_class; /* dom_sys_caps_net_class */
    u8 reserved[3];
} dom_sys_caps_network;

typedef struct dom_sys_caps_platform {
    u8 os_family;   /* dom_sys_caps_os_family */
    u8 arch_family; /* dom_sys_caps_arch_family */
    u16 reserved;
} dom_sys_caps_platform;

typedef struct dom_sys_caps_v1 {
    u32 version_major;
    u32 version_minor;
    dom_sys_caps_cpu cpu;
    dom_sys_caps_gpu gpu;
    dom_sys_caps_storage storage;
    dom_sys_caps_network network;
    dom_sys_caps_platform platform;
} dom_sys_caps_v1;

void dom_sys_caps_init(dom_sys_caps_v1* caps);
void dom_sys_caps_collect(dom_sys_caps_v1* out_caps);
void dom_sys_caps_set_override(const dom_sys_caps_v1* caps);
void dom_sys_caps_clear_override(void);
u64 dom_sys_caps_hash64(const dom_sys_caps_v1* caps);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_SYS_SYSCAPS_H */
