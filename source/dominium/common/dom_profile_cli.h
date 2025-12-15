#ifndef DOM_PROFILE_CLI_H
#define DOM_PROFILE_CLI_H

#include <cstdio>
#include <string>

extern "C" {
#include "domino/profile.h"
}

namespace dom {

struct ProfileCli {
    dom_profile profile;
    bool print_caps;
    bool print_selection;
};

void init_default_profile_cli(ProfileCli &out);
bool parse_profile_cli_args(int argc, char **argv, ProfileCli &io, std::string &err);

void print_caps(FILE *out);
int print_selection(const dom_profile &profile, FILE *out, FILE *err);

} // namespace dom

#endif /* DOM_PROFILE_CLI_H */

