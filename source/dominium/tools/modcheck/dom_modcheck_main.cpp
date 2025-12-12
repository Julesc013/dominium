#include <cstdio>

#include "dom_modcheck.h"

int main(int argc, char **argv) {
    if (argc < 2) {
        std::printf("Usage: modcheck <mod-path>\n");
        return 1;
    }

    const char *path = argv[1];
    return dom::modcheck_run(path) ? 0 : 1;
}
