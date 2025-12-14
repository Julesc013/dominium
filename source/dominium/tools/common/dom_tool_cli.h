#ifndef DOM_TOOL_CLI_H
#define DOM_TOOL_CLI_H

#include <string>

namespace dom {
namespace tools {

struct DomToolCliConfig {
    std::string home;
    std::string load;
    std::string sys_backend;
    std::string gfx_backend;
    bool demo;

    DomToolCliConfig() : home(), load(), sys_backend(), gfx_backend(), demo(false) {}
};

bool parse_tool_cli(int argc, char **argv, DomToolCliConfig &out, std::string &err);

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_CLI_H */

