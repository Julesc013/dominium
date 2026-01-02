#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#ifdef _WIN32
#include <process.h>
#endif

namespace {

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

static void dsk_append_kv(std::vector<std::string> &args,
                          const char *key,
                          const std::string &value) {
    if (!key || value.empty()) {
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
                                   const std::string &frontend_id,
                                   bool dry_run) {
    const char *status = (status_code == 0) ? "ok" : "error";
    std::printf("{\"schema_version\":\"setup-adapter-1\",");
    std::printf("\"adapter\":\"steam\",");
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
    std::printf("\"frontend_id\":\"%s\",", dsk_json_escape(frontend_id).c_str());
    std::printf("\"dry_run\":%s", dry_run ? "true" : "false");
    std::printf("}}\n");
}

#ifdef _WIN32
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
#else
static std::string dsk_quote_posix(const std::string &value) {
    std::string out = "'";
    size_t i;
    for (i = 0u; i < value.size(); ++i) {
        char c = value[i];
        if (c == '\'') {
            out += "'\\''";
        } else {
            out.push_back(c);
        }
    }
    out.push_back('\'');
    return out;
}

static int dsk_spawn(const std::string &exe, const std::vector<std::string> &args) {
    std::string cmd = dsk_quote_posix(exe);
    size_t i;
    for (i = 0u; i < args.size(); ++i) {
        cmd += " ";
        cmd += dsk_quote_posix(args[i]);
    }
    return std::system(cmd.c_str());
}
#endif

static int dsk_run_request_make(const std::string &cli,
                                const std::string &manifest_path,
                                const std::string &op,
                                const std::string &scope,
                                const std::string &root,
                                const std::string &out_request,
                                const std::string &frontend_id,
                                const std::string &platform,
                                const std::string &deterministic,
                                const std::string &fake_root) {
    std::vector<std::string> args;
    args.push_back("request");
    args.push_back("make");
    dsk_append_kv(args, "--manifest", manifest_path);
    dsk_append_kv(args, "--op", op);
    dsk_append_kv(args, "--scope", scope);
    dsk_append_kv(args, "--ui-mode", "cli");
    dsk_append_kv(args, "--root", root);
    dsk_append_kv(args, "--frontend-id", frontend_id);
    dsk_append_kv(args, "--requested-splat", "splat_steam");
    dsk_append_kv(args, "--ownership", "steam");
    dsk_append_kv(args, "--platform", platform);
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

static void dsk_print_usage(void) {
    std::printf("dominium-setup-steam <request-make|run> --manifest <file> [options]\n");
    std::printf("  [--op <install|upgrade|repair|uninstall|verify|status>] [--scope <user|system|portable>]\n");
    std::printf("  [--root <path>] [--platform <triple>] [--deterministic 0|1] [--out-request <file>]\n");
    std::printf("  [--use-fake-services <root>]\n");
    std::printf("  [--out-plan <file>] [--out-state <file>] [--out-audit <file>] [--out-journal <file>]\n");
    std::printf("  [--dry-run] [--json]\n");
}

} // namespace

int main(int argc, char **argv) {
    const char *subcommand = dsk_find_subcommand(argc, argv);
    std::string cli = dsk_get_arg_value(argc, argv, "--setup-cli")
        ? dsk_get_arg_value(argc, argv, "--setup-cli")
        : "dominium-setup";
    std::string manifest_path = dsk_get_arg_value(argc, argv, "--manifest") ? dsk_get_arg_value(argc, argv, "--manifest") : "";
    std::string op = dsk_get_arg_value(argc, argv, "--op") ? dsk_get_arg_value(argc, argv, "--op") : "verify";
    std::string scope = dsk_get_arg_value(argc, argv, "--scope") ? dsk_get_arg_value(argc, argv, "--scope") : "user";
    std::string root = dsk_get_arg_value(argc, argv, "--root") ? dsk_get_arg_value(argc, argv, "--root") : "";
    std::string platform = dsk_get_arg_value(argc, argv, "--platform") ? dsk_get_arg_value(argc, argv, "--platform") : "steam";
    std::string out_request = dsk_get_arg_value(argc, argv, "--out-request") ? dsk_get_arg_value(argc, argv, "--out-request") : "steam_request.tlv";
    std::string request_path = dsk_get_arg_value(argc, argv, "--request") ? dsk_get_arg_value(argc, argv, "--request") : "";
    std::string out_plan = dsk_get_arg_value(argc, argv, "--out-plan") ? dsk_get_arg_value(argc, argv, "--out-plan") : "steam_plan.tlv";
    std::string plan_path = dsk_get_arg_value(argc, argv, "--plan") ? dsk_get_arg_value(argc, argv, "--plan") : "";
    std::string out_state = dsk_get_arg_value(argc, argv, "--out-state") ? dsk_get_arg_value(argc, argv, "--out-state") : "installed_state.tlv";
    std::string out_audit = dsk_get_arg_value(argc, argv, "--out-audit") ? dsk_get_arg_value(argc, argv, "--out-audit") : "setup_audit.tlv";
    std::string out_journal = dsk_get_arg_value(argc, argv, "--out-journal") ? dsk_get_arg_value(argc, argv, "--out-journal") : "job_journal.tlv";
    std::string deterministic = dsk_get_arg_value(argc, argv, "--deterministic") ? dsk_get_arg_value(argc, argv, "--deterministic") : "1";
    std::string frontend_id = dsk_get_arg_value(argc, argv, "--frontend-id") ? dsk_get_arg_value(argc, argv, "--frontend-id") : "dominium-setup-steam";
    std::string fake_root = dsk_get_arg_value(argc, argv, "--use-fake-services") ? dsk_get_arg_value(argc, argv, "--use-fake-services") : "";
    const char *steam_env = std::getenv("STEAM_INSTALL_PATH");
    bool dry_run = dsk_has_flag(argc, argv, "--dry-run");
    bool json = dsk_has_flag(argc, argv, "--json");
    int exit_code = 0;

    if (!root.empty() && steam_env) {
        (void)steam_env;
    } else if (root.empty() && steam_env) {
        root = steam_env;
    }

    if (!subcommand || manifest_path.empty()) {
        dsk_print_usage();
        return 1;
    }

    if (std::strcmp(subcommand, "request-make") == 0) {
        exit_code = dsk_run_request_make(cli,
                                         manifest_path,
                                         op,
                                         scope,
                                         root,
                                         out_request,
                                         frontend_id,
                                         platform,
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
                                   frontend_id,
                                   false);
        }
        return exit_code == -1 ? 1 : exit_code;
    }

    if (std::strcmp(subcommand, "run") == 0) {
        if (request_path.empty()) {
            exit_code = dsk_run_request_make(cli,
                                             manifest_path,
                                             op,
                                             scope,
                                             root,
                                             out_request,
                                             frontend_id,
                                             platform,
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
                                   frontend_id,
                                   dry_run);
        }
        return exit_code == -1 ? 1 : exit_code;
    }

    dsk_print_usage();
    return 1;
}
