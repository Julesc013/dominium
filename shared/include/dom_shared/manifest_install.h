#ifndef DOM_SHARED_MANIFEST_INSTALL_H
#define DOM_SHARED_MANIFEST_INSTALL_H

#include <string>

struct InstallInfo {
    std::string install_id;
    std::string install_type;  /* portable | per-user | system */
    std::string platform;      /* win_nt | linux | mac */
    std::string version;
    std::string root_path;
    std::string created_at;
    std::string created_by;
};

InstallInfo parse_install_manifest(const std::string &root_path, bool &ok, std::string &err);
void        write_install_manifest(const InstallInfo &info, bool &ok, std::string &err);
bool        manifest_exists(const std::string &root_path);

#endif /* DOM_SHARED_MANIFEST_INSTALL_H */
