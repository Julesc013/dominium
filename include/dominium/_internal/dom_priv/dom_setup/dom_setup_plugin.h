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
