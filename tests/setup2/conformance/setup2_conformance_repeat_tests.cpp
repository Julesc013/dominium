#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#if defined(_WIN32)
#include <direct.h>
#include <io.h>
#include <process.h>
#include <sys/stat.h>
#include <errno.h>
#else
#include <dirent.h>
#include <errno.h>
#include <sys/stat.h>
#endif

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 1;
}

static int make_dir_one(const std::string &path) {
#if defined(_WIN32)
    if (_mkdir(path.c_str()) == 0) {
        return 1;
    }
#else
    if (mkdir(path.c_str(), 0755) == 0) {
        return 1;
    }
#endif
    return errno == EEXIST;
}

static int make_dir_recursive(const std::string &path) {
    size_t i;
    std::string current;
    if (path.empty()) {
        return 0;
    }
    for (i = 0u; i <= path.size(); ++i) {
        char c = (i < path.size()) ? path[i] : '\0';
        if (c == '/' || c == '\\' || c == '\0') {
            if (!current.empty()) {
                if (!make_dir_one(current)) {
                    return 0;
                }
            }
        }
        if (c != '\0') {
            current.push_back(c);
        }
    }
    return 1;
}

static int remove_dir_recursive(const std::string &path) {
#if defined(_WIN32)
    std::string pattern = path + "\\*";
    struct _finddata_t data;
    intptr_t handle = _findfirst(pattern.c_str(), &data);
    if (handle == -1) {
        return (errno == ENOENT) ? 1 : 0;
    }
    do {
        const char *name = data.name;
        if (std::strcmp(name, ".") == 0 || std::strcmp(name, "..") == 0) {
            continue;
        }
        std::string child = path + "\\" + name;
        if (data.attrib & _A_SUBDIR) {
            if (!remove_dir_recursive(child)) {
                _findclose(handle);
                return 0;
            }
            _rmdir(child.c_str());
        } else {
            std::remove(child.c_str());
        }
    } while (_findnext(handle, &data) == 0);
    _findclose(handle);
    _rmdir(path.c_str());
    return 1;
#else
    DIR *dir = opendir(path.c_str());
    if (!dir) {
        return (errno == ENOENT) ? 1 : 0;
    }
    struct dirent *ent;
    while ((ent = readdir(dir)) != NULL) {
        const char *name = ent->d_name;
        if (std::strcmp(name, ".") == 0 || std::strcmp(name, "..") == 0) {
            continue;
        }
        std::string child = path + "/" + name;
        struct stat st;
        if (stat(child.c_str(), &st) != 0) {
            continue;
        }
        if (S_ISDIR(st.st_mode)) {
            if (!remove_dir_recursive(child)) {
                closedir(dir);
                return 0;
            }
            rmdir(child.c_str());
        } else {
            std::remove(child.c_str());
        }
    }
    closedir(dir);
    rmdir(path.c_str());
    return 1;
#endif
}

static std::string join_path(const std::string &a, const std::string &b) {
#if defined(_WIN32)
    const char sep = '\\';
#else
    const char sep = '/';
#endif
    if (a.empty()) {
        return b;
    }
    if (b.empty()) {
        return a;
    }
    if (a[a.size() - 1u] == '/' || a[a.size() - 1u] == '\\') {
        return a + b;
    }
    return a + sep + b;
}

#if defined(_WIN32)
static std::string normalize_win_path(const std::string &path) {
    std::string out = path;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '/') {
            out[i] = '\\';
        }
    }
    return out;
}
#endif

static int read_file(const std::string &path, std::vector<unsigned char> &out) {
    std::FILE *in = std::fopen(path.c_str(), "rb");
    if (!in) {
        return 0;
    }
    std::fseek(in, 0, SEEK_END);
    long size = std::ftell(in);
    std::fseek(in, 0, SEEK_SET);
    if (size < 0) {
        std::fclose(in);
        return 0;
    }
    out.resize((size_t)size);
    if (size > 0 && std::fread(&out[0], 1u, (size_t)size, in) != (size_t)size) {
        std::fclose(in);
        return 0;
    }
    std::fclose(in);
    return 1;
}

static int compare_files(const std::string &left, const std::string &right) {
    std::vector<unsigned char> a;
    std::vector<unsigned char> b;
    if (!read_file(left, a)) {
        return 0;
    }
    if (!read_file(right, b)) {
        return 0;
    }
    return (a.size() == b.size() &&
            (a.empty() || std::memcmp(&a[0], &b[0], a.size()) == 0));
}

static std::string quote_arg(const std::string &arg) {
    if (arg.find(' ') == std::string::npos && arg.find('\t') == std::string::npos) {
        return arg;
    }
    std::string out = "\"";
    size_t i;
    for (i = 0u; i < arg.size(); ++i) {
        char c = arg[i];
        if (c == '"') {
            out += "\\\"";
        } else {
            out.push_back(c);
        }
    }
    out += "\"";
    return out;
}

static int run_runner(const std::string &exe,
                      const std::string &sandbox_root,
                      const std::string &fixtures_root,
                      const std::string &out_json) {
#if defined(_WIN32)
    std::vector<const char *> argv;
    std::string exe_path = normalize_win_path(exe);
    std::string sandbox_native = normalize_win_path(sandbox_root);
    std::string fixtures_native = normalize_win_path(fixtures_root);
    std::string json_native = normalize_win_path(out_json);
    argv.push_back(exe_path.c_str());
    argv.push_back("--sandbox-root");
    argv.push_back(sandbox_native.c_str());
    argv.push_back("--fixtures-root");
    argv.push_back(fixtures_native.c_str());
    argv.push_back("--deterministic");
    argv.push_back("1");
    argv.push_back("--out-json");
    argv.push_back(json_native.c_str());
    argv.push_back(0);
    return _spawnvp(_P_WAIT, exe_path.c_str(), &argv[0]) == 0;
#else
    std::string cmd = quote_arg(exe);
    cmd += " --sandbox-root " + quote_arg(sandbox_root);
    cmd += " --fixtures-root " + quote_arg(fixtures_root);
    cmd += " --deterministic 1";
    cmd += " --out-json " + quote_arg(out_json);
    return std::system(cmd.c_str()) == 0;
#endif
}

int main(int argc, char **argv) {
    if (argc < 4) {
        std::fprintf(stderr,
                     "usage: setup2_conformance_repeat_tests <runner> <fixtures_root> <sandbox_root>\n");
        return 1;
    }
    std::string runner = argv[1];
    std::string fixtures_root = argv[2];
    std::string sandbox_root = argv[3];

#if defined(_WIN32)
    runner = normalize_win_path(runner);
    fixtures_root = normalize_win_path(fixtures_root);
    sandbox_root = normalize_win_path(sandbox_root);
#endif

    std::string run_a = join_path(sandbox_root, "run_a");
    std::string run_b = join_path(sandbox_root, "run_b");
    std::string json_a = join_path(run_a, "conformance_summary.json");
    std::string json_b = join_path(run_b, "conformance_summary.json");

    remove_dir_recursive(sandbox_root);
    if (!make_dir_recursive(run_a) || !make_dir_recursive(run_b)) {
        return fail("failed to create sandbox roots");
    }
    if (!run_runner(runner, run_a, fixtures_root, json_a)) {
        return fail("runner failed (run_a)");
    }
    if (!run_runner(runner, run_b, fixtures_root, json_b)) {
        return fail("runner failed (run_b)");
    }
    if (!compare_files(json_a, json_b)) {
        return fail("conformance json mismatch");
    }

    {
        static const char *k_cases[] = {
            "fresh_install_portable",
            "crash_during_staging_resume",
            "crash_during_commit_rollback",
            "crash_during_commit_resume",
            "repair_fixes_corruption",
            "uninstall_leaves_only_documented_residue",
            "upgrade_preserves_user_data_and_can_rollback",
            "offline_install_works",
            "determinism_repeatability"
        };
        static const char *k_artifacts[] = {
            "out/plan.tlv",
            "out/state.tlv",
            "out/audit.tlv",
            "out/journal.tlv",
            "out/journal.tlv.txn.tlv"
        };
        size_t i;
        size_t j;
        for (i = 0u; i < sizeof(k_cases) / sizeof(k_cases[0]); ++i) {
            for (j = 0u; j < sizeof(k_artifacts) / sizeof(k_artifacts[0]); ++j) {
                std::string left = join_path(join_path(run_a, k_cases[i]), k_artifacts[j]);
                std::string right = join_path(join_path(run_b, k_cases[i]), k_artifacts[j]);
                if (!compare_files(left, right)) {
                    return fail("artifact mismatch between runs");
                }
            }
        }
    }
    return 0;
}
