#ifndef DOM_SETUP_REGISTRATION_H
#define DOM_SETUP_REGISTRATION_H

#include "dom_shared/manifest_install.h"

void register_install_with_system(const InstallInfo &info);
void unregister_install_from_system(const InstallInfo &info);
void create_shortcuts_for_install(const InstallInfo &info);
void remove_shortcuts_for_install(const InstallInfo &info);

#endif /* DOM_SETUP_REGISTRATION_H */
