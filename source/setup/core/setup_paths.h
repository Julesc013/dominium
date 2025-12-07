#ifndef DOM_SETUP_PATHS_H
#define DOM_SETUP_PATHS_H

#include <string>

std::string setup_user_data_root_for_install(const std::string &install_type, const std::string &install_root);
std::string setup_launcher_db_path_for_install(const std::string &install_type, const std::string &install_root);

#endif /* DOM_SETUP_PATHS_H */
