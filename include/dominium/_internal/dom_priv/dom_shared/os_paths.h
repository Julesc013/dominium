#ifndef DOM_SHARED_OS_PATHS_H
#define DOM_SHARED_OS_PATHS_H

#include <string>
#include <vector>

namespace dom_shared {

std::string os_get_executable_path();       // full path to this executable
std::string os_get_executable_directory();  // directory containing this executable

std::string os_get_platform_id();           // "win_nt" | "linux" | "mac"

// Default install roots for different modes
std::string os_get_default_per_user_install_root();
std::string os_get_default_system_install_root();
std::string os_get_default_portable_install_root(); // usually current dir

// Data roots for launcher and game
std::string os_get_per_user_launcher_data_root();
std::string os_get_per_user_game_data_root();

// Default install root search locations for discovery
std::vector<std::string> os_get_default_install_roots();

bool os_ensure_directory_exists(const std::string& path);
bool os_file_exists(const std::string& path);
bool os_directory_exists(const std::string& path);

// Join path segments with platform-appropriate separators
std::string os_path_join(const std::string& a, const std::string& b);

} // namespace dom_shared

#endif
