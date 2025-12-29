#include "dsk/dsk_api.h"
#include "dsk/dsk_audit.h"
#include "dsk/dsk_contracts.h"
#include "dsk/dsk_digest.h"
#include "dsk/dsk_error.h"

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

static int load_file(const char *path, std::vector<dsk_u8> &out) {
    FILE *f;
    long len;
    size_t read_count;
    out.clear();
    if (!path) {
        return 0;
    }
    f = std::fopen(path, "rb");
    if (!f) {
        return 0;
    }
    if (std::fseek(f, 0, SEEK_END) != 0) {
        std::fclose(f);
        return 0;
    }
    len = std::ftell(f);
    if (len < 0) {
        std::fclose(f);
        return 0;
    }
    if (std::fseek(f, 0, SEEK_SET) != 0) {
        std::fclose(f);
        return 0;
    }
    out.resize((size_t)len);
    read_count = (len > 0) ? std::fread(&out[0], 1u, (size_t)len, f) : 0u;
    std::fclose(f);
    return read_count == (size_t)len;
}

static int write_file(const char *path, const std::vector<dsk_u8> &data) {
    FILE *f;
    size_t wrote;
    if (!path) {
        return 0;
    }
    f = std::fopen(path, "wb");
    if (!f) {
        return 0;
    }
    wrote = data.empty() ? 0u : std::fwrite(&data[0], 1u, data.size(), f);
    std::fclose(f);
    return wrote == data.size();
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
    std::printf("dominium-setup2 run --manifest <file> --request <file> --out-state <file> --out-audit <file> [--json]\n");
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

int main(int argc, char **argv) {
    if (argc < 2) {
        print_usage();
        return 1;
    }

    if (std::strcmp(argv[1], "validate-manifest") == 0) {
        const char *path = get_arg_value(argc, argv, "--in");
        std::vector<dsk_u8> bytes;
        dsk_manifest_t manifest;
        dsk_status_t st;
        if (!path || !load_file(path, bytes)) {
            std::fprintf(stderr, "error: failed to read manifest\n");
            return 1;
        }
        st = dsk_manifest_parse(&bytes[0], (dsk_u32)bytes.size(), &manifest);
        if (!dsk_error_is_ok(st)) {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            return dsk_error_to_exit_code(st);
        }
        std::printf("ok\n");
        return 0;
    }

    if (std::strcmp(argv[1], "validate-request") == 0) {
        const char *path = get_arg_value(argc, argv, "--in");
        std::vector<dsk_u8> bytes;
        dsk_request_t request;
        dsk_status_t st;
        if (!path || !load_file(path, bytes)) {
            std::fprintf(stderr, "error: failed to read request\n");
            return 1;
        }
        st = dsk_request_parse(&bytes[0], (dsk_u32)bytes.size(), &request);
        if (!dsk_error_is_ok(st)) {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            return dsk_error_to_exit_code(st);
        }
        std::printf("ok\n");
        return 0;
    }

    if (std::strcmp(argv[1], "run") == 0) {
        const char *manifest_path = get_arg_value(argc, argv, "--manifest");
        const char *request_path = get_arg_value(argc, argv, "--request");
        const char *out_state = get_arg_value(argc, argv, "--out-state");
        const char *out_audit = get_arg_value(argc, argv, "--out-audit");
        int json = 0;
        std::vector<dsk_u8> manifest_bytes;
        std::vector<dsk_u8> request_bytes;
        dsk_request_t request;
        dsk_kernel_request_t kernel_req;
        dsk_mem_sink_t state_sink;
        dsk_mem_sink_t audit_sink;
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
        if (!load_file(manifest_path, manifest_bytes)) {
            std::fprintf(stderr, "error: failed to read manifest\n");
            return 1;
        }
        if (!load_file(request_path, request_bytes)) {
            std::fprintf(stderr, "error: failed to read request\n");
            return 1;
        }

        st = dsk_request_parse(&request_bytes[0], (dsk_u32)request_bytes.size(), &request);
        if (!dsk_error_is_ok(st)) {
            std::fprintf(stderr, "error: %s\n", dsk_error_to_string_stable(st));
            return dsk_error_to_exit_code(st);
        }

        dsk_kernel_request_init(&kernel_req);
        kernel_req.manifest_bytes = &manifest_bytes[0];
        kernel_req.manifest_size = (dsk_u32)manifest_bytes.size();
        kernel_req.request_bytes = &request_bytes[0];
        kernel_req.request_size = (dsk_u32)request_bytes.size();
        kernel_req.deterministic_mode = (request.policy_flags & DSK_POLICY_DETERMINISTIC) ? 1u : 0u;
        kernel_req.out_state.user = &state_sink;
        kernel_req.out_state.write = dsk_mem_sink_write;
        kernel_req.out_audit.user = &audit_sink;
        kernel_req.out_audit.write = dsk_mem_sink_write;

        switch (request.operation) {
        case DSK_OPERATION_INSTALL:
            st = dsk_install(&kernel_req);
            break;
        case DSK_OPERATION_REPAIR:
            st = dsk_repair(&kernel_req);
            break;
        case DSK_OPERATION_UNINSTALL:
            st = dsk_uninstall(&kernel_req);
            break;
        case DSK_OPERATION_VERIFY:
            st = dsk_verify(&kernel_req);
            break;
        case DSK_OPERATION_STATUS:
            st = dsk_status(&kernel_req);
            break;
        default:
            std::fprintf(stderr, "error: invalid operation\n");
            return 1;
        }

        if (!write_file(out_state, state_sink.data)) {
            std::fprintf(stderr, "error: failed to write state\n");
            return 1;
        }
        if (!write_file(out_audit, audit_sink.data)) {
            std::fprintf(stderr, "error: failed to write audit\n");
            return 1;
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

        return dsk_error_to_exit_code(st);
    }

    print_usage();
    return 1;
}
