#ifndef DOM_PACK_REGISTRY_H
#define DOM_PACK_REGISTRY_H

#include <string>

namespace dom {
namespace tools {

class DomPackRegistry {
public:
    DomPackRegistry();
    ~DomPackRegistry();

    void clear();
    bool load_from_home(const std::string &home, std::string &err);

private:
    DomPackRegistry(const DomPackRegistry &);
    DomPackRegistry &operator=(const DomPackRegistry &);
};

} // namespace tools
} // namespace dom

#endif /* DOM_PACK_REGISTRY_H */

