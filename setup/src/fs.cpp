#include "dom_setup_fs.h"

#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <sys/stat.h>
#include <errno.h>

#ifdef _WIN32
#include <direct.h>
#include <io.h>
#else
#include <dirent.h>
#include <unistd.h>
#include <errno.h>
#endif

static std::string fs_join(const std::string &a, const std::string &b)
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

bool dom_fs_path_exists(const std::string &path)
{
    struct stat st;
    return stat(path.c_str(), &st) == 0;
}

bool dom_fs_is_dir(const std::string &path)
{
    struct stat st;
    if (stat(path.c_str(), &st) != 0) return false;
#ifdef _WIN32
    return (st.st_mode & _S_IFDIR) != 0;
#else
    return S_ISDIR(st.st_mode);
#endif
}

static bool fs_mkdir_single(const std::string &path)
{
    if (path.empty()) return false;
#ifdef _WIN32
    int r = _mkdir(path.c_str());
    return (r == 0) || (errno == EEXIST);
#else
    int r = mkdir(path.c_str(), 0755);
    return (r == 0) || (errno == EEXIST);
#endif
}

bool dom_fs_make_dirs(const std::string &path)
{
    if (path.empty()) return false;
    if (dom_fs_is_dir(path)) return true;
    std::string partial;
    size_t start = 0;
#ifdef _WIN32
    if (path.size() > 1 && path[1] == ':') {
        partial = path.substr(0, 2); /* Preserve drive prefix */
        start = 2;
    }
#endif
    for (size_t i = start; i < path.size(); ++i) {
        char c = path[i];
        partial.push_back(c);
        if (c == '/' || c == '\\' || i == path.size() - 1) {
            if (!dom_fs_path_exists(partial)) {
                if (!fs_mkdir_single(partial)) {
                    return false;
                }
            }
        }
    }
    return true;
}

bool dom_fs_copy_file(const std::string &src, const std::string &dst)
{
    FILE *fin = std::fopen(src.c_str(), "rb");
    FILE *fout;
    char buf[4096];
    size_t n;
    if (!fin) return false;
    fout = std::fopen(dst.c_str(), "wb");
    if (!fout) {
        std::fclose(fin);
        return false;
    }
    while ((n = std::fread(buf, 1, sizeof(buf), fin)) > 0) {
        if (std::fwrite(buf, 1, n, fout) != n) {
            std::fclose(fin);
            std::fclose(fout);
            return false;
        }
    }
    std::fclose(fin);
    std::fclose(fout);
    return true;
}

std::vector<std::string> dom_fs_list_dir(const std::string &path)
{
    std::vector<std::string> out;
    if (!dom_fs_is_dir(path)) return out;
#ifdef _WIN32
    std::string pattern = fs_join(path, "*");
    _finddata_t fd;
    intptr_t h = _findfirst(pattern.c_str(), &fd);
    if (h == -1) return out;
    do {
        if (std::strcmp(fd.name, ".") == 0 || std::strcmp(fd.name, "..") == 0) continue;
        out.push_back(fd.name);
    } while (_findnext(h, &fd) == 0);
    _findclose(h);
#else
    DIR *dir = opendir(path.c_str());
    if (!dir) return out;
    struct dirent *de;
    while ((de = readdir(dir)) != 0) {
        if (std::strcmp(de->d_name, ".") == 0 || std::strcmp(de->d_name, "..") == 0) continue;
        out.push_back(de->d_name);
    }
    closedir(dir);
#endif
    return out;
}

bool dom_fs_remove_tree(const std::string &path)
{
    if (!dom_fs_path_exists(path)) return true;
    if (!dom_fs_is_dir(path)) {
#ifdef _WIN32
        return _unlink(path.c_str()) == 0;
#else
        return std::remove(path.c_str()) == 0;
#endif
    }
    std::vector<std::string> entries = dom_fs_list_dir(path);
    for (size_t i = 0; i < entries.size(); ++i) {
        std::string child = fs_join(path, entries[i]);
        if (!dom_fs_remove_tree(child)) {
            return false;
        }
    }
#ifdef _WIN32
    return _rmdir(path.c_str()) == 0;
#else
    return rmdir(path.c_str()) == 0;
#endif
}
