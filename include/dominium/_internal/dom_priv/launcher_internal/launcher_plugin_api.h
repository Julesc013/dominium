#ifndef DOM_LAUNCHER_PLUGIN_API_H
#define DOM_LAUNCHER_PLUGIN_API_H

#include <stddef.h>
#include "domino/baseline.h"

struct LauncherContext;
struct InstallInfo;
struct Instance;

typedef struct DomLauncherTabDescriptor {
    const char* id;
    const char* title;
    void (*on_open)(void);
    void (*on_close)(void);
    void (*on_tick)(float dt);
    void (*on_render_gui)(void* gui_ctx);
    void (*on_render_tui)(void* tui_ctx);
} DomLauncherTabDescriptor;

typedef struct DomLauncherCommandDescriptor {
    const char* name;
    const char* help;
    int (*run)(int argc, const char** argv);
} DomLauncherCommandDescriptor;

typedef struct DomLauncherPluginAPI {
    const LauncherContext* (*get_context)(void);

    const InstallInfo* (*get_installs)(size_t* out_count);
    const Instance*    (*get_instances)(size_t* out_count);
    const Instance*    (*get_instance)(const char* id);

    const char* (*start_instance)(const char* role,
                                  int display_mode,
                                  const char* universe_path,
                                  const char* profile_id,
                                  const char* mods_hash);

    bool (*stop_instance)(const char* instance_id);

    void (*log_info)(const char* fmt, ...);
    void (*log_warn)(const char* fmt, ...);
    void (*log_error)(const char* fmt, ...);

    bool (*set_plugin_kv)(const char* plugin_id, const char* key, const char* value);
    const char* (*get_plugin_kv)(const char* plugin_id, const char* key, const char* default_val);

    void (*register_tab)(const DomLauncherTabDescriptor*);
    void (*register_command)(const DomLauncherCommandDescriptor*);
} DomLauncherPluginAPI;

typedef struct DomLauncherPlugin {
    uint32_t abi_version;
    void (*on_load)(DomLauncherPluginAPI* api);
    void (*on_unload)(void);
} DomLauncherPlugin;

#ifdef _WIN32
__declspec(dllexport)
#endif
const DomLauncherPlugin* Dominium_GetLauncherPlugin(void);

#endif /* DOM_LAUNCHER_PLUGIN_API_H */
