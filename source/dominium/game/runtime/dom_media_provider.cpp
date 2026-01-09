/*
FILE: source/dominium/game/runtime/dom_media_provider.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/media_provider
RESPONSIBILITY: Media provider registry, bindings, and sampling helpers.
*/
#include "runtime/dom_media_provider.h"

#include <algorithm>
#include <cstring>
#include <string>
#include <vector>

#include "dominium/core_tlv.h"

namespace {

static const char kVacuumProviderId[] = "vacuum";

struct DomMediaProviderEntry {
    u32 kind;
    std::string id;
    dom_media_provider_vtbl vtbl;
};

struct DomMediaBindingEntry {
    dom_body_id body_id;
    u32 kind;
    std::string provider_id;
    std::vector<unsigned char> params;
    u64 params_hash;
};

static bool provider_entry_less(const DomMediaProviderEntry &a,
                                const DomMediaProviderEntry &b) {
    if (a.kind != b.kind) {
        return a.kind < b.kind;
    }
    return a.id < b.id;
}

static bool binding_entry_less(const DomMediaBindingEntry &a,
                               const DomMediaBindingEntry &b) {
    if (a.body_id != b.body_id) {
        return a.body_id < b.body_id;
    }
    if (a.kind != b.kind) {
        return a.kind < b.kind;
    }
    return a.provider_id < b.provider_id;
}

static bool kind_valid(u32 kind) {
    return kind == DOM_MEDIA_KIND_VACUUM ||
           kind == DOM_MEDIA_KIND_ATMOSPHERE ||
           kind == DOM_MEDIA_KIND_OCEAN;
}

static void zero_sample(dom_media_sample *out_sample) {
    if (!out_sample) {
        return;
    }
    out_sample->density_q16 = 0;
    out_sample->pressure_q16 = 0;
    out_sample->temperature_q16 = 0;
    std::memset(&out_sample->wind_body_q16, 0, sizeof(out_sample->wind_body_q16));
    out_sample->has_wind = 0u;
}

} // namespace

struct dom_media_registry {
    std::vector<DomMediaProviderEntry> providers;
    std::vector<DomMediaBindingEntry> bindings;
};

dom_media_registry *dom_media_registry_create(void) {
    return new dom_media_registry();
}

void dom_media_registry_destroy(dom_media_registry *registry) {
    delete registry;
}

int dom_media_registry_register_provider(dom_media_registry *registry,
                                         u32 kind,
                                         const char *provider_id,
                                         const dom_media_provider_vtbl *vtbl) {
    if (!registry || !provider_id || !provider_id[0] || !vtbl) {
        return DOM_MEDIA_INVALID_ARGUMENT;
    }
    if (!kind_valid(kind)) {
        return DOM_MEDIA_INVALID_ARGUMENT;
    }
    if (std::strlen(provider_id) >= DOM_MEDIA_PROVIDER_ID_MAX) {
        return DOM_MEDIA_INVALID_ARGUMENT;
    }
    for (size_t i = 0u; i < registry->providers.size(); ++i) {
        if (registry->providers[i].kind == kind &&
            registry->providers[i].id == provider_id) {
            return DOM_MEDIA_ERR;
        }
    }
    DomMediaProviderEntry entry;
    entry.kind = kind;
    entry.id = provider_id;
    entry.vtbl = *vtbl;
    registry->providers.push_back(entry);
    std::sort(registry->providers.begin(), registry->providers.end(), provider_entry_less);
    return DOM_MEDIA_OK;
}

int dom_media_registry_set_binding(dom_media_registry *registry,
                                   const dom_media_binding *binding) {
    if (!registry || !binding || binding->body_id == 0ull) {
        return DOM_MEDIA_INVALID_ARGUMENT;
    }
    if (!kind_valid(binding->kind)) {
        return DOM_MEDIA_INVALID_ARGUMENT;
    }

    const char *provider_id = binding->provider_id;
    u32 provider_id_len = binding->provider_id_len;
    if (binding->kind == DOM_MEDIA_KIND_VACUUM &&
        (!provider_id || provider_id_len == 0u)) {
        provider_id = kVacuumProviderId;
        provider_id_len = (u32)std::strlen(kVacuumProviderId);
    }
    if (!provider_id || provider_id_len == 0u) {
        return DOM_MEDIA_INVALID_ARGUMENT;
    }
    if (provider_id_len >= DOM_MEDIA_PROVIDER_ID_MAX) {
        return DOM_MEDIA_INVALID_ARGUMENT;
    }

    const DomMediaProviderEntry *provider = 0;
    if (binding->kind != DOM_MEDIA_KIND_VACUUM) {
        for (size_t i = 0u; i < registry->providers.size(); ++i) {
            if (registry->providers[i].kind == binding->kind &&
                registry->providers[i].id == provider_id) {
                provider = &registry->providers[i];
                break;
            }
        }
        if (!provider) {
            return DOM_MEDIA_NOT_FOUND;
        }
        if (provider->vtbl.validate) {
            dom_media_binding scratch = *binding;
            std::memset(scratch.provider_id, 0, sizeof(scratch.provider_id));
            std::memcpy(scratch.provider_id, provider_id, provider_id_len);
            scratch.provider_id_len = provider_id_len;
            if (provider->vtbl.validate(binding->body_id, &scratch) != DOM_MEDIA_OK) {
                return DOM_MEDIA_INVALID_DATA;
            }
        }
    }

    DomMediaBindingEntry entry;
    entry.body_id = binding->body_id;
    entry.kind = binding->kind;
    entry.provider_id.assign(provider_id, provider_id_len);
    entry.params_hash = dom::core_tlv::tlv_fnv1a64(binding->params, binding->params_len);
    if (binding->params && binding->params_len > 0u) {
        entry.params.assign(binding->params, binding->params + binding->params_len);
    }

    for (size_t i = 0u; i < registry->bindings.size(); ++i) {
        if (registry->bindings[i].body_id == entry.body_id &&
            registry->bindings[i].kind == entry.kind) {
            registry->bindings[i] = entry;
            std::sort(registry->bindings.begin(), registry->bindings.end(), binding_entry_less);
            return DOM_MEDIA_OK;
        }
    }

    registry->bindings.push_back(entry);
    std::sort(registry->bindings.begin(), registry->bindings.end(), binding_entry_less);
    return DOM_MEDIA_OK;
}

int dom_media_registry_get_binding(const dom_media_registry *registry,
                                   dom_body_id body_id,
                                   u32 kind,
                                   dom_media_binding *out_binding) {
    if (!registry || !out_binding || body_id == 0ull) {
        return DOM_MEDIA_INVALID_ARGUMENT;
    }
    for (size_t i = 0u; i < registry->bindings.size(); ++i) {
        const DomMediaBindingEntry &entry = registry->bindings[i];
        if (entry.body_id == body_id && entry.kind == kind) {
            std::memset(out_binding, 0, sizeof(*out_binding));
            out_binding->body_id = entry.body_id;
            out_binding->kind = entry.kind;
            if (!entry.provider_id.empty()) {
                const size_t len = entry.provider_id.size();
                const size_t cap = sizeof(out_binding->provider_id);
                const size_t copy_len = (len < cap) ? len : (cap - 1u);
                std::memcpy(out_binding->provider_id, entry.provider_id.data(), copy_len);
                out_binding->provider_id_len = (u32)copy_len;
            }
            out_binding->params = entry.params.empty() ? 0 : &entry.params[0];
            out_binding->params_len = (u32)entry.params.size();
            out_binding->params_hash = entry.params_hash;
            return DOM_MEDIA_OK;
        }
    }
    return DOM_MEDIA_NOT_FOUND;
}

int dom_media_sample(const dom_media_registry *registry,
                     dom_body_id body_id,
                     u32 kind,
                     const dom_posseg_q16 *pos_body_fixed,
                     q48_16 altitude_m,
                     dom_tick tick,
                     dom_media_sample *out_sample) {
    if (!registry || !out_sample || body_id == 0ull) {
        return DOM_MEDIA_INVALID_ARGUMENT;
    }
    if (!kind_valid(kind)) {
        return DOM_MEDIA_INVALID_ARGUMENT;
    }
    if (kind == DOM_MEDIA_KIND_VACUUM) {
        zero_sample(out_sample);
        return DOM_MEDIA_OK;
    }

    dom_media_binding binding;
    int rc = dom_media_registry_get_binding(registry, body_id, kind, &binding);
    if (rc != DOM_MEDIA_OK) {
        return rc;
    }

    const DomMediaProviderEntry *provider = 0;
    for (size_t i = 0u; i < registry->providers.size(); ++i) {
        if (registry->providers[i].kind == kind &&
            registry->providers[i].id == binding.provider_id) {
            provider = &registry->providers[i];
            break;
        }
    }
    if (!provider || !provider->vtbl.sample) {
        return DOM_MEDIA_NOT_FOUND;
    }

    return provider->vtbl.sample(body_id, &binding, pos_body_fixed, altitude_m, tick, out_sample);
}
