/*
FILE: source/dominium/providers/provider_registry.c
MODULE: Dominium
PURPOSE: Built-in provider registry for solver integration.
*/
#include "dominium/provider_registry.h"

#include <string.h>

#define CAP_BOOL(KEY, VAL) { (u32)(KEY), (u8)CORE_CAP_BOOL, 0u, 0u, { (u32)(VAL) } }

static const core_cap_entry g_caps_content_null[] = {
    CAP_BOOL(CORE_CAP_KEY_SUPPORTS_NETWORK, 0u),
    CAP_BOOL(CORE_CAP_KEY_SUPPORTS_OFFLINE, 1u)
};

static const core_cap_entry g_caps_content_local_fs[] = {
    CAP_BOOL(CORE_CAP_KEY_SUPPORTS_NETWORK, 0u),
    CAP_BOOL(CORE_CAP_KEY_SUPPORTS_OFFLINE, 1u)
};

static const core_cap_entry g_caps_net_null[] = {
    CAP_BOOL(CORE_CAP_KEY_SUPPORTS_NETWORK, 0u),
    CAP_BOOL(CORE_CAP_KEY_SUPPORTS_OFFLINE, 1u),
    CAP_BOOL(CORE_CAP_KEY_SUPPORTS_TLS, 0u)
};

static const core_cap_entry g_caps_trust_null[] = {
    CAP_BOOL(CORE_CAP_KEY_SUPPORTS_TRUST, 0u)
};

static const core_cap_entry g_caps_keychain_null[] = {
    CAP_BOOL(CORE_CAP_KEY_SUPPORTS_KEYCHAIN, 0u)
};

static const core_cap_entry g_caps_os_null[] = {
    CAP_BOOL(CORE_CAP_KEY_SUPPORTS_OPEN_FOLDER, 0u),
    CAP_BOOL(CORE_CAP_KEY_SUPPORTS_FILE_PICKER, 0u)
};

static provider_registry_entry g_entries[] = {
    {
        "null",
        CORE_SOLVER_CAT_PROVIDER_CONTENT,
        0u,
        g_caps_content_null, (u32)(sizeof(g_caps_content_null) / sizeof(g_caps_content_null[0])),
        0, 0u,
        0, 0u,
        0, 0u,
        0, 0u,
        0
    },
    {
        "local_fs",
        CORE_SOLVER_CAT_PROVIDER_CONTENT,
        10u,
        g_caps_content_local_fs, (u32)(sizeof(g_caps_content_local_fs) / sizeof(g_caps_content_local_fs[0])),
        0, 0u,
        0, 0u,
        0, 0u,
        0, 0u,
        0
    },
    {
        "null",
        CORE_SOLVER_CAT_PROVIDER_NET,
        0u,
        g_caps_net_null, (u32)(sizeof(g_caps_net_null) / sizeof(g_caps_net_null[0])),
        0, 0u,
        0, 0u,
        0, 0u,
        0, 0u,
        0
    },
    {
        "null",
        CORE_SOLVER_CAT_PROVIDER_TRUST,
        0u,
        g_caps_trust_null, (u32)(sizeof(g_caps_trust_null) / sizeof(g_caps_trust_null[0])),
        0, 0u,
        0, 0u,
        0, 0u,
        0, 0u,
        0
    },
    {
        "null",
        CORE_SOLVER_CAT_PROVIDER_KEYCHAIN,
        0u,
        g_caps_keychain_null, (u32)(sizeof(g_caps_keychain_null) / sizeof(g_caps_keychain_null[0])),
        0, 0u,
        0, 0u,
        0, 0u,
        0, 0u,
        0
    },
    {
        "null",
        CORE_SOLVER_CAT_PROVIDER_OS_INTEGRATION,
        0u,
        g_caps_os_null, (u32)(sizeof(g_caps_os_null) / sizeof(g_caps_os_null[0])),
        0, 0u,
        0, 0u,
        0, 0u,
        0, 0u,
        0
    }
};

static void provider_registry_init(void) {
    if (g_entries[0].provider) {
        return;
    }
    g_entries[0].provider = (const provider_base_v1*)provider_content_null_v1();
    g_entries[1].provider = (const provider_base_v1*)provider_content_local_fs_v1();
    g_entries[2].provider = (const provider_base_v1*)provider_net_null_v1();
    g_entries[3].provider = (const provider_base_v1*)provider_trust_null_v1();
    g_entries[4].provider = (const provider_base_v1*)provider_keychain_null_v1();
    g_entries[5].provider = (const provider_base_v1*)provider_os_integration_null_v1();
}

void provider_registry_get_entries(const provider_registry_entry** out_entries, u32* out_count) {
    provider_registry_init();
    if (out_entries) {
        *out_entries = g_entries;
    }
    if (out_count) {
        *out_count = (u32)(sizeof(g_entries) / sizeof(g_entries[0]));
    }
}

const provider_registry_entry* provider_registry_find(u32 category_id, const char* provider_id) {
    u32 i;
    provider_registry_init();
    if (!provider_id || !provider_id[0]) {
        return 0;
    }
    for (i = 0u; i < (u32)(sizeof(g_entries) / sizeof(g_entries[0])); ++i) {
        const provider_registry_entry* e = &g_entries[i];
        if (e->category_id == category_id && e->provider_id && strcmp(e->provider_id, provider_id) == 0) {
            return e;
        }
    }
    return 0;
}

static const void* provider_query(const provider_base_v1* base, dom_iid iid) {
    void* iface = 0;
    if (!base || !base->query_interface) {
        return 0;
    }
    if (base->query_interface(iid, &iface) != 0) {
        return 0;
    }
    return iface;
}

const provider_content_source_v1* provider_registry_get_content(const char* provider_id) {
    const provider_registry_entry* e = provider_registry_find(CORE_SOLVER_CAT_PROVIDER_CONTENT, provider_id);
    return (const provider_content_source_v1*)provider_query(e ? e->provider : 0, PROVIDER_IID_CONTENT_SOURCE_V1);
}

const provider_trust_v1* provider_registry_get_trust(const char* provider_id) {
    const provider_registry_entry* e = provider_registry_find(CORE_SOLVER_CAT_PROVIDER_TRUST, provider_id);
    return (const provider_trust_v1*)provider_query(e ? e->provider : 0, PROVIDER_IID_TRUST_V1);
}

const provider_keychain_v1* provider_registry_get_keychain(const char* provider_id) {
    const provider_registry_entry* e = provider_registry_find(CORE_SOLVER_CAT_PROVIDER_KEYCHAIN, provider_id);
    return (const provider_keychain_v1*)provider_query(e ? e->provider : 0, PROVIDER_IID_KEYCHAIN_V1);
}

const provider_net_v1* provider_registry_get_net(const char* provider_id) {
    const provider_registry_entry* e = provider_registry_find(CORE_SOLVER_CAT_PROVIDER_NET, provider_id);
    return (const provider_net_v1*)provider_query(e ? e->provider : 0, PROVIDER_IID_NET_V1);
}

const provider_os_integration_v1* provider_registry_get_os_integration(const char* provider_id) {
    const provider_registry_entry* e = provider_registry_find(CORE_SOLVER_CAT_PROVIDER_OS_INTEGRATION, provider_id);
    return (const provider_os_integration_v1*)provider_query(e ? e->provider : 0, PROVIDER_IID_OS_INTEGRATION_V1);
}
