#include "dom_shared/os_paths.h"

#include <cstdlib>
#include <string>

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <direct.h>
#include <shlobj.h>
#else
#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>
#endif

static std::string getenv_str(const char *name)
{
    const char *v = std::getenv(name);
    return v ? std::string(v) : std::string();
}

std::string os_path_join(const std::string &a, const std::string &b)
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

std::string os_get_executable_directory()
{
    char buf[1024];
#ifdef _WIN32
    DWORD len = GetModuleFileNameA(NULL, buf, sizeof(buf));
    if (len == 0 || len >= sizeof(buf)) return std::string(".");
    for (int i = (int)len - 1; i >= 0; --i) {
        if (buf[i] == '\\' || buf[i] == '/') {
            buf[i] = '\0';
            break;
        }
    }
    return std::string(buf);
#else
    ssize_t n = readlink("/proc/self/exe", buf, sizeof(buf) - 1);
    if (n <= 0) return std::string(".");
    buf[n] = '\0';
    for (int i = (int)n - 1; i >= 0; --i) {
        if (buf[i] == '/') {
            buf[i] = '\0';
            break;
        }
    }
    return std::string(buf);
#endif
}

static std::string home_dir()
{
#ifdef _WIN32
    std::string home = getenv_str("USERPROFILE");
    if (home.empty()) home = getenv_str("HOMEPATH");
    if (home.empty()) home = ".";
    return home;
#else
    std::string home = getenv_str("HOME");
    if (!home.empty()) return home;
    struct passwd *pw = getpwuid(getuid());
    if (pw) return std::string(pw->pw_dir);
    return std::string(".");
#endif
}

std::string os_get_platform_id()
{
#ifdef _WIN32
    return "win_nt";
#elif defined(__APPLE__)
    return "mac";
#else
    return "linux";
#endif
}

std::string os_get_default_per_user_install_root()
{
#ifdef _WIN32
    std::string base = getenv_str("LOCALAPPDATA");
    if (base.empty()) base = home_dir();
    return os_path_join(base, "Dominium\\Programs");
#elif defined(__APPLE__)
    return os_path_join(home_dir(), "Applications/Dominium");
#else
    std::string base = getenv_str("XDG_DATA_HOME");
    if (base.empty()) base = os_path_join(home_dir(), ".local/share");
    return os_path_join(base, "dominium");
#endif
}

std::string os_get_default_system_install_root()
{
#ifdef _WIN32
    std::string base = getenv_str("ProgramFiles");
    if (base.empty()) base = "C:\\\\Program Files";
    return os_path_join(base, "Dominium");
#elif defined(__APPLE__)
    return "/Applications/Dominium.app";
#else
    return "/opt/dominium";
#endif
}

std::string os_get_default_portable_install_root()
{
    return os_get_executable_directory();
}

std::string os_get_per_user_launcher_data_root()
{
#ifdef _WIN32
    std::string base = getenv_str("APPDATA");
    if (base.empty()) base = home_dir();
    return os_path_join(base, "Dominium\\Launcher");
#elif defined(__APPLE__)
    return os_path_join(home_dir(), "Library/Application Support/Dominium/Launcher");
#else
    std::string base = getenv_str("XDG_CONFIG_HOME");
    if (base.empty()) base = os_path_join(home_dir(), ".config");
    return os_path_join(base, "dominium/launcher");
#endif
}

std::string os_get_per_user_game_data_root()
{
#ifdef _WIN32
    std::string base = getenv_str("LOCALAPPDATA");
    if (base.empty()) base = home_dir();
    return os_path_join(base, "Dominium");
#elif defined(__APPLE__)
    return os_path_join(home_dir(), "Library/Application Support/Dominium");
#else
    std::string base = getenv_str("XDG_DATA_HOME");
    if (base.empty()) base = os_path_join(home_dir(), ".local/share");
    return os_path_join(base, "dominium");
#endif
}
