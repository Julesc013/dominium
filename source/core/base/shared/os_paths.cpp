#include "dom_shared/os_paths.h"

#include <cstdlib>
#include <string>
#include <cstring>
#include <vector>
#include <sys/stat.h>

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <direct.h>
#else
#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>
#ifdef __APPLE__
#include <mach-o/dyld.h>
#endif
#endif

namespace dom_shared {

static std::string getenv_str(const char* name)
{
    const char* v = std::getenv(name);
    return v ? std::string(v) : std::string();
}

static std::string trim_trailing_separators(const std::string& path)
{
    if (path.empty()) return path;
    std::string out = path;
    while (!out.empty()) {
        char c = out[out.size() - 1];
        if (c == '\\' || c == '/') {
            out.erase(out.size() - 1);
        } else {
            break;
        }
    }
    return out;
}

std::string os_path_join(const std::string& a, const std::string& b)
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

static std::string directory_of(const std::string& path)
{
    if (path.empty()) return std::string(".");
    std::string cleaned = trim_trailing_separators(path);
    for (int i = (int)cleaned.size() - 1; i >= 0; --i) {
        if (cleaned[i] == '\\' || cleaned[i] == '/') {
            return cleaned.substr(0, i);
        }
    }
    return std::string(".");
}

std::string os_get_executable_path()
{
#ifdef _WIN32
    DWORD size = 260;
    while (true) {
        std::string buffer(size, '\0');
        DWORD len = GetModuleFileNameA(NULL, &buffer[0], size);
        if (len == 0) {
            return std::string(".");
        }
        if (len < size - 1) {
            buffer.resize(len);
            return buffer;
        }
        size *= 2;
    }
#elif defined(__APPLE__)
    uint32_t size = 0;
    _NSGetExecutablePath(NULL, &size);
    std::string buffer(size, '\0');
    if (_NSGetExecutablePath(&buffer[0], &size) != 0) {
        return std::string(".");
    }
    buffer.resize(std::strlen(buffer.c_str()));
    char resolved[1024];
    if (realpath(buffer.c_str(), resolved)) {
        return std::string(resolved);
    }
    return buffer;
#else
    char buf[1024];
    ssize_t n = readlink("/proc/self/exe", buf, sizeof(buf) - 1);
    if (n <= 0) return std::string(".");
    buf[n] = '\0';
    return std::string(buf);
#endif
}

std::string os_get_executable_directory()
{
    return directory_of(os_get_executable_path());
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
    struct passwd* pw = getpwuid(getuid());
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
    return os_path_join(base, "Programs\\Dominium");
#elif defined(__APPLE__)
    return os_path_join(home_dir(), "Applications/Dominium.app");
#else
    std::string base = getenv_str("XDG_DATA_HOME");
    if (base.empty()) base = os_path_join(home_dir(), ".local/share");
    return os_path_join(base, "dominium/install");
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

static bool ensure_single_dir(const std::string& path)
{
#ifdef _WIN32
    int rc = _mkdir(path.c_str());
    if (rc == 0) return true;
    struct _stat st;
    if (_stat(path.c_str(), &st) == 0 && (st.st_mode & _S_IFDIR)) return true;
    return false;
#else
    int rc = mkdir(path.c_str(), 0755);
    if (rc == 0) return true;
    struct stat st;
    if (stat(path.c_str(), &st) == 0 && S_ISDIR(st.st_mode)) return true;
    return false;
#endif
}

bool os_ensure_directory_exists(const std::string& path)
{
    if (path.empty()) return false;
    if (os_directory_exists(path)) return true;

    std::string accum;
    for (size_t i = 0; i < path.size(); ++i) {
        char c = path[i];
        accum.push_back(c);
        if (c == '\\' || c == '/') {
            if (!accum.empty() && !os_directory_exists(accum)) {
                if (!ensure_single_dir(accum)) return false;
            }
        }
    }
    if (!os_directory_exists(accum)) {
        if (!ensure_single_dir(accum)) return false;
    }
    return true;
}

bool os_file_exists(const std::string& path)
{
    struct stat st;
    if (stat(path.c_str(), &st) != 0) return false;
    return (st.st_mode & S_IFREG) != 0;
}

bool os_directory_exists(const std::string& path)
{
    struct stat st;
    if (stat(path.c_str(), &st) != 0) return false;
    return (st.st_mode & S_IFDIR) != 0;
}

std::vector<std::string> os_get_default_install_roots()
{
    std::vector<std::string> roots;
    roots.push_back(os_get_default_per_user_install_root());
    roots.push_back(os_get_default_system_install_root());
    roots.push_back(os_get_default_portable_install_root());
#ifdef _WIN32
    std::string program_data = getenv_str("ProgramData");
    if (!program_data.empty()) roots.push_back(os_path_join(program_data, "Dominium"));
#elif defined(__APPLE__)
    // Already covered per-user/system; no-op placeholder for future bundle variants.
#else
    roots.push_back(os_path_join(home_dir(), "Applications/Dominium"));
#endif
    return roots;
}

} // namespace dom_shared
