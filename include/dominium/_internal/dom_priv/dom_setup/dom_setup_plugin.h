/*
FILE: include/dominium/_internal/dom_priv/dom_setup/dom_setup_plugin.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / _internal/dom_priv/dom_setup/dom_setup_plugin
RESPONSIBILITY: Defines the public contract for `dom_setup_plugin` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SETUP_PLUGIN_H
#define DOM_SETUP_PLUGIN_H

#include "domino/baseline.h"

#include "dom_shared/manifest_install.h"

struct SetupConfig;

typedef struct DomInstallProfileDescriptor {
    const char* id;
    const char* description;
    void (*apply_profile)(SetupConfig* cfg);
} DomInstallProfileDescriptor;

typedef struct DomSetupHookDescriptor {
    const char* id;
    const char* description;
    void (*run)(const dom_shared::InstallInfo* info);
} DomSetupHookDescriptor;

typedef struct DomSetupPluginAPI {
    void (*log_info)(const char* fmt, ...);
    void (*log_warn)(const char* fmt, ...);
    void (*log_error)(const char* fmt, ...);

    void (*register_install_profile)(const DomInstallProfileDescriptor*);
    void (*register_post_install_hook)(const DomSetupHookDescriptor*);
    void (*register_post_repair_hook)(const DomSetupHookDescriptor*);
    void (*register_post_uninstall_hook)(const DomSetupHookDescriptor*);
} DomSetupPluginAPI;

typedef struct DomSetupPlugin {
    uint32_t abi_version;
    void (*on_load)(DomSetupPluginAPI* api);
    void (*on_unload)(void);
} DomSetupPlugin;

#ifdef _WIN32
__declspec(dllexport)
#endif
const DomSetupPlugin* Dominium_GetSetupPlugin(void);

#endif /* DOM_SETUP_PLUGIN_H */
