/*
FILE: engine/modules/execution/kernels/simd/simd_caps.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels/simd
RESPONSIBILITY: Runtime SIMD capability detection.
ALLOWED DEPENDENCIES: engine/include public headers, C++98 headers, and platform headers as needed.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Detection only; does not affect simulation truth.
*/
#include "execution/kernels/simd/simd_caps.h"

#if defined(_MSC_VER) && (defined(_M_IX86) || defined(_M_X64))
#include <intrin.h>
#endif

#if defined(__linux__) && (defined(__aarch64__) || defined(__arm__))
#include <sys/auxv.h>
#include <asm/hwcap.h>
#endif

static u32 dom_simd_detect_x86_caps(void)
{
    u32 mask = 0u;

#if defined(_MSC_VER) && (defined(_M_IX86) || defined(_M_X64))
    int regs[4];
    __cpuidex(regs, 1, 0);
    if (regs[3] & (1 << 26)) {
        mask |= DOM_SIMD_CAP_SSE2;
    }
    if (regs[2] & (1 << 19)) {
        mask |= DOM_SIMD_CAP_SSE41;
    }
    {
        int osxsave = (regs[2] & (1 << 27)) != 0;
        int avx = (regs[2] & (1 << 28)) != 0;
        if (osxsave && avx) {
            u64 xcr0 = _xgetbv(0);
            if ((xcr0 & 0x6u) == 0x6u) {
                __cpuidex(regs, 7, 0);
                if (regs[1] & (1 << 5)) {
                    mask |= DOM_SIMD_CAP_AVX2;
                }
                if ((regs[1] & (1 << 16)) && (xcr0 & 0xE6u) == 0xE6u) {
                    mask |= DOM_SIMD_CAP_AVX512;
                }
            }
        }
    }
#elif (defined(__GNUC__) || defined(__clang__)) && (defined(__i386__) || defined(__x86_64__))
    if (__builtin_cpu_supports("sse2")) {
        mask |= DOM_SIMD_CAP_SSE2;
    }
    if (__builtin_cpu_supports("sse4.1")) {
        mask |= DOM_SIMD_CAP_SSE41;
    }
    if (__builtin_cpu_supports("avx2")) {
        mask |= DOM_SIMD_CAP_AVX2;
    }
    if (__builtin_cpu_supports("avx512f")) {
        mask |= DOM_SIMD_CAP_AVX512;
    }
#endif

    return mask;
}

static u32 dom_simd_detect_arm_caps(void)
{
    u32 mask = 0u;

#if defined(__linux__) && (defined(__aarch64__) || defined(__arm__))
    {
        unsigned long caps = getauxval(AT_HWCAP);
#if defined(__aarch64__)
#if defined(HWCAP_ASIMD)
        if (caps & HWCAP_ASIMD) {
            mask |= DOM_SIMD_CAP_NEON;
        }
#endif
#else
#if defined(HWCAP_NEON)
        if (caps & HWCAP_NEON) {
            mask |= DOM_SIMD_CAP_NEON;
        }
#endif
#endif
    }
#elif defined(__ARM_NEON) || defined(__ARM_NEON__) || defined(__aarch64__)
    mask |= DOM_SIMD_CAP_NEON;
#endif

    return mask;
}

void dom_simd_detect_caps(dom_simd_caps* out_caps)
{
    u32 mask = 0u;
    if (!out_caps) {
        return;
    }
    mask |= dom_simd_detect_x86_caps();
    mask |= dom_simd_detect_arm_caps();
    out_caps->mask = mask;
}

d_bool dom_simd_caps_has(const dom_simd_caps* caps, u32 required_mask)
{
    if (!caps) {
        return D_FALSE;
    }
    if (required_mask == 0u) {
        return D_TRUE;
    }
    return ((caps->mask & required_mask) == required_mask) ? D_TRUE : D_FALSE;
}

u32 dom_simd_backend_mask_from_caps(const dom_simd_caps* caps)
{
    u32 mask = DOM_KERNEL_BACKEND_MASK_SCALAR;
    if (caps && (caps->mask & DOM_SIMD_CAP_ANY)) {
        mask |= DOM_KERNEL_BACKEND_MASK_SIMD;
    }
    return mask;
}
