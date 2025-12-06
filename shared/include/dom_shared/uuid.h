#ifndef DOM_SHARED_UUID_H
#define DOM_SHARED_UUID_H

#include <string>

namespace dom_shared {

std::string generate_uuid(); // returns a RFC4122-like string "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

} // namespace dom_shared

#endif
