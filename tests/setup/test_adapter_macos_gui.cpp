#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include <spawn.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

extern char **environ;

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static int make_dir_if_needed(const std::string &path) {
    if (path.empty()) {
        return 0;
    }
    if (mkdir(path.c_str(), 0755) == 0) {
        return 1;
    }
    return (errno == EEXIST);
}

static int file_exists(const std::string &path) {
    struct stat st;
    return stat(path.c_str(), &st) == 0;
}

static int read_file(const std::string &path, std::vector<unsigned char> &out) {
    FILE *in = std::fopen(path.c_str(), "rb");
    size_t size;
    if (!in) {
        return 0;
    }
    std::fseek(in, 0, SEEK_END);
    size = (size_t)std::ftell(in);
    std::fseek(in, 0, SEEK_SET);
    out.resize(size);
    if (size > 0u && std::fread(&out[0], 1u, size, in) != size) {
        std::fclose(in);
        return 0;
    }
    std::fclose(in);
    return 1;
}

static int spawn_process(const std::string &exe, const std::vector<std::string> &args) {
    std::vector<char *> argv;
    argv.reserve(args.size() + 2u);
    argv.push_back(const_cast<char *>(exe.c_str()));
    for (size_t i = 0u; i < args.size(); ++i) {
        argv.push_back(const_cast<char *>(args[i].c_str()));
    }
    argv.push_back(NULL);

    pid_t pid = 0;
    int status = 0;
    if (posix_spawn(&pid, exe.c_str(), NULL, NULL, &argv[0], environ) != 0) {
        return -1;
    }
    if (waitpid(pid, &status, 0) == -1) {
        return -1;
    }
    if (WIFEXITED(status)) {
        return WEXITSTATUS(status);
    }
    return -1;
}

int main(int argc, char **argv) {
    if (argc < 4) {
        std::fprintf(stderr, "usage: test_adapter_macos_gui <app_bin> <repo_root> <work_dir>\n");
        return 1;
    }
    std::string app = argv[1];
    std::string root = argv[2];
    std::string work_dir = argv[3];
    std::string manifest = root + "/source/dominium/setup/tests/fixtures/manifests/minimal.dsumanifest";
    std::string out1 = work_dir + "/install_request_1.tlv";
    std::string out2 = work_dir + "/install_request_2.tlv";
    std::vector<unsigned char> a;
    std::vector<unsigned char> b;
    int code;

    if (!make_dir_if_needed(work_dir)) {
        return fail("failed to create work dir");
    }

    {
        std::vector<std::string> args;
        args.push_back("--export-request");
        args.push_back("--manifest");
        args.push_back(manifest);
        args.push_back("--op");
        args.push_back("install");
        args.push_back("--scope");
        args.push_back("user");
        args.push_back("--platform");
        args.push_back("macos-x64");
        args.push_back("--frontend-id");
        args.push_back("test-macos-gui");
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--out-request");
        args.push_back(out1);
        args.push_back("--sandbox-root");
        args.push_back(work_dir);
        code = spawn_process(app, args);
        if (code != 0 || !file_exists(out1)) {
            return fail("macos gui export (first) failed");
        }
    }

    {
        std::vector<std::string> args;
        args.push_back("--export-request");
        args.push_back("--manifest");
        args.push_back(manifest);
        args.push_back("--op");
        args.push_back("install");
        args.push_back("--scope");
        args.push_back("user");
        args.push_back("--platform");
        args.push_back("macos-x64");
        args.push_back("--frontend-id");
        args.push_back("test-macos-gui");
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--out-request");
        args.push_back(out2);
        args.push_back("--sandbox-root");
        args.push_back(work_dir);
        code = spawn_process(app, args);
        if (code != 0 || !file_exists(out2)) {
            return fail("macos gui export (second) failed");
        }
    }

    if (!read_file(out1, a) || !read_file(out2, b)) {
        return fail("failed to read request outputs");
    }
    if (a.size() != b.size() || std::memcmp(&a[0], &b[0], a.size()) != 0) {
        return fail("request bytes mismatch");
    }
    return 0;
}
