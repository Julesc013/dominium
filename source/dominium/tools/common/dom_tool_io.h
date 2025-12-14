#ifndef DOM_TOOL_IO_H
#define DOM_TOOL_IO_H

#include <string>
#include <vector>

namespace dom {
namespace tools {

bool read_file(const std::string &path,
               std::vector<unsigned char> &out,
               std::string *err);

bool write_file(const std::string &path,
                const unsigned char *data,
                size_t len,
                std::string *err);

bool file_exists(const std::string &path);

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_IO_H */

