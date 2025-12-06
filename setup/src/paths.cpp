#include "dom_setup_paths.h"

#include <cstdlib>
#include <string>

#ifdef _WIN32
#include <direct.h>
#else
#include <unistd.h>
#endif

static std::string env_or_empty(const char *name)
{
    const char *v = std::getenv(name);
    return v ? std::string(v) : std::string();
}

std::string dom_setup_path_join(const std::string &a, const std::string &b)
{
    if (a.empty()) return b;
    if (b.empty()) return a;
    char last = a[a.size() - 1];
#ifdef _WIN32
    const char sep = '\\';
#else
    const char sep = '/';
#endif
    if (last == '/' || last == '\\') {
        return a + b;
    }
    return a + sep + b;
}

std::string dom_setup_get_cwd()
{
    char buf[1024];
#ifdef _WIN32
    if (_getcwd(buf, sizeof(buf)) != 0) {
        return std::string(buf);
    }
#else
    if (getcwd(buf, sizeof(buf)) != 0) {
        return std::string(buf);
    }
#endif
    return std::string(".");
}

static std::string home_dir()
{
    std::string home = env_or_empty("HOME");
#ifdef _WIN32
    if (home.empty()) home = env_or_empty("USERPROFILE");
#endif
    if (home.empty()) home = ".";
    return home;
}

std::string dom_setup_default_install_root_per_user()
{
#ifdef _WIN32
    std::string base = env_or_empty("LOCALAPPDATA");
    if (base.empty()) base = home_dir();
    return dom_setup_path_join(base, "Dominium\\Programs");
#elif defined(__APPLE__)
    return dom_setup_path_join(home_dir(), "Applications/Dominium");
#else
    std::string base = env_or_empty("XDG_DATA_HOME");
    if (base.empty()) base = dom_setup_path_join(home_dir(), ".local/share");
    return dom_setup_path_join(base, "dominium");
#endif
}

std::string dom_setup_default_install_root_system()
{
#ifdef _WIN32
    std::string base = env_or_empty("ProgramFiles");
    if (base.empty()) base = "C:\\\\Program Files";
    return dom_setup_path_join(base, "Dominium");
#elif defined(__APPLE__)
    return "/Applications/Dominium.app";
#else
    return "/opt/dominium";
#endif
}

std::string dom_setup_portable_root_from_target(const std::string &target)
{
    if (!target.empty()) return target;
    return dom_setup_get_cwd();
}

std::string dom_setup_user_data_root()
{
#ifdef _WIN32
    std::string base = env_or_empty("LOCALAPPDATA");
    if (base.empty()) base = home_dir();
    return dom_setup_path_join(base, "Dominium");
#elif defined(__APPLE__)
    return dom_setup_path_join(home_dir(), "Library/Application Support/Dominium");
#else
    std::string base = env_or_empty("XDG_DATA_HOME");
    if (base.empty()) base = dom_setup_path_join(home_dir(), ".local/share");
    return dom_setup_path_join(base, "dominium");
#endif
}

std::string dom_setup_user_config_root()
{
#ifdef _WIN32
    std::string base = env_or_empty("APPDATA");
    if (base.empty()) base = home_dir();
    return dom_setup_path_join(base, "Dominium");
#elif defined(__APPLE__)
    return dom_setup_path_join(home_dir(), "Library/Application Support/Dominium");
#else
    std::string base = env_or_empty("XDG_CONFIG_HOME");
    if (base.empty()) base = dom_setup_path_join(home_dir(), ".config");
    return dom_setup_path_join(base, "dominium");
#endif
}

std::string dom_setup_user_data_root_for_install(const std::string &install_type, const std::string &install_root)
{
    if (install_type == "portable") {
        return install_root;
    }
    return dom_setup_user_data_root();
}

std::string dom_setup_launcher_db_path(const std::string &install_type, const std::string &install_root)
{
    if (install_type == "portable") {
        return dom_setup_path_join(dom_setup_path_join(install_root, "launcher"), "db.json");
    }
    return dom_setup_path_join(dom_setup_user_config_root(), "launcher/db.json");
}

std::string dom_setup_install_index_path()
{
    return dom_setup_path_join(dom_setup_user_config_root(), "install_index.json");
}
