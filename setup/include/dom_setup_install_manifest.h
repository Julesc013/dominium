// Copyright Dominium
// Install manifest format shared between launcher and setup.
// See docs/FORMATS/FORMAT_INSTALL_MANIFEST.md for the canonical schema.

#ifndef DOM_SETUP_INSTALL_MANIFEST_H
#define DOM_SETUP_INSTALL_MANIFEST_H

#include <string>

struct DomInstallManifest {
    int schema_version;
    std::string install_id;
    std::string install_type; /* portable | per-user | system */
    std::string platform;     /* win_nt | linux | mac */
    std::string version;
    std::string created_at;
    std::string created_by;
};

bool dom_manifest_read(const std::string &path, DomInstallManifest &out, std::string &err);
bool dom_manifest_write(const std::string &path, const DomInstallManifest &manifest, std::string &err);
std::string dom_manifest_generate_uuid();
std::string dom_manifest_platform_tag();

#endif /* DOM_SETUP_INSTALL_MANIFEST_H */
