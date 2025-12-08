#include "setup_plugins.h"
#include "dom_shared/logging.h"

#include <vector>

#ifdef _WIN32
#include <windows.h>
#else
#include <dlfcn.h>
#endif

struct PluginState {
    std::vector<DomInstallProfileDescriptor> profiles;
    std::vector<DomSetupHookDescriptor> post_install;
    std::vector<DomSetupHookDescriptor> post_repair;
    std::vector<DomSetupHookDescriptor> post_uninstall;
} g_plugins;

static void api_log_info(const char* fmt, ...)
{
    (void)fmt;
}
static void api_log_warn(const char* fmt, ...)
{
    (void)fmt;
}
static void api_log_error(const char* fmt, ...)
{
    (void)fmt;
}

static void api_register_profile(const DomInstallProfileDescriptor* desc)
{
    if (desc) g_plugins.profiles.push_back(*desc);
}
static void api_register_post_install(const DomSetupHookDescriptor* desc)
{
    if (desc) g_plugins.post_install.push_back(*desc);
}
static void api_register_post_repair(const DomSetupHookDescriptor* desc)
{
    if (desc) g_plugins.post_repair.push_back(*desc);
}
static void api_register_post_uninstall(const DomSetupHookDescriptor* desc)
{
    if (desc) g_plugins.post_uninstall.push_back(*desc);
}

void setup_plugins_load()
{
    g_plugins.profiles.clear();
    g_plugins.post_install.clear();
    g_plugins.post_repair.clear();
    g_plugins.post_uninstall.clear();
    /* Stub: no actual dynamic loading yet */
    DomSetupPluginAPI api;
    api.log_info = api_log_info;
    api.log_warn = api_log_warn;
    api.log_error = api_log_error;
    api.register_install_profile = api_register_profile;
    api.register_post_install_hook = api_register_post_install;
    api.register_post_repair_hook = api_register_post_repair;
    api.register_post_uninstall_hook = api_register_post_uninstall;
    (void)api;
}

void setup_plugins_unload()
{
    g_plugins.profiles.clear();
    g_plugins.post_install.clear();
    g_plugins.post_repair.clear();
    g_plugins.post_uninstall.clear();
}

void setup_plugins_apply_profiles(SetupConfig &cfg)
{
    for (size_t i = 0; i < g_plugins.profiles.size(); ++i) {
        if (g_plugins.profiles[i].apply_profile) {
            g_plugins.profiles[i].apply_profile(&cfg);
        }
    }
}

void setup_plugins_post_install(const dom_shared::InstallInfo &info)
{
    for (size_t i = 0; i < g_plugins.post_install.size(); ++i) {
        if (g_plugins.post_install[i].run) g_plugins.post_install[i].run(&info);
    }
}

void setup_plugins_post_repair(const dom_shared::InstallInfo &info)
{
    for (size_t i = 0; i < g_plugins.post_repair.size(); ++i) {
        if (g_plugins.post_repair[i].run) g_plugins.post_repair[i].run(&info);
    }
}

void setup_plugins_post_uninstall(const dom_shared::InstallInfo &info)
{
    for (size_t i = 0; i < g_plugins.post_uninstall.size(); ++i) {
        if (g_plugins.post_uninstall[i].run) g_plugins.post_uninstall[i].run(&info);
    }
}
