/*
FILE: source/dominium/game/runtime/dom_weather_provider.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/weather_provider
RESPONSIBILITY: Weather provider registry and modifier sampling (stub for v1).
*/
#include "runtime/dom_weather_provider.h"

#include <algorithm>
#include <cstring>
#include <string>
#include <vector>

#include "dominium/core_tlv.h"

namespace {

static const char kWeatherNoneId[] = "none";

struct DomWeatherProviderEntry {
    std::string id;
    dom_weather_provider_vtbl vtbl;
};

struct DomWeatherBindingEntry {
    dom_body_id body_id;
    std::string provider_id;
    std::vector<unsigned char> params;
    u64 params_hash;
};

static bool provider_entry_less(const DomWeatherProviderEntry &a,
                                const DomWeatherProviderEntry &b) {
    return a.id < b.id;
}

static bool binding_entry_less(const DomWeatherBindingEntry &a,
                               const DomWeatherBindingEntry &b) {
    if (a.body_id != b.body_id) {
        return a.body_id < b.body_id;
    }
    return a.provider_id < b.provider_id;
}

static void zero_mods(dom_weather_mods *mods) {
    if (!mods) {
        return;
    }
    mods->density_delta_q16 = 0;
    mods->pressure_delta_q16 = 0;
    mods->temperature_delta_q16 = 0;
    std::memset(&mods->wind_delta_q16, 0, sizeof(mods->wind_delta_q16));
    mods->has_wind = 0u;
}

static int weather_none_validate(dom_body_id body_id, const dom_weather_binding *binding) {
    (void)body_id;
    (void)binding;
    return DOM_WEATHER_OK;
}

static int weather_none_sample(dom_body_id body_id,
                               const dom_weather_binding *binding,
                               const dom_posseg_q16 *pos_body_fixed,
                               q48_16 altitude_m,
                               dom_tick tick,
                               dom_weather_mods *out_mods) {
    (void)body_id;
    (void)binding;
    (void)pos_body_fixed;
    (void)altitude_m;
    (void)tick;
    zero_mods(out_mods);
    return DOM_WEATHER_OK;
}

} // namespace

struct dom_weather_registry {
    std::vector<DomWeatherProviderEntry> providers;
    std::vector<DomWeatherBindingEntry> bindings;
};

dom_weather_registry *dom_weather_registry_create(void) {
    dom_weather_registry *registry = new dom_weather_registry();
    if (!registry) {
        return 0;
    }
    dom_weather_provider_vtbl vtbl;
    std::memset(&vtbl, 0, sizeof(vtbl));
    vtbl.api_version = 1u;
    vtbl.validate = weather_none_validate;
    vtbl.sample_modifiers = weather_none_sample;
    (void)dom_weather_registry_register_provider(registry, kWeatherNoneId, &vtbl);
    return registry;
}

void dom_weather_registry_destroy(dom_weather_registry *registry) {
    delete registry;
}

int dom_weather_registry_register_provider(dom_weather_registry *registry,
                                           const char *provider_id,
                                           const dom_weather_provider_vtbl *vtbl) {
    if (!registry || !provider_id || !provider_id[0] || !vtbl) {
        return DOM_WEATHER_INVALID_ARGUMENT;
    }
    if (std::strlen(provider_id) >= DOM_WEATHER_PROVIDER_ID_MAX) {
        return DOM_WEATHER_INVALID_ARGUMENT;
    }
    for (size_t i = 0u; i < registry->providers.size(); ++i) {
        if (registry->providers[i].id == provider_id) {
            return DOM_WEATHER_ERR;
        }
    }
    DomWeatherProviderEntry entry;
    entry.id = provider_id;
    entry.vtbl = *vtbl;
    registry->providers.push_back(entry);
    std::sort(registry->providers.begin(), registry->providers.end(), provider_entry_less);
    return DOM_WEATHER_OK;
}

int dom_weather_registry_set_binding(dom_weather_registry *registry,
                                     const dom_weather_binding *binding) {
    if (!registry || !binding || binding->body_id == 0ull) {
        return DOM_WEATHER_INVALID_ARGUMENT;
    }
    const char *provider_id = binding->provider_id;
    u32 provider_id_len = binding->provider_id_len;
    if (!provider_id || provider_id_len == 0u) {
        provider_id = kWeatherNoneId;
        provider_id_len = (u32)std::strlen(kWeatherNoneId);
    }
    if (provider_id_len >= DOM_WEATHER_PROVIDER_ID_MAX) {
        return DOM_WEATHER_INVALID_ARGUMENT;
    }

    const DomWeatherProviderEntry *provider = 0;
    for (size_t i = 0u; i < registry->providers.size(); ++i) {
        if (registry->providers[i].id == provider_id) {
            provider = &registry->providers[i];
            break;
        }
    }
    if (!provider) {
        return DOM_WEATHER_NOT_FOUND;
    }
    if (provider->vtbl.validate) {
        dom_weather_binding scratch = *binding;
        std::memset(scratch.provider_id, 0, sizeof(scratch.provider_id));
        std::memcpy(scratch.provider_id, provider_id, provider_id_len);
        scratch.provider_id_len = provider_id_len;
        if (provider->vtbl.validate(binding->body_id, &scratch) != DOM_WEATHER_OK) {
            return DOM_WEATHER_ERR;
        }
    }

    DomWeatherBindingEntry entry;
    entry.body_id = binding->body_id;
    entry.provider_id.assign(provider_id, provider_id_len);
    entry.params_hash = dom::core_tlv::tlv_fnv1a64(binding->params, binding->params_len);
    if (binding->params && binding->params_len > 0u) {
        entry.params.assign(binding->params, binding->params + binding->params_len);
    }

    for (size_t i = 0u; i < registry->bindings.size(); ++i) {
        if (registry->bindings[i].body_id == entry.body_id) {
            registry->bindings[i] = entry;
            std::sort(registry->bindings.begin(), registry->bindings.end(), binding_entry_less);
            return DOM_WEATHER_OK;
        }
    }

    registry->bindings.push_back(entry);
    std::sort(registry->bindings.begin(), registry->bindings.end(), binding_entry_less);
    return DOM_WEATHER_OK;
}

int dom_weather_registry_get_binding(const dom_weather_registry *registry,
                                     dom_body_id body_id,
                                     dom_weather_binding *out_binding) {
    if (!registry || !out_binding || body_id == 0ull) {
        return DOM_WEATHER_INVALID_ARGUMENT;
    }
    for (size_t i = 0u; i < registry->bindings.size(); ++i) {
        const DomWeatherBindingEntry &entry = registry->bindings[i];
        if (entry.body_id == body_id) {
            std::memset(out_binding, 0, sizeof(*out_binding));
            out_binding->body_id = entry.body_id;
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
            return DOM_WEATHER_OK;
        }
    }
    return DOM_WEATHER_NOT_FOUND;
}

int dom_weather_sample_modifiers(const dom_weather_registry *registry,
                                 dom_body_id body_id,
                                 const dom_posseg_q16 *pos_body_fixed,
                                 q48_16 altitude_m,
                                 dom_tick tick,
                                 dom_weather_mods *out_mods) {
    if (!registry || !out_mods || body_id == 0ull) {
        return DOM_WEATHER_INVALID_ARGUMENT;
    }
    dom_weather_binding binding;
    int rc = dom_weather_registry_get_binding(registry, body_id, &binding);
    if (rc != DOM_WEATHER_OK) {
        zero_mods(out_mods);
        return DOM_WEATHER_OK;
    }

    const DomWeatherProviderEntry *provider = 0;
    for (size_t i = 0u; i < registry->providers.size(); ++i) {
        if (registry->providers[i].id == binding.provider_id) {
            provider = &registry->providers[i];
            break;
        }
    }
    if (!provider || !provider->vtbl.sample_modifiers) {
        zero_mods(out_mods);
        return DOM_WEATHER_OK;
    }

    rc = provider->vtbl.sample_modifiers(body_id,
                                         &binding,
                                         pos_body_fixed,
                                         altitude_m,
                                         tick,
                                         out_mods);
    if (rc != DOM_WEATHER_OK) {
        zero_mods(out_mods);
        return rc;
    }
    return DOM_WEATHER_OK;
}
