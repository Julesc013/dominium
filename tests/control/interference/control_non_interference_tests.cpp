/*
Control enabled non-interference tests (TESTX2).
*/
#include "domino/control.h"
#include "tests/control/control_test_common.h"

#include <stdio.h>

#ifndef DOMINIUM_CONTROL_REGISTRY_PATH
#define DOMINIUM_CONTROL_REGISTRY_PATH "data/registries/control_capabilities.registry"
#endif

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

int main(void)
{
    dom_control_caps caps;
    const dom_registry* reg;
    u64 baseline = 0u;
    u64 hash = 0u;
    u32 i;
    u32 prev_id = 0u;

    print_version_banner();
    EXPECT(dom_control_caps_init(&caps, DOMINIUM_CONTROL_REGISTRY_PATH) == DOM_CONTROL_OK,
           "control registry init");

    EXPECT(mp0_run_hash(&baseline) != 0, "mp0 baseline hash");
    reg = dom_control_caps_registry(&caps);
    EXPECT(reg != 0, "control registry missing");

    for (i = 0u; i < reg->count; ++i) {
        const dom_registry_entry* entry = &reg->entries[i];
        if (prev_id) {
            (void)dom_control_caps_disable_id(&caps, prev_id);
        }
        EXPECT(dom_control_caps_enable_id(&caps, entry->id) == DOM_CONTROL_OK,
               "enable control capability");
        EXPECT(dom_control_caps_require(&caps, entry->id, "non_interference") == DOM_CONTROL_OK,
               "require enabled capability");
        EXPECT(mp0_run_hash(&hash) != 0, "mp0 hash with control enabled");
        EXPECT(hash == baseline, "control capability altered authoritative hash");
        prev_id = entry->id;
    }

    dom_control_caps_free(&caps);
    return 0;
}
