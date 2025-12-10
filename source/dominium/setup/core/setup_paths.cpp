#include "setup_paths.h"
#include "dom_shared/os_paths.h"

#include <string>

using namespace dom_shared;

std::string setup_user_data_root_for_install(const std::string &install_type, const std::string &install_root)
{
    if (install_type == "portable") {
        return install_root;
    }
    return os_get_per_user_game_data_root();
}

std::string setup_launcher_db_path_for_install(const std::string &install_type, const std::string &install_root)
{
    if (install_type == "portable") {
        return os_path_join(os_path_join(install_root, "launcher"), "db.json");
    }
    return os_path_join(os_get_per_user_launcher_data_root(), "db.json");
}
