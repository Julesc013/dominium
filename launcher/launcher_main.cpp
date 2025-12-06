#include <iostream>
#include <cstring>

static const char *get_arg(int argc, char **argv, const char *key, const char *fallback)
{
    size_t klen = std::strlen(key);
    int i;
    for (i = 1; i < argc; ++i) {
        if (std::strncmp(argv[i], key, klen) == 0) {
            const char *eq = argv[i] + klen;
            if (*eq == '=' || *eq == ':') {
                return eq + 1;
            }
        }
    }
    return fallback;
}

int main(int argc, char **argv)
{
    const char *universe = get_arg(argc, argv, "--universe", "saves/default");
    const char *surface = get_arg(argc, argv, "--surface", "0");
    const char *ticks = get_arg(argc, argv, "--ticks", "60");

    std::cout << "Dominium launcher (stub)\n";
    std::cout << "Prepare to run runtime CLI with:\n";
    std::cout << "  dom_cli --universe=" << universe
              << " --surface=" << surface
              << " --ticks=" << ticks << "\n";
    std::cout << "This launcher does not spawn processes yet; integrate with your platform shell to dispatch runtimes.\n";
    return 0;
}
