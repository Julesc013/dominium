// Cross-platform path helpers for dom_setup and dom_launcher.
#ifndef DOM_SETUP_PATHS_H
#define DOM_SETUP_PATHS_H

#include <string>

std::string dom_setup_path_join(const std::string &a, const std::string &b);
std::string dom_setup_get_cwd();

std::string dom_setup_default_install_root_per_user();
std::string dom_setup_default_install_root_system();
std::string dom_setup_portable_root_from_target(const std::string &target);

std::string dom_setup_user_data_root();
std::string dom_setup_user_config_root();
std::string dom_setup_user_data_root_for_install(const std::string &install_type, const std::string &install_root);
std::string dom_setup_launcher_db_path(const std::string &install_type, const std::string &install_root);
std::string dom_setup_install_index_path();

#endif /* DOM_SETUP_PATHS_H */
