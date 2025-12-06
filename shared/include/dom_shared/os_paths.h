#ifndef DOM_SHARED_OS_PATHS_H
#define DOM_SHARED_OS_PATHS_H

#include <string>
#include <vector>

std::string os_get_executable_directory();
std::string os_get_platform_id(); /* win_nt | linux | mac */

std::string os_get_default_per_user_install_root();
std::string os_get_default_system_install_root();
std::string os_get_default_portable_install_root();

std::string os_get_per_user_launcher_data_root();
std::string os_get_per_user_game_data_root();

std::string os_path_join(const std::string &a, const std::string &b);
std::vector<std::string> os_get_default_install_roots();

#endif /* DOM_SHARED_OS_PATHS_H */
