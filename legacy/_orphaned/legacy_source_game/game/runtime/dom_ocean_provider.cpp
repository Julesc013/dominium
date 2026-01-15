/*
FILE: source/dominium/game/runtime/dom_ocean_provider.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/ocean_provider
RESPONSIBILITY: Ocean provider stub registration (v1).
*/
#include "runtime/dom_ocean_provider.h"

#include <cstring>

namespace {

static int ocean_validate(dom_body_id body_id, const dom_media_binding *binding) {
    (void)body_id;
    (void)binding;
    return DOM_MEDIA_OK;
}

static int ocean_sample(dom_body_id body_id,
                        const dom_media_binding *binding,
                        const dom_posseg_q16 *pos_body_fixed,
                        q48_16 altitude_m,
                        dom_tick tick,
                        dom_media_sample *out_sample) {
    (void)body_id;
    (void)binding;
    (void)pos_body_fixed;
    (void)altitude_m;
    (void)tick;
    (void)out_sample;
    return DOM_MEDIA_NOT_IMPLEMENTED;
}

} // namespace

int dom_ocean_register_stub(dom_media_registry *registry) {
    dom_media_provider_vtbl vtbl;
    if (!registry) {
        return DOM_OCEAN_INVALID_ARGUMENT;
    }
    std::memset(&vtbl, 0, sizeof(vtbl));
    vtbl.api_version = 1u;
    vtbl.validate = ocean_validate;
    vtbl.sample = ocean_sample;
    return dom_media_registry_register_provider(registry,
                                                DOM_MEDIA_KIND_OCEAN,
                                                "stub",
                                                &vtbl);
}
