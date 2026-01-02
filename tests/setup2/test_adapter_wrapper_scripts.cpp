#include <cstdio>
#include <fstream>
#include <string>
#include <vector>

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static int file_contains(const std::string &path, const char *needle) {
    std::ifstream in(path.c_str(), std::ios::binary);
    std::string content;
    if (!in) {
        return 0;
    }
    in.seekg(0, std::ios::end);
    std::streamoff size = in.tellg();
    in.seekg(0, std::ios::beg);
    if (size <= 0) {
        return 0;
    }
    content.resize((size_t)size);
    in.read(&content[0], size);
    if (!in.good() && !in.eof()) {
        return 0;
    }
    return content.find(needle ? needle : "") != std::string::npos;
}

static std::string join_path(const std::string &root, const std::string &rel) {
#if defined(_WIN32)
    const char sep = '\\';
#else
    const char sep = '/';
#endif
    if (root.empty()) {
        return rel;
    }
    return root + sep + rel;
}

int main(int argc, char **argv) {
    std::vector<std::string> files;
    size_t i;
    if (argc < 2) {
        std::fprintf(stderr, "usage: test_adapter_wrapper_scripts <repo_root>\n");
        return 1;
    }
    {
        std::string root = argv[1];
        files.push_back(join_path(root, "source/dominium/setup/frontends/adapters/windows_msi/wix/DominiumSetup2.wxs"));
        files.push_back(join_path(root, "source/dominium/setup/frontends/adapters/macos_pkg/packaging/postinstall"));
        files.push_back(join_path(root, "source/dominium/setup/frontends/adapters/linux_deb/packaging/postinst.sh"));
        files.push_back(join_path(root, "source/dominium/setup/frontends/adapters/linux_rpm/packaging/postinst.sh"));
    }

    for (i = 0u; i < files.size(); ++i) {
        if (!file_contains(files[i], "dominium-setup2")) {
            std::fprintf(stderr, "missing dominium-setup2 in: %s\n", files[i].c_str());
            return fail("wrapper script check failed");
        }
    }
    return 0;
}
