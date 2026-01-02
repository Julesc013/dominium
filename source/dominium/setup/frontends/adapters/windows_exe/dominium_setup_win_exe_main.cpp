#include <windows.h>
#include <process.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

namespace {

enum dsk_win_mode_t {
    DSK_WIN_MODE_GUI = 1,
    DSK_WIN_MODE_TUI = 2,
    DSK_WIN_MODE_CLI = 3
};

static bool dsk_has_flag(int argc, char **argv, const char *flag) {
    int i;
    if (!flag) {
        return false;
    }
    for (i = 1; i < argc; ++i) {
        if (std::strcmp(argv[i], flag) == 0) {
            return true;
        }
    }
    return false;
}

static const char *dsk_get_arg_value(int argc, char **argv, const char *name) {
    int i;
    if (!name) {
        return 0;
    }
    for (i = 1; i < argc - 1; ++i) {
        if (std::strcmp(argv[i], name) == 0) {
            return argv[i + 1];
        }
    }
    return 0;
}

static const char *dsk_find_subcommand(int argc, char **argv) {
    int i;
    for (i = 1; i < argc; ++i) {
        if (argv[i][0] != '-') {
            return argv[i];
        }
    }
    return 0;
}

static std::string dsk_trim_line(const std::string &value) {
    size_t end = value.size();
    while (end > 0u && (value[end - 1u] == '\n' || value[end - 1u] == '\r')) {
        --end;
    }
    if (end == value.size()) {
        return value;
    }
    return value.substr(0u, end);
}

static std::string dsk_prompt(const char *label, const char *fallback) {
    char buffer[256];
    std::printf("%s [%s]: ", label, fallback ? fallback : "");
    std::fflush(stdout);
    if (!std::fgets(buffer, sizeof(buffer), stdin)) {
        return fallback ? fallback : "";
    }
    {
        std::string value = dsk_trim_line(buffer);
        if (value.empty()) {
            return fallback ? fallback : "";
        }
        return value;
    }
}

static bool dsk_file_exists(const std::string &path) {
    DWORD attrs = GetFileAttributesA(path.c_str());
    return (attrs != INVALID_FILE_ATTRIBUTES) && ((attrs & FILE_ATTRIBUTE_DIRECTORY) == 0u);
}

static std::string dsk_dirname_from_path(const std::string &path) {
    size_t i = path.find_last_of("\\/");
    if (i == std::string::npos) {
        return std::string();
    }
    return path.substr(0u, i);
}

static std::string dsk_join_path(const std::string &dir, const char *name) {
    if (dir.empty()) {
        return name ? name : "";
    }
    if (!name || !name[0]) {
        return dir;
    }
    return dir + "\\" + name;
}

static std::string dsk_find_setup_cli(int argc, char **argv) {
    const char *override_path = dsk_get_arg_value(argc, argv, "--setup-cli");
    if (override_path && override_path[0]) {
        return override_path;
    }
    {
        char module_path[MAX_PATH] = {0};
        DWORD len = GetModuleFileNameA(NULL, module_path, MAX_PATH);
        if (len > 0u && len < MAX_PATH) {
            std::string dir = dsk_dirname_from_path(module_path);
            std::string sibling = dsk_join_path(dir, "dominium-setup.exe");
            if (dsk_file_exists(sibling)) {
                return sibling;
            }
        }
    }
    return "dominium-setup";
}

static int dsk_spawn(const std::string &exe, const std::vector<std::string> &args) {
    std::vector<const char *> argv;
    size_t i;
    argv.reserve(args.size() + 2u);
    argv.push_back(exe.c_str());
    for (i = 0u; i < args.size(); ++i) {
        argv.push_back(args[i].c_str());
    }
    argv.push_back(0);
    return _spawnvp(_P_WAIT, exe.c_str(), &argv[0]);
}

static void dsk_append_kv(std::vector<std::string> &args,
                          const char *key,
                          const std::string &value) {
    if (!key || value.empty()) {
        return;
    }
    args.push_back(key);
    args.push_back(value);
}

static void dsk_append_kv_c(std::vector<std::string> &args,
                            const char *key,
                            const char *value) {
    if (!key || !value || !value[0]) {
        return;
    }
    args.push_back(key);
    args.push_back(value);
}

static std::string dsk_json_escape(const std::string &value) {
    static const char *hex = "0123456789abcdef";
    std::string out;
    size_t i;
    out.reserve(value.size() + 8u);
    for (i = 0u; i < value.size(); ++i) {
        unsigned char c = (unsigned char)value[i];
        if (c == '\\') {
            out += "\\\\";
        } else if (c == '"') {
            out += "\\\"";
        } else if (c == '\n') {
            out += "\\n";
        } else if (c == '\r') {
            out += "\\r";
        } else if (c == '\t') {
            out += "\\t";
        } else if (c < 0x20u) {
            out += "\\u00";
            out += hex[(c >> 4) & 0x0Fu];
            out += hex[c & 0x0Fu];
        } else {
            out.push_back((char)c);
        }
    }
    return out;
}

static void dsk_print_json_summary(const char *command,
                                   int status_code,
                                   const std::string &request_path,
                                   const std::string &plan_path,
                                   const std::string &state_path,
                                   const std::string &audit_path,
                                   const std::string &journal_path,
                                   const std::string &ui_mode,
                                   const std::string &frontend_id,
                                   bool dry_run) {
    const char *status = (status_code == 0) ? "ok" : "error";
    std::printf("{\"schema_version\":\"setup-adapter-1\",");
    std::printf("\"adapter\":\"windows_exe\",");
    std::printf("\"command\":\"%s\",", dsk_json_escape(command ? command : "").c_str());
    std::printf("\"status\":\"%s\",", status);
    std::printf("\"status_code\":%d,", status_code);
    std::printf("\"artifacts\":{");
    std::printf("\"request\":\"%s\",", dsk_json_escape(request_path).c_str());
    std::printf("\"plan\":\"%s\",", dsk_json_escape(plan_path).c_str());
    std::printf("\"state\":\"%s\",", dsk_json_escape(state_path).c_str());
    std::printf("\"audit\":\"%s\",", dsk_json_escape(audit_path).c_str());
    std::printf("\"journal\":\"%s\"},", dsk_json_escape(journal_path).c_str());
    std::printf("\"details\":{");
    std::printf("\"ui_mode\":\"%s\",", dsk_json_escape(ui_mode).c_str());
    std::printf("\"frontend_id\":\"%s\",", dsk_json_escape(frontend_id).c_str());
    std::printf("\"dry_run\":%s", dry_run ? "true" : "false");
    std::printf("}}\n");
}

static void dsk_print_usage(void) {
    std::printf("dominium-setup-win-exe --cli|--tui|--gui <request-make|run> [options]\n");
    std::printf("  request-make --manifest <file> --op <install|upgrade|repair|uninstall|verify|status>\n");
    std::printf("    --scope <user|system|portable> [--components <csv>] [--exclude <csv>] [--root <path>]\n");
    std::printf("    [--frontend-id <id>] [--requested-splat <id>] [--ownership <portable|pkg|steam|any>]\n");
    std::printf("    [--platform <triple>] [--payload-root <path>] [--deterministic 0|1]\n");
    std::printf("    --out-request <file> [--use-fake-services <root>] [--json]\n");
    std::printf("  run --manifest <file> --op <install|upgrade|repair|uninstall|verify|status> --scope <user|system|portable>\n");
    std::printf("    [--components <csv>] [--exclude <csv>] [--root <path>] [--frontend-id <id>]\n");
    std::printf("    [--requested-splat <id>] [--ownership <portable|pkg|steam|any>] [--platform <triple>]\n");
    std::printf("    [--payload-root <path>] [--deterministic 0|1] [--out-request <file>]\n");
    std::printf("    [--out-plan <file>] [--out-state <file>] [--out-audit <file>] [--out-journal <file>]\n");
    std::printf("    [--dry-run] [--use-fake-services <root>] [--json]\n");
}

static int dsk_run_request_make(const std::string &cli,
                                const std::string &manifest_path,
                                const std::string &op,
                                const std::string &scope,
                                const std::string &ui_mode,
                                const std::string &components,
                                const std::string &exclude,
                                const std::string &root,
                                const std::string &out_request,
                                const std::string &frontend_id,
                                const std::string &requested_splat,
                                const std::string &ownership,
                                const std::string &platform,
                                const std::string &payload_root,
                                const std::string &deterministic,
                                const std::string &fake_root) {
    std::vector<std::string> args;
    args.push_back("request");
    args.push_back("make");
    dsk_append_kv(args, "--manifest", manifest_path);
    dsk_append_kv(args, "--op", op);
    dsk_append_kv(args, "--scope", scope);
    dsk_append_kv(args, "--ui-mode", ui_mode);
    dsk_append_kv(args, "--components", components);
    dsk_append_kv(args, "--exclude", exclude);
    dsk_append_kv(args, "--root", root);
    dsk_append_kv(args, "--frontend-id", frontend_id);
    dsk_append_kv(args, "--requested-splat", requested_splat);
    dsk_append_kv(args, "--ownership", ownership);
    dsk_append_kv(args, "--platform", platform);
    dsk_append_kv(args, "--payload-root", payload_root);
    dsk_append_kv(args, "--deterministic", deterministic.empty() ? "1" : deterministic);
    dsk_append_kv(args, "--out-request", out_request);
    dsk_append_kv(args, "--use-fake-services", fake_root);
    return dsk_spawn(cli, args);
}

static int dsk_run_plan(const std::string &cli,
                        const std::string &manifest_path,
                        const std::string &request_path,
                        const std::string &out_plan,
                        const std::string &fake_root) {
    std::vector<std::string> args;
    args.push_back("plan");
    dsk_append_kv(args, "--manifest", manifest_path);
    dsk_append_kv(args, "--request", request_path);
    dsk_append_kv(args, "--out-plan", out_plan);
    dsk_append_kv(args, "--use-fake-services", fake_root);
    return dsk_spawn(cli, args);
}

static int dsk_run_apply(const std::string &cli,
                         const std::string &plan_path,
                         const std::string &out_state,
                         const std::string &out_audit,
                         const std::string &out_journal,
                         const std::string &fake_root,
                         bool dry_run) {
    std::vector<std::string> args;
    args.push_back("apply");
    dsk_append_kv(args, "--plan", plan_path);
    dsk_append_kv(args, "--out-state", out_state);
    dsk_append_kv(args, "--out-audit", out_audit);
    dsk_append_kv(args, "--out-journal", out_journal);
    if (dry_run) {
        args.push_back("--dry-run");
    }
    dsk_append_kv(args, "--use-fake-services", fake_root);
    return dsk_spawn(cli, args);
}

} // namespace

int main(int argc, char **argv) {
    dsk_win_mode_t mode = DSK_WIN_MODE_GUI;
    const char *subcommand = 0;
    std::string ui_mode = "gui";
    std::string manifest_path = dsk_get_arg_value(argc, argv, "--manifest") ? dsk_get_arg_value(argc, argv, "--manifest") : "";
    std::string op = dsk_get_arg_value(argc, argv, "--op") ? dsk_get_arg_value(argc, argv, "--op") : "";
    std::string scope = dsk_get_arg_value(argc, argv, "--scope") ? dsk_get_arg_value(argc, argv, "--scope") : "";
    std::string components = dsk_get_arg_value(argc, argv, "--components") ? dsk_get_arg_value(argc, argv, "--components") : "";
    std::string exclude = dsk_get_arg_value(argc, argv, "--exclude") ? dsk_get_arg_value(argc, argv, "--exclude") : "";
    std::string root = dsk_get_arg_value(argc, argv, "--root") ? dsk_get_arg_value(argc, argv, "--root") : "";
    std::string frontend_id = dsk_get_arg_value(argc, argv, "--frontend-id") ? dsk_get_arg_value(argc, argv, "--frontend-id") : "dominium-setup-win-exe";
    std::string requested_splat = dsk_get_arg_value(argc, argv, "--requested-splat") ? dsk_get_arg_value(argc, argv, "--requested-splat") : "";
    std::string ownership = dsk_get_arg_value(argc, argv, "--ownership") ? dsk_get_arg_value(argc, argv, "--ownership") : "";
    std::string platform = dsk_get_arg_value(argc, argv, "--platform") ? dsk_get_arg_value(argc, argv, "--platform") : "";
    std::string payload_root = dsk_get_arg_value(argc, argv, "--payload-root") ? dsk_get_arg_value(argc, argv, "--payload-root") : "";
    std::string deterministic = dsk_get_arg_value(argc, argv, "--deterministic") ? dsk_get_arg_value(argc, argv, "--deterministic") : "1";
    std::string out_request = dsk_get_arg_value(argc, argv, "--out-request") ? dsk_get_arg_value(argc, argv, "--out-request") : "install_request.tlv";
    std::string request_path = dsk_get_arg_value(argc, argv, "--request") ? dsk_get_arg_value(argc, argv, "--request") : "";
    std::string out_plan = dsk_get_arg_value(argc, argv, "--out-plan") ? dsk_get_arg_value(argc, argv, "--out-plan") : "install_plan.tlv";
    std::string plan_path = dsk_get_arg_value(argc, argv, "--plan") ? dsk_get_arg_value(argc, argv, "--plan") : "";
    std::string out_state = dsk_get_arg_value(argc, argv, "--out-state") ? dsk_get_arg_value(argc, argv, "--out-state") : "installed_state.tlv";
    std::string out_audit = dsk_get_arg_value(argc, argv, "--out-audit") ? dsk_get_arg_value(argc, argv, "--out-audit") : "setup_audit.tlv";
    std::string out_journal = dsk_get_arg_value(argc, argv, "--out-journal") ? dsk_get_arg_value(argc, argv, "--out-journal") : "job_journal.tlv";
    std::string fake_root = dsk_get_arg_value(argc, argv, "--use-fake-services") ? dsk_get_arg_value(argc, argv, "--use-fake-services") : "";
    bool dry_run = dsk_has_flag(argc, argv, "--dry-run");
    bool json = dsk_has_flag(argc, argv, "--json");
    int exit_code = 0;

    if (argc < 2 || dsk_has_flag(argc, argv, "--help")) {
        dsk_print_usage();
        return 1;
    }

    if (dsk_has_flag(argc, argv, "--cli")) {
        mode = DSK_WIN_MODE_CLI;
        ui_mode = "cli";
    } else if (dsk_has_flag(argc, argv, "--tui")) {
        mode = DSK_WIN_MODE_TUI;
        ui_mode = "tui";
    } else if (dsk_has_flag(argc, argv, "--gui")) {
        mode = DSK_WIN_MODE_GUI;
        ui_mode = "gui";
    }

    subcommand = dsk_find_subcommand(argc, argv);
    if (!subcommand) {
        dsk_print_usage();
        return 1;
    }

    if (mode == DSK_WIN_MODE_GUI) {
        MessageBoxA(0,
                    "GUI wizard is stubbed in SR-7. Falling back to console prompts.",
                    "Dominium Setup",
                    MB_OK | MB_ICONINFORMATION);
    }

    if ((mode == DSK_WIN_MODE_TUI || mode == DSK_WIN_MODE_GUI) && op.empty()) {
        op = dsk_prompt("Operation (install/upgrade/repair/uninstall/verify/status)", "install");
    }
    if ((mode == DSK_WIN_MODE_TUI || mode == DSK_WIN_MODE_GUI) && scope.empty()) {
        scope = dsk_prompt("Scope (user/system/portable)", "user");
    }
    if ((mode == DSK_WIN_MODE_TUI || mode == DSK_WIN_MODE_GUI) && root.empty()) {
        root = dsk_prompt("Install root (blank for default)", "");
    }
    if ((mode == DSK_WIN_MODE_TUI || mode == DSK_WIN_MODE_GUI) && components.empty()) {
        components = dsk_prompt("Components (csv, blank for defaults)", "");
    }
    if ((mode == DSK_WIN_MODE_TUI || mode == DSK_WIN_MODE_GUI) && exclude.empty()) {
        exclude = dsk_prompt("Exclude components (csv, blank for none)", "");
    }

    if (std::strcmp(subcommand, "request-make") == 0) {
        std::string cli = dsk_find_setup_cli(argc, argv);
        if (manifest_path.empty() || op.empty() || scope.empty()) {
            dsk_print_usage();
            return 1;
        }
        exit_code = dsk_run_request_make(cli,
                                         manifest_path,
                                         op,
                                         scope,
                                         ui_mode,
                                         components,
                                         exclude,
                                         root,
                                         out_request,
                                         frontend_id,
                                         requested_splat,
                                         ownership,
                                         platform,
                                         payload_root,
                                         deterministic,
                                         fake_root);
        if (json) {
            dsk_print_json_summary("request-make",
                                   exit_code,
                                   out_request,
                                   "",
                                   "",
                                   "",
                                   "",
                                   ui_mode,
                                   frontend_id,
                                   false);
        }
        return exit_code == -1 ? 1 : exit_code;
    }

    if (std::strcmp(subcommand, "run") == 0) {
        std::string cli = dsk_find_setup_cli(argc, argv);
        if (manifest_path.empty()) {
            dsk_print_usage();
            return 1;
        }
        if (request_path.empty()) {
            if (op.empty() || scope.empty()) {
                dsk_print_usage();
                return 1;
            }
            exit_code = dsk_run_request_make(cli,
                                             manifest_path,
                                             op,
                                             scope,
                                             ui_mode,
                                             components,
                                             exclude,
                                             root,
                                             out_request,
                                             frontend_id,
                                             requested_splat,
                                             ownership,
                                             platform,
                                             payload_root,
                                             deterministic,
                                             fake_root);
            if (exit_code != 0) {
                if (json) {
                    dsk_print_json_summary("run",
                                           exit_code,
                                           out_request,
                                           "",
                                           "",
                                           "",
                                           "",
                                           ui_mode,
                                           frontend_id,
                                           dry_run);
                }
                return exit_code == -1 ? 1 : exit_code;
            }
            request_path = out_request;
        }

        if (plan_path.empty()) {
            exit_code = dsk_run_plan(cli, manifest_path, request_path, out_plan, fake_root);
            if (exit_code != 0) {
                if (json) {
                    dsk_print_json_summary("run",
                                           exit_code,
                                           request_path,
                                           out_plan,
                                           "",
                                           "",
                                           "",
                                           ui_mode,
                                           frontend_id,
                                           dry_run);
                }
                return exit_code == -1 ? 1 : exit_code;
            }
            plan_path = out_plan;
        }

        exit_code = dsk_run_apply(cli, plan_path, out_state, out_audit, out_journal, fake_root, dry_run);
        if (json) {
            dsk_print_json_summary("run",
                                   exit_code,
                                   request_path,
                                   plan_path,
                                   out_state,
                                   out_audit,
                                   out_journal,
                                   ui_mode,
                                   frontend_id,
                                   dry_run);
        }
        return exit_code == -1 ? 1 : exit_code;
    }

    dsk_print_usage();
    return 1;
}
