#include "dsk/dsk_api.h"
#include "dsk/dsk_audit.h"
#include "dsk/dsk_contracts.h"
#include "dsk/dsk_error.h"
#include "dsk/dsk_jobs.h"
#include "dsk/dsk_plan.h"
#include "dsk/dsk_resume.h"
#include "dss/dss_services.h"

#include "args_parse.h"
#include "request_builder.h"

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

struct dsk_mem_sink_t {
    std::vector<dsk_u8> data;
};

static dsk_status_t dsk_mem_sink_write(void *user, const dsk_u8 *data, dsk_u32 len) {
    dsk_mem_sink_t *sink = reinterpret_cast<dsk_mem_sink_t *>(user);
    if (!sink) {
        return dsk_error_make(DSK_DOMAIN_FRONTEND, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    if (len && !data) {
        return dsk_error_make(DSK_DOMAIN_FRONTEND, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    sink->data.insert(sink->data.end(), data, data + len);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

static int load_file(const dss_fs_api_t *fs, const char *path, std::vector<dsk_u8> &out) {
    dss_error_t st;
    if (!fs || !fs->read_file_bytes) {
        return 0;
    }
    st = fs->read_file_bytes(fs->ctx, path, &out);
    return dss_error_is_ok(st);
}

static int write_file(const dss_fs_api_t *fs,
                      const char *path,
                      const std::vector<dsk_u8> &data) {
    dss_error_t st;
    if (!fs || !fs->write_file_bytes_atomic) {
        return 0;
    }
    st = fs->write_file_bytes_atomic(fs->ctx,
                                     path,
                                     data.empty() ? 0 : &data[0],
                                     (dss_u32)data.size());
    return dss_error_is_ok(st);
}

static std::string trim_copy(const std::string &value) {
    size_t start = 0u;
    size_t end = value.size();
    while (start < end && (value[start] == ' ' || value[start] == '\t')) {
        ++start;
    }
    while (end > start && (value[end - 1u] == ' ' || value[end - 1u] == '\t')) {
        --end;
    }
    return value.substr(start, end - start);
}

static std::string lowercase_copy(const std::string &value) {
    std::string out = value;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        char c = out[i];
        if (c >= 'A' && c <= 'Z') {
            out[i] = (char)(c - 'A' + 'a');
        }
    }
    return out;
}

static std::string quote_if_needed(const std::string &value) {
    if (value.find(' ') == std::string::npos) {
        return value;
    }
    return "\"" + value + "\"";
}

static dsk_bool parse_bool_option(const dsk_args_view_t *args,
                                  const char *name,
                                  dsk_bool default_value) {
    const char *value;
    dsk_bool parsed = default_value;
    if (!args || !name) {
        return default_value;
    }
    value = dsk_args_get_value(args, name);
    if (!value) {
        return default_value;
    }
    if (dsk_args_parse_bool(value, &parsed)) {
        return parsed;
    }
    return default_value;
}

enum prompt_result_t {
    PROMPT_OK = 0,
    PROMPT_BACK = 1,
    PROMPT_CANCEL = 2
};

static prompt_result_t prompt_line(const char *prompt, std::string *out_line) {
    std::string line;
    if (!out_line) {
        return PROMPT_CANCEL;
    }
    std::printf("%s", prompt);
    std::getline(std::cin, line);
    line = trim_copy(line);
    if (line == "back" || line == "b") {
        return PROMPT_BACK;
    }
    if (line == "cancel" || line == "c" || line == "q" || line == "quit") {
        return PROMPT_CANCEL;
    }
    *out_line = line;
    return PROMPT_OK;
}

static dsk_u16 choose_operation_noninteractive(void) {
    return DSK_OPERATION_INSTALL;
}

static dsk_u16 choose_scope_noninteractive(void) {
    return DSK_INSTALL_SCOPE_USER;
}

static dsk_u16 choose_ui_mode(void) {
    return DSK_UI_MODE_TUI;
}

static const char *operation_label(dsk_u16 op) {
    switch (op) {
    case DSK_OPERATION_INSTALL: return "install";
    case DSK_OPERATION_UPGRADE: return "upgrade";
    case DSK_OPERATION_REPAIR: return "repair";
    case DSK_OPERATION_UNINSTALL: return "uninstall";
    case DSK_OPERATION_VERIFY: return "verify";
    case DSK_OPERATION_STATUS: return "status";
    default: return "unknown";
    }
}

static const char *scope_label(dsk_u16 scope) {
    switch (scope) {
    case DSK_INSTALL_SCOPE_USER: return "user";
    case DSK_INSTALL_SCOPE_SYSTEM: return "system";
    case DSK_INSTALL_SCOPE_PORTABLE: return "portable";
    default: return "unknown";
    }
}

static dsk_u16 prompt_operation(prompt_result_t *out_result) {
    std::string line;
    for (;;) {
        std::printf("Select operation:\n");
        std::printf("  1) install\n");
        std::printf("  2) repair\n");
        std::printf("  3) uninstall\n");
        std::printf("  4) verify\n");
        std::printf("  5) status\n");
        {
            prompt_result_t res = prompt_line("Choice [1]: ", &line);
            if (res != PROMPT_OK) {
                *out_result = res;
                return 0u;
            }
        }
        if (line.empty() || line == "1") {
            *out_result = PROMPT_OK;
            return DSK_OPERATION_INSTALL;
        }
        if (line == "2") {
            *out_result = PROMPT_OK;
            return DSK_OPERATION_REPAIR;
        }
        if (line == "3") {
            *out_result = PROMPT_OK;
            return DSK_OPERATION_UNINSTALL;
        }
        if (line == "4") {
            *out_result = PROMPT_OK;
            return DSK_OPERATION_VERIFY;
        }
        if (line == "5") {
            *out_result = PROMPT_OK;
            return DSK_OPERATION_STATUS;
        }
        std::printf("Invalid choice. Type back to go back.\n");
    }
}

static dsk_u16 prompt_scope(prompt_result_t *out_result) {
    std::string line;
    for (;;) {
        std::printf("Select scope:\n");
        std::printf("  1) user\n");
        std::printf("  2) system\n");
        std::printf("  3) portable\n");
        {
            prompt_result_t res = prompt_line("Choice [1]: ", &line);
            if (res != PROMPT_OK) {
                *out_result = res;
                return 0u;
            }
        }
        if (line.empty() || line == "1") {
            *out_result = PROMPT_OK;
            return DSK_INSTALL_SCOPE_USER;
        }
        if (line == "2") {
            *out_result = PROMPT_OK;
            return DSK_INSTALL_SCOPE_SYSTEM;
        }
        if (line == "3") {
            *out_result = PROMPT_OK;
            return DSK_INSTALL_SCOPE_PORTABLE;
        }
        std::printf("Invalid choice. Type back to go back.\n");
    }
}

static dsk_bool prompt_quick_custom(prompt_result_t *out_result) {
    std::string line;
    for (;;) {
        {
            prompt_result_t res = prompt_line("Quick install (defaults)? [Y/n]: ", &line);
            if (res != PROMPT_OK) {
                *out_result = res;
                return DSK_TRUE;
            }
        }
        if (line.empty() || line == "y" || line == "yes") {
            *out_result = PROMPT_OK;
            return DSK_TRUE;
        }
        if (line == "n" || line == "no") {
            *out_result = PROMPT_OK;
            return DSK_FALSE;
        }
        std::printf("Invalid choice. Type back to go back.\n");
    }
}

static void prompt_components(const dsk_manifest_t &manifest,
                              std::vector<std::string> *out_components,
                              prompt_result_t *out_result) {
    size_t i;
    std::string line;
    if (!out_components) {
        *out_result = PROMPT_CANCEL;
        return;
    }
    out_components->clear();
    std::printf("Components:\n");
    for (i = 0u; i < manifest.components.size(); ++i) {
        const dsk_manifest_component_t &comp = manifest.components[i];
        std::printf("  %u) %s [%s]%s\n",
                    (unsigned)(i + 1u),
                    comp.component_id.c_str(),
                    comp.kind.c_str(),
                    comp.default_selected ? " (default)" : "");
    }
    {
        prompt_result_t res = prompt_line("Enter component ids or numbers (comma-separated), blank for defaults: ",
                                          &line);
        if (res != PROMPT_OK) {
            *out_result = res;
            return;
        }
    }
    if (line.empty()) {
        *out_result = PROMPT_OK;
        return;
    }
    {
        std::vector<std::string> tokens;
        dsk_args_split_csv(line.c_str(), &tokens);
        for (i = 0u; i < tokens.size(); ++i) {
            std::string token = trim_copy(tokens[i]);
            if (token.empty()) {
                continue;
            }
            if (token.find_first_not_of("0123456789") == std::string::npos) {
                int idx = std::atoi(token.c_str());
                if (idx >= 1 && (size_t)idx <= manifest.components.size()) {
                    out_components->push_back(manifest.components[idx - 1u].component_id);
                }
            } else {
                out_components->push_back(token);
            }
        }
    }
    *out_result = PROMPT_OK;
}

static int apply_plan_bytes(dss_services_t *services,
                            const std::vector<dsk_u8> &plan_bytes,
                            const char *out_state,
                            const char *out_audit,
                            const char *out_journal) {
    dsk_apply_request_t apply;
    dsk_status_t st;
    if (plan_bytes.empty()) {
        return dsk_error_to_exit_code(dsk_error_make(DSK_DOMAIN_KERNEL,
                                                     DSK_CODE_VALIDATION_ERROR,
                                                     DSK_SUBCODE_INVALID_FIELD,
                                                     DSK_ERROR_FLAG_USER_ACTIONABLE));
    }
    dsk_apply_request_init(&apply);
    apply.services = services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = out_state;
    apply.out_audit_path = out_audit;
    apply.out_journal_path = out_journal;
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (!dsk_error_is_ok(st)) {
        std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
    }
    return dsk_error_to_exit_code(st);
}

static void print_usage(void) {
    std::printf("dominium-setup-tui --manifest <file> [--out-request <file>] [--apply]\n");
    std::printf("  [--out-plan <file>] [--out-state <file>] [--out-audit <file>] [--out-journal <file>]\n");
    std::printf("  [--defaults] [--yes] [--deterministic 0|1] [--use-fake-services <root>]\n");
    std::printf("  [--platform <triple>] [--frontend-id <id>]\n");
}

int main(int argc, char **argv) {
    dss_services_t services;
    dss_services_config_t services_cfg;
    dss_error_t services_st;
    const char *fake_root;
    dsk_args_view_t args;
    const char *manifest_path;
    const char *out_request;
    const char *out_plan;
    const char *out_state;
    const char *out_audit;
    const char *out_journal;
    const char *frontend_id;
    const char *platform_triple;
    dsk_bool apply = DSK_FALSE;
    dsk_bool defaults = DSK_FALSE;
    dsk_bool assume_yes = DSK_FALSE;
    dsk_bool deterministic = DSK_TRUE;
    dsk_u16 operation = 0u;
    dsk_u16 scope = 0u;
    dsk_u16 ui_mode = choose_ui_mode();
    std::string frontend_id_value;
    std::string install_root;
    std::vector<std::string> requested_components;
    dsk_manifest_t manifest;
    std::vector<dsk_u8> manifest_bytes;
    dsk_request_t request;
    std::vector<dsk_u8> request_bytes;
    dsk_status_t st;
    int step = 0;

    if (argc < 2) {
        print_usage();
        return 1;
    }
    dsk_args_view_init(&args, argc, argv, 1);
    fake_root = dsk_args_get_value(&args, "--use-fake-services");
    platform_triple = dsk_args_get_value(&args, "--platform");
    manifest_path = dsk_args_get_value(&args, "--manifest");
    out_request = dsk_args_get_value(&args, "--out-request");
    out_plan = dsk_args_get_value(&args, "--out-plan");
    out_state = dsk_args_get_value(&args, "--out-state");
    out_audit = dsk_args_get_value(&args, "--out-audit");
    out_journal = dsk_args_get_value(&args, "--out-journal");
    apply = dsk_args_has_flag(&args, "--apply");
    defaults = dsk_args_has_flag(&args, "--defaults");
    assume_yes = dsk_args_has_flag(&args, "--yes");
    deterministic = parse_bool_option(&args, "--deterministic", DSK_TRUE);
    frontend_id = dsk_args_get_value(&args, "--frontend-id");
    frontend_id_value = frontend_id ? frontend_id : "tui";

    if (!manifest_path) {
        dsk_status_t missing = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                              DSK_CODE_INVALID_ARGS,
                                              DSK_SUBCODE_MISSING_FIELD,
                                              DSK_ERROR_FLAG_USER_ACTIONABLE);
        print_usage();
        return dsk_error_to_exit_code(missing);
    }
    if (!out_request) {
        out_request = "install_request.tlv";
    }
    if (!out_plan) {
        out_plan = "install_plan.tlv";
    }
    if (!out_state) {
        out_state = "installed_state.tlv";
    }
    if (!out_audit) {
        out_audit = "setup_audit.tlv";
    }
    if (!out_journal) {
        out_journal = "job_journal.tlv";
    }

    dss_services_config_init(&services_cfg);
    if (fake_root) {
        services_cfg.sandbox_root = fake_root;
        services_cfg.platform_triple = platform_triple;
        services_st = dss_services_init_fake(&services_cfg, &services);
    } else {
        services_st = dss_services_init_real(&services);
    }
    if (!dss_error_is_ok(services_st)) {
        std::fprintf(stderr, "error: failed to init services\n");
        return 1;
    }

    if (!load_file(&services.fs, manifest_path, manifest_bytes)) {
        st = dsk_error_make(DSK_DOMAIN_SERVICES,
                            DSK_CODE_IO_ERROR,
                            DSK_SUBCODE_NONE,
                            0u);
        std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
        dss_services_shutdown(&services);
        return dsk_error_to_exit_code(st);
    }
    st = dsk_manifest_parse(manifest_bytes.empty() ? 0 : &manifest_bytes[0],
                            (dsk_u32)manifest_bytes.size(),
                            &manifest);
    if (!dsk_error_is_ok(st)) {
        std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
        dss_services_shutdown(&services);
        return dsk_error_to_exit_code(st);
    }

    if (defaults || assume_yes) {
        operation = choose_operation_noninteractive();
        scope = choose_scope_noninteractive();
    } else {
        while (step < 6) {
            prompt_result_t result = PROMPT_OK;
            if (step == 0) {
                std::printf("Dominium Setup (TUI)\n");
                std::printf("Manifest: %s\n", manifest_path);
                step++;
                continue;
            }
            if (step == 1) {
                operation = prompt_operation(&result);
            } else if (step == 2) {
                dsk_bool quick = prompt_quick_custom(&result);
                if (result == PROMPT_OK && !quick) {
                    prompt_components(manifest, &requested_components, &result);
                } else if (result == PROMPT_OK && quick) {
                    requested_components.clear();
                }
            } else if (step == 3) {
                scope = prompt_scope(&result);
            } else if (step == 4) {
                std::string line;
                result = prompt_line("Install root (blank for default): ", &line);
                if (result == PROMPT_OK) {
                    install_root = line;
                }
            } else if (step == 5) {
                std::string line;
                std::printf("Summary:\n");
                std::printf("  operation: %s\n", operation_label(operation));
                std::printf("  scope: %s\n", scope_label(scope));
                std::printf("  install_root: %s\n", install_root.empty() ? "(default)" : install_root.c_str());
                std::printf("  components: %s\n", requested_components.empty() ? "(defaults)" : "custom");
                if (!assume_yes) {
                    result = prompt_line("Proceed? [Y/n]: ", &line);
                    if (result == PROMPT_OK) {
                        if (!line.empty() && line != "y" && line != "yes") {
                            result = PROMPT_BACK;
                        }
                    }
                } else {
                    result = PROMPT_OK;
                }
            }
            if (result == PROMPT_CANCEL) {
                dss_services_shutdown(&services);
                return 1;
            }
            if (result == PROMPT_BACK) {
                if (step > 0) {
                    --step;
                }
                continue;
            }
            ++step;
        }
    }

    if (operation == 0u || scope == 0u) {
        st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                            DSK_CODE_VALIDATION_ERROR,
                            DSK_SUBCODE_INVALID_FIELD,
                            DSK_ERROR_FLAG_USER_ACTIONABLE);
        std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
        dss_services_shutdown(&services);
        return dsk_error_to_exit_code(st);
    }

    {
        dsk_request_build_opts_t opts;
        dsk_request_build_opts_init(&opts);
        opts.manifest_path = manifest_path;
        opts.operation = operation;
        opts.install_scope = scope;
        opts.ui_mode = ui_mode;
        opts.policy_flags = deterministic ? DSK_POLICY_DETERMINISTIC : 0u;
        opts.preferred_install_root = install_root;
        opts.requested_components = requested_components;
        opts.frontend_id = frontend_id_value;
        st = dsk_request_build_bytes(&opts, &services, &request_bytes, &request);
        if (!dsk_error_is_ok(st)) {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            dss_services_shutdown(&services);
            return dsk_error_to_exit_code(st);
        }
        if (!write_file(&services.fs, out_request, request_bytes)) {
            st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                DSK_CODE_IO_ERROR,
                                DSK_SUBCODE_NONE,
                                0u);
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            dss_services_shutdown(&services);
            return dsk_error_to_exit_code(st);
        }
    }

    {
        std::string cmd = "dominium-setup request make";
        cmd += " --manifest " + quote_if_needed(manifest_path);
        cmd += " --op ";
        cmd += operation_label(operation);
        cmd += " --scope ";
        cmd += scope_label(scope);
        cmd += " --ui-mode tui";
        cmd += " --frontend-id " + quote_if_needed(frontend_id_value);
        if (!requested_components.empty()) {
            cmd += " --components ";
            {
                size_t i;
                for (i = 0u; i < requested_components.size(); ++i) {
                    if (i != 0u) {
                        cmd += ",";
                    }
                    cmd += requested_components[i];
                }
            }
        }
        if (!install_root.empty()) {
            cmd += " --root " + quote_if_needed(install_root);
        }
        cmd += " --out-request " + quote_if_needed(out_request);
        cmd += deterministic ? " --deterministic 1" : " --deterministic 0";
        std::printf("Equivalent CLI:\n  %s\n", cmd.c_str());
    }

    if (apply) {
        dsk_kernel_request_ex_t kernel_req;
        dsk_mem_sink_t plan_sink;
        dsk_mem_sink_t state_sink;
        dsk_mem_sink_t audit_sink;
        dsk_status_t plan_st;

        dsk_kernel_request_ex_init(&kernel_req);
        kernel_req.base.manifest_bytes = &manifest_bytes[0];
        kernel_req.base.manifest_size = (dsk_u32)manifest_bytes.size();
        kernel_req.base.request_bytes = &request_bytes[0];
        kernel_req.base.request_size = (dsk_u32)request_bytes.size();
        kernel_req.base.services = &services;
        kernel_req.base.deterministic_mode = deterministic ? 1u : 0u;
        kernel_req.base.out_plan.user = &plan_sink;
        kernel_req.base.out_plan.write = dsk_mem_sink_write;
        kernel_req.base.out_state.user = &state_sink;
        kernel_req.base.out_state.write = dsk_mem_sink_write;
        kernel_req.base.out_audit.user = &audit_sink;
        kernel_req.base.out_audit.write = dsk_mem_sink_write;

        switch (operation) {
        case DSK_OPERATION_INSTALL:
            plan_st = dsk_install_ex(&kernel_req);
            break;
        case DSK_OPERATION_UPGRADE:
            plan_st = dsk_upgrade_ex(&kernel_req);
            break;
        case DSK_OPERATION_REPAIR:
            plan_st = dsk_repair_ex(&kernel_req);
            break;
        case DSK_OPERATION_UNINSTALL:
            plan_st = dsk_uninstall_ex(&kernel_req);
            break;
        case DSK_OPERATION_VERIFY:
            plan_st = dsk_verify_ex(&kernel_req);
            break;
        case DSK_OPERATION_STATUS:
            plan_st = dsk_status_ex(&kernel_req);
            break;
        default:
            plan_st = dsk_error_make(DSK_DOMAIN_FRONTEND,
                                     DSK_CODE_VALIDATION_ERROR,
                                     DSK_SUBCODE_INVALID_FIELD,
                                     DSK_ERROR_FLAG_USER_ACTIONABLE);
            break;
        }

        if (!dsk_error_is_ok(plan_st)) {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(plan_st));
            dss_services_shutdown(&services);
            return dsk_error_to_exit_code(plan_st);
        }
        if (!write_file(&services.fs, out_plan, plan_sink.data)) {
            dsk_status_t io_st = dsk_error_make(DSK_DOMAIN_SERVICES,
                                                DSK_CODE_IO_ERROR,
                                                DSK_SUBCODE_NONE,
                                                0u);
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(io_st));
            dss_services_shutdown(&services);
            return dsk_error_to_exit_code(io_st);
        }

        std::printf("plan: %s\n", out_plan);
        std::printf("state: %s\n", out_state);
        std::printf("audit: %s\n", out_audit);
        std::printf("journal: %s\n", out_journal);
        {
            int exit_code = apply_plan_bytes(&services,
                                             plan_sink.data,
                                             out_state,
                                             out_audit,
                                             out_journal);
            dss_services_shutdown(&services);
            return exit_code;
        }
    }

    dss_services_shutdown(&services);
    return 0;
}
