#include "dsk/dsk_error.h"
#include "dsk/dsk_plan.h"
#include "dsk/dsk_contracts.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>

#if defined(_WIN32)
#include <direct.h>
#include <io.h>
#include <process.h>
#include <sys/stat.h>
#include <errno.h>
#include <windows.h>
#else
#include <dirent.h>
#include <errno.h>
#include <sys/stat.h>
#include <unistd.h>
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

static int is_drive_prefix(const std::string &path) {
#if defined(_WIN32)
    return path.size() == 2u && path[1] == ':';
#else
    (void)path;
    return 0;
#endif
}

static int is_drive_root(const std::string &path) {
#if defined(_WIN32)
    return path.size() == 3u && path[1] == ':' && (path[2] == '\\' || path[2] == '/');
#else
    (void)path;
    return 0;
#endif
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
            if (!current.empty() && !is_drive_prefix(current) && !is_drive_root(current)) {
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

static std::string base_name(const std::string &path) {
    size_t pos = path.find_last_of("/\\");
    if (pos == std::string::npos) {
        return path;
    }
    return path.substr(pos + 1u);
}

static std::string normalize_path(const std::string &value) {
#if defined(_WIN32)
    std::string out = value;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '/') {
            out[i] = '\\';
        }
    }
    if (!out.empty()) {
        char short_buf[4096];
        DWORD n = GetShortPathNameA(out.c_str(), short_buf, (DWORD)sizeof(short_buf));
        if (n > 0 && n < sizeof(short_buf)) {
            return std::string(short_buf);
        }
    }
    return out;
#else
    return value;
#endif
}

static std::string relative_to_cwd(const std::string &value) {
#if defined(_WIN32)
    char cwd_buf[4096];
    DWORD n = GetCurrentDirectoryA((DWORD)sizeof(cwd_buf), cwd_buf);
    if (n == 0 || n >= (DWORD)sizeof(cwd_buf)) {
        return value;
    }
    {
        std::string cwd = normalize_path(cwd_buf);
        std::string path = normalize_path(value);
        if (path.size() <= cwd.size()) {
            return value;
        }
        if (_strnicmp(path.c_str(), cwd.c_str(), cwd.size()) != 0) {
            return value;
        }
        size_t off = cwd.size();
        if (path[off] == '\\' || path[off] == '/') {
            ++off;
        }
        return path.substr(off);
    }
#else
    char cwd_buf[4096];
    if (!getcwd(cwd_buf, sizeof(cwd_buf))) {
        return value;
    }
    {
        std::string cwd = cwd_buf;
        if (value.size() <= cwd.size()) {
            return value;
        }
        if (value.compare(0, cwd.size(), cwd) != 0) {
            return value;
        }
        size_t off = cwd.size();
        if (value[off] == '/') {
            ++off;
        }
        return value.substr(off);
    }
#endif
}

static int read_file(const std::string &path, std::vector<unsigned char> &out) {
    std::FILE *in = std::fopen(path.c_str(), "rb");
    long size;
    if (!in) {
        return 0;
    }
    std::fseek(in, 0, SEEK_END);
    size = std::ftell(in);
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
    if (!read_file(src, data)) {
        return 0;
    }
    return write_file(dst, data);
}

static int copy_fixture_set(const std::string &fixtures_root,
                            const std::string &sandbox_root) {
    static const char *k_files[] = {
        "manifest_v1.tlv",
        "request_quick.tlv",
        "payloads/v1/base.bin",
        "payloads/v1/extras.bin"
    };
    size_t i;
    for (i = 0u; i < sizeof(k_files) / sizeof(k_files[0]); ++i) {
        std::string src = join_path(fixtures_root, k_files[i]);
        std::string dst = join_path(sandbox_root, k_files[i]);
        std::string dir = dst;
        size_t pos = dir.find_last_of("/\\");
        if (pos != std::string::npos) {
            dir = dir.substr(0u, pos);
            if (!make_dir_recursive(dir)) {
                return 0;
            }
        }
        if (!copy_file(src, dst)) {
            return 0;
        }
    }
    return 1;
}

static int string_list_contains(const std::vector<std::string> &list,
                                const std::string &value) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i] == value) {
            return 1;
        }
    }
    return 0;
}

static int load_manifest(const std::string &path, dsk_manifest_t *out) {
    std::vector<unsigned char> bytes;
    dsk_status_t st;
    if (!out) {
        return 0;
    }
    if (!read_file(path, bytes)) {
        return 0;
    }
    dsk_manifest_clear(out);
    st = dsk_manifest_parse(bytes.empty() ? 0 : &bytes[0],
                            (dsk_u32)bytes.size(),
                            out);
    return dsk_error_is_ok(st);
}

static int write_manifest(const std::string &path, const dsk_manifest_t &manifest) {
    dsk_tlv_buffer_t buf;
    dsk_status_t st;
    std::vector<unsigned char> data;
    std::memset(&buf, 0, sizeof(buf));
    st = dsk_manifest_write(&manifest, &buf);
    if (!dsk_error_is_ok(st)) {
        dsk_tlv_buffer_free(&buf);
        return 0;
    }
    if (buf.data && buf.size) {
        data.assign(buf.data, buf.data + buf.size);
    }
    dsk_tlv_buffer_free(&buf);
    return write_file(path, data);
}

static int derive_manifest_for_target(const std::string &src,
                                      const std::string &dst,
                                      const std::string &target,
                                      const std::string &splat) {
    dsk_manifest_t manifest;
    size_t i;
    if (!load_manifest(src, &manifest)) {
        return 0;
    }
    if (!string_list_contains(manifest.supported_targets, target)) {
        manifest.supported_targets.push_back(target);
    }
    if (!manifest.allowed_splats.empty() &&
        !string_list_contains(manifest.allowed_splats, splat)) {
        manifest.allowed_splats.push_back(splat);
    }
    for (i = 0u; i < manifest.components.size(); ++i) {
        std::vector<std::string> &targets = manifest.components[i].supported_targets;
        if (!targets.empty() && !string_list_contains(targets, target)) {
            targets.push_back(target);
        }
    }
    return write_manifest(dst, manifest);
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

static int run_cmd(const std::string &exe, const std::vector<std::string> &args) {
#if defined(_WIN32)
    std::vector<const char *> argv;
    std::string exe_name = base_name(exe);
    size_t i;
    argv.reserve(args.size() + 2u);
    argv.push_back(exe_name.c_str());
    for (i = 0u; i < args.size(); ++i) {
        argv.push_back(args[i].c_str());
    }
    argv.push_back(0);
    return _spawnv(_P_WAIT, exe.c_str(), &argv[0]);
#else
    std::string cmd = quote_arg(exe);
    size_t i;
    for (i = 0u; i < args.size(); ++i) {
        cmd += " ";
        cmd += quote_arg(args[i]);
    }
    return std::system(cmd.c_str());
#endif
}

static int files_equal(const std::string &left, const std::string &right) {
    std::vector<unsigned char> a;
    std::vector<unsigned char> b;
    if (!read_file(left, a) || !read_file(right, b)) {
        return 0;
    }
    return (a.size() == b.size() &&
            (a.empty() || std::memcmp(&a[0], &b[0], a.size()) == 0));
}

static int read_text(const std::string &path, std::string &out) {
    std::ifstream in(path.c_str(), std::ios::in | std::ios::binary);
    if (!in) {
        return 0;
    }
    std::string data;
    in.seekg(0, std::ios::end);
    std::streamoff size = in.tellg();
    if (size < 0) {
        return 0;
    }
    in.seekg(0, std::ios::beg);
    data.resize((size_t)size);
    if (size > 0) {
        in.read(&data[0], size);
    }
    out.swap(data);
    return in.good() || in.eof();
}

static int require_marker(const std::string &path, const char *marker) {
    std::string data;
    if (!read_text(path, data)) {
        return fail("unable to read parity lock matrix");
    }
    if (!marker || !marker[0]) {
        return fail("invalid marker");
    }
    if (data.find(marker) == std::string::npos) {
        std::fprintf(stderr, "FAIL: missing marker '%s' in %s\n", marker, path.c_str());
        return 1;
    }
    return 0;
}

static int check_parity_lock_matrix(const std::string &repo_root) {
    std::string path = join_path(repo_root, "docs/specs/setup/PARITY_LOCK_MATRIX.md");
    if (require_marker(path, "adapter=cli") != 0) return 1;
    if (require_marker(path, "adapter=tui") != 0) return 1;
    if (require_marker(path, "adapter=windows_exe") != 0) return 1;
    if (require_marker(path, "adapter=windows_msi") != 0) return 1;
    if (require_marker(path, "adapter=macos_pkg") != 0) return 1;
    if (require_marker(path, "adapter=linux_deb") != 0) return 1;
    if (require_marker(path, "adapter=linux_rpm") != 0) return 1;
    if (require_marker(path, "adapter=steam") != 0) return 1;
    if (require_marker(path, "wrapper_no_request") != 0) return 1;
    if (require_marker(path, "steam_manifest_target") != 0) return 1;
    return 0;
}

static int plan_digest_for_request(const std::string &cli,
                                   const std::string &manifest_path,
                                   const std::string &request_path,
                                   const std::string &plan_path,
                                   const std::string &sandbox_root,
                                   const std::string &platform,
                                   dsk_u64 *out_digest) {
    std::vector<std::string> args;
    dsk_plan_t plan;
    std::vector<unsigned char> bytes;
    dsk_status_t st;
    if (!out_digest) return 0;
    args.push_back("plan");
    args.push_back("--manifest");
    args.push_back(manifest_path);
    args.push_back("--request");
    args.push_back(request_path);
    args.push_back("--out-plan");
    args.push_back(plan_path);
    args.push_back("--use-fake-services");
    args.push_back(sandbox_root);
    args.push_back("--platform");
    args.push_back(platform);
    if (run_cmd(cli, args) != 0) {
        return 0;
    }
    if (!read_file(plan_path, bytes)) {
        return 0;
    }
    dsk_plan_clear(&plan);
    st = dsk_plan_parse(bytes.empty() ? 0 : &bytes[0], (dsk_u32)bytes.size(), &plan);
    if (!dsk_error_is_ok(st)) {
        return 0;
    }
    *out_digest = plan.plan_digest64;
    return 1;
}

static int request_equivalence_across_adapters(const std::string &cli,
                                               const std::string &tui,
                                               const std::string &steam,
                                               const std::string &win_exe,
                                               const std::string &fixtures_root,
                                               const std::string &sandbox_root,
                                               const std::string &repo_root) {
    std::string work_dir = join_path(sandbox_root, "parity_requests");
    std::string manifest_path = join_path(work_dir, "manifest_v1.tlv");
    std::string manifest_steam = join_path(work_dir, "manifest_steam.tlv");
    std::string cli_request = join_path(work_dir, "cli_request.tlv");
    std::string tui_request = join_path(work_dir, "tui_request.tlv");
    std::string frontend_id = "parity-lock";
    std::string platform = "win32_nt5";

    if (check_parity_lock_matrix(repo_root) != 0) {
        return 1;
    }
    remove_dir_recursive(work_dir);
    if (!make_dir_recursive(work_dir)) {
        return fail("failed to create parity lock sandbox");
    }
    if (!copy_fixture_set(fixtures_root, work_dir)) {
        return fail("failed to copy fixtures");
    }
    if (!steam.empty() && steam != "none") {
        if (!derive_manifest_for_target(manifest_path, manifest_steam, "steam", "splat_steam")) {
            return fail("failed to derive steam manifest");
        }
    }

    {
        std::vector<std::string> args;
        args.push_back("request");
        args.push_back("make");
        args.push_back("--manifest");
        args.push_back(manifest_path);
        args.push_back("--op");
        args.push_back("install");
        args.push_back("--scope");
        args.push_back("user");
        args.push_back("--ui-mode");
        args.push_back("tui");
        args.push_back("--frontend-id");
        args.push_back(frontend_id);
        args.push_back("--platform");
        args.push_back(platform);
        args.push_back("--out-request");
        args.push_back(cli_request);
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--use-fake-services");
        args.push_back(work_dir);
        if (run_cmd(cli, args) != 0) {
            return fail("cli request make failed");
        }
    }
    {
        std::vector<std::string> args;
        args.push_back("--manifest");
        args.push_back(manifest_path);
        args.push_back("--defaults");
        args.push_back("--yes");
        args.push_back("--out-request");
        args.push_back(tui_request);
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--use-fake-services");
        args.push_back(work_dir);
        args.push_back("--platform");
        args.push_back(platform);
        args.push_back("--frontend-id");
        args.push_back(frontend_id);
        if (run_cmd(tui, args) != 0) {
            return fail("tui request make failed");
        }
    }
    if (!files_equal(cli_request, tui_request)) {
        return fail("cli vs tui request mismatch");
    }

    if (!win_exe.empty() && win_exe != "none") {
        std::string cli_request_win = join_path(work_dir, "cli_request_win.tlv");
        std::string adapter_request = join_path(work_dir, "win_request.tlv");
        std::vector<std::string> args;
        args.push_back("request");
        args.push_back("make");
        args.push_back("--manifest");
        args.push_back(manifest_path);
        args.push_back("--op");
        args.push_back("install");
        args.push_back("--scope");
        args.push_back("user");
        args.push_back("--ui-mode");
        args.push_back("cli");
        args.push_back("--frontend-id");
        args.push_back(frontend_id);
        args.push_back("--platform");
        args.push_back(platform);
        args.push_back("--out-request");
        args.push_back(cli_request_win);
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--use-fake-services");
        args.push_back(work_dir);
        if (run_cmd(cli, args) != 0) {
            return fail("cli request make (win) failed");
        }

        args.clear();
        args.push_back("--cli");
        args.push_back("request-make");
        args.push_back("--manifest");
        args.push_back(manifest_path);
        args.push_back("--op");
        args.push_back("install");
        args.push_back("--scope");
        args.push_back("user");
        args.push_back("--frontend-id");
        args.push_back(frontend_id);
        args.push_back("--platform");
        args.push_back(platform);
        args.push_back("--out-request");
        args.push_back(adapter_request);
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--use-fake-services");
        args.push_back(work_dir);
        args.push_back("--setup-cli");
        args.push_back(cli);
        if (run_cmd(win_exe, args) != 0) {
            return fail("windows exe request make failed");
        }
        if (!files_equal(cli_request_win, adapter_request)) {
            return fail("cli vs windows exe request mismatch");
        }
    }

    if (!steam.empty() && steam != "none") {
        std::string cli_request_steam = join_path(work_dir, "cli_request_steam.tlv");
        std::string adapter_request = join_path(work_dir, "steam_request.tlv");
        std::vector<std::string> args;
        args.push_back("request");
        args.push_back("make");
        args.push_back("--manifest");
        args.push_back(manifest_steam);
        args.push_back("--op");
        args.push_back("install");
        args.push_back("--scope");
        args.push_back("user");
        args.push_back("--ui-mode");
        args.push_back("cli");
        args.push_back("--frontend-id");
        args.push_back(frontend_id);
        args.push_back("--requested-splat");
        args.push_back("splat_steam");
        args.push_back("--ownership");
        args.push_back("steam");
        args.push_back("--platform");
        args.push_back("steam");
        args.push_back("--out-request");
        args.push_back(cli_request_steam);
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--use-fake-services");
        args.push_back(work_dir);
        if (run_cmd(cli, args) != 0) {
            return fail("cli request make (steam) failed");
        }

        args.clear();
        args.push_back("request-make");
        args.push_back("--manifest");
        args.push_back(manifest_steam);
        args.push_back("--op");
        args.push_back("install");
        args.push_back("--scope");
        args.push_back("user");
        args.push_back("--frontend-id");
        args.push_back(frontend_id);
        args.push_back("--platform");
        args.push_back("steam");
        args.push_back("--out-request");
        args.push_back(adapter_request);
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--use-fake-services");
        args.push_back(work_dir);
        args.push_back("--setup-cli");
        args.push_back(cli);
        if (run_cmd(steam, args) != 0) {
            return fail("steam request make failed");
        }
        if (!files_equal(cli_request_steam, adapter_request)) {
            return fail("cli vs steam request mismatch");
        }
    }

    return 0;
}

static int plan_digest_equivalence_across_adapters(const std::string &cli,
                                                   const std::string &tui,
                                                   const std::string &steam,
                                                   const std::string &win_exe,
                                                   const std::string &fixtures_root,
                                                   const std::string &sandbox_root,
                                                   const std::string &repo_root) {
    std::string work_dir = join_path(sandbox_root, "parity_plans");
    std::string manifest_path = join_path(work_dir, "manifest_v1.tlv");
    std::string manifest_steam = join_path(work_dir, "manifest_steam.tlv");
    std::string cli_request = join_path(work_dir, "cli_request.tlv");
    std::string tui_request = join_path(work_dir, "tui_request.tlv");
    std::string frontend_id = "parity-lock";
    std::string platform = "win32_nt5";
    dsk_u64 digest_cli = 0u;
    dsk_u64 digest_tui = 0u;

    remove_dir_recursive(work_dir);
    if (!make_dir_recursive(work_dir)) {
        return fail("failed to create parity plan sandbox");
    }
    if (!copy_fixture_set(fixtures_root, work_dir)) {
        return fail("failed to copy fixtures");
    }
    if (check_parity_lock_matrix(repo_root) != 0) {
        return 1;
    }
    if (!steam.empty() && steam != "none") {
        if (!derive_manifest_for_target(manifest_path, manifest_steam, "steam", "splat_steam")) {
            return fail("failed to derive steam manifest");
        }
    }

    {
        std::vector<std::string> args;
        args.push_back("request");
        args.push_back("make");
        args.push_back("--manifest");
        args.push_back(manifest_steam);
        args.push_back("--op");
        args.push_back("install");
        args.push_back("--scope");
        args.push_back("user");
        args.push_back("--ui-mode");
        args.push_back("tui");
        args.push_back("--frontend-id");
        args.push_back(frontend_id);
        args.push_back("--platform");
        args.push_back(platform);
        args.push_back("--out-request");
        args.push_back(cli_request);
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--use-fake-services");
        args.push_back(work_dir);
        if (run_cmd(cli, args) != 0) {
            return fail("cli request make failed");
        }
    }
    {
        std::vector<std::string> args;
        args.push_back("--manifest");
        args.push_back(manifest_path);
        args.push_back("--defaults");
        args.push_back("--yes");
        args.push_back("--out-request");
        args.push_back(tui_request);
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--use-fake-services");
        args.push_back(work_dir);
        args.push_back("--platform");
        args.push_back(platform);
        args.push_back("--frontend-id");
        args.push_back(frontend_id);
        if (run_cmd(tui, args) != 0) {
            return fail("tui request make failed");
        }
    }

    if (!plan_digest_for_request(cli,
                                 manifest_path,
                                 cli_request,
                                 join_path(work_dir, "cli_plan.tlv"),
                                 work_dir,
                                 platform,
                                 &digest_cli)) {
        return fail("cli plan digest failed");
    }
    if (!plan_digest_for_request(cli,
                                 manifest_path,
                                 tui_request,
                                 join_path(work_dir, "tui_plan.tlv"),
                                 work_dir,
                                 platform,
                                 &digest_tui)) {
        return fail("tui plan digest failed");
    }
    if (digest_cli != digest_tui) {
        return fail("cli vs tui plan digest mismatch");
    }

    if (!win_exe.empty() && win_exe != "none") {
        std::string cli_request_win = join_path(work_dir, "cli_request_win.tlv");
        std::string win_request = join_path(work_dir, "win_request.tlv");
        dsk_u64 digest_win_cli = 0u;
        dsk_u64 digest_win = 0u;
        std::vector<std::string> args;
        args.push_back("request");
        args.push_back("make");
        args.push_back("--manifest");
        args.push_back(manifest_path);
        args.push_back("--op");
        args.push_back("install");
        args.push_back("--scope");
        args.push_back("user");
        args.push_back("--ui-mode");
        args.push_back("cli");
        args.push_back("--frontend-id");
        args.push_back(frontend_id);
        args.push_back("--platform");
        args.push_back(platform);
        args.push_back("--out-request");
        args.push_back(cli_request_win);
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--use-fake-services");
        args.push_back(work_dir);
        if (run_cmd(cli, args) != 0) {
            return fail("cli request make (win) failed");
        }

        args.clear();
        args.push_back("--cli");
        args.push_back("request-make");
        args.push_back("--manifest");
        args.push_back(manifest_path);
        args.push_back("--op");
        args.push_back("install");
        args.push_back("--scope");
        args.push_back("user");
        args.push_back("--frontend-id");
        args.push_back(frontend_id);
        args.push_back("--platform");
        args.push_back(platform);
        args.push_back("--out-request");
        args.push_back(win_request);
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--use-fake-services");
        args.push_back(work_dir);
        args.push_back("--setup-cli");
        args.push_back(cli);
        if (run_cmd(win_exe, args) != 0) {
            return fail("windows exe request make failed");
        }

        if (!plan_digest_for_request(cli,
                                     manifest_path,
                                     cli_request_win,
                                     join_path(work_dir, "cli_plan_win.tlv"),
                                     work_dir,
                                     platform,
                                     &digest_win_cli)) {
            return fail("cli win plan digest failed");
        }
        if (!plan_digest_for_request(cli,
                                     manifest_path,
                                     win_request,
                                     join_path(work_dir, "win_plan.tlv"),
                                     work_dir,
                                     platform,
                                     &digest_win)) {
            return fail("win plan digest failed");
        }
        if (digest_win_cli != digest_win) {
            return fail("cli vs windows exe plan digest mismatch");
        }
    }

    if (!steam.empty() && steam != "none") {
        std::string cli_request_steam = join_path(work_dir, "cli_request_steam.tlv");
        std::string steam_request = join_path(work_dir, "steam_request.tlv");
        dsk_u64 digest_cli_steam = 0u;
        dsk_u64 digest_steam = 0u;
        std::vector<std::string> args;
        args.push_back("request");
        args.push_back("make");
        args.push_back("--manifest");
        args.push_back(manifest_path);
        args.push_back("--op");
        args.push_back("install");
        args.push_back("--scope");
        args.push_back("user");
        args.push_back("--ui-mode");
        args.push_back("cli");
        args.push_back("--frontend-id");
        args.push_back(frontend_id);
        args.push_back("--requested-splat");
        args.push_back("splat_steam");
        args.push_back("--ownership");
        args.push_back("steam");
        args.push_back("--platform");
        args.push_back("steam");
        args.push_back("--out-request");
        args.push_back(cli_request_steam);
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--use-fake-services");
        args.push_back(work_dir);
        if (run_cmd(cli, args) != 0) {
            return fail("cli request make (steam) failed");
        }

        args.clear();
        args.push_back("request-make");
        args.push_back("--manifest");
        args.push_back(manifest_steam);
        args.push_back("--op");
        args.push_back("install");
        args.push_back("--scope");
        args.push_back("user");
        args.push_back("--frontend-id");
        args.push_back(frontend_id);
        args.push_back("--platform");
        args.push_back("steam");
        args.push_back("--out-request");
        args.push_back(steam_request);
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--use-fake-services");
        args.push_back(work_dir);
        args.push_back("--setup-cli");
        args.push_back(cli);
        if (run_cmd(steam, args) != 0) {
            return fail("steam request make failed");
        }

        if (!plan_digest_for_request(cli,
                                     manifest_steam,
                                     cli_request_steam,
                                     join_path(work_dir, "cli_plan_steam.tlv"),
                                     work_dir,
                                     "steam",
                                     &digest_cli_steam)) {
            return fail("cli steam plan digest failed");
        }
        if (!plan_digest_for_request(cli,
                                     manifest_steam,
                                     steam_request,
                                     join_path(work_dir, "steam_plan.tlv"),
                                     work_dir,
                                     "steam",
                                     &digest_steam)) {
            return fail("steam plan digest failed");
        }
        if (digest_cli_steam != digest_steam) {
            return fail("cli vs steam plan digest mismatch");
        }
    }

    return 0;
}

static int refusal_code_equivalence(const std::string &cli,
                                    const std::string &tui,
                                    const std::string &fixtures_root,
                                    const std::string &sandbox_root) {
    std::string work_dir = join_path(sandbox_root, "parity_refusal");
    std::string invalid_manifest = join_path(work_dir, "invalid_manifest.tlv");
    std::string out_request = join_path(work_dir, "invalid_request.tlv");
    std::string work_dir_rel;
    std::string invalid_manifest_rel;
    std::string out_request_rel;
    std::vector<unsigned char> empty;
    int rc_cli;
    int rc_tui;

    remove_dir_recursive(work_dir);
    if (!make_dir_recursive(work_dir)) {
        return fail("failed to create refusal sandbox");
    }
    if (!copy_fixture_set(fixtures_root, work_dir)) {
        return fail("failed to copy fixtures");
    }
    if (!write_file(invalid_manifest, empty)) {
        return fail("failed to write invalid manifest");
    }
    work_dir_rel = relative_to_cwd(work_dir);
    invalid_manifest_rel = relative_to_cwd(invalid_manifest);
    out_request_rel = relative_to_cwd(out_request);

    {
        std::vector<std::string> args;
        args.push_back("request");
        args.push_back("make");
        args.push_back("--manifest");
        args.push_back(invalid_manifest_rel);
        args.push_back("--op");
        args.push_back("install");
        args.push_back("--scope");
        args.push_back("user");
        args.push_back("--ui-mode");
        args.push_back("tui");
        args.push_back("--frontend-id");
        args.push_back("parity-lock");
        args.push_back("--platform");
        args.push_back("win32_nt5");
        args.push_back("--out-request");
        args.push_back(out_request_rel);
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--use-fake-services");
        args.push_back(work_dir_rel);
        rc_cli = run_cmd(cli, args);
    }
    {
        std::vector<std::string> args;
        args.push_back("--manifest");
        args.push_back(invalid_manifest_rel);
        args.push_back("--defaults");
        args.push_back("--yes");
        args.push_back("--out-request");
        args.push_back(out_request_rel);
        args.push_back("--deterministic");
        args.push_back("1");
        args.push_back("--use-fake-services");
        args.push_back(work_dir_rel);
        args.push_back("--platform");
        args.push_back("win32_nt5");
        args.push_back("--frontend-id");
        args.push_back("parity-lock");
        rc_tui = run_cmd(tui, args);
    }
    if (rc_cli != rc_tui) {
        std::fprintf(stderr, "FAIL: refusal codes mismatch cli=%d tui=%d\n", rc_cli, rc_tui);
        return 1;
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 7) {
        std::fprintf(stderr,
                     "usage: setup_parity_lock_tests <test> <cli> <tui> <fixtures_root> <sandbox_root> <repo_root> [steam] [win_exe]\n");
        return 1;
    }
    std::string test = argv[1];
    std::string cli = normalize_path(argv[2]);
    std::string tui = normalize_path(argv[3]);
    std::string fixtures_root = normalize_path(argv[4]);
    std::string sandbox_root = normalize_path(argv[5]);
    std::string repo_root = normalize_path(argv[6]);
    std::string steam = (argc > 7) ? normalize_path(argv[7]) : "";
    std::string win_exe = (argc > 8) ? normalize_path(argv[8]) : "";

    if (test == "request_equivalence_across_adapters") {
        return request_equivalence_across_adapters(cli,
                                                   tui,
                                                   steam,
                                                   win_exe,
                                                   fixtures_root,
                                                   sandbox_root,
                                                   repo_root);
    }
    if (test == "plan_digest_equivalence_across_adapters") {
        return plan_digest_equivalence_across_adapters(cli,
                                                       tui,
                                                       steam,
                                                       win_exe,
                                                       fixtures_root,
                                                       sandbox_root,
                                                       repo_root);
    }
    if (test == "refusal_code_equivalence") {
        return refusal_code_equivalence(cli, tui, fixtures_root, sandbox_root);
    }
    std::fprintf(stderr, "unknown test: %s\n", test.c_str());
    return 1;
}
