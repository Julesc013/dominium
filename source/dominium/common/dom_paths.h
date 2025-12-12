#ifndef DOM_PATHS_H
#define DOM_PATHS_H

#include <string>

namespace dom {

struct Paths {
    std::string root;      /* DOMINIUM_HOME */
    std::string products;  /* root + "/repo/products" */
    std::string mods;      /* root + "/repo/mods" */
    std::string packs;     /* root + "/repo/packs" */
    std::string instances; /* root + "/instances" */
    std::string temp;      /* root + "/temp" */
};

bool resolve_paths(Paths &out, const std::string &home);
std::string join(const std::string &a, const std::string &b);
bool file_exists(const std::string &p);
bool dir_exists(const std::string &p);

} // namespace dom

#endif
