#include <cstdio>
#include <fstream>
#include <string>

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

static int check_script(const std::string &path,
                        const char *needle_a,
                        const char *needle_b) {
    if (!file_contains(path, needle_a)) {
        std::fprintf(stderr, "missing %s in %s\n", needle_a, path.c_str());
        return 0;
    }
    if (needle_b && !file_contains(path, needle_b)) {
        std::fprintf(stderr, "missing %s in %s\n", needle_b, path.c_str());
        return 0;
    }
    return 1;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        std::fprintf(stderr, "usage: test_adapter_linux_wrappers <repo_root>\n");
        return 1;
    }
    {
        std::string root = argv[1];
        std::string deb_postinst = join_path(
            root,
            "source/dominium/setup/frontends/adapters/linux_deb/packaging/postinst.sh");
        std::string deb_prerm = join_path(
            root,
            "source/dominium/setup/frontends/adapters/linux_deb/packaging/prerm.sh");
        std::string rpm_postinst = join_path(
            root,
            "source/dominium/setup/frontends/adapters/linux_rpm/packaging/postinst.sh");
        std::string rpm_prerm = join_path(
            root,
            "source/dominium/setup/frontends/adapters/linux_rpm/packaging/prerm.sh");

        if (!check_script(deb_postinst, "dominium-setup2 status", "dominium-setup2 verify")) {
            return fail("deb postinst missing status/verify");
        }
        if (!check_script(rpm_postinst, "dominium-setup2 status", "dominium-setup2 verify")) {
            return fail("rpm postinst missing status/verify");
        }
        if (!check_script(deb_prerm, "installed_state.tlv", "job_journal.tlv")) {
            return fail("deb prerm missing state cleanup");
        }
        if (!check_script(rpm_prerm, "installed_state.tlv", "job_journal.tlv")) {
            return fail("rpm prerm missing state cleanup");
        }
    }
    return 0;
}
