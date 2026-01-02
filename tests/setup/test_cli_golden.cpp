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
    std::fprintf(stderr, "FAIL: %s\n", msg);
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

static std::string parent_dir(const std::string &path) {
    size_t i = path.find_last_of("/\\");
    if (i == std::string::npos) {
        return std::string();
    }
    return path.substr(0u, i);
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

static int write_file(const std::string &path, const std::vector<unsigned char> &data) {
    std::FILE *out = std::fopen(path.c_str(), "wb");
    if (!out) {
        return 0;
    }
    if (!data.empty()) {
        if (std::fwrite(&data[0], 1u, data.size(), out) != data.size()) {
            std::fclose(out);
            return 0;
        }
    }
    std::fclose(out);
    return 1;
}

static int copy_file(const std::string &src, const std::string &dst) {
    std::vector<unsigned char> data;
    std::string dir = parent_dir(dst);
    if (!dir.empty() && !make_dir_recursive(dir)) {
        return 0;
    }
    if (!read_file(src, data)) {
        return 0;
    }
    return write_file(dst, data);
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

static int run_cli(const std::string &exe,
                   const std::vector<std::string> &args,
                   const std::string &stdout_path) {
#if defined(_WIN32)
    std::vector<const char *> argv;
    FILE *out = 0;
    int saved_fd = -1;
    int code;
    size_t i;
    std::string exe_path = normalize_win_path(exe);
    std::string stdout_native = normalize_win_path(stdout_path);
    argv.reserve(args.size() + 2u);
    argv.push_back(exe_path.c_str());
    for (i = 0u; i < args.size(); ++i) {
        argv.push_back(args[i].c_str());
    }
    argv.push_back(0);
    if (!stdout_path.empty()) {
        out = std::fopen(stdout_native.c_str(), "wb");
        if (!out) {
            return 0;
        }
        saved_fd = _dup(_fileno(stdout));
        if (saved_fd == -1) {
            std::fclose(out);
            return 0;
        }
        if (_dup2(_fileno(out), _fileno(stdout)) != 0) {
            _close(saved_fd);
            std::fclose(out);
            return 0;
        }
    }
    code = _spawnvp(_P_WAIT, exe_path.c_str(), &argv[0]);
    if (!stdout_path.empty()) {
        std::fflush(stdout);
        _dup2(saved_fd, _fileno(stdout));
        _close(saved_fd);
        std::fclose(out);
    }
    return code == 0;
#else
    std::string cmd = quote_arg(exe);
    size_t i;
    for (i = 0u; i < args.size(); ++i) {
        cmd += " ";
        cmd += quote_arg(args[i]);
    }
    if (!stdout_path.empty()) {
        cmd += " > ";
        cmd += quote_arg(stdout_path);
    }
    return std::system(cmd.c_str()) == 0;
#endif
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

static int copy_fixture_set(const std::string &fixtures_root,
                            const std::string &sandbox_root) {
    static const char *k_files[] = {
        "manifest_v1.tlv",
        "manifest_v2.tlv",
        "request_quick.tlv",
        "request_custom.tlv",
        "payloads/v1/base.bin",
        "payloads/v1/extras.bin",
        "payloads/v2/base.bin",
        "payloads/v2/extras.bin"
    };
    size_t i;
    for (i = 0u; i < sizeof(k_files) / sizeof(k_files[0]); ++i) {
        std::string src = join_path(fixtures_root, k_files[i]);
        std::string dst = join_path(sandbox_root, k_files[i]);
        if (!copy_file(src, dst)) {
            return 0;
        }
    }
    return 1;
}

static int compare_or_update(const std::string &actual,
                             const std::string &golden,
                             int update) {
    if (update) {
        return copy_file(actual, golden);
    }
    return compare_files(actual, golden);
}

int main(int argc, char **argv) {
    if (argc < 5) {
        std::fprintf(stderr,
                     "usage: test_cli_golden <dominium-setup> <fixtures_root> <golden_root> <sandbox_root> [--update]\n");
        return 1;
    }
    std::string exe = argv[1];
    std::string fixtures_root = argv[2];
    std::string golden_root = argv[3];
    std::string sandbox_root = argv[4];
    int update = (argc > 5 && std::strcmp(argv[5], "--update") == 0) ? 1 : 0;
#if defined(_WIN32)
    exe = normalize_win_path(exe);
    fixtures_root = normalize_win_path(fixtures_root);
    golden_root = normalize_win_path(golden_root);
    sandbox_root = normalize_win_path(sandbox_root);
#endif
    std::string out_dir = join_path(sandbox_root, "out");
    std::string exe_local = join_path(sandbox_root, "dominium-setup.exe");
    std::string plan_json = join_path(out_dir, "cli_plan.json");
    std::string apply_json = join_path(out_dir, "cli_apply_dry_run.json");
    std::string status_json = join_path(out_dir, "cli_status.json");
    std::string verify_json = join_path(out_dir, "cli_verify.json");
    std::string audit_dump = join_path(out_dir, "audit_dump.json");
    std::string state_dump = join_path(out_dir, "state_dump.json");
    std::string doctor_json = join_path(out_dir, "cli_doctor.json");
    std::string explain_json = join_path(out_dir, "cli_explain_refusal.json");

    remove_dir_recursive(sandbox_root);
    if (!make_dir_recursive(out_dir)) {
        return fail("failed to create sandbox output dir");
    }
    if (!copy_fixture_set(fixtures_root, sandbox_root)) {
        return fail("failed to copy fixtures");
    }
    if (!copy_file(exe, exe_local)) {
        return fail("failed to stage dominium-setup");
    }

    {
        std::vector<std::string> args;
        args.push_back("plan");
        args.push_back("--manifest");
        args.push_back("manifest_v1.tlv");
        args.push_back("--request");
        args.push_back("request_quick.tlv");
        args.push_back("--out-plan");
        args.push_back("out/plan.tlv");
        args.push_back("--json");
        args.push_back("--use-fake-services");
        args.push_back(sandbox_root);
        args.push_back("--platform");
        args.push_back("win32_nt5");
        if (!run_cli(exe_local, args, plan_json)) {
            return fail("plan command failed");
        }
    }
    {
        std::vector<std::string> args;
        args.push_back("apply");
        args.push_back("--plan");
        args.push_back("out/plan.tlv");
        args.push_back("--out-state");
        args.push_back("out/state.tlv");
        args.push_back("--out-audit");
        args.push_back("out/audit.tlv");
        args.push_back("--out-journal");
        args.push_back("out/journal.tlv");
        args.push_back("--dry-run");
        args.push_back("--json");
        args.push_back("--use-fake-services");
        args.push_back(sandbox_root);
        args.push_back("--platform");
        args.push_back("win32_nt5");
        if (!run_cli(exe_local, args, apply_json)) {
            return fail("apply dry-run command failed");
        }
    }
    {
        std::vector<std::string> args;
        args.push_back("apply");
        args.push_back("--plan");
        args.push_back("out/plan.tlv");
        args.push_back("--out-state");
        args.push_back("out/state.tlv");
        args.push_back("--out-audit");
        args.push_back("out/audit.tlv");
        args.push_back("--out-journal");
        args.push_back("out/journal.tlv");
        args.push_back("--use-fake-services");
        args.push_back(sandbox_root);
        args.push_back("--platform");
        args.push_back("win32_nt5");
        if (!run_cli(exe_local, args, std::string())) {
            return fail("apply command failed");
        }
    }
    {
        std::vector<std::string> args;
        args.push_back("status");
        args.push_back("--journal");
        args.push_back("out/journal.tlv");
        args.push_back("--json");
        args.push_back("--use-fake-services");
        args.push_back(sandbox_root);
        args.push_back("--platform");
        args.push_back("win32_nt5");
        if (!run_cli(exe_local, args, status_json)) {
            return fail("status command failed");
        }
    }
    {
        std::vector<std::string> args;
        args.push_back("verify");
        args.push_back("--state");
        args.push_back("out/state.tlv");
        args.push_back("--format");
        args.push_back("json");
        args.push_back("--json");
        args.push_back("--use-fake-services");
        args.push_back(sandbox_root);
        args.push_back("--platform");
        args.push_back("win32_nt5");
        if (!run_cli(exe_local, args, verify_json)) {
            return fail("verify command failed");
        }
    }
    {
        std::vector<std::string> args;
        args.push_back("audit");
        args.push_back("dump");
        args.push_back("--in");
        args.push_back("out/audit.tlv");
        args.push_back("--out");
        args.push_back("out/audit_dump.json");
        args.push_back("--format");
        args.push_back("json");
        args.push_back("--json");
        args.push_back("--use-fake-services");
        args.push_back(sandbox_root);
        args.push_back("--platform");
        args.push_back("win32_nt5");
        if (!run_cli(exe_local, args, std::string())) {
            return fail("audit dump command failed");
        }
    }
    {
        std::vector<std::string> args;
        args.push_back("state");
        args.push_back("dump");
        args.push_back("--in");
        args.push_back("out/state.tlv");
        args.push_back("--out");
        args.push_back("out/state_dump.json");
        args.push_back("--format");
        args.push_back("json");
        args.push_back("--json");
        args.push_back("--use-fake-services");
        args.push_back(sandbox_root);
        args.push_back("--platform");
        args.push_back("win32_nt5");
        if (!run_cli(exe_local, args, std::string())) {
            return fail("state dump command failed");
        }
    }
    {
        std::vector<std::string> args;
        args.push_back("doctor");
        args.push_back("--state");
        args.push_back("out/state.tlv");
        args.push_back("--plan");
        args.push_back("out/plan.tlv");
        args.push_back("--journal");
        args.push_back("out/journal.tlv");
        args.push_back("--txn-journal");
        args.push_back("out/journal.tlv.txn.tlv");
        args.push_back("--audit");
        args.push_back("out/audit.tlv");
        args.push_back("--json");
        args.push_back("--use-fake-services");
        args.push_back(sandbox_root);
        args.push_back("--platform");
        args.push_back("win32_nt5");
        if (!run_cli(exe_local, args, doctor_json)) {
            return fail("doctor command failed");
        }
    }
    {
        std::vector<std::string> args;
        args.push_back("explain-refusal");
        args.push_back("--audit");
        args.push_back("out/audit.tlv");
        args.push_back("--json");
        args.push_back("--use-fake-services");
        args.push_back(sandbox_root);
        args.push_back("--platform");
        args.push_back("win32_nt5");
        if (!run_cli(exe_local, args, explain_json)) {
            return fail("explain-refusal command failed");
        }
    }

    if (!compare_or_update(plan_json, join_path(golden_root, "cli_plan.json"), update)) {
        return fail("plan json mismatch");
    }
    if (!compare_or_update(apply_json, join_path(golden_root, "cli_apply_dry_run.json"), update)) {
        return fail("apply json mismatch");
    }
    if (!compare_or_update(status_json, join_path(golden_root, "cli_status.json"), update)) {
        return fail("status json mismatch");
    }
    if (!compare_or_update(verify_json, join_path(golden_root, "cli_verify.json"), update)) {
        return fail("verify json mismatch");
    }
    if (!compare_or_update(audit_dump, join_path(golden_root, "cli_audit_dump.json"), update)) {
        return fail("audit dump mismatch");
    }
    if (!compare_or_update(state_dump, join_path(golden_root, "cli_state_dump.json"), update)) {
        return fail("state dump mismatch");
    }
    if (!compare_or_update(doctor_json, join_path(golden_root, "cli_doctor.json"), update)) {
        return fail("doctor json mismatch");
    }
    if (!compare_or_update(explain_json, join_path(golden_root, "cli_explain_refusal.json"), update)) {
        return fail("explain-refusal json mismatch");
    }
    return 0;
}
