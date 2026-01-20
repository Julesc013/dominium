/*
SysCaps tests (HWCAPS0).
*/
#include "domino/sys/sys_caps.h"

#include <stdio.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static int test_version_and_defaults(void)
{
    dom_sys_caps_v1 caps;
    dom_sys_caps_init(&caps);
    EXPECT(caps.version_major == DOM_SYS_CAPS_VERSION_MAJOR, "version major");
    EXPECT(caps.version_minor == DOM_SYS_CAPS_VERSION_MINOR, "version minor");
    EXPECT(caps.cpu.logical_cores == 0u, "default logical cores unknown");
    return 0;
}

static int test_override_injection(void)
{
    dom_sys_caps_v1 mock;
    dom_sys_caps_v1 out;

    dom_sys_caps_init(&mock);
    mock.cpu.logical_cores = 8u;
    mock.platform.os_family = DOM_SYS_CAPS_OS_WINDOWS;

    dom_sys_caps_set_override(&mock);
    dom_sys_caps_collect(&out);
    dom_sys_caps_clear_override();

    EXPECT(out.cpu.logical_cores == 8u, "override logical cores");
    EXPECT(out.platform.os_family == DOM_SYS_CAPS_OS_WINDOWS, "override os");
    return 0;
}

static int test_hash_determinism(void)
{
    dom_sys_caps_v1 caps_a;
    dom_sys_caps_v1 caps_b;
    u64 hash_a1;
    u64 hash_a2;
    u64 hash_b;

    dom_sys_caps_init(&caps_a);
    caps_a.cpu.logical_cores = 4u;
    caps_a.cpu.simd_caps.sse2 = DOM_SYS_CAPS_BOOL_TRUE;
    caps_a.storage.storage_class = DOM_SYS_CAPS_STORAGE_SSD;

    hash_a1 = dom_sys_caps_hash64(&caps_a);
    hash_a2 = dom_sys_caps_hash64(&caps_a);
    EXPECT(hash_a1 == hash_a2, "hash deterministic");

    caps_b = caps_a;
    caps_b.cpu.logical_cores = 5u;
    hash_b = dom_sys_caps_hash64(&caps_b);
    EXPECT(hash_a1 != hash_b, "hash changes on field change");
    return 0;
}

int main(void)
{
    if (test_version_and_defaults() != 0) return 1;
    if (test_override_injection() != 0) return 1;
    if (test_hash_determinism() != 0) return 1;
    return 0;
}
