#include "setup_registration.h"
#include "dom_shared/logging.h"

using namespace dom_shared;

void register_install_with_system(const dom_shared::InstallInfo &info)
{
    (void)info;
    log_info("register_install_with_system: stub (platform-specific registration not implemented)");
}

void unregister_install_from_system(const dom_shared::InstallInfo &info)
{
    (void)info;
    log_info("unregister_install_from_system: stub");
}

void create_shortcuts_for_install(const dom_shared::InstallInfo &info)
{
    (void)info;
    log_info("create_shortcuts_for_install: stub");
}

void remove_shortcuts_for_install(const dom_shared::InstallInfo &info)
{
    (void)info;
    log_info("remove_shortcuts_for_install: stub");
}
