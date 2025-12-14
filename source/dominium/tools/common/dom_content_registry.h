#ifndef DOM_CONTENT_REGISTRY_H
#define DOM_CONTENT_REGISTRY_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/d_tlv.h"
}

namespace dom {
namespace tools {

class DomContentRegistry {
public:
    DomContentRegistry();
    ~DomContentRegistry();

    void reset();

    bool load_as_pack(const d_tlv_blob &content_or_pack_manifest, std::string &err);
    bool load_as_mod(const d_tlv_blob &content_or_mod_manifest, std::string &err);

    bool validate_all(std::string &err);

private:
    DomContentRegistry(const DomContentRegistry &);
    DomContentRegistry &operator=(const DomContentRegistry &);
};

} // namespace tools
} // namespace dom

#endif /* DOM_CONTENT_REGISTRY_H */

