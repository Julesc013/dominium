#include "dsk/dsk_api.h"
#include "dsk/dsk_audit.h"
#include "dsk/dsk_contracts.h"
#include "dsk/dsk_digest.h"
#include "dsk/dsk_error.h"
#include "dsk/dsk_splat.h"
#include "dss/dss_services.h"

#include <algorithm>
#include <cstdio>
#include <cstring>
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

static const char *op_to_string(dsk_u16 op) {
    switch (op) {
    case DSK_OPERATION_INSTALL: return "install";
    case DSK_OPERATION_REPAIR: return "repair";
    case DSK_OPERATION_UNINSTALL: return "uninstall";
    case DSK_OPERATION_VERIFY: return "verify";
    case DSK_OPERATION_STATUS: return "status";
    default: return "unknown";
    }
}

static void json_escape(const char *s) {
    const char *p = s ? s : "";
    while (*p) {
        if (*p == '\\' || *p == '\"') {
            std::printf("\\%c", *p);
        } else if (*p == '\n') {
            std::printf("\\n");
        } else if (*p == '\r') {
            std::printf("\\r");
        } else if (*p == '\t') {
            std::printf("\\t");
        } else {
            std::printf("%c", *p);
        }
        ++p;
    }
}

static void print_json_string(const char *value) {
    std::printf("\"");
    json_escape(value ? value : "");
    std::printf("\"");
}

static void print_json_bool(int value) {
    std::printf(value ? "true" : "false");
}

static void print_json_u64_hex(dsk_u64 value) {
    char buf[17];
    std::snprintf(buf, sizeof(buf), "%016llx", (unsigned long long)value);
    std::printf("\"0x%s\"", buf);
}

static const char *root_convention_to_string(dsk_u16 value) {
    switch (value) {
    case DSK_SPLAT_ROOT_CONVENTION_PORTABLE: return "portable";
    case DSK_SPLAT_ROOT_CONVENTION_WINDOWS_PROGRAM_FILES: return "windows_program_files";
    case DSK_SPLAT_ROOT_CONVENTION_LINUX_PREFIX: return "linux_prefix";
    case DSK_SPLAT_ROOT_CONVENTION_MACOS_APPLICATIONS: return "macos_applications";
    case DSK_SPLAT_ROOT_CONVENTION_STEAM_LIBRARY: return "steam_library";
    default: return "unknown";
    }
}

static const char *elevation_to_string(dsk_u16 value) {
    switch (value) {
    case DSK_SPLAT_ELEVATION_NEVER: return "never";
    case DSK_SPLAT_ELEVATION_OPTIONAL: return "optional";
    case DSK_SPLAT_ELEVATION_ALWAYS: return "always";
    default: return "unknown";
    }
}

static const char *rollback_to_string(dsk_u16 value) {
    switch (value) {
    case DSK_SPLAT_ROLLBACK_NONE: return "none";
    case DSK_SPLAT_ROLLBACK_PARTIAL: return "partial";
    case DSK_SPLAT_ROLLBACK_FULL: return "full";
    default: return "unknown";
    }
}

static const char *selected_reason_to_string(dsk_u16 value) {
    switch (value) {
    case DSK_SPLAT_SELECTED_REQUESTED: return "requested_id";
    case DSK_SPLAT_SELECTED_FIRST_COMPATIBLE: return "first_compatible";
    default: return "none";
    }
}

static void print_json_string_list_sorted(const std::vector<std::string> &values) {
    std::vector<std::string> sorted = values;
    size_t i;
    std::sort(sorted.begin(), sorted.end());
    std::printf("[");
    for (i = 0u; i < sorted.size(); ++i) {
        if (i != 0u) {
            std::printf(",");
        }
        print_json_string(sorted[i].c_str());
    }
    std::printf("]");
}

static void print_json_scopes(dsk_u32 scopes) {
    int first = 1;
    std::printf("[");
    if (scopes & DSK_SPLAT_SCOPE_USER) {
        if (!first) std::printf(",");
        print_json_string("user");
        first = 0;
    }
    if (scopes & DSK_SPLAT_SCOPE_SYSTEM) {
        if (!first) std::printf(",");
        print_json_string("system");
        first = 0;
    }
    if (scopes & DSK_SPLAT_SCOPE_PORTABLE) {
        if (!first) std::printf(",");
        print_json_string("portable");
        first = 0;
    }
    std::printf("]");
}

static void print_json_ui_modes(dsk_u32 modes) {
    int first = 1;
    std::printf("[");
    if (modes & DSK_SPLAT_UI_GUI) {
        if (!first) std::printf(",");
        print_json_string("gui");
        first = 0;
    }
    if (modes & DSK_SPLAT_UI_TUI) {
        if (!first) std::printf(",");
        print_json_string("tui");
        first = 0;
    }
    if (modes & DSK_SPLAT_UI_CLI) {
        if (!first) std::printf(",");
        print_json_string("cli");
        first = 0;
    }
    std::printf("]");
}

static void print_json_actions(dsk_u32 actions) {
    int first = 1;
    std::printf("[");
    if (actions & DSK_SPLAT_ACTION_SHORTCUTS) {
        if (!first) std::printf(",");
        print_json_string("shortcuts");
        first = 0;
    }
    if (actions & DSK_SPLAT_ACTION_FILE_ASSOC) {
        if (!first) std::printf(",");
        print_json_string("file_assoc");
        first = 0;
    }
    if (actions & DSK_SPLAT_ACTION_URL_HANDLERS) {
        if (!first) std::printf(",");
        print_json_string("url_handlers");
        first = 0;
    }
    if (actions & DSK_SPLAT_ACTION_CODESIGN_HOOKS) {
        if (!first) std::printf(",");
        print_json_string("codesign_hooks");
        first = 0;
    }
    if (actions & DSK_SPLAT_ACTION_PKGMGR_HOOKS) {
        if (!first) std::printf(",");
        print_json_string("pkgmgr_hooks");
        first = 0;
    }
    if (actions & DSK_SPLAT_ACTION_STEAM_HOOKS) {
        if (!first) std::printf(",");
        print_json_string("steam_hooks");
        first = 0;
    }
    std::printf("]");
}

static void print_json_caps(const dsk_splat_caps_t &caps) {
    std::printf("{");
    std::printf("\"supported_platform_triples\":");
    print_json_string_list_sorted(caps.supported_platform_triples);
    std::printf(",\"supported_scopes\":");
    print_json_scopes(caps.supported_scopes);
    std::printf(",\"supported_ui_modes\":");
    print_json_ui_modes(caps.supported_ui_modes);
    std::printf(",\"supports_atomic_swap\":");
    print_json_bool(caps.supports_atomic_swap);
    std::printf(",\"supports_resume\":");
    print_json_bool(caps.supports_resume);
    std::printf(",\"supports_pkg_ownership\":");
    print_json_bool(caps.supports_pkg_ownership);
    std::printf(",\"supports_portable_ownership\":");
    print_json_bool(caps.supports_portable_ownership);
    std::printf(",\"supports_actions\":");
    print_json_actions(caps.supports_actions);
    std::printf(",\"default_root_convention\":");
    print_json_string(root_convention_to_string(caps.default_root_convention));
    std::printf(",\"elevation_required\":");
    print_json_string(elevation_to_string(caps.elevation_required));
    std::printf(",\"rollback_semantics\":");
    print_json_string(rollback_to_string(caps.rollback_semantics));
    std::printf(",\"notes\":");
    print_json_string(caps.notes.c_str());
    std::printf("}");
}

static bool dsk_candidate_less(const dsk_splat_candidate_t &a,
                               const dsk_splat_candidate_t &b) {
    return a.id < b.id;
}

static bool dsk_rejection_less(const dsk_splat_rejection_t &a,
                               const dsk_splat_rejection_t &b) {
    if (a.id != b.id) {
        return a.id < b.id;
    }
    return a.code < b.code;
}

static void print_json_splat_registry(const std::vector<dsk_splat_candidate_t> &splats) {
    std::vector<dsk_splat_candidate_t> sorted = splats;
    size_t i;
    std::sort(sorted.begin(), sorted.end(), dsk_candidate_less);
    std::printf("{\"splats\":[");
    for (i = 0u; i < sorted.size(); ++i) {
        if (i != 0u) {
            std::printf(",");
        }
        std::printf("{\"id\":");
        print_json_string(sorted[i].id.c_str());
        std::printf(",\"caps_digest64\":");
        print_json_u64_hex(sorted[i].caps_digest64);
        std::printf(",\"caps\":");
        print_json_caps(sorted[i].caps);
        std::printf("}");
    }
    std::printf("]}\n");
}

static void print_json_selection(const dsk_splat_selection_t &selection,
                                 dsk_status_t status) {
    std::vector<dsk_splat_candidate_t> candidates = selection.candidates;
    std::vector<dsk_splat_rejection_t> rejections = selection.rejections;
    size_t i;
    std::sort(candidates.begin(), candidates.end(), dsk_candidate_less);
    std::sort(rejections.begin(), rejections.end(), dsk_rejection_less);

    std::printf("{");
    std::printf("\"status\":\"%s\",", dsk_error_is_ok(status) ? "ok" : "error");
    std::printf("\"selected_splat\":");
    print_json_string(selection.selected_id.c_str());
    std::printf(",\"selected_reason\":%u,", (unsigned)selection.selected_reason);
    std::printf("\"selected_reason_label\":");
    print_json_string(selected_reason_to_string(selection.selected_reason));
    std::printf(",\"candidates\":[");
    for (i = 0u; i < candidates.size(); ++i) {
        if (i != 0u) {
            std::printf(",");
        }
        std::printf("{\"id\":");
        print_json_string(candidates[i].id.c_str());
        std::printf(",\"caps_digest64\":");
        print_json_u64_hex(candidates[i].caps_digest64);
        std::printf("}");
    }
    std::printf("],\"rejections\":[");
    for (i = 0u; i < rejections.size(); ++i) {
        if (i != 0u) {
            std::printf(",");
        }
        std::printf("{\"id\":");
        print_json_string(rejections[i].id.c_str());
        std::printf(",\"code\":%u", (unsigned)rejections[i].code);
        if (!rejections[i].detail.empty()) {
            std::printf(",\"detail\":");
            print_json_string(rejections[i].detail.c_str());
        }
        std::printf("}");
    }
    std::printf("],\"error\":{");
    std::printf("\"domain\":%u,", (unsigned)status.domain);
    std::printf("\"code\":%u,", (unsigned)status.code);
    std::printf("\"subcode\":%u,", (unsigned)status.subcode);
    std::printf("\"flags\":%u,", (unsigned)status.flags);
    std::printf("\"label\":");
    print_json_string(dsk_error_to_string_stable(status));
    std::printf("}}");
    std::printf("\n");
}

static void print_json_summary(const dsk_audit_t &audit, dsk_status_t status) {
    char manifest_hex[17];
    char request_hex[17];
    std::snprintf(manifest_hex, sizeof(manifest_hex), "%016llx",
                  (unsigned long long)audit.manifest_digest64);
    std::snprintf(request_hex, sizeof(request_hex), "%016llx",
                  (unsigned long long)audit.request_digest64);

    std::printf("{");
    std::printf("\"status\":\"%s\",", dsk_error_is_ok(status) ? "ok" : "error");
    std::printf("\"operation\":\"%s\",", op_to_string(audit.operation));
    std::printf("\"selected_splat\":\"");
    json_escape(audit.selected_splat.c_str());
    std::printf("\",");
    std::printf("\"manifest_digest64\":\"0x%s\",", manifest_hex);
    std::printf("\"request_digest64\":\"0x%s\",", request_hex);
    std::printf("\"error\":{");
    std::printf("\"domain\":%u,", (unsigned)status.domain);
    std::printf("\"code\":%u,", (unsigned)status.code);
    std::printf("\"subcode\":%u,", (unsigned)status.subcode);
    std::printf("\"flags\":%u,", (unsigned)status.flags);
    std::printf("\"label\":\"%s\"", dsk_error_to_string_stable(status));
    std::printf("}");
    std::printf("}\n");
}

static void print_usage(void) {
    std::printf("dominium-setup2 validate-manifest --in <file>\n");
    std::printf("dominium-setup2 validate-request --in <file>\n");
    std::printf("dominium-setup2 run --manifest <file> --request <file> --out-state <file> --out-audit <file> [--out-log <file>] [--json]\n");
    std::printf("dominium-setup2 dump-splats --json\n");
    std::printf("dominium-setup2 select-splat --manifest <file> --request <file> --json\n");
    std::printf("options: --use-fake-services <sandbox_root>\n");
}

static const char *get_arg_value(int argc, char **argv, const char *name) {
    int i;
    for (i = 2; i < argc - 1; ++i) {
        if (std::strcmp(argv[i], name) == 0) {
            return argv[i + 1];
        }
    }
    return 0;
}

static int has_flag(int argc, char **argv, const char *name) {
    int i;
    for (i = 2; i < argc; ++i) {
        if (std::strcmp(argv[i], name) == 0) {
            return 1;
        }
    }
    return 0;
}

static int finish(dss_services_t *services, int code) {
    if (services) {
        dss_services_shutdown(services);
    }
    return code;
}

int main(int argc, char **argv) {
    dss_services_t services;
    dss_services_config_t services_cfg;
    dss_error_t services_st;
    const char *fake_root = get_arg_value(argc, argv, "--use-fake-services");

    if (argc < 2) {
        print_usage();
        return 1;
    }

    dss_services_config_init(&services_cfg);
    if (fake_root) {
        services_cfg.sandbox_root = fake_root;
        services_st = dss_services_init_fake(&services_cfg, &services);
    } else {
        services_st = dss_services_init_real(&services);
    }
    if (!dss_error_is_ok(services_st)) {
        std::fprintf(stderr, "error: failed to init services\n");
        return 1;
    }

    if (std::strcmp(argv[1], "validate-manifest") == 0) {
        const char *path = get_arg_value(argc, argv, "--in");
        std::vector<dsk_u8> bytes;
        dsk_manifest_t manifest;
        dsk_status_t st;
        if (!path || !load_file(&services.fs, path, bytes)) {
            std::fprintf(stderr, "error: failed to read manifest\n");
            return finish(&services, 1);
        }
        st = dsk_manifest_parse(&bytes[0], (dsk_u32)bytes.size(), &manifest);
        if (!dsk_error_is_ok(st)) {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            return finish(&services, dsk_error_to_exit_code(st));
        }
        std::printf("ok\n");
        return finish(&services, 0);
    }

    if (std::strcmp(argv[1], "validate-request") == 0) {
        const char *path = get_arg_value(argc, argv, "--in");
        std::vector<dsk_u8> bytes;
        dsk_request_t request;
        dsk_status_t st;
        if (!path || !load_file(&services.fs, path, bytes)) {
            std::fprintf(stderr, "error: failed to read request\n");
            return finish(&services, 1);
        }
        st = dsk_request_parse(&bytes[0], (dsk_u32)bytes.size(), &request);
        if (!dsk_error_is_ok(st)) {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            return finish(&services, dsk_error_to_exit_code(st));
        }
        std::printf("ok\n");
        return finish(&services, 0);
    }

    if (std::strcmp(argv[1], "dump-splats") == 0) {
        std::vector<dsk_splat_candidate_t> splats;
        size_t i;
        int json = has_flag(argc, argv, "--json");
        dsk_splat_registry_list(splats);
        if (json) {
            print_json_splat_registry(splats);
        } else {
            for (i = 0u; i < splats.size(); ++i) {
                std::printf("%s\n", splats[i].id.c_str());
            }
        }
        return finish(&services, 0);
    }

    if (std::strcmp(argv[1], "select-splat") == 0) {
        const char *manifest_path = get_arg_value(argc, argv, "--manifest");
        const char *request_path = get_arg_value(argc, argv, "--request");
        int json = has_flag(argc, argv, "--json");
        std::vector<dsk_u8> manifest_bytes;
        std::vector<dsk_u8> request_bytes;
        dsk_manifest_t manifest;
        dsk_request_t request;
        dsk_splat_selection_t selection;
        dsk_status_t st;

        if (!manifest_path || !request_path) {
            print_usage();
            return finish(&services, 1);
        }
        if (!load_file(&services.fs, manifest_path, manifest_bytes)) {
            std::fprintf(stderr, "error: failed to read manifest\n");
            return finish(&services, 1);
        }
        if (!load_file(&services.fs, request_path, request_bytes)) {
            std::fprintf(stderr, "error: failed to read request\n");
            return finish(&services, 1);
        }

        st = dsk_manifest_parse(&manifest_bytes[0],
                                (dsk_u32)manifest_bytes.size(),
                                &manifest);
        if (!dsk_error_is_ok(st)) {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            return finish(&services, dsk_error_to_exit_code(st));
        }
        st = dsk_request_parse(&request_bytes[0],
                               (dsk_u32)request_bytes.size(),
                               &request);
        if (!dsk_error_is_ok(st)) {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            return finish(&services, dsk_error_to_exit_code(st));
        }
        if (services.platform.get_platform_triple) {
            std::string platform_override;
            dss_error_t pst = services.platform.get_platform_triple(services.platform.ctx,
                                                                    &platform_override);
            if (dss_error_is_ok(pst) && !platform_override.empty()) {
                request.target_platform_triple = platform_override;
            }
        }

        st = dsk_splat_select(manifest, request, &selection);
        if (json) {
            print_json_selection(selection, st);
        } else if (dsk_error_is_ok(st)) {
            std::printf("%s\n", selection.selected_id.c_str());
        } else {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
        }
        return finish(&services, dsk_error_to_exit_code(st));
    }

    if (std::strcmp(argv[1], "run") == 0) {
        const char *manifest_path = get_arg_value(argc, argv, "--manifest");
        const char *request_path = get_arg_value(argc, argv, "--request");
        const char *out_state = get_arg_value(argc, argv, "--out-state");
        const char *out_audit = get_arg_value(argc, argv, "--out-audit");
        const char *out_log = get_arg_value(argc, argv, "--out-log");
        int json = 0;
        std::vector<dsk_u8> manifest_bytes;
        std::vector<dsk_u8> request_bytes;
        dsk_request_t request;
        dsk_kernel_request_ex_t kernel_req;
        dsk_mem_sink_t state_sink;
        dsk_mem_sink_t audit_sink;
        dsk_mem_sink_t log_sink;
        dsk_status_t st;
        dsk_audit_t audit;
        int i;

        for (i = 2; i < argc; ++i) {
            if (std::strcmp(argv[i], "--json") == 0) {
                json = 1;
            }
        }

        if (!manifest_path || !request_path || !out_state || !out_audit) {
            print_usage();
            return 1;
        }
        if (!load_file(&services.fs, manifest_path, manifest_bytes)) {
            std::fprintf(stderr, "error: failed to read manifest\n");
            return finish(&services, 1);
        }
        if (!load_file(&services.fs, request_path, request_bytes)) {
            std::fprintf(stderr, "error: failed to read request\n");
            return finish(&services, 1);
        }

        st = dsk_request_parse(&request_bytes[0], (dsk_u32)request_bytes.size(), &request);
        if (!dsk_error_is_ok(st)) {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            return dsk_error_to_exit_code(st);
        }

        dsk_kernel_request_ex_init(&kernel_req);
        kernel_req.base.manifest_bytes = &manifest_bytes[0];
        kernel_req.base.manifest_size = (dsk_u32)manifest_bytes.size();
        kernel_req.base.request_bytes = &request_bytes[0];
        kernel_req.base.request_size = (dsk_u32)request_bytes.size();
        kernel_req.base.services = &services;
        kernel_req.base.deterministic_mode = (request.policy_flags & DSK_POLICY_DETERMINISTIC) ? 1u : 0u;
        kernel_req.base.out_state.user = &state_sink;
        kernel_req.base.out_state.write = dsk_mem_sink_write;
        kernel_req.base.out_audit.user = &audit_sink;
        kernel_req.base.out_audit.write = dsk_mem_sink_write;
        if (out_log && out_log[0]) {
            kernel_req.out_log.user = &log_sink;
            kernel_req.out_log.write = dsk_mem_sink_write;
        }

        switch (request.operation) {
        case DSK_OPERATION_INSTALL:
            st = dsk_install_ex(&kernel_req);
            break;
        case DSK_OPERATION_REPAIR:
            st = dsk_repair_ex(&kernel_req);
            break;
        case DSK_OPERATION_UNINSTALL:
            st = dsk_uninstall_ex(&kernel_req);
            break;
        case DSK_OPERATION_VERIFY:
            st = dsk_verify_ex(&kernel_req);
            break;
        case DSK_OPERATION_STATUS:
            st = dsk_status_ex(&kernel_req);
            break;
        default:
            std::fprintf(stderr, "error: invalid operation\n");
            return 1;
        }

        if (!write_file(&services.fs, out_state, state_sink.data)) {
            std::fprintf(stderr, "error: failed to write state\n");
            return finish(&services, 1);
        }
        if (!write_file(&services.fs, out_audit, audit_sink.data)) {
            std::fprintf(stderr, "error: failed to write audit\n");
            return finish(&services, 1);
        }
        if (out_log && out_log[0]) {
            if (!write_file(&services.fs, out_log, log_sink.data)) {
                std::fprintf(stderr, "error: failed to write log\n");
                return finish(&services, 1);
            }
        }

        if (json) {
            dsk_status_t parse_st = dsk_audit_parse(&audit_sink.data[0],
                                                    (dsk_u32)audit_sink.data.size(),
                                                    &audit);
            if (dsk_error_is_ok(parse_st)) {
                print_json_summary(audit, st);
            } else {
                dsk_audit_clear(&audit);
                audit.operation = request.operation;
                audit.manifest_digest64 = dsk_digest64_bytes(&manifest_bytes[0],
                                                            (dsk_u32)manifest_bytes.size());
                audit.request_digest64 = dsk_digest64_bytes(&request_bytes[0],
                                                            (dsk_u32)request_bytes.size());
                print_json_summary(audit, st);
            }
        }

        return finish(&services, dsk_error_to_exit_code(st));
    }

    print_usage();
    return finish(&services, 1);
}
