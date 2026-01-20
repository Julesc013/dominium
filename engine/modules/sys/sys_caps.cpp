/*
FILE: engine/modules/sys/sys_caps.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / sys/sys_caps
RESPONSIBILITY: Conservative SysCaps collection and hashing.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside sys.
DETERMINISM: No wall-clock or benchmarking; deterministic hashing only.
*/
#include "domino/sys/sys_caps.h"

#include <string.h>

#if defined(_WIN32)
#include <windows.h>
#else
#include <unistd.h>
#endif

static d_bool g_override_set = D_FALSE;
static dom_sys_caps_v1 g_override_caps;

static u32 dom_sys_caps_detect_logical_cores(void)
{
#if defined(_WIN32)
    SYSTEM_INFO info;
    ZeroMemory(&info, sizeof(info));
    GetNativeSystemInfo(&info);
    if (info.dwNumberOfProcessors > 0u) {
        return (u32)info.dwNumberOfProcessors;
    }
#elif defined(_SC_NPROCESSORS_ONLN)
    long cores = sysconf(_SC_NPROCESSORS_ONLN);
    if (cores > 0) {
        return (u32)cores;
    }
#endif
    return 0u;
}

void dom_sys_caps_init(dom_sys_caps_v1* caps)
{
    if (!caps) {
        return;
    }
    memset(caps, 0, sizeof(*caps));
    caps->version_major = DOM_SYS_CAPS_VERSION_MAJOR;
    caps->version_minor = DOM_SYS_CAPS_VERSION_MINOR;
    caps->gpu.gpu_class = DOM_SYS_CAPS_GPU_NONE;
}

void dom_sys_caps_collect(dom_sys_caps_v1* out_caps)
{
    if (!out_caps) {
        return;
    }
    if (g_override_set) {
        *out_caps = g_override_caps;
        return;
    }

    dom_sys_caps_init(out_caps);

    out_caps->cpu.logical_cores = dom_sys_caps_detect_logical_cores();

#if defined(_WIN32)
    out_caps->platform.os_family = DOM_SYS_CAPS_OS_WINDOWS;
#elif defined(__APPLE__)
    out_caps->platform.os_family = DOM_SYS_CAPS_OS_MACOS;
#elif defined(__linux__)
    out_caps->platform.os_family = DOM_SYS_CAPS_OS_LINUX;
#else
    out_caps->platform.os_family = DOM_SYS_CAPS_OS_UNKNOWN;
#endif

#if defined(_M_X64) || defined(__x86_64__) || defined(__amd64__)
    out_caps->platform.arch_family = DOM_SYS_CAPS_ARCH_X64;
#elif defined(_M_IX86) || defined(__i386__)
    out_caps->platform.arch_family = DOM_SYS_CAPS_ARCH_X86;
#elif defined(_M_ARM64) || defined(__aarch64__)
    out_caps->platform.arch_family = DOM_SYS_CAPS_ARCH_ARM64;
#else
    out_caps->platform.arch_family = DOM_SYS_CAPS_ARCH_UNKNOWN;
#endif

#if defined(__SSE2__) || defined(_M_X64)
    out_caps->cpu.simd_caps.sse2 = DOM_SYS_CAPS_BOOL_TRUE;
#endif
#if defined(__SSE4_1__) || defined(__SSE4_2__)
    out_caps->cpu.simd_caps.sse4 = DOM_SYS_CAPS_BOOL_TRUE;
#endif
#if defined(__AVX2__)
    out_caps->cpu.simd_caps.avx2 = DOM_SYS_CAPS_BOOL_TRUE;
#endif
#if defined(__AVX512F__)
    out_caps->cpu.simd_caps.avx512 = DOM_SYS_CAPS_BOOL_TRUE;
#endif
#if defined(__ARM_NEON) || defined(__ARM_NEON__)
    out_caps->cpu.simd_caps.neon = DOM_SYS_CAPS_BOOL_TRUE;
#endif
#if defined(__ARM_FEATURE_SVE)
    out_caps->cpu.simd_caps.sve = DOM_SYS_CAPS_BOOL_TRUE;
#endif
}

void dom_sys_caps_set_override(const dom_sys_caps_v1* caps)
{
    if (!caps) {
        return;
    }
    g_override_caps = *caps;
    g_override_set = D_TRUE;
}

void dom_sys_caps_clear_override(void)
{
    g_override_set = D_FALSE;
}

static u64 dom_sys_caps_hash_u8(u64 h, u8 v)
{
    h ^= (u64)v;
    h *= 1099511628211ULL;
    return h;
}

static u64 dom_sys_caps_hash_u32(u64 h, u32 v)
{
    h = dom_sys_caps_hash_u8(h, (u8)(v & 0xFFu));
    h = dom_sys_caps_hash_u8(h, (u8)((v >> 8u) & 0xFFu));
    h = dom_sys_caps_hash_u8(h, (u8)((v >> 16u) & 0xFFu));
    h = dom_sys_caps_hash_u8(h, (u8)((v >> 24u) & 0xFFu));
    return h;
}

u64 dom_sys_caps_hash64(const dom_sys_caps_v1* caps)
{
    u64 h = 14695981039346656037ULL;
    if (!caps) {
        return h;
    }

    h = dom_sys_caps_hash_u32(h, caps->version_major);
    h = dom_sys_caps_hash_u32(h, caps->version_minor);

    h = dom_sys_caps_hash_u32(h, caps->cpu.logical_cores);
    h = dom_sys_caps_hash_u32(h, caps->cpu.physical_cores_estimate);
    h = dom_sys_caps_hash_u8(h, caps->cpu.smt_present);
    h = dom_sys_caps_hash_u8(h, caps->cpu.core_classes);
    h = dom_sys_caps_hash_u32(h, caps->cpu.perf_cores_estimate);
    h = dom_sys_caps_hash_u32(h, caps->cpu.eff_cores_estimate);
    h = dom_sys_caps_hash_u32(h, caps->cpu.numa_nodes_estimate);
    h = dom_sys_caps_hash_u8(h, caps->cpu.cache_class.l3_size_class);
    h = dom_sys_caps_hash_u8(h, caps->cpu.cache_class.vcache_present);
    h = dom_sys_caps_hash_u8(h, caps->cpu.simd_caps.sse2);
    h = dom_sys_caps_hash_u8(h, caps->cpu.simd_caps.sse4);
    h = dom_sys_caps_hash_u8(h, caps->cpu.simd_caps.avx2);
    h = dom_sys_caps_hash_u8(h, caps->cpu.simd_caps.avx512);
    h = dom_sys_caps_hash_u8(h, caps->cpu.simd_caps.neon);
    h = dom_sys_caps_hash_u8(h, caps->cpu.simd_caps.sve);

    h = dom_sys_caps_hash_u8(h, caps->gpu.has_gpu);
    h = dom_sys_caps_hash_u8(h, caps->gpu.gpu_memory_model);
    h = dom_sys_caps_hash_u8(h, caps->gpu.has_compute_queue);
    h = dom_sys_caps_hash_u8(h, caps->gpu.gpu_class);

    h = dom_sys_caps_hash_u8(h, caps->storage.storage_class);
    h = dom_sys_caps_hash_u8(h, caps->storage.direct_storage_available);

    h = dom_sys_caps_hash_u8(h, caps->network.net_class);

    h = dom_sys_caps_hash_u8(h, caps->platform.os_family);
    h = dom_sys_caps_hash_u8(h, caps->platform.arch_family);

    return h;
}
